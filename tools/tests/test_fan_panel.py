"""Fan panel contract and authorization races; no physical actuator is used."""

import asyncio
from copy import deepcopy
from dataclasses import replace
import importlib
import json
from types import SimpleNamespace as NS
import unittest

import test_entity_control as shared
import test_fan_speed_choice as speed_fixture
import test_ha_layout as base

codec = shared.codec
fan = importlib.import_module("_atmosfera_test.fan_domain")
ACTION = {"kind": "control", "control": "fan"}
KINDS = ["light", "number", "choice", "cover", "fan"]
SERVICES = ["fan." + service for service in (
    "turn_on", "turn_off", "set_percentage", "set_preset_mode", "oscillate", "set_direction")]


def environment():
    state = base.State("fan.test", "on", {"supported_features": 63, "percentage_step": 100 / 3,
        "percentage": 33, "preset_modes": [" Eco ", "Żółty"], "preset_mode": None,
        "oscillating": False, "direction": "forward"})
    hass, _ = base.environment(states=[state], services=SERVICES)
    entity = NS(entity_id=state.entity_id, speed_count=3)
    hass.data = {"fan": NS(get_entity=lambda identifier: entity if identifier == state.entity_id else None)}
    return hass, state, entity


class FanPanelModelTests(unittest.TestCase):
    def setUp(self):
        fixture = speed_fixture.core_math_fixture()
        fixture.start()
        self.addCleanup(fixture.stop)
        self.hass, self.state, self.entity = environment()

    def test_discrete_domain_uses_core_oracle_and_preserves_exact_preset_names(self):
        for count in range(1, 8):
            self.entity.speed_count = count
            self.state.attributes["percentage_step"] = 100 / count
            domain = fan.FanDomain.from_ha(self.hass, self.state)
            self.assertEqual(domain.speeds, tuple(speed_fixture.SPEEDS[count]))
            self.assertEqual(domain.presets, (" Eco ", "Żółty"))
            self.assertEqual(fan.FanDomain.from_descriptor(domain.descriptor()), domain)
        self.assertEqual(domain.service_action("preset", 0), ("set_preset_mode", {"preset_mode": " Eco "}))

    def test_bad_optional_catalogue_leaves_other_controls_available(self):
        for options in ([], ["x"] * 9, ["x", "x"], ["ą" * 17], None):
            self.state.attributes["preset_modes"] = options
            domain = fan.FanDomain.from_ha(self.hass, self.state)
            self.assertEqual(domain.presets, ())
            self.assertTrue(domain.turn_on and domain.turn_off and domain.oscillate and domain.direction)
            self.assertEqual(domain.speeds, (0, 33, 66, 100))
        self.entity.speed_count = 100
        self.state.attributes["percentage_step"] = 1
        self.assertEqual(fan.FanDomain.from_ha(self.hass, self.state).speeds, ())
        self.assertEqual(fan.FanDomain.from_ha(self.hass, self.state).turn_on, True)

    def test_unknown_is_not_manual_false_forward_or_zero(self):
        domain = fan.FanDomain.from_ha(self.hass, self.state)
        observation = fan.FanObservation.from_ha(self.state, domain)
        self.assertTrue(observation.preset_known)
        self.assertIsNone(observation.preset_index)
        self.state.attributes.pop("preset_mode")
        self.state.attributes.update(percentage=None, oscillating=0, direction="unknown")
        observation = fan.FanObservation.from_ha(self.state, domain)
        self.assertEqual(observation, fan.FanObservation("on"))
        for operation in ("speed", "preset", "oscillation", "direction"):
            self.assertFalse(observation.can_command(domain, operation))
        self.assertTrue(observation.can_command(domain, "power"))
        self.state.state = "unavailable"
        self.assertEqual(fan.FanObservation.from_ha(self.state, domain), fan.FanObservation())

    def test_off_retains_reported_attributes_and_noncanonical_speed_is_not_rounded(self):
        self.state.state = "off"
        self.state.attributes.update(percentage=34, preset_mode="Żółty", oscillating=True, direction="reverse")
        domain = fan.FanDomain.from_ha(self.hass, self.state)
        observed = fan.FanObservation.from_ha(self.state, domain)
        self.assertEqual((observed.percentage, observed.preset_index, observed.oscillating, observed.direction),
                         (34, 1, True, "reverse"))
        self.assertTrue(observed.can_command(domain, "speed"))

    def test_power_only_and_missing_service_do_not_invent_capability(self):
        self.state.attributes["supported_features"] = 48
        domain = fan.FanDomain.from_ha(self.hass, self.state)
        self.assertEqual(domain.descriptor(), {"turn_on": True, "turn_off": True, "oscillate": False,
                         "direction": False, "speeds": [], "presets": []})
        self.hass.services.names.remove("fan.turn_on")
        self.assertFalse(fan.FanDomain.from_ha(self.hass, self.state).turn_on)
        self.hass.services.names.remove("fan.turn_off")
        with self.assertRaises(fan.FanDomainError):
            fan.FanDomain.from_ha(self.hass, self.state)

    def test_layout_requires_explicit_fan_action_and_catalogue_returns_all_fields(self):
        item = base.card(entity="fan.test", action=ACTION)
        doc = base.document([item]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        for entity, action, version in (("light.test", ACTION, 3), ("fan.test", ACTION, 2),
                ("fan.test", ACTION | {"property": "percentage"}, 3),
                ("fan.test", ACTION | {"data": {}}, 3)):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        meta = base.cards._fan_control_metadata(self.hass, self.state)["fan_control"]
        self.assertEqual(meta["caps"], fan.FanDomain.from_ha(self.hass, self.state).descriptor())
        self.assertEqual(meta["state"]["percentage"], 33)
        self.assertIsNone(base.cards.resolve_action(self.hass, item))
        self.assertIn("fan", base.layout.device_profile()["schema_control_types"])
        for supported in (False, True):
            payload = base.cards.presentation_payload(self.hass, [item], fan_control_supported=supported,
                                                     press_enabled_supported=True)
            row = payload["cards"][2]
            self.assertEqual(row.get("control_kind"), "fan" if supported else None)
            if not supported:
                self.assertIs(row["press_enabled"], False)
        self.state.state = "unavailable"
        payload = base.cards.presentation_payload(self.hass, [item], fan_control_supported=True)
        self.assertEqual(payload["cards"][2]["control_kind"], "fan")


class FanPanelCodecTests(unittest.TestCase):
    def state(self):
        identity = dict(channel="a" * 32, token="b" * 32, open_seq=1, slot=31,
                        card_id="fan31", revision=10, control_kind="fan")
        return codec.envelope("grant", **identity, state_seq=1, ttl_ms=30000, title="Wentylator",
            fan_state="on", available=True, percentage=33, preset_index=None, preset_known=True,
            oscillating=False, direction="forward", state_generation=1,
            fan_caps={"turn_on": True, "turn_off": True, "oscillate": True, "direction": True,
                      "speeds": [0, 33, 66, 100], "presets": ["Eco", "Sleep"]})

    def command(self):
        identity = {key: self.state()[key] for key in codec.SELECTION}
        return codec.envelope("command", **identity, command_seq=1, op="power", target_index=1,
                              expected_state_generation=1)

    def test_all_fan_envelopes_and_old_capabilities_roundtrip(self):
        state, command = self.state(), self.command()
        opening = {key: state[key] for key in codec.OPEN}
        values = [state, state | {"kind": "state"}, codec.envelope("open", **opening),
                  codec.envelope("cancel_open", **opening, reason="user"),
                  *(command | {"op": op} for op in fan.OPERATIONS)]
        for kinds in (["light", "number"], ["light", "number", "fan"], KINDS):
            values.append(codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=kinds))
        for value in values:
            self.assertEqual(codec.decode(codec.encode(value)), value)
        max_state = state | {"title": "ą" * 80, "fan_caps": state["fan_caps"] | {"presets": [str(i) + "ą" * 15 for i in range(8)]}}
        self.assertLess(len(codec.encode(max_state).encode()), 2048)

    def test_bad_snapshot_fields_types_and_knownness_fail_closed(self):
        state = self.state()
        for change in ({"available": 1}, {"available": False}, {"fan_state": "unavailable"},
                {"percentage": True}, {"percentage": 33.0}, {"percentage": -1}, {"percentage": 101},
                {"preset_known": False, "preset_index": 0}, {"preset_index": 2}, {"preset_index": True},
                {"oscillating": 0}, {"direction": "left"}, {"state_generation": True}, {"extra": 0},
                {"fan_state": "unknown", "available": False}):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(state | change))
        unknown = state | fan.FanObservation().descriptor()
        self.assertEqual(codec.decode(codec.encode(unknown)), unknown)
        for change in ({"turn_on": 1}, {"speeds": [0, 33, 33, 100]}, {"speeds": [0, True, 100]},
                {"speeds": [1, 100]}, {"presets": ["a"] * 9}, {"presets": ["x", "x"]},
                {"direction": False}, {"oscillate": False}):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(state | {"fan_caps": state["fan_caps"] | change}))

    def test_command_is_absolute_bounded_and_cannot_carry_a_service(self):
        command = self.command()
        for change in ({"op": "toggle"}, {"target_index": True}, {"target_index": 2},
                {"target_index": -1}, {"op": "speed", "target_index": 8},
                {"op": "preset", "target_index": 8}, {"expected_state_generation": 0},
                {"expected_state_generation": True}, {"service": "fan.turn_on"}, {"value": 100}):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(command | change))


class FanPanelOwnerTests(unittest.IsolatedAsyncioTestCase):
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
        fixture = speed_fixture.core_math_fixture()
        fixture.start()
        self.addCleanup(fixture.stop)
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.hass, self.state, self.entity = environment()
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

    async def open(self, seq=1, control="fan"):
        return await shared.NumberOwnerTests.open(self, seq, control)

    def command(self, seq=1, op="power", target=0, **changes):
        selected = self.owner._selection
        return codec.envelope("command", **selected.identity, command_seq=seq, op=op, target_index=target,
                              expected_state_generation=selected.domain_state[2]) | changes

    async def test_five_facets_dispatch_exact_services_once_with_original_context(self):
        grant = await self.open()
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual((grant["percentage"], grant["preset_known"], grant["preset_index"]), (33, True, None))
        for seq, op, target in ((1, "power", 0), (2, "power", 1), (3, "speed", 2),
                                (4, "preset", 0), (5, "oscillation", 1), (6, "direction", 1)):
            message = self.command(seq, op, target)
            await self.send(message)
            await self.send(message)
            self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual([args for args, _ in self.hass.services.calls], [
            ("fan", "turn_off", {"entity_id": "fan.test"}), ("fan", "turn_on", {"entity_id": "fan.test"}),
            ("fan", "set_percentage", {"entity_id": "fan.test", "percentage": 66}),
            ("fan", "set_preset_mode", {"entity_id": "fan.test", "preset_mode": " Eco "}),
            ("fan", "oscillate", {"entity_id": "fan.test", "oscillating": True}),
            ("fan", "set_direction", {"entity_id": "fan.test", "direction": "reverse"})])
        self.assertTrue(all(kwargs["context"] is self.user for _, kwargs in self.hass.services.calls))
        self.assert_terminal_order()

    async def test_already_matched_is_noop_and_missing_feedback_is_not_success(self):
        await self.open()
        await self.send(self.command(op="power", target=1))
        self.assertEqual(self.results()[-1]["status"], "already_matched")
        self.assertEqual(self.hass.services.calls, [])
        self.apply = False
        await self.send(self.command(2, "speed", 3))
        self.assertEqual(self.results()[-1]["status"], "not_confirmed")
        self.assertEqual(self.state.attributes["percentage"], 33)
        self.assert_terminal_order()

    async def test_known_percentage_outside_catalogue_can_select_exact_target(self):
        self.state.attributes["percentage"] = 67
        grant = await self.open()
        self.assertEqual(grant["percentage"], 67)
        self.assertEqual(grant["fan_caps"]["speeds"], [0, 33, 66, 100])
        await self.send(self.command(op="speed", target=1))
        self.assertEqual(self.hass.services.calls[0][0],
                         ("fan", "set_percentage", {"entity_id": "fan.test", "percentage": 33}))
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual(self.state.attributes["percentage"], 33)

    async def test_any_facet_ABA_during_authorization_rejects_old_generation(self):
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command(op="speed", target=2)), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("on", oscillating=True)
        self.change("on", oscillating=False)
        self.auth_gate.set()
        await asyncio.wait_for(self.owner._selection.command.task, .4)
        self.assertEqual(self.owner._selection.domain_state[2], 3)
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["reason"], "stale_state")

    async def test_capability_ABA_during_open_retires_token(self):
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        task = asyncio.create_task(self.open())
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("on", preset_modes=["Other"])
        self.change("on", preset_modes=[" Eco ", "Żółty"])
        self.auth_gate.set()
        await asyncio.wait_for(task, .4)
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])
        self.assertFalse(any(value["kind"] == "grant" for value in self.outputs))

    async def test_live_service_loss_before_dispatch_closes_without_execution(self):
        await self.open()
        message = self.command(op="oscillation", target=1)
        self.hass.services.names.remove("fan.oscillate")
        with self.assertRaisesRegex(codec.ProtocolError, "capabilities_changed"):
            await self.send(message)
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_unknown_facet_cannot_execute_but_power_remains_available(self):
        self.state.attributes.update(percentage=None, oscillating=None, direction=None)
        self.state.attributes.pop("preset_mode")
        await self.open()
        for seq, operation in enumerate(("speed", "preset", "oscillation", "direction"), 1):
            await self.send(self.command(seq, operation, 0))
            self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assertEqual(self.hass.services.calls, [])
        await self.send(self.command(5, "power", 0))
        self.assertEqual(self.results()[-1]["status"], "state_matches")

    async def test_denied_permission_and_changed_revision_never_execute(self):
        await self.open()
        self.allowed = False
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["reason"], "unauthorized")
        self.allowed = True
        self.context = replace(self.context, revision=self.context.revision + 1)
        with self.assertRaisesRegex(codec.ProtocolError, "selection_changed"):
            await self.send(self.command(2))
        self.assertEqual(self.hass.services.calls, [])


class FanPanelTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_fan_is_admitted_only_by_actual_native_capability(self):
        for extended in (False, True):
            fixture = shared.NumberModelTransportTests()
            bridge = fixture.generic_bridge()
            original = bridge.runtime.client.execute_service
            async def execute(action, data, **kwargs):
                result = await original(action, data, **kwargs)
                if extended and action.name == "entity_control_get_status":
                    value = json.loads(result.response_data)
                    value["control_kinds"].append("fan")
                    result.response_data = shared.wire(value).encode()
                return result
            bridge.runtime.client.execute_service = execute
            transport = shared.integration.transport.LightControlTransport(bridge)
            try:
                self.assertTrue(await transport.async_negotiate())
                self.assertEqual(transport.fan_supported, extended)
                transport.invalidate_connection()
                self.assertFalse(transport.fan_supported)
            finally:
                await transport.async_shutdown()
