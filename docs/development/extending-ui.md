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

Keep `controls_page` first in the merged `lvgl.pages` list. Product `on_boot`
at priority600 requests Home before LVGL's `PROCESSOR` setup, which later calls
`show_page(0)` unconditionally. A new first page can therefore replace Home at
startup even when navigation still reports Home1. Preserve the original order
`controls_page`, `settings_page`, `music_page`, `immich_page`, `camera_page`;
append new application-page includes after those five (the light detail is
currently sixth). Run `tools/tests/test_light_page_order.py` with the companion
fork on `PYTHONPATH`: it checks the actual package merge and page registration
with control admission both disabled and enabled. This source check does not
replace firmware boot and visible Home validation.

### Entity control detail

The locally adopted W03 source registers one shared light detail as app6, with six
compressed-preview entries and the existing single decoded work slot. Its
[entity-control contract](../architecture/entity-control.md) requires capturing
the granted selection generation before asynchronous opening and rechecking it
before NAV and renderer resume after settlement. Use the bool NAV admission and
actual Scalar drain result before scene changes; a lifecycle callback or wait
alone is not a barrier. Slot-0 request admission is not a lifetime lease: stop,
drain, release and fence competing presenters for the entire session, including
delayed/HA/physical entry and close-cancel preview. The shared native control-view
lifecycle owns matching captured-generation close-cancel recovery and calls
Scalar rendering hooks; do not add a second YAML resume path. Scalar still owns
its pixels, pause lease, source retirement and real drain result. Phase A keeps
the public Scalar guard and scheduling order; its new hardware acceptance is
tracked separately. Failed preparation
retains its owned suppression until verified cleanup, so other mutation paths
must also refuse while that ownership remains.

Before a system notification, revoke the light selection, obtain true close/drain
admission and wait for NAV settlement, then show the popup. Do not retain an
active Scalar underneath it or resume the old selection on dismissal. Voice,
sleep and theme/locale changes need the same explicit ownership handoff. This
source has a complete preserved v12 build and verified OTA/full ELF identity;
the first post-OTA functional Home check failed, so device acceptance remains
open. Product admission defaults off. Source adoption or flash identity does
not imply that the staged HA package has been activated.

### Light Color facet

To extend the existing App6 Light Detail, configure the optional
`light_color_profile` (disabled by default, requires Light Detail) with all 15
distinct widget references. Follow `modules/lvgl/pages/light_color.yaml` and
the MAIN row in `modules/lvgl/pages/light_detail.yaml`: 13 facet objects plus
the launcher and label, with product-owned geometry and capability-dependent
row widths. Keep the standard bottom-close gesture area clear. This facet needs
no new application, snapshot registration or display buffer.

Use a neutral root for native pointer capture; H/S slider children are visual,
non-clickable and non-animated. Do not attach YAML service actions to their
movement or release. The native owner retains the local draft and admits
Cancel/Apply under the existing Detail identity and generation fences. Share
the common inset/disabled appearance instead of allocating per-widget copies.
Keep the source/draft swatch independent of the global accent: after applying
the theme, call `refresh_light_color_palette()` before refreshing previews.
Do not reuse the active accent-picker widgets or its setting-writing callbacks.

The response-only `entity_detail_color_query`/`entity_detail_color_bind` pair
negotiates Color1 after Detail1 on the current channel. Keep the old Light
behavior when it is absent or rejected. Wire policy, CT switching, HA brightness
ownership and validation boundaries live in [Light Detail Color1](../architecture/ha-light-color.md).

### Climate Range facet

Configure `climate_range_profile` only beside the existing Climate Detail profile;
its upstream `enabled` option defaults to false. Supply the launcher `button`
and its child `label`, as in `modules/lvgl/pages/climate_detail.yaml`. Do not add
a second arc, application root, snapshot registration or buffer. The existing
Mode/Parameters/Range row becomes Lower/Upper/Back in the Range facet; product
flex layout yields3×156px with20px gaps,2×244px or one508px button in its508px row.
Keep the status below the dial and the standard close area at y750 clear.

Declare response-only `entity_detail_range_query` and `entity_detail_range_bind`
with the existing native populate/bind methods. The optional handshake is
independent of Color and does not change the old Detail API. Only the native
owner controls facet visibility, bound selection, pointer admission, preview
and one paired-target release; no YAML service handlers or duplicate draft
state are needed. Append Detail translations61..66 for bound labels and range
reasons; the product has67 Detail keys and1142 localized rows after this change.
Reuse existing decimal formatting and shared inset styles. MAIN pair text
must not mark a scalar target known or invent one knob position. The105
presenter uses the existing hero when the exact pair fits and the existing
localized Range caption otherwise; full values remain in the limits label.
Keep the configured font and all input authority unchanged. The paired range
is distinct from hysteresis. Read [Climate Range1](../architecture/ha-climate-range.md)
for the source/service contract and fail-closed unit policy.

### Read-only Agenda in Info

Configure optional `agenda_profile` with `enabled`, `previous`, `previous_label`,
`next`, and `next_label`; it requires Info1, not Detail or InfoContext. Keep the
upstream default disabled. Product callbacks expose `entity_info_agenda_query`
and `entity_info_agenda_bind` through the existing component methods. No extra
application, Home snapshot slot or display buffer is registered.

Reuse Calendar's existing labels/SVG and status. The product places two 244×48
buttons at (146,650) and (410,650), with non-clickable labels; hide UPDATED only
while Agenda is shown. Status ends at 742, leaving the bottom gesture from 750.
Both buttons remain disabled during a pending page or incomplete text rendering.
Do not recreate PAGE/receipt state machines or calendar fetching in YAML.

Append localized Extra keys 93..100 without changing the original 93; product
capacity is 579 keys per locale. Validate glyph fit, boundary/slide-out behavior,
semantic source cancellation and legacy Calendar restoration. Host proof is not
device acceptance. The [Agenda contract](../architecture/ha-agenda-panels.md)
owns authorization, dates, cache limits and explicit HA editor migration.

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

The direct scroll backend additionally accepts `color_format: RGB888` as an
explicit performance option; its default remains `RGB565`. Matching an RGB888
display permits the existing DMA2D copy path instead of per-frame PPA color
conversion. The same byte cap applies: calculate storage from the selected
format, resolution, stride, and complete content height. A native-format bitmap
uses more memory while the list is open and must be released on close.

When borrowing an external buffer before the first capture, query the owning
controller's `get_required_bytes()`. It includes that controller's configured
format before any direct region has been activated. Do not use a previous
region's global format or assume two bytes per pixel. The legacy C helper
keeps RGB565 as its default and accepts an explicit format. The 30 October
native-format hardware campaign is tracked in
[the performance report](touchdeck-performance-2026-10-30.md).

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

## Return a manual frame to LVGL

Perform the handoff on the LVGL owner task after the manual producer has
finished its frame. Keep its framebuffer lease and regional pause balanced;
do not infer ownership from an old generation number or add buffer copies in
product YAML.

| Entry point | Pause ownership |
| --- | --- |
| `lvgl_esphome_direct_handoff_to_lvgl(timeout_ms)` | Legacy C ABI; leaves an existing caller pause held, or balances the pause it acquires itself |
| `LvglComponent::direct_handoff_to_lvgl(timeout_ms, false)` | Same default behavior |
| `lvgl_esphome_direct_handoff_to_lvgl_and_resume(timeout_ms)` | Explicitly adopts and consumes one existing caller pause |
| `LvglComponent::direct_handoff_to_lvgl(timeout_ms, true)` | Same consuming behavior |

Use the consuming form only at the final release point of your own pause.
It consumes that one lease on failure too: never follow it with another
`direct_regions_pause(false, ...)`. At depth zero it returns false without
decrementing; at nested depth it consumes one level, returns false and does
not seed buffers. A sole lease must pass the worker barrier and DSI queue wait
before seeding. Barrier, queue and alignment failures use conservative cleanup
and cannot release another owner's remaining pause.

The component keeps the LVGL lock through seeding and resume. Only explicit
proof that all three DSI buffers were seeded permits coherent resume: under
the regional mutex it advances the base generation and writes all stamps
before publishing unpaused. Generic resume still invalidates the cached bases.
The return value means that LVGL alignment succeeded; it can remain true when
the full-pool optimization is unavailable and conservative resume was used.
Do not treat true as proof that every subsequent regional rebase was avoided.

This removes a source-proven redundant-copy path. It is not proof of the
initiating cause of a particular DSI underrun; retain separate runtime evidence
as described in the [graphics architecture](../architecture/graphics.md#coherent-handoff-and-pause-adoption).

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

Weather Lottie documents that participate in runtime theming may mark their
primary fill with the `sid` value `atmosfera-accent`. Configure the reusable
widget with `color_slot: atmosfera-accent` and update it through
`lvgl.lottie.set_color`; the action queues the change on the Lottie worker and
preserves the current animation phase. Do not add a per-frame YAML lambda or a
second full-screen buffer for palette changes. Keep secondary outlines and
semantic detail colours explicit when they must remain readable across themes.

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

### Static SVG illustrations

Use the companion `svg_icon` widget for a small, single-colour vector
illustration. It reads an SVG file at build time and retains its path geometry;
it does not convert the asset to a firmware bitmap or use `svg_loader`'s
independent render task. The product's first asset is `assets/icons/fan.svg`.

```yaml
- svg_icon:
    id: device_illustration
    file: assets/icons/fan.svg
    width: 96
    height: 96
    text_color: 0xD3E3FD
    clickable: false
```

The supported source is deliberately limited: one solid fill, a finite positive
`viewBox`, and closed paths containing absolute `M`, `L`, `Q`, `C` and `Z`
commands. Unsupported elements, transforms, strokes, filters, external images,
XML entities and differing path fills are rejected. A file is at most 64 KiB
with 256 path commands; each output dimension is at most 256 pixels. Width and
height are explicit. The aspect ratio is preserved and the illustration is
centred. `text_color` and `text_opa` supply the runtime tint and opacity; the
object starts transparent with zero border and padding.

One immutable LVGL path is built during setup and freed if the widget is
deleted. Drawing runs through the existing LVGL draw queue. It creates a
zero-origin ARGB child layer bounded to the icon, then submits that layer at
the widget's actual coordinates. For a 96x96 icon the pixel surface is 36,864
bytes plus renderer metadata, retained only until those draw tasks finish.
No icon timer, worker, canvas or full-screen pixel buffer is introduced.
Hidden icons retain only their small path state.

The bounded child layer is required: the current software vector renderer
would otherwise allocate an ARGB scratch surface covering the complete RGB888
parent layer. Do not draw a vector descriptor directly into the full-screen
layer or replace this with the older asynchronous SVG canvas loader. Native
compilation and on-device visual/lifecycle validation are still required when
admitting a new SVG widget or asset.

## Generated initialization stack

Retire the generated configuration initializer's stack frame before calling
`App.setup()`. Keep that initializer non-inlined into the small setup wrapper;
otherwise its temporary objects and register spills remain live beneath every
component's startup calls. Preserve the generated configuration and component
startup order, and check both fresh and existing generated source files.

The native87 Cover expansion exposed this boundary: its generated setup frame
grew from 9,088 to 9,280 bytes within a 12,288-byte loop-task stack. The device
reported a stack overflow during startup. SVG geometry and translations were
static; the i18n constructor still used only 16 stack bytes. Inspect compiled
frame sizes and repeat device boot tests after adding screens instead of
raising the task-stack limit to hide the retained initialization frame.

## Local translation capacity

Every configured locale entry participates in the companion `i18n` component's
generated `I18N_TRANSLATION_CAPACITY` definition. Its fixed pointer table is
sized at build time for the complete configuration, including repeated locale
packs in their original first-match order. Empty packs reserve one storage
slot; the schema rejects more than 65,535 entries, matching the counter type.
Strings remain flash-resident literals and no runtime allocation is added.
Manual registration beyond the configured capacity logs an explicit error.

On ESP32, the optional `use_flash_table: true` setting emits an immutable,
static-lifetime translation pointer table in flash. Atmosfera enables this mode
to preserve internal RAM for its existing audio tasks. Entry order, first-match
lookup, default-locale fallback and `translate_existing` semantics are unchanged.
No mutable shadow table or runtime allocation is created. Manual registration
with `add_translation` is explicitly rejected in this mode; extend the YAML
packs instead. The upstream default remains the mutable table and keeps its
existing registration and overflow behavior.

The 822-entry table contains 9,864 bytes of pointers on ESP32-P4. Moving this
metadata out of the component replaces the array with one four-byte pointer;
the expected internal saving is 9,860 bytes. Verify the final linked object,
startup order and actual audio-task startup after changing this policy. This
storage accounting alone does not establish sufficient contiguous heap or
hardware stability.

For the candidate with 574 entries on the 32-bit ESP32-P4, the three-pointer
table occupies 6,888 bytes instead of the previous fixed 6,144 bytes: a bounded
744-byte increase. The earlier 512-entry table silently dropped the last 30 of
542 entries, making the new Polish strings fall back to English. Validate the
last keys of every locale, fallback lookup and the generated count when adding
packs; a valid YAML file alone did not detect that older runtime limit.

## Optional external Media panel

The `media_controller` product composition is an optional dedicated view for an
explicit Home Assistant `panel/media` card. It uses the existing entity-control
application and negotiated Extra profile. It does not replace the local Player,
reinterpret a legacy Choice action, or infer service support from stray state
attributes. Upstream admission defaults to disabled; the product supplies the
`media_control_product_admitted` policy substitution.

`pages/media_panel.yaml` and `pages/media_volume.yaml` own static SVG, labels and
geometry. Native code owns capability filtering, input, authority, pending
commands and facet transitions. Main transport controls use a flex row: hidden
unsupported controls leave the layout, while supported but ineligible controls
remain visibly disabled. Play/Pause and On/Off each occupy one visible position.
Do not hardcode their absolute tap coordinates without resolving the visible
children first.

Volume borrows the existing bounded Scalar region and worker. Source, sound
mode and repeat borrow the existing eight-option Detail Choice tree. There is
one selected owner and active facet; no per-facet full-screen buffer or new
application snapshot is allocated. A facet handoff must complete before input
or screenshot capture, and closing must retire borrowed widgets before another
family can use them. The native backend enforces this lifecycle.

The text provider checks retained Media view state before Extra and Detail and
maps IDs 0 through 54. Keep the exact authoritative volume text separate from
the rounded drag preview. Existing normal/compact fonts are reused; a value
that cannot be displayed completely must not become an apparently precise
truncated observation. The product theme already walks their parent control
tree; SVG control icons inherit the same contrasting foreground as captions.

Configuration validation and font metrics are preparation evidence. Full native
compile, facet open/back/close, capability filtering, authoritative updates,
screenshots, memory and audio continuity remain device acceptance gates.

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
