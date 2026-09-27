# Graphics and display pipeline

This document explains where pixels are produced, which accelerator moves
them, who owns each frame buffer, and why the firmware uses both PPA and
DMA2D.

## Native Lottie publication (2026-09-19)

The raster task prepares the next ARGB surface off-thread. Native canvas
publication uses a bounded one-frame mailbox consumed by `LvglComponent::loop`.
The loop attaches the completed buffer, invalidates the widget, swaps ownership
of the two surfaces, and acknowledges the producer. There is no extra bitmap
copy or queue growth. The PPA direct presenter keeps its existing asynchronous
path. A worker-side LVGL mutex alone was insufficient: YAML actions execute on
the main loop without that mutex, and concurrent native canvas invalidation
could corrupt LVGL's event list during Home snapshot refresh.

Clock minute updates refresh only the clock region in the retained Home bitmap;
they do not regenerate the whole page or replace its frozen weather frame.

## Validated display configuration

Home weather retains its prepared canvas across a carousel handoff. Returning
to the page reveals that canvas synchronously before starting a new one-shot
clock; boot snapshot preparation time must not count as visible animation time.
The Home microphone is a child of page one and is captured/scrolled normally.
Only status icons and page indicators are fixed display chrome. Snapshot icon
rasterization uses the native label's content origin and font baseline, without
vertical centering or per-icon pixel offsets.

Inactive Home data pages 2-4 refresh one at a time every 15 seconds while the
screen is off and no input/transition/volume overlay owns the display. Page one
retains its prepared weather snapshot rather than rasterizing at swipe start.
Camera/Gallery loaders use the blue `m3_loading_contained_small` Lottie asset
and release its resources when loading ends or the application closes.

| Property | Value |
| --- | --- |
| Panel | Waveshare ESP32-P4 3.4-inch round panel |
| Logical size | 800x800 |
| Panel output | RGB888, 24 bits per pixel |
| LVGL color depth | 32-bit color semantics |
| LVGL render mode | `DIRECT`, using two full-screen buffers |
| LVGL refresh period | 5 ms |
| Display clock | 48 MHz |
| DSI lane bitrate | 1.5 Gbps |
| Frame buffers | Three, allocated and owned by the DSI display driver |
| LVGL buffers | Driver frame buffers 0 and 1 |
| Manual-compositor buffer | The currently idle member of the same three-buffer set |
| Byte order | `little_endian`, read from LVGL configuration |

LVGL uses 32-bit color semantics for widgets and sources that need alpha.
The panel scans RGB888, so the final display buffers use three bytes per pixel.
This distinction is important: an ARGB8888 source may be blended into an
RGB888 destination, but the display does not scan a four-byte framebuffer.

## Pixel path

```mermaid
flowchart LR
    OBJECTS["LVGL object tree"]
    DIRECT_WIDGET["Direct widgets<br/>wave, marquee, volume"]
    SNAPSHOT["Home/app/settings snapshots"]
    IMAGE["Artwork and gallery JPEG"]
    CAMERA["Native-size camera MJPEG"]
    LOTTIE["Lottie/ThorVG"]

    SW["LVGL software draw"]
    PPA["ESP32-P4 PPA<br/>SRM, selected blend"]
    DMA2D["ESP32-P4 DMA2D<br/>2D memory copies"]
    JPEG["Hardware JPEG<br/>decode/encode"]

    FB0["DSI frame buffer 0"]
    FB1["DSI frame buffer 1"]
    FB2["DSI frame buffer 2"]
    SCAN["DSI scanout"]

    OBJECTS --> SW
    OBJECTS --> PPA
    DIRECT_WIDGET --> PPA
    SNAPSHOT --> PPA
    SNAPSHOT --> DMA2D
    IMAGE --> JPEG
    JPEG --> PPA
    CAMERA --> JPEG
    JPEG -->|"direct idle lease"| FB0
    JPEG -->|"direct idle lease"| FB1
    JPEG -->|"direct idle lease"| FB2
    LOTTIE --> PPA

    SW --> FB0
    SW --> FB1
    PPA --> FB0
    PPA --> FB1
    PPA --> FB2
    DMA2D --> FB0
    DMA2D --> FB1
    DMA2D --> FB2

    FB0 --> SCAN
    FB1 --> SCAN
    FB2 --> SCAN
```

The arrows show possible paths, not simultaneous writes. Buffer ownership
decides which destination is legal for a particular frame.

## Why `DIRECT` and full-screen buffers

`DIRECT` means LVGL draws into display-driver frame buffers rather than a
separate software staging buffer. It removes a mandatory full-frame copy.

The product currently also sets `full_refresh: true`, but `direct_mode: true`
has precedence when ESPHome calls `lv_display_set_buffers()`. The effective
LVGL mode is therefore `LV_DISPLAY_RENDER_MODE_DIRECT`, not
`LV_DISPLAY_RENDER_MODE_FULL`. Native LVGL refreshes may update only invalidated
areas, while LVGL keeps its two direct buffers coherent.

Full-screen buffers are still required because each direct buffer is a complete
scanout surface. Snapshot and direct-region compositors can acquire the third
idle DSI buffer, compose a complete frame there, and present it manually.

## Triple-buffer ownership

At 800x800 RGB888, one frame buffer is:

```text
800 * 800 * 3 = 1,920,000 bytes = 1.83 MiB
```

The three display-owned buffers therefore occupy 5,760,000 bytes, or about
5.49 MiB.

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Rendering: acquire idle buffer
    Rendering --> Staged: cache sync completed
    Staged --> Queued: queue at frame boundary
    Queued --> Active: DSI begins scanout
    Active --> Idle: next frame becomes active
```

The driver tracks presented, active, queued, and staged indices atomically.
Manual rendering may only acquire a buffer that is none of those active
ownership states.

An external full-screen session, such as native-size camera presentation, is
the exclusive owner of this pool until it ends. The session pauses and drains
the direct-region compositor before acquiring its first lease. While the
session is active, the driver rejects frame queues from LVGL and independent
regional workers; otherwise a late widget frame can replace a camera frame or
leave LVGL with a stale base. On return, the active frame is made CPU-coherent,
the session ends, both LVGL direct buffers are realigned, and only then are
regional workers resumed.

LVGL normally uses buffers 0 and 1. Buffer 2 is not a fourth hidden copy: it is
the third member of the same display-owned pool and provides an idle target for
snapshot and direct composition. After a manual frame is presented,
`realign_direct_buffer_after_manual_present()` reconnects LVGL to a coherent
base. When native LVGL resumes, the final manual frame is seeded into both LVGL
buffers through DMA2D. This is a transition-boundary copy, not a per-frame
copy.

Skipping this synchronization is valid only when the next owner explicitly
guarantees a complete redraw of the screen and every active overlay before
either LVGL buffer can be scanned. Invalidating only the active screen is not
enough when top-layer widgets or direct regions remain visible.

### Native `DIRECT` dirty-region handoff

Native LVGL rendering also has a frame-boundary ownership rule. LVGL can issue
several flush callbacks for one frame. During the intermediate callbacks, the
second LVGL buffer may still be the DSI scanout source and must not be updated
just to keep the two `DIRECT` buffers coherent.

The component therefore:

1. records dirty rectangles in a fixed-capacity list;
2. writes back only the newly rendered source rectangle after every flush;
3. presents the frame on the last flush;
4. waits for the DSI frame boundary;
5. copies the accumulated dirty rectangles into the now-idle LVGL buffer;
6. clears the list for the next frame.

Overlapping rectangles are merged. If the bounded list fills, it collapses to
one enclosing rectangle instead of allocating memory in the flush callback.
On a frame-boundary timeout, synchronization is skipped rather than risking a
write into the active scanout buffer. The warning
`DIRECT frame boundary timed out` must be treated as a display ownership
failure, not hidden by copying earlier.

## Accelerator responsibilities

### DMA2D

DMA2D is used for deterministic 2D memory movement:

- copying RGB888 spans and complete frames;
- asynchronous LVGL flush/staging work;
- selected application transition operations;
- hardware JPEG support and associated color conversion through the IDF
  integration patch;
- synchronizing complete bases when a consumer explicitly needs it.

The current M2M path batches aligned spans and uses internal-memory
descriptors. Cache synchronization surrounds DMA access. DMA2D is preferred
when the operation is fundamentally a copy and does not require geometric
sampling or alpha composition.

### PPA SRM

PPA scale/rotate/mirror is used for:

- RGB888 snapshot movement;
- image scaling and rotation;
- gallery pan and slideshow transforms;
- direct-region copies;
- Lottie XRGB/ARGB conversion to the RGB888 display target;
- application transition geometry where supported.

SRM is the preferred accelerator for transformed images because it performs
sampling and destination writes without making the CPU touch every pixel.

### PPA blend

PPA blend is used only on validated explicit paths, such as compositing an
ARGB888 direct widget over an RGB888 base.

The generic LVGL RGB888 fill and blend draw-unit handlers remain restricted.
On ESP32-P4 they have produced short horizontal artifacts in cached PSRAM.
`use_ppa_blend: true` therefore means the capability is compiled and safe
explicit paths may use it; it does not mean every LVGL RGB888 blend operation
is routed through hardware.

Masked, rounded, unsupported, or small operations may still fall back to the
LVGL software renderer. This is intentional.

### Selection table

| Operation | Preferred engine | Reason |
| --- | --- | --- |
| Full RGB888 frame copy | DMA2D | Simple 2D copy with bounded descriptors |
| RGB888 image pan/scale/rotate | PPA SRM | Hardware geometric transform |
| ARGB8888 overlay on RGB888 base | Explicit PPA blend | Alpha composition without CPU pixel loop |
| Generic rounded LVGL widget | LVGL software or validated PPA path | Masks and RGB888 correctness take priority |
| JPEG decode/encode | ESP32-P4 JPEG peripheral | Avoid software codec and extra color pass |
| Native-size full-screen camera JPEG | JPEG directly to idle DSI frame | Avoid decoded RGB allocation and per-frame PPA copy |
| Home/app snapshot movement | PPA/DMA2D direct compositor | Avoid LVGL tree redraw |

## Reusable image scene transitions

`lvgl_image_presenter` separates image transport and decoding from display
presentation. The player uses it with `motion: none` and `crossfade: true`;
gallery and camera views can use the same owner with their own motion policy.

For a continuous source whose first frame may arrive much later than the page,
`defer_direct_session_until_frame` leaves LVGL in control of the loading scene.
The producer task signals that one complete encoded frame exists, while the
LVGL task owns the subsequent DSI-session begin/end lifecycle. The readiness
frame is dropped and the next frame enters the direct decode path. Never move
the session acquisition into the producer task: DSI presentation mutexes must
be released by the same task that acquired them.

On the validated ESP32-P4 RGB888 DSI path a crossfade does not create a second
LVGL image widget and does not invalidate the full screen for every animation
step. Its ownership sequence is:

1. `prepare_transition` runs before the decoder replaces or reuses the image
   source buffer and immediately takes direct-image ownership of the DSI pool.
   There must be no decoder-to-worker gap in which a dynamic region can queue
   a complete framebuffer from the previous artwork generation.
2. Registered dynamic regions keep producing updates, but while the scene
   transition owns DSI those updates only replace their cached ARGB overlays;
   they cannot independently present a framebuffer.
3. The currently presented DSI framebuffer remains the immutable old scene.
4. LVGL renders the complete incoming scene once into one temporary RGB888
   frame sized from the runtime display dimensions. The render includes the
   bottom, active-screen, top and system layers, so global overlays such as the
   clock survive the handoff.
5. Background copies required by direct widgets are completed before the
   crossfade starts. The player wave keeps three bounded RGB565 backdrop crops:
   active, in-flight and next. A replacement crop can therefore become active
   without waiting for, or overwriting, the source of an older PPA request. A
   task-owned PPA blend client then crossfades the old DSI frame into the final
   scene on the worker core. The pinned old DSI frame already contains the last
   direct overlay, so each direct region also preserves one compact clean
   background at transition start. After every full-frame blend, the compositor
   replaces that region with the matching clean old-to-new background blend and
   only then applies the newest registered ARGB overlay once. The player wave
   and marquee therefore remain live during an artwork change without briefly
   becoming thicker from two overlapping generations.
6. The final frame is handed back to LVGL and the temporary frame is released.

The full-screen PPA operation must not hold the direct-region metadata mutex.
During that operation region producers run in cache-only mode: they update the
latest compact ARGB overlay but cannot queue a DSI framebuffer. The crossfade
worker takes the mutex only after the full-screen blend, restores the clean
background below each region, and composites the newest cached overlay into the
completed frame. Holding the mutex across the 800x800 blend made the wave wait
roughly 50-70 ms for every artwork frame even though the wave itself occupies
only a small part of the screen.

At opacity zero the already visible old DSI frame is retained without issuing
a redundant full-screen blend. At full opacity an RGB888 PPA SRM copy reads
only the incoming scene instead of making the blend engine read both complete
frames. Intermediate opacity levels still require a full old/new blend.

The presenter owns LVGL display invalidation for this entire transaction.
Decoder and product YAML callbacks must not toggle invalidation separately.
Every success, cancellation, timeout, and decode-error path returns ownership
through the presenter, which re-enables invalidation and invalidates the active
screen. This keeps panels opened during an artwork transition renderable rather
than merely visible in the LVGL object tree.

A direct region taking part in this transition is cached as a
background-independent ARGB overlay. Never preserve its already composited RGB
rectangle: that rectangle contains the artwork generation visible when it was
produced and can paste a second or third cover over the current crossfade. Both
the transition worker and live direct-region updates blend ARGB in place over
the current target framebuffer.

The one-shot LVGL render of the incoming scene must exclude any native widget
whose pixels are also preserved as a direct-region overlay. Otherwise the
crossfade frame contains the widget once and the direct compositor blends it a
second time. `capture_exclude` declares these objects for an image presenter;
the player excludes its native wavy-progress image and preserves only the live
ARGB direct region.

The source is allowed to reuse the same decoded allocation. The old pixels are
owned by the pinned DSI framebuffer, not by a second artwork allocation. This
is why pointer equality between the old and new image descriptors must not
disable the direct-scene path.

The first player artwork follows the same path even though the decoded image
widget is still hidden behind a separate placeholder. `prepare_transition`
pins that visible placeholder scene before JPEG decode. The completed scene
then reveals the artwork widget, hides the placeholder, and crossfades from the
pinned DSI frame without allocating a placeholder-sized image buffer.

Gallery motion is exposed as the `slideshow` image option and implemented by
`SlideshowController`. The name describes the reusable presentation owner; it
does not imply zoom. The current Atmosfera gallery configures pan-only motion.

The preferred crossfade workspace is one full RGB888 frame. If PSRAM is
fragmented and no contiguous full-frame block exists, the controller allocates
one 64-row RGB888 band and performs the same full-resolution PPA SRM plus blend
transition band by band. This is a memory fallback, not a quality fallback: it
does not reduce source dimensions and never enters a CPU pixel loop. The band
and any full-frame workspace are released when the Gallery application closes.

Pausing the gallery for its controls does not recenter, retransform, or redraw
the source image. `pause_for_overlay()` copies the exact currently presented
DSI frame into one transient RGB888 surface, ends the direct slideshow lease,
and lets LVGL draw the controls over that frozen frame. Hiding the controls
returns ownership to the slideshow worker. This avoids the striped paused
frame previously produced by reconstructing a centered image through a second
render path.

Manual Previous and Next use that same frozen frame as the outgoing transition
source. The button handler hides the controls without resuming pan, fetches or
selects the requested image, and lets `transition_to()` re-enter direct mode
from the paused overlay capture. The hardware PPA crossfade is therefore the
same path as an automatic slideshow change. Calling `resume()` before the new
JPEG is ready is incorrect: it restarts motion on the current photo and makes a
button press look like a reset to the beginning of the same image.

The optional fade transition is scheduled before the pan duration expires.
The product currently uses a 1.2-second lead, so fade-out overlaps the final
part of motion instead of beginning after the image has visibly stopped.

The compressed successor is fetched shortly after the current image becomes
visible, but hardware decode remains deferred until that transition window.
This removes network latency from the end of a pan without adding a second
decoded photo for the whole slide.

Closing the gallery is an ownership boundary. The exact-frame scratch surface
may remain the LVGL image source while the application-close snapshot is being
captured, so `pause_for_snapshot()` must not release it at that point. After the
close snapshot owns a complete copy, `SlideshowController::clear()` detaches
the LVGL source and releases transition/subpixel buffers; only then may the
decoded artwork allocation be returned. Reversing this order leaves the image
widget pointing at freed PSRAM and produces the striped previous image on the
next open.

The temporary memory cost is one display-sized RGB888 frame during a transition
or while the exact-frame controls overlay is visible. Unsupported targets fall
back to an immediate source change; they must not emulate this path by redrawing
two full-screen LVGL widgets on every frame.

A direct marquee returns to its initial position through its registered direct
region. Once that frame is confirmed, the region remains parked at position
zero and submits no more frames. Releasing it immediately would expose the last
scrolled strip from another DSI framebuffer; normal panel/app handoff or a new
title releases and rebuilds it explicitly.

The global volume overlay captures the screen once on touch-down. Its prepared
dimmed frame removes the clock by rendering and patching only the clock-sized
rectangle. Long-press activation reuses that frame instead of performing a
second full-screen capture and scrim pass.

Activation is a single presented frame. `begin(value, visual)` composes the
scrim, complete inactive and active arc, knob, and percentage into an idle DSI
frame before that frame is queued. It then repairs the retained background
copy for incremental updates. Presenting the scrim first and adding the label
or arc in later calls is forbidden because it creates the visible two-step
flash reported by users. Drag updates are coalesced on the renderer worker and
redraw only the union of the old/new knob path and percentage label.

The clock patch is conditional. Camera intentionally suppresses the clock for
the entire application lifetime, while the touchscreen still treats the same
top-centre coordinates as the volume gesture activation area. In that state
the renderer must not reconstruct a clock-sized rectangle: doing so paints a
black box into an otherwise direct-rendered camera frame and leaves it visible
briefly after the arc closes.

Full-screen direct image producers cannot continue writing while that capture
is used as an overlay base. `DirectSceneController` is the common suspension
contract for Gallery and Camera. The volume renderer suspends every registered
controller immediately before capture. When the gesture ends it restores the
original frame, releases the overlay presentation session, and synchronously
lets the visible direct producer reacquire its own session while LVGL
invalidation is still disabled. Only then may LVGL invalidation be enabled
again. This preserves one writer for the DSI pool and prevents Gallery
artifacts or Camera frames covering the arc. A new full-screen direct producer
must be added to `scene_controllers`; it must not be fixed with timing delays or
per-screen YAML branches.

Suspending producers and disabling new LVGL invalidation are necessary but not
sufficient. A refresh queued before the gesture can still flush an undimmed
LVGL framebuffer after the full scrim has been presented. For the complete
direct-overlay gesture, the renderer therefore owns an LVGL framebuffer
presentation session. The session pauses the LVGL refresh timer, drains direct
regions and pending DSI work, and keeps that ownership through every regional
arc/knob update. The original complete frame is restored before the session is
released and Gallery or Camera is resumed. Without this session, an old flush
can remove the scrim globally while later regional updates redraw it only below
the moving knob, which appears as large undimmed image rectangles.

When moving Gallery is suspended, it already owns an exact 800x800 RGB888
capture used to freeze its current pan position. It exposes that immutable
surface through `DirectSceneController::get_direct_overlay_frame()`, and the
volume renderer borrows it until Gallery resumes. The renderer never frees a
borrowed surface and does not allocate or capture a duplicate original frame.
The product's paused Gallery state also retains this exact capture, so it lends
the same surface without rebuilding the transformed photo. Both paths disable
LVGL invalidation and hold the framebuffer presentation session while the
direct arc owns DSI. Teardown follows one strict order: restore the complete
base frame, release the overlay presentation session, resume the suspended
producer and let it reacquire its direct session, then re-enable LVGL
invalidation. A black Camera flash at this boundary is not the previous video
frame; it is the black native LVGL Camera page exposed by an ownership gap.
Do not call `lv_refr_now()` after the direct handoff; it races the resumed
full-screen producer and reintroduces striped native-LVGL rows.

## Direct-region compositor

The direct-region compositor updates a small dynamic region while preserving
the rest of the active frame. It is used by the wavy media control, marquee,
volume overlay, Voice waveform, and looping weather Lottie.

When a direct renderer replaces a native LVGL object, its first frame must be
an atomic and non-blocking handoff. The marquee temporarily hides the native
title only while rendering the bounded clean background into an off-screen
RGB888 strip, then restores it before returning to the event loop. Its worker
presents the first direct text frame asynchronously. The main LVGL task hides
the native label only after the matching direct-region slot has accepted the
position-zero frame. That hidden-flag mutation is performed with display
invalidation temporarily suppressed: the panel therefore keeps scanning the
old native pixels until DSI replaces them with the prepared direct frame,
instead of publishing one empty title strip. The temporary hide/restore used to
capture the clean background follows the same rule. The motion clock starts on
the following UI tick, so the handoff cannot surface an already-offset first
animation frame as a title blink. A rejected or busy request is retried while
the native title remains visible; a timeout leaves the static native title in
place. Never call
`lv_refr_now()` with the native label hidden and never wait synchronously for a
generic DSI frame, because the former exposes an empty title region and the
latter stalls `lv_timer_handler()` without proving that the marquee was shown.

It owns:

- four registered region slots;
- an eight-request queue;
- a 6 KiB worker stack;
- a generation number for each DSI buffer;
- a barrier used by page and application handoff.

```mermaid
sequenceDiagram
    participant Widget as Direct widget worker
    participant Region as Direct-region compositor
    participant DSI as MIPI DSI driver

    Widget->>Region: submit region and generation
    Region->>DSI: acquire idle frame buffer
    Region->>Region: copy current base if generation is stale
    Region->>Region: PPA copy/blend updated regions
    Region->>DSI: cache sync and queue frame
    DSI-->>Region: frame boundary/presented
```

The generation mechanism prevents a region rendered over an old base from
being presented after LVGL or navigation has changed the screen. Before a
snapshot, page switch, or app transition, navigation pauses the region
compositor and waits on its barrier. Resuming increments the base generation.
The final DSI queue operation also verifies, under the submission lock, that
the active framebuffer is still the base used for composition. This closes the
smaller race between the last generation check and serialized DSI submission.
Every completed direct framebuffer release advances the base generation, even
when the same physical DSI buffer becomes active again. Physical address
identity does not prove pixel identity: JPEG, Lottie, Camera, or an application
animation may have rewritten that buffer. Keeping the old generation lets a
regional renderer reuse a stale clean base and produces horizontal blend
artifacts on the next update.

Pause ownership is reference-counted. Navigation, image presentation, and a
modal notification may overlap, so the first owner drains the queue and only
the last owner resumes submissions. A component must release exactly the pause
it acquired, including timeout and error paths. Notification dismissal is
finished from the component loop rather than an LVGL animation callback: the
callback only marks completion, avoiding a nested `lv_refr_now()` during
animation processing.

Direct widgets must retire a completed in-flight frame even while presentation
is temporarily disabled. A widget that composites a private background must
also keep that background independent from its ARGB overlay and reserve every
buffer referenced by an in-flight PPA request. The wavy control blends its
RGB565 crop directly with ARGB8888; it does not convert the crop to RGB888 or
rerasterize all wave buffers when artwork changes. Without these ownership
rules, a background handoff can wait forever for a spare buffer or paste an
obsolete artwork rectangle below an otherwise correct overlay.

Animation-frame updates may use a short try-lock and coalesce when the raster
worker is busy. A new artwork backdrop is different: it is a mandatory state
handoff and must wait for ownership of the renderer mutex. Dropping that update
leaves the previous cover embedded below every later wave frame even though the
main artwork widget already shows the new source.

No additional full-screen region buffer exists. The compositor uses the three
DSI buffers and bounded per-widget sources.

A stopped direct widget must not be carried forward by copying its pixels from
whichever physical framebuffer happens to be active. Other direct regions can
still present frames after the widget stops, and one of the three DSI buffers
may contain an older animation phase. The compositor therefore marks a final
ARGB overlay as a stable carry, keeps one bounded copy of that overlay, and
reblends it over the current compact background whenever another region builds
a frame. This prevents marquee or artwork updates from resurrecting old
play/pause glyphs or wave phases without synchronizing a full screen.

The same reconstruction is mandatory when native LVGL rebases its `DIRECT`
render target. Copying the region from the currently presented framebuffer at
that boundary can import an older phase from another member of the DSI pool,
then visibly snap back when the regional compositor restores the stable carry.
Stable slots must instead rebuild the target from their clean background and
cached final ARGB overlay.

### Player transport wave state

The confirmed playback rotation and the transient loading sweep use separate
phases. `playing` and `pending` are submitted as one renderer transaction, so
an intermediate play glyph, pause glyph, or progress frame cannot reach DSI.
The loading segment is intentionally delayed by one second, so a transport
action that is confirmed quickly does not flash a short-lived spinner.
Touch-down freezes the base wave before LVGL can emit `CLICKED` on release,
and the release cycle discards any phase step accumulated with that input
transition. Command dispatch keeps it frozen. Before the delayed loader becomes
visible no phase advances; afterwards only the independent loader phase
advances until transport confirmation arrives. A touch released outside the
button resumes normal playback animation on the next display tick.

The renderer retains the exact progress value while a slow action is pending,
but temporarily draws a complete inactive wave plus the bright moving loader.
This keeps a 100% stream progress ring from hiding the loader. When the backend
acknowledges the action, the saved progress reappears without being reconstructed
from delayed position metadata. A confirmed paused frame is then marked as the
stable direct-region carry described above.

Transport feedback has an explicit confirmation type. `PLAYING` confirms play,
`IDLE` confirms pause, and changed track metadata confirms previous/next.
Position, duration, and duplicate metadata updates must not release feedback;
otherwise they briefly restart the main wave before the real state arrives.

SendSpin reports pause as `IDLE` and may publish a transient stale or near-zero
position while the previous `PLAYING` state is still visible. At command start,
the product captures the progress value directly from the material renderer.
That value has priority over title, position, duration and state echoes until
the command-feedback window closes. The same rule preserves the synthetic 100%
track used for an unbounded stream. Never recompute paused progress from a
delayed position echo or let a repeated title update replace this hold value.

## Hardware JPEG path

Artwork, gallery images, and compressed snapshots use the ESP32-P4 JPEG
peripheral. The important rules are:

- derive RGB order and byte order from display/LVGL configuration;
- decode into a reusable destination with known stride and capacity;
- avoid an intermediate full-screen RGB buffer when the destination can be
  leased directly;
- synchronize only the written range before PPA, DMA2D, or DSI consumes it;
- keep the old image valid until the replacement is completely decoded;
- publish the new source atomically, then refresh the affected LVGL/direct
  region;
- release the replaced buffer only after no display or worker still references
  it.

Full-screen camera MJPEG has a stricter fast path. If the encoded frame exactly
matches the display geometry and RGB888 stride, the JPEG peripheral writes into
an idle DSI framebuffer lease and the driver presents that lease at VSYNC. PPA
is bypassed. Geometry mismatch falls back to a reusable decoded source plus PPA
SRM; it must never silently turn into a static LVGL image while decode counters
continue to rise.

The current artwork path retains its decoded 800x800 RGB565 surface across
Player closes. Reopening Player can therefore present the last cover without a
new download or decode. SendSpin also retains the latest bounded compressed
input.

Gallery reserves one 1632x912 RGB565 hardware-JPEG destination after boot cache
preparation, while PSRAM is still contiguous. The active image is returned to
that exact reusable allocation when Gallery closes; stale presentation
generations and transition workspaces are released. This avoids an
order-dependent allocation failure after Camera or Player has fragmented the
heap without lowering source resolution. Gallery's encoded buffer remains
bounded. Hardware JPEG reduces codec CPU time and compressed storage, not the
size of the displayed pixels.

Pan uses fractional source coordinates for both decoder output formats. The
PPA SRM subpixel path accepts RGB565 as well as RGB888 and derives bytes per
pixel, source stride, and blend format from the image descriptor. This matters
most for portrait photos: their narrow RGB565 source must be scaled while it is
panned vertically. Falling back to integer crop coordinates repeats the same
row across several display frames and looks like low FPS even when the worker
is meeting its frame budget. On the 800x800 panel the validated portrait path
uses one reusable 512 KiB band workspace and renders in about 31 ms per frame;
the landscape path remains around 19-21 ms per frame.

## Gesture velocity and snapshot lifecycle

The shared gesture router owns axis capture and release velocity. It measures
instantaneous velocity from touchscreen samples and preserves a whole-gesture
estimate for short, sparsely sampled flicks.

- Home hands horizontal release velocity to the snapshot compositor.
- The settle duration accounts for the initial derivative of LVGL cubic
  ease-out, so the first frame after release continues near the finger speed.
- Settings hands vertical velocity to the snapshot scroll compositor. The
  scroll controller must not calculate a second independently filtered
  velocity, because that suppresses short flicks.
- Product thresholds remain declarative. The round display currently uses a
  two-pixel start distance and one-pixel axis bias for Home and Settings.

Settings owns its decoded scroll bitmap only while the application is open.
It does not allocate that bitmap from the heap. Gallery and Settings are
mutually exclusive, so Settings loans Gallery's boot-reserved contiguous arena,
captures directly into it through an externally owned LVGL draw buffer, and
returns the exact pointer after the scroll worker has drained. The current
Settings content uses 3,213,600 bytes; the aligned arena is 3,213,632 bytes and
also satisfies Gallery's 2,976,768-byte padded RGB565 decode requirement.
Closing Settings, including while inertia is active, ends the scroll compositor
before the pointer is detached and returned. Failed loans, undersized external
buffers, and fallback capture allocation emit diagnostics with required and
available capacities.

The Settings open lifecycle first applies every persisted control, cancels the
refreshes generated by that batch, and then performs exactly one synchronous
capture into the loaned arena. While Settings remains open, unchanged gestures
reuse that raw bitmap without JPEG encode/decode or allocation. A control
change schedules a short coalesced refresh and overwrites the same allocation
in place; it does not release the bitmap between drags. The current hardware
benchmark is 59 FPS over 79 frames, 16.35 ms average, 22.9 ms maximum, with no
failed frames.

### Home tile-window ownership

Home keeps three decoded RGB888 slots for the visible page and its immediate
neighbours. Moving the three-page window can recycle one outgoing slot by
encoding its dirty contents and decoding the incoming page on a background
worker. The slot has explicit ownership while that work is in progress:

- a busy slot is not addressable through either its outgoing or incoming page;
- the `page -> slot` mapping is published only after the complete JPEG decode
  and required cache synchronization succeed;
- after settle, prefetch is symmetric around the committed page rather than
  biased by the last swipe direction. Page 1 keeps pages 1-2, page 2 keeps
  pages 1-3, page 3 keeps pages 2-4, and page 4 keeps pages 3-4. This makes an
  immediate reverse swipe use an already decoded neighbour instead of exposing
  a black page while JPEG decode catches up;
- a failed or partial decode invalidates the slot mapping instead of exposing
  partially written pixels under the outgoing page;
- the swipe and JPEG workers are created while Home is prepared at boot, not
  on the first movement sample;
- the normal gesture-start path binds the already decoded slots only. Exposing,
  aligning, and laying out live LVGL page trees is reserved for the exceptional
  fresh-snapshot fallback;
- after settle, the exact final snapshot remains displayed until background
  prefetch finishes and the native target has been scheduled for redraw. The
  LVGL loop must not block waiting for the JPEG worker;
- the final handoff asks the navigation controller to re-establish exactly one
  visible, centred Home widget before invalidating it. Invalidating a widget is
  not sufficient if an interrupted transition left that widget hidden;
- The product uses a two-pixel Home start distance. This filters one-pixel
  GT911 coordinate jitter that otherwise nudges the carousel during a tile tap,
  while still capturing a real drag before it becomes visually perceptible.
  A stationary touch remains available to normal click handling.
- Home defers delivery of the initial press to LVGL. A stationary tap is
  replayed as a short press/release pair, but a captured drag never applies a
  tile's pressed style and therefore cannot invalidate the tile at swipe start.
- A contact beginning while an application transition owns the display enters
  a blocked navigation context and remains consumed until physical release.
  This closes the short interval after the close animation is visually complete
  but before Home snapshots and native input ownership are restored. Such a
  contact must neither begin a carousel drag nor replay as a tile click.
- A new touch during settle pauses the direct worker at its last presented
  coordinates. The next drag uses that offset as its origin, and crossing a
  page boundary rebases the current/next pair without ending direct ownership.
- Edge return uses smooth in/out timing rather than the committed-page
  velocity curve. Keep this policy separate so edge resistance can be softer
  without making ordinary page changes feel sluggish.

Animated content on a Home page is stopped at touch-down, before gesture-axis
capture. Waiting for the first captured horizontal pixel allows one final
animation frame to contend with the first carousel frame and produces a
visible start hitch. After a finite weather animation completes, its managed
snapshot is refreshed from the currently presented DSI frame only for the
weather tile rectangle. It must not redraw or recapture the complete 800x800
page. The current 680x302 region capture costs about 53-61 ms; the former full
page path cost 174-250 ms and could run inside the interaction window.

These rules prevent two distinct symptoms: a full-tree layout hitch at the
first captured pixels of a drag, and random black or partially decoded pages
when a recycled slot is read under its old identity.

On 2026-07-31 the 800x800 ESP32-P4 hardware tests exercised both cache windows,
edge bounce, cancelled drags, and first-pixel capture. An 84-gesture stress run
completed without a reset or DSI underrun. One compositor frame failed while
the API deliberately flooded the router; the handoff recovered and the native
Home page remained available.

On 2026-08-10, after moving weather refresh out of the gesture path, synthetic
hardware tests measured:

| Interaction | Frames | Effective rate | Average frame | Maximum frame | Failed frames |
| --- | ---: | ---: | ---: | ---: | ---: |
| Home page 1 to 2 | 31-32 | 55 FPS | 17.4 ms | 23.7-25.8 ms | 0 |
| Immediate chained page 2 to 3 | 45 | 55 FPS | 17.4 ms | 24.4-29.6 ms | 0 |
| Settings snapshot scroll | 79-82 | 58-59 FPS | 16.3-16.5 ms | 24.0-24.4 ms | 0 |

These are regression thresholds for the direct compositor, not native LVGL
rendering targets. A result obtained only after lowering global PPA/DSI burst
settings is not equivalent because it trades away unrelated UI throughput.

After introducing the Gallery/Settings arena lease on 2026-08-16, Settings
measured 57 FPS over 79 frames (16.9 ms average, 26.1 ms maximum, zero failed
frames). Gallery subsequently reused the returned arena for hardware JPEG, and
a second Settings open captured into the same pointer. This sequence is the
required ownership regression test; an isolated Settings benchmark does not
prove that the arena was returned correctly.

## Lottie and vector animation

The Lottie JSON is small, but rendering is not free. ThorVG expands the vector
scene into working data and ultimately produces raster pixels. The boot
animation can optionally pre-render frames to PSRAM for stable playback. That
cache is approximately 11 MiB for the current asset and is deliberately:

1. allocated while PSRAM is still contiguous;
2. used for one-shot boot playback;
3. reduced to the final retained frame;
4. released before Home and application caches are completed.

PPA can accelerate conversion and presentation of opaque or alpha frames, but
it does not execute the Lottie vector scene itself. Smooth vector playback
therefore requires either bounded pre-rendering or a sufficiently light scene.
Every CPU fallback that copies a cached Lottie frame into PSRAM must perform a
CPU-to-memory cache synchronization before PPA or DSI can read it. The PPA path
already establishes that ownership; omitting it only in the fallback can make
the first boot frame appear as a translucent corrupt rectangle.

Finite opaque weather animations use a different bounded path from the
one-shot boot animation. The LVGL canvas is attached once to an immutable
initial RGB888 frame. ThorVG then renders subsequent frames into one private
RGB888 source buffer and submits that buffer to the direct-region compositor.
The renderer cannot reuse the source until the asynchronous PPA completion
callback returns ownership. This avoids both a second post-render frame copy
and per-frame `lv_canvas_set_buffer()` calls. Rebinding the canvas every frame
invalidates LVGL's image cache and can eventually double-free its static canvas
descriptor.

An opaque direct Lottie object remains hidden until its first prepared PPA
frame is ready. Revealing it must not invalidate the native LVGL canvas: that
canvas still contains the cleared black allocation and can be flushed before
the direct frame, which appears as a black rectangle with stale horizontal
pixels. The direct completion path reveals the object without scheduling that
intermediate native redraw. Alpha/non-direct Lottie keeps normal invalidation.

The product weather policy is one cycle per visibility epoch. A restart resets
the monotonic animation clock instead of attempting to catch up elapsed hidden
time. It starts that new cycle at the phase represented by the retained frame,
so the snapshot-to-live handoff does not briefly reveal an unrelated first
frame. At completion the renderer retains the most recent sampled frame with
real foreground coverage because a Lottie out-point can legally be blank. It
then contracts the existing XRGB allocation in place to RGB888, attaches that
allocation to the canvas, releases the direct region, and requests one managed
Home snapshot refresh. The last weather image therefore survives both native
LVGL redraw and snapshot-backed carousel movement without another full image
allocation.

The render task runs on the core opposite the ESPHome loop task. Do not infer
the loop core from `CONFIG_ESP_MAIN_TASK_AFFINITY`: ESPHome creates `loopTask`
with its own affinity in `esp32/core.cpp`. Only the selected weather condition
runs; the other parsed animations remain hidden. The current 270x270 condition
retains about 633 KiB and measured roughly 33-35 FPS with an 8.9-9.6 ms average
ThorVG render cost.

Full-screen overlays must pause and drain this path before becoming visible.
Otherwise a late weather frame can be submitted after LVGL drew the overlay and
appear above its scrim. The renderer resumes only after the underlying native
frame has been restored and presented.

Home navigation follows the same ownership rule. The weather direct region is
suspended at touch-down and resumes only after the native target page is
presented plus its short settle delay. Returning to the weather page starts a fresh
single cycle from its retained native frame, so the snapshot cannot expose an
unowned first Lottie frame between navigation and animation startup.

The weather tile pressed state is also direct-rendered. Touch pauses and drains
the Lottie region, presents one bounded darkened tile surface, and resumes the
animation after release. A normal LVGL pressed style below an independently
presented Lottie surface is both visually incomplete and unsafe: the Lottie
rectangle would remain bright while the underlying tile redraw can race the
direct region and produce horizontal blend artifacts.

Stopping or hiding an active animation is also an ownership boundary. Wait for
the in-flight callback, release the registered direct region, and only then
suspend the task or free its private buffers. A timeout may retain memory for
safety, but it must never free a source still readable by PPA.

A hidden or disabled regional renderer must block until visibility or state
changes explicitly wake it. It must not self-notify after direct presentation
is disabled: on FreeRTOS that turns an invisible priority-2 worker into a busy
loop which can starve priority-1 HTTP and JPEG workers on the same core.

Small loading indicators use `MaterialDirectSpinner`, not a native LVGL spinner
on the full-refresh display. It precomputes two bounded RGB888 frames and
presents only the spinner rectangle through the direct-region compositor.
Camera and Gallery therefore keep a live 30 FPS loader while network/JPEG work
runs without invalidating the complete 800x800 tree on every tick.
Application-cache preparation may instantiate these page loaders, but it must
stop them again before Home is revealed. A preparation-only spinner left active
becomes an invisible direct-region producer and can appear later at screen
centre when another ownership transition resumes direct composition.

Do not keep a hidden one-pixel Lottie object as a dependency or compatibility
anchor. A hidden player animation previously continued rasterizing weather
frames at roughly 60 FPS and consumed renderer bandwidth even though no pixels
were visible. A compatibility script may remain a no-op; an invisible Lottie
runtime must not remain active.

A managed snapshot must not reposition a currently visible full-screen root to
obtain centered coordinates. Such a move invalidates the live DIRECT scene and
allows an independently scheduled regional frame to expose the intermediate
black framebuffer. If the object already covers the active display at `(0,0)`,
snapshot it in place; the align/restore path is reserved for hidden or
off-screen pages.

## Cache coherency rules

PSRAM is cached. Hardware engines and the CPU do not automatically see the
same bytes at the same instant.

Use the direction that matches ownership:

- CPU produced data, hardware will read: write back CPU cache to memory.
- Hardware produced data, CPU will read: invalidate CPU cache after hardware
  completion.
- Hardware produced data, another hardware engine will read: wait for the
  producer, synchronize the written range as required by the IDF API, then
  start the consumer.

Never synchronize an arbitrary full buffer merely because a small region
changed. Excessive cache operations consume the same PSRAM bandwidth needed by
DSI scanout.

## Failure signatures

| Symptom | First suspects |
| --- | --- |
| Blue full-screen flash | DSI starvation, illegal buffer ownership, missing frame acknowledgement, or excessive PSRAM/cache traffic |
| Horizontal short lines | RGB888 PPA fill/blend path, stale cache lines, wrong stride, or writing an active frame |
| Random horizontal split | Buffer switch before producer completion or incorrect frame stride |
| Correct frame after touching screen | Source changed without the required LVGL/direct refresh |
| Shifted image | DSI timing/mode mismatch, wrong stride, or source crop coordinates |
| Correct first image, corrupt replacements | Old/new buffer lifetime overlap or incomplete invalidation |
| Animation good until artwork update | Competing PSRAM transfer or direct-region base generation mismatch |

Do not hide these faults with a slower global burst setting until ownership and
coherency have been proven correct.

## Source map

## Navigation ownership notes

The Wi-Fi and volume symbols are global chrome on `lv_layer_top`. Home page
snapshots must not contain another copy of those symbols; otherwise a page
swap can expose an old copy or hide the current one. Weather's selected frame
is prepared while the boot overlay is opaque and the page snapshot is built
after the weather state update, so a carousel gesture never has to allocate or
render the first weather frame.

Direct snapshot scrolling is an acceleration path only. If its buffer is not
prepared, touch remains available to native LVGL widgets. Likewise, a direct
handoff may disable LVGL invalidation only while an explicit compositor owner
is active; the LVGL loop restores invalidation after a failed or stale handoff.
This keeps labels, buttons, and native settings scrolling usable without
slowing the normal direct-render path.

Artwork and gallery input remain hardware-JPEG-only. Gallery requests retain
the fullsize Immich derivative and reuse one reserved source-sized RGB565
staging pool. PPA fits that decoded source into the 800x800 panel surface;
the URL is never silently downgraded to a lower-quality preview. The staging
pool is released with the Gallery lifecycle so it cannot permanently starve
DSI or other LVGL producers.

Reusable implementation lives in the ESPHome integration tree:

- `esphome/components/mipi_dsi/mipi_dsi.cpp`
- `esphome/components/mipi_dsi/mipi_dsi.h`
- `esphome/components/lvgl/lvgl_esphome.cpp`
- `esphome/components/lvgl/dma2d_m2m_copy.cpp`
- `esphome/components/lvgl/ppa/`
- `esphome/components/lvgl/lottie_loader.h`
- `esphome/components/lvgl_material/`
- `esphome/components/esp32_jpeg/`

Product configuration lives in:

- `modules/hardware/display.yaml`
- `modules/lvgl/base.yaml`
- `modules/lvgl/material.yaml`
- `modules/player/artwork.yaml`
- `modules/immich/`

## Boot handoff and artwork worker (2026-09-21)

The boot path has two separate ownership boundaries that must remain ordered:

1. boot Lottie and its retained frame are hidden and drained;
2. direct-region producers are paused and DSI is put in the quiet handoff
   state;
3. the first Home snapshot is captured and committed;
4. direct producers are released before the backlight reveal.

Do not start weather, artwork, or another direct producer while the first Home
snapshot is being captured. Doing so can put a boot-Lottie frame or a partial
weather frame into the Home source. The boot sound and assistant error chime
use the same boundary: an assistant error request is suppressed while boot or
snapshot I/O is active.

Player artwork handoff is latest-generation only. The LVGL loop publishes the
new source pointer and generation; the wavy-progress render worker performs
the 800x800 RGB565 backdrop conversion into a reusable free backdrop buffer.
The loop must not walk the whole PSRAM artwork while changing the cover. If a
worker or render mutex does not exist yet during initial widget setup, the
setter uses the synchronous setup fallback without passing a null semaphore to
FreeRTOS. Once the worker exists, stale generations are dropped and only the
newest completed buffer is presented.

The 2026-09-21 fix14 hardware pass showed no assert/reset, no nonzero DSI
underrun counter, and 80-103 waveform renders per two-second interval during
player/media activity. This is runtime evidence for the worker handoff, not a
substitute for visual inspection of every animation state.

## ThorVG synchronization and LVGL watchdog guard (2026-09-22)

`tvg_canvas_sync()` is required after every submitted `tvg_canvas_draw()`,
including `TVG_RESULT_SUCCESS`. It is the ThorVG C API presentation fence; it
must not be skipped as a presumed FPS optimization. Skipping it can leave a
stale weather/boot frame visible and can publish an incompletely rasterized
target to the next direct producer.

The one-second home header tick is deliberately data-only. It updates clock
text and, only when the Wi-Fi bucket actually changes, synchronizes the small
fixed status chrome. Visibility flags, z-order, and full status-layer
invalidation belong to navigation handoffs. Repeating those LVGL operations
from a periodic poll caused `refresh_children_style -> lv_obj_invalidate`
watchdog stalls while the display was otherwise healthy.

