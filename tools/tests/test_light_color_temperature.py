"""Precise Kelvin facets retain real state, mode and existing command fences."""

import asyncio
import importlib
import unittest
from copy import deepcopy
from types import SimpleNamespace as NS

import test_entity_control as shared
import test_ha_layout as base

number = importlib.import_module("_atmosfera_test.number_domain")
ACTION = number.COLOR_TEMPERATURE_ACTION


def light():
    state = base.State("light.test", "on", {"supported_color_modes": ["color_temp", "hs"],
        "color_mode": "color_temp", "min_color_temp_kelvin": 2000, "max_color_temp_kelvin": 6500,
        "color_temp_kelvin": 2700, "brightness": 127, "effect": "Solid"})
    hass, _ = base.environment(states=[state], services=["light.turn_on", "light.turn_off"])
    return hass, state


class KelvinModelTests(unittest.TestCase):
    def test_explicit_light_v3_and_actual_range_with_integer_kelvin_unit(self):
        document = base.document([base.card(entity="light.test", action=ACTION)]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(document), document)
        self.assertTrue(base.layout.device_profile()["schema_light_color_temperature"])
        for entity, action, version in (("climate.test", ACTION, 3), ("light.test", ACTION, 2),
            ("light.test", ACTION | {"data": {}}, 3), ("light.test", ACTION | {"control": "choice"}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        hass, state = light()
        self.assertEqual(number.number_domain(hass, state, "color_temp_kelvin").descriptor(),
            {"schema": "numeric_steps_v1", "min": "2000", "max": "6500", "step": "1", "unit": "K", "max_index": 4500})
        self.assertEqual(base.cards._number_control_metadata(hass, state, "color_temp_kelvin")["light_color_temperature"]["index"], 700)
        item = base.card(entity="light.test", action=ACTION)
        for lang in ("en-US", "pl-PL"):
            self.assertEqual(base.cards.presentation_payload(hass, [item], language=lang, number_control_supported=True)["cards"][2]["subtitle"], "2700 K")

    def test_invalid_or_missing_bounds_remove_only_optional_kelvin_field(self):
        for patch in ({"min_color_temp_kelvin": None}, {"max_color_temp_kelvin": True},
            {"min_color_temp_kelvin": 2000.5}, {"max_color_temp_kelvin": float("nan")},
            {"min_color_temp_kelvin": 10**400}, {"min_color_temp_kelvin": "2000"},
            {"min_color_temp_kelvin": 999}, {"max_color_temp_kelvin": 20001},
            {"min_color_temp_kelvin": 6600}, {"supported_color_modes": 1},
            {"supported_color_modes": ["brightness"]}, {"supported_color_modes": [["color_temp"]]}):
            hass, state = light(); state.attributes.update(patch)
            with self.subTest(patch=patch):
                self.assertEqual(base.cards._number_control_metadata(hass, state, "color_temp_kelvin"), {})
                actions = base.cards.entity_actions(hass, state)
                turn_on = next(action for action in actions if action["service"] == "light.turn_on")
                self.assertNotIn("color_temp_kelvin", turn_on["fields"])
                self.assertTrue(any(action["service"] == "light.turn_off" for action in actions))
        hass, state = light(); del state.attributes["min_color_temp_kelvin"]
        self.assertEqual(base.cards._number_control_metadata(hass, state, "color_temp_kelvin"), {})

    def test_current_kelvin_never_comes_from_retained_off_rgb_or_fractional_state(self):
        for power, mode, value in (("off", "color_temp", 2700), ("on", "hs", 2700),
            ("on", None, 2700), ("unavailable", "color_temp", 2700), ("on", "color_temp", None),
            ("on", "color_temp", "2700"), ("on", "color_temp", True),
            ("on", "color_temp", 2700.5), ("on", "color_temp", 6501)):
            hass, state = light(); state.state = power
            state.attributes.update(color_mode=mode, color_temp_kelvin=value)
            domain = number.number_domain(hass, state, "color_temp_kelvin")
            with self.subTest(power=power, mode=mode, value=value):
                self.assertIsNone(domain.observed_index(number.number_state(state, "color_temp_kelvin")))

    def test_non_round_kelvin_and_endpoints_are_exact_integers_not_mired_conversions(self):
        hass, state = light(); state.attributes.update(min_color_temp_kelvin=2001, max_color_temp_kelvin=6536)
        domain = number.number_domain(hass, state, "color_temp_kelvin")
        for value in (2001, 2701, 6536):
            index = domain.exact_index(value)
            self.assertEqual(domain.service_value(index, current=domain), value)
            self.assertIs(type(domain.service_value(index, current=domain)), int)
        fields = next(action for action in base.cards.entity_actions(hass, state) if action["service"] == "light.turn_on")["fields"]
        self.assertEqual(fields["color_temp_kelvin"], {"type": "number", "min": 2001, "max": 6536, "step": 1, "required": False})


class KelvinOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.NumberOwnerTests(); await self.f.asyncSetUp(); f = self.f
        f.hass, f.state = light(); f.owner.hass = f.hass
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        def change(value, **attrs):
            f.state.attributes.update(color_temp_kelvin=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))
        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["color_temp_kelvin"])
        f.change = change; f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_one_exact_kelvin_call_without_power_brightness_rgb_or_effect_parameters(self):
        f = self.f; grant = await f.open()
        self.assertEqual((grant["value_text"], grant["domain"]["unit"], grant["index"]), ("2700", "K", 700))
        command = f.command(); await f.send(command); await f.send(command)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("light", "turn_on", {"entity_id": "light.test", "color_temp_kelvin": 2701}))
        self.assertIs(type(args[2]["color_temp_kelvin"]), int)
        self.assertIs(kwargs["context"], f.user)
        self.assertEqual((f.state.state, f.state.attributes["brightness"], f.state.attributes["effect"]), ("on", 127, "Solid"))
        self.assertEqual(f.results()[-1]["status"], "state_matches"); f.assert_terminal_order()

    async def test_mode_ABA_while_authorizing_refuses_stale_kelvin_step(self):
        f = self.f; await f.open(); f.auth_gate = asyncio.Event(); f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command()), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change(2700, color_mode="hs"); f.change(2700, color_mode="color_temp"); f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_bound_or_capability_change_revokes_and_unknown_value_disables(self):
        f = self.f; f.state.attributes["color_temp_kelvin"] = None
        grant = await f.open()
        self.assertEqual((grant["available"], grant["index"], grant["value_text"]), (False, None, "--"))
        f.change(2700); await f.owner.async_state_changed()
        self.assertEqual(f.change(2700, max_color_temp_kelvin=6000)["reason"], "capabilities_changed")
        await f.open(seq=2)
        self.assertEqual(f.change(2700, supported_color_modes=["hs"])["reason"], "capabilities_changed")
        self.assertEqual(f.hass.services.calls, [])

    async def test_service_accepted_without_kelvin_feedback_is_not_a_match(self):
        f = self.f; f.apply = False; await f.open(); await f.send(f.command())
        self.assertEqual(f.results()[-1]["status"], "not_confirmed")
        self.assertEqual(f.state.attributes["color_temp_kelvin"], 2700)
