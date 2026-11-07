"""Offline Info/Lock contracts: all services, contexts and sources are fakes."""

import asyncio
from copy import deepcopy
from datetime import datetime, timezone
import importlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import test_entity_control as shared
import test_panel_control as old_panel
import test_ha_layout as base

extra = importlib.import_module("_atmosfera_test.extra_panel_domain")
features = importlib.import_module("_atmosfera_test.extra_panel_features")
transport = importlib.import_module("_atmosfera_test.light_control_transport")
codec = shared.codec


def environment(domain="sensor", value=None, attrs=None):
    defaults = {"sensor": ("15.6", {"device_class": "temperature", "unit_of_measurement": "°C"}),
        "binary_sensor": ("off", {"device_class": "moisture"}), "alarm_control_panel": ("disarmed", {}),
        "calendar": ("off", {"message": "Future event", "all_day": False,
            "start_time": "2026-11-04 22:00:00", "end_time": "2026-11-04 23:00:00"}), "lock": ("unlocked", {})}
    original, attributes = defaults[domain]
    state = base.State(domain + ".test", original if value is None else value, deepcopy(attributes if attrs is None else attrs))
    state.last_updated = datetime(2026, 11, 4, 18, tzinfo=timezone.utc)
    hass, _ = base.environment(states=[state], services=["lock.lock"])
    hass.config.time_zone = "Europe/Warsaw"
    return hass, state


def snapshot(domain="sensor"):
    hass, state = environment(domain)
    model = extra.ExtraDomain.from_ha(hass, state)
    observed = extra.ExtraObservation.from_ha(hass, state, model)
    value = codec.envelope("grant", **(shared.CodecTests().identity() | {"control_kind": "panel"}),
        state_seq=1, ttl_ms=30000, title="Full observation", panel_type=model.family,
        panel_caps=model.descriptor(), panel_state=observed.descriptor(), available=observed.available,
        eligible_actions=observed.eligible(model), state_generation=1)
    return value


class ExtraModelTests(unittest.TestCase):
    def test_editor_metadata_is_bounded_and_never_exports_sensitive_source_attributes(self):
        for name in ("sensor", "binary_sensor", "alarm_control_panel", "calendar", "lock"):
            hass, state = environment(name)
            state.attributes.update(code="private", access_token="private", changed_by="private")
            before = extra.extra_metadata(hass, state)["extra_panel"]
            self.assertNotIn("private", json.dumps(before))
            self.assertEqual(set(before), {"version", "panel_type", "caps", "fingerprint", "state", "available", "eligible_actions"})
            state.last_updated += __import__('datetime').timedelta(seconds=1)
            self.assertEqual(extra.extra_metadata(hass, state)["extra_panel"]["fingerprint"], before["fingerprint"])

    def test_full_text_boundaries_never_return_prefix(self):
        for value, limit, status in (("ż" * 48, 96, "value"), ("ż" * 49, 96, "too_long"),
                                      ("x" * 16385, 96, "too_long"), ("", 96, "empty"), ("\ud800", 96, "invalid")):
            actual, text = extra.complete_text(value, limit)
            self.assertEqual(actual, status)
            self.assertEqual(text, value if status == "value" else "")

    def test_sensor_numeric_zero_negative_text_invalid_and_unit_limit(self):
        for value, attrs, expected in (("0", {"unit_of_measurement": "°C"}, "value"),
                ("-2.500", {"unit_of_measurement": "°C"}, "value"), ("a" * 97, {}, "too_long"),
                ("NaN", {"unit_of_measurement": "W"}, "invalid"), ("ready", {}, "value"),
                ("15", {"unit_of_measurement": "x" * 25}, "too_long")):
            hass, state = environment(value=value, attrs=attrs)
            observed = extra.ExtraObservation.from_ha(hass, state, extra.ExtraDomain.from_ha(hass, state)).fields
            self.assertEqual(observed["value_status"], expected)
            self.assertEqual(observed["value_text"], value if expected == "value" else "")
            self.assertNotIn("truncated_fields", observed)

    def test_binary_class_semantics_and_full_translated_status(self):
        hass, state = environment("binary_sensor")
        domain = extra.ExtraDomain.from_ha(hass, state)
        actual = extra.ExtraObservation.from_ha(hass, state, domain, "pl").fields
        self.assertEqual((actual["active"], actual["state_text"]), (False, "Sucho"))
        with patch.object(base.cards, "_translate_state_for_locale", return_value="ź" * 49):
            actual = extra.ExtraObservation.from_ha(hass, state, domain, "pl").fields
        self.assertEqual((actual["text_status"], actual["state_text"], actual["active"]), ("too_long", "", False))

    def test_alarm_and_lock_actual_phases_and_missing_lock_capability(self):
        for family, phases in (("alarm_control_panel", extra.ALARM_PHASES), ("lock", extra.LOCK_PHASES)):
            for phase in phases:
                hass, state = environment(family, phase)
                model = extra.ExtraDomain.from_ha(hass, state)
                self.assertEqual(extra.ExtraObservation.from_ha(hass, state, model).fields["phase"], phase)
        hass, state = environment("lock")
        hass.services.names = {"lock.unlock", "lock.open"}
        domain = extra.ExtraDomain.from_ha(hass, state)
        self.assertFalse(domain.lock)
        self.assertEqual(extra.ExtraObservation.from_ha(hass, state, domain).eligible(domain), 0)

    def test_unknown_removes_old_content_and_preserves_source_metadata_only(self):
        for name in ("sensor", "binary_sensor", "alarm_control_panel", "calendar", "lock"):
            for value in ("unknown", "unavailable"):
                hass, state = environment(name, value)
                domain = extra.ExtraDomain.from_ha(hass, state)
                observed = extra.ExtraObservation.from_ha(hass, state, domain)
                self.assertFalse(observed.available)
                self.assertEqual(observed.eligible(domain), 0)
                self.assertEqual(observed.fields["source"], value)
                for key in ("value_text", "state_text", "summary", "start_text", "end_text", "zone_text", "location", "description"):
                    if key in observed.fields:
                        self.assertEqual(observed.fields[key], "")

    def test_calendar_none_invalid_all_day_and_local_DST_wall_fields(self):
        hass, state = environment("calendar", attrs={})
        domain = extra.ExtraDomain.from_ha(hass, state)
        self.assertEqual(extra.ExtraObservation.from_ha(hass, state, domain).fields["event"], "none")
        state.attributes["message"] = "partial"
        self.assertEqual(extra.ExtraObservation.from_ha(hass, state, domain).fields["event"], "invalid")
        state.attributes.update(all_day=True, start_time="2026-10-24 00:00:00", end_time="2026-10-27 00:00:00")
        fields = extra.ExtraObservation.from_ha(hass, state, domain).fields
        self.assertEqual((fields["start_text"], fields["end_text"], fields["zone_text"]), ("2026-10-24", "2026-10-26", "Europe/Warsaw"))
        state.attributes.update(all_day=False, start_time="2026-10-25 02:50:00", end_time="2026-10-25 02:10:00")
        fields = extra.ExtraObservation.from_ha(hass, state, domain).fields
        self.assertEqual(fields["start_text"], "2026-10-25 02:50:00")
        self.assertEqual(fields["end_text"], "2026-10-25 02:10:00")
        state.attributes["start_time"] = "2026-10-25 02:50:00Z"
        self.assertEqual(extra.ExtraObservation.from_ha(hass, state, domain).fields["event"], "invalid")

    def test_calendar_only_descriptions_can_be_marked_excerpts(self):
        hass, state = environment("calendar")
        state.attributes.update(message="ż" * 90, location="L" * 120, description="D" * 90)
        fields = extra.ExtraObservation.from_ha(hass, state, extra.ExtraDomain.from_ha(hass, state)).fields
        self.assertEqual(fields["truncated_fields"], 7)
        self.assertTrue(all(fields[k].endswith("…") for k in ("summary", "location", "description")))
        self.assertEqual(fields["start_text"], "2026-11-04 22:00:00")

    def test_generation_signature_ignores_observation_time_but_not_lock_ABA(self):
        for name in ("sensor", "lock"):
            hass, state = environment(name)
            domain = extra.ExtraDomain.from_ha(hass, state)
            before = extra.ExtraObservation.from_ha(hass, state, domain)
            state.last_updated += __import__('datetime').timedelta(seconds=1)
            if name == "sensor": state.state = "16"
            self.assertEqual(extra.ExtraObservation.from_ha(hass, state, domain).command_state, before.command_state)
            if name == "lock":
                state.state = "locked"
                self.assertNotEqual(extra.ExtraObservation.from_ha(hass, state, domain).command_state, before.command_state)

    def test_info_layout_is_explicit_passive_and_negotiated(self):
        for name in ("sensor", "binary_sensor", "alarm_control_panel", "calendar", "lock"):
            hass, state = environment(name)
            action = extra.LOCK_ACTION if name == "lock" else extra.INFO_ACTION
            for card_type in (("entity",) if name == "lock" else ("sensor", "entity")):
                card = base.card(entity=state.entity_id, type=card_type, action=action)
                self.assertEqual(base.layout.validate_layout(base.document([card]) | {"version": 3})["cards"][0]["action"], action)
                self.assertIsNone(base.cards.resolve_action(hass, card))
                for profiles in ((), (action["property"],)):
                    row = base.cards.presentation_payload(hass, [card], panel_extra_profiles=profiles, press_enabled_supported=True)["cards"][2]
                    self.assertEqual(row.get("control_kind"), "panel" if profiles else None)
                    if not profiles: self.assertFalse(row["press_enabled"])
            self.assertEqual(hass.services.calls, [])
        for entity, action in (("lock.test", extra.INFO_ACTION), ("sensor.test", extra.LOCK_ACTION),
                ("input_text.test", extra.INFO_ACTION), ("alarm_control_panel.test", extra.LOCK_ACTION)):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=3)


class ExtraCodecTests(unittest.TestCase):
    def test_generated_maximum_and_actual_source_fixtures_remain_closed_and_bounded(self):
        root = Path(__file__).with_name("fixtures") / "extra_panel"
        for path in (root / "maxima.json", root / "observations.json"):
            rows = json.loads(path.read_text(encoding="utf8"))
            self.assertTrue(rows)
            for name, row in rows.items():
                with self.subTest(fixture=name):
                    self.assertEqual(len(row["json"].encode()), row["size_utf8"])
                    if name.startswith("extra_"):
                        self.assertLessEqual(row["size_utf8"], 512)
                        value = row["value"]
                        response = NS(success=True, response_data=row["json"].encode())
                        self.assertEqual(features.decode_response(response, channel=value["channel"],
                            offered=value["profiles"], bind=name == "extra_bind_success"), value)
                    else:
                        self.assertLessEqual(row["size_utf8"], 2048)
                        self.assertEqual(codec.decode(row["json"], extra_profiles=("info", "lock")), row["value"])

    def test_all_snapshots_require_independent_negotiation_and_closed_shape(self):
        for name in ("sensor", "binary_sensor", "alarm_control_panel", "calendar", "lock"):
            value = snapshot(name)
            encoded = codec.encode(value, extra_profiles=("info", "lock"))
            self.assertEqual(codec.decode(encoded, extra_profiles=("info", "lock")), value)
            self.assertLessEqual(len(encoded.encode()), 2048)
            with self.assertRaises(codec.ProtocolError): codec.decode(encoded)
            for updates in ({"extra": 1}, {"available": not value["available"]}, {"eligible_actions": 31},
                    {"panel_state": value["panel_state"] | {"extra": None}}, {"panel_caps": value["panel_caps"] | {"extra": None}}):
                with self.assertRaises(codec.ProtocolError): codec.encode(value | updates, extra_profiles=("info", "lock"))
            with self.assertRaises(codec.ProtocolError):
                codec.decode(encoded.replace('"source":', '"source":"known","source":'), extra_profiles=("info", "lock"))

    def test_overflow_or_error_cannot_carry_old_text_or_invent_binary_boolean(self):
        for name in ("sensor", "binary_sensor", "alarm_control_panel"):
            value = snapshot(name)
            status, text = ("value_status", "value_text") if name == "sensor" else ("text_status", "state_text")
            for invalid in ({status: "too_long"}, {status: "unknown"}, {text: "x" * 97}, {"truncated_fields": 1}):
                with self.assertRaises(codec.ProtocolError):
                    codec.encode(value | {"panel_state": value["panel_state"] | invalid}, extra_profiles=("info", "lock"))

    def test_only_lock_operation_structurally_added_and_no_targets_or_code(self):
        identity = {key: snapshot("lock")[key] for key in codec.SELECTION}
        command = codec.envelope("command", **identity, command_seq=1, op="lock", expected_state_generation=1)
        self.assertEqual(codec.decode(codec.encode(command, extra_profiles=("lock",)), extra_profiles=("lock",)), command)
        for value in (command, command | {"op": "unlock"}, command | {"op": "open"}, command | {"code": "1234"}, command | {"target_index": 0}):
            with self.assertRaises(codec.ProtocolError):
                codec.encode(value, extra_profiles=() if value == command else ("lock",))

    def test_unknown_semantic_boolean_or_phase_cannot_carry_a_known_status_text(self):
        for name, field, unknown in (("binary_sensor", "active", None), ("alarm_control_panel", "phase", "unknown")):
            value = snapshot(name)
            with self.assertRaises(codec.ProtocolError):
                codec.encode(value | {"panel_state": value["panel_state"] | {field: unknown}}, extra_profiles=("info",))
            invalid = value | {"panel_state": value["panel_state"] | {field: unknown, "text_status": "invalid", "state_text": ""}}
            self.assertEqual(codec.decode(codec.encode(invalid, extra_profiles=("info",)), extra_profiles=("info",)), invalid)

    def test_extra_handshake_closed_subset_order_and_exact_512_bound(self):
        offered = list(features.PROFILES)
        channel = "a" * 32
        query = json.loads(features.payload(channel, offered))
        def reply(value): return NS(success=True, response_data=shared.wire(value).encode())
        self.assertEqual(features.decode_response(reply(query), channel=channel, offered=offered), query)
        self.assertTrue(features.decode_response(reply(query | {"accepted": True}), channel=channel, offered=offered, bind=True)["accepted"])
        for invalid in (query | {"profiles": offered[::-1]}, query | {"profiles": offered * 2},
                query | {"profiles": [{"name": "info", "version": 2}]}, query | {"channel": "b" * 32}, query | {"extra": 0}):
            with self.assertRaises(codec.ProtocolError): features.decode_response(reply(invalid), channel=channel, offered=offered)
        max_profiles = [{"name": chr(97+i) * 24, "version": 255} for i in range(8)]
        maximum = json.loads(features.payload(channel, max_profiles)) | {"accepted": True}
        self.assertEqual(len(shared.wire(maximum).encode()), 512)
        features.decode_response(reply(maximum), channel=channel, offered=max_profiles, bind=True)


class ExtraOwnerTests(unittest.IsolatedAsyncioTestCase):
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown

    def bind(self):
        value = self.owner.prepare_bind(shared.wire(codec.envelope("capability", enabled=True, max_payload_bytes=2048,
            control_kinds=old_panel.KINDS)), epoch=1, runtime=self.runtime)
        self.owner.accept_bind(shared.wire(value), epoch=1, runtime=self.runtime)
        self.owner.accept_panel_features(self.owner.channel, list(old_panel.panel.PANEL_TYPES))
        self.owner.accept_extra_features(self.owner.channel, list(features.PROFILES))

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.read_allowed = True
        self.read_calls = []
        async def read(context, entity):
            self.read_calls.append((context, entity))
            self.auth_entered.set()
            if self.auth_gate: await self.auth_gate.wait()
            return self.read_allowed
        self.owner.authorize_read = read
        self.configure("sensor")

    def configure(self, name):
        self.hass, self.state = environment(name)
        self.owner.hass = self.hass
        self.card.update(entity_id=self.state.entity_id, type="entity", action=extra.LOCK_ACTION if name == "lock" else extra.INFO_ACTION)
        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate: await self.service_gate.wait()
            if self.apply: self.change("locked")
        self.hass.services.async_call = service

    async def open(self, seq=1):
        return await shared.NumberOwnerTests.open(self, seq, "panel")

    def command(self, seq=1, **changes):
        selected = self.owner._selection
        return codec.envelope("command", **selected.identity, command_seq=seq, op="lock",
            expected_state_generation=selected.domain_state[2]) | changes

    async def test_info_read_only_user_opens_and_renews_but_never_commands(self):
        self.allowed = False
        grant = await self.open()
        self.assertEqual(grant["panel_type"], "info")
        self.assertEqual(grant["eligible_actions"], 0)
        await self.owner.async_state_changed()
        self.assertEqual(len(self.read_calls), 2)
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["reason"], "unsupported")
        self.assertEqual(self.hass.services.calls, [])

    async def test_info_read_default_deny_and_permission_loss_revokes(self):
        deny = importlib.import_module("_atmosfera_test.extra_panel_control")._deny_read
        self.owner.authorize_read = deny
        with self.assertRaises(codec.ProtocolError): await self.open()
        self.owner.authorize_read = lambda *_: asyncio.sleep(0, result=True)
        await self.open(2)
        self.owner.authorize_read = deny
        await self.owner.async_state_changed()
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_info_measurement_preserves_generation_unknown_and_class_do_not(self):
        await self.open()
        self.change("16")
        self.assertEqual(self.owner._selection.domain_state[2], 1)
        self.change("unknown")
        self.assertEqual(self.owner._selection.domain_state[2], 2)
        self.change("16")
        self.assertEqual(self.owner._selection.domain_state[2], 3)
        self.change("16", device_class="humidity")
        self.assertIsNone(self.owner._selection)

    async def test_read_auth_await_card_rebind_cannot_grant_control(self):
        self.auth_gate = asyncio.Event()
        job = asyncio.create_task(self.open())
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.configure("lock")
        self.auth_gate.set()
        with self.assertRaises(codec.ProtocolError): await job
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_lock_requires_control_not_read_and_only_fresh_locked_proves_match(self):
        self.configure("lock")
        self.allowed = False
        with self.assertRaises(codec.ProtocolError): await self.open()
        self.allowed = True
        await self.open(2)
        self.assertEqual(self.read_calls, [])
        await self.send(self.command())
        self.assertEqual(self.hass.services.calls[0][0], ("lock", "lock", {"entity_id": "lock.test"}))
        self.assertIs(self.hass.services.calls[0][1]["context"], self.user)
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        await self.send(self.command(2))
        self.assertEqual(len(self.hass.services.calls), 1)
        self.assertEqual(self.results()[-1]["reason"], "stale_state")

    async def test_lock_source_ABA_during_authorization_never_dispatches(self):
        self.configure("lock")
        await self.open()
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("locked")
        self.change("unlocked")
        self.auth_gate.set()
        await asyncio.wait_for(self.owner._selection.command.task, .4)
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["reason"], "stale_state")

    async def test_lock_callback_without_feedback_is_not_mechanical_success(self):
        self.configure("lock")
        await self.open()
        self.apply = False
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["status"], "not_confirmed")
        self.assertNotIn("service_completed", [v["status"] for v in self.results()])

    async def test_lock_missing_service_allows_passive_view_and_lost_capability_revokes(self):
        self.configure("lock")
        self.hass.services.names.clear()
        grant = await self.open()
        self.assertFalse(grant["panel_caps"]["lock"])
        await self.send(self.command())
        self.assertEqual(self.hass.services.calls, [])
        self.hass.services.names.add("lock.lock")
        self.change("unlocked")
        self.assertIsNone(self.owner._selection)

    async def test_cross_family_late_lock_token_and_failed_bind_do_not_change_owner(self):
        self.configure("lock")
        await self.open()
        old = self.command()
        profiles = self.owner.panel_extra_profiles
        with self.assertRaises(codec.ProtocolError): self.owner.accept_extra_features(self.owner.channel, [{"name": "media", "version": 1}])
        self.assertEqual(self.owner.panel_extra_profiles, profiles)
        await self.owner.async_close()
        self.configure("sensor")
        await self.open(2)
        with self.assertRaises(codec.ProtocolError): await self.send(old)
        self.assertEqual(self.hass.services.calls, [])

    async def test_reconnect_resets_only_extra_admission_and_keeps_old_shapes_exact(self):
        await self.owner.async_disconnect()
        self.assertEqual(self.owner.panel_extra_profiles, [])
        self.bind()
        self.assertEqual(self.owner.panel_types, ("timer", "remote", "power"))
        self.owner._extra_channel = None
        with self.assertRaises(codec.ProtocolError): await self.open()
        self.assertEqual(base.layout.device_profile()["schema_panel_types"], ["timer", "remote", "power"])


class ReadPolicyTests(unittest.IsolatedAsyncioTestCase):
    async def test_public_context_read_and_control_are_distinct_and_fail_closed(self):
        sys.modules["homeassistant.auth.permissions.const"].POLICY_READ = "read"
        policies = []
        user = NS(is_active=True, permissions=NS(check_entity=lambda entity, policy: policies.append((entity, policy)) or policy == "read"))
        hass = NS(auth=NS(async_get_user=lambda _: asyncio.sleep(0, result=user)))
        context = shared.integration.Context("reader")
        self.assertTrue(await transport.authorize_ha_read_context(hass, context, "sensor.test"))
        self.assertFalse(await transport.authorize_ha_context(hass, context, "lock.test"))
        self.assertEqual(policies, [("sensor.test", "read"), ("lock.test", "control")])
        self.assertFalse(await transport.authorize_ha_read_context(hass, None, "sensor.test"))
        user.is_active = False
        self.assertFalse(await transport.authorize_ha_read_context(hass, context, "sensor.test"))


class ExtraTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_optional_profiles_are_strict_channel_bound_and_do_not_change_old_negotiations(self):
        detail_features = importlib.import_module("_atmosfera_test.detail_features")
        panel_features = importlib.import_module("_atmosfera_test.panel_features")
        for mode in ("valid", "subset", "empty", "missing", "wrong_channel", "wrong_version", "foreign_profile",
                     "bind_rejected", "epoch_query", "epoch_bind"):
            with self.subTest(mode=mode):
                bridge = shared.NumberModelTransportTests().generic_bridge()
                original = bridge.runtime.client.execute_service
                names = ["entity_panel_get_features", "entity_panel_bind_features", "entity_detail_get_features", "entity_detail_bind_features"]
                if mode != "missing":
                    names += ["entity_panel_extra_query", "entity_panel_extra_bind"]
                calls = []
                for name in names:
                    bridge.services[name] = NS(name=name, key=120 + len(bridge.services),
                        args=[] if "get_features" in name else [NS(name="payload", type=transport.UserServiceArgType.STRING)],
                        supports_response=transport.SupportsResponseType.ONLY)

                async def execute(service, data, **kwargs):
                    calls.append(service.name)
                    if service.name == "entity_panel_get_features":
                        value = {"v": 1, "type": panel_features.TYPE, "panel_version": 1, "panel_types": ["timer", "remote", "power"]}
                    elif service.name == "entity_detail_get_features":
                        value = {"v": 1, "type": detail_features.TYPE, "detail_version": 1, "light_detail_version": 1, "climate_panel_version": 1}
                    elif service.name in {"entity_panel_bind_features", "entity_detail_bind_features"}:
                        value = json.loads(data["payload"]) | {"accepted": True}
                    elif service.name in {"entity_panel_extra_query", "entity_panel_extra_bind"}:
                        value = json.loads(data["payload"])
                        self.assertEqual(value["type"], features.TYPE)
                        if service.name.endswith("query"):
                            self.assertEqual(value["profiles"], list(features.PROFILES))
                            if mode == "subset": value["profiles"] = [dict(features.PROFILES[0])]
                            if mode == "empty": value["profiles"] = []
                            if mode == "wrong_channel": value["channel"] = "f" * 32
                            if mode == "wrong_version": value["profiles"] = [{"name": "info", "version": 2}]
                            if mode == "foreign_profile": value["profiles"] = [{"name": "future_media", "version": 1}]
                            if mode == "epoch_query": bridge._connection_epoch += 1
                        else:
                            value["accepted"] = mode != "bind_rejected"
                            if mode == "bind_rejected": value["profiles"] = []
                            if mode == "epoch_bind": bridge._connection_epoch += 1
                    else:
                        response = await original(service, data, **kwargs)
                        if service.name == "entity_control_get_status":
                            value = json.loads(response.response_data)
                            value["control_kinds"].append("panel")
                            response.response_data = shared.wire(value).encode()
                        return response
                    return NS(success=True, response_data=shared.wire(value).encode())

                bridge.runtime.client.execute_service = execute
                adapter = bridge._light_control
                try:
                    success = await adapter.async_negotiate()
                    lost = mode.startswith("epoch_")
                    self.assertEqual(success, not lost)
                    expected = list(features.PROFILES) if mode == "valid" else [dict(features.PROFILES[0])] if mode == "subset" else []
                    self.assertEqual(adapter.panel_extra_profiles, expected)
                    if not lost:
                        self.assertEqual(adapter.panel_types, ("timer", "remote", "power"))
                        self.assertTrue(adapter.light_detail_supported)
                        self.assertTrue(adapter.climate_panel_supported)
                        self.assertTrue(adapter.number_supported)
                    if mode in {"empty", "wrong_channel", "wrong_version", "foreign_profile", "epoch_query", "missing"}:
                        self.assertNotIn("entity_panel_extra_bind", calls)
                    adapter.invalidate_connection()
                    self.assertEqual(adapter.panel_extra_profiles, [])
                finally:
                    await adapter.async_shutdown()


if __name__ == "__main__":
    unittest.main()
