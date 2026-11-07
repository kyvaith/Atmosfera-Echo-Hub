"""Humidifier power admits actual ToggleEntity state without guessing a mode."""

from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import test_ha_layout as base

SERVICES = ["humidifier.turn_on", "humidifier.turn_off", "humidifier.toggle"]


class HumidifierPowerModelTests(unittest.TestCase):
    def setUp(self):
        self.state = base.State("humidifier.test", "off", {"supported_features": 0, "device_class": "humidifier", "humidity": 45, "mode": "sleep"})
        self.hass, _ = base.environment(states=[self.state], services=SERVICES)
        self.card = base.card(entity=self.state.entity_id)

    def test_domain_and_power_service_schema_without_implicit_mode_or_target_fields(self):
        doc = base.document([self.card])
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_humidifier_power"])
        for service in SERVICES:
            action = {"kind": "service", "service": service, "data": {}}
            self.assertEqual(base.layout.validate_action(action, self.state.entity_id), action)
            for field in ("mode", "humidity", "entity_id"):
                with self.assertRaises(base.layout.LayoutError):
                    base.layout.validate_action(action | {"data": {field: 45}}, self.state.entity_id)

    def test_default_uses_opposite_current_power_without_modes_feature_or_extra_fields(self):
        for device_class in ("humidifier", "dehumidifier"):
            self.state.attributes["device_class"] = device_class
            for power, service in (("off", "turn_on"), ("on", "turn_off")):
                self.state.state = power
                action = base.cards.resolve_action(self.hass, self.card)
                self.assertEqual((action.domain, action.service, action.data), ("humidifier", service, {"entity_id": self.state.entity_id}))
                self.assertEqual((self.state.attributes["humidity"], self.state.attributes["mode"]), (45, "sleep"))
        self.assertEqual(self.hass.services.calls, [])

    def test_missing_unknown_unrecognized_or_missing_opposite_service_disables_default(self):
        for power in ("unknown", "unavailable", "humidifying", "ON", "", None):
            self.state.state = power
            self.assertIsNone(base.cards.resolve_action(self.hass, self.card))
            self.assertEqual(base.cards.entity_actions(self.hass, self.state), [])
        self.state.state = "off"
        self.hass.services.names.remove("humidifier.turn_on")
        self.assertIsNone(base.cards.resolve_action(self.hass, self.card))
        self.hass.states.items.clear()
        self.assertIsNone(base.cards.resolve_action(self.hass, self.card))

    def test_hidden_reserved_information_and_none_never_resolve(self):
        for changes in ({"visible": False}, {"slot": 0}, {"type": "sensor"}, {"action": {"kind": "none"}}):
            self.assertIsNone(base.cards.resolve_action(self.hass, self.card | changes))
        self.assertTrue(base.cards.ordinary_action_availability(self.card))

    def test_fixed_power_service_is_explicit_and_known_state_only(self):
        self.state.state = "on"
        for service in ("turn_on", "turn_off", "toggle"):
            card = self.card | {"action": {"kind": "service", "service": "humidifier." + service, "data": {}}}
            self.assertEqual(base.cards.resolve_action(self.hass, card).service, service)
            self.state.state = "unknown"
            self.assertIsNone(base.cards.resolve_action(self.hass, card))
            self.state.state = "on"

    def test_opt_in_palette_and_negotiated_availability_follow_real_power(self):
        card = self.card | {"state_color": True}
        for power in ("on", "off"):
            self.state.state = power
            rendered = base.cards.presentation_payload(self.hass, [card], press_enabled_supported=True)["cards"][2]
            self.assertTrue(rendered["press_enabled"])
            self.assertEqual(rendered["palette"], "primary" if power == "on" else "surface")
        self.state.state = "unavailable"
        rendered = base.cards.presentation_payload(self.hass, [card], press_enabled_supported=True)["cards"][2]
        self.assertFalse(rendered["press_enabled"])
        self.assertEqual(rendered["palette"], "surface")

    def test_ha_translations_win_and_missing_resource_has_pl_en_on_off_fallback(self):
        for power in ("on", "off"):
            self.state.state = power
            with patch.object(base.cards, "_translate_state_for_locale", return_value="HA exact"):
                self.assertEqual(base.cards._state_subtitle(self.hass, self.state, "pl"), "HA exact")
            with patch.object(base.cards, "_translate_state_for_locale", return_value=power):
                self.assertEqual(base.cards._state_subtitle(self.hass, self.state, "pl"), "Włączony" if power == "on" else "Wyłączony")
                self.assertEqual(base.cards._state_subtitle(self.hass, self.state, "en"), power.title())

    def test_catalogue_includes_both_device_classes_with_only_registered_power_services(self):
        for device_class in ("humidifier", "dehumidifier"):
            self.state.attributes["device_class"] = device_class
            result = base.cards.entity_catalogue(self.hass, domains=["humidifier"])
            self.assertEqual(len(result["entities"]), 1)
            self.assertEqual(result["entities"][0]["domain"], "humidifier")
            self.assertEqual({item["service"] for item in result["entities"][0]["actions"]}, set(SERVICES))


class HumidifierPowerDispatchTests(unittest.IsolatedAsyncioTestCase):
    def bridge(self):
        bridge = base.BridgeTests.bridge(None)
        state = base.State("humidifier.test", "off", {"humidity": 45, "mode": "sleep"})
        bridge.hass, _ = base.environment(states=[state], services=SERVICES)
        card = base.card(entity=state.entity_id)
        bridge.tile_cards, bridge.tile_entity_ids = [card], [state.entity_id]
        bridge._native_context_required, bridge._context_press_version, bridge._press_enabled_version = True, 1, 1
        bridge.saved_revision = bridge.sent_revision = 0
        return bridge, card, state

    async def test_typed_press_uses_current_opposite_power_with_context_and_no_extra_command(self):
        bridge, card, state = self.bridge()
        context = NS(user_id="allowed")
        for power, operation in (("off", "turn_on"), ("on", "turn_off")):
            state.state = power
            await bridge.async_press_tile(2, card_id=card["id"], revision=0, context=context)
            args, kwargs = bridge.hass.services.calls[-1]
            self.assertEqual(args, ("humidifier", operation, {"entity_id": state.entity_id}))
            self.assertIs(kwargs["context"], context)
        self.assertEqual(len(bridge.hass.services.calls), 2)
        self.assertEqual(state.attributes, {"humidity": 45, "mode": "sleep"})

    async def test_stale_legacy_unnegotiated_offline_pending_or_unknown_reports_dispatch_nothing(self):
        for mode in ("identity", "revision", "legacy", "unnegotiated", "offline", "pending", "unavailable", "missing_service"):
            bridge, card, state = self.bridge()
            kwargs = {"card_id": card["id"], "revision": 0}
            if mode == "identity": kwargs["card_id"] = "other"
            elif mode == "revision": kwargs["revision"] = 1
            elif mode == "legacy": kwargs = {}
            elif mode == "unnegotiated": bridge._press_enabled_version = 0
            elif mode == "offline": bridge.esphome_entry.runtime_data.available = False
            elif mode == "pending": bridge.saved_revision = 1
            elif mode == "unavailable": state.state = "unavailable"
            elif mode == "missing_service": bridge.hass.services.names.clear()
            await bridge.async_press_tile(2, **kwargs)
            self.assertEqual(bridge.hass.services.calls, [], mode)
