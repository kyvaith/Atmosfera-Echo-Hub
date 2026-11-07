"""Reported CalendarEntity event is passive, bounded and kept in its wide row."""

import importlib
import unittest
from copy import deepcopy

import test_ha_layout as base

formatting = importlib.import_module("_atmosfera_test.formatting")
EVENT = {"message": "Plan dnia", "all_day": False, "start_time": "2026-11-01 17:15:00", "end_time": "2026-11-01 18:15:00"}


class CalendarNextTests(unittest.TestCase):
    def test_reported_future_event_is_visible_even_when_calendar_state_is_off(self):
        for state in ("on", "off"):
            self.assertEqual(formatting.calendar_event_text(state, EVENT, "pl"), "01.11.2026 17:15 · Plan dnia")
            self.assertEqual(formatting.calendar_event_text(state, EVENT, "en"), "2026-11-01 17:15 · Plan dnia")

    def test_all_day_keeps_the_reported_date_and_does_not_invent_a_clock(self):
        event = EVENT | {"all_day": True, "message": "Wyjazd"}
        self.assertEqual(formatting.calendar_event_text("off", event, "pl"), "01.11.2026 · Cały dzień · Wyjazd")
        self.assertEqual(formatting.calendar_event_text("on", event, "en"), "2026-11-01 · All day · Wyjazd")
        event.update(start_time="2026-10-25 02:50:00", end_time="2026-10-25 02:10:00", all_day=False)
        self.assertEqual(formatting.calendar_event_text("on", event, "en"), "2026-10-25 02:50 · Wyjazd")

    def test_only_known_empty_off_is_no_event_and_partial_malformed_outage_is_not_empty(self):
        self.assertEqual(formatting.calendar_event_text("off", {"friendly_name": "Calendar"}, "pl"), "Brak wydarzeń")
        self.assertEqual(formatting.calendar_event_text("off", {}, "en"), "No events")
        for state, attrs in (("on", {}), ("unavailable", EVENT), ("unknown", EVENT), ("on", None), (None, EVENT)):
            expected = "Unavailable" if state == "unavailable" else "Unknown"
            self.assertEqual(formatting.calendar_event_text(state, attrs, "en"), expected)
        for patch in ({"message": None}, {"all_day": 1}, {"start_time": "2026-02-30 17:15:00"},
            {"start_time": "2026-11-01T17:15:00Z"}, {"end_time": "2026-11-01 24:00:00"}):
            self.assertEqual(formatting.calendar_event_text("off", EVENT | patch, "en"), "Unknown")
        partial = deepcopy(EVENT);partial.pop("start_time")
        self.assertEqual(formatting.calendar_event_text("off", partial, "en"), "Unknown")

    def test_summary_is_plain_bounded_and_does_not_include_location_description(self):
        event = EVENT | {"message": "<b>Żółć &amp; coś</b>\n", "description": "PRIVATE", "location": "SECRET"}
        self.assertEqual(formatting.calendar_event_text("off", event, "pl"), "01.11.2026 17:15 · Żółć & coś")
        text = formatting.calendar_event_text("off", event | {"message": "Ż" * 1000}, "pl")
        self.assertLessEqual(len(text), 40);self.assertTrue(text.endswith("..."))
        self.assertNotIn("PRIVATE", text);self.assertNotIn("SECRET", text)
        self.assertEqual(formatting.calendar_event_text("off", EVENT | {"message": "  "}, "en"), "2026-11-01 17:15 · Untitled")

    def test_only_the_existing_wide_information_row_is_admitted_and_no_action_is_allowed(self):
        for slot in range(16):
            doc = base.document([base.card(slot=slot, entity="calendar.test", type="sensor", action={"kind": "none"})])
            if slot == 12:
                self.assertEqual(base.layout.validate_layout(doc), doc)
            else:
                with self.assertRaises(base.layout.LayoutError):
                    base.layout.validate_layout(doc)
        self.assertEqual(base.layout.device_profile()["calendar_text_slots"], [12])
        for action in ({"kind": "default"}, {"kind": "service", "service": "homeassistant.turn_on", "data": {}},
            {"kind": "control", "control": "choice"}):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, "calendar.test", layout_version=3)

    def test_catalogue_and_native_projection_have_actual_event_text_and_never_an_actuator(self):
        state = base.State("calendar.test", "off", deepcopy(EVENT))
        hass, _ = base.environment(states=[state], services=["homeassistant.turn_on", "calendar.create_event"])
        item = base.card(slot=12, entity=state.entity_id, type="sensor", action={"kind": "none"})
        rendered = base.cards.presentation_payload(hass, [item], language="pl", press_enabled_supported=True)["cards"][12]
        self.assertEqual(rendered["subtitle"], "01.11.2026 17:15 · Plan dnia")
        self.assertEqual(base.cards.entity_actions(hass, state), [])
        self.assertIsNone(base.cards.resolve_action(hass, item | {"action": {"kind": "service", "service": "homeassistant.turn_on", "data": {}}}))
        self.assertEqual(hass.services.calls, [])
        result = base.cards.entity_catalogue(hass, domains=["calendar"])
        self.assertEqual(result["entities"][0]["actions"], [])
        self.assertEqual(result["entities"][0]["calendar_next"]["fields"], EVENT)

    def test_metadata_records_the_exact_bounded_observation_and_both_languages(self):
        state = base.State("calendar.test", "off", deepcopy(EVENT))
        value = base.cards._calendar_next_metadata(state)["calendar_next"]
        self.assertEqual(value["text"]["pl"], formatting.calendar_event_text("off", EVENT, "pl"))
        self.assertEqual(value["text"]["en"], formatting.calendar_event_text("off", EVENT, "en"))
        self.assertEqual(value["fields"], EVENT)
        state.attributes["message"] = "Ż" * 1000
        value = base.cards._calendar_next_metadata(state)["calendar_next"]
        self.assertEqual(len(value["fields"]["message"]), 256)
        state.attributes["all_day"] = None
        self.assertEqual(base.cards._calendar_next_metadata(state), {})
