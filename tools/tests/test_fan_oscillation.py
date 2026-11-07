"""Oscillation is an explicit state-aware action, independent of fan power."""

from copy import deepcopy
from enum import IntFlag
import importlib
import unittest
from types import SimpleNamespace as NS

import test_ha_layout as base

fan = importlib.import_module("_atmosfera_test.fan_oscillation")


class FanOscillationTests(unittest.TestCase):
    def setUp(self):
        self.state = base.State("fan.test", "on", {"supported_features": 2 | 16 | 32, "oscillating": False})
        self.hass, _ = base.environment(states=[self.state], services=["fan.oscillate", "fan.toggle"])
        self.card = base.card(entity="fan.test", action={"kind": "fan_oscillation"})

    def test_explicit_v3_fan_only_no_parameters(self):
        doc = base.document([self.card]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_fan_oscillation"])
        for version, entity, action in ((2, "fan.test", {"kind": "fan_oscillation"}),
                                        (3, "switch.test", {"kind": "fan_oscillation"}),
                                        (3, "fan.test", {"kind": "fan_oscillation", "data": {}}),
                                        (3, "fan.test", {"kind": "fan_oscillation", "control": "choice"})):
            with self.subTest(version=version, entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)

    def test_both_observed_values_resolve_opposite_without_power_command(self):
        for power in ("on", "off"):
            for observed in (False, True):
                with self.subTest(power=power, observed=observed):
                    self.state.state = power
                    self.state.attributes["oscillating"] = observed
                    action = base.cards.resolve_action(self.hass, self.card)
                    self.assertEqual((action.domain, action.service, action.data),
                                     ("fan", "oscillate", {"entity_id": "fan.test", "oscillating": not observed}))
                    self.assertEqual(base.cards.resolve_action(self.hass, base.card(entity="fan.test")).service, "toggle")

    def test_strict_boolean_and_live_capability_service(self):
        for malformed in (None, 0, 1, "on", "false", [], {}):
            with self.subTest(value=malformed):
                self.state.attributes["oscillating"] = malformed
                self.assertIsNone(base.cards.resolve_action(self.hass, self.card))
                self.assertEqual(base.cards._fan_oscillation_metadata(self.hass, self.state), {})
        self.state.attributes.pop("oscillating")
        self.assertIsNone(base.cards.resolve_action(self.hass, self.card))
        self.state.attributes["oscillating"] = False
        for features in (None, True, False, -1, 0, 8, "2"):
            with self.subTest(features=features):
                self.state.attributes["supported_features"] = features
                self.assertIsNone(base.cards.resolve_action(self.hass, self.card))
        class Features(IntFlag):
            OSCILLATE = 2
        self.state.attributes["supported_features"] = Features.OSCILLATE
        self.assertIsNotNone(base.cards.resolve_action(self.hass, self.card))
        self.hass.services.names.clear()
        self.assertIsNone(base.cards.resolve_action(self.hass, self.card))

    def test_missing_unknown_unavailable_read_only_hidden(self):
        for power in ("unknown", "unavailable", "bad", None):
            self.state.state = power
            self.assertIsNone(base.cards.resolve_action(self.hass, self.card))
        self.state.state = "on"
        for changes in ({"visible": False}, {"slot": 0}, {"type": "sensor"}):
            self.assertIsNone(base.cards.resolve_action(self.hass, self.card | changes))
        self.hass.states.items.clear()
        self.assertIsNone(base.cards.resolve_action(self.hass, self.card))

    def test_caption_palette_and_availability_follow_oscillation(self):
        item = self.card | {"state_color": True, "palette": "primary"}
        for power in ("on", "off"):
            self.state.state = power
            for value in (False, True):
                self.state.attributes["oscillating"] = value
                for locale, text in (("pl", "Oscylacja wł." if value else "Oscylacja wył."),
                                     ("en", "Oscillation: on" if value else "Oscillation: off")):
                    rendered = base.cards.presentation_payload(self.hass, [item], language=locale, press_enabled_supported=True)["cards"][2]
                    self.assertEqual(rendered["subtitle"], text)
                    self.assertEqual(rendered["palette"], "primary" if value else "surface")
                    self.assertTrue(rendered["press_enabled"])
        self.state.attributes["oscillating"] = None
        rendered = base.cards.presentation_payload(self.hass, [item], language="pl", press_enabled_supported=True)["cards"][2]
        self.assertEqual(rendered["subtitle"], "Nieznany")
        self.assertFalse(rendered["press_enabled"])
        self.assertEqual(rendered["palette"], "surface")

    def test_explicit_fixed_service_and_preset_control_unchanged(self):
        item = deepcopy(self.card)
        item["action"] = {"kind": "service", "service": "fan.oscillate", "data": {"oscillating": False}}
        self.assertIs(base.cards.resolve_action(self.hass, item).data["oscillating"], False)
        item["action"] = {"kind": "control", "control": "choice"}
        self.assertIsNone(base.cards.resolve_action(self.hass, item))


class FanOscillationDispatchTests(unittest.IsolatedAsyncioTestCase):
    def bridge(self):
        bridge = base.BridgeTests.bridge(None)
        state = base.State("fan.test", "off", {"supported_features": 2, "oscillating": False})
        bridge.hass, _ = base.environment(states=[state], services=["fan.oscillate"])
        item = base.card(entity="fan.test", action={"kind": "fan_oscillation"})
        bridge.tile_cards, bridge.tile_entity_ids = [item], ["fan.test"]
        bridge._native_context_required, bridge._context_press_version, bridge._press_enabled_version = True, 1, 1
        bridge.saved_revision = bridge.sent_revision = 0
        return bridge, item, state

    async def test_typed_report_dispatches_once_with_real_context_and_current_boolean(self):
        bridge, item, state = self.bridge()
        context = NS(user_id="allowed")
        await bridge.async_press_tile(2, card_id=item["id"], revision=0, context=context)
        self.assertEqual(bridge.hass.services.calls[0][0],
                         ("fan", "oscillate", {"entity_id": "fan.test", "oscillating": True}))
        self.assertIs(bridge.hass.services.calls[0][1]["context"], context)
        state.attributes["oscillating"] = True
        await bridge.async_press_tile(2, card_id=item["id"], revision=0, context=context)
        self.assertIs(bridge.hass.services.calls[1][0][2]["oscillating"], False)

    async def test_stale_missing_context_and_unnegotiated_availability_send_nothing(self):
        for mode in ("identity", "revision", "legacy", "unnegotiated", "unavailable", "missing_boolean"):
            bridge, item, state = self.bridge()
            kwargs = {"card_id": item["id"], "revision": 0}
            if mode == "identity": kwargs["card_id"] = "other"
            elif mode == "revision": kwargs["revision"] = 1
            elif mode == "legacy": kwargs = {}
            elif mode == "unnegotiated": bridge._press_enabled_version = 0
            elif mode == "unavailable": state.state = "unavailable"
            elif mode == "missing_boolean": state.attributes.pop("oscillating")
            await bridge.async_press_tile(2, **kwargs)
            self.assertEqual(bridge.hass.services.calls, [], mode)
