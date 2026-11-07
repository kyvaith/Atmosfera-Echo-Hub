"""Prevent real 290px Roboto16 clipping seen on native45 screenshots."""

import importlib
import unittest

import test_ha_layout  # Establish the isolated HA test package.

width = importlib.import_module("_atmosfera_test.caption_width")
formatting = importlib.import_module("_atmosfera_test.formatting")


class CaptionWidthTests(unittest.TestCase):
    def test_fifth_page_caption_fits_the_native_100_pixel_label(self):
        self.assertEqual(width.fit_caption("70 %", 100), "70 %")
        fitted = width.fit_caption("Pochylenie osłony 50 %", 100)
        self.assertTrue(fitted.endswith("..."))
        self.assertLessEqual(width.caption_width(fitted), 100)

    def test_wide_glyphs_keep_visible_ellipsis_but_narrow_text_keeps_character_budget(self):
        self.assertEqual(width.caption_width("W"), 14)
        self.assertEqual(width.caption_width("."), 4)
        self.assertEqual(width.fit_wide_caption("W" * 40), "W" * 19 + "...")
        self.assertEqual(width.fit_wide_caption("i" * 40), "i" * 40)
        self.assertEqual(width.fit_wide_caption("i" * 41), "i" * 37 + "...")
        self.assertEqual(width.fit_wide_caption("2026-11-01 17:15 · Plan dnia"), "2026-11-01 17:15 · Plan dnia")

    def test_calendar_and_person_share_actual_pixel_budget_for_every_supported_glyph(self):
        event = {"message": "", "all_day": False, "start_time": "2026-11-01 17:15:00", "end_time": "2026-11-01 18:15:00"}
        for cp in (*width._GLYPHS, 0x1F600):
            char = chr(cp)
            if not char.isprintable() or char in "<&":
                continue
            for language in ("pl", "en"):
                person = formatting.person_state_text(char * 255, language)
                calendar = formatting.calendar_event_text("off", event | {"message": char * 255}, language)
                for caption in (person, calendar):
                    self.assertLessEqual(len(caption), 40)
                    self.assertLessEqual(width.caption_width(caption), 288)
        self.assertEqual(width.caption_width("W" * 19 + "..."), 278)
