# Notification attention and history

The native49 / HA95 transport baseline is recorded in
[the hardware acceptance](../development/notifications-acceptance-2026-11-02.md).
The continuous list and banded cache baseline use native62 / HA96.
[The baseline device record](../development/notification-cards-2026-11-02.md)
precedes the native66 direct presentation and scanout measurements in the
[current checkpoint](../development/resume-2026-10-31.md).
This is a product notification target, not a bridge for arbitrary HA services,
URLs or vendor credentials.

Home Assistant owns a persistent, newest-first archive of at most100 records
with24-hour retention. Each immutable record has a random stable ID; identical
messages remain separate deliveries. Retention applies on load, append, read
and dismiss. Corrupt, duplicate and future-dated stored records are discarded.
The device caches eight titles/excerpts and one bounded detail body. It does
not persist the archive or retain one full-screen buffer per notification.

The existing ESPHome API carries versioned pages. A fresh random channel is
bound to each HA connection epoch. Requests contain only page/open/dismiss,
offset, sequence and an optional record ID. HA checks the actual caller's
control permission for this device's notify entity, the current channel and
strictly increasing sequence before mutation. Removal is idempotent by ID;
a delayed or repeated gesture cannot remove a replacement row. The display
cannot supply a service name, camera identity, or URL.

The optional `detail_action` widget enables wire v3. Its only current action
is `camera_preview`. HA stores the normal text record and keeps the associated
camera, original event ID, and a three-minute expiry in its bounded runtime
state. Detail sends the action type and remaining seconds only. Older clients
keep their original v1/v2 formats. The firmware sends a fresh, sequenced
`activate` request by record ID only after the user taps the action on Home
and the center restores the DSI/LVGL base. A different open application leaves
the button unavailable and shows how to reach Home. The device retires a held
tap on a detail replacement or channel change.

HA checks the current connection, notify and camera permissions, allow-list,
record validity and expiry before invoking the existing Camera preview.
An accepted preview consumes the action and leaves the text in history.
The action uses the existing main-task notification loop, one fixed label and
the normal Camera lifecycle. The drawer keeps its existing backdrop, row
cache, and display owners. A restart of HA leaves historical text available.

Eight existing row widgets are reused. The opt-in continuous-list profile uses
a clipped viewport and overlapping eight-record windows. HA selects wire v2 only
when the connected device exposes `notification_sync_v2`; legacy devices retain
the v1 paged delivery. V2 accepts arbitrary offsets and adds each row's creation
timestamp. The persistent archive schema and permission checks are unchanged.
The device derives relative age from its optional existing clock provider, keeps
no second archive, and reuses the same eight rows when prefetching in either
direction. A stable visible ID anchors the scroll position across updates.
Inertia stops at the latest presented position when a new contact begins.
Rows retain fixed local coordinates. Motion changes the native list container's
scroll offset once; it does not mutate the style/layout position of eight cards
on every sample. Rebinding an overlapping server window adjusts that local
offset while preserving the global history position and visible record anchor.

The product uses a transparent root over the immutable app background, rounded
accent-derived dark cards, source/age metadata and a detail card. The list opens
downward and closes upward in a bounded 240ms native animation. No additional
raw image, worker or full-screen allocation is introduced. The modal scene keeps
ownership until exit animation and coherent framebuffer restoration complete.
A modern root covering the complete display uses native root scrolling for its
entry/exit travel, leaving the captured backdrop stationary. An explicit virtual
self-size reserves that travel so an asynchronous history/text update cannot
clamp the opening offset. Smaller and legacy roots retain position animation.
A contact starting within the bottom 50px commits upward after 36px. It dismisses
the active banner, returns from detail to the list, or closes the list. Dismissing
a banner leaves its archive entry intact. The gesture is bound to the banner
visible at touch-down so a queued replacement cannot inherit it.
This profile has no close or pagination buttons. Vertical scrolling and horizontal
row dismissal lock to separate axes; an ambiguous diagonal cannot dismiss a row.
After HA confirms a row dismissal, surviving cards that move up start from
their previous screen positions, matched by stable ID. One LVGL animation
moves them into place over up to 180ms when drawer transitions are enabled.
The animation reuses the current row surfaces and immutable backdrop. A new
touch or drawer close settles the rows before accepting the next interaction.

The product also opts into `isolate_native_layers`. After the immutable base
is captured and the DSI session has safely ended, the modal scene hides the
active-screen, bottom-layer and top-layer roots. LVGL otherwise redraws the entire covered
application before drawing the system-layer background and cards. The modal
does not change individual page/widget flags or navigation state. Final close
restores exactly the saved layer visibility after coherent DSI/LVGL handback,
before direct controllers resume. Failed handback retains isolation and retries.
Hiding the active screen alone makes LVGL draw its opaque bottom-layer fallback;
that redundant software fill must be isolated too. Its prior hidden flag is
preserved through failed handback and restored exactly with the other roots.
This option defaults off for existing integrations. The weather presenter
defers its background cache maintenance for the entire direct-overlay lease;
pending weather changes remain pending until release. Product Home cache
maintenance likewise defers while the notification scene owns the display.
The product uses18/24/20px source/title/body typography and20px clearance below
a two-line excerpt. `cached_backdrop_dim` defaults off. When enabled, the center
dims the captured background once. `backdrop_dim_shift` defaults to 1 (50%
black). Atmosfera uses 2 (75% black) for the banner and history. Packed low
bits preserve the exact original frame for close. The product uses 480,000
auxiliary bytes at 800×800 in addition to the 1,920,000 band bytes. Each band
owns its packed low bits, so the scrim only needs 60,000 auxiliary bytes per
allocation at this resolution. The source bands stay immutable while displayed.
No second full RGB
image is allocated. Little-endian targets process eight channels per word pair;
unaligned starts/tails and other targets retain the exact byte operation. CPU writes
are cleaned to RAM before PPA reads. Final close
reconstructs the original bytes before the normal PPA/DSI restore and coherent
two-buffer handback. The auxiliary allocation is bounded and released at that
reconstruction, including partial-copy retry. A failed allocation or cache sync
refuses opening and retires the scene. This avoids reblending a full-screen
translucent native rectangle on every scroll frame.

`row_snapshot_cache` is an additional opt-in native rendering cache (default
off). The default cache uses four reusable ARGB8888 card surfaces for the
eight-row window.
It caches rounded corners, background and text together; the stationary app
backdrop is not baked into a moving card. LVGL and the existing PPA image
renderer compose the cached images. At600x172 the four surfaces contain
1,651,200 raw pixel bytes; independent aligned bands add a small amount of padding
while history is open.
`row_cache_band_count` is a preferred count, defaults to1 and accepts1..8. Each horizontal band owns a
separate aligned ARGB allocation and is captured directly into that band through
a private off-screen LVGL layer. There is no contiguous whole-card scratch buffer.
The capture uses the row's full coordinates with a clipped band, including rows
outside the physical viewport during drawer entry. LVGL's main task owns this
stack layer, waits for draw workers, restores the prior display/layer context and
balances draw-unit lifecycle events before publication. A stalled queue is drained
and its nested tasks retired; a partial or failed capture never becomes visible.
At600x172/radius44, the product's2 bands need at most206,464B per allocation;
four cards total1,651,712B including alignment padding. This keeps the same raw
pixel budget, but works when free PSRAM is fragmented below a412,800B whole card.
If total free memory passes the reserve check but a contiguous allocation fails,
only that unpublished slot is retired and retried with twice as many bands, up to8.
A successful smaller allocation shape is retained for later generations. A total
budget shortage, failed renderer or cache sync does not trigger those retries.
`row_cache_max_bands` reports the largest actual count among ready slots; this can
exceed the configured preference. Thus a2-band preference may need4 bands after
repeated app visits leave only172KiB contiguous, without reducing the1MiB reserve.
The independent aligned slices add only small padding, never another raster buffer.
Only a complete cache generation emits its disjoint native ARGB image tasks.
Changing band count detaches references and restores source widgets before
rebuilding textures. Generic RGB888 fill/blend handlers remain disabled.
A packed RGB888 interior/four-ARGB-corner experiment was rejected on native59
hardware: despite identical pixels it increased render cost versus native58.
Native60's single-allocation/sliced-draw experiment still failed after repeated
application visits, with1,992KiB free but a largest block of360KiB. Separate band
allocations address that fragmentation; drawing more pieces over one large
allocation does not. These rejected variants are not current runtime behavior.
Before each allocation the cache preserves `row_cache_min_free_bytes` of free
PSRAM (product/default1MiB). Allocation, size or cache-sync failure retains
ordinary native rendering for that row. One bounded pressure retry per cache session
may release JPEG-only idle application previews through LVGL's existing reader guards.
It does not release raw Home/application buffers, current/close/work owners, in-flight
compression/prefetch or any preview while an application is active. All registered Home
views remain protected, including a view outside the current raw window. A released
preview advances its generation and can be regenerated normally. This does not lower
the1MiB reserve or start repeated reclamation on scroll ticks.
When five rows intersect the viewport,
the four largest visible intersections receive priority.

Slots match stable record ID, displayed-text hash and appearance, so overlapping HA window
rebinding can reuse their pixels. Style changes invalidate cached generations
and restore original child visibility/background opacity before recapture.
Color-only updates are also checked explicitly because LVGL need not emit a
style-change event for them; row translation preserves cached pixels. The cache
accepts fixed, flat, fully opaque, borderless card roots without ext-draw effects;
other styles retain the native path.
One new surface is prepared per ordinary component tick; initial opening may
prepare four before revealing the drawer. Hidden source labels keep their
geometry and content for the existing gesture delegate. Entering detail or
finishing close detaches image/decoder references, restores source styles and
frees every card buffer. A failed final background handback retains only the
modal bands, never obsolete card textures. The card cache has a separate budget
from the temporary modal backdrop and its exact-restore data.

The legacy profile retains conservative disabled defaults for scrolling,
transition animation and bottom-edge closing, including its existing controls.
The optional `detail_view` binds the detail viewport separately from its text.
List mode hides that viewport, including its scrollbar and native hit region;
without a separate viewport the component hides only the detail label.
A navigation touch delegate reserves the top edge when closed, the bottom
edge while a banner is dismissible, and the complete modal surface when open.
An accepted modal gesture never enters Home paging, app close or a child's
pressed style. A stationary top-edge contact remains an ordinary tap; a
directional pull opens history. Row drags dismiss on horizontal release. The
product uses `dismiss_commit_pixels: 36` for rows and a separate threshold for
opening history.
Taps request detail. Legacy page buttons traverse the bounded archive.
A held row retains its ID, and a channel rebind cancels the contact.
A committed row is hidden while HA processes its ID. The modal compositor
discards any prepared frame that still contains the row. The archive changes
only when HA confirms the new window. An unanswered request restores the cached
row on timeout, and a new request uses a higher sequence.

The physical touchscreen calls its raw update listener before the product's
`on_touch` callback. Header policy must not cancel a delegate's candidate by
taking external input capture or preparing the volume DSI session on touch-down.
The header hold tracks intent only: movement beyond8px cancels the hold; a
stationary250ms hold may commit the existing volume controller, which then
takes exclusive input/display ownership. A tap or canceled hold never releases
capture it did not acquire. `owns_scene()` also excludes new volume preparation
while a banner/center is active or returning its framebuffer ownership.
Native49's synthetic tests bypassed these product callbacks; the physical
gesture failure and repair are recorded separately.

`MaterialModalScene` owns one temporary RGB888 background split into at most
eight aligned bands for the complete banner/center session: width × height ×3
bytes,1,920,000B total on this product, eight240,000B allocations. It adds no
task. Native47 hardware tests found6,038KiB free PSRAM but a largest block of
1,824KiB in Voice, below the1,875KiB contiguous request. That version safely
deferred the banner, but did not deliver it. Native48 therefore uses bands;
the total background budget and release boundary stay the same. Band row
alignment follows resolution/stride and cache alignment; no800-coordinate
assumption exists in the reusable component. It first suspends the direct scene controllers
(Weather, Gallery, Camera, scalar), balances a direct-region pause, acquires an
exclusive DSI session, and PPA-copies the actual presented frame into aligned
PSRAM bands. Banner and center share this background.

With `direct_presentation` enabled on ESP32-P4, the modal keeps the DSI session
for the entire interaction. The main task copies the dimmed backdrop into an
idle lease using batched DMA2D. Each physical buffer tracks its previous overlay
bounds, so subsequent frames only restore the union of the old and new bounds.
LVGL draws the modal widgets in a clipped offscreen layer over that lease.
The main task can prepare a third buffer while one is displayed and another
is queued. It submits the prepared frame after the queued frame becomes active.
Native touch processing and animation timers still run. The default profile
and the recovery path use a system-layer image group with ordinary LVGL drawing.
Only the session's close can seed and release the native LVGL buffers while
the external lease is active. A retained animation publication can update its
canvas during the session without restoring native scanout ownership.

For disjoint cached cards the direct path can use up to five slots. It captures
each card as three opaque RGB888 rectangles and four small ARGB8888 corners.
The opaque rectangles and the uncovered backdrop share one DMA2D submission.
The corner compositor preserves the original antialiasing and LVGL draws the
remaining controls and uncached rows. A failed packed capture can use the
existing banded ARGB representation. Every allocation still observes the
configured free-memory reserve and all textures release on close.

On final close, native invalidation is withheld while the DSI session restores all
bands into one idle DMA lease through PPA, presents once at VSYNC, and seeds
both LVGL buffers. A partially copied lease is released without presentation.
A latched failed session end retries the end without attempting another lease.
Direct scene controllers resume before invalidation is re-enabled. Image source
and decoder cache references are retired before the background is freed. A
failed drain/acquire refuses presentation; a failed release retains ownership
and retries instead of freeing a referenced buffer. Normal full-screen Camera
resume remains the existing JPEG/DSI presenter, not another video path.

The product supplies geometry, colors, text-provider callbacks from the existing
locale packs, close/back glyphs, and admission policy. Boot,
snapshot IO, global direct-volume ownership, transitions and selected entity
control preparation defer admission. Existing Light/Number notification policy
still closes its selected control before delivering a banner. The edge center
does not preempt a selected control. Navigation requests are guarded while the
modal scene owns the display. No voice/audio pipeline is stopped by this visual
pause. Physical audio continuity and subframe artifacts require device evidence;
a compile or host display facade cannot establish them.
