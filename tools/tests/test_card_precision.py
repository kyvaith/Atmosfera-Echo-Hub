"""Per-card decimal overrides, shared golden text, and the real normalization path."""

from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import test_ha_layout as base


def info(**updates):
    return base.card(
        entity="sensor.example", type="sensor", action={"kind": "none"}, **updates
    )


class CardPrecisionTests(unittest.TestCase):
    def test_strict_optional_zero_to_six_and_export_recovery(self):
        old = base.document([info()])
        self.assertEqual(base.layout.validate_layout(old), old)
        for precision in range(7):
            doc = base.document([info(display_precision=precision)])
            self.assertEqual(base.layout.validate_layout(doc), doc)
            self.assertEqual(
                base.layout.import_layout(base.layout.export_layout(doc), 8),
                {**doc, "revision": 8},
            )
        for value in (True, False, None, -1, 7, 1.5, 2.0, "2", [], {}):
            with self.subTest(value=value), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(
                    base.document([info(display_precision=value)])
                )

    def test_only_numeric_information_domains_admit_override(self):
        for entity in ("sensor.example", "number.example", "input_number.example"):
            card = info(display_precision=0)
            card["entity_id"] = entity
            self.assertEqual(
                base.layout.validate_layout(base.document([card]))["cards"][0][
                    "display_precision"
                ],
                0,
            )
        for entity, kind in (
            ("sensor.example", "entity"),
            ("timer.example", "sensor"),
            ("binary_sensor.example", "sensor"),
            ("light.example", "entity"),
        ):
            card = info(display_precision=0)
            card.update(entity_id=entity, type=kind)
            with (
                self.subTest(entity=entity, kind=kind),
                self.assertRaises(base.layout.LayoutError),
            ):
                base.layout.validate_layout(base.document([card]))

    def test_golden_numeric_text_in_both_languages_through_saved_adapter(self):
        cases = json.loads(
            (Path(__file__).parent / "fixtures/card_precision.json").read_text(
                encoding="utf-8"
            )
        )
        for case in cases:
            for language in ("pl", "en"):
                with self.subTest(case=case, language=language):
                    doc = base.document([info(display_precision=case["precision"])])
                    hass, entry = base.environment(
                        doc=doc,
                        states=[
                            base.State(
                                "sensor.example",
                                case["state"],
                                {"unit_of_measurement": case["unit"]},
                            )
                        ],
                    )
                    normalized = base.cards.normalize_cards(
                        base.cards.entry_layout(entry.options, entry.data)["cards"]
                    )
                    wire = base.cards.presentation_payload(
                        hass, normalized, language=language
                    )["cards"][2]
                    self.assertEqual(wire["subtitle"], case[language])
                    self.assertNotIn("display_precision", wire)
                    self.assertEqual(hass.services.calls, [])

    def test_override_is_per_card_not_registry_entity_or_other_card(self):
        options = {"sensor": {"display_precision": 4, "suggested_display_precision": 5}}
        state = base.State("sensor.example", "12.3456", {"unit_of_measurement": "°C"})
        hass, _ = base.environment(states=[state])
        hass.entity_registry.entries["sensor.example"] = SimpleNamespace(
            options=options
        )
        cards = [
            info(slot=2, display_precision=0),
            info(slot=3, display_precision=2),
            info(slot=4),
        ]
        before = deepcopy((options, state.attributes, cards))
        wire = base.cards.presentation_payload(hass, cards)["cards"]
        self.assertEqual(
            [wire[s]["subtitle"] for s in (2, 3, 4)],
            ["12 °C", "12.35 °C", "12.3456 °C"],
        )
        self.assertEqual((options, state.attributes, cards), before)

    def test_dates_enum_and_duration_keep_existing_semantics(self):
        for device_class, value, unit in (
            ("timestamp", "2026-10-30T12:00:00+00:00", ""),
            ("enum", "warm", ""),
            ("duration", "90.5", "s"),
        ):
            hass, _ = base.environment(
                states=[
                    base.State(
                        "sensor.example",
                        value,
                        {"device_class": device_class, "unit_of_measurement": unit},
                    )
                ]
            )
            old = base.cards.presentation_payload(hass, [info()])
            self.assertEqual(
                base.cards.presentation_payload(hass, [info(display_precision=0)]), old
            )

    def test_unknown_unavailable_and_malformed_data_never_become_zero(self):
        for value, label in (
            ("unknown", "Unknown"),
            ("unavailable", "Unavailable"),
            ("NaN", "Unknown"),
            ("12x", "Unknown"),
        ):
            hass, _ = base.environment(
                states=[
                    base.State("sensor.example", value, {"unit_of_measurement": "W"})
                ]
            )
            self.assertEqual(
                base.cards.presentation_payload(hass, [info(display_precision=0)])[
                    "cards"
                ][2]["subtitle"],
                label,
            )
        hass, _ = base.environment()
        self.assertEqual(
            base.cards.presentation_payload(hass, [info(display_precision=6)])["cards"][
                2
            ]["subtitle"],
            "Unavailable",
        )


if __name__ == "__main__":
    unittest.main()
