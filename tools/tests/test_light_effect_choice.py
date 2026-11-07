"""Effects use exact light.turn_on names; known empty requires negotiation."""

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
ACTION = {"kind": "control", "control": "choice", "property": "effect"}
OPTIONS = ["Solid", "Pulse", " Żółty "]


class EffectModelTests(unittest.TestCase):
    def setUp(self):
        self.state = base.State("light.test", "off", {"supported_features": 4,
            "supported_color_modes": ["onoff"], "effect_list": OPTIONS.copy(), "effect": None})
        self.hass, _ = base.environment(states=[self.state], services=["light.turn_on", "light.turn_off"])

    def test_explicit_v3_light_only_and_strict_feature_catalogue_service(self):
        doc = base.document([base.card(entity="light.test", action=ACTION)]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_light_effect"])
        for entity, action, version in (("fan.test", ACTION, 3), ("light.test", ACTION, 2),
            ("light.test", ACTION | {"control": "number"}, 3), ("light.test", ACTION | {"data": {}}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        for value in (0, 1, True, -1, "4"):
            self.state.attributes["supported_features"] = value
            self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "effect"), {})
        class Features(IntFlag):
            EFFECT = 4
        self.state.attributes["supported_features"] = Features.EFFECT
        self.assertTrue(base.cards._choice_control_metadata(self.hass, self.state, "effect"))
        self.hass.services.names.clear()
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "effect"), {})

    def test_actual_none_is_empty_while_missing_bad_and_stale_off_effect_are_unknown(self):
        for power in ("on", "off"):
            self.state.state = power
            meta = base.cards._choice_control_metadata(self.hass, self.state, "effect")
            self.assertEqual(meta, {"light_effect": {"options": OPTIONS, "index": None, "empty": True}})
            item = base.card(entity="light.test", action=ACTION)
            p = base.cards.presentation_payload(self.hass, [item], choice_control_supported=True, language="pl-PL")
            self.assertEqual(p["cards"][2]["subtitle"], "Brak efektu")
        for power, value, present in (("off", "Pulse", True), ("on", "missing", True),
            ("on", None, False), ("unknown", None, True), ("unavailable", None, True)):
            self.state.state = power; self.state.attributes["effect"] = value
            if not present:
                self.state.attributes.pop("effect")
            self.assertFalse(choice.choice_is_empty("light.test", power, self.state.attributes, "effect"))
            d = choice.choice_domain("light.test", self.state.attributes, "effect")
            self.assertIsNone(d.observed_index(choice.choice_state("light.test", power, self.state.attributes, "effect")))
        self.state.state = "on"; self.state.attributes.update(effect_list=["none", *OPTIONS], effect="none")
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "effect")["light_effect"]["index"], 0)
        self.assertFalse(choice.choice_is_empty("light.test", "on", self.state.attributes, "effect"))

    def test_bounded_distinct_real_list_and_unchanged_ordinary_power_descriptor(self):
        for options in ([], OPTIONS * 3, ["same", "same"], None, "Solid", tuple(OPTIONS), ["x" * 33], ["bad\n"]):
            self.state.attributes["effect_list"] = options
            self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "effect"), {})
        self.state.attributes.update(supported_features=0, effect_list=OPTIONS)
        actions = {a["service"]: a["fields"] for a in base.cards.entity_actions(self.hass, self.state)}
        self.assertEqual(actions["light.turn_on"], {})
        self.assertEqual(actions["light.turn_off"], {})
        with self.assertRaises(base.layout.LayoutError):
            base.cards.validate_live_action(self.hass, self.state, {"service": "light.turn_on", "data": {"effect": "Pulse"}})
        self.state.attributes["supported_features"] = 4
        fields = {a["service"]: a["fields"] for a in base.cards.entity_actions(self.hass, self.state)}
        self.assertEqual(fields["light.turn_on"], {"effect": {"type": "select", "options": OPTIONS, "required": False}})
        base.cards.validate_live_action(self.hass, self.state, {"service": "light.turn_on", "data": {"effect": "Pulse"}})

    def test_cached_effect_translation_changes_labels_never_service_names(self):
        d = choice.choice_domain("light.test", self.state.attributes, "effect")
        self.hass.entity_registry.entries["light.test"] = NS(platform="demo", translation_key="unit")
        translations = {"component.demo.entity.light.unit.state_attributes.effect.state.Pulse": "Pulsowanie HA"}
        with patch.object(base.cards, "async_get_cached_translations", side_effect=lambda _h, _l, category: translations if category == "entity" else {}):
            self.assertEqual(base.cards.choice_control_labels(self.hass, self.state, d, "effect", "pl"), ("Solid", "Pulsowanie HA", " Żółty "))
        self.assertEqual(d.options, tuple(OPTIONS))


class EffectOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.ChoiceOwnerTests()
        await self.f.asyncSetUp()
        f = self.f
        f.state = base.State("light.test", "off", {"supported_features": 4, "supported_color_modes": ["onoff"],
            "effect_list": OPTIONS.copy(), "effect": None})
        f.hass.states.items = {f.state.entity_id: f.state}
        f.hass.services.names = {"light.turn_on", "light.turn_off"}
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        def change(value, power=None, **attrs):
            if power is not None:
                f.state.state = power
            f.state.attributes.update(effect=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))
        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["effect"], power="on")
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

    async def test_known_empty_negotiation_then_one_exact_effect_call_can_activate_off_light(self):
        f = self.f
        grant = await f.open()
        self.assertEqual((grant["index"], grant["available"]), (None, False))
        await f.owner.async_close(); f.owner.accept_empty_choice_features(f.owner.channel, 1)
        grant = await f.open(seq=2)
        self.assertEqual((grant["index"], grant["available"], grant["options"]), (None, True, OPTIONS))
        value = f.command(2)
        self.assertIsNone(value["expected_index"])
        await self.send(value); await self.send(value)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("light", "turn_on", {"entity_id": "light.test", "effect": " Żółty "}))
        self.assertIs(kwargs["context"], f.user)
        self.assertEqual((f.state.state, f.state.attributes["effect"]), ("on", " Żółty "))
        self.assertEqual(f.results()[-1]["status"], "state_matches")
        f.assert_terminal_order()

    async def test_literal_none_option_is_an_ordinary_index_without_empty_negotiation(self):
        f = self.f
        f.change("none", power="on", effect_list=["none", *OPTIONS])
        grant = await f.open()
        self.assertEqual((grant["index"], grant["available"], f.owner.empty_choice_version), (0, True, 0))
        await self.send(f.command(1))
        self.assertEqual(f.hass.services.calls[0][0][2]["effect"], "Solid")

    async def test_empty_effect_empty_ABA_during_authorization_never_revives_input(self):
        f = self.f; f.owner.accept_empty_choice_features(f.owner.channel, 1); await f.open()
        f.auth_gate = asyncio.Event(); f.auth_entered.clear()
        await f.owner.async_handle(f.owner._encode(f.command(2)), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change("Solid", power="on"); f.change(None, power="off"); f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_off_stale_effect_outage_and_missing_value_do_not_confirm_or_send(self):
        f = self.f; f.change("Solid", power="on"); await f.open(); old = f.command(1)
        f.change("Pulse", power="off")
        self.assertEqual(f.owner._selection.domain_state[1:3], (None, False))
        await self.send(old)
        self.assertEqual(f.hass.services.calls, [])
        await f.owner.async_close(); f.change("Solid", power="on"); await f.open(seq=2)
        old = f.command(1); f.change("Solid", power="unavailable")
        await self.send(old)
        self.assertEqual(f.hass.services.calls, [])

    async def test_list_feature_and_service_loss_keep_the_existing_fences(self):
        f = self.f; f.change("Solid", power="on"); await f.open()
        close = f.change("Solid", effect_list=["Pulse", "Solid"])
        self.assertEqual(close["reason"], "capabilities_changed")
        await f.open(seq=2)
        close = f.change("Solid", supported_features=0)
        self.assertEqual(close["reason"], "capabilities_changed")
        f.change("Solid", supported_features=4); await f.open(seq=3)
        old = f.command(); f.hass.services.names.clear()
        with self.assertRaises(shared.codec.ProtocolError):
            await self.send(old)
        self.assertEqual(f.hass.services.calls, [])

    async def test_ha_service_acceptance_without_feedback_is_not_a_success(self):
        f = self.f; f.change("Solid", power="on"); await f.open(); f.apply = False
        await self.send(f.command(1))
        self.assertEqual(len(f.hass.services.calls), 1)
        self.assertNotEqual(f.results()[-1]["status"], "state_matches")
