"""Strict calendar semantics, native projection and unchanged information domains."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

import test_ha_layout as base


def information(entity="sensor.example", **updates):
    return base.card(entity=entity, type="sensor", action={"kind": "none"}, **updates)


class CalendarDateTests(unittest.TestCase):
    def test_shared_dates_are_strict_gregorian_and_independent_of_precision(self):
        cases = json.loads(
            (Path(__file__).parent / "fixtures/calendar_dates.json").read_text(encoding="utf-8")
        )
        for case in cases:
            for language, unknown in (("pl", "Nieznany"), ("en", "Unknown")):
                for precision in (None, 0, 6):
                    with self.subTest(case=case, language=language, precision=precision):
                        state = base.State("sensor.example", case["state"], {
                            "device_class": "date", "unit_of_measurement": "ignored",
                        })
                        hass, _ = base.environment(states=[state])
                        card = information(**({"display_precision": precision} if precision is not None else {}))
                        before = deepcopy((state.attributes, card))
                        text = base.cards.presentation_payload(hass, [card], language=language)["cards"][2]["subtitle"]
                        self.assertEqual(text, case.get(language, unknown))
                        self.assertLessEqual(len(text), 40)
                        self.assertEqual((state.attributes, card), before)
                        self.assertIsNone(base.cards.resolve_action(hass, card))

    def test_missing_and_exceptional_states_stay_explicit(self):
        card = information()
        hass, _ = base.environment()
        self.assertEqual(base.cards.presentation_payload(hass, [card], language="pl")["cards"][2]["subtitle"], "Niedostępny")
        for raw, expected in (("unknown", "Nieznany"), ("unavailable", "Niedostępny")):
            state = base.State("sensor.example", raw, {"device_class": "date"})
            hass, _ = base.environment(states=[state])
            self.assertEqual(base.cards.presentation_payload(hass, [card], language="pl")["cards"][2]["subtitle"], expected)

    def test_exact_user_mapping_wins_and_locale_does_not_shift_calendar_day(self):
        state = base.State("sensor.example", "2000-02-29", {"device_class": "date"})
        hass, _ = base.environment(states=[state])
        mapped = information(state_labels={"2000-02-29": "Przestępny"})
        self.assertEqual(base.cards.presentation_payload(hass, [mapped], language="en")["cards"][2]["subtitle"], "Przestępny")
        for zone in ("UTC", "Pacific/Honolulu", "Pacific/Kiritimati"):
            hass.config.time_zone = zone
            self.assertEqual(base.cards.presentation_payload(hass, [information()], language="PL_pl")["cards"][2]["subtitle"], "29.02.2000")
        self.assertEqual(base.cards.calendar_date_text("x" * 100000, "pl"), "Nieznany")

    def test_date_attribute_does_not_change_other_domains_or_timestamp_sensors(self):
        for domain, attributes in (("number", {}), ("input_number", {}), ("input_text", {"mode": "text"})):
            entity = domain + ".example"
            state = base.State(entity, "2026-10-31", {"device_class": "date", **attributes})
            hass, _ = base.environment(states=[state])
            text = base.cards.presentation_payload(hass, [information(entity)], language="pl")["cards"][2]["subtitle"]
            self.assertEqual(text, "2026-10-31")
        state = base.State("sensor.example", "2026-10-31T23:30:00+01:00", {"device_class": "timestamp"})
        hass, _ = base.environment(states=[state])
        self.assertEqual(base.cards.presentation_payload(hass, [information()], language="pl")["cards"][2]["subtitle"], "2026-10-31T23:30:00+01:00")
