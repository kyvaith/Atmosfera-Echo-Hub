"""Boot admission policy through the real package merge; no hardware claims."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from esphome import yaml_util
from esphome.components.packages import do_packages_pass, merge_packages
from esphome.components.substitutions import do_substitution_pass
from esphome.core import CORE

ROOT = Path(os.environ.get("AEH_SOURCE_ROOT", Path(__file__).resolve().parents[2]))
OVERLAY = os.environ.get("AEH_BOOT_OVERLAY_ROOT")


def merged_product():
    CORE.reset()
    CORE.config_path = ROOT / "atmosfera-echo-hub.yaml"
    config = yaml_util.load_yaml(CORE.config_path)
    # Offline delivery testing uses the unchanged full product entry point and
    # replaces only these real package nodes before ESPHome performs its merge.
    if OVERLAY:
        for name, path in {
            "core": "modules/common/core.yaml",
            "system_settings": "modules/common/system_settings.yaml",
            "audio_hardware": "modules/hardware/audio.yaml",
            "lvgl_boot_page": "modules/lvgl/pages/boot.yaml",
        }.items():
            config["packages"][name] = yaml_util.load_yaml(Path(OVERLAY) / path)
    config = do_packages_pass(config, command_line_substitutions={})
    config = do_substitution_pass(config, {})
    return merge_packages(config)


class BootAudioAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = merged_product()
        cls.boot = next(
            item["then"]
            for item in cls.config["esphome"]["on_boot"]
            if item["priority"] == 600
        )
        cls.scripts = {str(item["id"]): item["then"] for item in cls.config["script"]}

    def test_admission_is_bounded_before_any_animation_preparation(self):
        flag = next(
            item
            for item in self.config["globals"]
            if str(item["id"]) == "boot_animation_admitted"
        )
        self.assertEqual(flag["type"], "bool")
        self.assertFalse(flag["restore_value"])
        self.assertEqual(flag["initial_value"], "false")
        prepare = self.boot.index({"script.execute": "boot_show_esphome_animation"})
        gate = self.boot[prepare - 2]["wait_until"]
        self.assertEqual(gate["timeout"], "8s")
        self.assertIn("is_audio_prepared()", str(gate["condition"]["lambda"]))
        self.assertIn("is_task_ready()", str(gate["condition"]["lambda"]))
        capture = str(self.boot[prepare - 1]["lambda"])
        self.assertIn(
            "id(boot_animation_admitted) = audio_ready && mixer_ready && sendspin_ready",
            capture,
        )
        self.assertEqual(
            sum(
                "id(boot_animation_admitted) = audio_ready" in str(x) for x in self.boot
            ),
            1,
        )

    def test_timeout_cannot_restart_preparation_at_later_show_or_completion(self):
        for name, call in (
            ("boot_show_esphome_animation", "esphome::lvgl::lottie_prepare(ctx);"),
            ("boot_start_esphome_animation", "esphome::lvgl::lottie_show(ctx, true);"),
        ):
            code = str(self.scripts[name][0]["lambda"])
            guard = "if (id(boot_animation_admitted) && id(boot_esphome_animation) != nullptr) {"
            self.assertLess(code.index(guard), code.index(call))
            self.assertEqual(code.count(call), 1)
        prepare = self.boot.index({"script.execute": "boot_show_esphome_animation"})
        for actions, index in (
            (self.boot, prepare + 1),
            (self.scripts["boot_reveal_esphome_wordmark"], 0),
        ):
            code = str(actions[index]["wait_until"]["condition"]["lambda"])
            self.assertIn(
                "if (!id(boot_animation_admitted) || id(boot_esphome_animation) == nullptr) return true;",
                code,
            )

    def test_audio_timeout_does_not_unmute_or_enqueue_chime(self):
        pa = next(
            item["if"]
            for item in self.boot
            if "if" in item
            and {"switch.turn_on": "pa_enable"} in item["if"].get("then", [])
        )
        condition = str(pa["condition"]["lambda"])
        self.assertIn(
            "is_audio_prepared() && id(audio_mixer).is_task_ready()", condition
        )
        self.assertIn({"switch.turn_off": "pa_enable"}, pa["else"])
        self.assertNotIn({"switch.turn_on": "pa_enable"}, self.boot)
        self.assertNotIn({"media_player.unmute": "local_music_player"}, self.boot)
        chime = self.scripts["ui_play_boot_sound"]
        self.assertEqual(len(chime), 1)
        gate = chime[0]["if"]
        self.assertIn(
            "is_audio_prepared() && id(audio_mixer).is_task_ready() && id(pa_enable).state",
            str(gate["condition"]["lambda"]),
        )
        self.assertIn({"speaker.stop": "assistant_speaker"}, gate["then"])
        self.assertFalse(
            any("media_player.play_media" in item for item in gate["else"])
        )
        self.assertFalse(any("is_task_ready" in str(item) for item in gate["then"]))
        self.assertTrue(
            any(
                "id(boot_audio_ready) = id(audio_stack).is_audio_prepared() && id(pa_enable).state;"
                in str(item)
                for item in self.boot
            )
        )

    def test_fallback_keeps_static_wordmark_and_home_handoff(self):
        show = str(self.scripts["boot_show_esphome_animation"][0]["lambda"])
        self.assertLess(
            show.index("lv_obj_set_style_image_recolor(id(boot_esphome_house)"),
            show.index("if (id(boot_animation_admitted)"),
        )
        reveal = self.scripts["boot_reveal_esphome_wordmark"]
        self.assertTrue(
            any("lv_anim_start(&animation);" in str(item) for item in reveal)
        )
        self.assertIn(
            {"script.execute": "boot_reveal_esphome_wordmark"},
            self.scripts["boot_start_esphome_animation"],
        )
        for name in (
            "boot_hide_esphome_animation",
            "boot_finish_esphome_overlay",
            "ui_build_tile_snapshots_now",
            "ui_show_home_content_after_boot",
        ):
            self.assertIn({"script.execute": name}, self.boot)

    def test_actual_predicates_for_all_ready_states(self):
        compiler = os.environ.get("AEH_HOST_CXX")
        if not compiler:
            self.skipTest(
                "Set AEH_HOST_CXX to a C++ compiler (or zig) for the extracted predicate test"
            )
        prepare = self.boot.index({"script.execute": "boot_show_esphome_animation"})
        admission = str(self.boot[prepare - 2]["wait_until"]["condition"]["lambda"])
        chime = str(self.scripts["ui_play_boot_sound"][0]["if"]["condition"]["lambda"])
        code = (
            """#include <cassert>
struct Audio { bool ready; bool is_audio_prepared() const { return ready; } } audio_stack;
struct Mixer { bool ready; bool is_task_ready() const { return ready; } } audio_mixer;
struct Hub { bool running, disabled; bool is_client_running() const { return running; } bool is_disabled() const { return disabled; } } sendspin_hub;
struct Amp { bool state; } pa_enable;
#define id(x) x
bool admission() { """
            + admission
            + """ }
bool chime() { """
            + chime
            + """ }
int main() {
  for (int mask = 0; mask < 32; ++mask) {
    audio_stack.ready = mask & 1; audio_mixer.ready = mask & 2;
    sendspin_hub.running = mask & 4; sendspin_hub.disabled = mask & 8;
    pa_enable.state = mask & 16;
    assert(admission() == (bool(mask & 1) && bool(mask & 2) && bool(mask & 12)));
    assert(chime() == (bool(mask & 1) && bool(mask & 2) && bool(mask & 16)));
  }
}
"""
        )
        with tempfile.TemporaryDirectory(prefix="aeh-boot-admission-") as directory:
            source = Path(directory) / "predicates.cpp"
            binary = Path(directory) / "predicates.exe"
            source.write_text(code, encoding="utf8")
            command = [compiler]
            if Path(compiler).stem.lower() == "zig":
                command.append("c++")
            subprocess.run(
                command + ["-std=c++17", str(source), "-o", str(binary)],
                check=True,
                capture_output=True,
                timeout=60,
            )
            subprocess.run([str(binary)], check=True, capture_output=True, timeout=10)


if __name__ == "__main__":
    unittest.main()
