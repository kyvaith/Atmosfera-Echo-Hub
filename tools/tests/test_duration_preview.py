"""The preview shares the existing native-duration contract, not a new timer."""

import json
from pathlib import Path
import unittest

import test_ha_layout as base


class DurationPreviewContractTests(unittest.TestCase):
    def test_shared_preview_cases_pin_the_existing_decimal_duration_projection(self):
        cases = json.loads((Path(__file__).parent / "fixtures/duration_preview.json").read_text(encoding="utf-8"))
        self.assertGreater(len(cases), 100)
        for item in cases:
            options = {} if item["precision"] is None else {"sensor": {"display_precision": item["precision"]}}
            for language in ("pl", "en"):
                self.assertEqual(base.cards.sensor_text(item["state"], item["unit"], "duration", language, options), item[language], item)

    def test_ties_subseconds_sign_and_two_part_limit_remain_the_native_behavior(self):
        text = base.cards.sensor_text
        options = {"sensor": {"display_precision": 3}}
        self.assertEqual(text("59.9995", "s", "duration", "en", options), "1 min")
        self.assertEqual(text("59.9985", "s", "duration", "pl", options), "59,998 s")
        self.assertEqual(text("244291", "s", "duration", "pl"), "2 d 19 h")
        self.assertEqual(text("-3661", "s", "duration", "en"), "-1 h 1 min")
        self.assertEqual(text("12.3456", "μs", "duration", "pl"), "12,3456 us")
        self.assertEqual(text("316224001", "s", "duration", "pl"), "Poza zakresem")
