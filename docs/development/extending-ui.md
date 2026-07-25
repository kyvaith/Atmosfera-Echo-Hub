# Extending the UI

This guide describes how to add pages, applications, lists, and dynamic
controls without bypassing navigation, snapshots, display ownership, or audio
policy.

## First question: what are you adding?

| Element | Register with | Motion owner |
| --- | --- | --- |
| Another Home carousel page | `lvgl.navigation.home` | Home snapshot compositor |
| Full-screen application | `lvgl.navigation.applications` | Application snapshot compositor |
| Scrollable application list | `snapshot_compositor.scroll_regions` | Scroll snapshot controller |
| Small continuously animated region | `lvgl_material` direct component | Direct-region compositor |
| Static/rarely changing widget | Normal LVGL page YAML | LVGL |
| Network JPEG image | Image owner plus `esp32_jpeg` | Hardware JPEG and image presenter |
| Voice-related screen | Voice app plus phase callbacks | Voice session controller and navigation |

Do not turn a simple static widget into a direct renderer. Direct rendering is
for motion whose LVGL redraw cost is measured and significant.

## Add a Home page

1. Define the page root in `modules/lvgl/pages/`.
2. Give it a stable widget ID.
3. Add its root to `lvgl.navigation.home.widgets` in visual order.
4. Add one matching indicator to `home.indicators`.
5. Add invalidation triggers for data that changes after the boot snapshot.
6. Test the new three-page cache windows around every page boundary.

Conceptual example:

```yaml
lvgl:
  navigation:
    home:
      page: controls_page
      widgets:
        - controls_root_1
        - controls_root_2
        - controls_root_3
        - controls_root_4
        - controls_root_5
      indicators:
        - page_indicator_1
        - page_indicator_2
        - page_indicator_3
        - page_indicator_4
        - page_indicator_5
```

Do not allocate a fifth raw 800x800 snapshot. The cache must retain three raw
slots and use JPEG backing for pages outside the current window.

The current direct clock/indicator overlay has product-specific geometry.
Verify its placement and masking when page count changes.

## Add an application

An application is a full-screen page or overlay with a registered lifecycle.

### Required definition

```yaml
lvgl:
  navigation:
    applications:
      - id: example_application
        page: example_page
        widget: example_root
        close_gesture: true
        close_on_threshold: true
        on_prepare_open:
          - script.execute: example_quiesce_workers
        on_before_reveal:
          - script.execute: example_prepare_live_page
        on_opened:
          - script.execute: example_start_workers
        on_prepare_close:
          - script.execute: example_quiesce_workers
        on_close:
          - script.execute: example_end_external_session
        on_close_cancelled:
          - script.execute: example_resume_workers
        on_closed:
          - script.execute: example_release_runtime_buffers
```

Use only callbacks the application needs.

### Lifecycle contract

| Callback | Allowed responsibility |
| --- | --- |
| `on_prepare_open` | Stop competing direct workers, close transient overlays, establish a stable preview |
| `on_before_reveal` | Prepare the live LVGL page while the final snapshot frame is still visible |
| `on_opened` | Start app-owned timers/workers and allocate app-lifetime buffers |
| `on_prepare_close` | Pause/drain workers and make the live app safe to capture |
| `on_close` | Commit product action such as ending a voice session |
| `on_close_cancelled` | Restore workers and state without rebuilding the app |
| `on_closed` | Release app-only resources and restore Home ownership |

Never start a direct worker before the opening transition has handed ownership
to the live page. Never free an image or region source before its worker and
DSI frame have drained.

### Open action

Use the declarative navigation action from the tile. Do not call
`lv_scr_load`, manipulate page coordinates, or emulate the opening animation
in a click lambda.

### Boot preview

`lvgl.navigation.prepare_applications` prepares all registered previews during
the controlled boot phase. New applications are included automatically after
registration. Ensure the page can render a valid idle state without network
data.

## Add a snapshot-backed scroll region

Use a scroll region when a large list has measured poor LVGL motion.

```yaml
lvgl:
  snapshot_compositor:
    scroll_regions:
      - id: example_scroll
        application: example_application
        widget: example_list
        backend: direct
        preload: true
        max_content_size: 8MB
        swipe_start_distance: 2
        axis_bias: 6
        overscroll: 15%
        momentum_duration: 560ms
        bounce_duration: 320ms
        max_inertia_duration: 900ms
```

The exact schema is defined by the ESPHome component; use the current
`modules/lvgl/base.yaml` as the validated example.

Requirements:

- preload after the application is visible and stable;
- cancel the original LVGL pressed target when scrolling begins;
- apply final logical scroll position at settle;
- refresh the bitmap in place after content changes;
- delay refresh until pressed/hover state is clear;
- release all scroll buffers when the app closes.

Do not leave the raw list snapshot allocated globally.

## Invalidate a snapshot correctly

Use the component action or existing refresh script for the smallest changed
owner. A typical update sequence is:

1. update the live LVGL widget;
2. let its transient pressed state finish;
3. mark the owning Home page or scroll region dirty;
4. coalesce repeated updates;
5. refresh in place when no large snapshot/artwork operation owns the PSRAM
   transfer lane.

Avoid calling `lv_refr_now()` repeatedly from entity callbacks. It forces
synchronous rendering and can collide with the direct compositor.

## Add a direct Material control

Prefer an existing `lvgl_material` component:

- `pressed_styles`;
- `direct_state_layers`;
- `direct_marquees`;
- `direct_volume_overlays`;
- `wavy_progress`.

For a new reusable direct control:

1. Put the renderer in `esphome/components/lvgl_material/`.
2. Define a declarative schema and generated component binding.
3. Derive viewport, format, position, and dimensions from configured widgets.
4. Allocate bounded local buffers during setup.
5. Keep rendering off the ESPHome main loop.
6. Coalesce stale states if the worker is busy.
7. Register a direct region instead of owning a full-screen buffer.
8. Implement pause, barrier/drain, resume, and shutdown.
9. Tag frames with the current base generation.
10. Use PPA/DMA2D only for supported formats and operations.

If the control has a pressed state, use a style/state layer rather than
repeatedly changing several widget properties from YAML.

## Add an image source

For JPEG artwork or photos:

1. Keep compressed network data in a bounded encoded buffer.
2. Use `esp32_jpeg`; do not add a software JPEG fallback to hide a hardware
   ownership bug.
3. Decode into a reusable leased RGB888 destination.
4. Keep the old source visible until decode succeeds.
5. Synchronize the written range.
6. Atomically publish the new descriptor.
7. Refresh the specific LVGL/direct owner.
8. Release the old lease only after handoff.

Use the configured LVGL byte order. Do not hardcode channel reversal for one
panel.

## Add animation

Choose the cheapest representation that preserves the design:

| Need | Recommended path |
| --- | --- |
| Simple position/opacity change | Native LVGL animation |
| Large bitmap pan/scale/rotate | PPA SRM/direct image controller |
| Small custom shape with frequent updates | Bounded direct Material renderer |
| Complex vector animation | Lottie/ThorVG with measured frame-cache policy |
| Full-screen page transition | Snapshot compositor |

PPA moves pixels; it does not execute arbitrary vector paths. A Lottie change
must be tested for scene complexity, raster buffer size, cache size, and boot
phase overlap.

## Fonts and icons

- Use shared Roboto font variants for text.
- Use Material Symbols Rounded for standard icons.
- Do not add PNG icons when an appropriate Material Symbol exists.
- Declare the glyph in the font's allowed characters so ESPHome includes it.
- Keep typography and icon sizes in the page/style layer, not in generic
  renderer code.

## YAML policy

Use YAML for:

- page composition;
- Home Assistant entity bindings;
- readable automation sequences;
- app-specific policy and user settings;
- declarative component configuration.

Move to C++ when code:

- manages buffers or cross-task state;
- owns a gesture state machine;
- runs every frame;
- performs geometry or pixel processing;
- must coordinate display/audio ownership;
- is duplicated across views;
- requires more than a short, self-contained policy expression.

A lambda that calls one accessor or selects an entity is acceptable. A lambda
that implements navigation, animation, caching, audio flow, or a widget
renderer is not.

## Resolution independence

Reusable code must never assume:

- 800x800;
- a round screen;
- three Home pages or four Home pages;
- RGB888 unless the schema requires it;
- a particular stride;
- fixed clock, title, or button coordinates.

Read the active display dimensions and color format. Expose round masking,
transition target, cache size, and geometry as configuration where needed.

The current product still has known 800x800 and circular assumptions. Do not
copy them into new components; remove them when touching the owning code.

## Completion checklist

Before calling a new screen complete:

- [ ] It is registered in the correct navigation collection.
- [ ] Swipe/scroll cancels underlying taps.
- [ ] First and repeated open/close use valid snapshots.
- [ ] All direct workers pause and drain at handoff.
- [ ] Buffers have bounded allocation and deterministic release.
- [ ] The screen survives cold boot and software restart.
- [ ] Home and audio remain smooth while the screen is active.
- [ ] No blue flash, horizontal artifacts, stale frame, or shifted image.
- [ ] The new view does not introduce a hardcoded display dimension in reusable
      code.
- [ ] Architecture documentation is updated if a new ownership rule exists.
