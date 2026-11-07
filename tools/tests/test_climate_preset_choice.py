"""Climate presets distinguish real none options, known empty and unknown state."""

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
ACTION = {"kind": "control", "control": "choice", "property": "preset_mode"}
OPTIONS = ["eco", "comfort", " Nocny Żółty "]


class PresetModelTests(unittest.TestCase):
    def setUp(self):
        self.state = base.State("climate.test", "off", {"supported_features": 16, "preset_modes": OPTIONS.copy(), "preset_mode": None})
        self.hass, _ = base.environment(states=[self.state], services=["climate.set_preset_mode"])

    def test_explicit_v3_climate_only_and_strict_feature_list_service(self):
        doc = base.document([base.card(entity=self.state.entity_id, action=ACTION)]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_climate_preset_mode"])
        for entity, action, version in (("fan.test", ACTION, 3), ("climate.test", ACTION, 2),
                                       ("climate.test", ACTION | {"control": "number"}, 3),
                                       ("climate.test", ACTION | {"data": {}}, 3)):
            with self.subTest(action=action, entity=entity), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        for value in (0, 8, True, -1, "16"):
            self.state.attributes["supported_features"] = value
            self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "preset_mode"), {})
        class Features(IntFlag):
            PRESET = 16
        self.state.attributes["supported_features"] = Features.PRESET
        self.assertTrue(base.cards._choice_control_metadata(self.hass, self.state, "preset_mode"))
        self.hass.services.names.clear()
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "preset_mode"), {})

    def test_none_attribute_and_inactive_none_code_differ_from_a_real_none_option_and_unknown(self):
        for value in (None, "none"):
            self.state.attributes["preset_mode"] = value
            meta = base.cards._choice_control_metadata(self.hass, self.state, "preset_mode")
            self.assertEqual(meta, {"climate_preset_mode": {"options": OPTIONS, "index": None, "empty": True}})
        self.state.attributes.update(preset_modes=["none", *OPTIONS], preset_mode="none")
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "preset_mode"),
                         {"climate_preset_mode": {"options": ["none", *OPTIONS], "index": 0}})
        for value, present, mode in ((None, False, "off"), ("absent", True, "heat"), (None, True, "unavailable"), (None, True, "unknown")):
            self.state.state = mode
            self.state.attributes["preset_mode"] = value
            if not present:
                self.state.attributes.pop("preset_mode")
            self.assertFalse(choice.choice_is_empty(self.state.entity_id, mode, self.state.attributes, "preset_mode"))

    def test_attribute_translations_prefer_entity_then_generic_and_keep_service_values_exact(self):
        domain = choice.choice_domain(self.state.entity_id, self.state.attributes, "preset_mode")
        self.hass.entity_registry.entries[self.state.entity_id] = NS(platform="demo", translation_key="unit")
        entity = {"component.demo.entity.climate.unit.state_attributes.preset_mode.state.eco": "HA oszczędny"}
        generic = {"component.climate.entity_component._.state_attributes.preset_mode.state.eco": "Generic Eco"}
        with patch.object(base.cards, "async_get_cached_translations", side_effect=lambda _h, _l, category: entity if category == "entity" else generic):
            self.assertEqual(base.cards.choice_control_labels(self.hass, self.state, domain, "preset_mode", "pl"),
                             ("HA oszczędny", "Komfort", " Nocny Żółty "))
        self.assertEqual(domain.options, tuple(OPTIONS))
        collision = choice.ChoiceDomain(("eco", "Eco"))
        self.assertEqual(choice.choice_labels(collision, "preset_mode", "pl"), collision.options)


class PresetOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.ChoiceOwnerTests()
        await self.f.asyncSetUp()
        f = self.f
        f.state = base.State("climate.test", "off", {"supported_features": 16, "preset_modes": OPTIONS.copy(), "preset_mode": None, "temperature": 21.5})
        f.hass.states.items = {f.state.entity_id: f.state}
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        f.hass.services.names = {"climate.set_preset_mode"}
        self.language = "pl"
        f.owner._choice_language = lambda: self.language

        def change(value, **attrs):
            f.state.attributes.update(preset_mode=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))

        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["preset_mode"])

        f.change = change
        f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def send(self, value):
        f = self.f
        result = await f.owner.async_handle(f.owner._encode(value), f.user)
        if f.owner._selection and f.owner._selection.command:
            await asyncio.wait_for(f.owner._selection.command.task, .5)
        return result

    async def test_known_empty_requires_negotiation_then_dispatches_exact_name_once_with_context(self):
        f = self.f
        grant = await f.open()
        self.assertEqual((grant["index"], grant["available"]), (None, False))
        await f.owner.async_close()
        f.owner.accept_empty_choice_features(f.owner.channel, 1)
        grant = await f.open(seq=2)
        self.assertEqual((grant["index"], grant["available"], grant["options"]),
                         (None, True, ["Eco", "Komfort", " Nocny Żółty "]))
        value = f.command(2)
        self.assertIsNone(value["expected_index"])
        await self.send(value)
        await self.send(value)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("climate", "set_preset_mode", {"entity_id": "climate.test", "preset_mode": " Nocny Żółty "}))
        self.assertIs(kwargs["context"], f.user)
        self.assertEqual((f.state.state, f.state.attributes["temperature"]), ("off", 21.5))
        self.assertEqual(f.results()[-1]["status"], "state_matches")
        f.assert_terminal_order()

    async def test_real_none_option_does_not_require_empty_extension(self):
        f = self.f
        f.state.attributes.update(preset_modes=["none", *OPTIONS], preset_mode="none")
        grant = await f.open()
        self.assertEqual((grant["index"], grant["available"], f.owner.empty_choice_version), (0, True, 0))
        await self.send(f.command(1))
        self.assertEqual(f.hass.services.calls[0][0][2]["preset_mode"], "eco")

    async def test_empty_preset_empty_ABA_while_authorizing_cannot_revive_apply(self):
        f = self.f
        f.owner.accept_empty_choice_features(f.owner.channel, 1)
        await f.open()
        f.auth_gate = asyncio.Event()
        f.auth_entered.clear()
        await f.owner.async_handle(f.owner._encode(f.command(2)), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change("comfort")
        f.change(None)
        f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_list_capability_locale_and_service_loss_preserve_fences(self):
        f = self.f
        f.change("eco")
        await f.open()
        close = f.change("eco", preset_modes=["comfort", "eco"])
        self.assertEqual(close["reason"], "capabilities_changed")
        await f.open(seq=2)
        self.language = "en"
        await f.owner.async_state_changed()
        self.assertIsNone(f.owner._selection)
        await f.open(seq=3)
        close = f.change("eco", supported_features=0)
        self.assertEqual(close["reason"], "capabilities_changed")
        f.state.attributes["supported_features"] = 16
        await f.open(seq=4)
        old = f.command()
        f.hass.services.names.clear()
        with self.assertRaises(shared.codec.ProtocolError):
            await self.send(old)
        self.assertEqual(f.hass.services.calls, [])
