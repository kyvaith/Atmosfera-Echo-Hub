"""Panel v1 host contracts; no real Home Assistant or hardware actions."""

import asyncio
from copy import deepcopy
from datetime import datetime, timezone
import importlib
import json
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import test_entity_control as shared
import test_ha_layout as base

panel = importlib.import_module("_atmosfera_test.panel_domain")
features = importlib.import_module("_atmosfera_test.panel_features")
codec = shared.codec
NOW = 1793790000
KINDS = ["light", "number", "choice", "cover", "fan", "humidifier", "robot", "panel"]


def action(family, **values):
    return {"kind": "control", "control": "panel", "property": family, **values}


def environment(family="timer", domain=None):
    domain = domain or ("switch" if family == "power" else family)
    attributes = ({"duration": "0:02:00"} if family == "timer" else
                  {"supported_features": 4, "activity_list": [" Music ", "Cinema"], "current_activity": " Music "}
                  if family == "remote" else {"device_class": "outlet"})
    state = base.State(domain + ".test", "idle" if family == "timer" else "off", attributes)
    services = ("start", "pause", "cancel") if family == "timer" else ("turn_on", "turn_off")
    hass, _ = base.environment(states=[state], services=[domain + "." + name for name in services])
    return hass, state


class PanelModelTests(unittest.TestCase):
    def test_service_masks_and_phase_admission_are_exact(self):
        for phase, expected in (("idle", 17), ("active", 28), ("paused", 26), ("unknown", 0), ("unavailable", 0)):
            for mask in range(1, 8):
                hass, state = environment()
                state.state = phase
                names = [name for i, name in enumerate(("start", "pause", "cancel")) if mask & (1 << i)]
                hass.services.names = {"timer." + name for name in names}
                domain = panel.PanelDomain.from_ha(hass, state)
                observed = panel.PanelObservation.from_ha(state, domain, now=NOW)
                allowed = (19 if "start" in names else 0) | (4 if "pause" in names else 0) | (8 if "cancel" in names else 0)
                with self.subTest(phase=phase, mask=mask):
                    self.assertEqual(observed.eligible(domain), expected & allowed)
                    self.assertEqual(panel.PanelObservation.from_descriptor(domain, observed.descriptor()), observed)
        for family in ("remote", "power"):
            for state_name in ("on", "off", "unknown", "unavailable"):
                for names in (("turn_on",), ("turn_off",), ("turn_on", "turn_off")):
                    hass, state = environment(family)
                    state.state = state_name
                    domain_name = state.entity_id.partition(".")[0]
                    hass.services.names = {domain_name + "." + name for name in names}
                    domain = panel.PanelDomain.from_ha(hass, state)
                    observed = panel.PanelObservation.from_ha(state, domain)
                    self.assertEqual(observed.available, state_name in {"on", "off"})
                    self.assertEqual(panel.PanelObservation.from_descriptor(domain, observed.descriptor()), observed)

    def test_timer_source_parsing_preserves_knownness_and_excludes_clock_from_generation(self):
        hass, state = environment()
        domain = panel.PanelDomain.from_ha(hass, state, 120)
        state.state = "active"
        state.attributes.update(finishes_at=datetime.fromtimestamp(NOW + 120, timezone.utc).isoformat(), remaining="0:59:59")
        first = panel.PanelObservation.from_ha(state, domain, now=NOW)
        second = panel.PanelObservation.from_ha(state, domain, now=NOW + 30)
        self.assertEqual((first.remaining, second.remaining), (120, 90))
        self.assertEqual(first.command_state, second.command_state)
        expired = panel.PanelObservation.from_ha(state, domain, now=NOW + 180)
        self.assertEqual((expired.phase, expired.remaining, expired.eligible(domain)), ("active", 0, 28))
        for bad in (None, "bad", "2026-11-04T12:00:00", "2026-11-04T12:00:00.5Z"):
            state.attributes["finishes_at"] = bad
            observed = panel.PanelObservation.from_ha(state, domain, now=NOW)
            self.assertIsNone(observed.remaining)
            self.assertIsNone(observed.finishes_at)
            self.assertEqual(observed.eligible(domain), 28)
        state.attributes["finishes_at"] = "2099-12-31T23:59:59Z"
        observed = panel.PanelObservation.from_ha(state, domain, now=panel.MIN_UTC)
        self.assertEqual((observed.finishes_at, observed.remaining), (None, None))
        for value, expected in (("48:00:00", 172800), ("0:00:00", 0), ("1:60:00", None), (True, None), ("1:2:03", None)):
            self.assertEqual(panel.duration_seconds(value), expected)
        self.assertEqual(panel.utc_seconds("2026-10-25T02:30:00+02:00") + 3600,
                         panel.utc_seconds("2026-10-25T02:30:00+01:00"))

    def test_remote_exact_catalogue_off_retained_and_partial_unknown(self):
        hass, state = environment("remote")
        domain = panel.PanelDomain.from_ha(hass, state)
        observed = panel.PanelObservation.from_ha(state, domain)
        self.assertIsNone(observed.activity_index)
        self.assertEqual(observed.eligible(domain), 5)
        self.assertEqual(domain.service_action(state.entity_id, "activity", 0), ("remote", "turn_on", {"activity": " Music "}))
        state.state = "on"
        state.attributes["current_activity"] = "not-in-catalogue"
        self.assertEqual(panel.PanelObservation.from_ha(state, domain).eligible(domain), 2)
        for options in ([], [str(i) for i in range(9)], ["x" * 33], ["same", "same"], ["unknown"], ["bad\n"]):
            state.attributes["activity_list"] = options
            self.assertEqual(panel.PanelDomain.from_ha(hass, state).activities, ())
        state.attributes["activity_list"] = [" ", "ż" * 16]
        self.assertEqual(panel.PanelDomain.from_ha(hass, state).activities, (" ", "ż" * 16))
        state.attributes["supported_features"] = 0
        self.assertEqual(panel.PanelDomain.from_ha(hass, state).activities, ())

    def test_explicit_layout_catalogue_and_family_negotiated_launcher(self):
        for family in panel.PANEL_TYPES:
            hass, state = environment(family)
            configured = action(family, **({"initial_duration": 120} if family == "timer" else {}))
            card = base.card(entity=state.entity_id, action=configured)
            self.assertEqual(base.layout.validate_layout(base.document([card]) | {"version": 3})["cards"][0], card)
            self.assertIsNone(base.cards.resolve_action(hass, card))
            metadata = base.cards._panel_control_metadata(hass, state)["panel_control"]
            self.assertEqual(metadata["panel_type"], family)
            if family == "timer":
                self.assertIsNone(metadata["caps"]["initial_duration"])
            for types in ((), (family,)):
                row = base.cards.presentation_payload(hass, [card], panel_types=types, press_enabled_supported=True)["cards"][2]
                self.assertEqual(row.get("control_kind"), "panel" if types else None)
            self.assertEqual(hass.services.calls, [])
        for entity, configured, version in (("light.test", action("power"), 3), ("timer.test", action("timer"), 2),
                ("timer.test", action("timer", initial_duration=True), 3), ("timer.test", action("timer", initial_duration=0), 3),
                ("timer.test", action("timer", initial_duration=86401), 3), ("remote.test", action("remote", initial_duration=1), 3),
                ("timer.test", action("action"), 3), ("timer.test", action("timer", service="timer.start"), 3)):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(configured, entity, layout_version=version)

    def test_power_class_and_caps_are_actual_not_guessed(self):
        hass, state = environment("power")
        for value, expected in (("outlet", "outlet"), ("switch", "switch"), (None, "unknown"),
                                ("valve", "unknown"), ([], "unknown"), ({}, "unknown")):
            state.attributes["device_class"] = value
            self.assertEqual(panel.PanelDomain.from_ha(hass, state).device_class, expected)
        hass.services.names = {"switch.toggle"}
        with self.assertRaises(panel.PanelDomainError):
            panel.PanelDomain.from_ha(hass, state)
        for caps in ({"turn_on": 1, "turn_off": False, "device_class": "unknown"},
                     {"turn_on": False, "turn_off": False, "device_class": "unknown"}):
            with self.assertRaises(panel.PanelDomainError):
                panel.PanelDomain.from_descriptor("power", caps)


class PanelCodecTests(unittest.TestCase):
    def snapshot(self, family):
        hass, state = environment(family)
        domain = panel.PanelDomain.from_ha(hass, state)
        observed = panel.PanelObservation.from_ha(state, domain, now=NOW)
        return codec.envelope("grant", **(shared.CodecTests().identity() | {"control_kind": "panel"}),
            state_seq=1, ttl_ms=30000, title="Panel", panel_type=family, panel_caps=domain.descriptor(),
            panel_state=observed.descriptor(), available=observed.available, eligible_actions=observed.eligible(domain), state_generation=1)

    def test_roundtrip_exact_variants_commands_and_payload_bound(self):
        for family in panel.PANEL_TYPES:
            value = self.snapshot(family)
            self.assertEqual(codec.decode(codec.encode(value)), value)
            identity = {key: value[key] for key in codec.SELECTION}
            for operation in panel.OPERATIONS:
                fields = ({"target_index": 1} if operation in {"power", "activity"} else
                          {"duration_seconds": 86400} if operation == "set_duration" else {})
                command = codec.envelope("command", **identity, command_seq=1, op=operation, expected_state_generation=1, **fields)
                self.assertEqual(codec.decode(codec.encode(command)), command)
            for change in ({"available": 1}, {"eligible_actions": 31}, {"state_generation": True}, {"panel_type": "lock"}, {"extra": 0}):
                with self.assertRaises(codec.ProtocolError):
                    codec.decode(shared.wire(value | change))
        value = self.snapshot("remote")
        value["panel_caps"]["activities"] = [str(i) + '\\"' * 15 + "x" for i in range(8)]
        value["title"] = '"' * 160
        self.assertLess(len(codec.encode(value).encode()), 2048)
        for bad in (True, -1, 86401, 1.5, "120"):
            command = codec.envelope("command", **identity, command_seq=1, op="set_duration", expected_state_generation=1, duration_seconds=bad)
            with self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(command))

    def test_features_strict_family_subsets_and_legacy_result_rejection(self):
        value = {"v": 1, "type": features.TYPE, "panel_version": 1, "panel_types": ["timer", "power"]}
        self.assertEqual(features.decode_features(NS(success=True, response_data=shared.wire(value).encode())), value)
        for change in ({"panel_types": ["power", "timer"]}, {"panel_types": ["timer", "timer"]},
                       {"panel_types": ["lock"]}, {"panel_types": []}, {"panel_version": True}, {"extra": 1}):
            with self.assertRaises(codec.ProtocolError):
                features.decode_features(NS(success=True, response_data=shared.wire(value | change).encode()))
        bind = json.loads(features.bind_payload("a" * 32, ["remote"])) | {"accepted": True}
        self.assertEqual(features.decode_features(NS(success=True, response_data=shared.wire(bind).encode()), bind=True), bind)
        with self.assertRaises(codec.ProtocolError):
            features.decode_features(NS(success=True, response_data=b'{"v":1,"v":1}'))
        for kind in ("panel", "light", "choice"):
            value = codec.envelope("result", **(shared.CodecTests().identity() | {"control_kind": kind}),
                command_seq=1, state_seq=1, status="service_completed", reason="none")
            if kind == "panel":
                self.assertEqual(codec.decode(codec.encode(value)), value)
            else:
                with self.assertRaises(codec.ProtocolError):
                    codec.encode(value)

    def test_timer_observation_strict_cross_fields_and_max_bounds(self):
        value = self.snapshot("timer")
        for bad in ({"phase": "idle", "remaining_seconds": 0}, {"duration_seconds": True},
                    {"sampled_at_utc_s": NOW * 1000}, {"sampled_at_utc_s": 0},
                    {"phase": "paused", "finishes_at_utc_s": NOW + 3},
                    {"phase": "active", "remaining_seconds": 10, "finishes_at_utc_s": NOW + 11},
                    {"phase": "active", "remaining_seconds": 0},
                    {"phase": "unknown", "duration_seconds": 120}):
            modified = value | {"panel_state": value["panel_state"] | bad}
            with self.assertRaises(codec.ProtocolError):
                codec.encode(modified)
        for family in ("timer", "remote", "power"):
            value = self.snapshot(family)
            raw = shared.wire(value).replace('"panel_caps":{', '"panel_caps":{"extra":0,')
            with self.assertRaises(codec.ProtocolError):
                codec.decode(raw)


class PanelOwnerTests(unittest.IsolatedAsyncioTestCase):
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown

    def bind(self):
        value = self.owner.prepare_bind(shared.wire(codec.envelope("capability", enabled=True, max_payload_bytes=2048,
                                       control_kinds=KINDS)), epoch=1, runtime=self.runtime)
        self.owner.accept_bind(shared.wire(value), epoch=1, runtime=self.runtime)
        self.owner.accept_panel_features(self.owner.channel, list(panel.PANEL_TYPES))

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.fail_service = False
        self.configure("timer")

    def configure(self, family, domain=None):
        self.hass, self.state = environment(family, domain)
        self.owner.hass = self.hass
        self.card.update(entity_id=self.state.entity_id, action=action(family, **({"initial_duration": 120} if family == "timer" else {})))
        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate:
                await self.service_gate.wait()
            if self.fail_service:
                raise RuntimeError("provider failed")
            if not self.apply:
                return
            operation, data = args[1:3]
            if family == "timer":
                if operation == "start":
                    self.change("active", duration="0:02:00", finishes_at=datetime.fromtimestamp(NOW + 120, timezone.utc).isoformat())
                elif operation == "pause":
                    self.change("paused", remaining="0:01:30")
                else:
                    self.change("idle")
            else:
                self.change("on" if operation == "turn_on" else "off", **({"current_activity": data["activity"]} if "activity" in data else {}))
        self.hass.services.async_call = service

    async def open(self, seq=1):
        return await shared.NumberOwnerTests.open(self, seq, "panel")

    def command(self, seq=1, operation="start", target=None, **updates):
        selected = self.owner._selection
        fields = ({"duration_seconds": target} if operation == "set_duration" else
                  {"target_index": target} if operation in {"power", "activity"} else {})
        return codec.envelope("command", **selected.identity, command_seq=seq, op=operation,
            expected_state_generation=selected.domain_state[2], **fields) | updates

    async def test_timer_passive_open_resume_exact_commands_and_terminal_order(self):
        grant = await self.open()
        self.assertEqual(grant["panel_caps"]["initial_duration"], 120)
        self.assertEqual(self.hass.services.calls, [])
        for seq, op, target in ((1, "set_duration", 120), (2, "pause", None), (3, "resume", None), (4, "cancel", None), (5, "start", None)):
            command = self.command(seq, op, target)
            await self.send(command)
            await self.send(command)
            self.assertEqual(self.results()[-1]["status"], "service_completed" if op == "set_duration" else "state_matches")
        self.assertEqual(len(self.hass.services.calls), 5)
        self.assertEqual(self.hass.services.calls[2][0], ("timer", "start", {"entity_id": "timer.test"}))
        self.assertEqual(self.hass.services.calls[0][0][2]["duration"], 120)
        self.assertTrue(all(kwargs["context"] is self.user for _, kwargs in self.hass.services.calls))
        for i, value in enumerate(self.outputs):
            if value["kind"] == "result" and value["status"] in self.owner._terminal_statuses:
                self.assertEqual((self.outputs[i-1]["kind"], self.outputs[i-1]["state_seq"]), ("state", value["state_seq"]))
        await self.owner.async_close()
        self.assertEqual(len(self.hass.services.calls), 5)

    async def test_timer_repeatable_restart_waits_for_callback_and_never_matches(self):
        self.change("active", finishes_at=datetime.fromtimestamp(NOW + 120, timezone.utc).isoformat())
        await self.open()
        self.apply = False
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command(operation="set_duration", target=120)), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        record = self.owner._selection.command
        self.assertEqual(record.result["status"], "pending")
        self.service_gate.set()
        await asyncio.wait_for(record.task, .3)
        self.assertEqual(record.result["status"], "service_completed")
        await self.send(self.command(2, "set_duration", 120))
        self.assertEqual(len(self.hass.services.calls), 2)
        self.assertFalse(any(value["status"] in {"state_matches", "already_matched"} for value in self.results()))

    async def test_timer_tick_preserves_held_intent_but_deadline_ABA_rejects(self):
        self.change("active", finishes_at=datetime.fromtimestamp(NOW + 120, timezone.utc).isoformat())
        with patch.object(panel.time, "time", return_value=NOW):
            await self.open()
            old = self.command(operation="pause")
        with patch.object(panel.time, "time", return_value=NOW + 10):
            self.change("active")
            self.assertEqual(self.owner._selection.domain_state[2], old["expected_state_generation"])
            await self.send(old)
        self.change("active", finishes_at=datetime.fromtimestamp(NOW + 120, timezone.utc).isoformat())
        old = self.command(2, "pause")
        self.change("active", finishes_at=datetime.fromtimestamp(NOW + 121, timezone.utc).isoformat())
        self.change("active", finishes_at=datetime.fromtimestamp(NOW + 120, timezone.utc).isoformat())
        await self.send(old)
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_remote_off_retained_activity_apply_exact_then_redundant(self):
        self.configure("remote")
        grant = await self.open()
        self.assertIsNone(grant["panel_state"]["activity_index"])
        self.assertEqual(self.hass.services.calls, [])
        await self.send(self.command(operation="activity", target=0))
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual(self.hass.services.calls[0][0], ("remote", "turn_on", {"entity_id": "remote.test", "activity": " Music "}))
        await self.send(self.command(2, "activity", 0))
        self.assertEqual(self.results()[-1]["status"], "already_matched")
        await self.send(self.command(3, "power", 0))
        self.assertEqual(self.state.state, "off")
        self.assertEqual(len(self.hass.services.calls), 2)
        self.change("on", current_activity="missing")
        await self.send(self.command(4, "activity", 1))
        self.assertEqual(self.results()[-1]["reason"], "stale_state")

    async def test_power_absolute_input_boolean_partial_and_unknown(self):
        self.configure("power", "input_boolean")
        await self.open()
        await self.send(self.command(operation="power", target=1))
        self.assertEqual(self.hass.services.calls[0][0], ("input_boolean", "turn_on", {"entity_id": "input_boolean.test"}))
        await self.send(self.command(2, "power", 1))
        self.assertEqual(self.results()[-1]["status"], "already_matched")
        self.change("unknown")
        await self.send(self.command(3, "power", 0))
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_negotiation_rebind_and_family_open_fences(self):
        self.owner._panel_types = ("remote",)
        with self.assertRaises(codec.ProtocolError):
            await self.open()
        self.assertEqual(self.hass.services.calls, [])
        self.owner.accept_panel_features(self.owner.channel, ["timer"])
        await self.open(2)
        with self.assertRaises(codec.ProtocolError):
            self.owner.accept_panel_features(self.owner.channel, ["timer"])
        await self.owner.async_disconnect()
        self.assertEqual(self.owner.panel_types, ())
        bound = self.owner.prepare_bind(shared.wire(codec.envelope("capability", enabled=True, max_payload_bytes=2048,
                                        control_kinds=KINDS)), epoch=1, runtime=self.runtime)
        self.owner.accept_bind(shared.wire(bound), epoch=1, runtime=self.runtime)
        self.assertEqual(self.owner.panel_types, ())

    async def test_service_error_timeout_no_feedback_and_close_do_not_fake_success(self):
        await self.open()
        self.fail_service = True
        await self.send(self.command(operation="set_duration", target=120))
        self.assertEqual((self.results()[-1]["status"], self.results()[-1]["reason"]), ("rejected", "service_error"))
        self.fail_service, self.apply = False, False
        await self.send(self.command(2))
        self.assertEqual((self.results()[-1]["status"], self.results()[-1]["reason"]), ("not_confirmed", "state_timeout"))
        self.service_gate = asyncio.Event()
        await self.send(self.command(3, "set_duration", 120))
        self.assertEqual((self.results()[-1]["status"], self.results()[-1]["reason"]), ("not_confirmed", "service_timeout"))
        await self.owner.async_close()
        self.service_gate.set()
        await asyncio.sleep(.01)
        self.assertFalse(any(value["status"] == "service_completed" for value in self.results()))

    async def test_auth_await_metadata_ABA_and_cross_family_command_are_fenced(self):
        self.configure("remote")
        await self.open()
        await self.send(self.command(operation="start"))
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.auth_entered.clear()
        self.auth_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command(2, "activity", 1)), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("off", activity_list=["Changed"])
        self.change("off", activity_list=[" Music ", "Cinema"])
        self.auth_gate.set()
        await asyncio.sleep(.01)
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_timer_authorization_await_keeps_ticks_but_cancels_real_ABA(self):
        self.change("active", finishes_at=datetime.fromtimestamp(NOW + 120, timezone.utc).isoformat())
        with patch.object(panel.time, "time", return_value=NOW):
            await self.open()
            self.auth_entered.clear()
            self.auth_gate = asyncio.Event()
            await self.owner.async_handle(shared.wire(self.command(operation="pause")), self.user)
            await asyncio.wait_for(self.auth_entered.wait(), .2)
            with patch.object(panel.time, "time", return_value=NOW + 10):
                self.change("active")
                record = self.owner._selection.command
                self.auth_gate.set()
                await asyncio.wait_for(record.task, .3)
            self.assertEqual(record.result["status"], "state_matches")
            self.auth_gate = None
            self.change("active")
            self.auth_entered.clear()
            self.auth_gate = asyncio.Event()
            await self.owner.async_handle(shared.wire(self.command(2, "pause")), self.user)
            await asyncio.wait_for(self.auth_entered.wait(), .2)
            record = self.owner._selection.command
            self.change("paused", remaining="0:00:30")
            self.change("active")
            self.auth_gate.set()
            await asyncio.wait_for(record.task, .3)
            self.assertEqual(record.result["reason"], "stale_state")
            self.assertEqual(len(self.hass.services.calls), 1)

    async def test_permission_revocation_and_close_before_dispatch_do_not_send(self):
        await self.open()
        self.allowed = False
        await self.send(self.command(operation="set_duration", target=120))
        self.assertEqual(self.results()[-1]["reason"], "unauthorized")
        self.allowed = True
        self.auth_entered.clear()
        self.auth_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command(2, "set_duration", 120)), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        await self.owner.async_close()
        self.auth_gate.set()
        await asyncio.sleep(.01)
        self.assertEqual(self.hass.services.calls, [])

    async def test_hidden_service_fields_and_lost_capability_never_bypass_binding(self):
        self.card["action"]["service"] = "timer.start"
        with self.assertRaises(codec.ProtocolError):
            await self.open()
        self.card["action"].pop("service")
        await self.open(2)
        self.hass.services.names.remove("timer.start")
        self.change("idle")
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])


class PanelTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_optional_query_bind_is_channel_bound_and_failure_keeps_old_controls(self):
        api = shared.integration.transport
        for mode in ("valid", "missing", "wrong_channel", "unknown_family"):
            bridge = shared.NumberModelTransportTests().generic_bridge()
            original = bridge.runtime.client.execute_service
            calls = []
            if mode != "missing":
                for name in ("entity_panel_get_features", "entity_panel_bind_features"):
                    bridge.services[name] = NS(name=name, key=80 + len(bridge.services),
                        args=[] if "get" in name else [NS(name="payload", type=api.UserServiceArgType.STRING)],
                        supports_response=api.SupportsResponseType.ONLY)
            async def execute(service, data, **kwargs):
                calls.append(service.name)
                if service.name == "entity_panel_get_features":
                    value = {"v": 1, "type": features.TYPE, "panel_version": 1,
                             "panel_types": ["timer", "remote"] if mode != "unknown_family" else ["action"]}
                elif service.name == "entity_panel_bind_features":
                    value = json.loads(data["payload"]) | {"accepted": True}
                    if mode == "wrong_channel":
                        value["channel"] = "f" * 32
                else:
                    response = await original(service, data, **kwargs)
                    if service.name == "entity_control_get_status":
                        value = json.loads(response.response_data)
                        value["control_kinds"].append("panel")
                        response.response_data = shared.wire(value).encode()
                    return response
                return NS(success=True, response_data=shared.wire(value).encode())
            bridge.runtime.client.execute_service = execute
            transport = bridge._light_control
            try:
                self.assertTrue(await transport.async_negotiate())
                self.assertEqual(transport.panel_types, ("timer", "remote") if mode == "valid" else ())
                self.assertEqual(transport.status()["panel_version"], 1 if mode == "valid" else 0)
                self.assertTrue(transport.number_supported)
                transport.invalidate_connection()
                self.assertEqual(transport.panel_types, ())
            finally:
                await transport.async_shutdown()
