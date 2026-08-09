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
- Arm an application transition in its LVGL click callback, but start its
  compositor worker only after the current `lv_timer_handler()` returns and the
  pending DSI frame is presented. Otherwise the callback's native flush can
  cover every correctly rendered transition frame.
- If an application-close source aliases a DSI framebuffer, refresh its JPEG
  cache before realigning the DSI pool to the final Home frame. Realignment
  overwrites every display buffer and must never run before that source is
  consumed.
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
- In direct-region material renderers, draw transient state such as a loading
  sweep as an independent overlay over the stable progress track. Do not clip
  it against the played/remaining partition: that makes the sweep disappear
  and reappear at segment boundaries. Give the transient segment its own
  antialiased rounded caps and remove it atomically when the confirmed state
  arrives.
- Keep the player wave phase and loading-sweep phase independent. Pause must
  freeze the confirmed wave geometry while a genuinely slow command may still
  advance the loader. Preserve the one-second loader delay so fast actions do
  not flash. Capture command progress from the material renderer itself, not
  from delayed SendSpin title/position state. Treat SendSpin `IDLE` as a paused
  state and retain the exact rendered hold value, including the synthetic 100%
  value used by unbounded streams.
- Submit confirmed playback and loader visibility atomically. During pending
  feedback, retain the real progress internally but draw an inactive full wave
  plus the loader so a full stream ring cannot obscure it. Once a direct-region
  animation stops, pin its final ARGB overlay as a stable carry and reblend it
  into later regional frames. Never carry a stopped widget by copying pixels
  from an arbitrary member of the DSI triple-buffer pool; that resurrects stale
  phases and play/pause glyphs when another region updates. Apply this rule to
  native LVGL target rebases too: reconstruct a stable slot from its clean
  background and cached ARGB overlay instead of copying the current scanout.
- Freeze the playback phase on touch-down, before LVGL emits `CLICKED` on
  release, and discard a phase step accumulated in the same worker cycle as a
  press/release transition. Keep it frozen at transport-command dispatch; a
  delayed `PLAYING` echo during pause/next/previous feedback must never move the
  main wave. Do not submit phase ticks during the one-second loader grace
  period; once the loader is visible, advance its independent phase only.
- Cancel an older transport-feedback release when a new command starts and use
  typed acknowledgements: `PLAYING` for play, `IDLE` for pause, and changed
  metadata for previous/next. Position/duration echoes are not acknowledgements.
- Hand native LVGL content to a direct-region renderer atomically and without
  blocking `lv_timer_handler()`. Hide the native object only for the off-screen
  clean-background render, restore it immediately, and leave it visible until
  the matching direct-region slot is confirmed active on DSI. Only then hide
  the native object in the LVGL tree. Retry `BUSY` or rejected first frames
  asynchronously and keep the native fallback on timeout. Never use a generic
  frame wait as proof that the requested region was presented, and never call
  `lv_refr_now()` while the native object is hidden.
- For full-screen image replacement, keep transport/decode separate from
  presentation. Prepare the image presenter before a decoder mutates its
  reusable source and take DSI ownership in that same operation; a gap between
  decoder preparation and display ownership allows a dynamic region to publish
  stale artwork. Pin the old visible DSI frame, render the final LVGL scene
  once, and animate with the task-owned PPA crossfade path. Do not reintroduce
  two sibling LVGL image widgets or full-screen invalidation on every fade
  frame. Reusing the same decoded source pointer is valid because the old scene
  is owned by DSI, not by the image allocation.
- Let the image presenter be the sole owner of LVGL display invalidation for
  the complete prepare/decode/crossfade/handoff transaction. Do not disable or
  restore invalidation independently in YAML callbacks: an early error, panel
  click, or overlapping transition can otherwise leave a logically visible
  queue, speaker panel, or volume overlay with `invalidation=NO`. Returning DSI
  ownership must re-enable invalidation and invalidate the active screen once.
- A player scene transition must render the bottom, active-screen, top and
  system LVGL layers. Rendering only the active screen drops global overlays
  such as the clock from the final DSI frame. Keep registered direct regions
  enabled and composite their latest pixels over every crossfade frame so the
  wave and marquee do not disappear or freeze while artwork changes. Cache
  those regions as background-independent ARGB overlays, never as RGB
  rectangles already composited with an artwork generation; blend ARGB over
  the current transition target in place.
- Exclude a direct region's native LVGL widget from the presenter's one-shot
  incoming-scene capture. Preserving both copies renders the object twice. Use
  `capture_exclude` for this rather than hiding the direct region itself.
- Remember that the pinned outgoing DSI frame already contains the previously
  presented direct overlay. At transition start, preserve the region's compact
  clean background. For every crossfade frame, reconstruct that clean
  old-to-new background first and apply the newest ARGB overlay exactly once.
  Overlaying a live region directly on the blended outgoing frame temporarily
  doubles and thickens objects such as the player wave.
- Keep private direct-widget backgrounds in their native compact format and
  separate from background-independent ARGB overlays. Never rewrite a buffer
  referenced by an in-flight PPA request. The player wave uses three RGB565
  crops (active, in-flight, next) and blends RGB565+ARGB8888 directly; do not
  reintroduce RGB888 crop conversion, borrowed artwork pointers, or full wave
  rerasterization during an artwork handoff.
- Treat a new artwork backdrop as a mandatory ownership handoff. Do not use the
  short, drop/coalesce render try-lock used by disposable animation frames; a
  dropped backdrop permanently pastes the previous cover below the wave.
- End a direct marquee only after position zero has been presented through its
  direct region. Releasing the region first leaves the last scrolled pixels in
  the DSI framebuffer until an unrelated LVGL refresh. Once position zero is
  confirmed, park the direct region and stop submitting frames; release it only
  when another UI owner needs the region or the title changes.
- Do not start a direct marquee's motion clock in `begin()`. First present and
  confirm the position-zero direct frame, complete the native-label handoff,
  and start motion on the following UI tick. Advancing while the handoff is
  pending exposes an offset first frame as a visible title blink.
- A native-label to direct-marquee handoff must not invalidate the label when
  changing its hidden flag. Keep the currently scanned native pixels visible,
  update only the future LVGL object-tree state, and let the queued direct
  region replace them at the next DSI frame boundary. An ordinary hide
  invalidation can publish one title-less native frame and looks like the text
  disappearing and reappearing before it starts moving.
- Prepare the direct volume overlay on touch-down and reuse that capture when
  the hold threshold expires. Remove the activation widget with a small
  re-rendered patch; never recapture and re-dim the full display in `begin()`.
- Keep direct volume-overlay preparation idempotent. GT911 may reannounce one
  uninterrupted contact after a framebuffer handoff; a repeated touch-down
  must preserve an already prepared or active overlay instead of ending and
  recapturing it.
- Register every full-screen direct producer in the volume renderer's
  `scene_controllers`. Suspend and drain those producers before capturing the
  overlay base, restore the base before resuming them, and never allow Gallery
  motion or Camera presentation to write concurrently with the volume arc.
  While Camera is suspended for an overlay, reject native JPEG as `DROPPED`,
  not `UNSUPPORTED`, so the pause cannot allocate a full RGB fallback frame.
- Hold `begin_frame_buffer_presentation()` through the complete direct-overlay
  gesture and release it only after restoring the original full frame. Merely
  disabling LVGL invalidation does not cancel a refresh already queued before
  the gesture; that stale flush removes the full scrim and leaves dimmed
  rectangles only where later knob updates redraw it.
- Let a suspended direct scene lend an immutable exact RGB888 frame through
  `get_direct_overlay_frame()` when it already captured one. The overlay may
  borrow that pointer only until the scene resumes, must never free it, and
  must not allocate a duplicate full-screen original. Keep transient drawing
  scratch banded rather than display-sized.
- Set whether the clock activation widget was actually painted before calling
  `prepare()`. Camera hides the clock but retains its top-centre touch region;
  patching a hidden clock into the captured video creates a black rectangle.
- While the direct volume overlay is active, the clock must be absent on every
  screen. Hiding the LVGL widget is insufficient when a suspended direct scene
  lends a frame that already contains it. Such a scene must implement the
  direct-overlay background-render hooks so the renderer can reconstruct the
  small clock rectangle from its clean source without another full-screen
  capture or allocation.
- End a direct volume overlay in this strict order: restore its complete base,
  release the overlay presentation session, synchronously resume the visible
  direct scene and let it reacquire its session while invalidation is still
  disabled, then re-enable LVGL invalidation. Do not call `lv_refr_now()` on
  this path: an immediate native refresh races Gallery or Camera ownership and
  can expose horizontal strips or the black native backing page. Use an
  explicit refresh only for the native fallback path.
- Gallery metadata shows the Immich album name and a date-only `YYYY-MM-DD`
  subtitle. Never expose the original asset filename in the product UI.
- Use the reusable `slideshow` image option and
  `SlideshowController` name for gallery presentation. Do not reintroduce
  the old effect-specific controller name; pan-only galleries are valid.
- Gallery controls freeze the exact presented frame through
  `pause_for_overlay()`. Never rebuild a centered paused image: that creates a
  second transform path and can expose horizontal stripes. Release the
  transient full-screen capture when controls hide or the application closes.
- Never free an exact-frame/subpixel scratch surface while the LVGL image
  descriptor still points to it. During close, retain it through the close
  snapshot, then call `SlideshowController::clear()` to detach the source and
  release motion buffers before releasing the decoded artwork allocation.
- Use directional transition policy for volatile full-screen media: Gallery
  and Camera use `transition_snapshot.open: black` so an old source never
  appears during opening, and `transition_snapshot.close: live` so closing
  shrinks the exact currently presented frame. Scalar `black`/`live` remains a
  compatibility form that applies to both directions. The navigation component
  owns one shared display-sized black frame; never allocate one per app.
- For delayed continuous sources, keep the native LVGL loader in control with
  `defer_direct_session_until_frame`. The producer task may atomically signal
  first-frame readiness, but the LVGL task must both acquire and release the
  direct DSI presentation session. Cross-task ownership can assert in
  `xTaskPriorityDisinherit` during application close.
- Give loading spinners an opaque background matching their page, with no
  border or shadow. Their partial invalidations must clear the complete redraw
  rectangle so stale lower scanlines cannot survive an animation frame.
- Gallery Previous/Next must transition from the exact frame captured by
  `pause_for_overlay()`. Hide the HUD, keep the overlay capture paused, and let
  `transition_to()` resume direct ownership only when the requested JPEG is
  ready. Do not call `resume()` in the button path.
- Schedule fade-through-black before pan completion. Prefetch encoded JPEG in
  parallel, but defer hardware decode until the transition boundary so decode
  and normal motion do not compete for DSI/PSRAM bandwidth for the whole slide.
- Start Camera presentation only after pausing active SendSpin playback. Resume
  only when Camera recorded ownership of that pause. For performance diagnosis,
  first prove the device path with a native-size moving MJPEG source; a static
  or unavailable HA entity cannot be fixed by renderer tuning.
- A Home Assistant camera with a native MJPEG handler must bypass still-image
  preflight and delegate directly to that handler. Some MJPEG entities have no
  valid still endpoint; requiring one turns a healthy stream into HTTP 502 and
  wastes CPU on unnecessary decode/re-encode work.
- The Camera source picker pauses presentation. Confirming the already active
  source must explicitly close the picker and resume that same presenter;
  `select_source()` correctly performs no restart for an unchanged healthy
  source and therefore cannot be used as the resume signal.
- For the first player artwork, prepare the presenter while the separate
  placeholder is visible, then reveal the artwork widget and hide the
  placeholder inside the one-shot incoming scene. The pinned DSI frame is the
  outgoing source, so a second placeholder-sized buffer is unnecessary.
- Keep the boot chime inside the final wordmark phase and wait for local audio
  to finish before fading the backlight out. Prepare Home only while the panel
  is black, then reveal it with the hardware LEDC fade.
- Keep display power policy independent from LVGL redraw activity. Only a
  coherent physical touch or an explicit session/user wake refreshes the
  inactivity epoch; background state, artwork, and frame updates must not wake
  the panel. `display_wake` must not restart an LEDC fade when the light target
  is already on.
- Inhibit display timeout for an active backend Voice phase (`waiting`,
  `listening`, `thinking`, or `replying`), an open Immich gallery, or a visible
  Camera preview. The phase is authoritative; never require a matching page or
  `ui_active_app`, because navigation can lag wake-up or overlay handoff. Keep
  refreshing the timeout epoch while protected so a complete timeout starts
  when the activity ends.
- Keep the Voice application visually minimal: one black full-screen scene,
  a small unframed phase label, centered gray user text, centered white
  assistant text, and a purple lower waveform over a gradient anchored to the
  physical bottom edge. Do not add in-app close controls;
  the universal application-close gesture owns conversation termination.
- Make `LvglNavigation` the sole owner of Voice visibility. Wake words and tile
  taps must both use `lvgl.navigation.open: voice_application`; phase and
  transcript callbacks may update content but must never unhide the overlay or
  activate the direct presenter on their own. Activate presentation only after
  `ui_active_app` identifies Voice so the black scene is already presented.
- On local Voice close, set the stop/suppression latch before calling
  `end_session()`. Delayed backend phases or transcripts must not reopen Voice.
  Clear the latch only in the next navigation-owned open. Test close both before
  speech and during an active reply, then verify Home remains visible after the
  delayed callbacks have drained.
- Treat terminal `thanks -> idle` differently from follow-up idle. The terminal
  idle closes `voice_application`; after navigation reports `on_closed`, restore
  the backlight to off only when the wake word originally found it off. A tile
  or diagnostic open must leave an already-lit display on. Keep the restore
  hook in Voice `on_closed`, never in another application's lifecycle.
- Drive the Voice waveform from `va_pipecat.on_audio_level`. The transport
  publishes normalized input and output envelopes on the ESPHome main loop;
  audio callbacks may only update atomics and must never allocate, log, call
  LVGL, or invoke YAML automations directly.
- Do not animate the Voice waveform as an LVGL object tree. Keep one compact
  RGB888 backdrop and two reusable direct-presentation slots, rasterize on a
  low-priority worker, and hand the region to the PPA compositor. Coalesce a
  frame when both slots are busy instead of allocating another buffer or
  blocking the main loop.
- Restore only the rows touched by a slot's previous Voice wave before reusing
  it. A full 660x190 PSRAM backdrop copy on every frame consumes most of the
  33 ms budget. Keep `set_active(true)` idempotent so repeated level or phase
  updates cannot reset cadence or enqueue duplicate frames.
- Quiesce player wave, marquee, artwork, and other direct-region presenters
  before Voice starts. Concurrent direct renderers contend for the same PPA
  queue and can reduce a validated 30 FPS Voice wave to roughly 15-23 FPS.
- Treat Pipecat phase as authoritative for which envelope is displayed: input
  while listening, output while replying, and a slow synthetic breath during
  thinking or silence. Apply attack/release smoothing in the presenter so the
  transport remains UI-agnostic.
- Coalesce raw Pipecat transcript tokens into cumulative phrases before they
  reach ESPHome: currently four words for user partials and six for assistant
  partials, with punctuation and final-turn flushes. A pending final phrase may
  share a message with its phase, so device parsers must process both fields.
  Update existing text in place and run the fade/translate entrance only for a
  new speaker turn.
- Accumulate each Pipecat assistant observer independently and select one
  authoritative source by priority. Never concatenate `bot-output`,
  `bot-transcription`, `bot-tts-text`, and `bot-llm-text` chunks into one text;
  their different boundaries duplicate clauses. On a priority upgrade, retain
  the current longer prefix until the new source catches up.
- Keep Voice history bounded to the previous assistant answer, current user
  turn, and current assistant answer. On follow-up, discard the old user turn,
  promote the preceding answer, and place the new user below it. Render all
  three blocks in the existing transcript direct region and coalesce their
  upward shift with the new-paragraph entrance animation; do not add scrolling
  LVGL labels or another framebuffer.
- Treat the declarative Voice labels as geometry/font/color sources only. The
  material presenter owns fixed status and transcript RGB888 direct regions,
  rasterizes UTF-8 from the configured LVGL fonts into reusable PSRAM buffers,
  and performs fade/translation inside the transcript region. Schedule a due
  wave frame before phrase rasterization so text PSRAM work cannot postpone the
  independent worker. Never restore live native-label updates: their RGB888
  DIRECT invalidation reduced the wave from about 30 FPS to 5-23 FPS and caused
  116-283 ms LVGL stalls. After the one-time page handoff, the validated direct
  path keeps phrase updates at 28.8-30.4 FPS with a 1-8 ms LVGL loop and zero
  native invalidated pixels.
- Before hiding or closing Voice, stop submissions and drain both direct
  presentation slots. Releasing the region while a PPA request is in flight
  risks stale waveform pixels appearing over the next application.

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
