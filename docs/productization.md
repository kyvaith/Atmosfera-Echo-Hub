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
| Firmware image | 6,256,408 bytes |
| Smallest app partition free | 10,258,224 bytes (62%) |
| Internal DIRAM | 216,210 / 576,464 bytes (37.5%) |
| Display buffers | Three display-owned full-screen buffers |

The validated checkpoint also replaces direct calls to LEDC implementation
internals with the declarative `output.ledc.set_next_fade_duration` action.
The known-good device branch remains untouched.

Two PlatformIO-only framework patch scripts are still present as explicitly
marked transitional compatibility code. Native builds ignore them. They must
be replaced with source-level or component-owned implementations before the
project is considered portable:

- FreeRTOS static-allocation framework patch;
- ESP-Hosted SDIO streaming framework patch.

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

| Component | Current source | Target |
| --- | --- | --- |
| `const` | Consolidated ESPHome integration | Remove from the explicit external list |
| `mipi` | Consolidated ESPHome integration | Use upstream |
| `mipi_dsi` | Consolidated ESPHome integration | Rebase local DSI changes and upstream them in scoped PRs |
| `lvgl` | Consolidated ESPHome integration | Rebase accelerators; extract navigation and snapshots |
| `image` | Consolidated ESPHome integration | Reconcile with the current upstream image platform |
| `audio_file` | Consolidated ESPHome integration | Use upstream |
| `ledc` | Consolidated ESPHome integration | Upstream the hardware-fade action |
| `es7210` | Consolidated ESPHome integration | Use upstream |
| `esp32_jpeg` | Consolidated ESPHome integration | Keep as a generic hardware codec and upstream it |
| `artwork_image` | Consolidated ESPHome integration | Replace with generic online/runtime image hardware decode support |
| `sendspin` | Consolidated ESPHome integration | Keep only fixes missing from current upstream |
| `speaker_source` | Consolidated ESPHome integration | Keep only fixes missing from current upstream |
| `va_client` | Consolidated ESPHome integration | Keep as a transport using standard microphone and speaker APIs |
| `resampler` | Consolidated ESPHome integration | Keep only missing microphone/full-duplex support |
| `audio_processor` | Consolidated ESPHome integration | Keep as a generic processor interface |
| `esp_afe` | Consolidated ESPHome integration | Keep as an ESP audio processor implementation |
| `esp_audio_stack` | Consolidated ESPHome integration | Rename and refactor into a generic duplex audio transport |

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
- volume arc overlay;
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
