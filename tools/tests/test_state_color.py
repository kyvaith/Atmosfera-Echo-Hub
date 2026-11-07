"""Opt-in state colors reuse semantic roles without changing action authority."""

from copy import deepcopy
import json
import unittest

import test_ha_layout as base


class StateColorTests(unittest.TestCase):
    def test_saved_layout_retains_style_through_actual_compatibility_adapter(self):
        doc = base.document(
            [base.card(entity="input_boolean.example", state_color=True)]
        )
        hass, entry = base.environment(
            doc=doc, states=[base.State("input_boolean.example", "off")]
        )
        source = base.cards.entry_layout(entry.options, entry.data)
        normalized = base.cards.normalize_cards(source["cards"])
        self.assertIs(normalized[0]["state_color"], True)
        wire = base.cards.presentation_payload(hass, normalized)["cards"][2]
        self.assertEqual(wire["palette"], "surface")
        self.assertEqual(source, doc)
        normalized[0]["state_color"] = False
        self.assertIs(source["cards"][0]["state_color"], True)

    def test_optional_boolean_roundtrips_without_rewriting_existing_cards(self):
        old = base.document()
        self.assertEqual(base.layout.validate_layout(old), old)
        self.assertNotIn("state_color", base.layout.validate_layout(old)["cards"][0])
        for flag in (False, True):
            doc = base.document([base.card(state_color=flag)])
            result = base.layout.validate_layout(doc)
            self.assertIs(result["cards"][0]["state_color"], flag)
            restored = base.layout.import_layout(base.layout.export_layout(result), 7)
            self.assertEqual(restored, {**result, "revision": 7})
        self.assertEqual(old, base.document())

    def test_flag_requires_boolean_and_enabled_style_requires_known_entity_semantics(
        self,
    ):
        for flag in (1, 0, "true", None, [], {}):
            with self.subTest(flag=flag), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(
                    base.document([base.card(state_color=flag)])
                )
        for entity in (
            "timer.example",
            "sensor.example",
            "cover.example",
            "lock.example",
            "binary_sensor.example",
            "",
        ):
            with (
                self.subTest(entity=entity),
                self.assertRaises(base.layout.LayoutError),
            ):
                base.layout.validate_layout(
                    base.document([base.card(entity=entity, state_color=True)])
                )
        for kind in ("sensor", "action"):
            with self.subTest(kind=kind), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(
                    base.document(
                        [
                            base.card(
                                type=kind, action={"kind": "none"}, state_color=True
                            )
                        ]
                    )
                )

    def test_only_exact_on_uses_selected_role_and_unknown_never_looks_active(self):
        for domain in ("light", "switch", "input_boolean", "fan"):
            for state in ("on", "off", "unknown", "unavailable", "ON", None):
                entity = domain + ".example"
                card = base.card(entity=entity, palette="tertiary", state_color=True)
                hass, _ = base.environment(
                    states=[] if state is None else [base.State(entity, state)]
                )
                before = deepcopy(card)
                wire = base.cards.presentation_payload(hass, [card])["cards"][2]
                self.assertEqual(
                    wire["palette"], "tertiary" if state == "on" else "surface"
                )
                self.assertNotIn("state_color", wire)
                self.assertEqual(card, before)
                self.assertEqual(hass.services.calls, [])

    def test_existing_fixed_palettes_keep_their_pixels_in_every_state(self):
        for state in ("on", "off", "unknown", "unavailable"):
            hass, _ = base.environment(states=[base.State("light.room", state)])
            old = base.card(entity="light.room", palette="secondary")
            fixed = {**old, "state_color": False}
            self.assertEqual(
                base.cards.presentation_payload(hass, [old]),
                base.cards.presentation_payload(hass, [fixed]),
            )

    def test_state_color_keeps_selected_accent_and_matching_foreground_roles(self):
        for accent in ("000000", "FFFFFF", "AEE2FF", "B2E4D0"):
            palette = base.cards.derive_palette(base.cards.normalize_accent(accent))
            for state in ("on", "off"):
                hass, _ = base.environment(
                    states=[base.State("input_boolean.example", state)]
                )
                card = base.card(
                    entity="input_boolean.example", state_color=True, palette="primary"
                )
                wire = base.cards.presentation_payload(hass, [card], accent)["cards"][2]
                self.assertEqual(
                    (wire["background"], wire["foreground"]), palette[wire["palette"]]
                )

    def test_presentation_never_changes_live_toggle_authority_or_data(self):
        entity = "input_boolean.example"
        for state in ("on", "off", "unavailable"):
            hass, _ = base.environment(
                states=[base.State(entity, state)], services=["input_boolean.toggle"]
            )
            card = base.card(entity=entity, state_color=True)
            before = base.cards.resolve_action(hass, card)
            base.cards.presentation_payload(hass, [card])
            self.assertEqual(base.cards.resolve_action(hass, card), before)
            if state == "unavailable":
                self.assertIsNone(before)
            else:
                self.assertEqual(before.data, {"entity_id": entity})
            self.assertEqual(hass.services.calls, [])

    def test_payload_remains_bounded_and_resets_unused_slots_without_new_wire_keys(
        self,
    ):
        cards = [
            base.card(slot=slot, entity="light.room", state_color=True)
            for slot in range(2, 16)
        ]
        hass, _ = base.environment(states=[base.State("light.room", "on")])
        wire = base.cards.presentation_payload(hass, cards)
        self.assertEqual(len(wire["cards"]), 16)
        self.assertEqual(wire["cards"][0], {"slot": 0, "id": "", "visible": False})
        self.assertLess(len(json.dumps(wire).encode()), 8192)
        self.assertNotIn("state_color", json.dumps(wire))


if __name__ == "__main__":
    unittest.main()
