"""Datetime host contracts; fake HA services never operate real devices."""

import asyncio
from copy import deepcopy
from datetime import datetime, timezone
import importlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

import test_ha_layout as base
import test_entity_control as shared
import test_extra_panels as extra_tests

domain = importlib.import_module("_atmosfera_test.datetime_panel_domain")
codec = shared.codec
FIELDS = domain.FIELDS


def environment(mode="datetime", *, year=2026, service=True, raw=None):
    full = dict(zip(FIELDS, (year, 11, 5, 12, 34, 56)))
    values = {key: full[key] if present else None for key, present in zip(FIELDS, domain.MODES[mode])}
    text = f"{year:04d}-11-05" if mode != "time" else ""
    if mode != "date": text += (" " if text else "") + "12:34:56"
    attrs = {key: value for key, value in values.items() if value is not None}
    attrs.update(has_date=mode != "time", has_time=mode != "date", editable=False)
    state = base.State("input_datetime.test", text if raw is None else raw, attrs)
    state.last_updated = datetime(2026, 11, 5, 10, 0, 0, 123456, tzinfo=timezone.utc)
    hass, _ = base.environment(states=[state], services=["input_datetime.set_datetime"] if service else [])
    hass.config.time_zone = "Europe/Warsaw"
    return hass, state, values


class DatetimeDomainTests(unittest.TestCase):
    def test_three_modes_padding_seconds_and_exact_one_service_payload(self):
        for mode in domain.MODES:
            for year in (1, 99, 999, 1000, 2026, 9999):
                hass, state, target = environment(mode, year=year)
                caps = domain.DatetimeDomain.from_ha(hass, state)
                observed = domain.DatetimeObservation.from_ha(hass, state, caps)
                self.assertTrue(observed.available)
                self.assertEqual(observed.target(), target)
                service, operation, data = caps.service_action(state.entity_id, "set_datetime", target)
                self.assertEqual((service, operation), ("input_datetime", "set_datetime"))
                self.assertEqual(set(data), ({"date", "time"} if mode == "datetime" else {mode}))
                if mode != "time":
                    self.assertEqual(data["date"], f"{year:04d}-11-05")
                    state.state = state.state.lstrip("0")
                    self.assertTrue(domain.DatetimeObservation.from_ha(hass, state, caps).available)
                if mode != "date": self.assertEqual(data["time"], "12:34:56")

    def test_strict_source_attrs_parity_unknown_and_current_observation_timestamp(self):
        hass, state, target = environment()
        caps = domain.DatetimeDomain.from_ha(hass, state)
        for raw, source in (("unknown", "unknown"), ("unavailable", "unavailable"), ("2026-02-31 12:34:56", "unknown"),
                            ("2026-11-05 12:34:56\n", "unknown"), ("2026-11-05T12:34:56", "unknown")):
            state.state = raw
            value = domain.DatetimeObservation.from_ha(hass, state, caps)
            self.assertEqual((value.source, value.values), (source, (None,) * 6))
            self.assertEqual(value.updated_text, "2026-11-05T11:00:00+01:00")
        state.state = "2026-11-05 12:34:56"
        for bad in ("56", 56.0, True, 55, None):
            state.attributes["second"] = bad
            self.assertFalse(domain.DatetimeObservation.from_ha(hass, state, caps).available)
        state.attributes["second"] = 56
        self.assertTrue(domain.DatetimeObservation.from_ha(hass, state, caps).available)

    def test_gregorian_and_strict_nullable_integer_targets(self):
        _, _, good = environment()
        for change in ({"year": 0}, {"year": 10000}, {"year": True}, {"month": 2, "day": 30},
                       {"year": 1900, "month": 2, "day": 29}, {"second": 60}, {"hour": 24},
                       {"minute": "1"}, {"year": 2026.0}, {"second": None}, {"extra": 1}):
            self.assertFalse(domain.valid_tuple(good | change, "datetime"), change)
        self.assertTrue(domain.valid_tuple(good | {"year": 2000, "month": 2, "day": 29}, "datetime"))
        self.assertFalse(domain.valid_tuple(dict.fromkeys(FIELDS)))

    def test_metadata_mode_service_semantics_zone_is_only_display_context(self):
        hass, state, _ = environment()
        before = domain.datetime_metadata(hass, state)["datetime_panel"]
        hass.config.time_zone = "UTC"
        after = domain.datetime_metadata(hass, state)["datetime_panel"]
        self.assertEqual(before["fingerprint"], after["fingerprint"])
        self.assertNotEqual(before["caps"]["zone_text"], after["caps"]["zone_text"])
        self.assertEqual(domain.DatetimeDomain.from_descriptor(before["caps"]), domain.DatetimeDomain.from_descriptor(after["caps"]))
        hass.services.names.clear()
        readonly = domain.datetime_metadata(hass, state)["datetime_panel"]
        self.assertTrue(readonly["available"])
        self.assertFalse(readonly["caps"]["can_set"])
        self.assertEqual(readonly["eligible_actions"], 0)
        self.assertNotEqual(before["fingerprint"], readonly["fingerprint"])
        for flags in ((False, False), (1, True), (True, None)):
            state.attributes.update(zip(("has_date", "has_time"), flags))
            self.assertEqual(domain.datetime_metadata(hass, state), {})

    def test_explicit_layout_profile_projection_and_legacy_passive_path_preserved(self):
        hass, state, _ = environment()
        card = base.card(entity=state.entity_id, action=dict(domain.ACTION))
        value = base.layout.validate_layout(base.document([card]) | {"version": 3})
        self.assertEqual(value["cards"][0]["action"], domain.ACTION)
        for profiles in ((), ("datetime",)):
            item = base.cards.presentation_payload(hass, [card], panel_extra_profiles=profiles, press_enabled_supported=True)["cards"][2]
            self.assertEqual(item.get("control_kind"), "panel" if profiles else None)
        self.assertEqual(base.cards.entity_actions(hass, state), [])
        self.assertIsNone(base.cards.resolve_action(hass, card))
        for change in ({"type": "sensor"}, {"action": {"kind": "default"}}, {"action": domain.ACTION | {"extra": 1}}):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(base.document([card | change]) | {"version": 3})


class DatetimeCodecTests(unittest.TestCase):
    def test_datetime_profile_independent_and_older_peer_subset_preserves_existing_profiles(self):
        features = importlib.import_module("_atmosfera_test.extra_panel_features")
        channel = "a" * 32
        offered = list(features.PROFILES)
        self.assertEqual([row["name"] for row in offered], ["action", "datetime", "info", "info_context", "lock", "media", "text"])
        self.assertTrue(features.valid_profiles([{"name": "datetime", "version": 1}]))
        for profiles in ([{"name": "datetime", "version": 1}], [row for row in offered if row["name"] != "datetime"]):
            response = {"v": 1, "type": "entity_panel_extra_v1", "channel": channel, "profiles": profiles}
            parsed = features.decode_response(NS(success=True, response_data=json.dumps(response).encode()), channel=channel, offered=offered)
            self.assertEqual(parsed, response)

    def test_frozen_design_examples_cross_ha_encoder_and_default_off(self):
        fixture = Path(__file__).with_name("fixtures") / "datetime_panel" / "wire.json"
        rows = json.loads(fixture.read_text(encoding="utf8"))
        self.assertEqual(len(rows), 26)
        for row in rows:
            self.assertEqual(codec.encode(row["value"], extra_profiles=("datetime",)), row["json"])
            self.assertEqual(codec.decode(row["json"], extra_profiles=("datetime",)), row["value"])
            if row["value"]["kind"] in ("grant", "state", "command"):
                with self.assertRaises(codec.ProtocolError): codec.decode(row["json"])

    def snapshot(self, mode="datetime"):
        hass, state, _ = environment(mode)
        meta = domain.datetime_metadata(hass, state)["datetime_panel"]
        return codec.envelope("grant", channel="a"*32, open_seq=1, slot=2, card_id="card-2", revision=4,
            control_kind="panel", token="b"*32, state_seq=1, ttl_ms=30000, title="Date", panel_type="datetime",
            panel_caps=meta["caps"], panel_state=meta["state"], available=meta["available"],
            eligible_actions=meta["eligible_actions"], state_generation=1)

    def test_three_modes_exact_roundtrip_default_off_and_closed_fields(self):
        for mode in domain.MODES:
            value = self.snapshot(mode)
            _, _, target = environment(mode)
            command = codec.envelope("command", **{key: value[key] for key in codec.SELECTION}, datetime_version=1,
                command_seq=1, expected_state_generation=1, op="set_datetime", target=target)
            for message in (value, value | {"kind": "state"}, command):
                self.assertEqual(codec.decode(codec.encode(message, extra_profiles=("datetime",)), extra_profiles=("datetime",)), message)
                with self.assertRaises(codec.ProtocolError): codec.encode(message)
                with self.assertRaises(codec.ProtocolError): codec.encode(message | {"unknown": 1}, extra_profiles=("datetime",))

    def test_malformed_scalars_null_masks_and_duplicate_nested_keys_rejected(self):
        value = self.snapshot()
        for field, changes in (("panel_caps", ({"mode": []}, {"can_set": 1}, {"mode": "time"}, {"extra": 1})),
                ("panel_state", ({"year": 1.0}, {"year": True}, {"day": None}, {"source": "unknown"},
                    {"updated_text": "2026-11-05T12:00:00+01:60"}, {"updated_text": "2026-11-05T12:00:00.123+01:00"}))):
            for change in changes:
                with self.assertRaises(codec.ProtocolError): codec.encode(value | {field: value[field] | change}, extra_profiles=("datetime",))
        raw = shared.wire(value).replace('"year":2026', '"year":2026,"year":2026')
        with self.assertRaises(codec.ProtocolError): codec.decode(raw, extra_profiles=("datetime",))


class DatetimeOwnerTests(unittest.IsolatedAsyncioTestCase):
    bind = extra_tests.ExtraOwnerTests.bind
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    assert_terminal_order = shared.NumberOwnerTests.assert_terminal_order
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.configure()

    def configure(self, mode="datetime", **kwargs):
        self.hass, self.state, self.initial = environment(mode, **kwargs)
        self.owner.hass = self.hass
        self.card.update(entity_id=self.state.entity_id, type="entity", action=dict(domain.ACTION))
        self.fail = self.retire = False
        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate: await self.service_gate.wait()
            if self.retire: self.owner.revoke_now("selection_changed")
            if self.fail: raise RuntimeError("fake service failed")
            if self.apply:
                data = args[2]
                raw = " ".join(data[key] for key in ("date", "time") if key in data)
                groups = [int(item) for item in domain.RAW[mode].fullmatch(raw).groups()]
                attrs = dict(zip((key for key, present in zip(FIELDS, domain.MODES[mode]) if present), groups))
                self.change(raw, **attrs)
        self.hass.services.async_call = service

    async def open(self, seq=1):
        return await shared.NumberOwnerTests.open(self, seq, "panel")

    def command(self, seq=1, target=None, **updates):
        selected = self.owner._selection
        target = target if target is not None else self.initial | {"second": 57}
        return codec.envelope("command", **selected.identity, datetime_version=1, command_seq=seq,
            op="set_datetime", expected_state_generation=selected.domain_state[2], target=target) | updates

    async def test_one_absolute_service_observed_state_before_result_all_modes(self):
        for index, mode in enumerate(domain.MODES):
            await self.owner.async_close()
            self.configure(mode, year=1)
            await self.open(index+1)
            target = self.initial | ({"day": 6} if mode == "date" else {"second": 57})
            command = self.command(target=target)
            await self.send(command)
            args, kwargs = self.hass.services.calls[0]
            expected = domain.DatetimeDomain.from_ha(self.hass, self.state).service_action(self.state.entity_id, "set_datetime", target)
            self.assertEqual(args, (expected[0], expected[1], {"entity_id": self.state.entity_id, **expected[2]}))
            self.assertIs(kwargs["context"], self.user)
            self.assertTrue(kwargs["blocking"])
            self.assertEqual(self.results()[-1]["status"], "state_matches")
            self.assert_terminal_order()
            await self.send(command)
            self.assertEqual(len(self.hass.services.calls), 1)

    async def test_already_matched_never_dispatches_service_callback_is_not_confirmation(self):
        await self.open()
        await self.send(self.command(target=self.initial))
        self.assertEqual(self.results()[-1]["status"], "already_matched")
        self.assertEqual(self.hass.services.calls, [])
        self.apply = False
        await self.send(self.command(seq=2))
        self.assertEqual(self.results()[-1]["status"], "not_confirmed")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_semantic_ABA_before_coalescing_rejects_but_metadata_preserves_hold(self):
        await self.open()
        for seq, aba in ((1, False), (2, True)):
            self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
            await self.owner.async_handle(shared.wire(self.command(seq, target=self.initial | {"second": 58})), self.user)
            task = self.owner._selection.command.task
            await asyncio.wait_for(self.auth_entered.wait(), .2)
            before = self.owner._selection.domain_state[2]
            if aba:
                original = self.state.state
                self.change("unknown")
                self.change(original)
                self.assertEqual(self.owner._selection.domain_state[2], before+2)
            else:
                self.hass.config.time_zone = "UTC"
                self.state.last_updated = datetime(2026, 11, 5, 11, tzinfo=timezone.utc)
                self.change(self.state.state, friendly_name="Changed")
                self.assertEqual(self.owner._selection.domain_state[2], before)
            self.auth_gate.set()
            await asyncio.wait_for(task, .4)
            self.assertEqual(self.results()[-1]["status"], "rejected" if aba else "state_matches")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_readonly_control_permission_and_negotiation_fail_closed(self):
        self.owner._extra_profiles = ()
        with self.assertRaises(codec.ProtocolError): await self.open()
        self.bind()
        self.configure(service=False)
        grant = await self.open()
        self.assertTrue(grant["available"])
        self.assertEqual(grant["eligible_actions"], 0)
        await self.send(self.command())
        self.assertEqual(self.hass.services.calls, [])
        await self.owner.async_close()
        self.configure()
        self.allowed = False
        with self.assertRaises(codec.ProtocolError): await self.open(2)
        self.assertEqual(self.hass.services.calls, [])

    async def test_mode_and_service_changes_retire_but_zone_updates_live_snapshot(self):
        await self.open()
        self.hass.config.time_zone = "UTC"
        await self.owner.async_state_changed()
        self.assertEqual(self.outputs[-1]["panel_caps"]["zone_text"], "UTC")
        self.assertEqual(self.outputs[-1]["state_generation"], 1)
        self.hass.services.names.clear()
        self.change(self.state.state)
        self.assertIsNone(self.owner._selection)
        self.configure()
        await self.open(2)
        self.change(self.state.state, has_time=False)
        self.assertIsNone(self.owner._selection)

    async def test_tuple_ABA_synchronous_events_prevent_coalesced_authorization_dispatch(self):
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        task = self.owner._selection.command.task
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        # No async refresh between these state events: only the final A could be
        # emitted, but the held Save must still observe both semantic changes.
        self.change("2026-11-05 12:34:55", second=55)
        self.change("2026-11-05 12:34:56", second=56)
        self.assertEqual(self.owner._selection.domain_state[2], 3)
        self.auth_gate.set()
        await asyncio.wait_for(task, .4)
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["reason"], "stale_state")

    async def test_pending_service_retains_shared_fence_and_late_state_cannot_confirm_new_owner(self):
        await self.open()
        self.owner.service_timeout = 1
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        job = self.owner._service_task
        await self.owner.async_close()
        await self.open(2)
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["reason"], "busy")
        self.assertEqual(len(self.hass.services.calls), 1)
        self.service_gate.set()
        await asyncio.wait_for(job, .2)
        self.assertFalse(any(row["status"] == "state_matches" for row in self.results()))

    async def test_permission_loss_or_provider_error_never_reports_success(self):
        await self.open()
        self.allowed = False
        await self.send(self.command())
        self.assertEqual(self.hass.services.calls, [])
        self.allowed = True
        await self.owner.async_close()
        self.configure()
        await self.open(2)
        self.fail = True
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["status"], "rejected")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_wrong_mode_retirement_and_late_callback_never_paint_or_repeat(self):
        await self.open()
        bad = self.initial | {"year": None, "month": None, "day": None}
        await self.send(self.command(target=bad))
        self.assertEqual(self.hass.services.calls, [])
        self.retire = True
        await self.send(self.command(seq=2))
        self.assertIsNone(self.owner._selection)
        self.assertEqual(len(self.hass.services.calls), 1)
        self.assertFalse(any(row["kind"] == "result" and row.get("status") == "state_matches" for row in self.outputs))


if __name__ == "__main__":
    unittest.main()
