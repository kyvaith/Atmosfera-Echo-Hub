"""Climate fan mode is a bounded attribute choice, never a percentage or preset."""
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
ACTION = {"kind": "control", "control": "choice", "property": "fan_mode"}
OPTIONS = ["auto", "low", "medium", "high"]


class ClimateFanModelTests(unittest.TestCase):
    def setUp(self):
        self.state = base.State("climate.test", "off", {"supported_features": 8, "fan_modes": OPTIONS.copy(), "fan_mode": "auto", "preset_mode": "comfort"})
        self.hass, _ = base.environment(states=[self.state], services=["climate.set_fan_mode"])

    def test_explicit_v3_climate_property_feature_and_live_registered_service(self):
        doc = base.document([base.card(entity=self.state.entity_id, action=ACTION)]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_climate_fan_mode"])
        for entity, action, version in (("fan.test", ACTION, 3), ("climate.test", ACTION, 2), ("climate.test", ACTION | {"data": {}}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        for features in (0, 16, True, -1, "8"):
            self.state.attributes["supported_features"] = features
            self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "fan_mode"), {})
        class Features(IntFlag):
            FAN = 8
        self.state.attributes["supported_features"] = Features.FAN
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "fan_mode"), {"climate_fan_mode": {"options": OPTIONS, "index": 0}})
        self.hass.services.names.clear()
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "fan_mode"), {})

    def test_null_missing_offlist_and_hvac_outage_never_become_known_empty_or_a_preset(self):
        attrs = self.state.attributes
        for value, mode, present in ((None, "off", True), ("none", "heat", True), ("absent", "off", True), ("auto", "unavailable", True), ("auto", "unknown", True), (None, "off", False)):
            attrs["fan_mode"] = value
            if not present:
                attrs.pop("fan_mode")
            self.assertFalse(choice.choice_is_empty(self.state.entity_id, mode, attrs, "fan_mode"))
            domain = choice.choice_domain(self.state.entity_id, attrs, "fan_mode")
            self.assertIsNone(domain.observed_index(choice.choice_state(self.state.entity_id, mode, attrs, "fan_mode")))
        for values in ([], ["auto", "auto"], ["auto", "ą" * 17], ["auto", "bad\n"], ["auto", "unknown"]):
            attrs.update(fan_modes=values, fan_mode="auto")
            with self.assertRaises(choice.ChoiceDomainError):
                choice.choice_domain(self.state.entity_id, attrs, "fan_mode")

    def test_actual_attribute_translation_keys_and_bounded_collision_fallback(self):
        domain = choice.choice_domain(self.state.entity_id, self.state.attributes, "fan_mode")
        self.hass.entity_registry.entries[self.state.entity_id] = NS(platform="demo", translation_key="unit")
        labels = {"component.demo.entity.climate.unit.state_attributes.fan_mode.state.auto": "HA Auto"}
        with patch.object(base.cards, "async_get_cached_translations", side_effect=lambda _h, _l, category: labels if category == "entity" else {}):
            self.assertEqual(base.cards.choice_control_labels(self.hass, self.state, domain, "fan_mode", "pl"), ("HA Auto", "Niski", "Średni", "Wysoki"))
        self.assertEqual(domain.options, tuple(OPTIONS))
        collision = choice.ChoiceDomain(("low", "Niski"))
        self.assertEqual(choice.choice_labels(collision, "fan_mode", "pl"), collision.options)


class ClimateFanOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.ChoiceOwnerTests()
        await self.f.asyncSetUp()
        f = self.f
        f.state = base.State("climate.test", "off", {"fan_modes": OPTIONS.copy(), "fan_mode": "auto", "temperature": 21.5, "preset_mode": "comfort", "supported_features": 8})
        f.hass.states.items = {f.state.entity_id: f.state}
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        f.hass.services.names = {"climate.set_fan_mode"}
        self.language = "pl"
        f.owner._choice_language = lambda: self.language
        def change(value, **attrs):
            f.state.attributes.update(fan_mode=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))
        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["fan_mode"])
        f.change = change
        f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_localized_selection_sends_exact_fan_only_once_with_context(self):
        f = self.f
        grant = await f.open()
        self.assertEqual(grant["options"], ["Automatyczny", "Niski", "Średni", "Wysoki"])
        value = f.command(2)
        await f.send(value)
        await f.send(value)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("climate", "set_fan_mode", {"entity_id": "climate.test", "fan_mode": "medium"}))
        self.assertIs(kwargs["context"], f.user)
        self.assertEqual((f.state.state, f.state.attributes["temperature"], f.state.attributes["preset_mode"]), ("off", 21.5, "comfort"))
        self.assertEqual(f.results()[-1]["status"], "state_matches")
        f.assert_terminal_order()

    async def test_fan_ABA_during_authorization_cannot_revive_apply(self):
        f = self.f
        await f.open()
        f.auth_gate = asyncio.Event()
        f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command(2)), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change("high")
        f.change("auto")
        f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_reordered_options_and_locale_change_revoke_selection(self):
        f = self.f
        await f.open()
        close = f.change("auto", fan_modes=["auto", "high", "medium", "low"])
        self.assertEqual(close["reason"], "capabilities_changed")
        await f.open(seq=2)
        self.language = "en"
        await f.owner.async_state_changed()
        self.assertIsNone(f.owner._selection)
        grant = await f.open(seq=3)
        self.assertEqual(grant["options"], ["Automatic", "High", "Medium", "Low"])
        self.assertEqual(f.hass.services.calls, [])

    async def test_outage_capability_loss_and_missing_service_cannot_send_stale_command(self):
        f = self.f
        await f.open()
        old = f.command()
        f.state.state = "unavailable"
        f.change("auto")
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
        f.hass.services.names.add("climate.set_fan_mode")
        await f.owner.async_close()
        await f.open(seq=3)
        close = f.change("auto", supported_features=16)
        self.assertEqual(close["reason"], "capabilities_changed")
        self.assertEqual(f.hass.services.calls, [])
