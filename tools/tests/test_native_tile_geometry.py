"""Static native-card bounds; this does not render LVGL or exercise a device."""

from __future__ import annotations

from pathlib import Path
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]

# Font line heights measured from the shared TTFs with FreeType and matched to
# the generated v7 font::Font(..., baseline, height, ...) constructors. A font
# change must remeasure these bounds; point size alone is not its line height.
FONT_METRICS = {
    "roboto_16": (16, 400, 19),
    "roboto_18": (18, 400, 21),
    "roboto_20": (20, 500, 23),
    "roboto_24": (24, 500, 28),
    "roboto_30": (30, 500, 35),
    "roboto_34": (34, 500, 40),
    "material_symbols_36": (36, 400, 43),
    "material_symbols_44": (44, 400, 53),
    "material_symbols_68": (68, 400, 82),
}

# Approved native hit geometry, including the two retained hidden bindings.
CARD_RECTS = {
    0: (75, 454, 310, 128),
    1: (415, 454, 310, 128),
    2: (55, 176, 220, 248),
    3: (290, 176, 220, 248),
    4: (525, 176, 220, 248),
    5: (94, 462, 296, 116),
    6: (60, 168, 210, 190),
    7: (295, 168, 210, 190),
    8: (58, 392, 216, 116),
    9: (292, 392, 216, 116),
    10: (526, 392, 216, 116),
    11: (410, 462, 296, 116),
    12: (180, 606, 440, 76),
    13: (112, 548, 276, 112),
    14: (412, 548, 276, 112),
    15: (530, 168, 210, 190),
}


class ProductLoader(yaml.SafeLoader):
    """Read declarative metadata without executing ESPHome tags/lambdas."""


ProductLoader.add_multi_constructor(
    "!", lambda loader, _tag, node: loader.construct_scalar(node)
)


def load(path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=ProductLoader)


def object_index(node, result=None):
    if result is None:
        result = {}
    if isinstance(node, dict):
        if "id" in node:
            if node["id"] in result:
                raise ValueError(f"Duplicate widget {node['id']}")
            result[node["id"]] = node
        for value in node.values():
            object_index(value, result)
    elif isinstance(node, list):
        for value in node:
            object_index(value, result)
    return result


def local_rect(label, card):
    font = label["text_font"]
    point_size, _, line_height = FONT_METRICS[font]
    width = label.get("width", point_size)
    height = label.get("height", line_height)
    x, y = label.get("x", 0), label.get("y", 0)
    align = label.get("align")
    if align in ("TOP_MID", "BOTTOM_MID"):
        x += (card["width"] - width) / 2
    if align == "BOTTOM_MID":
        y += card["height"] - height
    if align == "LEFT_MID":
        y += (card["height"] - height) / 2
    return x, y, width, height


def separation(first, second):
    x, y, width, height = first
    other_x, other_y, other_width, other_height = second
    return max(
        other_x - x - width,
        x - other_x - other_width,
        other_y - y - height,
        y - other_y - other_height,
    )


def inside_rounded_card(x, y, width, height, radius):
    if not 0 <= x < width or not 0 <= y < height:
        return False
    center_x = min(max(x, radius), width - radius)
    center_y = min(max(y, radius), height - radius)
    return (x - center_x) ** 2 + (y - center_y) ** 2 <= radius**2


class NativeTileGeometryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.widgets = object_index(load(ROOT / "modules/lvgl/pages/tiles_m3.yaml"))
        cls.bindings = load(ROOT / "modules/lvgl/material.yaml")["lvgl_material"][
            "tile_surfaces"
        ][0]["tiles"]
        cls.styles = {
            item["id"]: item
            for item in load(ROOT / "modules/lvgl/base.yaml")["lvgl"][
                "style_definitions"
            ]
        }
        cls.fonts = {
            item["id"]: item
            for item in load(ROOT / "modules/lvgl/fonts.yaml")["font"]
        }

    def test_all_16_bindings_keep_approved_native_hit_geometry(self):
        self.assertEqual({binding["slot"] for binding in self.bindings}, set(range(16)))
        self.assertEqual(len(self.bindings), 16)
        for binding in self.bindings:
            with self.subTest(slot=binding["slot"]):
                card = self.widgets[binding["widget"]]
                self.assertEqual(
                    tuple(card[key] for key in ("x", "y", "width", "height")),
                    CARD_RECTS[binding["slot"]],
                )
                self.assertEqual(
                    binding.get("always_hidden", False), binding["slot"] in (0, 1)
                )
                if binding["slot"] in (0, 1):
                    self.assertTrue(card["hidden"])

    def test_all_32_managed_text_labels_have_one_line_clip_bands(self):
        labels = set()
        for binding in self.bindings:
            for role in ("title_label", "subtitle_label"):
                label_id = binding[role]
                labels.add(label_id)
                with self.subTest(slot=binding["slot"], role=role):
                    label = self.widgets[label_id]
                    line_height = FONT_METRICS[label["text_font"]][2]
                    self.assertGreater(label["width"], 0)
                    self.assertGreaterEqual(label["height"], line_height)
                    self.assertLess(label["height"], 2 * line_height)
                    # LVGL DOT modifies lv_label_get_text(), which native
                    # comparison/readback uses. CLIP retains the full value.
                    self.assertEqual(label["long_mode"], "CLIP")
        self.assertEqual(len(labels), 32)

    def test_title_and_state_bands_are_separate_for_every_binding(self):
        for binding in self.bindings:
            with self.subTest(slot=binding["slot"]):
                card = self.widgets[binding["widget"]]
                title = local_rect(self.widgets[binding["title_label"]], card)
                state = local_rect(self.widgets[binding["subtitle_label"]], card)
                self.assertGreaterEqual(separation(title, state), 3)

    def test_visible_icons_have_a_gap_from_both_text_bands(self):
        for binding in self.bindings:
            card = self.widgets[binding["widget"]]
            icon = self.widgets[binding["icon_label"]]
            if icon.get("hidden"):
                continue
            for role in ("title_label", "subtitle_label"):
                with self.subTest(slot=binding["slot"], role=role):
                    self.assertGreaterEqual(
                        separation(
                            local_rect(icon, card),
                            local_rect(self.widgets[binding[role]], card),
                        ),
                        4,
                    )

    def test_entire_text_bands_stay_inside_curved_surface(self):
        for binding in self.bindings:
            card = self.widgets[binding["widget"]]
            style = self.styles[card["styles"]]
            self.assertEqual(style["pad_all"], 0)
            radius = min(
                card.get("radius", style["radius"]),
                card["width"] / 2,
                card["height"] / 2,
            )
            for role in ("title_label", "subtitle_label"):
                with self.subTest(slot=binding["slot"], role=role):
                    x, y, width, height = local_rect(self.widgets[binding[role]], card)
                    for corner_x in (x, x + width - 1):
                        for corner_y in (y, y + height - 1):
                            self.assertTrue(
                                inside_rounded_card(
                                    corner_x,
                                    corner_y,
                                    card["width"],
                                    card["height"],
                                    radius,
                                ),
                                f"Text corner {(corner_x, corner_y)} outside card",
                            )

    def test_metrics_follow_the_shared_product_fonts(self):
        for font_id, (size, weight, _height) in FONT_METRICS.items():
            with self.subTest(font=font_id):
                font = self.fonts[font_id]
                self.assertEqual(font["size"], size)
                if isinstance(font["file"], dict):
                    self.assertEqual(font["file"]["weight"], weight)
                else:
                    self.assertEqual(font["file"], "gfonts://Material+Symbols+Rounded")

    def test_cached_freetype_metrics_and_long_pl_en_inputs_when_available(self):
        try:
            import freetype
        except ImportError:
            self.skipTest("Optional FreeType/cache verification unavailable")
        faces = {}
        for font_id, (size, weight, height) in FONT_METRICS.items():
            family = "Roboto" if font_id.startswith("roboto") else "Material+Symbols+Rounded"
            path = ROOT / ".esphome/font" / f"{family}@{weight}@False@v1.ttf"
            if not path.is_file():
                self.skipTest("Optional local font cache unavailable")
            face = freetype.Face(str(path))
            face.set_pixel_sizes(0, size)
            self.assertEqual(face.size.height // 64, height, font_id)
            faces[font_id] = face
            characters = (
                self.fonts[font_id]["glyphs"]
                if font_id.startswith("material_symbols")
                else "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                "ĄĆĘŁŃÓŚŹŻąćęłńóśźż0123456789_.,:;+/-°%—"
            )
            for character in characters:
                face.load_char(character)
                top = face.size.ascender // 64 - face.glyph.bitmap_top
                self.assertGreaterEqual(top, 0, (font_id, character))
                self.assertLessEqual(
                    top + face.glyph.bitmap.rows, height, (font_id, character)
                )
                if font_id.startswith("material_symbols"):
                    self.assertLessEqual(face.glyph.advance.x // 64, size)
        samples = [
            ("Zażółć gęślą jaźń — długi tytuł pokoju " * 2)[:40],
            ("Living room blinds and reading lamp " * 2)[:40],
            "2026-10-24T20:30:00+00:00",
            "W" * 40,
        ]
        self.assertEqual([len(value) for value in samples[:2]], [40, 40])
        for binding in self.bindings:
            for role, inputs in (
                ("title_label", [*samples[:2], samples[3]]),
                ("subtitle_label", samples),
            ):
                label = self.widgets[binding[role]]
                face = faces[label["text_font"]]
                widths = []
                for sample in inputs:
                    width = 0
                    for character in sample:
                        self.assertNotEqual(face.get_char_index(ord(character)), 0)
                        face.load_char(character)
                        width += face.glyph.advance.x // 64
                    widths.append(width)
                # The fixtures really overflow; fixed height + CLIP must handle
                # them. This is font/geometry evidence, not a rendering claim.
                self.assertGreater(max(widths), label["width"])


if __name__ == "__main__":
    unittest.main()
