"""Actual loaded fan count selects exact Core speed percentages through Choice."""

import asyncio
import importlib
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from unittest.mock import patch

import test_choice_control as shared
import test_ha_layout as base

choice = importlib.import_module("_atmosfera_test.choice_domain")
ACTION = {"kind": "control", "control": "choice", "property": "percentage"}
ORACLE = json.loads((Path(__file__).parent / "fixtures/fan_speed_core_2026_7.json").read_text())
SPEEDS = {row["count"]: row["percentages"] for row in ORACLE["counts"]}


def core_math_fixture():
    """Offline boundary stub uses pinned installed-Core outputs, not local math."""
    module = ModuleType("homeassistant.util.percentage")
    def to_percentage(bounds, value):
        assert bounds[0] == 1
        return SPEEDS[bounds[1]][value]
    def to_speed(bounds, value):
        assert bounds[0] == 1
        return SPEEDS[bounds[1]].index(value)
    module.ranged_value_to_percentage = to_percentage
    module.percentage_to_ranged_value = to_speed
    return patch.dict(sys.modules, {module.__name__: module})


def fan(count=3):
    state = base.State("fan.test", "on", {"supported_features": 9, "percentage_step": 100 / count,
        "percentage": SPEEDS[count][1], "preset_mode": None, "preset_modes": ["eco", "sleep"]})
    hass, _ = base.environment(states=[state], services=["fan.set_percentage", "fan.set_preset_mode"])
    entity = NS(entity_id=state.entity_id, speed_count=count)
    hass.data = {"fan": NS(get_entity=lambda identifier: entity if identifier == state.entity_id else None)}
    return hass, state, entity


class FanSpeedModelTests(unittest.TestCase):
    def setUp(self):
        self.math = core_math_fixture(); self.math.start(); self.addCleanup(self.math.stop)

    def test_explicit_v3_fan_only_leaves_presets_and_direction_separate(self):
        doc = base.document([base.card(entity="fan.test", action=ACTION)]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_fan_speed"])
        for entity, action, version in (("light.test", ACTION, 3), ("fan.test", ACTION, 2),
            ("fan.test", ACTION | {"data": {}}, 3), ("fan.test", ACTION | {"control": "number"}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        self.assertEqual(choice.choice_service("fan.test"), ("set_preset_mode", "preset_mode"))
        self.assertEqual(choice.choice_service("fan.test", "direction"), ("set_direction", "direction"))

    def test_all_seven_counts_use_pinned_core_percentages_including_uneven_steps(self):
        for count in range(1, 8):
            hass, state, _ = fan(count)
            domain = choice.choice_domain(state.entity_id, state.attributes, "percentage", hass=hass)
            self.assertEqual(domain.options, tuple(map(str, SPEEDS[count])))
            metadata = base.cards._choice_control_metadata(hass, state, "percentage")["fan_speed"]
            self.assertEqual((metadata["speed_count"], metadata["index"]), (count, 1))
            self.assertEqual(choice.choice_labels(domain, "percentage", "pl"), tuple(str(value) + " %" for value in SPEEDS[count]))
        self.assertEqual(SPEEDS[3], [0, 33, 66, 100])
        self.assertEqual(SPEEDS[6], [0, 16, 33, 50, 66, 83, 100])

    def test_loaded_count_and_actual_step_are_required_without_guesses(self):
        for count, step in ((None, 100 / 3), (True, 100), (0, 100), (8, 12.5),
            (100, 1), (3, 33), (3, None), (3, True), (3, "33.333333333333336"), (3, float("nan"))):
            hass, state, entity = fan(); entity.speed_count = count; state.attributes["percentage_step"] = step
            with self.subTest(count=count, step=step):
                self.assertEqual(base.cards._choice_control_metadata(hass, state, "percentage"), {})
        hass, state, entity = fan(); hass.data.clear()
        self.assertEqual(base.cards._choice_control_metadata(hass, state, "percentage"), {})
        hass, state, entity = fan(); entity.entity_id = "fan.other"
        self.assertEqual(base.cards._choice_control_metadata(hass, state, "percentage"), {})

    def test_unknown_or_off_list_speed_is_not_rounded_or_inferred_from_power(self):
        hass, state, _ = fan(); domain = choice.choice_domain(state.entity_id, state.attributes, "percentage", hass=hass)
        for value in (None, True, "33", 33.0, 34, -1, 101):
            state.attributes["percentage"] = value
            self.assertIsNone(domain.observed_index(choice.choice_state(state.entity_id, state.state, state.attributes, "percentage")))
            self.assertFalse(choice.choice_is_empty(state.entity_id, state.state, state.attributes, "percentage"))
        for power in ("on", "off"):
            state.state = power; state.attributes["percentage"] = 66
            item = base.card(entity=state.entity_id, action=ACTION)
            for lang in ("en", "pl"):
                payload = base.cards.presentation_payload(hass, [item], language=lang, choice_control_supported=True)
                self.assertEqual(payload["cards"][2]["subtitle"], "66 %")
        state.state = "unavailable"
        self.assertIsNone(choice.choice_state(state.entity_id, state.state, state.attributes, "percentage"))

    def test_lost_capability_or_service_removes_only_speed_metadata(self):
        hass, state, _ = fan(); state.attributes["supported_features"] = 8
        self.assertEqual(base.cards._choice_control_metadata(hass, state, "percentage"), {})
        self.assertIn("choice_control", base.cards._choice_control_metadata(hass, state))
        state.attributes["supported_features"] = 9; hass.services.names.remove("fan.set_percentage")
        self.assertEqual(base.cards._choice_control_metadata(hass, state, "percentage"), {})
        self.assertIn("choice_control", base.cards._choice_control_metadata(hass, state))


class FanSpeedOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.math = core_math_fixture(); self.math.start(); self.addCleanup(self.math.stop)
        self.f = shared.ChoiceOwnerTests(); await self.f.asyncSetUp(); f = self.f
        f.hass, f.state, self.entity = fan(); f.owner.hass = f.hass
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        def change(value, **attrs):
            f.state.attributes.update(percentage=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))
        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["percentage"])
        f.change = change; f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_exact_integer_speed_and_zero_are_single_fenced_calls_without_other_operations(self):
        f = self.f; grant = await f.open()
        self.assertEqual((grant["options"], grant["index"]), (["0 %", "33 %", "66 %", "100 %"], 1))
        command = f.command(target=2); await f.send(command); await f.send(command)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("fan", "set_percentage", {"entity_id": "fan.test", "percentage": 66}))
        self.assertIs(type(args[2]["percentage"]), int); self.assertIs(kwargs["context"], f.user)
        self.assertEqual(f.results()[-1]["status"], "state_matches")
        await f.send(f.command(target=0, command_seq=2))
        self.assertEqual(f.hass.services.calls[-1][0][2], {"entity_id": "fan.test", "percentage": 0})
        self.assertEqual(f.state.attributes["preset_mode"], None)
        f.assert_terminal_order()

    async def test_speed_ABA_during_authorization_refuses_stale_choice(self):
        f = self.f; await f.open(); f.auth_gate = asyncio.Event(); f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command(target=2)), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change(66); f.change(33); f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_count_and_step_change_revokes_without_reviving_old_selection(self):
        f = self.f; await f.open(); self.entity.speed_count = 7
        close = f.change(33, percentage_step=100 / 7)
        self.assertEqual(close["reason"], "capabilities_changed")
        self.entity.speed_count = 3; f.change(33, percentage_step=100 / 3)
        self.assertIsNone(f.owner._selection)
        await f.open(seq=2)
        self.assertEqual(f.change(33, percentage_step=33)["reason"], "capabilities_changed")
        self.assertEqual(f.hass.services.calls, [])

    async def test_unknown_disables_and_service_acceptance_without_feedback_is_not_a_match(self):
        f = self.f; f.state.attributes["percentage"] = None
        grant = await f.open(); self.assertEqual((grant["available"], grant["index"]), (False, None))
        f.change(33); await f.owner.async_state_changed(); f.apply = False
        await f.send(f.command(target=3))
        self.assertEqual(f.results()[-1]["status"], "not_confirmed")
