"""Semantic binary information is passive, with opt-in roles and existing glyphs."""

from copy import deepcopy
from pathlib import Path
import re
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_ha_layout as base


def info(**updates):
    return base.card(
        entity="binary_sensor.example",
        type="sensor",
        action={"kind": "none"},
        icon="auto",
        state_color=True,
        **updates,
    )


class BinaryInformationTests(unittest.TestCase):
    def test_readonly_binary_style_and_auto_icon_roundtrip_as_opt_in(self):
        doc = base.document([info()])
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertEqual(
            base.layout.import_layout(base.layout.export_layout(doc), 8),
            {**doc, "revision": 8},
        )
        normalized = base.cards.normalize_cards(doc["cards"])
        self.assertIs(normalized[0]["state_color"], True)
        self.assertEqual(normalized[0]["icon"], "auto")
        for entity, kind in (
            ("light.room", "sensor"),
            ("binary_sensor.example", "entity"),
            ("timer.example", "sensor"),
        ):
            card = info()
            card.update(entity_id=entity, type=kind)
            with (
                self.subTest(entity=entity),
                self.assertRaises(base.layout.LayoutError),
            ):
                base.layout.validate_layout(base.document([card]))

    def test_semantic_class_selects_only_existing_compiled_icons_and_expected_roles(
        self,
    ):
        for device_class, icon in (
            ("door", "door"),
            ("window", "door"),
            ("opening", "door"),
            ("garage_door", "door"),
            ("motion", "presence"),
            ("occupancy", "presence"),
            ("presence", "presence"),
            ("power", "sensor"),
            (None, "sensor"),
            ([], "sensor"),
        ):
            for state in ("on", "off", "unknown", "unavailable"):
                hass, _ = base.environment(
                    states=[
                        base.State(
                            "binary_sensor.example",
                            state,
                            {"device_class": device_class},
                        )
                    ]
                )
                card = info()
                before = deepcopy(card)
                wire = base.cards.presentation_payload(hass, [card], language="pl")[
                    "cards"
                ][2]
                self.assertEqual(wire["icon"], base.cards.ICONS[icon])
                self.assertEqual(
                    wire["palette"], "primary" if state == "on" else "surface"
                )
                self.assertNotIn("control_kind", wire)
                self.assertEqual(card, before)

    def test_moisture_auto_projection_keeps_state_translation_and_manual_icons(self):
        for state in ("on", "off", "unknown", "unavailable"):
            observed = base.State(
                "binary_sensor.example", state, {"device_class": "moisture"}
            )
            hass, _ = base.environment(states=[observed])
            for action in (
                {"kind": "none"},
                {"kind": "control", "control": "panel", "property": "info"},
            ):
                card = {**info(), "action": action}
                before = deepcopy(card)
                wire = base.cards.presentation_payload(hass, [card], language="pl")[
                    "cards"
                ][2]
                self.assertEqual(wire["icon"], "\ue798")
                manual = {**card, "icon": "door"}
                manual_wire = base.cards.presentation_payload(
                    hass, [manual], language="pl"
                )["cards"][2]
                self.assertEqual(wire["subtitle"], manual_wire["subtitle"])
                self.assertEqual(manual_wire["icon"], base.cards.ICONS["door"])
                self.assertEqual(card, before)
                self.assertEqual(hass.services.calls, [])
            for manual_icon in base.cards.ICONS.keys() - {"auto"}:
                self.assertEqual(
                    base.cards.presentation_icon(
                        {**info(), "icon": manual_icon}, observed
                    ),
                    base.cards.ICONS[manual_icon],
                )

    def test_moisture_auto_unknown_class_keeps_fallback_and_public_choices(self):
        for device_class in (
            None, [], {}, 42, "unknown", "humidity", "temperature", "power"
        ):
            state = base.State(
                "binary_sensor.example", "off", {"device_class": device_class}
            )
            self.assertEqual(
                base.cards.presentation_icon(info(), state), base.cards.ICONS["sensor"]
            )
        self.assertEqual(
            base.cards.presentation_icon(info(), None), base.cards.ICONS["sensor"]
        )
        self.assertNotIn("humidity", base.cards.ICONS)
        with self.assertRaises(base.layout.LayoutError):
            base.layout.validate_layout(base.document([{**info(), "icon": "humidity"}]))

    def test_moisture_auto_glyph_is_declared_in_every_actual_home_icon_font(self):
        product = Path(__file__).resolve().parents[2]
        material = (product / "modules/lvgl/material.yaml").read_text(encoding="utf8")
        tiles = (product / "modules/lvgl/pages/tiles_m3.yaml").read_text(encoding="utf8")
        icons = set(re.findall(r"icon_label: ([a-zA-Z0-9_]+)", material))
        used, current = set(), None
        for line in tiles.splitlines():
            if match := re.match(r"\s*id: (\S+)$", line):
                current = match.group(1)
            if current in icons and (match := re.match(r"\s*text_font: (\S+)$", line)):
                used.add(match.group(1))
        self.assertEqual(
            used, {"material_symbols_36", "material_symbols_44", "material_symbols_68"}
        )
        fonts = (product / "modules/lvgl/fonts.yaml").read_text(encoding="utf8")
        blocks = re.split(r"(?=^  - file:)", fonts, flags=re.M)
        for font in used:
            block, = [part for part in blocks if f"    id: {font}\n" in part]
            self.assertRegex(block, r'\\[uU]0*[eE]798')

    def test_unknown_never_looks_closed_or_clear_and_info_can_never_dispatch(self):
        for state, label in (("unknown", "Nieznany"), ("unavailable", "Niedostępny")):
            hass, _ = base.environment(
                states=[
                    base.State("binary_sensor.example", state, {"device_class": "door"})
                ],
                services=["homeassistant.toggle", "binary_sensor.turn_on"],
            )
            card = info()
            self.assertEqual(
                base.cards.presentation_payload(hass, [card], language="pl")["cards"][
                    2
                ]["subtitle"],
                label,
            )
            self.assertIsNone(base.cards.resolve_action(hass, card))
            self.assertEqual(hass.services.calls, [])
        for state in ("on", "off"):
            hass, _ = base.environment(
                states=[
                    base.State("binary_sensor.example", state, {"device_class": "door"})
                ],
                services=["homeassistant.toggle"],
            )
            self.assertIsNone(base.cards.resolve_action(hass, info()))

    def test_manual_icons_and_fixed_old_binary_cards_keep_existing_behavior(self):
        hass, _ = base.environment(
            states=[
                base.State("binary_sensor.example", "on", {"device_class": "motion"})
            ]
        )
        card = info()
        card["icon"] = "door"
        card.pop("state_color")
        wire = base.cards.presentation_payload(hass, [card])["cards"][2]
        self.assertEqual(wire["icon"], base.cards.ICONS["door"])
        self.assertEqual(wire["palette"], card["palette"])

    def test_unsupported_legacy_auto_keeps_previous_safe_fallback(self):
        card = base.card(entity="light.example", icon="auto")
        normalized = base.cards.normalize_cards([card])
        self.assertEqual(normalized[0]["icon"], "action")
        self.assertEqual(
            base.layout.migrate_legacy(normalized)["cards"][0]["icon"], "action"
        )

    def test_polish_stock_presence_fallback_is_localized_but_entity_override_wins(self):
        for state, english, polish in (
            ("on", "Home", "Obecność"),
            ("off", "Away", "Brak obecności"),
        ):
            hass, _ = base.environment(
                states=[
                    base.State(
                        "binary_sensor.example", state, {"device_class": "presence"}
                    )
                ]
            )
            resources = {
                f"component.binary_sensor.entity_component.presence.state.{state}": english
            }
            with patch.object(
                base.cards,
                "async_get_cached_translations",
                side_effect=lambda h, l, c: (
                    resources if c == "entity_component" else {}
                ),
            ):
                self.assertEqual(
                    base.cards.presentation_payload(hass, [info()], language="pl")[
                        "cards"
                    ][2]["subtitle"],
                    polish,
                )
                self.assertEqual(
                    base.cards.presentation_payload(hass, [info()], language="en")[
                        "cards"
                    ][2]["subtitle"],
                    english,
                )
            hass.entity_registry.entries["binary_sensor.example"] = SimpleNamespace(
                platform="qa", translation_key="presence"
            )
            specific = {
                f"component.qa.entity.binary_sensor.presence.state.{state}": english
            }
            with patch.object(
                base.cards,
                "async_get_cached_translations",
                side_effect=lambda h, l, c: specific if c == "entity" else resources,
            ):
                self.assertEqual(
                    base.cards.presentation_payload(hass, [info()], language="pl")[
                        "cards"
                    ][2]["subtitle"],
                    english,
                )


if __name__ == "__main__":
    unittest.main()
