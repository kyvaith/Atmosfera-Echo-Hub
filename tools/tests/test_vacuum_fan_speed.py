"""Vacuum suction uses exact observed levels, independently of activity."""

import asyncio
import importlib
import unittest
from copy import deepcopy
from types import SimpleNamespace as NS
from unittest.mock import patch

import test_choice_control as shared
import test_ha_layout as base

choice = importlib.import_module("_atmosfera_test.choice_domain")
ACTION = {"kind": "control", "control": "choice", "property": "fan_speed"}
OPTIONS = ["quiet", "normal", " Żółty "]


class VacuumModelTests(unittest.TestCase):
    def setUp(self):
        self.state = base.State("vacuum.test", "docked", {"supported_features": 8192 | 32,
            "fan_speed_list": OPTIONS.copy(), "fan_speed": "quiet"})
        self.hass, _ = base.environment(states=[self.state], services=["vacuum.set_fan_speed", "vacuum.start"])

    def test_explicit_v3_and_domain_and_exact_registered_service(self):
        doc = base.document([base.card(entity="vacuum.test", action=ACTION)]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_vacuum_fan_speed"])
        for entity, action, version in (("fan.test", ACTION, 3), ("vacuum.test", ACTION, 2),
            ("vacuum.test", ACTION | {"data": {}}, 3), ("vacuum.test", ACTION | {"property": "state"}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "fan_speed"),
            {"vacuum_fan_speed": {"options": OPTIONS, "index": 0}})
        self.hass.services.names.remove("vacuum.set_fan_speed")
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "fan_speed"), {})

    def test_known_activities_do_not_change_suction_and_none_is_never_empty(self):
        for activity in choice.VACUUM_STATES:
            self.state.state = activity
            self.assertEqual(choice.choice_state("vacuum.test", activity, self.state.attributes, "fan_speed"), "quiet")
        for value in (None, 0, False, "other"):
            self.state.attributes["fan_speed"] = value
            d = choice.choice_domain("vacuum.test", self.state.attributes, "fan_speed")
            self.assertIsNone(d.observed_index(choice.choice_state("vacuum.test", "docked", self.state.attributes, "fan_speed")))
            self.assertFalse(choice.choice_is_empty("vacuum.test", "docked", self.state.attributes, "fan_speed"))
        self.assertIsNone(choice.choice_state("vacuum.test", "unavailable", self.state.attributes, "fan_speed"))
        self.state.attributes.update(fan_speed_list=["none", *OPTIONS], fan_speed="none")
        self.state.state = "docked"
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "fan_speed")["vacuum_fan_speed"]["index"], 0)

    def test_list_and_feature_boundaries_preserve_ordinary_start(self):
        for options in ([], OPTIONS * 3, ["same", "same"], None, "quiet", tuple(OPTIONS), ["x" * 33], ["bad\n"]):
            self.state.attributes["fan_speed_list"] = options
            self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "fan_speed"), {})
        self.state.attributes.update(fan_speed_list=OPTIONS, supported_features=8192)
        actions = {a["service"]: a["fields"] for a in base.cards.entity_actions(self.hass, self.state)}
        self.assertEqual(actions, {"vacuum.start": {}})
        for feature in (0, True, -1, "32"):
            self.state.attributes["supported_features"] = feature
            self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state, "fan_speed"), {})
        self.state.attributes["supported_features"] = 32 | 8192
        fields = {a["service"]: a["fields"] for a in base.cards.entity_actions(self.hass, self.state)}
        self.assertEqual(fields["vacuum.set_fan_speed"], {"fan_speed": {"type": "select", "options": OPTIONS, "required": True}})
        base.cards.validate_live_action(self.hass, self.state, {"service": "vacuum.set_fan_speed", "data": {"fan_speed": " Żółty "}})

    def test_translation_never_alters_raw_values_and_collisions_fall_back(self):
        d = choice.choice_domain("vacuum.test", self.state.attributes, "fan_speed")
        self.assertEqual(choice.choice_labels(d, "fan_speed", "pl-PL"), ("Cicha", "Normalna", " Żółty "))
        self.assertEqual(choice.choice_labels(choice.ChoiceDomain(("quiet", "silent")), "fan_speed", "pl"), ("quiet", "silent"))
        self.hass.entity_registry.entries["vacuum.test"] = NS(platform="demo", translation_key="unit")
        translations = {"component.demo.entity.vacuum.unit.state_attributes.fan_speed.state.normal": "HA moc"}
        with patch.object(base.cards, "async_get_cached_translations", side_effect=lambda _h, _l, category: translations if category == "entity" else {}):
            self.assertEqual(base.cards.choice_control_labels(self.hass, self.state, d, "fan_speed", "pl"), ("Cicha", "HA moc", " Żółty "))
        self.assertEqual(d.options, tuple(OPTIONS))


class VacuumOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.ChoiceOwnerTests()
        await self.f.asyncSetUp()
        f = self.f
        f.state = base.State("vacuum.test", "docked", {"supported_features": 32,
            "fan_speed_list": OPTIONS.copy(), "fan_speed": "quiet"})
        f.hass.states.items = {f.state.entity_id: f.state}
        f.hass.services.names = {"vacuum.set_fan_speed", "vacuum.start", "vacuum.return_to_base"}
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        def change(value, activity=None, **attrs):
            if activity is not None:
                f.state.state = activity
            f.state.attributes.update(fan_speed=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))
        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["fan_speed"])
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

    async def test_one_exact_unicode_command_with_context_and_no_activity_command(self):
        f = self.f
        await f.open()
        value = f.command(2)
        await self.send(value)
        await self.send(value)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("vacuum", "set_fan_speed", {"entity_id": "vacuum.test", "fan_speed": " Żółty "}))
        self.assertIs(kwargs["context"], f.user)
        self.assertEqual(f.state.state, "docked")
        self.assertEqual(f.results()[-1]["status"], "state_matches")

    async def test_held_aba_never_revives_input(self):
        f = self.f
        await f.open()
        f.auth_gate = asyncio.Event()
        f.auth_entered.clear()
        await f.owner.async_handle(f.owner._encode(f.command(2)), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change("normal")
        f.change("quiet")
        f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_capability_change_revokes_and_no_feedback_is_not_confirmation(self):
        f = self.f
        await f.open()
        self.assertEqual(f.change("quiet", fan_speed_list=list(reversed(OPTIONS)))["reason"], "capabilities_changed")
        await f.open(seq=2)
        self.assertEqual(f.change("quiet", supported_features=0)["reason"], "capabilities_changed")
        f.change("quiet", supported_features=32)
        await f.open(seq=3)
        f.apply = False
        await self.send(f.command(1))
        self.assertEqual(len(f.hass.services.calls), 1)
        self.assertNotEqual(f.results()[-1]["status"], "state_matches")
