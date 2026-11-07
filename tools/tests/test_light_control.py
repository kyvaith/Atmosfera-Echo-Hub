"""Isolated Gate A tests: fake HA services only; no real installation or device."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from dataclasses import replace
import importlib
import json
from pathlib import Path
import types
import unittest

import test_ha_layout as base

light = importlib.import_module("_atmosfera_test.light_control")
ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tools" / "tests" / "fixtures" / "light_control"


def wire(message):
    return json.dumps(message, ensure_ascii=False, separators=(",", ":"))


class WireTests(unittest.TestCase):
    def test_every_shared_fixture_roundtrips_under_2048_utf8_bytes(self):
        paths = list(FIXTURES.glob("*.json"))
        self.assertEqual(len(paths), 15)
        for path in paths:
            with self.subTest(path=path.name):
                raw = path.read_bytes()
                self.assertLessEqual(len(raw), 2048)
                parsed = light.decode(raw)
                self.assertEqual(light.decode(light.encode(parsed)), parsed)

    def test_exact_fields_duplicate_keys_and_direction_specific_types(self):
        source = json.loads((FIXTURES / "command.json").read_text())
        changes = ({"v": True}, {"v": 2}, {"entity_id": "light.bad"},
                   {"value": True}, {"value": 101}, {"value": -1},
                   {"value": 1.0}, {"op": "toggle"}, {"command_seq": 0},
                   {"command_seq": 2**31}, {"revision": 2**53},
                   {"revision": True}, {"slot": 1}, {"card_id": "bad space"},
                   {"channel": "A" * 32}, {"token": "f" * 31})
        for change in changes:
            with self.subTest(change=change), self.assertRaises(light.ProtocolError):
                light.decode(wire(source | change))
        for raw in ('{"v":1,"v":1}', '[]', '{"v":NaN}', '{"v":Infinity}',
                    '"' + 'x' * 2048 + '"', b'\xff'):
            with self.subTest(raw=str(raw)[:30]), self.assertRaises(light.ProtocolError):
                light.decode(raw)

    def test_power_op_forbids_value_and_brightness_requires_it(self):
        source = json.loads((FIXTURES / "command.json").read_text())
        for message in (source | {"op": "turn_on"}, {k: v for k, v in source.items() if k != "value"}):
            with self.assertRaises(light.ProtocolError):
                light.decode(wire(message))

    def test_snapshot_strict_booleans_complete_caps_and_title_byte_budget(self):
        source = json.loads((FIXTURES / "grant.json").read_text())
        changes = ({"on": 1}, {"brightness_pct": False}, {"ttl_ms": True},
                   {"ttl_ms": 30001}, {"title": "ą" * 81}, {"title": "line\nbreak"},
                   {"caps": {"brightness": True, "turn_on": True, "turn_off": False}},
                   {"caps": {"brightness": False, "turn_on": True, "turn_off": True}},
                   {"caps": {"brightness": True, "turn_on": 1, "turn_off": True}})
        for change in changes:
            with self.subTest(change=change), self.assertRaises(light.ProtocolError):
                light.decode(wire(source | change))

    def test_unhashable_unknown_values_and_deep_json_fail_structurally(self):
        source = json.loads((FIXTURES / "result.json").read_text())
        for change in ({"kind": []}, {"status": []}, {"reason": {}}, {"type": []}):
            with self.assertRaises(light.ProtocolError):
                light.decode(wire(source | change))
        with self.assertRaises(light.ProtocolError):
            light.decode("[" * 1000 + "]" * 1000)

    def test_result_reason_matches_status_and_unknown_fields_are_never_tolerated(self):
        source = json.loads((FIXTURES / "result.json").read_text())
        for change in ({"status": "pending", "reason": "service_error"},
                       {"status": "not_confirmed", "reason": "none"},
                       {"status": "rejected", "reason": "state_timeout"},
                       {"service": "light.turn_on"}):
            with self.assertRaises(light.ProtocolError):
                light.decode(wire(source | change))


class OwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.hass, _ = base.environment(states=[base.State("light.test", "off", {
            "friendly_name": "Test", "supported_color_modes": ["brightness"], "brightness": 0,
        })], services=["light.turn_on", "light.turn_off"])
        self.card = base.card(entity="light.test", id="card-light-2", title="Test",
                              action={"kind": "control", "control": "light"})
        self.runtime = object()
        self.current = light.LightContext(1, self.runtime, True, 3, 7, 7, (self.card,))
        self.outputs, self.permissions = [], []
        self.allowed, self.apply, self.failure = True, True, None
        self.service_gate = None
        self.auth_gate = None
        self.service_entered = asyncio.Event()
        self.auth_entered = asyncio.Event()
        self.serial = 0
        self.user = types.SimpleNamespace(user_id="user-one")

        async def emit(message, epoch, runtime):
            self.assertEqual(epoch, 1)
            self.assertIs(runtime, self.runtime)
            self.outputs.append(message)

        async def authorize(context, entity_id):
            self.permissions.append((context, entity_id))
            self.auth_entered.set()
            if self.auth_gate is not None:
                await self.auth_gate.wait()
            return self.allowed

        async def call(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate is not None:
                await self.service_gate.wait()
            if self.failure is not None:
                raise self.failure
            if self.apply:
                state = self.hass.states.get("light.test")
                state.state = "off" if args[1] == "turn_off" else "on"
                if "brightness_pct" in args[2]:
                    state.attributes["brightness"] = round(args[2]["brightness_pct"] * 255 / 100)

        self.hass.services.async_call = call

        def token():
            self.serial += 1
            return f"{self.serial:032x}"

        self.owner = light.LightControlOwner(self.hass, lambda: self.current, emit, authorize,
                                             token_factory=token, service_timeout=.03,
                                             state_timeout=.03, renewal_interval=100,
                                             authorization_timeout=.03)
        capability = (FIXTURES / "capability.json").read_bytes()
        self.bind = self.owner.prepare_bind(capability, epoch=1, runtime=self.runtime)
        self.owner.accept_bind(wire(self.bind), epoch=1, runtime=self.runtime)

    async def asyncTearDown(self):
        await self.owner.async_unload()
        if self.service_gate is not None:
            self.service_gate.set()
        await asyncio.sleep(.001)

    def open_message(self, seq=1, **updates):
        return light.envelope("open", channel=self.bind["channel"], open_seq=seq, slot=2,
                              card_id="card-light-2", revision=7) | updates

    async def open(self, seq=1):
        return await self.owner.async_handle(wire(self.open_message(seq)), self.user)

    def command(self, seq=1, op="brightness", value=100):
        message = light.envelope("command", **self.owner._selection.identity, command_seq=seq, op=op)
        if op == "brightness":
            message["value"] = value
        return message

    async def settle(self):
        selected = self.owner._selection
        task = selected.command.task if selected and selected.command else None
        if task:
            await asyncio.wait_for(task, .3)

    async def send(self, seq=1, op="brightness", value=100):
        result = await self.owner.async_handle(wire(self.command(seq, op, value)), self.user)
        await self.settle()
        return result

    def results(self):
        return [value for value in self.outputs if value["kind"] == "result"]

    async def test_open_is_presentation_only_and_requires_explicit_v3_action(self):
        grant = await self.open()
        self.assertEqual((grant["on"], grant["brightness_pct"], grant["state_seq"]), (False, 0, 1))
        self.assertEqual(self.hass.services.calls, [])
        await self.owner.async_close()
        self.current = replace(self.current, layout_version=2)
        with self.assertRaisesRegex(light.ProtocolError, "selection_changed"):
            await self.open(2)
        self.current = replace(self.current, layout_version=3)
        self.card["action"] = {"kind": "default"}
        with self.assertRaises(light.ProtocolError):
            await self.open(3)

    async def test_100_and_1_send_one_turn_on_with_context_and_no_arbitrary_data(self):
        for index, value in enumerate((100, 1), 1):
            await self.open(index)
            await self.send(value=value)
            args, kwargs = self.hass.services.calls[-1]
            self.assertEqual(args, ("light", "turn_on", {"entity_id": "light.test", "brightness_pct": value}))
            self.assertIs(kwargs["context"], self.user)
            self.assertIs(kwargs["blocking"], True)
            self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual(len(self.hass.services.calls), 2)

    async def test_zero_means_turn_off_without_brightness_data(self):
        self.hass.states.get("light.test").state = "on"
        self.hass.states.get("light.test").attributes["brightness"] = 120
        await self.open()
        await self.send(value=0)
        self.assertEqual(self.hass.services.calls[0][0], ("light", "turn_off", {"entity_id": "light.test"}))

    async def test_explicit_on_restores_without_inventing_brightness_and_off_is_separate(self):
        await self.open()
        await self.send(op="turn_on")
        await self.send(seq=2, op="turn_off")
        self.assertEqual([call[0] for call in self.hass.services.calls], [
            ("light", "turn_on", {"entity_id": "light.test"}),
            ("light", "turn_off", {"entity_id": "light.test"}),
        ])

    async def test_unknown_on_brightness_is_null_and_capability_is_not_inferred_from_attr(self):
        state = self.hass.states.get("light.test")
        state.state = "on"
        for index, malformed in enumerate((None, True, -1, 256, float("nan"), "128"), 1):
            state.attributes["brightness"] = malformed
            self.assertIsNone((await self.open(index))["brightness_pct"])
        state.attributes.update(supported_color_modes=["onoff"], brightness=128)
        grant = await self.open(7)
        self.assertFalse(grant["caps"]["brightness"])
        self.assertIsNone(grant["brightness_pct"])

    async def test_malformed_or_unknown_mode_does_not_enable_brightness(self):
        for index, modes in enumerate(("brightness", ["bogus"], [], None), 1):
            self.hass.states.get("light.test").attributes["supported_color_modes"] = modes
            grant = await self.open(index)
            self.assertFalse(grant["caps"]["brightness"])

    async def test_onoff_only_allows_power_and_rejects_slider_including_zero(self):
        self.hass.states.get("light.test").attributes["supported_color_modes"] = ["onoff"]
        grant = await self.open()
        self.assertEqual(grant["caps"], {"brightness": False, "turn_on": True, "turn_off": True})
        await self.send(value=0)
        self.assertEqual(self.results()[-1]["reason"], "unsupported")
        self.assertEqual(self.hass.services.calls, [])
        await self.send(seq=2, op="turn_on")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_missing_unknown_unavailable_or_non_light_cannot_open(self):
        for index, value in enumerate(("unknown", "unavailable", "custom"), 1):
            self.hass.states.get("light.test").state = value
            with self.assertRaisesRegex(light.ProtocolError, "entity_unavailable"):
                await self.open(index)
        self.hass.states.items.clear()
        with self.assertRaises(light.ProtocolError):
            await self.open(4)
        self.card["entity_id"] = "switch.test"
        with self.assertRaises(light.ProtocolError):
            await self.open(5)

    async def test_live_service_removal_or_caps_change_prevents_dispatch(self):
        await self.open()
        self.hass.services.names.remove("light.turn_on")
        with self.assertRaisesRegex(light.ProtocolError, "capabilities_changed"):
            await self.send()
        await self.owner.async_state_changed()
        self.assertEqual(self.outputs[-1]["kind"], "close")
        self.assertEqual(self.hass.services.calls, [])

    async def test_denied_open_returns_correlated_cancel_without_token(self):
        self.hass.states.get("light.test").state = "unavailable"
        with self.assertRaisesRegex(light.ProtocolError, "entity_unavailable"):
            await self.open()
        denial = self.outputs[-1]
        self.assertEqual((denial["kind"], denial["reason"]), ("cancel_open", "entity_unavailable"))
        self.assertNotIn("token", denial)
        self.assertEqual({key: denial[key] for key in light.OPEN},
                         {key: self.open_message()[key] for key in light.OPEN})

    async def test_current_revision_sent_revision_visibility_and_editability_are_required(self):
        for index, changes in enumerate(({"revision": 8}, {"sent_revision": 6},
                                         {"editable_slots": frozenset()}), 1):
            original = self.current
            self.current = replace(original, **changes)
            with self.assertRaises(light.ProtocolError):
                await self.open(index)
            self.current = original
        self.card["visible"] = False
        with self.assertRaises(light.ProtocolError):
            await self.open(4)

    async def test_open_rechecks_revision_and_epoch_after_authorization_await(self):
        self.auth_gate = asyncio.Event()
        pending = asyncio.create_task(self.open())
        await self.auth_entered.wait()
        self.current = replace(self.current, epoch=2)
        self.auth_gate.set()
        with self.assertRaisesRegex(light.ProtocolError, "connection_lost"):
            await pending
        self.assertEqual(self.hass.services.calls, [])

    async def test_command_rechecks_binding_after_authorization_await(self):
        await self.open()
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        await self.owner.async_handle(wire(self.command()), self.user)
        await self.auth_entered.wait()
        self.card["entity_id"] = "light.other"
        self.auth_gate.set()
        await self.settle()
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["status"], "rejected")

    async def test_permission_denial_on_open_and_command_has_no_dispatch(self):
        self.allowed = False
        with self.assertRaisesRegex(light.ProtocolError, "unauthorized"):
            await self.open()
        self.allowed = True
        await self.open(2)
        self.allowed = False
        await self.send()
        self.assertEqual(self.results()[-1]["reason"], "unauthorized")
        self.assertEqual(self.hass.services.calls, [])

    async def test_permission_exception_and_non_boolean_allow_are_denied(self):
        self.allowed = "yes"
        with self.assertRaisesRegex(light.ProtocolError, "unauthorized"):
            await self.open()

        async def broken(*_):
            raise RuntimeError("permission lookup failed")

        self.owner.authorize = broken
        with self.assertRaisesRegex(light.ProtocolError, "unauthorized"):
            await self.open(2)
        self.assertEqual(self.hass.services.calls, [])

    async def test_other_ha_principal_cannot_command_or_close_selection(self):
        await self.open()
        other = types.SimpleNamespace(user_id="other")
        for message in (self.command(), light.envelope("close", **self.owner._selection.identity, reason="user")):
            with self.assertRaisesRegex(light.ProtocolError, "unauthorized"):
                await self.owner.async_handle(wire(message), other)
        self.assertIsNotNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_identical_duplicate_and_reordered_keys_replay_last_result_without_service(self):
        await self.open()
        message = self.command()
        await self.owner.async_handle(wire(message), self.user)
        await self.settle()
        previous = deepcopy(self.results()[-1])
        result = await self.owner.async_handle(wire(dict(reversed(list(message.items())))), self.user)
        self.assertEqual(result, previous)
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_same_sequence_different_digest_is_rejected(self):
        await self.open()
        await self.send()
        result = await self.owner.async_handle(wire(self.command(value=1)), self.user)
        self.assertEqual(result["reason"], "sequence_conflict")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_one_pending_busy_is_retained_and_never_replayed_as_new_call(self):
        self.service_gate = asyncio.Event()
        await self.open()
        first = self.command()
        await self.owner.async_handle(wire(first), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        duplicate = await self.owner.async_handle(wire(first), self.user)
        self.assertEqual(duplicate["status"], "pending")
        second = self.command(seq=2, value=1)
        self.assertEqual((await self.owner.async_handle(wire(second), self.user))["reason"], "busy")
        self.service_gate.set()
        await self.settle()
        replay = await self.owner.async_handle(wire(second), self.user)
        self.assertEqual(replay["status"], "rejected")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_last_result_eviction_keeps_sequence_high_water(self):
        await self.open()
        old = self.command()
        await self.send()
        await self.send(seq=2, value=1)
        result = await self.owner.async_handle(wire(old), self.user)
        self.assertEqual(result["reason"], "stale_sequence")
        self.assertEqual(len(self.hass.services.calls), 2)

    async def test_already_matching_is_truthful_noop_without_claiming_execution(self):
        await self.open()
        await self.send(op="turn_off")
        self.assertEqual(self.results()[-1]["status"], "already_matched")
        self.assertEqual(self.hass.services.calls, [])

    async def test_service_return_without_state_is_not_physical_completion(self):
        self.apply = False
        await self.open()
        await self.send()
        self.assertEqual([r["status"] for r in self.results()], ["pending", "ha_accepted", "not_confirmed"])
        self.assertEqual(self.results()[-1]["reason"], "state_timeout")

    async def test_state_event_confirms_match_with_fresh_snapshot_sequence(self):
        self.apply = False
        await self.open()
        await self.owner.async_handle(wire(self.command(value=1)), self.user)
        for _ in range(30):
            await asyncio.sleep(.001)
            if self.results()[-1]["status"] == "ha_accepted":
                break
        state = self.hass.states.get("light.test")
        state.state, state.attributes["brightness"] = "on", 3
        await self.owner.async_state_changed()
        await self.settle()
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual(self.results()[-1]["state_seq"], 2)

    async def test_service_error_and_timeout_are_distinct_and_no_auto_retry(self):
        self.failure = RuntimeError("synthetic service error")
        await self.open()
        await self.send()
        self.assertEqual((self.results()[-1]["status"], self.results()[-1]["reason"]), ("rejected", "service_error"))
        self.failure = None
        self.service_gate = asyncio.Event()
        await self.send(seq=2)
        self.assertEqual((self.results()[-1]["status"], self.results()[-1]["reason"]), ("not_confirmed", "service_timeout"))
        await self.send(seq=3)
        self.assertEqual(self.results()[-1]["reason"], "busy")
        self.assertEqual(len(self.hass.services.calls), 2)

    async def test_close_cancels_owned_observer_but_never_issues_inverse_or_late_result(self):
        self.service_gate = asyncio.Event()
        await self.open()
        selected = self.owner._selection
        await self.owner.async_handle(wire(self.command()), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        await self.owner.async_close("navigation")
        count = len(self.outputs)
        self.service_gate.set()
        await asyncio.sleep(.005)
        self.assertEqual(len(self.outputs), count)
        self.assertTrue(selected.renewal.cancelled() or selected.renewal.done())
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_old_token_same_card_revision_cannot_command_reopened_selection(self):
        await self.open()
        old = self.command()
        await self.open(2)
        with self.assertRaisesRegex(light.ProtocolError, "selection_changed"):
            await self.owner.async_handle(wire(old), self.user)
        self.assertEqual(self.hass.services.calls, [])

    async def test_cancel_open_during_authorization_prevents_delayed_grant(self):
        self.auth_gate = asyncio.Event()
        pending = asyncio.create_task(self.open())
        await self.auth_entered.wait()
        cancel = self.open_message() | {"kind": "cancel_open", "reason": "navigation"}
        await self.owner.async_handle(wire(cancel), self.user)
        self.auth_gate.set()
        self.assertIsNone(await pending)
        self.assertFalse(any(item["kind"] == "grant" for item in self.outputs))
        with self.assertRaisesRegex(light.ProtocolError, "stale_sequence"):
            await self.open()

    async def test_cancel_before_open_and_old_cancel_cannot_revoke_new_selection(self):
        cancel = self.open_message() | {"kind": "cancel_open", "reason": "navigation"}
        await self.owner.async_handle(wire(cancel), self.user)
        with self.assertRaises(light.ProtocolError):
            await self.open()
        await self.open(2)
        await self.owner.async_handle(wire(cancel), self.user)
        self.assertEqual(self.owner._selection.identity["open_seq"], 2)

    async def test_cancel_requires_exact_pending_identity_and_caller(self):
        self.auth_gate = asyncio.Event()
        pending = asyncio.create_task(self.open())
        await self.auth_entered.wait()
        cancel = self.open_message() | {"kind": "cancel_open", "reason": "navigation"}
        with self.assertRaisesRegex(light.ProtocolError, "selection_changed"):
            await self.owner.async_handle(wire(cancel | {"card_id": "other-card"}), self.user)
        with self.assertRaisesRegex(light.ProtocolError, "unauthorized"):
            await self.owner.async_handle(wire(cancel), types.SimpleNamespace(user_id="other"))
        self.auth_gate.set()
        self.assertEqual((await pending)["kind"], "grant")

    async def test_external_close_cancels_pending_authorization_without_grant(self):
        self.auth_gate = asyncio.Event()
        pending = asyncio.create_task(self.open())
        await self.auth_entered.wait()
        await self.owner.async_close("sleep")
        self.auth_gate.set()
        self.assertIsNone(await pending)
        self.assertIsNone(self.owner._selection)

    async def test_orphan_service_fences_reopened_selection_and_late_result_is_discarded(self):
        self.service_gate = asyncio.Event()
        await self.open()
        await self.owner.async_handle(wire(self.command()), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        await self.owner.async_close("navigation")
        new_grant = await self.open(2)
        result = await self.owner.async_handle(wire(self.command(value=1)), self.user)
        self.assertEqual(result["reason"], "busy")
        count = len(self.outputs)
        self.service_gate.set()
        await asyncio.sleep(.005)
        self.assertEqual(len(self.outputs), count)
        self.assertEqual(self.owner._selection.identity["token"], new_grant["token"])
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_unload_cancels_pre_dispatch_authorization_and_renewal(self):
        await self.open()
        selected = self.owner._selection
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        await self.owner.async_handle(wire(self.command()), self.user)
        await self.auth_entered.wait()
        await self.owner.async_unload()
        self.auth_gate.set()
        await asyncio.sleep(.001)
        self.assertTrue(selected.renewal.done())
        self.assertEqual(self.hass.services.calls, [])

    async def test_unload_cancels_local_service_wait_without_inverse_or_retry(self):
        self.service_gate = asyncio.Event()
        await self.open()
        await self.owner.async_handle(wire(self.command()), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        job = self.owner._service_task
        await self.owner.async_unload()
        await asyncio.sleep(.001)
        self.assertTrue(job.cancelled())
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_output_transport_error_revokes_admission_and_cannot_dispatch(self):
        await self.open()

        async def fail(*_):
            raise RuntimeError("synthetic disconnected transport")

        self.owner.emit = fail
        with self.assertRaisesRegex(light.ProtocolError, "connection_lost"):
            await self.owner.async_handle(wire(self.command()), self.user)
        self.assertIsNone(self.owner._selection)
        self.assertFalse(self.owner._bound)
        self.assertEqual(self.hass.services.calls, [])

    async def test_expired_selection_is_never_renewed_or_reactivated_by_state(self):
        await self.open()
        self.owner._selection.deadline = self.owner.clock() - 1
        await self.owner.async_state_changed()
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.outputs[-1]["reason"], "expired")

    async def test_epoch_runtime_replacement_disconnect_and_unload_reject_late_events(self):
        await self.open()
        old = self.command()
        self.current = replace(self.current, runtime=object())
        with self.assertRaisesRegex(light.ProtocolError, "connection_lost"):
            await self.owner.async_handle(wire(old), self.user)
        await self.owner.async_disconnect()
        await self.owner.async_unload()
        with self.assertRaises(light.ProtocolError):
            await self.owner.async_handle(wire(old), self.user)
        self.assertEqual(self.hass.services.calls, [])

    async def test_bind_echo_must_match_real_epoch_runtime_and_capability(self):
        with self.assertRaises(light.ProtocolError):
            self.owner.accept_bind(wire(self.bind), epoch=2, runtime=self.runtime)
        with self.assertRaises(light.ProtocolError):
            self.owner.accept_bind(wire(self.bind), epoch=1, runtime=object())
        with self.assertRaises(light.ProtocolError):
            self.owner.prepare_bind((FIXTURES / "capability.json").read_bytes(), epoch=0, runtime=self.runtime)

    async def test_renewal_permission_loss_closes_without_dispatch(self):
        await self.open()
        self.allowed = False
        await self.owner.async_state_changed()
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_late_false_permission_refresh_never_closes_a_new_selection(self):
        await self.open()
        entered, release = asyncio.Event(), asyncio.Event()
        actual = self.owner._authorized

        async def delayed(context, entity_id, *, authorizer=None):
            if asyncio.current_task().get_name() == "old-refresh":
                entered.set()
                await release.wait()
                return False
            return await actual(context, entity_id, authorizer=authorizer)

        self.owner._authorized = delayed
        old = asyncio.create_task(self.owner.async_state_changed(), name="old-refresh")
        await asyncio.wait_for(entered.wait(), .2)
        await self.open(2)
        current = self.owner._selection
        release.set()
        await old
        self.assertIs(self.owner._selection, current)

    async def test_old_emit_failure_cannot_revoke_rebound_runtime_or_channel(self):
        await self.open()
        entered, release = asyncio.Event(), asyncio.Event()

        async def emit(message, epoch, _runtime):
            if message["kind"] == "state" and epoch == 1:
                entered.set()
                await release.wait()
                raise RuntimeError("old connection completion")
            self.outputs.append(message)

        self.owner.emit = emit
        old = asyncio.create_task(self.owner.async_state_changed())
        await asyncio.wait_for(entered.wait(), .2)
        await self.owner.async_disconnect()
        self.runtime = object()
        self.current = replace(self.current, epoch=2, runtime=self.runtime)
        self.bind = self.owner.prepare_bind((FIXTURES / "capability.json").read_bytes(), epoch=2, runtime=self.runtime)
        self.owner.accept_bind(wire(self.bind), epoch=2, runtime=self.runtime)
        await self.open()
        current = self.owner._selection
        release.set()
        with self.assertRaises(light.ProtocolError):
            await old
        self.assertTrue(self.owner._bound)
        self.assertIs(self.owner._selection, current)

    async def test_old_emit_failure_cannot_revoke_new_selection_on_same_channel(self):
        await self.open()
        entered, release = asyncio.Event(), asyncio.Event()

        async def emit(message, _epoch, _runtime):
            if message["kind"] == "state" and message["open_seq"] == 1:
                entered.set()
                await release.wait()
                raise RuntimeError("old request completion")
            self.outputs.append(message)

        self.owner.emit = emit
        old = asyncio.create_task(self.owner.async_state_changed())
        await asyncio.wait_for(entered.wait(), .2)
        await self.open(2)
        current = self.owner._selection
        release.set()
        with self.assertRaises(light.ProtocolError):
            await old
        self.assertTrue(self.owner._bound)
        self.assertIs(self.owner._selection, current)

    async def test_open_cannot_grant_a_different_entity_from_the_authorized_one(self):
        self.auth_gate = asyncio.Event()
        pending = asyncio.create_task(self.open())
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.hass.states.items["light.other"] = base.State("light.other", "on", {
            "supported_color_modes": ["brightness"], "brightness": 180,
        })
        self.card["entity_id"] = "light.other"
        self.auth_gate.set()
        with self.assertRaisesRegex(light.ProtocolError, "selection_changed"):
            await pending
        self.assertIsNone(self.owner._selection)
        self.assertFalse(any(message["kind"] == "grant" for message in self.outputs))

    async def test_local_control_chars_and_surrogates_are_sanitized_without_saving_changes(self):
        for seq, title in enumerate(("Lamp\x00name", "Lamp\ud800name", "\x00\udfff\x7f"), 1):
            self.card["title"] = title
            grant = await self.open(seq)
            self.assertEqual(self.card["title"], title)
            self.assertFalse(any(ord(char) < 32 or ord(char) == 127 or 0xD800 <= ord(char) <= 0xDFFF
                                 for char in grant["title"]))
            light.encode(grant)
            self.assertIsNotNone(self.owner._selection.renewal)

    async def test_invalid_generated_token_rolls_back_only_attempted_grant(self):
        self.owner.token_factory = lambda: "invalid"
        with self.assertRaises(light.ProtocolError):
            await self.open()
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.outputs[-1]["kind"], "cancel_open")

    async def test_permission_timeout_has_finite_wait_and_never_dispatches(self):
        self.auth_gate = asyncio.Event()
        self.owner.authorization_timeout = .005
        with self.assertRaisesRegex(light.ProtocolError, "unauthorized"):
            await asyncio.wait_for(self.open(), .2)
        job = self.owner._authorization_task
        if job is not None:
            await asyncio.wait_for(asyncio.gather(job, return_exceptions=True), .2)
            self.assertTrue(job.done())
        self.assertIsNone(self.owner._authorization_task)
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_permission_lookup_is_single_flight_and_refreshes_do_not_queue(self):
        self.owner.authorization_timeout = 2.0  # Test coalescing independently of the30ms fixture timing.
        await self.open()
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        refresh = asyncio.create_task(self.owner.async_state_changed())
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        job = self.owner._authorization_task
        permission_count = len(self.permissions)
        await asyncio.gather(*(self.owner.async_state_changed() for _ in range(30)))
        self.assertIs(self.owner._authorization_task, job)
        self.assertEqual(len(self.permissions), permission_count)
        self.assertIsNotNone(self.owner._selection)
        self.auth_gate.set()
        await refresh

    async def test_cancellation_resistant_authorizer_retains_one_slot_without_new_jobs(self):
        entered, release = asyncio.Event(), asyncio.Event()
        self.addCleanup(release.set)
        count = 0

        async def stubborn(*_):
            nonlocal count
            count += 1
            entered.set()
            while not release.is_set():
                try:
                    await release.wait()
                except asyncio.CancelledError:
                    pass
            return True

        self.owner.authorize = stubborn
        self.owner.authorization_timeout = .005
        first = asyncio.create_task(self.open())
        await asyncio.wait_for(entered.wait(), .2)
        with self.assertRaisesRegex(light.ProtocolError, "unauthorized"):
            await asyncio.wait_for(first, .2)
        job = self.owner._authorization_task
        for seq in range(2, 22):
            with self.assertRaisesRegex(light.ProtocolError, "busy"):
                await asyncio.wait_for(self.open(seq), .2)
            self.assertIs(self.owner._authorization_task, job)
        self.assertEqual(count, 1)
        release.set()
        await asyncio.wait_for(job, .2)
        grant = await self.open(22)
        self.assertEqual(grant["kind"], "grant")
        self.assertEqual(count, 2)
        self.assertEqual(self.hass.services.calls, [])

    async def test_concurrent_superseding_opens_admit_only_latest_lookup_and_grant(self):
        results = await asyncio.gather(*(self.open(seq) for seq in range(1, 51)))
        self.assertEqual(sum(result is not None for result in results), 1)
        self.assertEqual(self.owner._selection.identity["open_seq"], 50)
        self.assertEqual(len(self.permissions), 1)
        self.assertEqual(sum(message["kind"] == "grant" for message in self.outputs), 1)
        self.assertEqual(self.hass.services.calls, [])


if __name__ == "__main__":
    unittest.main()
