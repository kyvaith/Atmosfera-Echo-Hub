"""Humidifier modes is a bounded attribute choice, never a percentage or preset."""
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
ACTION = {"kind": "control", "control": "choice", "property": "mode"}
OPTIONS = ["normal", "sleep", " Żółty "]


class HumidifierModeModelTests(unittest.TestCase):
    def setUp(self):
        self.state = base.State("humidifier.test", "off", {"supported_features": 1, "available_modes": OPTIONS.copy(), "mode": "normal"})
        self.hass, _ = base.environment(states=[self.state], services=["humidifier.set_mode"])

    def test_explicit_v3_climate_property_feature_and_live_registered_service(self):
        doc = base.document([base.card(entity=self.state.entity_id, action=ACTION)]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_humidifier_mode"])
        for entity, action, version in (("fan.test", ACTION, 3), ("humidifier.test", ACTION, 2), ("humidifier.test", ACTION | {"data": {}}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        for features in (0, 8, 32, True, -1, "1"):
            self.state.attributes["supported_features"] = features
            self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "mode"), {})
        class Features(IntFlag):
            MODES = 1
        self.state.attributes["supported_features"] = Features.MODES
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "mode"), {"humidifier_mode": {"options": OPTIONS, "index": 0}})
        self.hass.services.names.clear()
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "mode"), {})

    def test_null_missing_offlist_and_hvac_outage_never_become_known_empty_or_a_preset(self):
        attrs = self.state.attributes
        for value, mode, present in ((None, "off", True), ("none", "heat", True), ("absent", "off", True), ("normal", "unavailable", True), ("normal", "unknown", True), (None, "off", False)):
            attrs["mode"] = value
            if not present:
                attrs.pop("mode")
            self.assertFalse(choice.choice_is_empty(self.state.entity_id, mode, attrs, "mode"))
            domain = choice.choice_domain(self.state.entity_id, attrs, "mode")
            self.assertIsNone(domain.observed_index(choice.choice_state(self.state.entity_id, mode, attrs, "mode")))
        for values in ([], ["normal", "normal"], ["normal", "ą" * 17], ["normal", "bad\n"], ["normal", "unknown"]):
            attrs.update(available_modes=values, mode="normal")
            with self.assertRaises(choice.ChoiceDomainError):
                choice.choice_domain(self.state.entity_id, attrs, "mode")

    def test_actual_attribute_translation_keys_and_bounded_collision_fallback(self):
        domain = choice.choice_domain(self.state.entity_id, self.state.attributes, "mode")
        self.hass.entity_registry.entries[self.state.entity_id] = NS(platform="demo", translation_key="unit")
        labels = {"component.demo.entity.humidifier.unit.state_attributes.mode.state.normal": "HA mode"}
        with patch.object(base.cards, "async_get_cached_translations", side_effect=lambda _h, _l, category: labels if category == "entity" else {}):
            self.assertEqual(base.cards.choice_control_labels(self.hass, self.state, domain, "mode", "pl"), ("HA mode", "Sen", " Żółty "))
        self.assertEqual(domain.options, tuple(OPTIONS))
        collision = choice.ChoiceDomain(("normal", "Normalny"))
        self.assertEqual(choice.choice_labels(collision, "mode", "pl"), collision.options)


    def test_sticky_feature_with_empty_or_malformed_modes_never_exposes_a_native_mode(self):
        self.state.attributes["supported_features"] = 1
        for values in ([], None, "normal", {"normal": 1}, ("normal", "sleep")):
            self.state.attributes["available_modes"] = values
            self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "mode"), {})
        # Legacy explicit-service descriptors keep list/tuple compatibility,
        # while malformed optional metadata cannot crash the whole catalogue.
        for entity, service, field, attribute in (("humidifier.test", "humidifier.set_mode", "mode", "available_modes"),
                                                  ("select.test", "select.select_option", "option", "options")):
            state = base.State(entity, "off" if entity.startswith("humidifier.") else "normal", {"supported_features": 1})
            hass, _ = base.environment(states=[state], services=[service])
            for values in (None, "normal", {"normal": 1}, False):
                state.attributes[attribute] = values
                self.assertEqual(base.cards.entity_actions(hass, state), [])
            state.attributes[attribute] = ("normal", "sleep")
            self.assertEqual(base.cards.entity_actions(hass, state), [{"service": service, "fields": {field: {"type": "select", "options": ["normal", "sleep"], "required": True}}}])


class HumidifierModeOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.ChoiceOwnerTests()
        await self.f.asyncSetUp()
        f = self.f
        f.state = base.State("humidifier.test", "off", {"available_modes": OPTIONS.copy(), "mode": "normal", "humidity": 45, "supported_features": 1})
        f.hass.states.items = {f.state.entity_id: f.state}
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        f.hass.services.names = {"humidifier.set_mode"}
        self.language = "pl"
        f.owner._choice_language = lambda: self.language
        def change(value, **attrs):
            f.state.attributes.update(mode=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))
        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["mode"])
        f.change = change
        f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_localized_selection_sends_exact_mode_only_once_with_context(self):
        f = self.f
        grant = await f.open()
        self.assertEqual(grant["options"], ["Normalny", "Sen", " Żółty "])
        value = f.command(2)
        await f.send(value)
        await f.send(value)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("humidifier", "set_mode", {"entity_id": "humidifier.test", "mode": " Żółty "}))
        self.assertIs(kwargs["context"], f.user)
        self.assertEqual((f.state.state, f.state.attributes["humidity"]), ("off", 45))
        self.assertEqual(f.results()[-1]["status"], "state_matches")
        f.assert_terminal_order()

    async def test_fan_ABA_during_authorization_cannot_revive_apply(self):
        f = self.f
        await f.open()
        f.auth_gate = asyncio.Event()
        f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command(2)), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change("sleep")
        f.change("normal")
        f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_reordered_options_and_locale_change_revoke_selection(self):
        f = self.f
        await f.open()
        close = f.change("normal", available_modes=["normal", " Żółty ", "sleep"])
        self.assertEqual(close["reason"], "capabilities_changed")
        await f.open(seq=2)
        self.language = "en"
        await f.owner.async_state_changed()
        self.assertIsNone(f.owner._selection)
        grant = await f.open(seq=3)
        self.assertEqual(grant["options"], ["Normal", " Żółty ", "Sleep"])
        self.assertEqual(f.hass.services.calls, [])

    async def test_outage_capability_loss_and_missing_service_cannot_send_stale_command(self):
        f = self.f
        await f.open()
        old = f.command()
        f.state.state = "unavailable"
        f.change("normal")
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
        f.hass.services.names.add("humidifier.set_mode")
        await f.owner.async_close()
        await f.open(seq=3)
        close = f.change("normal", supported_features=0)
        self.assertEqual(close["reason"], "capabilities_changed")
        self.assertEqual(f.hass.services.calls, [])

    async def test_unknown_mode_is_not_negotiated_empty_or_an_initial_candidate(self):
        f = self.f
        f.change(None)
        self.assertFalse(choice.choice_is_empty(f.state.entity_id, f.state.state, f.state.attributes, "mode"))
        grant = await f.open()
        self.assertFalse(grant["available"])
        with self.assertRaises(shared.codec.ProtocolError):
            await f.send(f.command(1))
        self.assertEqual(f.hass.services.calls, [])
