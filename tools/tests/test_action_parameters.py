"""Required Boolean forms; fake HA service objects, no household actions."""

import asyncio
from copy import deepcopy
import importlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

import test_action_panels as legacy
import test_ha_layout as base
import test_entity_control as shared

params = importlib.import_module("_atmosfera_test.action_parameters_domain")
features = importlib.import_module("_atmosfera_test.action_parameters_features")
codec = shared.codec
OPTIONS = dict(extra_profiles=("action",), action_dispatched=True, action_parameters=True)
FIELD = {"required": True, "selector": {"boolean": {}}, "name": "Confirm test"}


def environment(field=None):
    hass, state, _ = legacy.environment("script")
    hass.entity_registry.entries[state.entity_id].id = "registry-id"
    handlers = {"original_name": object(), "turn_off": object()}
    hass.services.async_services_for_domain = lambda name: dict(handlers) if name == "script" else {}
    hass.service_descriptions[("script", "original_name")] = {"fields": {"confirm_test": deepcopy(FIELD if field is None else field)}}
    return hass, state, handlers


class DomainTests(unittest.TestCase):
    def test_required_only_defaults_exact_and_examples_not_defaults(self):
        for default in (None, False, True):
            field = FIELD | ({} if default is None else {"default": default})
            hass, state, _ = environment(field | {"example": True})
            domain = params.ActionParametersDomain.from_ha(hass, state)
            self.assertEqual(domain.parameter_status, "ready")
            self.assertIs(domain.parameter_default, default)
            observed = params.ActionParametersObservation.from_ha(hass, state, domain)
            self.assertEqual(observed.eligible(domain), 4)
            self.assertFalse(observed.can_command(domain, "run"))
            for target in (True, False):
                self.assertTrue(observed.can_command(domain, "run", target))
                self.assertEqual(domain.service_action(state.entity_id, "run", target),
                                 ("script", "original_name", {"confirm_test": target}))
            self.assertEqual(hass.services.calls, [])

    def test_unsupported_forms_never_truncate_or_coerce(self):
        bad = [FIELD | {"required": False}, FIELD | {"required": 1}, FIELD | {"default": 0},
               FIELD | {"default": None}, FIELD | {"default": "false"}, FIELD | {"selector": {"number": {}}},
               FIELD | {"selector": {"boolean": {"read_only": True}}}, FIELD | {"name": "x" * 97},
               FIELD | {"advanced": True}, FIELD | {"name": "   "}]
        for field in bad:
            self.assertEqual(params.parameter_fields({"fields": {"test": field}}), ("unsupported", "", None, ""))
        self.assertEqual(params.parameter_fields({"fields": {"one": FIELD, "two": {"required": False}}})[0], "unsupported")
        self.assertEqual(params.parameter_fields({})[0], "metadata_unavailable")

    def test_identity_renamed_entity_and_service_incarnation(self):
        hass, state, handlers = environment()
        first = params.ActionParametersDomain.from_ha(hass, state)
        second = params.ActionParametersDomain.from_ha(hass, state)
        self.assertEqual(first, second)
        self.assertIs(first.binding.service, handlers["original_name"])
        handlers["original_name"] = object()
        self.assertNotEqual(first, params.ActionParametersDomain.from_ha(hass, state))
        # Incarnation belongs to the HA fence, never to the wire/fingerprint.
        self.assertEqual(first.descriptor(), params.ActionParametersDomain.from_ha(hass, state).descriptor())
        self.assertNotIn("registry-id", json.dumps(first.descriptor()))

    def test_direct_service_independent_of_turn_on_and_missing_stop(self):
        hass, state, handlers = environment()
        hass.services.names.remove("script.turn_on")
        self.assertEqual(params.ActionParametersDomain.from_ha(hass, state).operations, 12)
        hass.services.names.remove("script.turn_off")
        self.assertEqual(params.ActionParametersDomain.from_ha(hass, state).operations, 4)
        handlers.pop("original_name")
        domain = params.ActionParametersDomain.from_ha(hass, state)
        self.assertEqual((domain.operations, domain.run_blocked), (0, "service_unavailable"))

    def test_layout_and_render_explicit_negotiation_no_fallback(self):
        hass, state, _ = environment()
        card = base.card(entity=state.entity_id, type="action", action=params.ACTION)
        self.assertEqual(base.layout.validate_action(params.ACTION, state.entity_id, layout_version=3), params.ACTION)
        for action, entity in ((params.ACTION, "button.test"), (params.ACTION | {"value": True}, state.entity_id)):
            with self.assertRaises(base.layout.LayoutError): base.layout.validate_action(action, entity, layout_version=3)
        for enabled in (False, True):
            row = base.cards.presentation_payload(hass, [card], panel_extra_profiles=("action",),
                action_parameters_supported=enabled, press_enabled_supported=True)["cards"][2]
            self.assertEqual(row.get("control_kind"), "panel" if enabled else None)
        self.assertIsNone(base.cards.resolve_action(hass, card))

    def test_server_rejects_new_invalid_form_but_keeps_saved_form(self):
        hass, state, _ = environment(FIELD | {"required": False})
        card = base.card(entity=state.entity_id, type="action", action=params.ACTION)
        with self.assertRaises(base.layout.LayoutError): base.panel._validate_actions(hass, {"cards": [card]})
        _, entry = base.environment(base.document([card]) | {"version": 3})
        base.panel._validate_actions(hass, {"cards": [card]}, entry)
        self.assertEqual(hass.services.calls, [])

    def test_shared_actual_domain_corpus_and_strict_wire(self):
        root = Path(__file__).with_name("fixtures") / "action_parameters"
        metadata = json.loads((root / "metadata.json").read_text(encoding="utf-8"))
        wire = json.loads((root / "wire.json").read_text(encoding="utf-8"))
        self.assertEqual(len(metadata), 8)
        for row, message in zip(metadata, wire, strict=True):
            self.assertEqual(row["name"], message["name"])
            domain = params.ActionParametersDomain.from_descriptor(row["metadata"]["caps"])
            self.assertEqual(domain.fingerprint, row["metadata"]["fingerprint"])
            self.assertEqual(codec.decode(codec.encode(message["value"], **OPTIONS), **OPTIONS), message["value"])
            with self.assertRaises(codec.ProtocolError): codec.encode(message["value"], extra_profiles=("action",), action_dispatched=True)

    def test_lifecycle_subscriptions_are_scoped_and_replaced(self):
        bridge = base.BridgeTests().bridge()
        bridge.tile_cards = [base.card(entity="script.test", type="action", action=params.ACTION)]
        bridge.tile_entity_ids = ["script.test"]
        callbacks, removed, notifications, pushes = {}, [], [], []
        def listen(kind, callback):
            callbacks[kind] = callback
            return lambda: removed.append(kind)
        bridge.hass.bus = NS(async_listen=listen)
        bridge.hass.entity_registry.entries["script.test"] = NS(unique_id="original_name")
        bridge._light_control = NS(action_parameters_lifecycle_changed=notifications.append)
        bridge.async_schedule_tile_push = lambda **kwargs: pushes.append(kwargs)
        bridge._replace_tile_subscription()
        self.assertEqual(set(callbacks), {"entity_registry_updated", "service_registered", "service_removed"})
        callbacks["service_removed"](NS(event_type="service_removed", data={"domain": "script", "service": "other"}))
        self.assertEqual(pushes, [])
        callbacks["service_removed"](NS(event_type="service_removed", data={"domain": "script", "service": "original_name"}))
        self.assertEqual(pushes, [{"delay": 0}])
        bridge.tile_cards[0]["action"] = dict(legacy.action.ACTION)
        bridge._replace_tile_subscription()
        self.assertEqual(set(removed), set(callbacks))
        self.assertEqual(bridge._tile_registry_unsubscribers, [])


class OwnerTests(unittest.IsolatedAsyncioTestCase):
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown
    open = legacy.ActionOwnerTests.open

    def bind(self):
        legacy.ActionOwnerTests.bind(self)
        self.owner.accept_action_parameters_features(self.owner.channel)

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.hass, self.state, self.handlers = environment()
        self.owner.hass = self.hass
        self.card.update(entity_id=self.state.entity_id, type="action", action=params.ACTION)
        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate: await self.service_gate.wait()
            if args[1] == "turn_off": self.change("off")
        self.hass.services.async_call = service

    def command(self, seq=1, value=True, op="run"):
        command = legacy.ActionOwnerTests.command(self, seq, op)
        return command | ({"action_parameters_version": 1, "parameter_value": value} if op == "run" else {})

    async def test_true_false_one_call_context_dispatch_not_completion(self):
        for seq, value in enumerate((False, True), 1):
            await self.owner.async_close()
            grant = await self.open(seq)
            self.assertEqual(grant["eligible_actions"], 4)
            self.assertIsNone(grant["panel_caps"]["parameter_default"])
            command = self.command(value=value)
            await self.send(command)
            await self.send(command)
            args, kwargs = self.hass.services.calls[-1]
            self.assertEqual(args, ("script", "original_name", {"confirm_test": value}))
            self.assertIs(kwargs["context"], self.user)
            self.assertIs(kwargs["blocking"], False)
            self.assertEqual(self.results()[-1]["status"], "service_dispatched")
            self.assertEqual(len(self.hass.services.calls), seq)

    async def test_stop_stays_legacy_no_variables(self):
        self.state.state = "on"
        await self.open()
        await self.send(self.command(op="stop"))
        self.assertEqual(self.hass.services.calls[0][0], ("script", "turn_off", {"entity_id": "script.test"}))

    async def test_no_marker_never_falls_back_to_zero_arguments(self):
        await self.open()
        await self.send(legacy.ActionOwnerTests.command(self, op="run"))
        self.assertEqual(self.hass.services.calls, [])

    async def test_metadata_changes_during_authorization_reject_then_new_open_succeeds(self):
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        task = self.owner._selection.command.task
        await self.auth_entered.wait()
        self.hass.service_descriptions[("script", "original_name")]["fields"]["confirm_test"]["default"] = False
        self.auth_gate.set()
        await task
        self.assertEqual(self.hass.services.calls, [])
        await self.owner.async_close()
        await self.open(2)
        await self.send(self.command(value=False))
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_real_create_task_boundary_replaced_same_metadata_service_rejected(self):
        await self.open()
        original_dispatch = self.owner._command_dispatch
        queued = False
        def capture(*args):
            nonlocal queued
            result = original_dispatch(*args)
            if not queued:
                queued = True
                # _execute schedules its service job after capture returns.
                # This callback therefore runs at the actual job boundary first.
                asyncio.get_running_loop().call_soon(self.handlers.__setitem__, "original_name", object())
            return result
        self.owner._command_dispatch = capture
        await self.send(self.command())
        self.assertEqual(self.hass.services.calls, [])
        self.owner._command_dispatch = original_dispatch
        await self.owner.async_close()
        await self.open(2)
        await self.send(self.command())
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_service_and_registry_events_revoke_aba(self):
        for seq, event in enumerate((NS(event_type="service_removed", data={"domain": "script", "service": "original_name"}),
                NS(event_type="service_registered", data={"domain": "script", "service": "original_name"}),
                NS(event_type="entity_registry_updated", data={"entity_id": "script.test", "action": "remove"})), 1):
            await self.open(seq)
            close = self.owner.observe_action_parameters_lifecycle(event)
            self.assertIsNotNone(close)
            self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_principal_change_at_real_job_boundary_never_dispatches(self):
        await self.open()
        original_dispatch = self.owner._command_dispatch
        def capture(*args):
            result = original_dispatch(*args)
            asyncio.get_running_loop().call_soon(setattr, self.user, "user_id", "different-principal")
            return result
        self.owner._command_dispatch = capture
        await self.send(self.command())
        self.assertEqual(self.hass.services.calls, [])

    async def test_renewal_keeps_same_handler_and_state_telemetry_does_not_revoke(self):
        await self.open()
        service = self.owner._selection.caps["panel_domain"].binding.service
        self.state.attributes["last_triggered"] = "2026-11-07T10:00:00+00:00"
        await self.owner.async_state_changed()
        self.assertIs(self.owner._selection.caps["panel_domain"].binding.service, service)
        await self.send(self.command())
        self.assertEqual(len(self.hass.services.calls), 1)


class CodecTests(unittest.TestCase):
    def test_strict_true_false_and_no_optional_or_arbitrary_variable_keys(self):
        fixture = Path(__file__).with_name("fixtures") / "action_panel/wire/command-run.json"
        command = json.loads(fixture.read_text(encoding="utf-8"))
        for value in (True, False):
            valid = command | {"action_parameters_version": 1, "parameter_value": value}
            self.assertEqual(codec.decode(codec.encode(valid, **OPTIONS), **OPTIONS), valid)
            with self.assertRaises(codec.ProtocolError): codec.encode(valid, extra_profiles=("action",), action_dispatched=True)
            for changes in ({"parameter_value": 0}, {"parameter_value": None}, {"parameter_value": "false"},
                            {"action_parameters_version": True}, {"op": "stop"}, {"variables": {}}, {"field": "another"}):
                with self.assertRaises(codec.ProtocolError): codec.encode(valid | changes, **OPTIONS)

    def test_handshake_closed_default_off(self):
        query = {"v": 1, "type": features.TYPE, "parameters_version": 1}
        reply = lambda v: NS(success=True, response_data=json.dumps(v).encode())
        self.assertEqual(features.decode_features(reply(query)), query)
        for bad in (query | {"parameters_version": True}, query | {"extra": 1}):
            with self.assertRaises(codec.ProtocolError): features.decode_features(reply(bad))


class ParametersTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_optional_features_fence_client_runtime_channel_and_epoch(self):
        api = shared.integration.transport
        modes = ("valid", "missing", "no_action", "bad_query", "rejected", "wrong_channel",
                 "query_client", "bind_client", "epoch", "runtime", "channel")
        for mode in modes:
            with self.subTest(mode=mode):
                bridge = shared.NumberModelTransportTests().generic_bridge()
                original = bridge.runtime.client.execute_service
                for name in ("entity_panel_extra_query", "entity_panel_extra_bind", features.QUERY, features.BIND):
                    if mode == "missing" and name in (features.QUERY, features.BIND): continue
                    bridge.services[name] = NS(name=name, key=100+len(bridge.services),
                        args=[] if name == features.QUERY else [NS(name="payload", type=api.UserServiceArgType.STRING)],
                        supports_response=api.SupportsResponseType.ONLY)
                calls = []
                async def execute(service, data, **kwargs):
                    calls.append(service.name)
                    if service.name == "entity_control_get_status":
                        value = shared.codec.envelope("capability", enabled=True, max_payload_bytes=2048,
                                                      control_kinds=legacy.extra_tests.old_panel.KINDS)
                    elif service.name in ("entity_panel_extra_query", "entity_panel_extra_bind"):
                        value = json.loads(data["payload"])
                        value["profiles"] = [] if mode == "no_action" else [{"name": "action", "version": 2}]
                        if service.name.endswith("bind"): value["accepted"] = True
                    elif service.name == features.QUERY:
                        value = {"v": 1, "type": features.TYPE, "parameters_version": 2 if mode == "bad_query" else 1}
                        if mode == "query_client": bridge.runtime.client = NS(execute_service=execute)
                    elif service.name == features.BIND:
                        value = json.loads(data["payload"]) | {"accepted": True}
                        if mode == "rejected": value.update(accepted=False, parameters_version=0, channel="")
                        if mode == "wrong_channel": value["channel"] = "f"*32
                        if mode == "bind_client": bridge.runtime.client = NS(execute_service=execute)
                        if mode == "epoch": bridge._connection_epoch += 1
                        if mode == "runtime": bridge.esphome_entry.runtime_data = NS(client=bridge.runtime.client, available=True)
                        if mode == "channel": bridge._light_control.owner.channel = "f"*32
                    else: return await original(service, data, **kwargs)
                    return NS(success=True, response_data=shared.wire(value).encode())
                bridge.runtime.client.execute_service = execute
                transport = bridge._light_control
                try:
                    await transport.async_negotiate()
                    self.assertEqual(transport.action_parameters_version, int(mode == "valid"))
                    if mode in ("missing", "bad_query", "query_client", "no_action"):
                        self.assertNotIn(features.BIND, calls)
                    transport.invalidate_connection()
                    self.assertEqual(transport.action_parameters_version, 0)
                finally:
                    await transport.async_shutdown()


if __name__ == "__main__":
    unittest.main()
