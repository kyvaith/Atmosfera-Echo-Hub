"""Negotiated Cover detail tests, including both axes over the one Stop fence."""

import asyncio
from copy import deepcopy
import importlib
import json
from types import SimpleNamespace as NS
import unittest

import test_cover_control as legacy
import test_entity_control as shared
import test_ha_layout as base

codec = shared.codec
panel = importlib.import_module("_atmosfera_test.cover_panel_domain")
features = importlib.import_module("_atmosfera_test.entity_control_features")
BITS = {"open": 1, "close": 2, "stop": 8, **panel.PANEL_FEATURES}
SERVICES = {name: True for name in panel.SERVICES.values()}


class CoverPanelModelTests(unittest.TestCase):
    def test_all_feature_masks_crossed_with_service_loss_keep_axes_independent(self):
        for mask in range(256):
            for missing in (None, *SERVICES):
                services = SERVICES | ({missing: False} if missing else {})
                expected = {op: bool(mask & bit) and services[panel.SERVICES[op]] for op, bit in BITS.items()}
                with self.subTest(mask=mask, missing=missing):
                    if not any(expected.values()):
                        with self.assertRaises(panel.CoverDomainError):
                            panel.CoverPanelDomain.from_ha({"supported_features": mask}, services)
                        continue
                    domain = panel.CoverPanelDomain.from_ha({"supported_features": mask}, services)
                    self.assertEqual({op: domain.supports(op) for op in BITS}, expected)
                    self.assertEqual(domain.device_class, "unknown")
                    self.assertEqual(panel.CoverPanelDomain.from_panel_descriptor(domain.descriptor(), domain.panel_descriptor(None)), domain)

    def test_actual_positions_do_not_cross_axes_or_invent_unknown(self):
        for state in ("open", "closed", "opening", "closing"):
            observed = panel.CoverPanelObservation.from_ha(state, {"current_position": 30, "current_tilt_position": 75.0})
            self.assertEqual((observed.position, observed.tilt_position), (30, 75))
            self.assertTrue(observed.target_matches("set_tilt_position", 75))
            self.assertFalse(observed.target_matches("set_position", 75))
            self.assertFalse(observed.target_matches("stop_tilt"))
        for value in (None, True, False, "75", -1, 101, 75.5, float("nan")):
            observed = panel.CoverPanelObservation.from_ha("open", {"current_position": 30, "current_tilt_position": value})
            self.assertEqual((observed.position, observed.tilt_position), (30, None))
        self.assertEqual(panel.CoverPanelObservation.from_ha("unavailable", {"current_position": 30, "current_tilt_position": 75}),
                         panel.CoverPanelObservation("unknown", None, None))

    def test_tilt_only_metadata_is_new_without_changing_legacy_admission(self):
        state = base.State("cover.test", "open", {"supported_features": 128, "current_position": 30,
                           "current_tilt_position": 60, "device_class": "blind"})
        hass, _ = base.environment(states=[state], services=["cover.set_cover_tilt_position"])
        self.assertEqual(base.cards._cover_control_metadata(hass, state), {})
        metadata = base.cards._cover_panel_metadata(hass, state)["cover_panel"]
        self.assertEqual(metadata["device_class"], "blind")
        self.assertEqual(metadata["state"]["tilt_position"], 60)
        self.assertEqual(sum(metadata["caps"].values()), 1)
        card = base.card(entity=state.entity_id, action={"kind": "control", "control": "cover"})
        for enabled in (False, True):
            row = base.cards.presentation_payload(hass, [card], cover_control_supported=True,
                cover_panel_supported=enabled, press_enabled_supported=True)["cards"][2]
            self.assertEqual(row.get("control_kind"), "cover" if enabled else None)

    def test_commands_map_exact_axis_and_never_assume_stop_capability(self):
        domain = panel.CoverPanelDomain.from_ha({"supported_features": 255, "device_class": "garage"}, SERVICES)
        self.assertEqual(domain.service_action("set_position", 71), ("set_cover_position", {"position": 71}))
        self.assertEqual(domain.service_action("set_tilt_position", 23), ("set_cover_tilt_position", {"tilt_position": 23}))
        self.assertEqual(domain.service_action("stop_tilt"), ("stop_cover_tilt", {}))
        for target in (-1, 101, True, "23", 23.0):
            with self.assertRaises(panel.CoverDomainError):
                domain.service_action("set_tilt_position", target)


class CoverPanelCodecTests(unittest.TestCase):
    def state(self):
        value = legacy.CoverCodecTests().state()
        domain = panel.CoverPanelDomain.from_ha({"supported_features": 255, "device_class": "blind"}, SERVICES)
        return value | {"cover_panel": domain.panel_descriptor(40)}

    def test_legacy_stays_exact_and_detail_requires_explicit_codec_mode(self):
        legacy_value, detail = legacy.CoverCodecTests().state(), self.state()
        self.assertEqual(codec.decode(codec.encode(legacy_value)), legacy_value)
        self.assertEqual(codec.decode(codec.encode(detail, cover_panel=True), cover_panel=True), detail)
        self.assertLess(len(codec.encode(detail, cover_panel=True).encode()), 2048)
        for payload, enabled in ((detail, False), (legacy_value, True)):
            with self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(payload), cover_panel=enabled)
        identity = {key: detail[key] for key in codec.SELECTION}
        for operation in panel.PANEL_OPERATIONS:
            command = codec.envelope("command", **identity, command_seq=1, op=operation, expected_state_generation=1,
                                    **({"target_index": 41} if operation in panel.NUMERIC_OPERATIONS else {}))
            self.assertEqual(codec.decode_report(codec.encode(command, cover_panel=True)), command)
            if operation not in {"open", "close", "stop"}:
                with self.assertRaises(codec.ProtocolError):
                    codec.decode(shared.wire(command))

    def test_strict_panel_objects_unknown_values_and_target_fields(self):
        value = self.state()
        for change in ({"version": True}, {"version": 2}, {"device_class": "garage_door"},
                {"tilt_position": True}, {"tilt_position": 101}, {"tilt_position": 1.5},
                {"extra": 0}, {"caps": value["cover_panel"]["caps"] | {"stop_tilt": 1}},
                {"caps": value["cover_panel"]["caps"] | {"tilt": True}}):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(value | {"cover_panel": value["cover_panel"] | change}), cover_panel=True)
        raw = shared.wire(value).replace('"version":1,"device_class"', '"version":1,"version":1,"device_class"')
        with self.assertRaises(codec.ProtocolError):
            codec.decode(raw, cover_panel=True)
        with self.assertRaises(codec.ProtocolError):
            codec.decode(shared.wire(value | {"cover_state": "unknown", "available": False, "position": None}), cover_panel=True)
        command = codec.envelope("command", **{key: value[key] for key in codec.SELECTION}, command_seq=1,
                                 op="set_position", target_index=20, expected_state_generation=1)
        for change in ({"target_index": True}, {"target_index": 101}, {"target_index": -1},
                {"op": "stop"}, {"position": 20}, {"expected_state_generation": True}):
            with self.subTest(command=change), self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(command | change), cover_panel=True)


class CoverPanelOwnerTests(legacy.CoverOwnerTests):
    def bind(self):
        super().bind()
        self.owner.accept_cover_panel_features(self.owner.channel, 1)

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.state.attributes.update(supported_features=255, current_tilt_position=40, device_class="blind")
        self.hass.services.names.update("cover." + name for name in SERVICES)
        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate:
                await self.service_gate.wait()
            if not self.apply:
                return
            operation, data = args[1:3]
            if operation in {"open_cover", "close_cover", "stop_cover"}:
                status, position = {"open_cover": ("opening", 0), "close_cover": ("closing", 100),
                                    "stop_cover": ("open", 40)}[operation]
                self.change(status, current_position=position)
            elif operation == "set_cover_position":
                self.change("open" if data["position"] else "closed", current_position=data["position"])
            elif operation == "set_cover_tilt_position":
                self.change(self.state.state, current_tilt_position=data["tilt_position"])
            elif operation in {"open_cover_tilt", "close_cover_tilt"}:
                self.change(self.state.state, current_tilt_position=100 if operation == "open_cover_tilt" else 0)
            # StopTilt has no standard observable stopped feedback.
        self.hass.services.async_call = service

    async def test_axes_target_buttons_dispatch_once_without_opening_or_implicit_stop(self):
        grant = await self.open()
        self.assertEqual(grant["cover_panel"]["tilt_position"], 40)
        self.assertEqual(self.hass.services.calls, [])
        for seq, op, target in ((1, "set_position", 71), (2, "set_tilt_position", 23),
                               (3, "open_tilt", None), (4, "close_tilt", None)):
            command = self.command(seq, op, **({"target_index": target} if target is not None else {}))
            await self.send(command)
            await self.send(command)
            self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual([args for args, _ in self.hass.services.calls], [
            ("cover", "set_cover_position", {"entity_id": "cover.test", "position": 71}),
            ("cover", "set_cover_tilt_position", {"entity_id": "cover.test", "tilt_position": 23}),
            ("cover", "open_cover_tilt", {"entity_id": "cover.test"}),
            ("cover", "close_cover_tilt", {"entity_id": "cover.test"})])
        self.assertEqual(self.state.attributes["current_position"], 71)
        await self.owner.async_close()
        self.assertEqual(len(self.hass.services.calls), 4)
        self.assert_terminal_order()

    async def test_missing_tilt_disables_only_rail_not_known_primary_or_absolute_tilt_button(self):
        self.state.attributes["current_tilt_position"] = None
        await self.open()
        await self.send(self.command(operation="set_tilt_position", target_index=50))
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        await self.send(self.command(2, "open_tilt"))
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        await self.send(self.command(3, "set_position", target_index=50))
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual(len(self.hass.services.calls), 2)

    async def test_tilt_ABA_retires_held_primary_target_and_class_ABA_revokes_open(self):
        await self.open()
        message = self.command(operation="set_position", target_index=50)
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        await self.owner.async_handle(shared.wire(message), self.user)
        pending = self.owner._selection.command
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("closed", current_tilt_position=50)
        self.change("closed", current_tilt_position=40)
        self.auth_gate.set()
        await asyncio.wait_for(pending.task, .3)
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assertEqual(self.hass.services.calls, [])
        await self.owner.async_close()
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        opening = asyncio.create_task(self.open(2))
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("closed", device_class="curtain")
        self.change("closed", device_class="blind")
        self.auth_gate.set()
        await opening
        self.assertIsNone(self.owner._selection)

    async def test_stop_tilt_never_claims_stationary_primary_or_changed_tilt_as_proof(self):
        await self.open()
        self.owner.state_timeout = .15
        await self.owner.async_handle(shared.wire(self.command(operation="stop_tilt")), self.user)
        record = self.owner._selection.command
        await asyncio.wait_for(self.service_entered.wait(), .2)
        self.change("open", current_position=40, current_tilt_position=60)
        await self.owner.async_state_changed()
        await asyncio.wait_for(record.task, .3)
        self.assertEqual((record.result["status"], record.result["reason"]), ("not_confirmed", "state_timeout"))
        self.assertEqual([args[1] for args, _ in self.hass.services.calls], ["stop_cover_tilt"])

    async def test_pending_primary_and_tilt_targets_accept_only_their_own_stop(self):
        for op, stop, other_stop, services in (
                ("set_position", "stop", "stop_tilt", ["set_cover_position", "stop_cover"]),
                ("set_tilt_position", "stop_tilt", "stop", ["set_cover_tilt_position", "stop_cover_tilt"])):
            await self.open(1 if stop == "stop" else 2)
            self.service_gate = asyncio.Event()
            self.service_entered.clear()
            before = len(self.hass.services.calls)
            await self.owner.async_handle(shared.wire(self.command(operation=op, target_index=70)), self.user)
            await asyncio.wait_for(self.service_entered.wait(), .2)
            movement = self.owner._selection.command
            rejected = await self.owner.async_handle(shared.wire(self.command(2, other_stop)), self.user)
            self.assertEqual(rejected["reason"], "busy")
            self.assertIs(self.owner._selection.command, movement)
            response = await self.owner.async_handle(shared.wire(self.command(3, stop)), self.user)
            successor = self.owner._selection.command
            self.assertTrue(successor.priority and successor.predecessor_started)
            self.assertEqual(response["status"], "pending")
            self.service_gate.set()
            await asyncio.wait_for(successor.task, .3)
            self.assertEqual([args[1] for args, _ in self.hass.services.calls[before:]], services)
            self.assertEqual(successor.result["status"], "state_matches" if stop == "stop" else "not_confirmed")
            await self.owner.async_close()

    async def test_unsent_tilt_canceled_then_only_explicit_stop_tilt_executes(self):
        await self.open()
        await self.owner.async_handle(shared.wire(self.command(operation="set_tilt_position", target_index=70)), self.user)
        movement = self.owner._selection.command
        await self.owner.async_handle(shared.wire(self.command(2, "stop_tilt")), self.user)
        successor = self.owner._selection.command
        await asyncio.wait_for(successor.task, .3)
        self.assertFalse(movement.service_started)
        self.assertEqual([args[1] for args, _ in self.hass.services.calls], ["stop_cover_tilt"])
        self.assertEqual(successor.result["status"], "not_confirmed")

    async def test_future_stop_and_second_successor_never_replace_admitted_job(self):
        await self.open()
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command(operation="set_tilt_position", target_index=70)), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        first = self.owner._selection.command
        result = await self.owner.async_handle(shared.wire(self.command(2, "stop_tilt", expected_state_generation=99)), self.user)
        self.assertEqual(result["reason"], "stale_state")
        self.assertIs(self.owner._selection.command, first)
        await self.owner.async_handle(shared.wire(self.command(3, "stop_tilt")), self.user)
        successor = self.owner._selection.command
        result = await self.owner.async_handle(shared.wire(self.command(4, "stop_tilt")), self.user)
        self.assertEqual(result["reason"], "busy")
        self.assertIs(self.owner._selection.command, successor)
        self.service_gate.set()
        await asyncio.wait_for(successor.task, .3)

    async def test_panel_binding_requires_stop_and_current_channel_before_open(self):
        for channel, version in (("f" * 32, 1), (self.owner.channel, True), (self.owner.channel, 0)):
            with self.assertRaises(codec.ProtocolError):
                self.owner.accept_cover_panel_features(channel, version)
        await self.open()
        with self.assertRaises(codec.ProtocolError):
            self.owner.accept_cover_panel_features(self.owner.channel, 1)
        await self.owner.async_disconnect()
        self.assertEqual(self.owner.cover_panel_version, 0)
        capability = codec.envelope("capability", enabled=True, max_payload_bytes=2048,
                                    control_kinds=["light", "number", "cover"])
        value = self.owner.prepare_bind(shared.wire(capability), epoch=1, runtime=self.runtime)
        self.owner.accept_bind(shared.wire(value), epoch=1, runtime=self.runtime)
        with self.assertRaises(codec.ProtocolError):
            self.owner.accept_cover_panel_features(self.owner.channel, 1)
        self.owner.accept_cover_features(self.owner.channel, 1)
        self.assertEqual(self.owner.cover_panel_version, 0)
        await self.open(2)
        with self.assertRaises(codec.ProtocolError):
            await self.send(self.command(operation="set_position", target_index=30))
        self.assertEqual(self.hass.services.calls, [])

    async def test_close_during_tilt_stop_predecessor_wait_never_dispatches_late_stop(self):
        await self.open()
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command(operation="set_tilt_position", target_index=70)), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        await self.owner.async_handle(shared.wire(self.command(2, "stop_tilt")), self.user)
        await self.owner.async_close()
        self.service_gate.set()
        await asyncio.sleep(.01)
        self.assertEqual([args[1] for args, _ in self.hass.services.calls], ["set_cover_tilt_position"])

    async def test_tilt_stop_permission_loss_after_predecessor_never_dispatches(self):
        await self.open()
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command(operation="set_tilt_position", target_index=70)), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        await self.owner.async_handle(shared.wire(self.command(2, "stop_tilt")), self.user)
        successor = self.owner._selection.command
        self.allowed = False
        self.service_gate.set()
        await asyncio.wait_for(successor.task, .3)
        self.assertEqual(successor.result["reason"], "unauthorized")
        self.assertEqual([args[1] for args, _ in self.hass.services.calls], ["set_cover_tilt_position"])


class CoverPanelTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_feature_handshake_is_after_stop_and_malformed_detail_falls_back_only_to_legacy(self):
        api = shared.integration.transport
        for detail, stop in ((True, True), (False, True), (True, False)):
            bridge = shared.NumberModelTransportTests().generic_bridge()
            original = bridge.runtime.client.execute_service
            calls = []
            for prefix, field in (("entity_control", "cover_stop_version"), ("entity_cover", "cover_panel_version")):
                bridge.services[prefix + "_get_features"] = NS(name=prefix + "_get_features", key=50 + len(bridge.services),
                    args=[], supports_response=api.SupportsResponseType.ONLY)
                bridge.services[prefix + "_bind_features"] = NS(name=prefix + "_bind_features", key=60 + len(bridge.services),
                    args=[NS(name="channel", type=api.UserServiceArgType.STRING), NS(name=field, type=api.UserServiceArgType.INT)],
                    supports_response=api.SupportsResponseType.ONLY)
            async def execute(action, data, **kwargs):
                calls.append(action.name)
                if action.name.endswith("_features"):
                    is_detail = action.name.startswith("entity_cover_")
                    field = "cover_panel_version" if is_detail else "cover_stop_version"
                    available = detail if is_detail else stop
                    value = {"v": 1, "type": "entity_cover_features_v1" if is_detail else "entity_control_features_v1", field: 1 if available else 0}
                    if "bind" in action.name:
                        value.update(channel=data["channel"], accepted=True)
                    return NS(success=True, response_data=shared.wire(value).encode())
                response = await original(action, data, **kwargs)
                if action.name == "entity_control_get_status":
                    value = json.loads(response.response_data)
                    value["control_kinds"].append("cover")
                    response.response_data = shared.wire(value).encode()
                return response
            bridge.runtime.client.execute_service = execute
            transport = bridge._light_control
            try:
                self.assertTrue(await transport.async_negotiate())
                self.assertEqual(transport.cover_supported, stop)
                self.assertEqual(transport.cover_panel_supported, detail and stop)
                if detail and stop:
                    self.assertLess(calls.index("entity_control_bind_features"), calls.index("entity_cover_get_features"))
                if not stop:
                    self.assertNotIn("entity_cover_get_features", calls)
                transport.invalidate_connection()
                self.assertEqual(transport.owner.cover_panel_version, 0)
            finally:
                await transport.async_shutdown()

    async def test_feature_reply_is_strict_and_rejects_wrong_channel_shape(self):
        value = {"v": 1, "type": "entity_cover_features_v1", "cover_panel_version": 1,
                 "channel": "a" * 32, "accepted": True}
        self.assertEqual(features.decode_features(NS(success=True, response_data=shared.wire(value).encode()), bind=True, cover_panel=True), value)
        for change in ({"cover_panel_version": True}, {"cover_panel_version": 2}, {"channel": ""},
                       {"accepted": 1}, {"extra": 0}, {"type": "entity_control_features_v1"}):
            with self.assertRaises(codec.ProtocolError):
                features.decode_features(NS(success=True, response_data=shared.wire(value | change).encode()), bind=True, cover_panel=True)
