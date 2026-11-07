"""Text:1 exact public values and existing owner fences; no live HA calls."""

import asyncio
from copy import deepcopy
import importlib
import json
from pathlib import Path
import unittest

import test_ha_layout as base
import test_entity_control as shared
import test_extra_panels as extra_tests

domain = importlib.import_module("_atmosfera_test.text_panel_domain")
codec = shared.codec


def environment(value="Zażółć gęślą jaźń", *, service=True, **attrs):
    state = base.State("input_text.test", value, {"mode": "text", "min": 0, "max": 255, "editable": False, **attrs})
    hass, _ = base.environment(states=[state], services=["input_text.set_value"] if service else [])
    return hass, state


class TextDomainTests(unittest.TestCase):
    def test_exact_public_empty_spaces_polish_limits_and_service(self):
        for value in ("", "  ", "Zażółć gęślą jaźń", "Ł" * 255, '\\"' * 127 + '"'):
            hass, state = environment(value)
            caps = domain.TextDomain.from_ha(hass, state)
            observation = domain.TextObservation.from_ha(hass, state, caps)
            self.assertEqual(observation.value, value)
            self.assertTrue(observation.available)
            self.assertEqual(caps.service_action(state.entity_id, "set_value", value), ("input_text", "set_value", {"value": value}))
            self.assertEqual(domain.TextObservation.from_descriptor(caps, observation.descriptor()), observation)

    def test_privacy_is_checked_before_reading_value_and_pattern_is_not_exposed(self):
        class Guarded:
            entity_id = "input_text.secret"
            @property
            def state(self):
                raise AssertionError("private raw value was inspected")
        hass, _ = environment()
        for attrs, reason in (({"mode": "password"}, "password"), ({"mode": None}, "mode"),
                              ({"pattern": ""}, "pattern"), ({"pattern": "private regex"}, "pattern"), ({"max": True}, "bounds")):
            state = Guarded()
            state.attributes = {"mode": "text", "min": 0, "max": 255, **attrs}
            meta = domain.text_metadata(hass, state)["text_panel"]
            self.assertEqual(meta["state"], {"source": "unsupported", "value": None, "reason": reason})
            self.assertFalse(meta["caps"]["can_set"])
            self.assertNotIn("private regex", json.dumps(meta))

    def test_exact_typed_bounds_repertoire_reserved_and_no_coercion(self):
        for attrs in ({"min": True}, {"max": 255.0}, {"min": "0"}, {"max": 0}, {"min": -1}, {"max": 256}, {"min": 3, "max": 2}):
            hass, state = environment(**attrs)
            meta = domain.text_metadata(hass, state)["text_panel"]
            self.assertEqual(meta["caps"], {"min": None, "max": None, "can_set": False})
            self.assertEqual(meta["state"]["reason"], "bounds")
        for value, reason in (("x"*256, "length"), ("\ud800", "encoding"), (None, "encoding"), (1, "encoding"),
                              ("a\n", "characters"), ("\t", "characters"), ("🙂", "characters"), ("a\u0301", "characters"), ("\x7f", "characters")):
            hass, state = environment(value)
            meta = domain.text_metadata(hass, state)["text_panel"]
            self.assertEqual(meta["state"], {"source": "unsupported", "value": None, "reason": reason})
            self.assertEqual(meta["eligible_actions"], 0)
            self.assertTrue(meta["caps"]["can_set"])
            self.assertFalse(domain.valid_target(value))
        for value in ("unknown", "unavailable"):
            hass, state = environment(value)
            self.assertEqual(domain.text_metadata(hass, state)["text_panel"]["state"], {"source": value, "value": None, "reason": "none"})
            self.assertFalse(domain.valid_target(value))
        self.assertFalse(domain.valid_target("", 1, 255))
        self.assertTrue(domain.valid_target(" ", 1, 1))

    def test_fingerprint_only_semantic_policy_and_readonly_known_state(self):
        hass, state = environment()
        first = domain.TextDomain.from_ha(hass, state)
        state.attributes.update(friendly_name="Other", editable=True, icon="mdi:text", pattern=None)
        self.assertEqual(first, domain.TextDomain.from_ha(hass, state))
        self.assertEqual(first.fingerprint, domain.TextDomain.from_ha(hass, state).fingerprint)
        state.attributes["pattern"] = ""
        empty = domain.TextDomain.from_ha(hass, state)
        state.attributes["pattern"] = ".*"
        self.assertNotEqual(empty, domain.TextDomain.from_ha(hass, state))
        hass, state = environment(service=False)
        meta = domain.text_metadata(hass, state)["text_panel"]
        self.assertTrue(meta["available"])
        self.assertEqual(meta["eligible_actions"], 0)
        self.assertFalse(meta["caps"]["can_set"])

    def test_explicit_layout_profile_projection_and_passive_legacy(self):
        hass, state = environment()
        card = base.card(entity=state.entity_id, action=dict(domain.ACTION))
        value = base.layout.validate_layout(base.document([card]) | {"version": 3})
        self.assertEqual(value["cards"][0]["action"], domain.ACTION)
        for profiles in ((), ("text",)):
            item = base.cards.presentation_payload(hass, [card], panel_extra_profiles=profiles, press_enabled_supported=True)["cards"][2]
            self.assertEqual(item.get("control_kind"), "panel" if profiles else None)
        self.assertEqual(base.cards.entity_actions(hass, state), [])
        self.assertIsNone(base.cards.resolve_action(hass, card))
        for change in ({"type": "sensor"}, {"action": domain.ACTION | {"extra": 1}}, {"entity_id": "text.other"}):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(base.document([card | change]) | {"version": 3})


class TextCodecTests(unittest.TestCase):
    def snapshot(self):
        hass, state = environment()
        meta = domain.text_metadata(hass, state)["text_panel"]
        return codec.envelope("grant", channel="a"*32, open_seq=1, slot=2, card_id="card-2", revision=4,
            control_kind="panel", token="b"*32, state_seq=1, ttl_ms=30000, title="Text", panel_type="text",
            panel_caps=meta["caps"], panel_state=meta["state"], available=meta["available"],
            eligible_actions=meta["eligible_actions"], state_generation=1)

    def test_actual_adapter_wire_corpus_roundtrip_and_default_off(self):
        rows = json.loads((Path(__file__).with_name("fixtures") / "text_panel/wire.json").read_text(encoding="utf8"))
        self.assertEqual(len(rows), 20)
        for row in rows:
            encoded = codec.encode(row["value"], extra_profiles=("text",))
            self.assertEqual(encoded, row["json"])
            self.assertEqual(len(encoded.encode("utf8")), row["bytes"])
            self.assertLessEqual(row["bytes"], 2048)
            self.assertEqual(codec.decode(encoded, extra_profiles=("text",)), row["value"])
            with self.assertRaises(codec.ProtocolError): codec.decode(encoded)

    def test_closed_matrix_duplicate_keys_and_typed_scalars(self):
        value = self.snapshot()
        for field, changes in (("panel_caps", ({"min": True}, {"max": "255"}, {"can_set": 1}, {"extra": 1}, {"min": None, "max": None, "can_set": False})),
                              ("panel_state", ({"source": []}, {"reason": []}, {"value": 2}, {"reason": "password"}, {"source": "unknown"}, {"value": "unknown"}, {"value": "🙂"}, {"extra": 1}))):
            for change in changes:
                with self.assertRaises(codec.ProtocolError): codec.encode(value | {field: value[field] | change}, extra_profiles=("text",))
        raw = shared.wire(value).replace('"min":0', '"min":0,"min":0')
        with self.assertRaises(codec.ProtocolError): codec.decode(raw, extra_profiles=("text",))
        command = codec.envelope("command", **{key: value[key] for key in codec.SELECTION}, text_version=1, command_seq=1,
                                 op="set_value", value="", expected_state_generation=1)
        for change in ({"text_version": True}, {"value": None}, {"value": "unknown"}, {"value": "x"*256}, {"expected_state_generation": 0}, {"extra": 1}, {"op": "append"}):
            with self.assertRaises(codec.ProtocolError): codec.encode(command | change, extra_profiles=("text",))

    def test_unsupported_reason_bounds_capability_matrix(self):
        for numeric in (False, True):
            for can_set in (False, True):
                for reason in domain.REASONS:
                    value = self.snapshot()
                    value.update(panel_caps={"min": 0 if numeric else None, "max": 255 if numeric else None, "can_set": can_set},
                        panel_state={"source": "unsupported", "value": None, "reason": reason}, available=False, eligible_actions=0)
                    valid = (reason in {"password", "mode", "pattern"} and not can_set or
                             reason == "bounds" and not numeric and not can_set or
                             reason in {"length", "encoding", "characters"} and numeric)
                    if valid:
                        self.assertEqual(codec.decode(codec.encode(value, extra_profiles=("text",)), extra_profiles=("text",)), value)
                    else:
                        with self.assertRaises(codec.ProtocolError): codec.encode(value, extra_profiles=("text",))

    def test_worst_current_repertoire_packets_and_seven_profile_reply_are_bounded(self):
        value = self.snapshot()
        value.update(open_seq=codec.MAX_SEQUENCE, slot=31, card_id="c"*64, revision=2**53-1,
                     state_seq=codec.MAX_SEQUENCE, state_generation=codec.MAX_SEQUENCE, title='"'*160,
                     panel_caps={"min": 255, "max": 255, "can_set": False}, eligible_actions=0)
        sizes = []
        for text in ('"'*255, "Ż"*255):
            value["panel_state"]["value"] = text
            for kind in ("grant", "state"):
                sizes.append(len(codec.encode(value | {"kind": kind}, extra_profiles=("text",)).encode("utf8")))
            command = codec.envelope("command", **{key:value[key] for key in codec.SELECTION}, text_version=1,
                command_seq=codec.MAX_SEQUENCE, expected_state_generation=codec.MAX_SEQUENCE, op="set_value", value=text)
            sizes.append(len(codec.encode(command, extra_profiles=("text",)).encode("utf8")))
        self.assertEqual(max(sizes), 1375)
        features = importlib.import_module("_atmosfera_test.extra_panel_features")
        response = json.loads(features.payload("a"*32, list(features.PROFILES))) | {"accepted": True}
        self.assertEqual(len(json.dumps(response, separators=(",", ":")).encode()), 323)


class TextOwnerTests(unittest.IsolatedAsyncioTestCase):
    bind = extra_tests.ExtraOwnerTests.bind
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    assert_terminal_order = shared.NumberOwnerTests.assert_terminal_order
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.configure()

    def configure(self, **kwargs):
        self.hass, self.state = environment(**kwargs)
        self.owner.hass = self.hass
        self.card.update(entity_id=self.state.entity_id, type="entity", action=dict(domain.ACTION))
        self.fail = self.retire = False
        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate: await self.service_gate.wait()
            if self.retire: self.owner.revoke_now("selection_changed")
            if self.fail: raise RuntimeError("fake provider rejection")
            if self.apply: self.change(args[2]["value"])
        self.hass.services.async_call = service

    async def open(self, seq=1):
        return await shared.NumberOwnerTests.open(self, seq, "panel")

    def command(self, seq=1, value="Nowa wartość", **updates):
        selected = self.owner._selection
        return codec.envelope("command", **selected.identity, text_version=1, command_seq=seq,
            op="set_value", expected_state_generation=selected.domain_state[2], value=value) | updates

    async def test_one_exact_service_context_state_then_terminal_duplicate_is_idempotent(self):
        await self.open()
        for seq, value in enumerate((" ", "", "Ż"*255), 1):
            command = self.command(seq, value)
            await self.send(command)
            args, kwargs = self.hass.services.calls[-1]
            self.assertEqual(args, ("input_text", "set_value", {"entity_id": self.state.entity_id, "value": value}))
            self.assertIs(kwargs["context"], self.user)
            self.assertTrue(kwargs["blocking"])
            self.assertEqual(self.results()[-1]["status"], "state_matches")
            self.assert_terminal_order()
            await self.send(command)
            self.assertEqual(len(self.hass.services.calls), seq)

    async def test_already_matched_zero_calls_and_callback_without_observation_is_not_success(self):
        await self.open()
        await self.send(self.command(value=self.state.state))
        self.assertEqual(self.results()[-1]["status"], "already_matched")
        self.assertEqual(self.hass.services.calls, [])
        self.apply = False
        await self.send(self.command(seq=2))
        self.assertEqual(self.results()[-1]["status"], "not_confirmed")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_held_authorization_source_ABA_rejected_metadata_only_retains_generation(self):
        await self.open()
        for seq, aba in ((1, False), (2, True)):
            self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
            await self.owner.async_handle(shared.wire(self.command(seq, "new" + str(seq))), self.user)
            task = self.owner._selection.command.task
            await asyncio.wait_for(self.auth_entered.wait(), .2)
            before = self.owner._selection.domain_state[2]
            original = self.state.state
            if aba:
                self.change("B")
                self.change(original)
                self.assertEqual(self.owner._selection.domain_state[2], before+2)
            else:
                self.change(original, friendly_name="Other", editable=True, icon="mdi:text")
                self.assertEqual(self.owner._selection.domain_state[2], before)
            self.auth_gate.set()
            await asyncio.wait_for(task, .4)
            self.assertEqual(self.results()[-1]["status"], "rejected" if aba else "state_matches")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_privacy_pattern_bounds_service_changes_retire_before_state_payload(self):
        for seq, attrs in enumerate(({"mode": "password"}, {"pattern": ""}, {"max": 254}, {}), 1):
            self.configure()
            await self.open(seq)
            start = len(self.outputs)
            if not attrs: self.hass.services.names.clear()
            self.change("SECRET_MUST_NOT_BE_EMITTED", **attrs)
            self.assertIsNone(self.owner._selection)
            self.assertNotIn("SECRET_MUST_NOT_BE_EMITTED", json.dumps(self.outputs[start:]))
            self.assertEqual(self.hass.services.calls, [])

    async def test_readonly_privacy_unknown_and_permission_negotiation_fail_closed(self):
        self.owner._extra_profiles = ()
        with self.assertRaises(codec.ProtocolError): await self.open()
        self.bind()
        for seq, kwargs in enumerate(({"service": False}, {"mode": "password"}, {"pattern": ".*"}, {"value": "unknown"}, {"value": "bad\n"}), 1):
            await self.owner.async_close()
            self.configure(**kwargs)
            grant = await self.open(seq)
            self.assertEqual(grant["eligible_actions"], 0)
            await self.send(self.command())
            self.assertEqual(self.hass.services.calls, [])
        await self.owner.async_close()
        self.configure()
        self.allowed = False
        with self.assertRaises(codec.ProtocolError): await self.open(6)

    async def test_provider_failure_and_pending_shared_service_fence_no_retry(self):
        await self.open()
        self.fail = True
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["status"], "rejected")
        self.assertEqual(len(self.hass.services.calls), 1)
        self.fail = False
        self.owner.service_timeout = 1
        self.service_gate = asyncio.Event()
        self.service_entered.clear()
        await self.owner.async_handle(shared.wire(self.command(seq=2)), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        job = self.owner._service_task
        await self.owner.async_close()
        await self.open(2)
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["reason"], "busy")
        self.assertEqual(len(self.hass.services.calls), 2)
        self.service_gate.set()
        await asyncio.wait_for(job, .2)
        self.assertFalse(any(row["status"] == "state_matches" for row in self.results()))


if __name__ == "__main__":
    unittest.main()
