"""Offline Agenda1 policy and actual ingress; no live calendars or services."""

import asyncio
from copy import deepcopy
from datetime import date, datetime, time, timedelta, timezone
from dataclasses import dataclass
import importlib
import json
from types import SimpleNamespace as NS
import unittest
from pathlib import Path
import ast
from unittest.mock import patch

import test_entity_control as shared
import test_extra_panels as extra
import test_ha_layout as base

model = importlib.import_module("_atmosfera_test.agenda_domain")
features = importlib.import_module("_atmosfera_test.agenda_features")
codec = shared.codec
NOW = datetime(2026, 10, 24, 10, tzinfo=timezone.utc)


class Calendar:
    def __init__(self):
        self.callbacks = []
        self.fetches = 0
        self.unsubscribes = 0

    def async_subscribe_events(self, start, end, callback):
        self.callbacks.append(callback)
        def unsubscribe():
            self.callbacks.remove(callback)
            self.unsubscribes += 1
        return unsubscribe

    def async_update_single_event_listener(self, start, end, callback):
        self.fetches += 1


base.module("homeassistant.components.calendar", CalendarEntity=Calendar, DATA_COMPONENT="calendar")


def rows(count=3):
    return [{"start": (NOW + timedelta(hours=i)).isoformat(),
             "end": (NOW + timedelta(hours=i+1)).isoformat(), "all_day": False,
             "summary": "Wydarzenie " + str(i), "description": "Opis", "location": "Dom"}
            for i in range(count)]


def environment():
    hass, state = extra.environment("calendar")
    entity = Calendar()
    source = {state.entity_id: entity}
    hass.data = {"calendar": NS(get_entity=source.get)}
    return hass, state, entity, source


class AgendaDomainTests(unittest.TestCase):
    def test_loaded_source_identity_without_registry_and_no_service_capability(self):
        hass, state, entity, source = environment()
        first = model.AgendaDomain.from_ha(hass, state)
        self.assertIs(first.entity, entity)
        self.assertEqual(first.descriptor(), model.CAPS)
        self.assertEqual(model.agenda_metadata(hass, state), {"agenda": {"version": 1, "read_only": True}})
        source[state.entity_id] = Calendar()
        self.assertNotEqual(first, model.AgendaDomain.from_ha(hass, state))
        source.clear()
        self.assertEqual(model.agenda_metadata(hass, state), {})

    def test_bounded_unordered_provider_is_not_mutated_or_copied_wholesale(self):
        value = list(reversed(rows(25)))
        original = deepcopy(value)
        start, end = model.window(NOW, "Europe/Warsaw")
        retained, more = model.bounded_events(value, start, end, "Europe/Warsaw")
        self.assertEqual(len(retained), 16)
        self.assertTrue(more)
        self.assertEqual(value, original)
        self.assertEqual(retained[0].fields["summary"], "Wydarzenie 0")
        self.assertEqual(retained[-1].fields["summary"], "Wydarzenie 15")

    def test_all_day_exclusive_end_dst_offsets_and_overlap_boundaries(self):
        value = [{"start": "2026-10-24", "end": "2026-10-27", "all_day": True, "summary": "All day"},
                 {"start": "2026-10-25T02:50:00+02:00", "end": "2026-10-25T02:10:00+01:00",
                  "all_day": False, "summary": "DST"}]
        start, end = model.window(NOW, "Europe/Warsaw")
        retained, more = model.bounded_events(value, start, end, "Europe/Warsaw")
        self.assertFalse(more)
        self.assertEqual(retained[0].fields["end_text"], "2026-10-26")
        self.assertEqual(retained[1].fields["start_text"], value[1]["start"])
        self.assertEqual(retained[1].fields["end_text"], value[1]["end"])
        edge = rows(1)[0] | {"end": NOW.isoformat(), "start": (NOW-timedelta(hours=1)).isoformat()}
        self.assertEqual(model.bounded_events([edge], start, end, "Europe/Warsaw"), ([], False))
        self.assertEqual(end.isoformat(), "2026-10-31T00:00:00+01:00")

    def test_full_semantic_change_beyond_excerpt_and_occurrences_are_preserved(self):
        start, end = model.window(NOW, "Europe/Warsaw")
        value = rows(1)[0] | {"description": "ż"*100 + "A", "summary": "<b>Żółć</b>", "uid": "same"}
        retained, _ = model.bounded_events([value, dict(value)], start, end, "Europe/Warsaw")
        self.assertEqual(len(retained), 2)
        self.assertEqual(retained[0].fields["summary"], "Żółć")
        self.assertTrue(retained[0].fields["description"].endswith("…"))
        self.assertEqual(retained[0].fields["truncated_fields"], 4)
        changed, _ = model.bounded_events([value | {"description": "ż"*100 + "B"}], start, end, "Europe/Warsaw")
        self.assertEqual(retained[0].fields, changed[0].fields)
        self.assertNotEqual(retained[0].digest, changed[0].digest)

    def test_invalid_dates_naive_values_and_nonfinite_text_fail_closed(self):
        start, end = model.window(NOW, "Europe/Warsaw")
        for delta in ({"start": "bad"}, {"start": "2026-10-24T11:00:00"}, {"all_day": 1},
                      {"end": (NOW-timedelta(hours=1)).isoformat()}, {"summary": float("nan")}, {"description": "\ud800"}):
            with self.subTest(delta=repr(delta)), self.assertRaises((model.AgendaError, UnicodeError)):
                model.bounded_events([rows(1)[0] | delta], start, end, "Europe/Warsaw")

    def test_point_event_is_valid_but_all_day_end_must_be_exclusive(self):
        start, end = model.window(NOW, "Europe/Warsaw")
        point = rows(2)[1] | {"end": rows(2)[1]["start"]}
        retained, _ = model.bounded_events([point], start, end, "Europe/Warsaw")
        self.assertEqual(len(retained), 1)
        with self.assertRaises(model.AgendaError):
            model.bounded_events([{"start": "2026-10-25", "end": "2026-10-25", "all_day": True}], start, end, "Europe/Warsaw")

    def test_layout_explicit_agenda_preserves_passive_info_and_rejects_other_domains(self):
        for domain in ("calendar",):
            self.assertEqual(base.layout.validate_action(model.ACTION, domain+".test", layout_version=3), model.ACTION)
        for domain in ("sensor", "sun", "light"):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(model.ACTION, domain+".test", layout_version=3)
        with self.assertRaises(base.layout.LayoutError):
            base.layout.validate_action(model.ACTION, "calendar.test", layout_version=2)
        self.assertEqual(base.layout.validate_action(extra.extra.INFO_ACTION, "calendar.test", layout_version=3), extra.extra.INFO_ACTION)


class AgendaOwnerTests(unittest.IsolatedAsyncioTestCase):
    bind = extra.ExtraOwnerTests.bind
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown
    send = shared.NumberOwnerTests.send

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.hass, self.state, self.calendar, self.sources = environment()
        self.owner.hass = self.hass
        self.owner._agenda_now = lambda: NOW
        self.card.update(entity_id=self.state.entity_id, type="sensor", action=dict(model.ACTION))
        self.read_allowed = True
        self.read_calls = []
        self.changed = 0
        def changed(): self.changed += 1
        self.owner._agenda_changed = changed
        async def read(context, entity):
            self.read_calls.append((context, entity))
            self.auth_entered.set()
            if self.auth_gate: await self.auth_gate.wait()
            return self.read_allowed
        self.owner.authorize_read = read
        self.owner.accept_agenda_features(self.owner.channel)

    async def open(self, seq=1):
        return await shared.NumberOwnerTests.open(self, seq, "panel")

    async def ready(self, value=None):
        self.calendar.callbacks[0](rows() if value is None else value)
        await self.owner.async_state_changed()
        return self.outputs[-1]

    def page(self, seq=1, index=1, generation=None):
        selected = self.owner._selection
        return codec.envelope("page", **selected.identity, request_seq=seq, target_index=index,
                              expected_state_generation=generation or selected.domain_state.generation)

    async def test_read_permission_grant_page_receipt_and_duplicate_zero_services(self):
        self.allowed = False
        grant = await self.open()
        self.assertEqual(grant["panel_state"]["status"], "loading")
        self.assertEqual(self.calendar.fetches, 1)
        initial = await self.ready()
        request = self.page()
        self.assertEqual(codec.decode_report(shared.wire(request)), request)
        result = await self.send(request)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(self.outputs[-2]["panel_state"]["index"], 1)
        self.assertEqual(self.outputs[-2]["state_generation"], initial["state_generation"])
        before = len(self.outputs)
        await self.send(request)
        self.assertEqual(len(self.outputs), before+1)
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.calendar.fetches, 1)
        self.assertIs(self.read_calls[-1][0], self.user)
        self.assertEqual(self.owner._selection.command, None)

    async def test_bounds_conflicts_stale_and_unchanged_are_rejected_without_fetch(self):
        await self.open(); await self.ready()
        self.assertEqual((await self.send(self.page(index=0)))["reason"], "stale_state")
        self.assertEqual((await self.send(self.page(index=2)))["reason"], "sequence_conflict")
        self.assertEqual((await self.send(self.page(2, 15)))["reason"], "stale_state")
        self.assertEqual((await self.send(self.page(1, 1)))["reason"], "stale_sequence")
        self.assertEqual(self.calendar.fetches, 1)

    async def test_list_ABA_during_read_await_cancels_page(self):
        await self.open(); first = await self.ready()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        task = asyncio.create_task(self.send(self.page()))
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.calendar.callbacks[0](rows(2))
        self.calendar.callbacks[0](rows())
        self.auth_gate.set()
        result = await task
        self.assertEqual(result["reason"], "stale_state")
        self.assertEqual(self.owner._selection.domain_state.generation, first["state_generation"]+2)
        self.assertEqual(self.owner._selection.domain_state.index, 0)

    async def test_metadata_identical_callback_preserves_generation_and_page(self):
        await self.open(); initial = await self.ready(); await self.send(self.page())
        self.state.attributes["friendly_name"] = "New title"
        repeated = await self.ready()
        self.assertEqual(repeated["state_generation"], initial["state_generation"])
        self.assertEqual(repeated["panel_state"]["index"], 1)

    async def test_close_then_late_fetch_cannot_mutate_next_selection(self):
        await self.open(); callback = self.calendar.callbacks[0]
        await self.owner.async_close()
        self.assertEqual(self.calendar.unsubscribes, 1)
        await self.open(2)
        before = len(self.outputs)
        callback(rows())
        self.assertEqual(len(self.outputs), before)
        self.assertEqual(self.owner._selection.domain_state.status, "loading")

    async def test_private_source_replacement_and_timezone_change_retire(self):
        await self.open(); await self.ready()
        self.sources[self.state.entity_id] = Calendar()
        await self.owner.async_state_changed()
        self.assertIsNone(self.owner._selection)
        self.calendar = self.sources[self.state.entity_id]
        await self.open(2)
        self.hass.config.time_zone = "UTC"
        await self.owner.async_state_changed()
        self.assertIsNone(self.owner._selection)

    async def test_empty_error_unknown_status_generations_clear_all_old_values(self):
        await self.open(); await self.ready()
        previous = self.owner._selection.domain_state.generation
        for value, status in ((None, "error"), ([], "ready")):
            self.calendar.callbacks[0](value)
            await self.owner.async_state_changed()
            field = self.outputs[-1]["panel_state"]
            self.assertEqual((field["status"], field["count"], field["index"]), (status, 0, None))
            self.assertEqual(field["summary"], "")
            self.assertGreater(self.outputs[-1]["state_generation"], previous)
            previous = self.outputs[-1]["state_generation"]
        self.state.state = "unavailable"
        await self.owner.async_state_changed()
        self.assertEqual(self.outputs[-1]["panel_state"]["status"], "unknown")

    async def test_default_off_rejects_but_old_info_keeps_working(self):
        self.owner._agenda_channel = None
        with self.assertRaises(codec.ProtocolError): await self.open()
        self.card["action"] = extra.extra.INFO_ACTION
        grant = await self.open(2)
        self.assertEqual(grant["panel_caps"]["info_type"], "calendar")
        self.assertEqual(self.calendar.fetches, 0)

    async def test_wire_closed_and_negotiation_is_not_bypassed_by_structural_ingress(self):
        grant = await self.open(); await self.ready()
        request = self.page()
        encoded = shared.wire(request)
        for flags in ({}, {"info_agenda": True}, {"extra_profiles": ("info",)}):
            with self.assertRaises(codec.ProtocolError): codec.decode(encoded, **flags)
        for update in ({"request_seq": True}, {"target_index": 16}, {"expected_state_generation": 0},
                       {"command_seq": 1}, {"op": "set_value"}, {"entity_id": "calendar.other"}):
            with self.assertRaises(codec.ProtocolError): codec.decode_report(shared.wire(request | update))
        with self.assertRaises(codec.ProtocolError):
            codec.decode_report(encoded.replace('"target_index":1', '"target_index":1,"target_index":1'))
        for delta in ({"count": True}, {"has_more": True}, {"summary": "stale"}, {"index": 0}):
            with self.assertRaises(codec.ProtocolError):
                codec.encode(grant | {"panel_state": grant["panel_state"] | delta}, info_agenda=True, extra_profiles=("info",))

    async def test_actual_corpus_and_maximum_closed_state_fields(self):
        corpus = json.loads((Path(__file__).parent / "fixtures/agenda/wire.json").read_text(encoding="utf8"))
        for row in corpus["examples"]:
            value = row["value"]
            if value["type"] != "entity_control_v1":
                continue
            self.assertEqual(codec.decode(row["json"], info_agenda=True, extra_profiles=("info",)), value)
        await self.open(); state = await self.ready()
        fields = state["panel_state"] | {key: '"' * limit for key, limit in model.LIMITS.items()}
        maximum = state | {"panel_state": fields}
        encoded = codec.encode(maximum, info_agenda=True, extra_profiles=("info",))
        self.assertLessEqual(len(encoded.encode("utf8")), 2048)
        for key, limit in model.LIMITS.items():
            with self.subTest(field=key), self.assertRaises(codec.ProtocolError):
                codec.encode(state | {"panel_state": fields | {key: "x"*(limit+1)}}, info_agenda=True, extra_profiles=("info",))
        for delta in ({"index": True}, {"count": 17}, {"request_seq": -1}, {"all_day": 1},
                      {"truncated_fields": 8}, {"updated_text": "old"}, {"has_more": True},
                      {"source": "unavailable"}, {"status": "unknown"}):
            with self.subTest(delta=delta), self.assertRaises(codec.ProtocolError):
                codec.encode(state | {"panel_state": state["panel_state"] | delta}, info_agenda=True, extra_profiles=("info",))

    async def test_actual_registered_service_schema_router_keeps_context_and_no_commands(self):
        from test_text_report_ingress import report_registration
        import voluptuous as vol
        await self.open(); await self.ready()
        calls = []
        async def report(payload, context):
            calls.append(context)
            await self.owner.async_handle(payload, context)
        bridge = NS(node_name="agenda-node", _light_control=NS(owner=self.owner, async_report_generic=report))
        self.hass.config_entries = NS(async_loaded_entries=lambda _: [NS(runtime_data=bridge)])
        registered = report_registration(self.hass)
        payload = shared.wire(self.page())
        data = registered["schema"]({"node_name": "agenda-node", "payload": payload})
        await registered["handler"](NS(data=data, context=self.user))
        self.assertEqual(self.outputs[-1]["status"], "ready")
        self.assertIs(calls[0], self.user)
        self.assertEqual(self.hass.services.calls, [])
        for invalid in (payload.replace('"target_index":', '"target_index":0,"target_index":'),
                        shared.wire(self.outputs[-1]), shared.wire(self.page() | {"op": "create_event"})):
            with self.assertRaises(vol.Invalid): registered["schema"]({"node_name": "agenda-node", "payload": invalid})
        self.owner._agenda_channel = None
        await registered["handler"](NS(data=data, context=self.user))
        self.assertEqual(self.hass.services.calls, [])
        self.assertIsNone(self.owner._selection.command)

    async def test_permission_denied_and_close_during_page_authorization(self):
        await self.open(); await self.ready(); self.read_allowed = False
        self.assertEqual((await self.send(self.page()))["reason"], "unauthorized")
        self.read_allowed = True
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        job = asyncio.create_task(self.send(self.page(2)))
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        await self.owner.async_close("navigation")
        self.auth_gate.set(); await job
        self.assertFalse(any(v["kind"] == "page_result" and v["status"] == "ready" for v in self.outputs))
        self.assertEqual(self.calendar.unsubscribes, 1)

    async def test_close_during_state_emit_cannot_publish_late_receipt(self):
        await self.open(); await self.ready()
        gate, entered = asyncio.Event(), asyncio.Event()
        original = self.owner.emit
        async def emit(value, *args):
            if value["kind"] == "state" and value["panel_state"]["request_seq"] == 1:
                entered.set(); await gate.wait()
            return await original(value, *args)
        self.owner.emit = emit
        job = asyncio.create_task(self.send(self.page()))
        await asyncio.wait_for(entered.wait(), .2)
        await self.owner.async_close("navigation")
        gate.set(); await job
        self.assertFalse(any(v["kind"] == "page_result" for v in self.outputs))
        self.assertEqual(self.hass.services.calls, [])

    async def test_source_change_during_page_emit_returns_stale_and_coalesces_new_observation(self):
        await self.open(); await self.ready()
        original = self.owner.emit
        async def emit(value, *args):
            if value["kind"] == "state" and value["panel_state"]["request_seq"] == 1:
                self.calendar.callbacks[0](rows(2))
            return await original(value, *args)
        self.owner.emit = emit
        result = await self.send(self.page())
        self.assertEqual(result["reason"], "stale_state")
        self.assertEqual(self.owner._selection.domain_state.index, 0)
        self.assertGreaterEqual(self.changed, 2)

    async def test_loading_deadline_late_recovery_and_overflow_retirement(self):
        clock = [0.0]; self.owner.clock = lambda: clock[0]
        await self.open(); clock[0] = 11
        await self.owner.async_state_changed()
        self.assertEqual(self.outputs[-1]["panel_state"]["status"], "error")
        await self.ready()
        self.assertEqual(self.outputs[-1]["panel_state"]["status"], "ready")
        self.owner._selection.domain_state.generation = 2147483647
        self.calendar.callbacks[0]([])
        await self.owner.async_state_changed()
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.outputs[-1]["kind"], "close")

    async def test_registry_identity_aba_revokes_but_presentation_does_not(self):
        await self.open(); await self.ready()
        self.assertIsNone(self.owner.observe_robot_registry_event(NS(data={"action": "update", "entity_id": self.state.entity_id,
                                                                          "changes": {"name": "old"}})))
        result = self.owner.observe_robot_registry_event(NS(data={"action": "update", "entity_id": "calendar.new",
                                                                  "changes": {"entity_id": self.state.entity_id}}))
        self.assertEqual(result["reason"], "capabilities_changed")
        self.assertIsNone(self.owner._selection)


class AgendaMockTests(unittest.IsolatedAsyncioTestCase):
    async def test_actual_provider_retains_identity_and_six_readonly_ordered_examples(self):
        @dataclass
        class Event:
            start: date | datetime
            end: date | datetime
            summary: str
            location: str | None = None
            description: str | None = None

            @staticmethod
            def local(value):
                return value if isinstance(value, datetime) else datetime.combine(value, time(), timezone.utc)

            @property
            def start_datetime_local(self):
                return self.local(self.start)

            @property
            def end_datetime_local(self):
                return self.local(self.end)

        source = Path(__file__).parents[1] / "ha_demo/atmosfera_demo/calendar.py"
        tree = ast.parse(source.read_text(encoding="utf8"))
        tree.body = [item for item in tree.body if not isinstance(item, (ast.Import, ast.ImportFrom))]
        clock = [NOW.replace(hour=23, minute=30)]
        scope = {"CalendarEntity": Calendar, "CalendarEvent": Event, "timedelta": timedelta,
                 "dt_util": NS(now=lambda: clock[0])}
        exec(compile(tree, str(source), "exec"), scope)
        added = []
        await scope["async_setup_entry"](None, None, added.extend)
        entity = added[0]
        self.assertEqual((entity.entity_id, entity._attr_name), ("calendar.atmosfera_demo_agenda", "Calendar 1"))
        self.assertFalse(any(name in type(entity).__dict__ for name in ("_attr_unique_id", "_attr_device_info", "async_create_event", "async_delete_event")))
        all_events = await entity.async_get_events(None, clock[0], clock[0] + timedelta(days=7))
        self.assertEqual(len(all_events), 6)
        self.assertEqual(all_events, sorted(all_events, key=lambda event: event.start_datetime_local))
        self.assertEqual(sum(type(event.start) is date for event in all_events), 2)
        clock[0] += timedelta(hours=1)
        self.assertEqual(entity.event.summary, "Dzień dla rodziny")
        before = tuple(entity._events)
        self.assertEqual(await entity.async_get_events(None, clock[0]+timedelta(days=20), clock[0]+timedelta(days=21)), [])
        self.assertEqual(tuple(entity._events), before)


class AgendaTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_optional_current_runtime_client_and_info_ack(self):
        api = shared.integration.transport
        for mode in ("valid", "missing", "no_info", "bad_query", "rejected", "wrong_channel", "query_client", "bind_client", "epoch"):
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
                        value = codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=extra.old_panel.KINDS)
                    elif service.name in ("entity_panel_extra_query", "entity_panel_extra_bind"):
                        value = json.loads(data["payload"])
                        value["profiles"] = [] if mode == "no_info" else [{"name": "info", "version": 1}]
                        if service.name.endswith("bind"): value["accepted"] = True
                    elif service.name == features.QUERY:
                        value = {"v": 1, "type": features.TYPE, "agenda_version": 2 if mode == "bad_query" else 1}
                        if mode == "query_client": bridge.runtime.client = NS(execute_service=execute)
                    elif service.name == features.BIND:
                        value = json.loads(data["payload"]) | {"accepted": True}
                        if mode == "rejected": value.update(accepted=False, agenda_version=0, channel="")
                        if mode == "wrong_channel": value["channel"] = "f"*32
                        if mode == "bind_client": bridge.runtime.client = NS(execute_service=execute)
                        if mode == "epoch": bridge._connection_epoch += 1
                    else: return await original(service, data, **kwargs)
                    return NS(success=True, response_data=shared.wire(value).encode())
                bridge.runtime.client.execute_service = execute
                transport = bridge._light_control
                try:
                    accepted = await transport.async_negotiate()
                    self.assertEqual(accepted, mode != "epoch")
                    self.assertEqual(transport.info_agenda_version, int(mode == "valid"))
                    if mode in ("missing", "bad_query", "query_client", "no_info"): self.assertNotIn(features.BIND, calls)
                    transport.invalidate_connection(); self.assertEqual(transport.info_agenda_version, 0)
                finally: await transport.async_shutdown()

    def test_feature_envelope_strict_duplicates_types_and_limit(self):
        good = {"v": 1, "type": features.TYPE, "agenda_version": 1}
        for value in (good | {"agenda_version": True}, good | {"extra": 0}, good | {"v": True}):
            with self.assertRaises(codec.ProtocolError):
                features.decode_features(NS(success=True, response_data=shared.wire(value).encode()))
        for raw in ('{"v":1,"v":1}', 'x'*513, '{"v":NaN}'):
            with self.assertRaises(codec.ProtocolError): features.decode_features(NS(success=True, response_data=raw.encode()))


if __name__ == "__main__":
    unittest.main()
