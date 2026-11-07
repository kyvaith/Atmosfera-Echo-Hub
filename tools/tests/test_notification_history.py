"""History retention and hostile/stale wire requests, without a running HA."""

import importlib
import json
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2] / "custom_components/atmosfera_echo_hub"
package = types.ModuleType("_notification_test")
package.__path__ = [str(ROOT)]
sys.modules[package.__name__] = package
history = importlib.import_module("_notification_test.notification_history")


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.now = 200000
        self.history = history.NotificationHistory(lambda: self.now)

    def test_bound_newest_first_and_page_clamp_after_dismiss(self):
        for index in range(109):
            self.history.add(str(index), "test")
        self.assertEqual(len(self.history.records), 100)
        self.assertEqual(self.history.records[0].title, "108")
        self.assertEqual(self.history.page(96)["rows"][0]["title"], "12")
        for record in list(self.history.records[88:]):
            self.assertTrue(self.history.dismiss(record.id))
        self.assertEqual(self.history.page(96)["offset"], 80)

    def test_retention_runs_on_read_dismiss_and_reload(self):
        record = self.history.add("Zażółć", "Test")
        saved = self.history.dump()
        self.now += history.RETENTION_SECONDS
        self.assertIsNone(self.history.detail(record.id))
        self.assertFalse(self.history.dismiss(record.id))
        self.history.load(saved)
        self.assertEqual(self.history.page(0)["total"], 0)

    def test_modern_overlapping_window_has_timestamps_and_clamps_after_removal(self):
        for index in range(20):
            self.history.add(str(index), "Body" * 30)
        page = self.history.page(5, version=2)
        self.assertEqual(page["offset"], 5)
        self.assertEqual([r["title"] for r in page["rows"]], [str(i) for i in range(14, 6, -1)])
        self.assertTrue(all(r["created"] == self.now for r in page["rows"]))
        self.assertEqual(len(page["rows"][0]["message"]), 96)
        self.assertEqual(self.history.page(99, version=2)["offset"], 12)
        self.assertNotIn("created", self.history.page(5)["rows"][0])

    def test_reload_same_timestamp_preserves_insertion_order(self):
        for index in range(12):
            self.history.add(str(index), "Body")
        saved = self.history.dump()
        self.history.load(saved)
        self.assertEqual(self.history.dump(), saved)

    def test_stable_id_never_targets_replacement_at_same_row(self):
        old = self.history.add("A", "body")
        new = self.history.add("B", "body")
        self.history.dismiss(old.id)
        self.assertFalse(self.history.dismiss(old.id))
        self.assertEqual(self.history.detail(new.id)["title"], "B")

    def test_corrupt_duplicate_future_and_expired_records_are_dropped(self):
        record = self.history.add("A", "B")
        valid = self.history.dump()[0]
        self.history.load(
            [
                None,
                {},
                {**valid, "created": True},
                {**valid, "id": "f" * 32, "created": self.now + 1},
                valid,
                valid,
            ]
        )
        self.assertEqual(self.history.page(0)["total"], 1)
        self.assertEqual(self.history.records[0].id, record.id)

    def test_text_has_no_html_and_is_bounded_in_characters(self):
        record = self.history.add("<b>ż</b>" * 100, "ą" * 1000)
        self.assertLessEqual(len(record.title), 64)
        self.assertLessEqual(len(record.message), 384)
        self.assertNotIn("<", record.title)
        self.assertLessEqual(len(self.history.page(0)["rows"][0]["message"]), 64)


class RequestTests(unittest.TestCase):
    def request(self, **updates):
        return {
            "v": 1,
            "channel": "a" * 32,
            "seq": 1,
            "op": "page",
            "offset": 0,
            **updates,
        }

    def test_each_typed_request_round_trips(self):
        for op in ("page", "open", "dismiss"):
            data = self.request(op=op)
            if op != "page":
                data["id"] = "b" * 32
            self.assertEqual(history.decode_request(json.dumps(data)), data)

    def test_modern_requests_allow_sliding_window_but_keep_strict_schema(self):
        for offset in (1, 5, 99):
            data = self.request(v=2, offset=offset)
            self.assertEqual(history.decode_request(json.dumps(data)), data)
        for version in (0, 4, True, 2.0):
            with self.assertRaises(ValueError):
                history.decode_request(json.dumps(self.request(v=version)))

    def test_unknown_identity_fields_and_wrong_types_are_rejected(self):
        for update in (
            {"user": "admin"},
            {"service": "light.toggle"},
            {"id": "b" * 32},
            {"offset": 1},
            {"offset": 104},
            {"offset": True},
            {"seq": 0},
            {"seq": 2**31},
            {"seq": 1.0},
            {"v": True},
            {"op": "clear_all"},
            {"channel": "x" * 32},
        ):
            with self.subTest(update=update), self.assertRaises(ValueError):
                history.decode_request(json.dumps(self.request(**update)))

    def test_duplicate_keys_and_oversized_payload_are_rejected(self):
        payload = json.dumps(self.request())
        with self.assertRaises(ValueError):
            history.decode_request(payload[:-1] + ', "seq": 2}')
        with self.assertRaises(ValueError):
            history.decode_request(" " * 513)


if __name__ == "__main__":
    unittest.main()
