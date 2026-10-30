"""Number Phase B host fakes; no real HA, SDK, connection or device."""

import asyncio
from copy import deepcopy
import importlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

import test_ha_layout as base
import test_light_integration as integration

codec = importlib.import_module("_atmosfera_test.entity_control_codec")
owner_module = importlib.import_module("_atmosfera_test.entity_control")
light = importlib.import_module("_atmosfera_test.light_control")
numeric = importlib.import_module("_atmosfera_test.numeric_domain")


def wire(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class CodecTests(unittest.TestCase):
    def test_shared_native_HA_fixtures_roundtrip(self):
        fixtures = list((Path(__file__).parent / "fixtures/entity_control").glob("*.json"))
        self.assertEqual(len(fixtures), 13)
        for path in fixtures:
            with self.subTest(name=path.name):
                value = codec.decode(path.read_bytes())
                self.assertEqual(codec.decode(codec.encode(value)), value)

    def identity(self):
        return dict(channel="a" * 32, open_seq=1, slot=2, card_id="card-2", revision=4,
                    control_kind="number", token="b" * 32)

    def state(self):
        return codec.envelope("state", **self.identity(), state_seq=1, ttl_ms=30000,
                              title="Number", domain=numeric.NumericDomain.from_ha(
                                  {"min": "-1", "max": "1", "step": "0.25"}).descriptor(),
                              index=4, available=True, value_text="0", state_generation=1)

    def test_every_generic_envelope_roundtrips(self):
        identity = self.identity()
        opening = {k: v for k, v in identity.items() if k != "token"}
        messages = [codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=["light", "number"]),
                    codec.envelope("bind", channel=identity["channel"]), codec.envelope("open", **opening),
                    codec.envelope("cancel_open", **opening, reason="user"), self.state(),
                    self.state() | {"kind": "grant"},
                    codec.envelope("command", **identity, command_seq=1, op="step", direction=1,
                                   expected_index=4, expected_state_generation=1),
                    codec.envelope("result", **identity, command_seq=1, state_seq=1, status="rejected", reason="stale_state"),
                    codec.envelope("close", **identity, reason="navigation")]
        for value in messages:
            with self.subTest(kind=value["kind"]):
                self.assertEqual(codec.decode(codec.encode(value)), value)

    def test_strict_duplicate_unknown_kind_fields_utf8_and_size(self):
        state = self.state()
        for value in (state | {"control_kind": "fan"}, state | {"v": True}, state | {"on": False},
                      state | {"title": "\n"}, state | {"value_text": "ą" * 33}, state | {"value_text": "\ud800"},
                      state | {"state_generation": True}, state | {"index": 4.0}, state | {"available": 1},
                      state | {"index": None}, state | {"index": 9}, state | {"extra": 1}):
            with self.subTest(value=repr(value)[:80]), self.assertRaises((codec.ProtocolError, UnicodeError)):
                codec.decode(wire(value))
        for raw in (b"\xff", '{"v":1,"v":1}', '{"v":NaN}', " " * 2049,
                    wire(state).replace('"schema":"numeric_steps_v1"', '"schema":"numeric_steps_v1","schema":"numeric_steps_v1"')):
            with self.assertRaises(codec.ProtocolError):
                codec.decode(raw)

    def test_domain_exact_canonical_metadata_and_unknown_state(self):
        state = self.state()
        for change in ({"min": "-1.0"}, {"max_index": True}, {"step": "0"}, {"unit": "ą" * 17}, {"schema": "float"}):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.decode(wire(state | {"domain": state["domain"] | change}))
        unknown = state | {"index": None, "available": False, "value_text": "--"}
        self.assertEqual(codec.decode(wire(unknown)), unknown)

    def test_generic_light_roundtrips_every_legacy_fixture_without_legacy_change(self):
        from test_light_control import FIXTURES
        for path in FIXTURES.glob("*.json"):
            legacy = light.decode(path.read_bytes())
            value = dict(legacy, type=codec.TYPE)
            if legacy["kind"] == "capability":
                value["control_kinds"] = ["light", "number"]
            elif legacy["kind"] != "bind":
                value["control_kind"] = "light"
            self.assertEqual(codec.decode(codec.encode(value)), value)
            self.assertEqual(light.decode(light.encode(legacy)), legacy)

    def test_capability_commands_and_result_reasons_exact(self):
        command = codec.envelope("command", **self.identity(), command_seq=1, op="step", direction=1,
                                 expected_index=4, expected_state_generation=1)
        for change in ({"direction": True}, {"direction": 0}, {"expected_index": None},
                       {"expected_state_generation": 0}, {"value": 1}, {"op": "set_value"}):
            with self.assertRaises(codec.ProtocolError):
                codec.decode(wire(command | change))
        cap = codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=["light", "number"])
        for kinds in ([], ["number", "light"], ["light", "number", "number"], ["light"], "light"):
            with self.assertRaises(codec.ProtocolError):
                codec.decode(wire(cap | {"control_kinds": kinds}))
        result = codec.envelope("result", **self.identity(), command_seq=1, state_seq=1, status="ha_accepted", reason="stale_state")
        with self.assertRaises(codec.ProtocolError):
            codec.decode(wire(result))


class NumberOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.state = base.State("input_number.test", "0", {"min": "-1", "max": "1", "step": "0.25", "unit_of_measurement": "°C"})
        self.hass, _ = base.environment(states=[self.state, base.State("light.test", "off", {"supported_color_modes": ["onoff"]})],
                                        services=["input_number.set_value", "light.turn_on", "light.turn_off"])
        self.card = base.card(entity="input_number.test", action={"kind": "control", "control": "number"})
        self.runtime = object()
        self.context = light.LightContext(1, self.runtime, True, 3, 4, 4, (self.card,))
        self.user, self.outputs = NS(user_id="one"), []
        self.auth_gate = self.service_gate = None
        self.auth_entered, self.service_entered = asyncio.Event(), asyncio.Event()
        self.allowed, self.apply, self.serial = True, True, 0

        async def emit(value, *_):
            self.outputs.append(deepcopy(value))

        async def authorize(*_):
            self.auth_entered.set()
            if self.auth_gate:
                await self.auth_gate.wait()
            return self.allowed

        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate:
                await self.service_gate.wait()
            if self.apply and args[0] == "input_number":
                self.change(str(args[2]["value"]))

        def token():
            self.serial += 1
            return f"{self.serial:032x}"

        self.hass.services.async_call = service
        self.owner = owner_module.EntityControlOwner(self.hass, lambda: self.context, emit, authorize,
                                                    token_factory=token, service_timeout=.03, state_timeout=.03,
                                                    renewal_interval=100, authorization_timeout=.2)
        self.owner.set_mode("entity")
        self.bind()

    def bind(self):
        if self.owner.mode == "entity":
            cap = codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=["light", "number"])
        else:
            cap = light.envelope("capability", enabled=True, max_payload_bytes=2048)
        value = self.owner.prepare_bind(wire(cap), epoch=1, runtime=self.runtime)
        self.owner.accept_bind(wire(value), epoch=1, runtime=self.runtime)

    async def asyncTearDown(self):
        if self.auth_gate:
            self.auth_gate.set()
        if self.service_gate:
            self.service_gate.set()
        await self.owner.async_unload()
        await asyncio.sleep(.001)

    async def open(self, seq=1, control="number"):
        fields = dict(channel=self.owner.channel, open_seq=seq, slot=2, card_id="card-2", revision=4)
        if self.owner.mode == "entity":
            fields["control_kind"] = control
        return await self.owner.async_handle(wire(self.owner._envelope("open", **fields)), self.user)

    def command(self, seq=1, **updates):
        selected = self.owner._selection
        value = codec.envelope("command", **selected.identity, command_seq=seq, op="step", direction=1,
                               expected_index=selected.domain_state[1], expected_state_generation=selected.domain_state[3])
        return value | updates

    async def send(self, value):
        result = await self.owner.async_handle(wire(value), self.user)
        selected = self.owner._selection
        task = selected.command.task if selected and selected.command else None
        if task:
            await asyncio.wait_for(task, .4)
        return result

    def change(self, value, **attributes):
        self.state.state = value
        self.state.attributes.update(attributes)
        return self.owner.observe_state_event(NS(data={"entity_id": self.state.entity_id, "new_state": self.state}))

    def results(self):
        return [v for v in self.outputs if v["kind"] == "result"]

    def assert_terminal_order(self):
        for i, result in enumerate(self.outputs):
            if result["kind"] == "result" and result["status"] in {"rejected", "not_confirmed", "state_matches", "already_matched"}:
                state = self.outputs[i - 1]
                self.assertEqual((state["kind"], state["token"], state["state_seq"]), ("state", result["token"], result["state_seq"]))

    async def test_exact_zero_grant_and_one_absolute_service_with_caller_context(self):
        grant = await self.open()
        self.assertEqual((grant["index"], grant["value_text"], grant["state_generation"]), (4, "0", 1))
        await self.send(self.command())
        args, kwargs = self.hass.services.calls[0]
        self.assertEqual(args, ("input_number", "set_value", {"entity_id": "input_number.test", "value": .25}))
        self.assertIs(kwargs["context"], self.user)
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assert_terminal_order()

    async def test_authorization_pending_value_ABA_rejects_captured_generation(self):
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(wire(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("0.25")
        self.change("0")
        self.assertEqual(self.owner._selection.domain_state[3], 3)
        self.auth_gate.set()
        await asyncio.wait_for(self.owner._selection.command.task, .4)
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assert_terminal_order()

    async def test_metadata_ABA_revokes_immediately_even_before_refresh_task(self):
        await self.open()
        close = self.change("0", step="0.5")
        self.assertEqual(close["reason"], "capabilities_changed")
        self.change("0", step="0.25")
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_metadata_ABA_during_authorization_cannot_dispatch(self):
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(wire(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("0", unit_of_measurement="W")
        self.change("0", unit_of_measurement="°C")
        self.auth_gate.set()
        await asyncio.sleep(.005)
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_open_authorization_metadata_ABA_is_not_granted(self):
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        job = asyncio.create_task(self.open())
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("0", max="2")
        self.change("0", max="1")
        self.auth_gate.set()
        self.assertIsNone(await job)
        self.assertIsNone(self.owner._selection)

    async def overlapping_opens(self, metadata_aba):
        first_entered, second_entered, release_second = asyncio.Event(), asyncio.Event(), asyncio.Event()
        calls = [0]

        async def authorize(*_):
            calls[0] += 1
            if calls[0] == 1:
                first_entered.set()
                await asyncio.Event().wait()
            second_entered.set()
            await release_second.wait()
            return True

        self.owner.authorize = authorize
        old = asyncio.create_task(self.open(1))
        await asyncio.wait_for(first_entered.wait(), .2)
        current = asyncio.create_task(self.open(2))
        await asyncio.wait_for(second_entered.wait(), .2)
        self.assertIsNone(await asyncio.wait_for(old, .4))
        captured = self.owner._opening_domain
        self.assertIsNotNone(captured)
        self.assertEqual(captured[0], self.owner._open_generation)
        if metadata_aba:
            self.change("0", step="0.5")
            self.change("0", step="0.25")
        release_second.set()
        grant = await asyncio.wait_for(current, .4)
        self.assertEqual(self.hass.services.calls, [])
        return grant

    async def test_superseded_open_finally_preserves_current_open_guard_and_valid_grant(self):
        grant = await self.overlapping_opens(metadata_aba=False)
        self.assertEqual(grant["open_seq"], 2)
        self.assertEqual(self.owner._selection.identity["open_seq"], 2)
        self.assertIsNone(self.owner._opening_domain)

    async def test_superseded_open_finally_cannot_hide_current_metadata_ABA(self):
        self.assertIsNone(await self.overlapping_opens(metadata_aba=True))
        self.assertIsNone(self.owner._selection)
        self.assertIsNone(self.owner._opening_domain)

    async def test_renewal_and_title_update_keep_captured_tap_valid(self):
        await self.open()
        command = self.command()
        self.card["title"] = "Updated"
        await self.owner.async_state_changed()
        self.assertEqual(self.owner._selection.domain_state[3], 1)
        self.assertEqual(self.owner._selection.state_seq, 2)
        await self.send(command)
        self.assertEqual(len(self.hass.services.calls), 1)
        self.assertEqual(self.results()[-1]["status"], "state_matches")

    async def test_renewal_while_permission_pending_keeps_tap_valid(self):
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(wire(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        # The one authorization slot refuses a concurrent renewal lookup; no
        # semantic change occurs and no second permission task is queued.
        await self.owner.async_state_changed()
        self.assertEqual(self.owner._selection.domain_state[3], 1)
        self.auth_gate.set()
        await asyncio.wait_for(self.owner._selection.command.task, .4)
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_stale_unknown_endpoint_and_duplicate_never_extra_dispatch(self):
        await self.open()
        command = self.command(expected_state_generation=2)
        await self.send(command)
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assertEqual(self.hass.services.calls, [])
        good = self.command(seq=2)
        await self.send(good)
        await self.send(good)
        self.assertEqual(len(self.hass.services.calls), 1)
        self.assert_terminal_order()
        self.change("1")
        await self.send(self.command(seq=3))
        self.assertEqual(len(self.hass.services.calls), 1)
        self.change("unknown")
        self.assertEqual(self.owner._selection.domain_state[1:3], (None, False))
        stale = good | {"command_seq": 4}
        await self.send(stale)
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_offgrid_state_and_missing_service_do_not_invent_index(self):
        self.state.state = ".1"
        grant = await self.open()
        self.assertEqual((grant["index"], grant["available"]), (None, False))
        await self.owner.async_close()
        self.hass.services.names.remove("input_number.set_value")
        with self.assertRaises(codec.ProtocolError):
            await self.open(2)

    async def test_one_service_fence_survives_cross_kind_and_mode_switch(self):
        await self.open()
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(wire(self.command()), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        job = self.owner._service_task
        self.owner.revoke_now("connection_lost", disconnect=True)
        self.owner.set_mode("legacy")
        self.bind()
        self.card.update(entity_id="light.test", action={"kind": "control", "control": "light"})
        await self.open(1, "light")
        message = light.envelope("command", **self.owner._selection.identity, command_seq=1, op="turn_on")
        result = await self.owner.async_handle(wire(message), self.user)
        self.assertEqual(result["reason"], "busy")
        self.assertIs(self.owner._service_task, job)
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_timeout_sends_state_before_terminal_without_retry(self):
        await self.open()
        self.apply = False
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["status"], "not_confirmed")
        self.assertEqual(len(self.hass.services.calls), 1)
        self.assert_terminal_order()

    async def test_cancel_stale_identity_and_unauthorized_do_not_dispatch(self):
        await self.open()
        with self.assertRaises(codec.ProtocolError):
            await self.owner.async_handle(wire(self.command() | {"control_kind": "light"}), self.user)
        self.allowed = False
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["reason"], "unauthorized")
        self.assertEqual(self.hass.services.calls, [])
        self.assert_terminal_order()

    async def test_expiry_during_permission_await_closes_without_terminal_or_service(self):
        now = [0]
        self.owner.clock = lambda: now[0]
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(wire(self.command()), self.user)
        task = self.owner._selection.command.task
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        now[0] = 31
        self.auth_gate.set()
        await asyncio.wait_for(task, .4)
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.outputs[-1]["reason"], "expired")
        self.assertEqual(self.outputs[-1]["kind"], "close")
        self.assertEqual(self.hass.services.calls, [])

    async def test_metadata_representation_equivalence_does_not_revoke_or_change_generation(self):
        await self.open()
        self.assertIsNone(self.change("0.0", min="-1.000", max=1, step=.25))
        self.assertEqual(self.owner._selection.domain_state[3], 1)
        await self.send(self.command())
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_lossy_float_target_is_refused_before_HA_boundary(self):
        self.state.state = "999999999999.999998"
        self.state.attributes.update(min="999999999999.999998", max="1000000000000", step="0.000001")
        await self.open()
        await self.send(self.command())
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["reason"], "unsupported")
        self.assert_terminal_order()

    async def test_availability_ABA_and_singleton_never_invent_a_step(self):
        await self.open()
        command = self.command()
        self.change("unavailable")
        self.change("0")
        await self.send(command)
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assertEqual(self.hass.services.calls, [])
        await self.owner.async_close()
        self.state.attributes.update(min="0", max="0", step="1")
        await self.open(2)
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["reason"], "unsupported")
        self.assertEqual(self.hass.services.calls, [])


class NumberModelTransportTests(unittest.IsolatedAsyncioTestCase):
    def generic_bridge(self, *, malformed=False):
        bridge = integration.Bridge()
        original = bridge.execute

        async def execute(action, data, **kwargs):
            if not action.name.startswith("entity_control_"):
                return await original(action, data, **kwargs)
            bridge.calls.append((action.name, deepcopy(data), kwargs))
            if action.name.endswith("get_status"):
                value = (light.envelope("capability", enabled=True, max_payload_bytes=2048) if malformed else
                         codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=["light", "number"]))
            elif action.name.endswith("bind"):
                value = json.loads(data["payload"])
            else:
                bridge.models.append(json.loads(data["payload"]))
                return None
            return NS(success=True, response_data=wire(value).encode())

        bridge.runtime.client.execute_service = execute
        for index, suffix in enumerate(("get_status", "bind", "update")):
            legacy = bridge.services[("light_control_get_status", "light_control_bind", "light_control_update")[index]]
            bridge.services["entity_control_" + suffix] = NS(**{**vars(legacy), "name": "entity_control_" + suffix, "key": 10 + index})
        return bridge

    async def test_explicit_input_number_only_no_implicit_toggle_and_unsupported_marker(self):
        card = base.card(entity="input_number.test", action={"kind": "control", "control": "number"})
        doc = base.document([card]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc)["cards"][0]["action"]["control"], "number")
        for entity in ("number.test", "light.test", "sensor.test"):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(doc | {"cards": [card | {"entity_id": entity}]})
        hass, _ = base.environment(states=[base.State("input_number.test", "0")])
        self.assertIsNone(base.cards.resolve_action(hass, card))
        self.assertNotIn("control_kind", base.cards.presentation_payload(hass, [card])["cards"][2])
        self.assertEqual(base.cards.presentation_payload(hass, [card], number_control_supported=True)["cards"][2]["control_kind"], "number")
        exported = base.layout.export_layout(doc)
        imported = base.layout.import_layout(exported, 9)
        self.assertEqual(imported["cards"][0]["action"], card["action"])
        self.assertEqual((imported["version"], imported["revision"]), (3, 9))

    async def test_catalogue_numeric_descriptor_is_exact_bounded_and_input_number_only(self):
        state = base.State("input_number.helper", "0.5", {"min": "-1.00", "max": "1", "step": "0.25", "unit_of_measurement": "°C"})
        hass, _ = base.environment(states=[state], services=["input_number.set_value"])
        metadata = base.cards._number_control_metadata(hass, state)["number_control"]
        self.assertEqual(metadata["domain"], {"schema": "numeric_steps_v1", "min": "-1", "max": "1", "step": "0.25", "unit": "°C", "max_index": 8})
        self.assertEqual(metadata["index"], 6)
        state.attributes["step"] = "0.0000001"
        self.assertEqual(base.cards._number_control_metadata(hass, state), {})
        state.entity_id = "number.provider"
        self.assertEqual(base.cards._number_control_metadata(hass, state), {})

    async def test_malformed_advertised_generic_capability_does_not_downgrade_or_retry(self):
        bridge = self.generic_bridge(malformed=True)
        try:
            self.assertFalse(await bridge._light_control.async_negotiate())
            self.assertFalse(await bridge._light_control.async_negotiate())
            self.assertEqual([call[0] for call in bridge.calls], ["entity_control_get_status"])
            self.assertEqual(bridge._light_control.state, "unconfirmed")
            self.assertIsNone(bridge._light_control.owner.channel)
        finally:
            await bridge._light_control.async_shutdown()

    async def test_transport_observes_every_value_event_before_coalescing_and_routes_one_owner(self):
        bridge = self.generic_bridge()
        state = base.State("input_number.helper", "0", {"min": "0", "max": "10", "step": "1"})
        bridge.hass.states.items[state.entity_id] = state
        bridge.hass.services.names.add("input_number.set_value")
        bridge.tile_cards = [base.card(entity=state.entity_id, action={"kind": "control", "control": "number"})]
        bridge.hass.config_entries.entry.runtime_data = bridge
        transport = bridge._light_control
        gate, entered = asyncio.Event(), asyncio.Event()
        pending = [False]

        async def user(_):
            if pending[0]:
                entered.set()
                await gate.wait()
            return NS(is_active=True, permissions=NS(check_entity=lambda *_: True))

        bridge.hass.auth.async_get_user = user
        try:
            self.assertTrue(await transport.async_negotiate())
            message = codec.envelope("open", channel=transport.owner.channel, open_seq=1, slot=2,
                                     card_id="card-2", revision=4, control_kind="number")
            caller = integration.Context("user")
            self.assertTrue(await integration.transport.async_route_entity_report(bridge.hass, bridge.node_name, wire(message), caller))
            selected = transport.owner._selection
            command = codec.envelope("command", **selected.identity, command_seq=1, op="step", direction=1,
                                     expected_index=0, expected_state_generation=1)
            pending[0] = True
            await transport.async_report_generic(wire(command), caller)
            task = selected.command.task
            await asyncio.wait_for(entered.wait(), .2)
            state.state = "1"
            transport.state_changed(NS(data={"entity_id": state.entity_id, "new_state": state}))
            refresh = transport._state_task
            state.state = "0"
            transport.state_changed(NS(data={"entity_id": state.entity_id, "new_state": state}))
            self.assertIs(transport._state_task, refresh)
            self.assertEqual(selected.domain_state[3], 3)
            gate.set()
            await asyncio.wait_for(task, .4)
            self.assertEqual(bridge.hass.services.calls, [])
            self.assertEqual(bridge.models[-1]["reason"], "stale_state")
            self.assertEqual(bridge.models[-2]["kind"], "state")
            self.assertEqual(bridge.models[-2]["state_seq"], bridge.models[-1]["state_seq"])
        finally:
            gate.set()
            await transport.async_shutdown()
            if bridge.tasks:
                await asyncio.gather(*bridge.tasks, return_exceptions=True)
    async def test_generic_negotiation_prefers_complete_contract_and_legacy_fallback_exact(self):
        bridge = integration.Bridge()
        transport = bridge._light_control
        owner_identity = id(transport.owner)
        original_execute = bridge.execute

        async def execute(action, data, **kwargs):
            if action.name.startswith("entity_control_"):
                bridge.calls.append((action.name, deepcopy(data), kwargs))
                if action.name.endswith("get_status"):
                    value = codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=["light", "number"])
                elif action.name.endswith("bind"):
                    value = json.loads(data["payload"])
                else:
                    bridge.models.append(json.loads(data["payload"]))
                    return None
                return NS(success=True, response_data=codec.encode(value).encode())
            return await original_execute(action, data, **kwargs)

        bridge.runtime.client.execute_service = execute
        for index, suffix in enumerate(("get_status", "bind", "update")):
            legacy = bridge.services[("light_control_get_status", "light_control_bind", "light_control_update")[index]]
            bridge.services["entity_control_" + suffix] = NS(**{**vars(legacy), "name": "entity_control_" + suffix, "key": 10 + index})
        try:
            self.assertTrue(await transport.async_negotiate())
            self.assertEqual(bridge.calls[0][0], "entity_control_get_status")
            self.assertTrue(transport.number_supported)
            self.assertEqual(id(transport.owner), owner_identity)
            transport.invalidate_connection()
            bridge.services.pop("entity_control_update")
            self.assertTrue(await transport.async_negotiate())
            self.assertFalse(transport.number_supported)
            self.assertEqual(bridge.calls[-2][0], "light_control_get_status")
            self.assertEqual(id(transport.owner), owner_identity)
        finally:
            await transport.async_shutdown()
