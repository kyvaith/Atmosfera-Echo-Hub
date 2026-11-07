"""Person uses Core's state and HA labels, without tracker/location authority."""

import importlib
import json
import unittest
from unittest.mock import patch

import test_ha_layout as base

formatting = importlib.import_module("_atmosfera_test.formatting")


class PersonPresenceTests(unittest.TestCase):
    def test_home_away_fallback_and_primary_ha_translation(self):
        for raw, pl, en in (("home", "W domu", "Home"), ("not_home", "Poza domem", "Away")):
            self.assertEqual(formatting.person_state_text(raw, "pl-PL"), pl)
            self.assertEqual(formatting.person_state_text(raw, "en"), en)
            state = base.State("person.qa", raw)
            hass, _ = base.environment(states=[state])
            labels = {f"component.person.entity_component._.state.{raw}": "Etykieta HA"}
            with patch.object(base.cards, "async_get_cached_translations", return_value=labels):
                self.assertEqual(base.cards._state_subtitle(hass, state, "pl"), "Etykieta HA")

    def test_zone_keeps_case_and_underscores_not_a_guessed_home_state(self):
        self.assertEqual(formatting.person_state_text("Praca_Północ", "pl"), "Praca_Północ")
        self.assertEqual(formatting.person_state_text("home office", "en", "Home"), "home office")
        self.assertEqual(formatting.person_state_text("<b>Żółć &amp; coś</b>\n", "pl"), "Żółć & coś")
        text = formatting.person_state_text("W" * 255, "en")
        self.assertEqual(text, "W" * 19 + "...")

    def test_unknown_unavailable_and_blank_never_claim_away(self):
        for raw in (None, 1, "", "  ", "<b></b>", "\u200b", "unknown"):
            self.assertEqual(formatting.person_state_text(raw, "pl"), "Nieznany")
        self.assertEqual(formatting.person_state_text("unavailable", "pl"), "Niedostępny")

    def test_only_wide_information_row_and_no_actions_are_admitted(self):
        for slot in range(16):
            doc = base.document([base.card(slot=slot, entity="person.qa", type="sensor", icon="presence", action={"kind": "none"}, state_color=True)])
            if slot == 12:
                self.assertEqual(base.layout.validate_layout(doc), doc)
            else:
                with self.assertRaises(base.layout.LayoutError):
                    base.layout.validate_layout(doc)
        self.assertTrue(base.layout.device_profile()["schema_person_presence"])
        self.assertEqual(base.layout.device_profile()["person_text_slots"], [12])
        for action in ({"kind": "default"}, {"kind": "service", "service": "homeassistant.turn_on", "data": {}}, {"kind": "control", "control": "choice"}):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, "person.qa", layout_version=3)

    def test_optional_accent_requires_exact_home_and_unknown_keeps_surface(self):
        item = base.card(slot=12, entity="person.qa", type="sensor", action={"kind": "none"}, state_color=True)
        for raw in ("home", "not_home", "Home", "on", "work", "unknown", "unavailable"):
            state = base.State("person.qa", raw)
            self.assertEqual(base.cards.presentation_palette(item, state), "primary" if raw == "home" else "surface")
        self.assertEqual(base.cards.presentation_palette(item, None), "surface")
        self.assertEqual(base.cards.presentation_palette(item | {"state_color": False}, base.State("person.qa", "not_home")), "primary")

    def test_metadata_never_exports_private_attributes_and_labels_match_native(self):
        attrs = {"latitude": 1.2, "longitude": 3.4, "gps_accuracy": 7, "user_id": "ACCOUNT", "entity_picture": "/SECRET", "source": "device_tracker.private", "device_trackers": ["device_tracker.private"]}
        state = base.State("person.qa", "Praca", attrs)
        hass, _ = base.environment(states=[state])
        meta = base.cards._person_presence_metadata(hass, state)["person_presence"]
        self.assertEqual(meta, {"state": "Praca", "text": {"pl": "Praca", "en": "Praca"}})
        result = base.cards.entity_catalogue(hass, domains=["person"])
        self.assertEqual(result["total"], 1)
        serialized = json.dumps(result)
        for private in ("latitude", "longitude", "gps_accuracy", "user_id", "ACCOUNT", "SECRET", "device_tracker.private"):
            self.assertNotIn(private, serialized)
        item = base.card(slot=12, entity=state.entity_id, type="sensor", icon="presence", action={"kind": "none"})
        rendered = base.cards.presentation_payload(hass, [item], language="pl")["cards"][12]
        self.assertEqual(rendered["subtitle"], meta["text"]["pl"])

    def test_raw_legacy_actions_cannot_execute_or_be_advertised(self):
        state = base.State("person.qa", "home")
        hass, _ = base.environment(states=[state], services=["homeassistant.turn_on"])
        item = base.card(slot=12, entity=state.entity_id, type="entity", action={"kind": "service", "service": "homeassistant.turn_on", "data": {}})
        self.assertIsNone(base.cards.resolve_action(hass, item))
        self.assertEqual(base.cards.entity_actions(hass, state), [])
        self.assertEqual(hass.services.calls, [])
