"""Product Settings Auto-Home metadata and actual policy host checks; no SDK/device."""
from __future__ import annotations

import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
HARNESS = Path(__file__).with_name("settings_auto_home_policy.cpp.in")


class ProductLoader(yaml.SafeLoader):
    """Read declarative source without running ESPHome tags or includes."""


ProductLoader.add_multi_constructor(
    "!", lambda loader, _tag, node: loader.construct_scalar(node)
)


def load(name):
    return yaml.load((ROOT / name).read_text(encoding="utf-8"), Loader=ProductLoader)


def by_id(node, target):
    if isinstance(node, dict):
        if node.get("id") == target:
            return node
        for child in node.values():
            if (result := by_id(child, target)) is not None:
                return result
    elif isinstance(node, list):
        for child in node:
            if (result := by_id(child, target)) is not None:
                return result
    return None


def actual_policy():
    settings = load("modules/common/system_settings.yaml")
    policies = [item["lambda"] for interval in settings["interval"] for item in interval["then"]
                if isinstance(item, dict) and "settings_auto_home_timeout" in item.get("lambda", "")]
    if len(policies) != 1:
        raise AssertionError("Exactly one existing-interval Auto-Home policy required")
    return policies[0]


def compiler_command():
    """Same explicit compiler convention as companion host tests; never install tools."""
    if compiler := os.environ.get("ESPHOME_TEST_CXX"):
        if not Path(compiler).is_file() and shutil.which(compiler) is None:
            raise AssertionError("ESPHOME_TEST_CXX does not identify an available compiler")
        return [compiler, *shlex.split(os.environ.get("ESPHOME_TEST_CXX_ARGS", ""))]
    if compiler := shutil.which("c++") or shutil.which("g++") or shutil.which("clang++"):
        return [compiler]
    return None


class SettingsAutoHomeTests(unittest.TestCase):
    def test_default_off_bounded_restore_setting_reuses_existing_tick(self):
        settings = load("modules/common/system_settings.yaml")
        self.assertEqual(1, len(settings["interval"]))
        self.assertEqual("1s", settings["interval"][0]["interval"])
        # Existing independent display sleep still precedes Auto-Home.
        self.assertIn("settings_display_timeout", str(settings["interval"][0]["then"][0]))
        number = by_id(settings["number"], "settings_auto_home_timeout")
        for key, value in (("platform", "template"), ("update_interval", "never"),
                           ("min_value", 0), ("max_value", 300), ("step", 30),
                           ("initial_value", 0), ("optimistic", True), ("restore_value", True)):
            self.assertEqual(value, number[key], key)
        self.assertEqual([{"script.execute": "ui_update_settings_auto_home_state"}], number["on_value"])

    def test_local_cycle_translation_and_snapshot_refresh_share_setting(self):
        row = by_id(load("modules/lvgl/pages/settings.yaml"), "settings_auto_home_button")
        self.assertEqual([{"number.increment": {"id": "settings_auto_home_timeout", "cycle": True}}], row["on_click"]["then"])
        for target in ("settings_auto_home_label", "settings_auto_home_value"):
            self.assertEqual("CLIP", by_id(row, target)["long_mode"])
        for language in ("en-US", "pl-PL"):
            text = load(f"translations/{language}.yaml")["settings.auto_home"]
            self.assertTrue(text.strip())
            self.assertNotIn("\ufffd", text)
        i18n = (ROOT / "modules/lvgl/i18n.yaml").read_text(encoding="utf-8")
        self.assertIn('translate("settings.auto_home")', i18n)
        pressed = by_id(load("modules/lvgl/material.yaml"), "shared_pressed_feedback")
        self.assertEqual(1, pressed["widgets"].count("settings_auto_home_button"))
        scripts = load("modules/lvgl/navigation.yaml")
        update = by_id(scripts, "ui_update_settings_auto_home_state")
        self.assertEqual({"script.execute": "ui_refresh_settings_snapshot"}, update["then"][-1])
        self.assertIn({"script.wait": "ui_update_settings_auto_home_state"}, by_id(scripts, "ui_apply_settings_state")["then"])

    def test_policy_has_no_forced_page_wake_or_pending_fallback(self):
        policy = actual_policy()
        self.assertEqual(1, policy.count("try_show_home()"))
        self.assertTrue(policy.rstrip().endswith("if (!id(ui_navigation).try_show_home()) return;"))
        for forbidden in ("ui_home_page", "ui_page", "display_wake", "lv_scr_load", "new ",
                          "set_timeout", "globals.set", "mark_slots_ready"):
            self.assertNotIn(forbidden, policy)

    def test_actual_policy_deadlines_inertia_touch_and_refused_nav(self):
        if (compiler := compiler_command()) is None:
            self.skipTest("A C++17 host compiler is required; set ESPHOME_TEST_CXX/ARGS if needed")
        template = HARNESS.read_text(encoding="utf-8")
        self.assertEqual(1, template.count("// INSERT_ACTUAL_PRODUCT_POLICY"))
        with tempfile.TemporaryDirectory(prefix="settings-auto-home-host-") as directory:
            root = Path(directory)
            source = root / "policy.cpp"
            source.write_text(template.replace("// INSERT_ACTUAL_PRODUCT_POLICY", actual_policy()), encoding="utf-8")
            executable = root / ("policy.exe" if os.name == "nt" else "policy")
            result = subprocess.run([*compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(executable)],
                                    capture_output=True, text=True, timeout=60, check=False)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10, check=False)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("policy cases: 54", result.stdout)


if __name__ == "__main__":
    unittest.main()
