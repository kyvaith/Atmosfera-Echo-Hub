# Atmosfera Echo Hub development guide

This file is the mandatory starting point for every change in this repository.
The firmware is a product integration built on a companion ESPHome fork. Read
the documents below before changing runtime behavior:

1. `docs/architecture/README.md`
2. `docs/architecture/decisions.md`
3. The subsystem document relevant to the change
4. `docs/development/extending-ui.md`
5. `docs/development/validation.md`
6. `docs/productization.md` for migration and upstream boundaries

When changing the ESPHome fork, also read its root `AGENTS.md` and follow
upstream ESPHome conventions.

## Source ownership

- This repository owns product configuration, page composition, application
  policy, assets, and Home Assistant integration.
- The ESPHome integration tree owns reusable C++ state machines, display
  transport, acceleration, snapshots, navigation, audio transport, and
  reusable Material widgets.
- Heavy runtime logic must not be added to YAML lambdas. Prefer declarative
  ESPHome actions and reusable components.
- Product YAML may provide policy callbacks, entity IDs, and application
  lifecycle decisions. It must not reimplement component state machines.

## Non-negotiable runtime invariants

### Display

- The validated display path is RGB888, LVGL `DIRECT` with two full-screen
  LVGL buffers, and three display-owned MIPI DSI frame buffers.
- `direct_mode: true` selects `LV_DISPLAY_RENDER_MODE_DIRECT` even when the
  product also sets `full_refresh: true`. Do not assume that combination makes
  LVGL redraw every pixel after a manual framebuffer handoff.
- Never write to a frame buffer that is being scanned out, queued, or staged.
- A manual compositor must acquire an idle frame buffer, complete cache
  synchronization, and present it through the MIPI DSI ownership API.
- Before native LVGL widgets resume after a manual full-screen frame, both LVGL
  buffers must contain that coherent base unless the next owner explicitly
  redraws every display and overlay pixel.
- Pause and drain direct-region workers before page changes, application
  handoff, snapshots, or any operation that changes the base frame.
- Do not enable the generic RGB888 PPA fill/blend draw handlers without a
  hardware test. They have produced short horizontal corruption on ESP32-P4.
- Do not replace a proven hardware path with a CPU copy as a permanent fix for
  an artifact. Find the ownership, stride, alignment, or cache-coherency error.

### Snapshot navigation

- Home uses three reusable raw RGB888 slots for the current page window.
  Off-window pages use JPEG backing and are decoded into a recycled slot.
- Applications keep compressed previews and share one reusable raw work
  buffer. Do not allocate one raw full-screen buffer per application.
- Settings owns a raw scroll snapshot only while Settings is open. Refresh it
  in place after a setting changes and release it when the application closes.
- A new touch during Settings inertia pauses the scroll worker at the last
  presented Y coordinate and continues from that frame. The hidden source tree
  remains hit-testable by its registered geometry while the snapshot is shown.
- Home settle must restore the target through the navigation controller before
  invalidation. A hidden LVGL object cannot be revealed by redraw alone.
- `swipe_start_distance: 0` means first directional pixel; a stationary
  touch-down must remain a tap.
- Defer LVGL press on Home and registered scroll regions until tap-versus-drag
  is known. Replaying one short press/release is valid for a tap; a drag must
  never render a child's pressed style or leave a delayed hover after inertia.
- A touch during Home settle takes over the last presented compositor frame.
  Do not finalize to LVGL or restart from a page origin. Rebase the prepared
  current/next pair only at an exact page boundary.
- New pages, applications, and scroll regions do not become snapshot-aware
  automatically. Register them declaratively as described in
  `docs/development/extending-ui.md`.

### Audio and voice

- Idle mode runs wake-word detection only; expensive AFE/AEC processing stays
  disabled until an active conversation.
- Realtime voice consumes the post-AFE microphone and plays through the
  assistant mixer source.
- Full duplex means simultaneous capture and playback with a playback
  reference supplied to AEC. Do not split this into unrelated RX and TX paths.
- Barge-in must stop or suppress assistant output before reopening listening.
- The amplifier remains muted until codecs and I2S channels are initialized.

### Memory

- Full-screen RGB888 at 800x800 costs 1,920,000 bytes. Treat every additional
  full-screen allocation as an architectural decision.
- Allocate bounded buffers once and reuse them whenever possible.
- Do not keep raw and compressed copies longer than their documented
  lifecycle.
- Large frame caches, gallery images, and application work buffers must have a
  deterministic release point.

### Camera streams

- Normalize RTSP, HLS, and WebRTC through Home Assistant, Frigate, or go2rtc;
  the device camera component consumes MJPEG frames.
- Keep one encoded input buffer and one reusable decoded frame. Drop late
  frames instead of building a latency queue.
- Publish a new image generation only after hardware JPEG decode completes.
- Pause and drain direct presentation before releasing the decoded frame or
  handing display ownership back to navigation.
- Read `docs/architecture/camera-streaming.md` before changing stream,
  presentation, or camera application lifecycle behavior.

## Reusable component rules

- No Atmosfera-specific names, entity IDs, GPIOs, colors, or 800x800
  coordinates in reusable ESPHome components.
- Derive resolution, stride, color format, byte order, and display ownership
  from configured metadata or the active display.
- New behavior-changing or acceleration options default to disabled upstream.
- Do not depend on PlatformIO or SCons-only behavior. The native ESP-IDF build
  is the reference.
- Put compile-time definitions in the component's generated `defines.h` path.
- Diagnostics and profilers default to disabled.
- Preserve existing behavior when moving code. Refactoring and behavioral
  changes belong in separate commits.

## Change workflow

1. Inspect both product YAML and the owning ESPHome component.
2. State which buffer, task, and lifecycle owns the changed data.
3. Make the smallest coherent change.
4. Run configuration validation and focused component tests.
5. Compile the complete firmware.
6. Flash and run the relevant hardware scenarios when runtime behavior changed.
7. Compare FPS, loop time, memory, DSI FIFO diagnostics, audio continuity, and
   visual artifacts with the known-good checkpoint.
8. Update architecture documentation if ownership, buffering, task placement,
   or extension contracts changed.

Never treat a successful compile as proof that display ownership, cache
coherency, audio timing, or touch arbitration is correct.
