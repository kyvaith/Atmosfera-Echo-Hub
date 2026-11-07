"""Independent horizontal swing is a bounded attribute choice, never a percentage or preset."""
import asyncio
from copy import deepcopy
from enum import IntFlag
import importlib
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import test_ha_layout as base
import test_choice_control as shared

choice = importlib.import_module("_atmosfera_test.choice_domain")
ACTION = {"kind": "control", "control": "choice", "property": "swing_horizontal_mode"}
OPTIONS = ["off", "on", "Prawy Żółty"]


class ClimateHorizontalModelTests(unittest.TestCase):
    def setUp(self):
        self.state = base.State("climate.test", "off", {"supported_features": 512, "swing_horizontal_modes": OPTIONS.copy(), "swing_horizontal_mode": "off", "preset_mode": "comfort"})
        self.hass, _ = base.environment(states=[self.state], services=["climate.set_swing_horizontal_mode"])

    def test_explicit_v3_climate_property_feature_and_live_registered_service(self):
        doc = base.document([base.card(entity=self.state.entity_id, action=ACTION)]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_climate_swing_horizontal_mode"])
        for entity, action, version in (("fan.test", ACTION, 3), ("climate.test", ACTION, 2), ("climate.test", ACTION | {"data": {}}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        for features in (0, 8, 32, True, -1, "512"):
            self.state.attributes["supported_features"] = features
            self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "swing_horizontal_mode"), {})
        class Features(IntFlag):
            HORIZONTAL = 512
        self.state.attributes["supported_features"] = Features.HORIZONTAL
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "swing_horizontal_mode"), {"climate_swing_horizontal_mode": {"options": OPTIONS, "index": 0}})
        self.hass.services.names.clear()
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "swing_horizontal_mode"), {})

    def test_null_missing_offlist_and_hvac_outage_never_become_known_empty_or_a_preset(self):
        attrs = self.state.attributes
        for value, mode, present in ((None, "off", True), ("none", "heat", True), ("absent", "off", True), ("off", "unavailable", True), ("off", "unknown", True), (None, "off", False)):
            attrs["swing_horizontal_mode"] = value
            if not present:
                attrs.pop("swing_horizontal_mode")
            self.assertFalse(choice.choice_is_empty(self.state.entity_id, mode, attrs, "swing_horizontal_mode"))
            domain = choice.choice_domain(self.state.entity_id, attrs, "swing_horizontal_mode")
            self.assertIsNone(domain.observed_index(choice.choice_state(self.state.entity_id, mode, attrs, "swing_horizontal_mode")))
        for values in ([], ["off", "off"], ["off", "ą" * 17], ["off", "bad\n"], ["off", "unknown"]):
            attrs.update(swing_horizontal_modes=values, swing_horizontal_mode="off")
            with self.assertRaises(choice.ChoiceDomainError):
                choice.choice_domain(self.state.entity_id, attrs, "swing_horizontal_mode")

    def test_actual_attribute_translation_keys_and_bounded_collision_fallback(self):
        domain = choice.choice_domain(self.state.entity_id, self.state.attributes, "swing_horizontal_mode")
        self.hass.entity_registry.entries[self.state.entity_id] = NS(platform="demo", translation_key="unit")
        labels = {"component.demo.entity.climate.unit.state_attributes.swing_horizontal_mode.state.off": "HA stop"}
        with patch.object(base.cards, "async_get_cached_translations", side_effect=lambda _h, _l, category: labels if category == "entity" else {}):
            self.assertEqual(base.cards.choice_control_labels(self.hass, self.state, domain, "swing_horizontal_mode", "pl"), ("HA stop", "Włączone", "Prawy Żółty"))
        self.assertEqual(domain.options, tuple(OPTIONS))
        collision = choice.ChoiceDomain(("off", "Wyłączone"))
        self.assertEqual(choice.choice_labels(collision, "swing_horizontal_mode", "pl"), collision.options)


    def test_service_editor_whitelist_and_live_catalogue_require_exact_axis_feature_and_field(self):
        service = "climate.set_swing_horizontal_mode"
        action = {"kind": "service", "service": service, "data": {"swing_horizontal_mode": "Prawy Żółty"}}
        self.assertEqual(base.layout.validate_action(action, self.state.entity_id, layout_version=3), action)
        self.assertEqual(base.cards.entity_actions(self.hass, self.state), [{"service": service, "fields": {"swing_horizontal_mode": {"type": "select", "options": OPTIONS, "required": True}}}])
        base.cards.validate_live_action(self.hass, self.state, action)
        with self.assertRaises(base.layout.LayoutError):
            base.cards.validate_live_action(self.hass, self.state, action | {"data": {"swing_mode": "on"}})
        self.state.attributes["supported_features"] = 32
        self.assertEqual(base.cards.entity_actions(self.hass, self.state), [])
        with self.assertRaises(base.layout.LayoutError):
            base.cards.validate_live_action(self.hass, self.state, action)


class ClimateHorizontalOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.ChoiceOwnerTests()
        await self.f.asyncSetUp()
        f = self.f
        f.state = base.State("climate.test", "off", {"swing_horizontal_modes": OPTIONS.copy(), "swing_horizontal_mode": "off", "temperature": 21.5, "preset_mode": "comfort", "fan_mode": "auto", "swing_mode": "vertical", "supported_features": 512})
        f.hass.states.items = {f.state.entity_id: f.state}
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        f.hass.services.names = {"climate.set_swing_horizontal_mode"}
        self.language = "pl"
        f.owner._choice_language = lambda: self.language
        def change(value, **attrs):
            f.state.attributes.update(swing_horizontal_mode=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))
        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["swing_horizontal_mode"])
        f.change = change
        f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_localized_selection_sends_exact_fan_only_once_with_context(self):
        f = self.f
        grant = await f.open()
        self.assertEqual(grant["options"], ["Wyłączone", "Włączone", "Prawy Żółty"])
        value = f.command(2)
        await f.send(value)
        await f.send(value)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("climate", "set_swing_horizontal_mode", {"entity_id": "climate.test", "swing_horizontal_mode": "Prawy Żółty"}))
        self.assertIs(kwargs["context"], f.user)
        self.assertEqual((f.state.state, f.state.attributes["temperature"], f.state.attributes["preset_mode"], f.state.attributes["fan_mode"], f.state.attributes["swing_mode"]), ("off", 21.5, "comfort", "auto", "vertical"))
        self.assertEqual(f.results()[-1]["status"], "state_matches")
        f.assert_terminal_order()

    async def test_fan_ABA_during_authorization_cannot_revive_apply(self):
        f = self.f
        await f.open()
        f.auth_gate = asyncio.Event()
        f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command(2)), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change("on")
        f.change("off")
        f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_reordered_options_and_locale_change_revoke_selection(self):
        f = self.f
        await f.open()
        close = f.change("off", swing_horizontal_modes=["off", "Prawy Żółty", "on"])
        self.assertEqual(close["reason"], "capabilities_changed")
        await f.open(seq=2)
        self.language = "en"
        await f.owner.async_state_changed()
        self.assertIsNone(f.owner._selection)
        grant = await f.open(seq=3)
        self.assertEqual(grant["options"], ["Off", "Prawy Żółty", "On"])
        self.assertEqual(f.hass.services.calls, [])

    async def test_outage_capability_loss_and_missing_service_cannot_send_stale_command(self):
        f = self.f
        await f.open()
        old = f.command()
        f.state.state = "unavailable"
        f.change("off")
        await f.send(old)
        self.assertEqual(f.hass.services.calls, [])
        f.state.state = "off"
        await f.owner.async_close()
        await f.open(seq=2)
        old = f.command()
        f.hass.services.names.clear()
        with self.assertRaises(shared.codec.ProtocolError):
            await f.send(old)
        self.assertEqual(f.hass.services.calls, [])
        f.hass.services.names.add("climate.set_swing_horizontal_mode")
        await f.owner.async_close()
        await f.open(seq=3)
        close = f.change("off", supported_features=32)
        self.assertEqual(close["reason"], "capabilities_changed")
        self.assertEqual(f.hass.services.calls, [])
