"""Compile the actual physical-header policy, separately from synthetic LVGL input."""

from pathlib import Path
import os
import shlex
import subprocess
import tempfile
import textwrap
import unittest


PRODUCT = Path(__file__).resolve().parents[2]


def block(source, marker):
    start = source.index(marker)
    opening = source.index("{", start)
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]


class NotificationPhysicalHeaderPolicyTests(unittest.TestCase):
    def test_pull_hold_release_and_modal_ownership(self):
        if not (compiler := os.environ.get("ESPHOME_TEST_CXX")):
            self.skipTest("ESPHOME_TEST_CXX is required for compiled product policy")
        source = (PRODUCT / "modules/hardware/touchscreen.yaml").read_text(
            encoding="utf8"
        )
        begin = source.split(
            "            id(global_volume_time_press_tracking) = false;\n", 1
        )[1]
        begin = begin.split(
            "            id(media_transport_touch_tracking) = false;", 1
        )[0]
        begin = "global_volume_time_press_tracking = false;\n" + textwrap.dedent(begin)
        update = block(
            source.split("    on_update:", 1)[1],
            "if (id(global_volume_time_press_tracking))",
        )
        release = block(
            source.split("    on_release:", 1)[1],
            "if (id(global_volume_time_press_tracking))",
        )
        runtime = (PRODUCT / "modules/player/runtime.yaml").read_text(encoding="utf8")
        guard = runtime.split("  - id: global_volume_long_press_guard\n", 1)[1].split(
            "  - id:", 1
        )[0]
        predicate = textwrap.dedent(
            guard.split("            lambda: |-\n", 1)[1].split("          then:", 1)[0]
        )
        # The physical driver's dispatch order is the missing boundary in the
        # former synthetic-only tests: update listeners run before on_touch.
        fork = os.environ.get("ESPHOME_TEST_FORK_SOURCE")
        if fork:
            transport = (
                Path(fork) / "esphome/components/touchscreen/touchscreen.cpp"
            ).read_text()
            dispatch = block(transport, "void Touchscreen::send_touches_()")
            self.assertLess(
                dispatch.index("listener->update(touches)"),
                dispatch.index("this->touch_trigger_.trigger("),
            )
        harness = r"""
#include <cassert>
#include <cstdlib>
#define id(name) name
static unsigned now;
static unsigned millis() { return now; }
struct Script { unsigned executions{}, stops{}; void execute() { ++executions; } void stop() { ++stops; } };
struct Navigation { unsigned captures{}; bool is_application_open(int) const { return false; }
  void set_external_touch_capture(bool value) { captures += value; } };
struct Center { bool owned{}; bool owns_scene() const { return owned; } };
struct Renderer { unsigned preparations{}, cancellations{}; void prepare() { ++preparations; }
  void cancel_prepare() { ++cancellations; } void set_activation_widget_was_visible(bool) {} };
struct Backlight { struct Value { bool is_on() const { return true; } } current_values; };
static void lv_indev_reset(void *, void *) {}
struct Header {
  bool boot_sequence_done{true}, ui_snapshot_io_busy{}, ui_light_preparation_owned{};
  bool global_volume_time_press_tracking{}, global_volume_dragging{}, global_volume_activation_suppressed{};
  unsigned global_volume_time_press_start_ms{}, ui_touch_click_block_until_ms{};
  int global_volume_time_press_start_x{}, global_volume_time_press_start_y{}, light_control_application{};
  Backlight display_backlight;
  Navigation ui_navigation;
  Center notification_center;
  Renderer global_volume_renderer;
  Script global_volume_long_press_guard, global_volume_release_touch_capture, global_volume_begin_drag;
  struct Point { int x, y; };
  void begin(Point touch) { BEGIN }
  void update(Point touch) { UPDATE }
  void release() { RELEASE }
  bool can_hold() { PREDICATE }
};
int main() {
  // Listener claims a candidate; the following physical on_touch must not
  // cancel it or acquire display resources before motion classification.
  Header pull; now = 0; pull.begin({410, 11});
  assert(pull.global_volume_time_press_tracking);
  assert(pull.ui_navigation.captures == 0 && pull.global_volume_renderer.preparations == 0);
  now = 269; pull.update({425, 299});
  assert(!pull.can_hold() && !pull.global_volume_time_press_tracking);
  assert(pull.global_volume_release_touch_capture.executions == 0);
  Header hold; now = 0; hold.begin({400, 12}); now = 249; hold.update({405, 17});
  assert(hold.global_volume_begin_drag.executions == 0);
  now = 250; hold.update({405, 17}); assert(hold.global_volume_begin_drag.executions == 1);
  Header tap; now = 0; tap.begin({400, 12}); now = 80; tap.release();
  assert(!tap.can_hold() && tap.ui_navigation.captures == 0);
  assert(tap.global_volume_release_touch_capture.executions == 0);
  Header modal; modal.notification_center.owned = true; modal.begin({400, 12});
  assert(!modal.global_volume_time_press_tracking && modal.ui_navigation.captures == 0);
  Header arriving; now = 0; arriving.begin({400, 12});
  arriving.notification_center.owned = true; now = 250;
  assert(!arriving.can_hold()); arriving.update({400, 12});
  assert(!arriving.global_volume_time_press_tracking && arriving.global_volume_begin_drag.executions == 0);
  Header sideways; now = 0; sideways.begin({400, 12}); now = 40; sideways.update({422, 13});
  assert(!sideways.can_hold());
}
"""
        for token, code in (
            ("BEGIN", begin),
            ("UPDATE", update),
            ("RELEASE", release),
            ("PREDICATE", predicate),
        ):
            harness = harness.replace(token, code)
        with tempfile.TemporaryDirectory(prefix="notification-header-") as folder:
            root = Path(folder)
            cpp, exe = root / "policy.cpp", root / "policy.exe"
            cpp.write_text(harness, encoding="utf8")
            command = [
                compiler,
                *shlex.split(os.environ.get("ESPHOME_TEST_CXX_ARGS", "")),
                "-std=c++20",
                "-UNDEBUG",
                str(cpp),
                "-o",
                str(exe),
            ]
            built = subprocess.run(command, capture_output=True, text=True, timeout=90)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
