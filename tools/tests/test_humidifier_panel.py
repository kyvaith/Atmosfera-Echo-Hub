"""Dedicated humidity panel: exact domain, shared session and source authority."""

import asyncio
from copy import deepcopy
from dataclasses import replace
import importlib
import json
import unittest

import test_entity_control as shared
import test_ha_layout as base

codec = shared.codec
humidifier = importlib.import_module("_atmosfera_test.humidifier_domain")
ACTION = {"kind": "control", "control": "humidifier"}
KINDS = ["light", "number", "choice", "cover", "fan", "humidifier"]
SERVICES = ["humidifier." + service for service in ("turn_on", "turn_off", "set_humidity", "set_mode")]


def environment():
    state = base.State("humidifier.test", "on", {"supported_features": 1, "min_humidity": 30,
        "max_humidity": 80, "target_humidity_step": 5, "humidity": 45, "current_humidity": 42.5,
        "available_modes": [" Eco ", "Żółty"], "mode": " Eco ", "device_class": "dehumidifier"})
    hass, _ = base.environment(states=[state], services=SERVICES)
    return hass, state


class HumidifierModelTests(unittest.TestCase):
    def setUp(self):
        self.hass, self.state = environment()

    def test_exact_integer_lattice_and_complete_mode_names(self):
        domain = humidifier.HumidifierDomain.from_ha(self.hass, self.state)
        self.assertEqual(domain.numeric_descriptor(), {"schema": "numeric_steps_v1", "min": "30",
            "max": "80", "step": "5", "unit": "%", "max_index": 10})
        self.assertEqual(domain.modes, (" Eco ", "Żółty"))
        self.assertEqual(domain.device_class, "dehumidifier")
        self.assertEqual(domain.service_action("humidity", 10), ("set_humidity", {"humidity": 80}))
        self.assertEqual(domain.service_action("mode", 0), ("set_mode", {"mode": " Eco "}))
        self.state.attributes.pop("target_humidity_step")
        self.assertEqual(humidifier.HumidifierDomain.from_ha(self.hass, self.state).humidity.max_index, 50)

    def test_bad_optional_limits_and_modes_do_not_disable_power(self):
        for target_step in (None, True, .5, 0, "1", float("inf")):
            self.state.attributes.update(target_humidity_step=target_step, available_modes=["x"] * 9)
            domain = humidifier.HumidifierDomain.from_ha(self.hass, self.state)
            self.assertIsNone(domain.humidity)
            self.assertEqual(domain.modes, ())
            self.assertTrue(domain.turn_on and domain.turn_off)
        self.hass.services.names = set()
        with self.assertRaises(humidifier.HumidifierDomainError):
            humidifier.HumidifierDomain.from_ha(self.hass, self.state)

    def test_modes_require_feature_and_actual_service_and_missing_class_stays_unknown(self):
        self.state.attributes.update(supported_features=0, device_class="invented")
        domain = humidifier.HumidifierDomain.from_ha(self.hass, self.state)
        self.assertEqual((domain.modes, domain.device_class), ((), "unknown"))
        self.state.attributes["supported_features"] = 1
        self.hass.services.names.remove("humidifier.set_mode")
        self.assertEqual(humidifier.HumidifierDomain.from_ha(self.hass, self.state).modes, ())

    def test_off_retains_actual_target_measurement_independent_and_unknown_not_zero(self):
        domain = humidifier.HumidifierDomain.from_ha(self.hass, self.state)
        self.state.state = "off"
        observed = humidifier.HumidifierObservation.from_ha(self.state, domain)
        self.assertEqual((observed.humidity_index, observed.humidity_text, observed.current_humidity), (3, "45", "42.5"))
        self.state.attributes.update(humidity=46, current_humidity=True, mode=None)
        observed = humidifier.HumidifierObservation.from_ha(self.state, domain)
        self.assertEqual((observed.humidity_index, observed.humidity_text, observed.current_humidity, observed.mode_index),
                         (None, "--", "", None))
        self.assertTrue(observed.can_command(domain, "power"))
        self.assertFalse(observed.can_command(domain, "humidity"))
        self.assertFalse(observed.can_command(domain, "mode"))
        self.state.state = "unavailable"
        self.assertEqual(humidifier.HumidifierObservation.from_ha(self.state, domain), humidifier.HumidifierObservation())

    def test_measurements_are_bounded_exact_and_not_command_state(self):
        domain = humidifier.HumidifierDomain.from_ha(self.hass, self.state)
        before = humidifier.HumidifierObservation.from_ha(self.state, domain)
        for raw, expected in ((0, "0"), (100, "100"), (0.000001, "0.000001"), (-1, ""),
                              (101, ""), (float("nan"), ""), (45.0000001, ""), ("42", "")):
            self.state.attributes["current_humidity"] = raw
            current = humidifier.HumidifierObservation.from_ha(self.state, domain)
            self.assertEqual(current.current_humidity, expected)
            self.assertEqual(current.command_state, before.command_state)

    def test_explicit_launcher_validation_projection_and_catalogue(self):
        item = base.card(entity="humidifier.test", action=ACTION)
        doc = base.document([item]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        for entity, action, version in (("fan.test", ACTION, 3), ("humidifier.test", ACTION, 2),
                ("humidifier.test", ACTION | {"property": "humidity"}, 3)):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        meta = base.cards._humidifier_control_metadata(self.hass, self.state)["humidifier_control"]
        self.assertEqual((meta["state"]["humidity_text"], meta["state"]["current_humidity"]), ("45", "42.5"))
        self.assertEqual(meta["humidity_domain"]["max_index"], 10)
        self.assertIsNone(base.cards.resolve_action(self.hass, item))
        for supported in (False, True):
            row = base.cards.presentation_payload(self.hass, [item], humidifier_control_supported=supported,
                press_enabled_supported=True)["cards"][2]
            self.assertEqual(row.get("control_kind"), "humidifier" if supported else None)
            if not supported:
                self.assertIs(row["press_enabled"], False)


class HumidifierCodecTests(unittest.TestCase):
    def state(self):
        hass, state = environment()
        domain = humidifier.HumidifierDomain.from_ha(hass, state)
        return codec.envelope("grant", channel="a" * 32, token="b" * 32, open_seq=1, slot=31,
            card_id="humidity31", revision=10, control_kind="humidifier", state_seq=1, ttl_ms=30000,
            title="Wilgotność", state_generation=1, humidity_domain=domain.numeric_descriptor(),
            device_class=domain.device_class, humidifier_caps=domain.descriptor(),
            **humidifier.HumidifierObservation.from_ha(state, domain).descriptor())

    def command(self):
        return codec.envelope("command", **{key: self.state()[key] for key in codec.SELECTION},
            command_seq=1, op="humidity", target_index=4, expected_state_generation=1)

    def test_all_envelopes_exact_schema_and_maximum_wire(self):
        state, command = self.state(), self.command()
        values = [state, state | {"kind": "state"}, codec.envelope("open", **{k: state[k] for k in codec.OPEN}),
                  command, command | {"op": "mode", "target_index": 1}, command | {"op": "power", "target_index": 0}]
        for kinds in (["light", "number"], ["light", "number", "humidifier"], KINDS):
            values.append(codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=kinds))
        for value in values:
            self.assertEqual(codec.decode(codec.encode(value)), value)
        maximum = state | {"title": "ą" * 80, "humidifier_caps": state["humidifier_caps"] | {"modes": [str(i) + "ą" * 15 for i in range(8)]}}
        self.assertLess(len(codec.encode(maximum).encode()), 2048)
        unknown = state | humidifier.HumidifierObservation().descriptor()
        self.assertEqual(codec.decode(codec.encode(unknown)), unknown)

    def test_strict_observations_and_domain_reject_malformed_or_invented_values(self):
        state = self.state()
        for change in ({"available": 1}, {"available": False}, {"humidifier_state": "unavailable"},
                {"humidity_index": True}, {"humidity_index": 11}, {"humidity_index": None},
                {"humidity_text": "45.0"}, {"humidity_text": 45}, {"humidity_domain": None},
                {"current_humidity": "42.50"}, {"current_humidity": "101"}, {"current_humidity": "NaN"},
                {"current_humidity": 42.5}, {"mode_index": 2}, {"mode_index": True},
                {"device_class": "mister"}, {"state_generation": True}, {"extra": 0},
                {"humidifier_state": "unknown", "available": False}):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(state | change))
        for change in ({"unit": "°C"}, {"step": "0.5", "max_index": 100}, {"min": "-1", "max_index": 16}):
            with self.subTest(domain=change), self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(state | {"humidity_domain": state["humidity_domain"] | change}))

    def test_absolute_command_cannot_carry_arbitrary_service_or_target_value(self):
        command = self.command()
        for change in ({"target_index": 101}, {"target_index": -1}, {"target_index": True},
                {"op": "toggle"}, {"op": "mode", "target_index": 8}, {"op": "power", "target_index": 2},
                {"expected_state_generation": 0}, {"service": "humidifier.turn_on"}, {"humidity": 50}):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(command | change))


class HumidifierOwnerTests(unittest.IsolatedAsyncioTestCase):
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    assert_terminal_order = shared.NumberOwnerTests.assert_terminal_order
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown

    def bind(self):
        capability = codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=KINDS)
        value = self.owner.prepare_bind(shared.wire(capability), epoch=1, runtime=self.runtime)
        self.owner.accept_bind(shared.wire(value), epoch=1, runtime=self.runtime)

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.hass, self.state = environment()
        self.owner.hass = self.hass
        self.card.update(entity_id=self.state.entity_id, action=deepcopy(ACTION))
        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate:
                await self.service_gate.wait()
            if not self.apply:
                return
            operation, data = args[1:3]
            if operation in ("turn_on", "turn_off"):
                self.change("on" if operation == "turn_on" else "off")
            else:
                self.change(self.state.state, **{key: value for key, value in data.items() if key != "entity_id"})
        self.hass.services.async_call = service

    async def open(self, seq=1, control="humidifier"):
        return await shared.NumberOwnerTests.open(self, seq, control)

    def command(self, seq=1, op="humidity", target=4, **changes):
        selected = self.owner._selection
        return codec.envelope("command", **selected.identity, command_seq=seq, op=op, target_index=target,
                              expected_state_generation=selected.domain_state[2]) | changes

    async def test_three_facets_send_exact_services_once_and_opening_does_nothing(self):
        grant = await self.open()
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual((grant["humidity_text"], grant["current_humidity"]), ("45", "42.5"))
        for seq, op, target in ((1, "power", 0), (2, "power", 1), (3, "humidity", 4), (4, "mode", 1)):
            message = self.command(seq, op, target)
            await self.send(message)
            await self.send(message)
            self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual([args for args, _ in self.hass.services.calls], [
            ("humidifier", "turn_off", {"entity_id": "humidifier.test"}),
            ("humidifier", "turn_on", {"entity_id": "humidifier.test"}),
            ("humidifier", "set_humidity", {"entity_id": "humidifier.test", "humidity": 50}),
            ("humidifier", "set_mode", {"entity_id": "humidifier.test", "mode": "Żółty"})])
        self.assertTrue(all(kwargs["context"] is self.user for _, kwargs in self.hass.services.calls))
        self.assert_terminal_order()

    async def test_measurement_changes_during_authorization_do_not_cancel_target(self):
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("on", current_humidity=40.1)
        self.change("on", current_humidity=41.2)
        self.assertEqual(self.owner._selection.domain_state[2], 1)
        self.auth_gate.set()
        await asyncio.wait_for(self.owner._selection.command.task, .4)
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual(self.outputs[-2]["current_humidity"], "41.2")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_target_ABA_during_authorization_rejects_even_same_final_value(self):
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("on", humidity=55)
        self.change("on", humidity=45)
        self.auth_gate.set()
        await asyncio.wait_for(self.owner._selection.command.task, .4)
        self.assertEqual(self.owner._selection.domain_state[2], 3)
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["reason"], "stale_state")

    async def test_capability_ABA_during_open_and_service_loss_revoke(self):
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        task = asyncio.create_task(self.open())
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("on", min_humidity=35)
        self.change("on", min_humidity=30)
        self.auth_gate.set()
        await asyncio.wait_for(task, .4)
        self.assertIsNone(self.owner._selection)
        self.assertFalse(any(value["kind"] == "grant" for value in self.outputs))
        await self.open(2)
        message = self.command()
        self.hass.services.names.remove("humidifier.set_humidity")
        with self.assertRaisesRegex(codec.ProtocolError, "capabilities_changed"):
            await self.send(message)
        self.assertEqual(self.hass.services.calls, [])

    async def test_unknown_facets_independent_power_noop_and_unconfirmed_not_success(self):
        self.state.attributes.update(humidity=None, mode=None, current_humidity=None)
        await self.open()
        for seq, op in ((1, "humidity"), (2, "mode")):
            await self.send(self.command(seq, op, 0))
            self.assertEqual(self.results()[-1]["reason"], "stale_state")
        await self.send(self.command(3, "power", 1))
        self.assertEqual(self.results()[-1]["status"], "already_matched")
        self.assertEqual(self.hass.services.calls, [])
        self.apply = False
        await self.send(self.command(4, "power", 0))
        self.assertEqual(self.results()[-1]["status"], "not_confirmed")
        self.assert_terminal_order()

    async def test_permission_and_revision_fence(self):
        await self.open()
        self.allowed = False
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["reason"], "unauthorized")
        self.allowed = True
        self.context = replace(self.context, revision=self.context.revision + 1)
        with self.assertRaisesRegex(codec.ProtocolError, "selection_changed"):
            await self.send(self.command(2))
        self.assertEqual(self.hass.services.calls, [])

    async def test_distinct_entity_rebinding_rejects_old_token_without_any_service(self):
        await self.open()
        message = self.command()
        other = base.State("humidifier.other", "on", deepcopy(self.state.attributes))
        self.hass.states.items[other.entity_id] = other
        self.card["entity_id"] = other.entity_id
        with self.assertRaisesRegex(codec.ProtocolError, "selection_changed"):
            await self.send(message)
        self.assertEqual(self.hass.services.calls, [])


class HumidifierTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_humidifier_requires_negotiated_native_capability(self):
        for extended in (False, True):
            bridge = shared.NumberModelTransportTests().generic_bridge()
            original = bridge.runtime.client.execute_service
            async def execute(action, data, **kwargs):
                result = await original(action, data, **kwargs)
                if extended and action.name == "entity_control_get_status":
                    value = json.loads(result.response_data)
                    value["control_kinds"].append("humidifier")
                    result.response_data = shared.wire(value).encode()
                return result
            bridge.runtime.client.execute_service = execute
            transport = shared.integration.transport.LightControlTransport(bridge)
            try:
                self.assertTrue(await transport.async_negotiate())
                self.assertEqual(transport.humidifier_supported, extended)
                transport.invalidate_connection()
                self.assertFalse(transport.humidifier_supported)
            finally:
                await transport.async_shutdown()
