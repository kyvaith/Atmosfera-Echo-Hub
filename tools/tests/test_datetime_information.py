"""Date/time helpers remain literal, bounded and non-executable."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

import yaml

import test_ha_layout as base


def information(**updates):
    card = base.card(entity="input_datetime.example", type="sensor", icon="clock", action={"kind": "none"})
    card.update(updates)
    return card


class DatetimeInformationTests(unittest.TestCase):
    def test_admitted_product_captions_fit_the_combined_literal(self):
        product = Path(__file__).resolve().parents[2] / "modules/lvgl/pages/tiles_m3.yaml"
        widths = {}

        def visit(node):
            if isinstance(node, dict):
                if node.get("text_font") == "roboto_16" and "id" in node:
                    widths[node["id"]] = node.get("width", 0)
                for child in node.values():
                    visit(child)
            elif isinstance(node, list):
                for child in node:
                    visit(child)

        visit(yaml.safe_load(product.read_text(encoding="utf-8")))
        captions = {3: "tile_lock_subtitle", 5: "tile_garage_subtitle",
                    8: "tile_switch_subtitle", 9: "tile_scene_subtitle",
                    10: "tile_trigger_subtitle", 11: "tile_window_subtitle",
                    12: "tile_presence_subtitle"}
        self.assertEqual(set(captions), set(base.layout.DATETIME_TEXT_SLOTS))
        for slot, label in captions.items():
            with self.subTest(slot=slot, label=label):
                self.assertGreaterEqual(widths[label], 172)

    def test_three_modes_share_strict_vectors_with_editor_and_do_not_mutate(self):
        cases = json.loads((Path(__file__).parent / "fixtures/datetime_helpers.json").read_text(encoding="utf-8"))
        for item in cases:
            for language, unknown in (("pl", "Nieznany"), ("en", "Unknown")):
                with self.subTest(item=item, language=language):
                    state = base.State("input_datetime.example", item["state"], item["attributes"])
                    hass, _ = base.environment(states=[state], services=["input_datetime.set_datetime", "homeassistant.toggle"])
                    card = information()
                    before = deepcopy((state.attributes, card))
                    text = base.cards.presentation_payload(hass, [card], language=language)["cards"][2]["subtitle"]
                    self.assertEqual(text, item.get(language, unknown))
                    self.assertLessEqual(len(text), 19)
                    self.assertEqual((state.attributes, card), before)
                    self.assertIsNone(base.cards.resolve_action(hass, card))
                    self.assertEqual(base.cards.entity_actions(hass, state), [])

    def test_only_information_in_text_places_with_explicit_none_action(self):
        profile = base.layout.device_profile()
        self.assertEqual(profile["datetime_text_slots"], [3, 5, 8, 9, 10, 11, 12])
        self.assertEqual(profile["datetime_text_slots"], list(base.layout.DATETIME_TEXT_SLOTS))
        for slot in range(16):
            card = information(slot=slot, visible=slot >= 2)
            if slot in base.layout.DATETIME_TEXT_SLOTS:
                doc = base.document([card])
                self.assertEqual(base.layout.validate_layout(doc), doc)
                self.assertEqual(base.layout.import_layout(base.layout.export_layout(doc), 8)["cards"], [card])
            else:
                with self.subTest(slot=slot), self.assertRaises(base.layout.LayoutError):
                    base.layout.validate_layout(base.document([card]))
        for updates in ({"type": "entity"}, {"type": "action"}, {"action": {"kind": "default"}},
                        {"action": {"kind": "service", "service": "input_datetime.set_datetime", "data": {}}},
                        {"display_precision": 0}):
            with self.subTest(updates=updates), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(base.document([information(**updates)]))

    def test_raw_legacy_commands_cannot_turn_helper_into_an_action(self):
        state = base.State("input_datetime.example", "12:34:56", {"has_date": False, "has_time": True})
        hass, _ = base.environment(states=[state], services=["input_datetime.set_datetime", "homeassistant.toggle"])
        for action in ({"kind": "default"}, {"kind": "service", "service": "homeassistant.toggle", "data": {}},
                       {"kind": "service", "service": "input_datetime.set_datetime", "data": {"time": "01:02:03"}}):
            raw = information(type="entity", action=action)
            self.assertIsNone(base.cards.resolve_action(hass, raw))
        normalized = base.cards.normalize_cards([information()])
        self.assertEqual(normalized[0]["entity_id"], state.entity_id)
        self.assertEqual([e["entity_id"] for e in base.cards.entity_catalogue(hass)["entities"]], [state.entity_id])

    def test_mappings_outages_and_timezone_independence(self):
        attributes = {"has_date": True, "has_time": True, "timestamp": 0}
        state = base.State("input_datetime.example", "2000-02-29 12:34:56", attributes)
        hass, _ = base.environment(states=[state])
        card = information(state_labels={state.state: "Rocznica"})
        self.assertEqual(base.cards.presentation_payload(hass, [card], language="en")["cards"][2]["subtitle"], "Rocznica")
        for zone in ("Pacific/Honolulu", "Pacific/Kiritimati"):
            hass.config.time_zone = zone
            self.assertEqual(base.cards.presentation_payload(hass, [information()], language="pl")["cards"][2]["subtitle"], "29.02.2000 12:34:56")
        for raw, expected in (("unknown", "Nieznany"), ("unavailable", "Niedostępny")):
            state.state = raw
            self.assertEqual(base.cards.presentation_payload(hass, [card], language="pl")["cards"][2]["subtitle"], expected)
        self.assertEqual(base.cards.datetime_helper_text("x" * 100000, attributes), "Unknown")
