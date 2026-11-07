"""Climate target humidity shares Number without borrowing measured humidity."""

import asyncio
import importlib
import unittest
from copy import deepcopy
from types import SimpleNamespace as NS

import test_entity_control as shared
import test_ha_layout as base

number = importlib.import_module("_atmosfera_test.number_domain")
ACTION = number.HUMIDITY_ACTION


def climate():
    state = base.State("climate.test", "auto", {"supported_features": 4, "humidity": 45,
        "min_humidity": 30, "max_humidity": 70, "current_humidity": 99, "temperature": 21.5})
    hass, _ = base.environment(states=[state], services=["climate.set_humidity"])
    return hass, state


class ClimateHumidityModelTests(unittest.TestCase):
    def test_explicit_v3_climate_and_feature_four_without_temperature_support(self):
        document = base.document([base.card(entity="climate.test", action=ACTION)]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(document), document)
        self.assertTrue(base.layout.device_profile()["schema_climate_humidity"])
        for entity, action, version in (("climate.test", ACTION, 2), ("fan.test", ACTION, 3),
            ("climate.test", ACTION | {"data": {}}, 3), ("climate.test", ACTION | {"control": "choice"}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        hass, state = climate()
        self.assertEqual(base.cards._number_control_metadata(hass, state, "humidity")["climate_humidity"]["index"], 15)
        self.assertEqual(base.cards._number_control_metadata(hass, state, "temperature"), {})
        self.assertEqual(base.cards.entity_actions(hass, state), [{"service": "climate.set_humidity", "fields": {
            "humidity": {"type": "number", "min": 30, "max": 70, "step": 1, "required": True}}}])

    def test_known_hvac_modes_keep_real_target_independent_of_current_measurement(self):
        hass, state = climate(); item = base.card(entity=state.entity_id, action=ACTION)
        for mode in ("off", "heat", "cool", "heat_cool", "auto", "dry", "fan_only"):
            state.state = mode
            self.assertEqual(number.number_state(state, "humidity"), 45)
            for lang, expected in (("pl", "Cel 45 %"), ("en", "Target 45 %")):
                payload = base.cards.presentation_payload(hass, [item], language=lang, number_control_supported=True)
                self.assertEqual(payload["cards"][2]["subtitle"], expected)
        for mode in ("unknown", "unavailable", "on", "bad"):
            state.state = mode; self.assertIsNone(number.number_state(state, "humidity"))

    def test_missing_feature_or_service_and_invalid_bounds_or_step_fail_closed(self):
        for patch in ({"supported_features": 0}, {"supported_features": True}, {"supported_features": 1},
            {"supported_features": "4"}, {"min_humidity": None}, {"min_humidity": 30.5},
            {"max_humidity": 101}, {"target_humidity_step": None}, {"target_humidity_step": .5}):
            hass, state = climate(); state.attributes.update(patch)
            with self.subTest(patch=patch):
                self.assertEqual(base.cards._number_control_metadata(hass, state, "humidity"), {})
                self.assertEqual(base.cards.entity_actions(hass, state), [])
        hass, state = climate(); hass.services.names.clear()
        self.assertEqual(base.cards._number_control_metadata(hass, state, "humidity"), {})

    def test_exact_steps_tail_and_static_integer_service_do_not_round_target(self):
        hass, state = climate(); state.attributes.update(target_humidity_step=5, max_humidity=71)
        domain = number.number_domain(hass, state, "humidity")
        self.assertEqual((domain.observed_index(70), domain.observed_index(71), domain.observed_index(None)), (8, None, None))
        for value in (True, 45.5, -1, 101):
            with self.subTest(value=value), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action({"kind": "service", "service": "climate.set_humidity", "data": {"humidity": value}}, "climate.test", layout_version=3)
        state.attributes["humidity"] = None
        self.assertIsNone(domain.observed_index(number.number_state(state, "humidity")))


class ClimateHumidityOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.NumberOwnerTests(); await self.f.asyncSetUp(); f = self.f
        f.hass, f.state = climate(); f.state.attributes["target_humidity_step"] = 5
        f.owner.hass = f.hass; f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        def change(value, **attrs):
            f.state.attributes.update(humidity=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))
        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["humidity"])
        f.change = change; f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_one_integer_target_call_retains_hvac_temperature_and_measurement(self):
        f = self.f; grant = await f.open()
        self.assertEqual((grant["value_text"], grant["domain"]["unit"], grant["index"]), ("45", "%", 3))
        command = f.command(); await f.send(command); await f.send(command)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("climate", "set_humidity", {"entity_id": "climate.test", "humidity": 50}))
        self.assertIs(type(args[2]["humidity"]), int); self.assertIs(kwargs["context"], f.user)
        self.assertEqual((f.state.state, f.state.attributes["temperature"], f.state.attributes["current_humidity"]), ("auto", 21.5, 99))
        self.assertEqual(f.results()[-1]["status"], "state_matches"); f.assert_terminal_order()

    async def test_target_ABA_during_authorization_cannot_reuse_expected_state(self):
        f = self.f; await f.open(); f.auth_gate = asyncio.Event(); f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command()), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change(50); f.change(45); f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, []); self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_unknown_disables_and_feature_or_range_change_revokes(self):
        f = self.f; f.state.attributes["humidity"] = None
        grant = await f.open(); self.assertEqual((grant["available"], grant["index"], grant["value_text"]), (False, None, "--"))
        f.change(45); await f.owner.async_state_changed()
        self.assertEqual(f.change(45, max_humidity=65)["reason"], "capabilities_changed")
        await f.open(seq=2)
        self.assertEqual(f.change(45, supported_features=0)["reason"], "capabilities_changed")
        self.assertEqual(f.hass.services.calls, [])
