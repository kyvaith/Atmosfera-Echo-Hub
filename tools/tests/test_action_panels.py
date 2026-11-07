"""Action2 host contracts; HA objects, services and contexts are fakes."""

import asyncio
import ast
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

import test_ha_layout as base
import test_entity_control as shared
import test_extra_panels as extra_tests

action = importlib.import_module("_atmosfera_test.action_panel_domain")
codec = shared.codec


def environment(subtype="button", value=None, attrs=None, *, stop=False, skip=False):
    state = base.State(subtype + ".test", value if value is not None else (
        "unknown" if subtype in {"button", "input_button", "scene"} else "off"), attrs)
    services = [subtype + "." + name for name in action.SERVICES[subtype].values()]
    hass, _ = base.environment(states=[state], services=services)
    hass.config.time_zone = "Europe/Warsaw"
    saved = dict(action.ACTION)
    if subtype == "automation": saved.update(skip_condition=skip, stop_actions=stop)
    if subtype == "script":
        # The service identity intentionally differs from the renamed entity.
        hass.entity_registry.entries[state.entity_id] = NS(platform="script", unique_id="original_name", translation_key=None)
        hass.services.names.add("script.original_name")
        hass.service_descriptions = {("script", "original_name"): {"fields": {}}}
    return hass, state, saved


class ActionDomainTests(unittest.TestCase):
    def test_panel_asset_version_matches_integration_manifest(self):
        root = Path(__file__).resolve().parents[2] / "custom_components/atmosfera_echo_hub"
        tree = ast.parse((root / "panel.py").read_text(encoding="utf8"))
        versions = [node.value.value for node in tree.body if isinstance(node, ast.Assign)
                    and any(isinstance(name, ast.Name) and name.id == "PANEL_ASSET_VERSION" for name in node.targets)]
        self.assertEqual(versions, [json.loads((root / "manifest.json").read_text())["version"]])

    def test_all_subtypes_exact_registered_services_and_policy(self):
        for subtype in action.MASKS:
            with self.subTest(subtype=subtype):
                hass, state, saved = environment(subtype, stop=True, skip=True)
                domain = action.ActionDomain.from_ha(hass, state, saved)
                self.assertEqual(domain.operations, action.MASKS[subtype])
                for op, service in action.SERVICES[subtype].items():
                    data = {"skip_condition": True} if op == "trigger" else {"stop_actions": True} if op == "disable" else {}
                    self.assertEqual(domain.service_action(state.entity_id, op), (subtype, service, data))
                    hass.services.names.remove(subtype + "." + service)
                    self.assertFalse(action.ActionDomain.from_ha(hass, state, saved).operations & action.BITS[op])
                self.assertEqual(hass.services.calls, [])

    def test_first_use_timestamp_is_not_unavailable_or_a_toggle(self):
        for subtype in ("button", "input_button", "scene", "script", "automation"):
            hass, state, saved = environment(subtype, "unknown")
            domain = action.ActionDomain.from_ha(hass, state, saved)
            observed = action.ActionObservation.from_ha(hass, state, domain)
            self.assertEqual(observed.available, subtype in {"button", "input_button", "scene"})
            self.assertEqual(observed.last_used_status, "unknown")
            state.state = "unavailable"
            state.attributes.update(current=3, last_triggered="2026-11-05T10:00:00+00:00")
            observed = action.ActionObservation.from_ha(hass, state, domain)
            self.assertEqual(observed.descriptor(), {"source": "unavailable", "phase": "unknown", "last_used_status": "unknown", "last_used_text": "", "current": None})
            self.assertEqual(observed.eligible(domain), 0)

    def test_script_metadata_registry_renames_required_defaults_and_missing(self):
        hass, state, saved = environment("script")
        self.assertEqual(action.ActionDomain.from_ha(hass, state, saved).run_blocked, "none")
        for descriptor, blocked in (({"fields": {"name": {"required": True, "default": "not supplied"}}}, "needs_parameters"),
                ({"fields": {"name": {"required": False}}}, "none"), ({"fields": {"name": {"required": 1}}}, "metadata_unavailable"),
                ({"fields": {"section": {"fields": {}}}}, "metadata_unavailable"), ({}, "metadata_unavailable"),
                ({"fields": {str(i): {} for i in range(129)}}, "metadata_unavailable")):
            hass.service_descriptions[("script", "original_name")] = descriptor
            self.assertEqual(action.ActionDomain.from_ha(hass, state, saved).run_blocked, blocked)
        hass.entity_registry.entries.clear()
        self.assertEqual(action.ActionDomain.from_ha(hass, state, saved).run_blocked, "metadata_unavailable")
        hass.services.names.remove("script.turn_on")
        self.assertEqual(action.ActionDomain.from_ha(hass, state, saved).run_blocked, "service_unavailable")

    def test_timestamps_complete_normalized_and_no_silent_fraction_rounding(self):
        hass, state, saved = environment("script", attrs={"last_triggered": datetime(2026, 11, 5, 10, tzinfo=timezone.utc), "current": 0})
        domain = action.ActionDomain.from_ha(hass, state, saved)
        observed = action.ActionObservation.from_ha(hass, state, domain)
        self.assertEqual(observed.last_used_text, "2026-11-05T11:00:00+01:00")
        for raw, expected in (("2026-11-05T10:00:00.1234567+00:00", "invalid"), ("2026-11-05T10:00:00", "invalid"),
                              ("x" * 49, "too_long"), ("\ud800", "invalid")):
            state.attributes["last_triggered"] = raw
            self.assertEqual(action.ActionObservation.from_ha(hass, state, domain).last_used_status, expected)
        for count in (-1, 65536, True, "2", 2.5):
            state.attributes["current"] = count
            self.assertIsNone(action.ActionObservation.from_ha(hass, state, domain).current)

    def test_layout_profile_explicit_policies_types_and_no_legacy_mutation(self):
        for subtype in action.MASKS:
            hass, state, saved = environment(subtype)
            for kind in ("entity", "action"):
                card = base.card(entity=state.entity_id, type=kind, action=saved)
                self.assertEqual(base.layout.validate_layout(base.document([card]) | {"version": 3})["cards"][0]["action"], saved)
                self.assertIsNone(base.cards.resolve_action(hass, card))
                for profiles in ((), ("action",)):
                    row = base.cards.presentation_payload(hass, [card], panel_extra_profiles=profiles, press_enabled_supported=True)["cards"][2]
                    self.assertEqual(row.get("control_kind"), "panel" if profiles else None)
            for bad in (saved | {"extra": 1}, saved | {"stop_actions": 0}, saved | {"initial_duration": 5}):
                with self.assertRaises(base.layout.LayoutError): base.layout.validate_action(bad, state.entity_id, layout_version=3)
            with self.assertRaises(base.layout.LayoutError): base.layout.validate_action(saved, state.entity_id, layout_version=2)
        with self.assertRaises(base.layout.LayoutError): base.layout.validate_action(action.ACTION, "automation.test", layout_version=3)
        direct = {"kind": "service", "service": "button.press", "data": {}}
        self.assertEqual(base.layout.validate_action(direct, "button.atmosfera_demo_doorbell", layout_version=3), direct)

    def test_metadata_fingerprint_excludes_telemetry_and_exports_only_closed_fields(self):
        hass, state, _ = environment("automation")
        before = action.action_metadata(hass, state)["action_panel"]
        state.attributes.update(current=3, last_triggered="2026-11-05T10:00:00+00:00", token="secret")
        after = action.action_metadata(hass, state)["action_panel"]
        self.assertEqual(before["fingerprint"], after["fingerprint"])
        self.assertNotIn("secret", json.dumps(after))
        self.assertEqual(after["caps"]["skip_condition"], False)


class ActionCodecTests(unittest.TestCase):
    def fixtures(self):
        root = Path(__file__).with_name("fixtures") / "action_panel" / "wire"
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf8"))
        for name, expected in manifest["files"].items():
            data = (root / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected)
            if name != "contract.json": yield name, json.loads(data)

    def test_frozen_wire_exact_roundtrip_and_optional_admission(self):
        count = 0
        for name, value in self.fixtures():
            with self.subTest(name=name):
                count += 1
                encoded = codec.encode(value, extra_profiles=("action",))
                self.assertEqual(codec.decode(encoded, extra_profiles=("action",)), value)
                if value["kind"] != "result":
                    with self.assertRaises(codec.ProtocolError): codec.decode(encoded)
        self.assertEqual(count, 29)

    def test_closed_command_no_service_target_policy_vars_or_other_profile(self):
        command = next(value for name, value in self.fixtures() if name == "command-press.json")
        for updates in ({"action_version": True}, {"action_version": 2}, {"op": "toggle"}, {"op": "unlock"}, {"target": 0},
                {"vars": {}}, {"skip_condition": True}, {"service": "button.press"}, {"facet": "main"}, {"media_version": 1}, {"control_kind": "light"}):
            with self.subTest(updates=updates), self.assertRaises(codec.ProtocolError):
                codec.encode(command | updates, extra_profiles=("action", "media"))

    def test_dispatched_terminal_requires_explicit_action2_admission(self):
        value = next(value for name, value in self.fixtures() if value["kind"] == "result")
        dispatched = value | {"status": "service_dispatched", "reason": "none"}
        encoded = codec.encode(dispatched, extra_profiles=("action",), action_dispatched=True)
        self.assertEqual(codec.decode(encoded, extra_profiles=("action",), action_dispatched=True), dispatched)
        for kwargs in ({}, {"extra_profiles": ("action",)}, {"action_dispatched": True},
                       {"extra_profiles": ("media",), "action_dispatched": True},
                       {"extra_profiles": ("action",), "action_dispatched": 1}):
            with self.assertRaises(codec.ProtocolError): codec.encode(dispatched, **kwargs)
        for changes in ({"control_kind": "robot"}, {"reason": "service_error"}, {"status": "queued"}):
            with self.assertRaises(codec.ProtocolError):
                codec.encode(dispatched | changes, extra_profiles=("action",), action_dispatched=True)

    def test_crossfield_known_phase_mask_policies_and_stale_metadata_rejected(self):
        for name, value in self.fixtures():
            if value["kind"] not in {"grant", "state"}: continue
            for caps in ({"operations": 127}, {"skip_condition": 1}, {"run_blocked": "alien"}):
                with self.assertRaises(codec.ProtocolError): codec.encode(value | {"panel_caps": value["panel_caps"] | caps}, extra_profiles=("action",))
            for state in ({"phase": "alien"}, {"source": "unavailable", "last_used_status": "value", "last_used_text": "2026-11-05T10:00:00+00:00"},
                          {"current": True}, {"last_used_status": "value", "last_used_text": "not a date"}):
                with self.assertRaises(codec.ProtocolError): codec.encode(value | {"panel_state": value["panel_state"] | state}, extra_profiles=("action",))


class ActionOwnerTests(unittest.IsolatedAsyncioTestCase):
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown
    bind = extra_tests.ExtraOwnerTests.bind

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.configure("button")

    def configure(self, subtype, value=None, *, stop=False, skip=False):
        self.hass, self.state, saved = environment(subtype, value, stop=stop, skip=skip)
        self.owner.hass = self.hass
        self.card.update(entity_id=self.state.entity_id, type="action", action=saved)
        self.fail = self.retire = False
        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate: await self.service_gate.wait()
            if self.retire: self.owner.revoke_now("selection_changed")
            if self.apply:
                if subtype in {"script", "automation"} and args[1] in {"turn_on", "turn_off"}:
                    self.change("on" if args[1] == "turn_on" else "off")
                else: self.change(self.state.state, last_triggered="2026-11-05T10:00:00+00:00")
            if self.fail: raise RuntimeError("fake service failed")
        self.hass.services.async_call = service

    async def open(self, seq=1):
        return await shared.NumberOwnerTests.open(self, seq, "panel")

    def command(self, seq=1, op="press", **changes):
        selected = self.owner._selection
        return codec.envelope("command", **selected.identity, action_version=1, command_seq=seq, op=op,
            expected_state_generation=selected.domain_state[2]) | changes

    async def test_first_use_one_press_context_and_service_only_no_fake_state_match(self):
        grant = await self.open()
        self.assertEqual(grant["eligible_actions"], 1)
        await self.send(self.command())
        self.assertEqual(self.hass.services.calls[0][0], ("button", "press", {"entity_id": "button.test"}))
        self.assertIs(self.hass.services.calls[0][1]["context"], self.user)
        self.assertEqual(self.results()[-1]["status"], "service_completed")
        await self.send(self.command())
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_service_only_for_scene_script_run_trigger_and_stop_true_off(self):
        for index, (subtype, op, stop, skip) in enumerate((("scene", "activate", False, False), ("script", "run", False, False),
                ("automation", "trigger", False, True), ("automation", "disable", True, False))):
            await self.owner.async_close()
            self.configure(subtype, stop=stop, skip=skip)
            await self.open(index + 1)
            await self.send(self.command(op=op))
            self.assertEqual(len(self.hass.services.calls), 1)
            self.assertEqual(self.results()[-1]["status"], "service_dispatched" if op == "trigger" else "service_completed")
            self.assertIs(self.hass.services.calls[0][1]["blocking"], op != "trigger")
            expected = {"skip_condition": True} if op == "trigger" else {"stop_actions": True} if op == "disable" else {}
            self.assertEqual(self.hass.services.calls[0][0][2], {"entity_id": self.state.entity_id, **expected})

    async def test_observed_enable_disable_stop_need_fresh_phase_not_callback(self):
        for index, (subtype, value, op) in enumerate((("automation", "off", "enable"), ("automation", "on", "disable"), ("script", "on", "stop"))):
            for apply in (False, True):
                await self.owner.async_close()
                self.configure(subtype, value)
                self.apply = apply
                await self.open(1 + index * 2 + int(apply))
                await self.send(self.command(op=op))
                self.assertEqual(self.results()[-1]["status"], "state_matches" if apply else "not_confirmed")

    async def test_held_authorization_source_ABA_rejects_but_timestamp_count_does_not(self):
        self.configure("automation")
        await self.open()
        for seq, aba in ((1, False), (2, True)):
            self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
            await self.owner.async_handle(shared.wire(self.command(seq, op="trigger")), self.user)
            task = self.owner._selection.command.task
            await asyncio.wait_for(self.auth_entered.wait(), .2)
            if aba:
                self.change("unavailable")
                self.change("off")
            else: self.change("off", current=2, last_triggered="2026-11-05T10:00:00+00:00")
            self.auth_gate.set()
            await asyncio.wait_for(task, .4)
            self.assertEqual(self.results()[-1]["status"], "rejected" if aba else "service_dispatched")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_required_script_cannot_run_and_metadata_loss_retires_selection(self):
        self.configure("script")
        self.hass.service_descriptions[("script", "original_name")] = {"fields": {"name": {"required": True}}}
        grant = await self.open()
        self.assertEqual(grant["panel_caps"]["run_blocked"], "needs_parameters")
        await self.send(self.command(op="run"))
        self.assertEqual(self.hass.services.calls, [])
        self.hass.service_descriptions.clear()
        self.change("off")
        self.assertIsNone(self.owner._selection)

    async def test_permission_loss_policy_change_and_missing_negotiation_refuse(self):
        self.owner._extra_profiles = ()
        with self.assertRaises(codec.ProtocolError): await self.open()
        self.bind()
        self.configure("automation")
        await self.open()
        self.allowed = False
        await self.send(self.command(op="trigger"))
        self.assertEqual(self.hass.services.calls, [])
        self.allowed = True
        self.card["action"]["skip_condition"] = True
        self.change("off")
        self.assertIsNone(self.owner._selection)

    async def test_retiring_notice_action_does_not_paint_late_result_or_reopen(self):
        await self.open()
        self.retire = True
        await self.send(self.command())
        self.assertEqual(len(self.hass.services.calls), 1)
        self.assertIsNone(self.owner._selection)
        self.assertFalse(any(row["kind"] == "result" and row["status"] == "service_completed" for row in self.outputs))

    async def test_timestamp_change_does_not_turn_failed_service_into_success(self):
        await self.open()
        self.fail = True
        await self.send(self.command())
        self.assertEqual(len(self.hass.services.calls), 1)
        self.assertEqual(self.results()[-1]["status"], "rejected")

    async def test_retired_action_keeps_shared_service_fence_until_callback_finishes(self):
        await self.open()
        self.owner.service_timeout = 1
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        job, original_calls = self.owner._service_task, self.hass.services.calls
        await self.owner.async_close()
        self.configure("automation")
        await self.open(2)
        await self.send(self.command(op="trigger"))
        self.assertEqual(self.results()[-1]["reason"], "busy")
        self.assertEqual((len(original_calls), len(self.hass.services.calls)), (1, 0))
        self.assertIs(self.owner._service_task, job)
        self.service_gate.set()
        await asyncio.wait_for(job, .2)

    async def test_unmarked_legacy_panel_command_and_old_identity_never_dispatch_action(self):
        await self.open()
        prior = self.command()
        legacy = dict(prior, op="pause")
        legacy.pop("action_version")
        await self.send(legacy)
        self.assertEqual(self.results()[-1]["reason"], "unsupported")
        await self.owner.async_close()
        await self.open(2)
        with self.assertRaises(codec.ProtocolError): await self.send(prior)
        self.assertEqual(self.hass.services.calls, [])

    def install_background_core_fake(self, *, early_error=False, late_error=False):
        """Core async_call contract: validate first, then schedule/catch provider errors.

        Mirrors Core2026.7.1 core.py2581-2708; no actual provider or HA is run.
        The separate provider remains pending beyond the owner's service deadline.
        """
        self.provider_gate, self.provider_entered = asyncio.Event(), asyncio.Event()
        self.provider_jobs, self.provider_errors = [], []

        async def provider():
            self.provider_entered.set()
            await self.provider_gate.wait()
            if late_error:
                raise RuntimeError("provider failure")

        async def background():
            try:
                await provider()
            except RuntimeError as error:
                # Core catches/logs provider errors after accepting dispatch.
                self.provider_errors.append(str(error))

        async def dispatch(*args, **kwargs):
            if early_error:
                raise ValueError("schema rejected before queue")
            self.hass.services.calls.append((args, kwargs))
            self.assertIs(kwargs["context"], self.user)
            if kwargs["blocking"]:
                await provider()
            else:
                self.provider_jobs.append(asyncio.create_task(background()))

        self.hass.services.async_call = dispatch

    async def test_trigger_dispatch_does_not_wait_or_claim_provider_completion_and_releases_fence(self):
        self.configure("automation", skip=True)
        await self.open()
        self.install_background_core_fake()
        try:
            command = self.command(op="trigger")
            await self.send(command)
            await asyncio.wait_for(self.provider_entered.wait(), .2)
            await asyncio.sleep(self.owner.service_timeout * 2)
            self.assertFalse(self.provider_jobs[0].done())
            self.assertEqual(self.results()[-1]["status"], "service_dispatched")
            self.assertIsNone(self.owner._selection.command)
            self.assertIsNone(self.owner._service_task)
            self.assertFalse(any(row["status"] == "service_completed" for row in self.results()))
            # A duplicate receipt must never enqueue the same sequence twice.
            await self.send(command)
            self.assertEqual(len(self.hass.services.calls), 1)
            self.assertEqual(self.hass.services.calls[0][0][2], {"entity_id": "automation.test", "skip_condition": True})
        finally:
            self.provider_gate.set()
            await asyncio.gather(*self.provider_jobs)

    async def test_trigger_early_validation_error_is_not_dispatched(self):
        self.configure("automation", skip=True)
        await self.open()
        self.install_background_core_fake(early_error=True)
        await self.send(self.command(op="trigger"))
        self.assertEqual((self.results()[-1]["status"], self.results()[-1]["reason"]), ("rejected", "service_error"))
        self.assertEqual(self.provider_jobs, [])
        self.assertEqual(self.hass.services.calls, [])

    async def test_dispatched_running_automation_accepts_explicit_disable_without_waiting_sequence(self):
        self.configure("automation", "on", skip=True)
        await self.open()
        self.install_background_core_fake()
        dispatch = self.hass.services.async_call

        async def service(*args, **kwargs):
            if args[1] == "turn_off":
                self.assertIs(kwargs["blocking"], True)
                self.assertIs(args[2]["stop_actions"], False)
                self.hass.services.calls.append((args, kwargs))
                self.change("off", current=1)
            else:
                await dispatch(*args, **kwargs)

        self.hass.services.async_call = service
        try:
            await self.send(self.command(op="trigger"))
            await asyncio.wait_for(self.provider_entered.wait(), .2)
            self.assertEqual(self.results()[-1]["status"], "service_dispatched")
            await self.send(self.command(2, op="disable"))
            self.assertEqual(self.results()[-1]["status"], "state_matches")
            self.assertFalse(self.provider_jobs[0].done())
            self.assertEqual([row[0][1] for row in self.hass.services.calls], ["trigger", "turn_off"])
        finally:
            self.provider_gate.set()
            await asyncio.gather(*self.provider_jobs)

    async def test_late_provider_failure_never_reports_completed_or_reopens_retired_view(self):
        self.configure("automation", skip=True)
        await self.open()
        self.install_background_core_fake(late_error=True)
        await self.send(self.command(op="trigger"))
        self.assertEqual(self.results()[-1]["status"], "service_dispatched")
        await self.owner.async_close("navigation")
        output_count = len(self.outputs)
        self.provider_gate.set()
        await asyncio.gather(*self.provider_jobs)
        await asyncio.sleep(.001)
        self.assertEqual(self.provider_errors, ["provider failure"])
        self.assertIsNone(self.owner._selection)
        self.assertEqual(len(self.outputs), output_count)
        self.assertFalse(any(row["status"] == "service_completed" for row in self.results()))

    async def test_non_trigger_action_still_waits_for_callback_and_holds_fence(self):
        await self.open()
        self.install_background_core_fake()
        await self.send(self.command())
        self.assertEqual((self.results()[-1]["status"], self.results()[-1]["reason"]), ("not_confirmed", "service_timeout"))
        self.assertIs(self.hass.services.calls[0][1]["blocking"], True)
        job = self.owner._service_task
        self.assertIsNotNone(job)
        self.assertFalse(job.done())
        self.provider_gate.set()
        await job

    async def test_action1_peer_is_unsupported_without_disabling_other_profiles(self):
        self.owner._extra_profiles = tuple(row for row in self.owner._extra_profiles if row["name"] in {"info", "lock", "media"})
        self.assertEqual([row["name"] for row in self.owner.panel_extra_profiles], ["info", "lock", "media"])
        with self.assertRaises(codec.ProtocolError): await self.open()
        self.assertEqual(self.hass.services.calls, [])


if __name__ == "__main__":
    unittest.main()
