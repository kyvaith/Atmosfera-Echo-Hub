"""HA icon keys must be drawable in every registered native tile icon font.

Source-only regression: no HA import, ESPHome build, device or renderer claim.
An isolated proposal can use AEH_SOURCE_ROOT and AEH_FONT_CATALOG; once copied
into the product tree the defaults inspect the actual product sources.
"""

from __future__ import annotations

import ast
import os
import unittest
from pathlib import Path

import yaml

ROOT = Path(os.environ.get("AEH_SOURCE_ROOT", Path(__file__).resolve().parents[2]))
FONT_CATALOG = Path(
    os.environ.get("AEH_FONT_CATALOG", ROOT / "modules/lvgl/fonts.yaml")
)


class ProductLoader(yaml.SafeLoader):
    """Read metadata without executing ESPHome lambdas or importing HA."""


ProductLoader.add_multi_constructor(
    "!", lambda loader, _tag, node: loader.construct_scalar(node)
)


def load(path: Path):
    return yaml.load(path.read_text(encoding="utf-8"), Loader=ProductLoader)


def icon_catalog(path: Path) -> dict[str, str]:
    """Read the literal public catalogue without loading integration imports."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    assignments = [
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "ICONS"
            for target in node.targets
        )
    ]
    if len(assignments) != 1:
        raise ValueError("Expected exactly one literal ICONS assignment")
    return ast.literal_eval(assignments[0])


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


def glyphs(font):
    value = font.get("glyphs", [])
    return set(value if isinstance(value, str) else "".join(value))


def missing_icons(icons, fonts):
    return {
        (font_id, key): f"U+{ord(character):04X}"
        for font_id, font in fonts.items()
        for key, character in icons.items()
        if character not in glyphs(font)
    }


class TileIconCatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.icons = icon_catalog(ROOT / "custom_components/atmosfera_echo_hub/cards.py")
        cls.widgets = object_index(load(ROOT / "modules/lvgl/pages/tiles_m3.yaml"))
        cls.bindings = load(ROOT / "modules/lvgl/material.yaml")["lvgl_material"][
            "tile_surfaces"
        ][0]["tiles"]
        cls.fonts = {font["id"]: font for font in load(FONT_CATALOG)["font"]}
        cls.used_fonts = {
            cls.widgets[binding["icon_label"]]["text_font"] for binding in cls.bindings
        }

    def test_registered_icon_labels_resolve_to_the_shared_material_fonts(self):
        # Include hidden sensor/clock labels and reserved bindings: copies may
        # place any accepted catalogue icon into another editable physical slot.
        self.assertEqual({item["slot"] for item in self.bindings}, set(range(16)))
        self.assertEqual(len(self.bindings), 16)
        self.assertEqual(len({item["icon_label"] for item in self.bindings}), 16)
        self.assertEqual(
            self.used_fonts,
            {"material_symbols_36", "material_symbols_44", "material_symbols_68"},
        )
        for binding in self.bindings:
            with self.subTest(slot=binding["slot"]):
                font = self.fonts[self.widgets[binding["icon_label"]]["text_font"]]
                self.assertEqual(font["file"], "gfonts://Material+Symbols+Rounded")

    def test_catalogue_values_are_single_unicode_codepoints(self):
        self.assertTrue(self.icons)
        for key, character in self.icons.items():
            with self.subTest(icon=key):
                self.assertIsInstance(key, str)
                self.assertTrue(key)
                self.assertIsInstance(character, str)
                self.assertEqual(len(character), 1)
                self.assertGreater(ord(character), 0)

    def test_every_catalogue_key_is_in_every_registered_font_subset(self):
        # Deliberately checks all keys, including keys sharing a codepoint. This
        # catches a new catalogue entry even with ignore_missing_glyphs:true.
        for font_id in sorted(self.used_fonts):
            for key, character in self.icons.items():
                with self.subTest(
                    font=font_id, icon=key, codepoint=f"U+{ord(character):04X}"
                ):
                    self.assertIn(character, glyphs(self.fonts[font_id]))

    def test_missing_catalogue_glyph_cannot_be_hidden_by_ignore_missing(self):
        # Demonstrate detection against each of the five formerly missing pairs.
        for font_id, key in (
            ("material_symbols_36", "clock"),
            ("material_symbols_44", "clock"),
            ("material_symbols_68", "door"),
            ("material_symbols_68", "presence"),
            ("material_symbols_68", "clock"),
        ):
            with self.subTest(font=font_id, icon=key):
                font = dict(self.fonts[font_id])
                font["glyphs"] = sorted(glyphs(font) - {self.icons[key]})
                self.assertTrue(font["ignore_missing_glyphs"])
                self.assertIn(
                    (font_id, key), missing_icons(self.icons, {font_id: font})
                )

    def test_cached_ttf_contains_real_catalogue_glyphs_when_available(self):
        try:
            import freetype
        except ImportError:
            self.skipTest("Optional local FreeType verification unavailable")
        path = ROOT / ".esphome/font/Material+Symbols+Rounded@400@False@v1.ttf"
        if not path.is_file():
            self.skipTest("Optional local Material Symbols TTF cache unavailable")
        face = freetype.Face(str(path))
        for font_id in sorted(self.used_fonts):
            font = self.fonts[font_id]
            face.set_pixel_sizes(0, font["size"])
            line_height = face.size.height // 64
            for key, character in self.icons.items():
                with self.subTest(font=font_id, icon=key):
                    self.assertNotEqual(face.get_char_index(ord(character)), 0)
                    face.load_char(character)
                    self.assertGreater(face.glyph.bitmap.width, 0)
                    self.assertGreater(face.glyph.bitmap.rows, 0)
                    top = face.size.ascender // 64 - face.glyph.bitmap_top
                    self.assertGreaterEqual(top, 0)
                    self.assertLessEqual(top + face.glyph.bitmap.rows, line_height)
                    self.assertLessEqual(face.glyph.advance.x // 64, font["size"])


if __name__ == "__main__":
    unittest.main()
