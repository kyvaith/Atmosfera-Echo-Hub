# Atmosfera Echo Hub development

Use this skill for firmware, LVGL, display, audio, navigation, and UI work in
this repository.

## Read first

1. Read the repository `AGENTS.md`.
2. Read the relevant files under `docs/architecture/`.
3. For changes in the ESPHome fork, also follow
   `C:/Users/kyvai/.codex/skills/esphome-upstream/SKILL.md` and the fork's
   `AGENTS.md`.

## Runtime invariants

- Preserve the RGB888 MIPI DSI triple-buffer ownership contract.
- The effective LVGL mode is `DIRECT`; `full_refresh: true` does not change it
  to `LV_DISPLAY_RENDER_MODE_FULL` when `direct_mode: true` is set.
- Pause and drain direct-region workers before changing the visible base.
- Seed both LVGL buffers after a manual full-screen frame before native widgets
  resume, unless the next owner guarantees a complete screen and overlay redraw.
- For native `DIRECT` frames, never synchronize dirty regions into the other
  LVGL buffer before DSI confirms the frame boundary. Accumulate bounded dirty
  rectangles and copy them only into the now-idle buffer.
- Keep full-screen allocations bounded and document their lifecycle.
- Do not trade artifacts for permanent CPU copies or reduced global bandwidth.
- Route gesture velocity once in the shared gesture router. Home settle and
  Settings inertia consume that release velocity; do not add a second filtered
  estimator in an individual view.
- Keep a Home tile slot unaddressable while its background worker is encoding
  or decoding it. Publish the new page-to-slot mapping only after the complete
  operation and cache synchronization succeed; invalidate a partially written
  slot on failure.
- The normal Home gesture-start path may bind prepared raw slots only. Do not
  expose, align, lay out, or freshly snapshot live LVGL page trees there; that
  work is fallback-only and otherwise turns the first movement into a visible
  full-screen hitch.
- Create the swipe and JPEG-prefetch workers during Home preparation. At settle,
  keep the exact final snapshot visible and finish prefetch asynchronously
  rather than waiting in the LVGL loop.
- At the final Home handoff, restore visibility through `LvglNavigation`, centre
  the target widget, and only then invalidate it. An invalidate call cannot
  reveal an object that still carries `LV_OBJ_FLAG_HIDDEN`.
- A navigation `swipe_start_distance` of zero captures on the first directional
  coordinate change. It must still use axis selection so touch-down alone
  remains available to click handling.
- Withhold native LVGL press on Home and registered scroll regions until
  tap-versus-drag is known. A tap gets one synthetic press/release for feedback
  and click handling; a drag must not enter `LV_STATE_PRESSED`, invalidate the
  child at gesture start, or replay hover after inertia.
- If Home settle is active, pause the worker at the last presented frame and
  continue from that visual offset. Crossing a page boundary rebases the
  prepared current/next pair; it must not expose native LVGL or restart the
  gesture from a page origin.
- Keep committed-page settle and edge return as separate policies. Edge return
  uses a softer smooth in/out curve and may be longer without slowing normal
  page changes.
- Settings releases its raw scroll snapshot before application-close capture,
  including when inertia is still active.
- A pointer-down during Settings inertia must pause the direct scroll worker at
  its last presented Y coordinate and continue the new drag from that frame.
  Do not reject the gesture merely because snapshot playback hides the live
  Settings root.

## Change workflow

1. Identify the owning component, task, buffer, and handoff.
2. Make one coherent change group and keep unrelated performance experiments
   out of it.
3. Run ESPHome configuration validation and a complete firmware compile.
4. Flash through COM and verify the exact affected interaction on hardware.
5. Check runtime logs for restarts, DSI starvation, heap loss, and long loops.
6. Update architecture documentation when ownership or lifecycle changes.

For gesture work, exercise slow drags, short fast flicks, chained Home pages,
tap feedback on tiles, takeover-and-reverse during settle, takeover-and-continue
to the following page, edge bounce, and close/reopen while Settings inertia is still running. For
native LVGL artifact work, test small independently invalidated widgets; a
full-screen snapshot benchmark cannot validate the native double-buffer
handoff.
