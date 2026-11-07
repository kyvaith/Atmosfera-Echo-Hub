"""Choice extension retains old generic capabilities and strict 2048-byte wire."""

import json
import unittest

import test_entity_control as base

codec = base.codec


def identity():
    return {
        "channel": "a" * 32,
        "open_seq": 1,
        "slot": 2,
        "card_id": "card-2",
        "revision": 4,
        "control_kind": "choice",
        "token": "b" * 32,
    }


def state():
    return codec.envelope(
        "state",
        **identity(),
        state_seq=1,
        ttl_ms=30000,
        title="Wybierz tryb",
        options=["Eco", "Komfort"],
        index=0,
        available=True,
        state_generation=1,
    )


def command():
    return codec.envelope(
        "command",
        **identity(),
        command_seq=1,
        op="choose",
        target_index=1,
        expected_index=0,
        expected_state_generation=1,
    )


class ChoiceCodecTests(unittest.TestCase):
    def test_choice_envelopes_and_both_exact_capability_versions_roundtrip(self):
        opening = {key: value for key, value in identity().items() if key != "token"}
        values = [
            state(),
            state() | {"kind": "grant"},
            command(),
            codec.envelope("open", **opening),
            codec.envelope("cancel_open", **opening, reason="user"),
            codec.envelope("close", **identity(), reason="capabilities_changed"),
            codec.envelope(
                "result",
                **identity(),
                command_seq=1,
                state_seq=1,
                status="rejected",
                reason="stale_state",
            ),
        ]
        values += [
            codec.envelope(
                "capability", enabled=True, max_payload_bytes=2048, control_kinds=kinds
            )
            for kinds in (["light", "number"], ["light", "number", "choice"])
        ]
        for value in values:
            with self.subTest(kind=value["kind"]):
                self.assertEqual(codec.decode(codec.encode(value)), value)

    def test_snapshot_indices_availability_options_and_exact_fields(self):
        self.assertEqual(
            codec.decode(codec.encode(state() | {"index": None, "available": False}))[
                "index"
            ],
            None,
        )
        for change in (
            {"index": True},
            {"index": -1},
            {"index": 2},
            {"index": None},
            {"available": False},
            {"available": 1},
            {"state_generation": 0},
            {"options": ["Eco", "Eco"]},
            {"options": ["a"] * 9},
            {"options": ["a" * 33]},
            {"value_text": "Eco"},
            {"title": None},
        ):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.decode(json.dumps(state() | change))

    def test_command_captures_strict_target_current_and_generation(self):
        for change in (
            {"target_index": True},
            {"target_index": -1},
            {"target_index": 8},
            {"expected_index": None},
            {"expected_state_generation": 0},
            {"direction": 1},
            {"value": 1},
            {"op": "step"},
            {"option": "Eco"},
        ):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.decode(json.dumps(command() | change))
        for missing in ("target_index", "expected_index", "expected_state_generation"):
            value = command()
            del value[missing]
            with self.assertRaises(codec.ProtocolError):
                codec.decode(json.dumps(value))

    def test_maximum_escaped_options_and_identity_fit_the_existing_wire_bound(self):
        value = state() | {
            "options": [('"' * 31) + str(i) for i in range(8)],
            "title": '"' * 160,
            "index": 7,
            "revision": 2**53 - 1,
            "card_id": "c" * 64,
            "open_seq": 2**31 - 1,
            "state_seq": 2**31 - 1,
            "state_generation": 2**31 - 1,
        }
        wire = codec.encode(value)
        self.assertLessEqual(len(wire.encode()), 2048)
        self.assertEqual(codec.decode(wire), value)
        raw = codec.encode(state()).replace('"index":0', '"index":0,"index":1')
        with self.assertRaises(codec.ProtocolError):
            codec.decode(raw)


if __name__ == "__main__":
    unittest.main()
