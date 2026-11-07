"""Passive HA text helpers; password mode never reaches card/library values."""

import unittest

import test_ha_layout as base


class TextInformationTests(unittest.TestCase):
    def test_plain_helper_is_discoverable_and_passive_with_bounded_text(self):
        state = base.State("input_text.note", "Kurier o 15:30", {"mode": "text", "friendly_name": "Notatka"})
        hass, _ = base.environment(states=[state], services=["input_text.set_value"])
        result = base.cards.entity_catalogue(hass, query="Notatka")
        self.assertEqual([e["entity_id"] for e in result["entities"]], [state.entity_id])
        self.assertEqual(result["entities"][0]["actions"], [])
        card = base.card(entity=state.entity_id, type="sensor", action={"kind": "none"})
        document = base.document([card])
        self.assertEqual(base.layout.import_layout(base.layout.export_layout(document), 8)["cards"], [card])
        self.assertEqual(base.cards.presentation_payload(hass, [card], language="pl")["cards"][2]["subtitle"], "Kurier o 15:30")
        self.assertIsNone(base.cards.resolve_action(hass, card))
        state.state = "x" * 200
        self.assertLessEqual(len(base.cards.presentation_payload(hass, [card])["cards"][2]["subtitle"]), 40)
        state.state = "  <b>Notatka</b>\n  domowa  "
        self.assertEqual(base.cards.presentation_payload(hass, [card])["cards"][2]["subtitle"], "<b>Notatka</b> domowa")

    def test_password_or_unrecognized_mode_is_not_discovered_and_cannot_be_unmasked_by_labels(self):
        for mode in ("password", None, "unknown"):
            state = base.State("input_text.note", "QA-value", {"mode": mode})
            hass, _ = base.environment(states=[state])
            card = base.card(entity=state.entity_id, type="sensor", action={"kind": "none"}, state_labels={"QA-value": "Exposed"})
            base.layout.validate_layout(base.document([card]))
            self.assertEqual(base.cards.entity_catalogue(hass)["entities"], [])
            for locale, expected in [("pl", "Tekst ukryty"), ("en", "Hidden text")]:
                self.assertEqual(base.cards.presentation_payload(hass, [card], language=locale)["cards"][2]["subtitle"], expected)

    def test_outages_are_not_replaced_by_custom_text_or_password_status(self):
        state = base.State("input_text.note", "unknown", {"mode": "password"})
        hass, _ = base.environment(states=[state])
        card = base.card(entity=state.entity_id, type="sensor", action={"kind": "none"})
        for value, expected in [("unknown", "Nieznany"), ("unavailable", "Niedostępny")]:
            state.state = value
            self.assertEqual(base.cards.presentation_payload(hass, [card], language="pl")["cards"][2]["subtitle"], expected)

    def test_plain_mode_supports_presentation_labels_but_no_write_action(self):
        state = base.State("input_text.note", "Eco", {"mode": "text"})
        hass, _ = base.environment(states=[state])
        card = base.card(entity=state.entity_id, type="sensor", action={"kind": "none"}, state_labels={"Eco": "Oszczędny"})
        self.assertEqual(base.cards.presentation_payload(hass, [card])["cards"][2]["subtitle"], "Oszczędny")
        card.update(type="action", action={"kind": "service", "service": "input_text.set_value", "data": {"value": "bad"}})
        with self.assertRaises(base.layout.LayoutError):
            base.layout.validate_layout(base.document([card]))
