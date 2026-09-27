# Wear OS M3 LVGL Map

Sources:

- local application kit: `C:\Users\kyvai\Downloads\M3 Wear OS Apps Design Kit (Community).fig`;
- Home tile kit: [M3 Wear OS Tiles Design Kit](https://www.figma.com/design/myfUIQL0cC5Paer4NbtFAI/M3-Wear-OS-Tiles-Design-Kit--Community-?node-id=38851-231913&p=f).
- product Home composition: `Prezentacja1.pptx`, supplied with the product
  artwork and measured against the 800x800 circular display.

The local `.fig` was decoded as `fig-kiwi` and used as the design source for the LVGL UI. The kit uses a 192dp Wear OS canvas; this project renders at 800px, so the reference scale is `800 / 192 = 4.1667`.

The Figma kits are the source of truth for geometry, typography, color,
opacity, state layers, and interaction hierarchy. New views must start from a
specific frame or component in one of these kits rather than from an informal
visual approximation.

## Tokens

Core WM3 tokens used in LVGL:

- Background: `0x000000`
- Surface: `0x303030`
- Surface bright: `0x474747`
- Tonal control surface: `0x332E3C`
- Selected tonal surface: `0x4D3D76`
- On surface: `0xF2F2F2`
- On surface variant: `0xC4C7C5`
- Outline variant: `0x5C5F5E`
- Primary: `0xD3E3FD`
- On primary: `0x001944`
- Primary container: `0x04409F`
- Secondary container/on: `0x004A77` / `0xC2E7FF`
- Tertiary container/on: `0x0F5223` / `0xC3EDCF`
- Error: `0xFD7267`

## Component Mapping

- `Icon-Button`: circular LVGL buttons, 52-60dp source size, used for player controls and close buttons.
- `Button`: pill action, 172x52dp source size, used as the basis for primary tile actions.
- `Button-Compact`: dense pill action, used as the basis for two-column home controls.
- `Toggle+Selection-Buttons`: settings states use selected tonal colors instead of custom green/purple labels.
- `Card`: tonal rounded cards use the kit radius of 26dp conceptually; in LVGL this is implemented as fully rounded grouped containers for the round viewport.
- `Slider`: 172x52dp tonal slider, mapped to the brightness card.
- `Page-Indicator`: replaced text counters with active/inactive dot indicators.
- `Media-Player`: player colors and controls now follow the WM3 dark token set.
- `Grouped containers`: home controls are intentionally arranged as uneven primary/secondary clusters instead of a uniform 2x3 grid.
- `Edge-hugging containers`: bottom clusters use wider rounded forms that visually embrace the circular viewport.

## Home Tile Framework

The four Home pages in `modules/lvgl/pages/tiles_m3.yaml` use one 800x800 root
per page. The first page is the M3 weather composition, followed by Security,
Applications, and Controls. The first page intentionally breaks the circular
safe area: the oversized clock and weather artwork are clipped by the physical
display edge exactly as in the product composition. It uses the following
structure:

- two large Cherry Bomb One clock rows, with per-digit white/accent color.
  The minute contour uses a second font compiled at the SAME size, with
  `outline_width: 6`. FreeType expands glyph contours during code generation
  while preserving advances and baselines. Both labels have identical x/y,
  letter spacing and text-box dimensions. A larger font is not an outline:
  it displaces the second digit. LVGL's native outline only handles vector
  glyphs in the current draw backend, not ESPHome's bitmap fonts;
- a static volume icon plus an API-aware Wi-Fi icon at the top: Wi-Fi strength
  is shown only while Home Assistant state subscriptions are active, otherwise
  the disconnected icon is shown;
- the old small global clock is removed from every page and overlay. The
  transparent global_volume_activation_surface remains only as the long-press
  gesture target for the volume arc;
- a diagonal dark weather chip whose upright temperature and condition labels
  remain readable independently of the chip transform;
- an oversized, clipped weather animation and a bottom microphone action;
- one primary, high-emphasis surface;
- one or two secondary tonal controls;
- an optional compact slider or state row;
- one shared page indicator outside the captured page content.

Dynamic Home Assistant cards use a fixed object pool declared through
`lvgl_material.tile_surfaces`. Runtime configuration changes only icon text,
labels, colors, visibility, and action metadata. It never deletes or rebuilds
the LVGL tree, which avoids heap fragmentation and long layout passes.
The legacy light, climate, and slider bindings remain hidden compatibility
objects only; they are not part of the first-page visual composition or its
snapshot.

The weather card follows the same fixed-tree rule. Its labels are native LVGL
objects, while exactly one predeclared Lottie widget is active at a time. The
condition-to-animation mapping belongs to `lvgl_material.weather_presenters`;
Home Assistant remains the source of weather state. The condition animation
plays exactly one complete cycle whenever page 1 becomes visible. It then hands a
non-empty retained RGB888 frame back to the LVGL canvas so the live page and
its next managed snapshot contain the same final weather image.
The next visibility epoch resumes from the phase represented by that retained
frame, rather than flashing frame zero and then restarting. This makes the
snapshot-to-live handoff visually continuous while still replaying one full
cycle.

The first-page weather canvas is 384x384 at `(444,68)` in the 800px product
space. The direct compositor paints the complete weather region with its
backdrop, so the left edge stays to the right of the widest outlined minute
glyph; otherwise the last minute digit can be covered intermittently.
The circular physical viewport intentionally clips the outer rays.
For screenshot comparison, crop the supplied PowerPoint reference to its
physical screen circle before scaling it to the framebuffer. The second
reference PNG uses bounds `(26,24,470,468)`. `tools/compare_home_design.py`
produces reference, capture, 50% overlay, and difference views. The JPEG from
`debug_capture_screen` already has RGB channel order; do not swap its channels.
The source animations are normalized by `tools/style_weather_lottie.py`: color
accents use the same `36BCF0` token as the clock, neutral cloud highlights stay
white, and all filled or stroked geometry receives a round black outline. The
fast radial renderer uses a 3.5-unit contour half-width in its 128-unit design
space, about 10.5 display pixels after the 320px raster is enlarged to 384px. When
the global accent becomes configurable, regenerate the assets with the same
token rather than hand-editing individual JSON files.

## Interaction States

- Pressed feedback is a short M3 state layer, not a color-transition animation.
- A drag must not enter the pressed state. The shared gesture router resolves
  tap versus drag before replaying native LVGL press/release events.
- The page indicator remains stationary while page snapshots move and is
  anchored to the same bottom-safe coordinate in live and snapshot modes. On
  the 800x800 product display both bounds are `y=737..746`. Navigation publishes
  the laid-out row geometry to the snapshot compositor, instead of maintaining
  a second fixed Y value. The microphone is at `(356,610)`, size 90, above the
  indicators and below the minute row in the second reference layout.
- Notifications are modal bottom sheets: a full-screen scrim and a rounded
  lower panel. They queue in a bounded component and dismiss by timeout or tap.
- Continuous direct renderers pause while a modal overlay owns the display so
  they cannot draw above the overlay.

## Performance Budget

- No per-frame allocation is allowed after setup.
- Home pages are snapshotted outside the touch-start path.
- The sunny weather scene rasterizes its small primitive set at the configured
  internal resolution, then scales the complete ARGB frame once with PPA. The
  CPU-written source is synchronized only at that PPA ownership boundary; the
  primitive renderer must not perform an earlier duplicate PSRAM writeback.
  The two compact source buffers are ping-ponged, so CPU rasterization overlaps
  the previous PPA transaction. A bounded clean RGB888 background is rendered
  offscreen once per playback epoch with the animation excluded. Transparent
  frames blend onto this immutable background, never onto the previous DSI
  image. It is released after draining the animation region, including on
  navigation and modal entry. The complete 384x384 background has 442,368
  pixel bytes before allocator alignment; it is not another full-screen framebuffer.
  Opaque boot and scaled weather publishers must record the exact registered
  region width/height. A zero-sized boot release left a stale region active
  and added a copy to every later weather frame.
  Generic finite weather Lottie keeps the LVGL canvas source immutable while
  active and retains a non-empty final frame for snapshots.
- Only the visible weather condition renders. Hidden condition assets retain
  parsed state but do not submit frames.
- A snapshot of an already visible, full-screen Home root must render it in
  place. Temporarily aligning that live root invalidates the physical DIRECT
  framebuffer and can expose a black base beneath weather or another regional
  renderer.
- A modal overlay drains direct-region work before becoming visible and keeps
  that pause until the underlying LVGL frame is presented again.

## Constraints

LVGL does not support every Figma component behavior directly, so the mapping prioritizes visible structure, colors, radii, typography, and interaction targets while preserving existing ESPHome IDs and scripts. Native Wear OS shape morphing and scroll-time corner animation remain outside ESPHome LVGL, but static containers should still follow the M3 Expressive visual language.

## Design Check

Run the repository-side check after changing the composition or regenerating
the weather assets:

```text
python tools/validate_m3_home_design.py
python tools/style_weather_lottie.py --check
```

The check locks the measured 800px geometry, the intentional overflow, the
clock/icon anchors, and the nine-asset accent/outline contract. The original
PowerPoint remains the visual reference for typography and relative placement;
the numeric values are kept in the YAML substitutions so they can be reviewed
without opening the presentation.

For animation QA, use the atomic `debug_capture_screen` service through
`tools/test_voice_assistant_ui.py:capture_screen`. The raw region downloader
reads a live framebuffer in multiple requests and can mix different animation
times. Inspect an intermediate frame AND the retained final frame; a correct
final canvas can conceal trail accumulation during direct playback.

### Earlier Hardware Validation, 2026-09-14 11:14 Build

This earlier native ESP-IDF 5.5.5 build was flashed through COM5 with the flash
hash verified. Config hash: `0x65e5c263`; build time: `2026-09-14 11:14:12 +0200`.
Firmware SHA256:
`DC1B8D33E875E55ADA610CC951E66448A2FF8CAEC0A18A404377F0A346191574`.

Run `python tools/test_m3_home_ui.py --output C:/aeh-build/m3-home-qa` for the
bounded hardware sequence. It captures intermediate and retained weather
frames, all four Home pages, volume over weather, Player and Settings, and
returns from those applications. Atomic JPEG capture reserves 512 KiB of
encoded output; this diagnostic-only bound does not change production JPEG
quality or artwork/snapshot allocation defaults.

| Check | Observed result |
| --- | --- |
| Weather playback | Approximately 58-60 accepted regional frames/s; intermediate images have no accumulated ray outlines |
| Weather cost | CPU raster/render approximately 3.6-4.5 ms/frame; regional composition usually 13.7-15.3 ms average, with occasional longer frames |
| Synthetic Home drag | Pages 1 -> 2 -> 1 committed, 56 frames each, no failed submissions; input was injected every 25 ms, so the roughly 41 fps gesture result is input-rate limited |
| Application transitions | Player and Settings produced approximately 25 opening and 21 closing frames with nonempty content signatures |
| Layout | Superseded by the circle-aligned comparison below; do not use this earlier run to validate the current geometry |
| Boot DSI diagnostic | 434 samples, no nonzero underrun samples, minimum observed FIFO 896 |
| Host checks | 39 font component tests passed; design validator passed 27 geometry tokens and 9 weather assets; changed Python passed Ruff |

Preview remains intentionally pinned to 12:58, sunny, 21 degrees C for visual
comparison. Captures and serial evidence are in `C:/aeh-build/m3-home-qa` and
`C:/aeh-build/m3-home-final-runtime.log`. These tests do not establish physical
finger tracking, performance during concurrent music playback, or long-run
stability. No restart occurred in the bounded sequence.

**Open regression-test finding:** Settings opened and closed visually, but its
scroll bitmap was not created after visiting Player. At 11:20:12 the contiguous
3,213,603-byte attempt and the 1,605,603-byte segmented attempt failed. Gallery
had no existing destination to lend (`bytes=0`); idle Player retained 2,500 KiB
of decode capacity. After closing Settings, PSRAM free was 2,613 KiB, largest
block 1,600 KiB, and scroll snapshot memory was zero. Do not mark Settings
scrolling as validated or fix this by silently reducing snapshot resolution.
The temporary clean weather background was already released at this point.
This run does not establish when the Settings allocation problem began.

### Circle-Aligned Layout Validation, 2026-09-14 16:51 Build

Config hash `0x915111a4`, compiled at `16:51:18 +0200`, uploaded through COM5
with flash hash verification. The screenshot comparison uses the actual
reference circle `(26,24,470,468)`, not the white slide margins. Both rows use
the same 300px Cherry Bomb font. Text-box origins are `(40,66)` for hours and
`(43,256)` for minutes; glyph bearings put their visible tops around y=204
and y=394. Minutes have a same-metrics 8px outline, not an offset duplicate.

Artifacts in `C:/aeh-build/`:
- `m3-aligned-final-device.png`: full-resolution raw capture after weather stopped.
- `m3-aligned-final-comparison.png`: reference, capture, overlay, and difference.
- `m3-aligned-final-after-player.png`: retained Home frame after opening and closing Player.
- `m3-aligned-final-runtime.log`: bounded COM runtime evidence.

The atomic JPEG capture failed with `ESP_ERR_NO_MEM` during weather playback.
The static layout comparison therefore uses the streaming raw capture after
the animation completed; it is not evidence about moving-frame quality.
The raw RGB888 path requires red/blue conversion, unlike the JPEG endpoint.
Weather restarted after Player closed without display-buffer allocation errors
in this sequence. Keep the separate immutable display back buffer: the temporary
single-canvas alias experiment was rejected and removed before this build.

Current weather measurements were 50-51 published frames per two seconds,
about 25 FPS, not the 58-60 FPS of the earlier configuration. The 320px raster
is still scaled to 384px. Higher-fidelity rendering and its performance remain
open work; a correct layout does not establish that those requests are resolved.
The shared Gallery/Settings pool also still failed its boot reservation, so
Settings scrolling is not validated by this layout change.
