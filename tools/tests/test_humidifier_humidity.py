"""Integer target humidity reuses Number; measured humidity and power are separate."""

import asyncio
from copy import deepcopy
import importlib
from types import SimpleNamespace as NS
import unittest

import test_ha_layout as base
import test_entity_control as shared

number = importlib.import_module("_atmosfera_test.number_domain")
ACTION = number.HUMIDITY_ACTION


def humidifier():
    state = base.State("humidifier.test", "off", {"min_humidity": 30, "max_humidity": 70,
        "humidity": 45, "current_humidity": 99, "mode": "eco", "supported_features": 0})
    hass, _ = base.environment(states=[state], services=["humidifier.set_humidity"])
    return hass, state


class HumidityModelTests(unittest.TestCase):
    def test_explicit_v3_humidifier_only_and_integer_static_service(self):
        item = base.card(entity="humidifier.test", action=deepcopy(ACTION))
        doc = base.document([item]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_humidifier_humidity"])
        for entity, action, version in (("humidifier.test", ACTION, 2), ("number.test", ACTION, 3),
            ("light.test", ACTION, 3), ("humidifier.test", ACTION | {"data": {}}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        for value in (-1, 101, True, 45.5):
            with self.subTest(value=value), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action({"kind": "service", "service": "humidifier.set_humidity",
                    "data": {"humidity": value}}, "humidifier.test", layout_version=3)

    def test_omitted_step_uses_core_integer_contract_and_target_not_measurement(self):
        hass, state = humidifier()
        descriptor = number.number_domain(hass, state, "humidity")
        self.assertEqual(descriptor.descriptor(), {"schema": "numeric_steps_v1", "min": "30", "max": "70",
            "step": "1", "unit": "%", "max_index": 40})
        self.assertEqual(number.number_state(state, "humidity"), 45)
        self.assertEqual(base.cards._number_control_metadata(hass, state, "humidity")["humidifier_humidity"]["index"], 15)
        item = base.card(entity=state.entity_id, action=ACTION)
        for lang, expected in (("pl-PL", "Cel 45 %"), ("en-US", "Target 45 %")):
            payload = base.cards.presentation_payload(hass, [item], language=lang, number_control_supported=True)
            self.assertEqual(payload["cards"][2]["subtitle"], expected)
        fields = base.cards.entity_actions(hass, state)[0]["fields"]["humidity"]
        self.assertEqual(fields, {"type": "number", "min": 30, "max": 70, "step": 1, "required": True})

    def test_exact_step_tail_and_zero_hundred_endpoints_are_not_rounded(self):
        hass, state = humidifier()
        state.attributes.update(min_humidity=0, max_humidity=100, target_humidity_step=5.0)
        d = number.number_domain(hass, state, "humidity")
        self.assertEqual((d.observed_index(0), d.observed_index(100), d.observed_index(99)), (0, 20, None))
        self.assertIs(type(d.service_value(20, current=d)), int)
        state.attributes.update(min_humidity=30, max_humidity=71, target_humidity_step=5)
        d = number.number_domain(hass, state, "humidity")
        self.assertEqual((d.max_index, d.value_at(d.max_index), d.observed_index(71)), (8, 70, None))

    def test_missing_malformed_or_fractional_bounds_and_steps_fail_closed(self):
        for patch in ({"min_humidity": None}, {"min_humidity": -1}, {"max_humidity": 101},
            {"min_humidity": 80}, {"min_humidity": 30.5}, {"max_humidity": True}, {"min_humidity": "30"},
            {"target_humidity_step": None}, {"target_humidity_step": True}, {"target_humidity_step": .5},
            {"target_humidity_step": 0}, {"target_humidity_step": float("inf")}, {"target_humidity_step": "5"}):
            hass, state = humidifier(); state.attributes.update(patch)
            with self.subTest(patch=patch):
                self.assertEqual(base.cards._number_control_metadata(hass, state, "humidity"), {})
                self.assertEqual(base.cards.entity_actions(hass, state), [])
        hass, state = humidifier(); del state.attributes["min_humidity"]
        self.assertEqual(base.cards._number_control_metadata(hass, state, "humidity"), {})

    def test_unknown_off_grid_target_or_unknown_power_never_invents_a_value(self):
        hass, state = humidifier(); state.attributes["target_humidity_step"] = 5
        d = number.number_domain(hass, state, "humidity")
        for value in (None, True, "45", "unknown", 44, 99, 45.5):
            state.attributes["humidity"] = value
            with self.subTest(value=value):
                self.assertIsNone(d.observed_index(number.number_state(state, "humidity")))
        state.attributes["humidity"] = 45
        for power in ("unknown", "unavailable", "bad"):
            state.state = power
            self.assertIsNone(number.number_state(state, "humidity"))


class HumidityOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.NumberOwnerTests()
        await self.f.asyncSetUp()
        f = self.f
        f.hass, f.state = humidifier()
        f.state.attributes["target_humidity_step"] = 5
        f.owner.hass = f.hass
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        def change(value, **attrs):
            f.state.attributes.update(humidity=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))
        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["humidity"])
        f.change = change
        f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_one_exact_integer_step_keeps_mode_power_and_measurement(self):
        f = self.f
        grant = await f.open()
        self.assertEqual((grant["value_text"], grant["domain"]["unit"], grant["index"]), ("45", "%", 3))
        command = f.command()
        await f.send(command); await f.send(command)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("humidifier", "set_humidity", {"entity_id": "humidifier.test", "humidity": 50}))
        self.assertIs(type(args[2]["humidity"]), int)
        self.assertIs(kwargs["context"], f.user)
        self.assertEqual((f.state.state, f.state.attributes["mode"], f.state.attributes["current_humidity"]), ("off", "eco", 99))
        self.assertEqual(f.results()[-1]["status"], "state_matches")
        f.assert_terminal_order()

    async def test_target_ABA_during_authorization_refuses_stale_step(self):
        f = self.f; await f.open()
        f.auth_gate = asyncio.Event(); f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command()), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change(50); f.change(45); f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_bound_or_step_change_revokes_without_service_and_unknown_disables(self):
        f = self.f
        f.state.attributes["humidity"] = None
        grant = await f.open()
        self.assertEqual((grant["index"], grant["available"], grant["value_text"]), (None, False, "--"))
        f.change(45); await f.owner.async_state_changed()
        close = f.change(45, target_humidity_step=1)
        self.assertEqual(close["reason"], "capabilities_changed")
        await f.open(seq=2)
        close = f.change(45, max_humidity=65)
        self.assertEqual(close["reason"], "capabilities_changed")
        self.assertEqual(f.hass.services.calls, [])

    async def test_service_loss_blocks_dispatch(self):
        f = self.f; await f.open()
        command = f.command(); f.hass.services.names.clear()
        with self.assertRaises(shared.codec.ProtocolError):
            await f.send(command)
        self.assertEqual(f.hass.services.calls, [])
