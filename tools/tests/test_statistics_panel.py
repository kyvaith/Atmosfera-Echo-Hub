"""Statistics adapter/owner tests; no live Recorder, HA or synthetic live rows."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from enum import IntEnum
import importlib
import json
import runpy
from pathlib import Path
import time
import threading
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import test_entity_control as shared
import test_extra_panels as extra
import test_ha_layout as base

model = importlib.import_module("_atmosfera_test.statistics_domain")
reader = importlib.import_module("_atmosfera_test.statistics_recorder")
policy = importlib.import_module("_atmosfera_test.statistics_control")
features = importlib.import_module("_atmosfera_test.statistics_features")
NOW = datetime(2026, 10, 25, 9, 43, tzinfo=timezone.utc)
END = model.window_end(NOW)
UnitOfTemperature = runpy.run_path(str(Path(__file__).parent / "fixtures/statistics/core202611_unit_temperature.py"))["UnitOfTemperature"]


class Sensor:
    state_class = "measurement"
    device_class = "temperature"
    unit_of_measurement = "°C"


base.module("homeassistant.components.sensor", SensorEntity=Sensor, DATA_COMPONENT="sensor")


def environment():
    state = base.State("sensor.test", "15.6", {"state_class": "measurement", "device_class": "temperature", "unit_of_measurement": "°C"})
    hass, _ = base.environment(states=[state])
    hass.config.time_zone = "Europe/Warsaw"
    sensor = Sensor()
    sources = {state.entity_id: sensor}
    hass.data = {"sensor": NS(get_entity=sources.get)}
    return hass, state, sensor, sources


def rows(values=((0, -2.0, 0.0, 3.0), (2, 0.0, 1.0, 2.0)), unit="°C"):
    return [(7, "recorder", 1, unit, "temperature", (END - 24 + i) * 3600, low, mean, high)
            for i, low, mean, high in values]


def dataset(value=None):
    return reader.normalized(rows() if value is None else value, END, "°C", lambda *_: lambda x: x)


class StatisticsDataTests(unittest.TestCase):
    def test_actual_core_temperature_enum_is_normalized_before_domain_fence(self):
        for unit in UnitOfTemperature:
            with self.subTest(unit=repr(unit)):
                hass, state, sensor, sources = environment()
                state.attributes["unit_of_measurement"] = sensor.unit_of_measurement = unit
                self.assertIsInstance(unit, str)
                self.assertIsNot(type(unit), str)
                domain = model.StatisticsDomain.from_ha(hass, state)
                self.assertIs(domain.entity, sensor)
                self.assertIs(type(domain.unit), str)
                self.assertEqual(domain.unit, str(unit))
                self.assertTrue(all(type(v) is str for v in domain.qualification))
                self.assertEqual(model.statistics_metadata(hass, state), {"statistics": {"version": 1, "read_only": True, "hours": 24}})
                fields = model.fields_for(domain, END)
                self.assertEqual(fields["status"], "loading")
                self.assertIs(type(fields["unit"]), str)
                model.validate_fields(fields)
                state.attributes["unit_of_measurement"] = sensor.unit_of_measurement = str(unit)
                self.assertEqual(domain, model.StatisticsDomain.from_ha(hass, state))
                sources[state.entity_id] = Sensor()
                self.assertNotEqual(domain, model.StatisticsDomain.from_ha(hass, state))

    def test_string_subclass_fence_preserves_unit_changes_and_rejects_coercion(self):
        class Text(str):
            pass

        class LooksLikeUnit:
            def __str__(self):
                return "°C"

        hass, state, sensor, _ = environment()
        hass.config.time_zone = Text("Europe/Warsaw")
        for key in ("state_class", "device_class", "unit_of_measurement"):
            state.attributes[key] = Text(state.attributes[key])
            setattr(sensor, key, Text(getattr(sensor, key)))
        first = model.StatisticsDomain.from_ha(hass, state)
        self.assertIs(type(first.zone), str)
        self.assertTrue(all(type(v) is str for v in first.qualification))
        state.attributes["unit_of_measurement"] = sensor.unit_of_measurement = UnitOfTemperature.FAHRENHEIT
        changed = model.StatisticsDomain.from_ha(hass, state)
        self.assertNotEqual(first, changed)
        state.attributes["unit_of_measurement"] = sensor.unit_of_measurement = UnitOfTemperature.CELSIUS
        self.assertEqual(first, model.StatisticsDomain.from_ha(hass, state))
        for bad in (0, True, b"C", LooksLikeUnit()):
            state.attributes["unit_of_measurement"] = bad
            self.assertEqual(model.statistics_metadata(hass, state), {})
        state.attributes["unit_of_measurement"] = sensor.unit_of_measurement = None
        self.assertIsNone(model.StatisticsDomain.from_ha(hass, state).unit)

    def test_loaded_identity_metadata_no_query_and_nonregistry_source(self):
        hass, state, sensor, sources = environment()
        domain = model.StatisticsDomain.from_ha(hass, state)
        self.assertIs(domain.entity, sensor)
        self.assertIsNone(domain.registry)
        self.assertEqual(model.statistics_metadata(hass, state), {"statistics": {"version": 1, "read_only": True, "hours": 24}})
        sources[state.entity_id] = Sensor()
        self.assertNotEqual(domain, model.StatisticsDomain.from_ha(hass, state))
        sources.clear()
        self.assertEqual(model.statistics_metadata(hass, state), {})

    def test_totals_circular_and_string_types_do_not_advertise(self):
        for state_class in ("total", "total_increasing", "measurement_angle", None):
            hass, state, sensor, _ = environment()
            state.attributes["state_class"] = sensor.state_class = state_class
            self.assertEqual(model.statistics_metadata(hass, state), {})

    def test_utc24_dst_dates_negative_zero_gaps_and_singleton_flat(self):
        hass, state, _, _ = environment()
        fields = model.fields_for(model.StatisticsDomain.from_ha(hass, state), END)
        self.assertTrue(fields["start_text"].endswith("+02:00"))
        self.assertTrue(fields["end_text"].endswith("+01:00"))
        result = dataset()
        fields.update(result.fields)
        model.validate_fields(fields)
        self.assertEqual(fields["valid_mask"], 5)
        self.assertEqual(fields["packed_q"][12:24], "0"*12)
        self.assertEqual(fields["axis_min_text"], "-2.0")
        flat = dataset(rows(((23, 0, 0, 0),)))
        self.assertTrue(flat.fields["flat"])
        self.assertEqual(flat.fields["packed_q"][-12:], "01f4"*3)
        self.assertEqual(flat.fields["valid_mask"], 1 << 23)

    def test_empty_missing_metadata_and_incomplete_triple_are_distinct(self):
        with self.assertRaisesRegex(model.StatisticsError, "no_metadata"):
            dataset([])
        self.assertEqual(dataset([(7, "recorder", 1, "°C", "temperature", None, None, None, None)]).fields["status"], "empty")
        self.assertEqual(dataset(rows(((0, None, 2, 3),))).fields["status"], "empty")

    def test_invalid_timestamp_metadata_and_nonfinite_values_fail_closed(self):
        bad = [rows() + rows(), rows(((24, 0, 1, 2),)), rows(((0, 5, 4, 6),)), rows(((0, 0, float("nan"), 2),)),
               [rows()[0][:-4] + (rows()[0][5] + 1, 0, 1, 2)], [rows()[0][:2] + (2,) + rows()[0][3:]],
               [(7, "external", 1, "°C", "temperature", None, None, None, None)]]
        for value in bad:
            with self.subTest(value=repr(value)), self.assertRaises(model.StatisticsError):
                dataset(value)

    def test_finite_extremes_do_not_overflow_and_hidden_change_changes_digest(self):
        result = dataset(rows(((0, -1.7976931348623157e308, 0, 1.7976931348623157e308),)))
        self.assertEqual(result.fields["packed_q"][:12], "000001f403e8")
        first = dataset(rows(((0, 0, .500001, 1),)))
        second = dataset(rows(((0, 0, .500002, 1),)))
        self.assertEqual(first.fields, second.fields)
        self.assertNotEqual(first.digest, second.digest)

    def test_unit_conversion_none_is_only_identity_for_identical_units(self):
        calls = []
        def factory(kind, old, new):
            calls.append((kind, old, new))
            return (lambda v: (v - 32) * 5 / 9) if (old, new) == ("°F", "°C") else None
        base.module("homeassistant.components.recorder")
        base.module("homeassistant.components.recorder.statistics", _get_unit_converter_func=factory)
        result = reader.normalized(rows(((0, 32, 50, 68),), "°F"), END, "°C")
        self.assertEqual((result.fields["axis_min_text"], result.fields["axis_max_text"]), ("0.0", "20.0"))
        self.assertEqual(calls, [("temperature", "°F", "°C")])
        with self.assertRaisesRegex(model.StatisticsError, "unit_incompatible"):
            reader.normalized(rows(unit="bad"), END, "°C")
        reader.normalized(rows(), END, "°C")
        self.assertEqual(len(calls), 2)

    def test_wire_strict_default_off_and_context_independent_from_current(self):
        hass, state, _, _ = environment()
        fields = model.fields_for(model.StatisticsDomain.from_ha(hass, state), END, "unavailable") | dataset().fields
        packet = shared.codec.envelope("state", channel="a"*32, open_seq=1, slot=2, card_id="card-2", revision=4,
            control_kind="panel", token="b"*32, state_seq=1, ttl_ms=30000, title="Temperature",
            panel_type="info", panel_caps=model.CAPS, panel_state=fields, available=True,
            eligible_actions=0, state_generation=1)
        raw = shared.wire(packet)
        self.assertEqual(shared.codec.decode(raw, info_statistics=True, extra_profiles=("info",)), packet)
        # A statistics STATE is HA->device, never a native report.
        with self.assertRaisesRegex(shared.codec.ProtocolError, "direction"):
            shared.codec.decode_report(raw)
        with self.assertRaises(shared.codec.ProtocolError):
            shared.codec.decode(raw, extra_profiles=("info",))
        for update in ({"valid_mask": True}, {"packed_q": "f"*288}, {"flat": 1}, {"current_status": "live"},
                       {"axis_min_text": "ą"}, {"zone_text": ""}, {"source": "unavailable"}, {"unit": "x"*33}):
            changed = deepcopy(packet); changed["panel_state"].update(update)
            with self.subTest(update=update), self.assertRaises(shared.codec.ProtocolError):
                shared.codec.decode(shared.wire(changed), info_statistics=True, extra_profiles=("info",))
        with self.assertRaises(shared.codec.ProtocolError):
            shared.codec.decode(raw.replace('"valid_mask":5', '"valid_mask":5,"valid_mask":5'),
                                info_statistics=True, extra_profiles=("info",))

    def test_layout_explicit_closed_action_never_changes_existing_info(self):
        self.assertEqual(base.layout.validate_action(model.ACTION, "sensor.test", layout_version=3), model.ACTION)
        for entity in ("calendar.test", "input_number.test", "light.test"):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(model.ACTION, entity, layout_version=3)
        with self.assertRaises(base.layout.LayoutError):
            base.layout.validate_action(model.ACTION | {"hours": 48}, "sensor.test", layout_version=3)
        with self.assertRaises(base.layout.LayoutError):
            base.layout.validate_action(model.ACTION, "sensor.test", layout_version=2)
        self.assertEqual(base.layout.validate_action(extra.extra.INFO_ACTION, "sensor.test", layout_version=3), extra.extra.INFO_ACTION)

    def test_feature_closed_query_bind_negative_and_boolean_version(self):
        import json
        query = {"v": 1, "type": features.TYPE, "statistics_version": 1}
        self.assertEqual(features.decode_features(NS(success=True, response_data=json.dumps(query).encode())), query)
        accepted = query | {"channel": "a"*32, "accepted": True}
        self.assertEqual(features.decode_features(NS(success=True, response_data=json.dumps(accepted).encode()), bind=True), accepted)
        for value in (query | {"statistics_version": True}, query | {"extra": 1}, accepted | {"channel": ""}):
            with self.assertRaises(shared.codec.ProtocolError):
                features.decode_features(NS(success=True, response_data=json.dumps(value).encode()), bind="accepted" in value)


class StatisticsOwnerTests(unittest.IsolatedAsyncioTestCase):
    bind = extra.ExtraOwnerTests.bind
    send = shared.NumberOwnerTests.send

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.hass, self.state, self.sensor, self.sources = environment()
        self.owner.hass = self.hass
        self.owner._statistics_now = lambda: NOW
        self.card.update(entity_id=self.state.entity_id, type="sensor", action=dict(model.ACTION))
        self.read_allowed = True
        self.read_calls = []
        async def read(context, entity):
            self.read_calls.append((context, entity))
            self.auth_entered.set()
            if self.auth_gate: await self.auth_gate.wait()
            return self.read_allowed
        self.owner.authorize_read = read
        self.owner.accept_statistics_features(self.owner.channel)
        self.jobs = []
        def submit(*args):
            future = asyncio.get_running_loop().create_future()
            self.jobs.append((future, args))
            return future
        self.recorder = NS(async_add_executor_job=submit)
        self.recorder_patch = patch.object(policy, "ready_recorder", return_value=self.recorder)
        self.recorder_patch.start()

    async def asyncTearDown(self):
        await shared.NumberOwnerTests.asyncTearDown(self)
        for future, _ in self.jobs:
            if not future.done(): future.set_result(dataset())
        await asyncio.sleep(0)
        self.recorder_patch.stop()

    async def open(self, seq=1):
        return await shared.NumberOwnerTests.open(self, seq, "panel")

    async def finish(self, value=None):
        self.jobs[-1][0].set_result(dataset() if value is None else value)
        await asyncio.sleep(0)
        await self.owner.async_state_changed()
        return self.outputs[-1]

    async def test_one_read_read_permission_no_command_and_renewals_do_not_query(self):
        self.allowed = False
        grant = await self.open()
        self.assertEqual(grant["panel_state"]["status"], "loading")
        self.assertEqual(len(self.jobs), 1)
        result = await self.finish()
        self.assertEqual(result["panel_state"]["status"], "ready")
        generation = result["state_generation"]
        self.state.state = "17.2"
        await self.owner.async_state_changed()
        self.assertEqual(self.outputs[-1]["state_generation"], generation)
        self.state.state = "unavailable"
        await self.owner.async_state_changed()
        self.assertEqual(self.outputs[-1]["panel_state"]["status"], "ready")
        self.assertEqual(self.outputs[-1]["panel_state"]["current_status"], "unavailable")
        self.assertGreater(self.outputs[-1]["state_generation"], generation)
        self.assertEqual(len(self.jobs), 1)
        self.assertEqual(self.hass.services.calls, [])

    async def test_denied_open_and_permission_lost_after_read_do_not_publish(self):
        self.read_allowed = False
        with self.assertRaises(shared.codec.ProtocolError): await self.open()
        self.assertEqual(self.jobs, [])
        self.read_allowed = True
        await self.open(2)
        self.read_allowed = False
        await self.finish()
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.outputs[-1]["kind"], "close")
        self.assertFalse(any(x.get("panel_state", {}).get("status") == "ready" for x in self.outputs))

    async def test_close_reopen_busy_until_original_future_completion_no_retry(self):
        await self.open()
        future = self.jobs[0][0]
        await self.owner.async_close("navigation")
        self.assertFalse(future.cancelled())
        await self.open(2)
        await self.owner.async_state_changed()
        self.assertEqual(self.outputs[-1]["panel_state"]["reason"], "busy")
        await self.finish()
        self.assertEqual(self.outputs[-1]["panel_state"]["reason"], "busy")
        self.assertIsNone(self.owner._statistics_job)
        self.assertEqual(len(self.jobs), 1)
        await self.owner.async_close("navigation")
        await self.open(3)
        self.assertEqual(len(self.jobs), 2)

    async def test_timeout_leaves_worker_occupied_and_discards_late_data(self):
        await self.open()
        current = self.owner._selection.domain_state
        current.started -= 11
        await self.owner.async_state_changed()
        self.assertEqual(self.outputs[-1]["panel_state"]["reason"], "read_timeout")
        self.assertIs(self.owner._statistics_job, self.jobs[0][0])
        self.assertFalse(self.jobs[0][0].cancelled())
        await self.finish()
        self.assertEqual(self.outputs[-1]["panel_state"]["reason"], "read_timeout")
        self.assertEqual(self.outputs[-1]["panel_state"]["packed_q"], "")

    async def test_unit_aba_source_replacement_and_registry_changes_retire(self):
        await self.open()
        state_b = base.State(self.state.entity_id, "15", self.state.attributes | {"unit_of_measurement": "°F"})
        close = self.owner.observe_state_event(NS(data={"entity_id": self.state.entity_id, "new_state": state_b}))
        self.assertEqual(close["reason"], "capabilities_changed")
        self.assertIsNone(self.owner._selection)
        await self.finish()
        await self.open(2)
        self.sources[self.state.entity_id] = Sensor()
        await self.owner.async_state_changed()
        self.assertIsNone(self.owner._selection)
        self.jobs[-1][0].set_result(dataset()); await asyncio.sleep(0)
        await self.open(3)
        self.assertIsNone(self.owner.observe_robot_registry_event(NS(data={"entity_id": self.state.entity_id, "action": "update", "changes": {"name": "Renamed"}})))
        close = self.owner.observe_robot_registry_event(NS(data={"entity_id": self.state.entity_id, "action": "update", "changes": {"disabled_by": None}}))
        self.assertEqual(close["reason"], "capabilities_changed")

    async def test_timezone_aba_and_generation_exhaustion_retire_without_write(self):
        await self.open()
        close = self.owner.observe_statistics_zone_event(NS(data={"time_zone": "UTC"}))
        self.assertEqual(close["reason"], "capabilities_changed")
        await self.finish()
        await self.open(2)
        await self.finish()
        self.owner._selection.domain_state.generation = 2147483647
        self.state.state = "unknown"
        await self.owner.async_state_changed()
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.outputs[-1]["reason"], "expired")

    async def test_recorder_missing_and_read_exception_are_explicit_no_private_error(self):
        self.recorder_patch.stop()
        self.recorder_patch = patch.object(policy, "ready_recorder", side_effect=model.StatisticsError("recorder_missing"))
        self.recorder_patch.start()
        await self.open()
        await self.owner.async_state_changed()
        self.assertEqual(self.outputs[-1]["panel_state"]["reason"], "recorder_missing")
        self.assertEqual(self.jobs, [])

    async def test_cancel_refresh_and_unload_keep_real_executor_job_owned(self):
        # A cancelled asyncio waiter cannot stop an already-running DB thread.
        started, release = threading.Event(), threading.Event()
        pool = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_running_loop()
        actual = []
        def worker():
            started.set()
            if not release.wait(3):
                raise AssertionError("test did not release worker")
            return dataset()
        def submit(*_):
            future = loop.run_in_executor(pool, worker)
            actual.append(future)
            return future
        self.recorder.async_add_executor_job = submit
        try:
            await self.open()
            for _ in range(100):
                if started.is_set(): break
                await asyncio.sleep(.005)
            self.assertTrue(started.is_set())
            original = actual[0]
            self.auth_gate = asyncio.Event()
            self.auth_entered.clear()
            refresh = asyncio.create_task(self.owner.async_state_changed())
            await self.auth_entered.wait()
            refresh.cancel()
            await asyncio.gather(refresh, return_exceptions=True)
            self.assertIs(self.owner._statistics_job, original)
            self.assertFalse(original.done())
            self.assertFalse(original.cancelled())
            self.auth_gate.set()
            await self.owner.async_unload()
            count = len(self.outputs)
            self.assertIs(self.owner._statistics_job, original)
            self.assertFalse(original.done())
            release.set()
            await asyncio.wait_for(asyncio.shield(original), 2)
            await asyncio.sleep(0)
            self.assertIsNone(self.owner._statistics_job)
            self.assertEqual(len(self.outputs), count)
            self.assertIsNone(self.owner._selection)
            self.assertEqual(self.hass.services.calls, [])
        finally:
            release.set()
            pool.shutdown(wait=True)

    async def test_unload_late_executor_exception_retrieved_without_refresh(self):
        changed = []
        self.owner._statistics_changed = lambda: changed.append(True)
        await self.open()
        future = self.jobs[0][0]
        await self.owner.async_unload()
        count = len(self.outputs)
        self.assertIs(self.owner._statistics_job, future)
        future.set_exception(RuntimeError("private worker error"))
        await asyncio.sleep(0)
        self.assertIsNone(self.owner._statistics_job)
        self.assertEqual(changed, [])
        self.assertEqual(len(self.outputs), count)

    async def test_finished_result_after_rebind_cannot_target_new_selection(self):
        await self.open()
        old = self.jobs[0][0]
        self.owner.revoke_now("connection_lost", disconnect=True)
        self.bind()
        self.owner.accept_statistics_features(self.owner.channel)
        await self.open(2)
        await self.owner.async_state_changed()
        identity = dict(self.owner._selection.identity)
        self.assertEqual(self.outputs[-1]["panel_state"]["reason"], "busy")
        old.set_result(dataset())
        await asyncio.sleep(0)
        await self.owner.async_state_changed()
        self.assertEqual(self.owner._selection.identity, identity)
        self.assertEqual(self.outputs[-1]["panel_state"]["reason"], "busy")
        self.assertEqual(len(self.jobs), 1)

    async def test_authorization_await_unit_aba_retires_open_before_submission(self):
        self.auth_gate = asyncio.Event()
        opening = asyncio.create_task(self.open())
        await self.auth_entered.wait()
        self.assertIsNotNone(self.owner._opening_panel)
        state_b = base.State(self.state.entity_id, "15", self.state.attributes | {"unit_of_measurement": "°F"})
        self.owner.observe_state_event(NS(data={"entity_id": self.state.entity_id, "new_state": state_b}))
        # Current HA state remains A. Observing B synchronously must still retire.
        self.owner.observe_state_event(NS(data={"entity_id": self.state.entity_id, "new_state": self.state}))
        self.auth_gate.set()
        await asyncio.gather(opening, return_exceptions=True)
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.jobs, [])
        self.assertFalse(any(x["kind"] == "grant" for x in self.outputs))

    async def test_authorization_await_source_replacement_retires_open(self):
        self.auth_gate = asyncio.Event()
        opening = asyncio.create_task(self.open())
        await self.auth_entered.wait()
        self.sources[self.state.entity_id] = Sensor()
        self.auth_gate.set()
        await asyncio.gather(opening, return_exceptions=True)
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.jobs, [])
        self.assertFalse(any(x["kind"] == "grant" for x in self.outputs))

    async def test_grant_send_await_rechecks_permission_before_database(self):
        original_send = self.owner._send
        async def send(value):
            result = await original_send(value)
            if value["kind"] == "grant":
                self.read_allowed = False
            return result
        self.owner._send = send
        await self.open()
        self.assertEqual(self.jobs, [])
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.outputs[-1]["kind"], "close")

    async def test_result_authorization_await_source_change_never_publishes(self):
        await self.open()
        self.jobs[0][0].set_result(dataset())
        await asyncio.sleep(0)
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        refresh = asyncio.create_task(self.owner.async_state_changed())
        await self.auth_entered.wait()
        self.sources[self.state.entity_id] = Sensor()
        self.auth_gate.set()
        await refresh
        self.assertIsNone(self.owner._selection)
        self.assertFalse(any(x.get("panel_state", {}).get("status") == "ready" for x in self.outputs))

    async def test_qualification_and_zone_events_during_open_are_synchronous_fences(self):
        for seq, event in enumerate(("state_class", "device_class", "registry", "zone"), 1):
            with self.subTest(event=event):
                self.auth_gate = asyncio.Event()
                self.auth_entered.clear()
                opening = asyncio.create_task(self.open(seq))
                await self.auth_entered.wait()
                if event == "zone":
                    self.owner.observe_statistics_zone_event(NS(data={"time_zone": "UTC"}))
                elif event == "registry":
                    self.owner.observe_robot_registry_event(NS(data={"entity_id": self.state.entity_id,
                        "action": "update", "changes": {"unique_id": "replacement"}}))
                else:
                    state_b = base.State(self.state.entity_id, "15", self.state.attributes | {event: "different"})
                    self.owner.observe_state_event(NS(data={"entity_id": self.state.entity_id, "new_state": state_b}))
                self.auth_gate.set()
                await asyncio.gather(opening, return_exceptions=True)
                self.assertIsNone(self.owner._selection)
                self.assertEqual(self.jobs, [])
        self.assertFalse(any(x["kind"] == "grant" for x in self.outputs))

    async def test_recorder_not_ready_failed_cancelled_or_stopping_never_submits(self):
        instance = NS(is_running=True)
        base.module("homeassistant.helpers.recorder", DATA_INSTANCE="recorder",
                    get_instance=lambda _hass: instance)
        with self.assertRaisesRegex(model.StatisticsError, "recorder_missing"):
            reader.ready_recorder(self.hass)
        self.hass.data["recorder"] = instance
        for state in ("pending", "cancelled", "exception", "false", "stopping", "ready"):
            with self.subTest(state=state):
                future = asyncio.get_running_loop().create_future()
                instance.async_db_ready = future
                instance.is_running = state != "stopping"
                if state == "cancelled": future.cancel()
                elif state == "exception": future.set_exception(RuntimeError("private"))
                elif state != "pending": future.set_result(state != "false")
                if state == "ready": self.assertIs(reader.ready_recorder(self.hass), instance)
                else:
                    with self.assertRaisesRegex(model.StatisticsError, "recorder_unavailable"):
                        reader.ready_recorder(self.hass)

    async def test_current_measurement_change_during_worker_keeps_historical_generation(self):
        await self.open()
        generation = self.owner._selection.domain_state.generation
        self.state.state = "99"
        await self.owner.async_state_changed()
        self.assertEqual(self.owner._selection.domain_state.generation, generation)
        result = await self.finish()
        self.assertEqual(result["panel_state"]["axis_min_text"], "-2.0")
        self.assertEqual(result["panel_state"]["axis_max_text"], "3.0")
        self.assertEqual(len(self.jobs), 1)


class StatisticsTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_optional_features_fence_client_runtime_channel_and_epoch(self):
        api = shared.integration.transport
        modes = ("valid", "missing", "no_info", "bad_query", "rejected", "wrong_channel",
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
                                                      control_kinds=extra.old_panel.KINDS)
                    elif service.name in ("entity_panel_extra_query", "entity_panel_extra_bind"):
                        value = json.loads(data["payload"])
                        value["profiles"] = [] if mode == "no_info" else [{"name": "info", "version": 1}]
                        if service.name.endswith("bind"): value["accepted"] = True
                    elif service.name == features.QUERY:
                        value = {"v": 1, "type": features.TYPE, "statistics_version": 2 if mode == "bad_query" else 1}
                        if mode == "query_client": bridge.runtime.client = NS(execute_service=execute)
                    elif service.name == features.BIND:
                        value = json.loads(data["payload"]) | {"accepted": True}
                        if mode == "rejected": value.update(accepted=False, statistics_version=0, channel="")
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
                    self.assertEqual(transport.info_statistics_version, int(mode == "valid"))
                    if mode in ("missing", "bad_query", "query_client", "no_info"):
                        self.assertNotIn(features.BIND, calls)
                    transport.invalidate_connection()
                    self.assertEqual(transport.info_statistics_version, 0)
                finally:
                    await transport.async_shutdown()


class CoreSchemaSQLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import sqlalchemy as sa
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
        class Base(DeclarativeBase): pass
        class Mean(IntEnum): NONE = 0; ARITHMETIC = 1; CIRCULAR = 2
        namespace = dict(__name__="statistics_schema_fixture", Base=Base, Mapped=Mapped,
            mapped_column=mapped_column, ID_TYPE=sa.Integer, TIMESTAMP_TYPE=sa.Double,
            DOUBLE_TYPE=sa.Double, UNUSED_LEGACY_DATETIME_COLUMN=sa.DateTime,
            ForeignKey=sa.ForeignKey, Identity=sa.Identity, Index=sa.Index,
            Integer=sa.Integer, String=sa.String, Boolean=sa.Boolean, SmallInteger=sa.SmallInteger,
            _DEFAULT_TABLE_ARGS={}, TABLE_STATISTICS="statistics", TABLE_STATISTICS_META="statistics_meta",
            StatisticMeanType=Mean, timedelta=timedelta, datetime=datetime, time=time)
        # SQLAlchemy resolves postponed annotations through the module namespace.
        module = base.module("statistics_schema_fixture", **namespace)
        fixture = Path(__file__).parent / "fixtures/statistics/core202611_schema.py"
        exec(compile(fixture.read_bytes(), str(fixture), "exec"), module.__dict__)
        cls.sa, cls.Session, cls.Base, cls.M, cls.S = sa, Session, Base, module.StatisticsMeta, module.Statistics
        base.module("homeassistant.components.recorder")
        base.module("homeassistant.components.recorder.db_schema", Statistics=cls.S, StatisticsMeta=cls.M)

    def setUp(self):
        self.engine = self.sa.create_engine("sqlite://")
        self.Base.metadata.create_all(self.engine)

    def tearDown(self): self.engine.dispose()

    def test_real_core_tables_single_select_limit_metadata_only_and_24_hours(self):
        with self.Session(self.engine) as session:
            query = reader.statement("sensor.test", (END-24)*3600, END*3600)
            self.assertEqual(session.execute(query).all(), [])
            session.add(self.M(id=7, statistic_id="sensor.test", source="recorder", mean_type=1, unit_of_measurement="°C", unit_class="temperature"))
            session.commit()
            result = session.execute(query).all()
            self.assertEqual(len(result), 1)
            self.assertEqual(tuple(result[0][5:]), (None, None, None, None))
            for i in range(-2, 26):
                session.add(self.S(metadata_id=7, start_ts=(END-24+i)*3600, min=i, mean=i+.5, max=i+1))
            session.commit()
        statements = []
        self.sa.event.listen(self.engine, "before_cursor_execute", lambda _c, _u, sql, *_: statements.append(sql))
        @contextmanager
        def scope(*, session, read_only):
            self.assertTrue(read_only)
            try: yield session
            finally: session.close()
        base.module("homeassistant.helpers.recorder", session_scope=scope)
        # Exercise the actual adapter, including its default converter selection.
        base.module("homeassistant.components.recorder.statistics", _get_unit_converter_func=lambda *_: None)
        value = reader.read_dataset(NS(get_session=lambda: self.Session(self.engine)), "sensor.test", END, "°C")
        self.assertEqual(value.fields["valid_mask"], 0xFFFFFF)
        self.assertEqual(len(statements), 1)
        self.assertTrue(statements[0].lstrip().startswith("SELECT"))
        self.assertIn("LEFT OUTER JOIN", statements[0])
        self.assertIn("LIMIT", statements[0])
        self.assertEqual(value.fields["axis_min_text"], "0.0")
        self.assertEqual(value.fields["axis_max_text"], "24.0")


if __name__ == "__main__":
    unittest.main()
