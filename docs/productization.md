# Productionization roadmap

This document tracks the migration of Atmosfera Echo Hub from a product
prototype to an upstream-compatible ESPHome project. Refactoring must preserve
the current user-visible behavior and measured performance unless a change is
explicitly documented and approved.

## Known-good baseline

The baseline is tagged `pre-productization-2026-07-23` in all three source
repositories.

| Repository | Baseline commit |
| --- | --- |
| `kyvaith/Atmosfera-Echo-Hub` | `09bb26ed20f4d49ab9b5141dc3e204f16142ab18` |
| `kyvaith/esphome` | `d35c9664c71413bb4676a095f48f00d85e73ab11` |
| `kyvaith/esphome-intercom` | `df37bbcfa18c5d9e97f84366b9be52b59160f703` |

The ESPHome productization branch is built in a separate worktree from the
current upstream `dev`. The working firmware checkout must not be switched to
that branch until the complete device build and hardware regression suite pass.

## Current checkpoint

The first native ESP-IDF checkpoint compiles successfully against ESPHome
`2026.8.0-dev` and ESP-IDF `5.5.5`. It produces factory, OTA, and ELF artifacts
without relying on PlatformIO to pass compile definitions or flash settings.

| Metric | Result |
| --- | --- |
| Firmware image | 6,274,746 bytes |
| Smallest app partition free | 10,241,520 bytes (62%) |
| Internal DIRAM | 215,890 / 576,464 bytes (37.45%) |
| Display buffers | Three display-owned full-screen buffers |

The validated checkpoint also replaces direct calls to LEDC implementation
internals with the declarative `output.ledc.set_next_fade_duration` action.
It adds an optional `lvgl_material.direct_state_layers` component for
allocation-free direct touch feedback and compile-time guards that keep the
extended LVGL runtime buildable when image, snapshot, PPA, or MIPI DSI support
is disabled. The Atmosfera previous/next transport feedback now uses that
component instead of a project-local C++ include.
Immich URL handling, query generation, response parsing, orientation filtering,
and recent-asset selection now live in a reusable, platform-neutral
`immich_gallery` component with an isolated ESP-IDF build test. The product no
longer injects `static/ui_immich_helpers.h` into generated application code.
The known-good device branch remains untouched.

Home paging and the Player, Settings, Voice Assistant, and Immich application
lifecycles now use the declarative `lvgl.navigation` schema. The component owns
gesture arbitration, tap cancellation, application open/close transitions,
home indicators, deferred lifecycle callbacks, and the Settings scroll
snapshot. Product YAML still supplies application policy callbacks, but no
longer implements the navigation state machine itself.

Shared pressed feedback is now declared once in
`modules/lvgl/material.yaml`. A reusable `lvgl_material.pressed_styles`
component owns the single LVGL style and applies it after all widgets have been
created. This removes the boot-time C++ style lambda and its ordering scripts
without adding image buffers or runtime animation. The complete firmware build
is 2,096 bytes smaller and uses 712 fewer bytes of DIRAM than the preceding
declarative-navigation checkpoint.

The title marquee direct renderer now lives in
`lvgl_material.direct_marquees` instead of a product-local injected header.
Its visible region is derived from the configured LVGL viewport, so the
renderer no longer hardcodes an 800-pixel display or title coordinates. The
existing PPA/direct-blit path, worker-core scheduling, timings, and lifecycle
conditions are unchanged. The migration removes another 1,488 bytes from the
firmware image and 16 bytes from DIRAM.

The global volume renderer now uses
`lvgl_material.direct_volume_overlays`. Its geometry is derived from the
configured LVGL arc, knob, label, activation widget, and display dimensions;
the product no longer injects `static/ui_volume_overlay.h` or carries an
800-pixel drag clamp. The migration deliberately preserves the validated
RGB888 PPA capture, direct presentation, and three-buffer lifetime. It removes
800 bytes from the firmware image at a cost of 96 bytes of DIRAM. RGB565
support and reducing the runtime PSRAM footprint remain separate changes that
must be benchmarked independently.

The Player's wavy progress/play renderer now uses
`lvgl_material.wavy_progress` instead of the injected
`static/ui_wavy_arc.h`. The component preserves the existing worker-core,
PPA/direct-present, cache synchronization, and buffer-reuse paths. Its
background crop is derived from the active display and configured widget
coordinates rather than an 800x800 screen assumption. The validated product
widget remains 244x244; making the renderer scale its internal shape geometry
is intentionally a separate hardware-tested change. This migration removes
the product-local 1,400-line renderer without increasing DIRAM.

Application preview preparation now uses the registered
`lvgl.navigation.applications` collection through the declarative
`lvgl.navigation.prepare_applications` action. Home snapshot preparation uses
`lvgl.navigation.refresh` and the selected compositor backend. The boot script
therefore no longer names all four application roots or calls the legacy
snapshot cache directly. Buffer reservation and boot ordering remain unchanged
until this checkpoint passes the hardware regression suite.
The remaining legacy Home positioning and refresh lambdas now derive page
count from their configured object arrays and width from the active LVGL
display. They no longer embed the product's 800-pixel panel width.

The obsolete PlatformIO-only FreeRTOS and ESP-Hosted patch scripts have been
removed. Native ESP-IDF builds never executed them, so keeping their absolute
paths in the product configuration provided no runtime behavior and made the
project machine-specific. Any future ESP-Hosted transport optimization must be
implemented in a versioned component, disabled by default, and validated in the
native ESP-IDF test matrix.

Task runtime diagnostics now use the optional `task_runtime_profiler`
component and its declarative `task_runtime_profiler.log` action. This removes
the product-local `static/task_runtime_profiler.h`, private ESP-IDF backtrace
headers, and board-level FreeRTOS profiling sdkconfig entries. The component
owns the required sdkconfig setting and allocates its bounded PSRAM state only
when profiling is requested. The complete migration costs 8 bytes of firmware
image and 8 bytes of DIRAM.

## Non-negotiable rules

- Do not combine behavioral changes with code movement.
- Preserve commit authorship when porting existing work.
- Do not add Atmosfera-specific names, pins, dimensions, colors, or entity IDs
  to generic ESPHome components.
- Do not inspect or depend on `platformio_options` from component code.
- Do not use PlatformIO/SCons-only patch scripts for upstreamable behavior.
- New acceleration and behavior-changing options default to disabled.
- Derive display resolution, stride, color format, and byte order from ESPHome
  display metadata or the active LVGL display and draw buffers.
- Avoid heap allocation after component setup. Allocate bounded buffers once
  and reuse them.
- Debugging, profiling, and verbose logs default to disabled.
- Every migration step must pass config validation, a focused component build,
  and the relevant device regression scenarios before it replaces the baseline.

All currently required product components now come from one ESPHome integration
tree. The separate legacy LVGL, artwork bridge, voice client, and intercom
external sources have been removed from the product configuration. This is an
integration checkpoint, not the final upstream boundary: the table below still
tracks which components must be reconciled or replaced before release.

## External component inventory

The product currently imports 15 components from one consolidated ESPHome
integration tree:

| Component | Target |
| --- | --- |
| `audio_processor` | Keep as a generic processor interface |
| `artwork_image` | Fold transport-specific policy into the media integration and reuse generic image decode/presentation APIs |
| `display` | Rebase the required display API additions onto upstream |
| `esp_afe` | Keep as the Espressif implementation of `audio_processor` |
| `esp_audio_stack` | Rename and refactor into a generic duplex audio transport |
| `esp32_jpeg` | Keep as a generic hardware JPEG codec and upstream it |
| `image` | Reconcile with the current upstream image platform |
| `immich_gallery` | Grow from the validated API/parser boundary into the generic Immich application controller |
| `lvgl_material` | Keep independent reusable widgets, direct state layers, marquees, volume overlays, and wavy progress controls |
| `lvgl` | Rebase accelerators; extract navigation and snapshots |
| `micro_wake_word` | Keep only the configurable buffering changes missing upstream |
| `mipi_dsi` | Rebase local DSI changes and upstream them in scoped PRs |
| `sendspin` | Keep only fixes missing from current upstream |
| `task_runtime_profiler` | Keep as an optional ESP32-P4 diagnostic component; profiling is inactive until explicitly requested |
| `va_client` | Keep as a transport using standard microphone and speaker APIs |

The unused `generic_image`, `online_image`, `runtime_image`,
`lvgl_image_presenter`, and `lvgl_region_presenter` implementations remain in
the integration tree for their own feature branches, but the product no longer
imports them. The active image path is now explicit: `artwork_image` owns
network image lifetime, `esp32_jpeg` owns hardware decoding, and `image`
provides stable pixel-buffer leases. Further consolidation must preserve the
proven direct hardware JPEG path and artwork replacement behavior.

The project does not use `intercom_api`. The former repository name was
historical; only its generic audio processing and full-duplex transport layers
were carried into the consolidated ESPHome integration tree.

## Target component boundaries

### Low-level ESPHome components

- `mipi_dsi`: panel transport, frame-buffer ownership, and DSI synchronization.
- `esp32_jpeg`: reusable hardware JPEG encode/decode API.
- `lvgl`: generic display integration and optional PPA/DMA2D draw primitives.
- `audio_processor`: processor interface and bounded audio buffer utilities.
- `esp_afe`: Espressif AFE implementation of `audio_processor`.
- `audio_duplex`: I2S RX/TX coordination and AEC playback-reference transport.
- `va_client`: realtime voice protocol only.

### LVGL navigation

The public configuration belongs below `lvgl.navigation`, while the
implementation is split into focused modules:

- `GestureRouter`: pointer tracking, gesture recognition, and click
  cancellation.
- `SnapshotStore`: raw/JPEG cache ownership and bounded eviction policy.
- `SnapshotCompositor`: accelerated presentation and transition rendering.
- `AppNavigationController`: home pages, applications, and lifecycle state.
- `ScrollSnapshotController`: reusable snapshot-backed scrolling.

### Reusable UI widgets

The provisional `lvgl_material` feature contains independent widgets rather
than application-specific code:

- wavy progress/play button;
- marquee label;
- direct volume arc overlay;
- Material state-layer feedback;
- page indicator.

### Application controllers

- `immich_gallery`: API, asset selection, download, prefetch, and slideshow
  state.
- `voice_session`: wake word, native/realtime session state, media ducking, and
  deterministic finish behavior.
- A media UI controller may follow after the generic widgets and image sources
  are stable.

## Migration sequence

1. Rebuild an integration branch from current upstream `dev`.
2. Port and validate isolated components, starting with `esp32_jpeg`.
3. Reconcile existing upstream changes before porting local patches.
4. Replace project-local compile flags with component schemas, generated
   defines, supported sdkconfig values, or source-level fixes.
5. Move the three audio components out of the intercom repository.
6. Extract snapshot code from `lvgl_esphome.cpp` without changing behavior.
7. Add the declarative navigation schema and remove raw touchscreen lambdas.
8. Convert `static/ui_*.h` helpers into reusable LVGL widgets.
9. Move Immich, voice, and media state machines out of YAML.
10. Remove redundant external components and absolute local paths.
11. Split the validated work into focused upstream branches and documentation
    PRs.

## Validation gates

Each stage must pass:

- Python syntax and focused pre-commit checks;
- component config validation;
- ESP32-P4 ESP-IDF component compilation;
- complete Atmosfera firmware compilation;
- five cold boots and five software restarts;
- home swipe, edge bounce, and consecutive-page swipe tests;
- first and repeated application open/close tests;
- settings snapshot scroll and input cancellation tests;
- artwork replacement during playback;
- local audio, SendSpin, wake word, realtime voice, and AEC tests;
- Immich initial load, next-image transition, and application close;
- memory, FPS, DSI FIFO, crash, and artifact comparison with the baseline.

The production project is ready to replace the baseline only when no gate
regresses and the YAML contains no component-internal state machines.
