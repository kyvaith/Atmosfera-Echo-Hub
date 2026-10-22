# Navigation and snapshot lifecycle

The navigation layer makes expensive motion independent of the complexity of
the live LVGL object tree. It owns gesture arbitration, Home paging,
application transitions, Settings scrolling, tap cancellation, and snapshot
lifetime.

## Declarative registration

The product declares navigation below `lvgl.navigation` in
`modules/lvgl/base.yaml`. The important collections are:

- `home.widgets`: ordered Home page roots;
- `home.indicators`: matching page indicators;
- `blockers`: overlays that temporarily prevent navigation;
- `applications`: app page/root pairs and lifecycle policy;
- `snapshot_compositor.scroll_regions`: lists that use snapshot scrolling.

A new object is not included because it happens to be visible. It must be
registered in the relevant collection.

## Gesture router

The gesture router observes one pointer stream and decides whether it is:

- a tap;
- a horizontal Home swipe;
- a vertical Settings scroll;
- a bottom-edge application close;
- a blocked interaction owned by an overlay.

Navigation-owned surfaces withhold the LVGL press until the pointer stream is
classified. This applies to Home and every registered snapshot scroll region.
A real tap is replayed as one short press/release pair, while a drag never
enters `LV_STATE_PRESSED`. This avoids accidental activation, delayed hover
after inertia, and a pressed-style redraw on the first movement sample. Other
surfaces keep the normal LVGL input path; for example, the top-layer clock can
still own its volume long-press.

Gesture classification, axis selection, release velocity, tap replay, and
in-flight takeover live in the shared navigation core. Motion backends remain
specialized: Home is a horizontal page window with commit/edge-settle policy,
while a scroll region is continuous vertical content with momentum and bounce.
Registering another list under `snapshot_compositor.scroll_regions` reuses the
same arbitration without copying Settings code.

Current product thresholds are:

| Gesture | Threshold |
| --- | --- |
| Home swipe start | First directional pixel |
| Home axis bias | 0 px |
| Home page commit | 25% of display width |
| App close edge | Bottom 50 px |
| App close commit | 36 px |
| Settings scroll start | First directional pixel |
| Settings axis bias | 1 px |

Thresholds are policy and may be tuned in YAML. The state machine and click
cancellation stay in the component.

## Home snapshot window

The Home screen currently contains four pages. Keeping all four raw at RGB888
would consume 7.68 MB. The runtime instead owns three fixed raw slots:

```text
3 * 800 * 800 * 3 = 5,760,000 bytes
```

The pages outside the window keep compressed JPEG backing.

| Current page | Raw window |
| --- | --- |
| Page 1 | Pages 1, 2, 3 |
| Page 2 | Pages 1, 2, 3 |
| Page 3 | Pages 2, 3, 4 |
| Page 4 | Pages 2, 3, 4 |

```mermaid
flowchart LR
    P1["Page 1<br/>raw or JPEG"]
    P2["Page 2<br/>raw"]
    P3["Page 3<br/>raw"]
    P4["Page 4<br/>raw or JPEG"]
    S0["Raw slot 0"]
    S1["Raw slot 1"]
    S2["Raw slot 2"]

    P1 -. decode/recycle .-> S0
    P2 --> S1
    P3 --> S2
    P4 -. decode/recycle .-> S0
```

When the window moves:

1. A dirty page is JPEG-encoded before its slot is recycled.
2. A page already in the new window keeps its current raw slot.
3. The incoming page is decoded from JPEG into the released slot.
4. If no JPEG exists yet, it is created through an existing slot or the shared
   application work buffer.
5. The preallocated boot-time JPEG encoder output can be released after the
   initial cache is complete.

This is a bounded cache, not a growing panorama. Adding more Home pages does
not allocate another raw frame per page, but it increases compressed storage
and page preparation work.

The complete three-slot window is mandatory before normal Home paging resumes.
Gallery and Settings may temporarily trim the window while retaining their
current Home close background. Settings attempts its contiguous scroll loan
only after a counted regional drain and successful trim; refusal keeps the
bounded segmented fallback available. Its close releases the scroll surface
and shared loan before navigation refills three slots. Product window metadata
is refreshed after that close, or through the pending accent batch.
If refilling three slots fails after that handoff, the failed allocation attempt
first rolls back. The cache then releases eligible idle app JPEG previews and
retries once. Home JPEG/raw data, the close background and all worker-owned
inputs remain protected. Optional previews can be regenerated through the
existing fresh DSI capture path when an app next opens. A failed second attempt
remains a failure; extra free heap caused by missing Home slots is not recovery.

## Home swipe lifecycle

```mermaid
sequenceDiagram
    participant Touch
    participant Nav as Gesture router
    participant Cache as Three-slot Home cache
    participant Comp as Direct snapshot compositor
    participant LVGL

    Touch->>Nav: pointer down; defer Home press
    Nav->>Nav: first directional pixel selects horizontal drag
    Nav->>LVGL: discard deferred press
    Nav->>Cache: request current and neighbor slots
    Nav->>Comp: begin direct movement
    loop pointer motion
        Touch->>Comp: absolute drag offset
        Comp->>Comp: PPA/DMA2D compose frame
    end
    Touch->>Nav: release
    Nav->>Comp: settle to committed page or bounce back
    opt pointer down while settle is active
        Nav->>Comp: pause worker on displayed frame
        Touch->>Comp: continue from the captured offset
        Comp->>Cache: rebase page pair at exact page boundary
    end
    Comp->>LVGL: apply final logical page
    Nav->>Cache: prepare the new three-page window
    Nav->>Comp: release manual ownership
```

The compositor starts on the first directional coordinate change. A pointer
down during settle pauses the worker at the last frame actually presented and
keeps manual framebuffer ownership. Dragging back reverses from that exact
offset. Continuing past the next page rebases the existing raw pair to the next
three-slot window at the page boundary; it does not expose LVGL or restart the
gesture from zero.

Settle duration scales with remaining distance and release velocity. Edge
return uses a separate smooth in/out curve and a 240-400 ms distance-dependent
duration, so the first and last page return more softly than a committed page
transition.

At the first and last page, the same compositor renders edge resistance and
bounce using the current snapshot rather than a nonexistent neighbor.

Stable activation of a registered full-screen Home widget restores its
parent-relative centered origin before revealing it. Navigation does not keep
a separate original x/y position. The same restoration applies when direct
snapshot preparation and its widget fallback both fail: merely clearing the
hidden flag can otherwise reveal a page still positioned one screen offscreen.
This uses the compositor's existing centered settle geometry and adds no
framebuffer or forced refresh.

## Clock and page indicator

The clock and page indicator must look stable while page content moves. They
are drawn as a fixed overlay rather than being visually duplicated with every
page.

The direct snapshot path currently renders these elements into the composed
RGB888 output. The clock uses a persistent 64x64 A8 glyph buffer. Current
coordinates are product-specific and remain migration debt; a reusable
component must derive their geometry from configured widgets.

When an indicator or clock appears twice, shifts, or briefly shows the old
state, the usual cause is that both the snapshot and live LVGL layers own the
same pixels during handoff.

## Application lifecycle

Registered applications use the same controller. The reusable mechanism owns
transition timing and display handoff; YAML callbacks own application policy.

The application compositor worker holds its snapshot sources continuously
from queued work through the last render. It publishes `running` before
consuming `pending`; cancellation waits until both are clear before releasing
the source buffers or resetting transition state. There must be no apparent
idle gap while a queued job moves onto the other core.
The direct-region pause barrier also completes after every frame source
callback in its batch, including frames dropped during the pause. A pause
waiter may release producer resources as soon as the barrier returns.
When a handoff seeds the idle framebuffer pool with DMA2D, transfer completion
and destination cache invalidation establish the copied base. The production
path does not re-read both full frames on the CPU to compare them: that would
add 7.68 MB of PSRAM reads when seeding two 800x800 RGB888 buffers.
A close or Home request received during application opening is coalesced into
one deferred close. It runs after opening has completed its `on_opened`
callbacks, so opening and closing resource leases stay paired. Repeated close
requests during the committed closing transition are ignored. Closing-frame
capture must never compete with the still-running opening compositor.

### Return the drained transition source before native callbacks

The application animation worker must finish before its external DSI source
lease is returned. On completion, `complete_direct_application_()` releases
that source before `prepare_application_transition()` or lifecycle callbacks
can refresh native LVGL or admit another full-screen owner. The final
presented frame and regional pause remain held while the destination is
prepared. Only then are the open hold/work buffer released and the transition
completed/reset. Releasing this drained source is not permission to write a
queued or scanned framebuffer; the display ownership API still controls that.

Camera opening can call native refresh and then acquire its own direct
session. Keeping the old transition source pinned across those callbacks
violated that handoff contract. R23 changes this release order in the reusable
compositor, with no new buffer, task, timeout or product-specific branch.
The R23 main stress and Camera/Volume addon passed their bounded
application/direct-session state scenarios. These passes do not eliminate the
separately observed natural DMA fault or replace remaining warm/cold gates.
Cancellation and prepared-close paths retain their existing worker-drain/release
discipline.

### Boot preparation

At the splash-to-Home boundary, cache preparation is admitted only after
the regional barrier succeeds. Product boot's declarative wait balances each
failed pause immediately and retains one successful lease through the final
coherent handoff. It has no timeout that could continue into refresh with a
failed drain. The consuming handoff releases that lease on failure too; never
release it again afterward. This gate changes product sequencing, not snapshot
buffers or compositor ownership. See [boot drain admission](runtime-memory.md#boot-drain-admission)
for framework evaluation, blocking-time and persistent-failure limits.

`lvgl.navigation.prepare_applications` renders each registered application and
stores compressed backing. Application previews do not remain as independent
raw 800x800 surfaces.

Applications can select their transition source independently for opening and
closing:

```yaml
applications:
  - id: immich_application
    page: immich_page
    widget: immich_root
    transition_snapshot:
      open: black
      close: live
```

`live` remains the default in both directions. The scalar forms
`transition_snapshot: live` and `transition_snapshot: black` remain compatible
and apply the same value to both directions. A black opening skips boot-time
capture. A black closing skips the close-time capture and refresh. The
compositor allocates one display-sized black draw buffer in the active LVGL
color format and shares it between every application that needs it. It does
not allocate one black frame per app.

Gallery and Camera use a black opening and a live closing. Opening from black
prevents a stale photo or video frame from appearing before the source has
restarted and shown its loader. Closing captures the current, fully presented
media frame, so the application shrinks back into Home instead of collapsing
as a black surface. Their transition geometry remains identical to normal
applications.

### Open

```mermaid
sequenceDiagram
    participant Home
    participant Nav
    participant JPEG
    participant Work as Shared app work buffer
    participant DSI
    participant App as Live LVGL app

    Home->>Nav: tile click
    Nav->>Nav: cancel Home gestures and pause direct regions
    Nav->>JPEG: decode registered app preview
    JPEG->>Work: write RGB888 preview
    Nav->>DSI: animate preview from configured start geometry
    Nav->>App: reveal live page after final transition frame
    Nav->>Nav: resume app-owned workers
```

The raw preview is obtained on demand through one reusable full-screen work
buffer. The Home frame remains visible behind the opening transition.

Tile clicks are dispatched from inside `lv_timer_handler()`. The transition
worker must therefore be armed by the click handler but started only from the
next `LvglComponent::loop()` iteration, after that handler and its pending DSI
handoff have completed. Starting the worker directly in the click callback can
produce valid transition frames that are immediately covered by the native
LVGL flush which dispatched the click.

### Close

```mermaid
sequenceDiagram
    participant Touch
    participant Nav
    participant App as Live LVGL app
    participant Work as Shared app work buffer
    participant DSI
    participant JPEG
    participant Home

    Touch->>Nav: bottom-edge upward gesture
    Nav->>App: pause app workers and capture current frame
    App->>Work: fresh RGB888 snapshot
    Nav->>DSI: animate toward x=50%, y=75%
    DSI->>Home: reveal current Home frame underneath
    Nav->>JPEG: refresh compressed app preview
    Nav->>Work: release/reuse raw work buffer
    Nav->>Home: restore Home gesture ownership
```

The closing animation uses a fresh raw image so it matches the app's current
state. Compression occurs after the visible close transition; the next open
uses that refreshed JPEG.

For a black close policy, the close path deliberately does not capture or
compress the live app. It binds the shared immutable black frame and leaves the
media owner free to stop its worker and release decoded content after the
navigation handoff.

For a live close policy on a direct full-screen producer, navigation first
pauses and drains that producer, then captures the exact DSI frame currently
presented by the panel. The close animation owns the resulting raw frame. Only
after capture may Camera or Gallery release its decoder, source, and motion
buffers. This is intentionally asymmetric with their black opening policy.

When the close source aliases a DSI framebuffer, encode the application preview
before `realign_direct_buffer_after_manual_present()` synchronizes the DSI pool.
Realignment copies the final Home frame to every display buffer; doing it first
would replace the application source and cache the same Home image for every
application.

The current direct transition applies a circular mask and assumes a square
display. The schema is reusable, but that implementation detail must be made
configurable before upstreaming it as display-agnostic behavior.

## Product lifecycle callbacks

Applications need different policy:

- Player pauses marquee and direct wave rendering during ownership handoff.
- Voice Assistant ends or preserves the conversation according to the close
  action, stops output when required, and disables AFE after the session.
- Settings allocates and releases its scroll snapshot.
- Immich freezes gallery presentation, hands off the current DSI frame, and
  releases decoded photos only when no worker references them.
- Camera drains its direct JPEG presentation session, hands the current frame
  to the close transition, then releases stream-owned fallback storage.

These callbacks are intentionally explicit. The goal is to move stable policy
into application controllers, not to hide unrelated cleanup inside the generic
navigation component.

An `on_opened` callback may return while a delayed automation is still pending.
Navigation's deferred close preserves callback order, but does not wait for
those product delays. Player and Gallery therefore run delayed post-open work
in restartable scripts cancelled by `on_prepare_close`; they recheck the actual
active application before enabling renderers or loaders. Camera and Voice
cancel their existing startup scripts at the same boundary and recheck
application identity before starting a stream or voice session. Restart mode
replaces an older pending run when the same application reopens, without a
second lifecycle state machine or generation counter. Settings currently has
no delayed startup in its synchronous preparation chain.

Voice has one additional ownership invariant: wake words and tile taps must
both enter through `lvgl.navigation.open: voice_application`. Backend phases
describe the contents of the open application; they are not navigation events
and must never show the overlay directly. The presenter becomes active only
after `ui_active_app` identifies Voice, which keeps the direct waveform behind
the black application surface during handoff. Closing first raises the local
stop latch and then terminates the backend session, preventing delayed phase
callbacks from bringing Voice back after the close transition.

Regression tests for this contract must cover closing immediately after open,
before any speech, and keeping Home visible for several seconds after closing
during an active listening or replying session.

## Settings snapshot scrolling

Settings is a special scroll region. Redrawing the complete LVGL list on every
touch sample was slow, so the controller keeps a raw bitmap while Settings is
open.

```mermaid
flowchart TD
    OPEN["Open Settings"] --> BUILD["Render list into bounded raw content buffer"]
    BUILD --> DRAG["Move bitmap directly during drag"]
    DRAG --> RELEASE["Apply momentum and bounce"]
    RELEASE --> INERTIA["Render inertia on snapshot worker"]
    INERTIA -->|finishes| LOGICAL["Apply final logical LVGL scroll position"]
    INERTIA -->|new pointer down| TAKEOVER["Pause at last presented scroll position"]
    TAKEOVER --> DRAG
    LOGICAL --> REFRESH["Refresh raw bitmap in place"]
    REFRESH --> DRAG
    CHANGE["Setting changed"] --> DELAY["Wait for pressed state to clear"]
    DELAY --> REFRESH
    CLOSE["Close Settings"] --> FREE["Release list snapshot buffers"]
```

Current policy:

- preload on app entry;
- maximum snapshot memory 8 MB;
- 15% overscroll;
- 560 ms momentum;
- 320 ms bounce;
- 900 ms maximum inertia;
- first directional pixel captures the drag; pointer-down without movement is
  replayed as a normal LVGL tap;
- pressed/hover state is never delivered to list children once the scroll owns
  the pointer stream;
- pointer-down during inertia pauses the worker at its last presented Y
  coordinate and lets the new drag continue from that exact frame;
- refresh in place after a setting change;
- release on app close.

The total raw content must fit the configured cap; splitting never bypasses
that limit. The 2026-10-22 integration retains an external loan or one contiguous
surface when available. On a fragmented heap it partitions the same RGB565
pixels into row-aligned pieces with a 256 KiB target. When that fallback is
selected, the 800x1436 list uses nine pieces and 2,297,600 pixel bytes. A viewport
can cross several pieces; PPA composes each intersection directly into an idle
display framebuffer.

Capture publishes only a complete partition. Refresh drains the worker before
writing the existing pieces; a partial refresh is discarded rather than shown.
A worker-drain timeout preserves its source buffers. Closing Settings releases
owned pieces and returns borrowed storage only after the worker has stopped.

The refreshed snapshot is delayed until pressed/hover state is gone. Capturing
earlier would bake a temporary state layer into the scroll bitmap.

The live Settings tree is deliberately hidden while its snapshot owns the
display. Gesture hit-testing therefore uses the registered root geometry even
when that source tree is hidden; requiring `lv_obj_is_visible()` would make an
in-flight snapshot impossible to interrupt.

## Generic store versus production cache

The public snapshot schema currently configures a generic
`LvglSnapshotStore` with bounded entries and decoded slots. The direct
production compositor also uses specialized cache functions in
`lvgl_esphome.cpp`:

- three raw Home slots plus JPEG backing;
- compressed application previews plus one shared work buffer;
- Settings raw content buffers for the application lifetime.

Therefore `compression: none` in the generic store must not be read as "the
product never uses JPEG snapshots." It describes the generic store policy,
while the specialized direct cache still uses hardware JPEG for off-window
Home pages and applications. Consolidating these implementations is an
explicit productization task.

## Snapshot invalidation

Mark a snapshot dirty when its visible content changes:

- a Home entity changes;
- a slider or switch changes;
- time or an indicator owned by the snapshot changes;
- application state changes before its next open;
- the Settings list changes.

Do not immediately rebuild every cache in the callback that changed the
widget. Coalesce updates, wait for transient pressed state to clear, then
refresh the smallest affected owner. Rebuilding while DSI, artwork decode, or
another snapshot operation is active increases PSRAM contention.

### Accent refresh completion

`LvglNavigation::last_application_snapshot_preparation_succeeded()` reports
only the most recent synchronous `prepare_application_snapshots()` call. The
value is reset to false before each call, stays false without an available
compositor or required snapshot/image support, and otherwise receives the
compositor's aggregate result. It is not a live cache-validity query or a
record of every later widget change. Read it immediately after the call whose
outcome is needed.

The product's accent batch is complete only when invalidating all four Home
pages succeeds, the current three-slot Home window is prepared, and application
preview preparation succeeds. `ui_accent_home_refresh_pending` stays true if
any part fails. A separate invalidation-pending flag avoids invalidating
already updated pages on every preparation retry; a new accent selection
marks both pending again.

Each admitted attempt performs its direct-region pause, cache work and
balanced release synchronously in one lambda. A failed pause barrier also
releases its acquired pause depth. The snapshot IO flag and pause are cleared
before any script delay or restart boundary; no yielding action may retain
that scope. The existing synchronous tile helper may first restore an
interrupted raw slot before preparation is retried.

An admitted batch tries at most three times and delays 400 ms while still
pending. Lifecycle admission may separately defer by 240 ms while an
application, touch, volume interaction, snapshot or another IO owner is busy;
the three-attempt limit is not an overall wall-clock deadline. Exhausting a
batch leaves pending true. Settings close and `on_home_presented` provide
later retry boundaries; the Home hook starts a batch only if none is running.
The `snapshot.refresh: accent batch` record exposes attempt, invalidation,
Home, application and pending results. A visually updated current page alone
must not be treated as a successful all-cache refresh.

### Background backing refresh ownership

The synchronous `snapshot_refresh_tile_backing` helper owns one nested regional
pause lease while maintaining a resident or borrowed Home slot. It resolves the
LVGL component from the page display and drains regional presentation before any
slot encoding or snapshot drawing. A 120 ms barrier timeout refuses the refresh
without changing a slot and releases only that attempt's lease. The lease spans
JPEG work and borrowed-slot restoration, including every failure return. Existing
pauses owned by another caller remain held. This does not acquire a DSI frame or
allocate another raw page; the existing slot ownership and busy flags still apply.

### Bounded clock partial refresh owner

The product groups the eight layered clock labels under
`home_clock_refresh_region` below the fixed header (x0/y71/412×548). Relative
child positions preserve their previous absolute glyph geometry and draw order.
The existing multi-region refresh receives the one container and count 1,
retaining its hidden-source, pending, 40 ms admission wait and dirty behavior.
The cached region must contain the changing clock pixels and exclude fixed
header siblings; LVGL label bounds can extend above the visible glyph ink.
This uses existing slot storage and ownership, without an extra raw copy.

The expected diagnostic is `refreshed merged scanout` with `regions=1` and
`area=0,71 412x548`. Fast partial refreshes log only with existing swipe logging
enabled. A diagnostic test must enable/restore that switch before waiting for
the natural policy event; absence of a disabled log is not absence of refresh.
R25's source geometry/codegen, actual native build and twelve recorded header
transition pixel checks passed. Root viewed two selected before/return frames
with one fixed header and preserved clock overlap. Physical cold-power startup
and health evidence is recorded separately in validation.md.

## Bounded JPEG preparation under preview pressure

A synchronous Home window preparation carries one local recovery budget through
its slot encode/restore helpers. Only a real JPEG `ESP_ERR_NO_MEM` can consume
that budget. Eligible idle application JPEG previews may then be released, and
the same source is encoded once more only if reclamation actually freed bytes.
Home backing, active close sources and current worker readers remain protected.
Any active navigation application refuses this preview reclamation entirely.

The context is local to the public synchronous preparation call; background
refreshes and compression/prefetch workers receive no reclamation authority.
Failure preserves the previous encoded entry and generation. A successful
replacement advances its generation once. This JPEG recovery budget is separate
from the existing single retry for reserving the complete three-slot raw window.

## Extension boundary

The following are automatic after registration:

- gesture classification and tap cancellation;
- Home commit/bounce behavior;
- application transition timing;
- display ownership handoff;
- Settings-style scroll mechanics.

The following still require explicit product configuration:

- page and indicator IDs;
- app page/root IDs;
- app lifecycle policy;
- snapshot invalidation triggers;
- direct worker pause/resume hooks;
- overlay blockers;
- whether an app close terminates an external session.

See [Extending the UI](../development/extending-ui.md) for concrete steps.

## Source map

Reusable implementation:

- `esphome/components/lvgl/lvgl_navigation.*`
- `esphome/components/lvgl/lvgl_direct_snapshot_compositor.*`
- `esphome/components/lvgl/lvgl_snapshot_store.*`
- `esphome/components/lvgl/snapshot/`
- `esphome/components/lvgl/lvgl_esphome.cpp`

Product configuration:

- `modules/lvgl/base.yaml`
- `modules/lvgl/navigation.yaml`
- `modules/lvgl/pages/`


R24's enabled SDK shutdown option changes no navigation/session ownership.
R23's main and addon owner checks passed within their recorded intervals, but
the later warmed shutdown panic rejected the complete candidate. Keep that
restart acceptance failure separate from navigation source-order validation.
