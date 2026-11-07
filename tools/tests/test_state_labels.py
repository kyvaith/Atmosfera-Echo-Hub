"""Literal information labels preserve source semantics and action boundaries."""

from copy import deepcopy
import unittest

import test_ha_layout as base


def information(**updates):
    return base.card(entity="input_select.mode", type="sensor", action={"kind": "none"},
                     state_labels={"Eco": "Oszczędny", "Comfort": "Komfortowy"}) | updates


class StateLabelTests(unittest.TestCase):
    def test_roundtrip_and_actual_normalizer_preserve_exact_mapping_without_aliasing(self):
        document = base.document([information()])
        self.assertEqual(base.layout.validate_layout(document), document)
        imported = base.layout.import_layout(base.layout.export_layout(document), 9)
        self.assertEqual(imported["cards"], document["cards"])
        normalized = base.cards.normalize_cards(document["cards"])
        self.assertEqual(normalized[0]["state_labels"], information()["state_labels"])
        normalized[0]["state_labels"]["Eco"] = "Changed"
        self.assertEqual(document["cards"][0]["state_labels"]["Eco"], "Oszczędny")

    def test_only_explicit_information_cards_in_supported_editable_slots(self):
        for change in ({"type": "entity"}, {"type": "action"}, {"entity_id": "sun.sun"},
                       {"entity_id": "light.example"}, {"slot": 0, "visible": False}):
            with self.subTest(change=change), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(base.document([information(**change)]))

    def test_mapping_bounds_reserved_outages_and_printable_exact_text(self):
        invalid = [None, [], "text", {"unknown": "OK"}, {"unavailable": "OK"},
                   {"": "Empty"}, {"Eco": " "}, {"Eco": False}, {"Eco": "a\nb"},
                   {"Eco": "x\u202ey"}, {"Eco": "ą" * 17}, {"x" * 33: "Long"},
                   {str(index): "Label" for index in range(9)}]
        for labels in invalid:
            with self.subTest(labels=labels), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(base.document([information(state_labels=labels)]))
        for labels in ({}, {str(index): "Label" for index in range(8)}, {" Eco ": "literal <&> text"}):
            value = base.layout.validate_layout(base.document([information(state_labels=labels)]))["cards"][0]
            self.assertEqual(value.get("state_labels", {}), labels)

    def test_projection_maps_only_exact_valid_raw_states_and_preserves_missing_state(self):
        card = information()
        state = base.State(card["entity_id"], "Eco", {"options": ["Eco", "Comfort", "Boost"]})
        hass, _ = base.environment(states=[state])
        for raw, expected in [("Eco", "Oszczędny"), ("Comfort", "Komfortowy"), ("Boost", "Boost"),
                              ("eco", "Eco"), ("unknown", "Nieznany"), ("unavailable", "Niedostępny")]:
            state.state = raw
            wire = base.cards.presentation_payload(hass, [card], language="pl-PL")["cards"][2]
            self.assertEqual(wire["subtitle"], expected)
            self.assertNotIn("state_labels", wire)
            self.assertIsNone(base.cards.resolve_action(hass, card))
        hass.states.items.clear()
        self.assertEqual(base.cards.presentation_payload(hass, [card], language="pl")["cards"][2]["subtitle"], "Niedostępny")

    def test_label_is_literal_not_markup_template_or_a_service(self):
        label = "<b>{{ state }}</b>"
        card = information(state_labels={"Eco": label})
        document = base.layout.validate_layout(base.document([card]))
        hass, _ = base.environment(states=[base.State(card["entity_id"], "Eco")])
        before = deepcopy(document)
        self.assertEqual(base.cards.presentation_payload(hass, [card])["cards"][2]["subtitle"], label)
        self.assertEqual(document, before)
        self.assertEqual(hass.services.calls, [])

    def test_binary_source_still_owns_palette_and_icon_after_renaming_presentation(self):
        card = information(entity_id="binary_sensor.door", icon="auto", state_color=True,
                           state_labels={"on": "Otwarte", "off": "Zamknięte"})
        state = base.State(card["entity_id"], "on", {"device_class": "door"})
        hass, _ = base.environment(states=[state])
        wire = base.cards.presentation_payload(hass, [card], language="pl")["cards"][2]
        self.assertEqual((wire["subtitle"], wire["palette"]), ("Otwarte", card["palette"]))
        state.state = "off"
        wire = base.cards.presentation_payload(hass, [card], language="pl")["cards"][2]
        self.assertEqual((wire["subtitle"], wire["palette"]), ("Zamknięte", "surface"))
