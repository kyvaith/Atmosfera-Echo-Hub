"""Check actual ESPHome package merging and page registration without an SDK.

Run with the companion fork on PYTHONPATH. Widget styling/children are omitted
from the focused codegen check; package order and add_pages are real ESPHome.
"""

from __future__ import annotations

import asyncio
import copy
import os
from pathlib import Path
import re
import unittest
from unittest.mock import AsyncMock, patch

from esphome import codegen as cg, config_validation as cv, yaml_util
from esphome.components.lvgl.types import lv_page_t
from esphome.components.lvgl.widgets import page
from esphome.components.packages import do_packages_pass, merge_packages
from esphome.components.substitutions import do_substitution_pass
from esphome.core import CORE

ROOT = Path(os.environ.get("AEH_SOURCE_ROOT", Path(__file__).resolve().parents[2]))
EXPECTED = (
    "controls_page",
    "settings_page",
    "music_page",
    "immich_page",
    "camera_page",
    "light_control_page",
)


def merged_product(enabled: bool, *, old_order: bool = False):
    """Use the real local include/substitution/package pipeline; no validation fetch."""
    CORE.reset()
    CORE.config_path = ROOT / "atmosfera-echo-hub.yaml"
    config = yaml_util.load_yaml(CORE.config_path)
    if old_order:
        packages = config["packages"]
        light_page = packages.pop("lvgl_light_control_page")
        reordered = {}
        for key, value in packages.items():
            if key == "lvgl_tiles_page":
                reordered["lvgl_light_control_page"] = light_page
            reordered[key] = value
        config["packages"] = reordered
    substitutions = {"light_control_product_admitted": str(enabled).lower()}
    config = do_packages_pass(config, command_line_substitutions=substitutions)
    config = do_substitution_pass(config, substitutions)
    return merge_packages(config)


def page_config(config):
    lvgl = config["lvgl"]
    if isinstance(lvgl, list):
        if len(lvgl) != 1:
            raise AssertionError("Expected one product LVGL instance")
        lvgl = lvgl[0]
    return lvgl


def require_startup_order(config):
    ids = tuple(str(item["id"]) for item in page_config(config)["pages"])
    if ids != EXPECTED:
        raise AssertionError(f"Startup page contract violated: {ids!r}")
    return ids


class LightPageOrderTests(unittest.TestCase):
    def test_actual_merged_product_preserves_page_indices_in_both_modes(self):
        for enabled in (False, True):
            with self.subTest(enabled=enabled):
                config = merged_product(enabled)
                self.assertEqual(require_startup_order(config), EXPECTED)
                controls = config["lvgl_material"]["entity_controls"]
                self.assertEqual(cv.boolean(controls[0]["enabled"]), enabled)

    def test_original_bad_include_order_is_detected_after_actual_merge(self):
        config = merged_product(True, old_order=True)
        self.assertEqual(str(page_config(config)["pages"][0]["id"]), "light_control_page")
        with self.assertRaisesRegex(AssertionError, "Startup page contract"):
            require_startup_order(config)

    def test_real_page_codegen_registers_home_first_and_app6_last(self):
        for enabled in (False, True):
            with self.subTest(enabled=enabled):
                merged = merged_product(enabled)
                config = copy.deepcopy(page_config(merged))
                for item in config["pages"]:
                    item["id"] = cv.declare_id(lv_page_t)(str(item["id"]))
                    item.setdefault("skip", False)
                config.setdefault("page_wrap", True)
                statements = []
                with (
                    patch.object(page, "lv_add", side_effect=lambda value: statements.append(str(value))),
                    patch.object(page, "set_obj_properties", new_callable=AsyncMock),
                    patch.object(page, "add_widgets", new_callable=AsyncMock),
                ):
                    asyncio.run(page.add_pages(cg.MockObj("ui_lvgl", "->"), config))
                registered = tuple(
                    re.fullmatch(r"ui_lvgl->add_page\((\w+)\)", value).group(1)
                    for value in statements
                    if "->add_page(" in value
                )
                self.assertEqual(registered, EXPECTED)


if __name__ == "__main__":
    unittest.main()
