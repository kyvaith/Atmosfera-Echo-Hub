# P1 light brightness vertical slice — implementation plan

Date: 2026-10-24. Status: firmware16 compiled, was uploaded and matched its complete running ELF. Its visible Home health and individually reviewed original application6 glyphs passed. HA dev12 is now active with the explicit v3/revision3 control card. One open/close completed in 19.510 seconds with zero explicit selected-light On/Off dispatches in the paired observer. A separate 13.360-second diagnostic drag produced exactly one current brightness60 command after its owned release and exactly one observed HA light.turn_on with brightness_pct60. The selected Lightener entity remained on/raw202; Zigbee2MQTT recorded NwkRouteDiscoveryFailed (0xd0) on the child command. This proves software dispatch, while resulting HA state and physical actuation remain UNCONFIRMED_EXTERNAL_ZIGBEE_ROUTE. No inverse/restore was sent. Closing after the capture preceded the eight-second state timeout, so that UI path was not exercised. The v15 regional glyph visual FAIL and historical failed11/12/13 records remain unchanged; firmware14 was never uploaded. Physical touch, sustained motion, lifetime/audio and total retained-memory acceptance remain open. This advances the next vertical slice after the [HA dashboard](ha-dashboard-2026-10-24.md); it does not establish an accepted light regulator. The original interface tables below retain their planning context; current contracts are in [entity control](../architecture/entity-control.md), and [live deployment evidence](live-ha-deployment-2026-10-24.md) separates completed and open gates.

The deliverable is one explicitly configured light-control entry that opens application 6, shows the selected light, previews brightness locally, and submits one command when the finger is released. Explicit On and Off are included. Colour temperature/RGB/effects, other entity domains, custom pages, resizing and broad native-control support remain outside this slice. This advances AEH-CTL-003 and the necessary part of AEH-UI-003; it does not complete all P1 or all native-control families.

Planning revision, now implemented in source12: the [whole-product implementation plan](implementation-plan-2026-10-24.md) selected the lean 564×112 rail/value-bubble canvas below instead of the earlier 564×250 union. The large native hero value updates at release/state boundaries, while the small regional candidate follows dragging. The first light owner remains `light_control.py`; generic extraction is a separate W04 step after evidence.

## Existing contracts and the required change

The combined source includes the regional renderer, generation and NAV guards,
TileSurface control routing, Wave quiescence, product application6 and dev4 HA
owner/editor. Product admission is false in source by default and explicitly
true for the v12 validation build. Full configuration passed in both states.
The first v11 build exposed a `StringRef`/`string_view` API boundary error;
v12 changes only that adapter. Failed v11 generated source/compiler metadata
and logs were archived before ordinary regeneration in the same mutable build
directory; the v11 source freeze remains unchanged.

V12 compiled with ESP-IDF5.5.6/GCC14.2. Static RAM is293352 bytes (+11696 vs10),
flash7881850 bytes (+85252). Full preserved ELF:
`b2f957136ff42fa7c2dee810a9df4af11a5a07cdf9e2ba466dc9a1a833c80e1c`.
These are compiler/artifact facts, not target allocation, performance or HA
service acceptance. The live deployment record tracks subsequent gates.

P0 is a sixteen-slot, fixed-pool Home model. Slots 0/1 remain hidden. Its v2 document supports `none`, `default` and fixed `service` actions; `native_controls` is false. A configured brightness preset is not a native slider. `MaterialTileSurface` already captures ID/revision/context generation on press, rejects changed context before click, and separates visual readiness from context readiness. `CameraBridge.async_press_tile` checks saved/sent revision, the connection's negotiated protocol and current card ID before resolving a live HA action. These checks remain intact.

The initial proposal's native LVGL slider is insufficient for production dragging: `animated:false` prevents interpolation, but touch changes still invalidate LVGL. The product uses DIRECT plus full refresh, so those changes can redraw the entire screen. The existing volume renderer illustrates worker/coalescing and ownership, but it is a full-screen overlay session with arc-specific geometry. Do not instantiate another global volume overlay or copy its full-screen ownership model into this page.

## Concrete scope and ownership

The tables below retain the planning baseline: **new** means new relative to P0,
not absent from the adopted source. Current schemas and the entity-control
architecture govern the implemented contract; HA staging is not activation.

| Owner | Planned responsibility and exact location |
| --- | --- |
| HA model | `custom_components/atmosfera_echo_hub/layout.py`: next document version, explicit light-control action, strict migration/export validation and advertised supported control types. Keep existing typed tap presets. |
| HA capabilities | `cards.py`: derive the light descriptor from the existing `entity_actions`/`validate_live_action` path and current `hass.states`; resolve service data server-side. No generic device-provided service dispatch. |
| HA session/action owner | **New** `custom_components/atmosfera_echo_hub/light_control.py`: one bounded current selection per bridge, command admission/deduplication, grant expiry, service error/result reconciliation. `controller.py` owns it, connection epoch and task/listener cleanup. |
| HA registration/editor | `__init__.py`, `const.py`, `services.yaml`: strict report registration. `panel.py`/`www/tile-editor.js`: an explicit Light control choice, only when the connected firmware advertises this exact capability. Update localized labels through the existing owners. |
| Reusable context routing | Fork `esphome/components/lvgl_material/material_tile_surface.{h,cpp}` and `__init__.py`: optional per-tile control intent and a correlated control-open callback. Retain the existing press snapshot/readiness rules and suppress the ordinary tap callback for a control entry. |
| Reusable native session | **New** fork `lvgl_material/material_entity_control.{h,cpp}`: bounded selection, input/command lifecycle and correlation; no HA domain service names or product coordinates. Declarative configuration/codegen in the component's `__init__.py`. |
| Reusable rendering/input | **New** fork `lvgl_material/material_direct_scalar_control.{h,cpp}`: configured widget geometry, single regional canvas, hit testing, latest-value coalescing, pause/drain/rebase, no network policy. |
| Graphics transport | Existing `esphome/components/lvgl/lvgl_esphome.{h,cpp}` owns regional requests and DSI leases. Add only an opt-in expected-base-generation check if needed as described below; existing callers keep their current defaults. |
| Navigation | Existing `lvgl_navigation.cpp` and `lvgl_direct_snapshot_compositor.cpp` continue to own open/close, gesture arbitration, snapshots and full-screen handoff. Do not add a second app animator. |
| Product composition/policy | **New** `modules/lvgl/pages/light_control.yaml`, plus package inclusion, `base.yaml`, `material.yaml`, `navigation.yaml`, product i18n/translation files, and explicit Voice-return policy in `modules/voice_assistant/runtime.yaml`. YAML binds policy and IDs; no session, dispatch, retry or drag state machine in lambdas. |

The fork remains reusable: derive display dimensions/stride/colour format and widget bounds from configuration, and expose the control disabled by default. No Atmosfera names, 800×800 constants, entity IDs or product colours in reusable C++.

## Entry and versioning decision

Use an explicit action, **proposed** `{kind:"control", control:"light"}`, in a v3 layout. This is a deliberate schema extension, rather than changing what an existing `default` light tap means. Deterministic v2→v3 migration preserves every existing action, card ID and slot. Existing layouts do not acquire controls automatically. The editor offers the new choice only for a runtime `light.*` entity with an advertised usable light capability and matching firmware support. A sensor card cannot use it. Hidden slots remain inadmissible.

Keep presentation wire v1 and its complete sixteen-slot projection. Add only an optional per-card `control_kind:"light"` marker on negotiated P1 connections. Old firmware receives the P0 projection with this entry passive and a clear unsupported-device status; it must never fall back to toggle or a fixed service. New firmware routes that marker to the new control-open callback, not both callbacks. The renderer still knows no entity ID or arbitrary action. The HA model owns the selected entity behind slot/card ID/revision.

Advertise a narrow capability such as **proposed** `native_control_types:["light_brightness_v1"]`, with an explicit protocol version. Do not treat the existing `native_controls` boolean as support for every domain. Negotiate through a new response-capable native action before enabling this feature. P0 `home_tiles_get_status`, its context-press v1 contract and physical `applied:null` semantics remain compatible. Exact schema fixtures must be agreed before implementation across HA, codegen and C++.

## Proposed bounded channel and state contract

Use the existing ESPHome API transport and HA service-call permission/context path. The current product API configuration does not establish encrypted transport, so this plan does not claim it. No additional HTTP server, MQTT broker, HA token, arbitrary entity ID, URL, service name or script body comes from the screen. A correlation token is not an authentication credential. A native report must route to the matching loaded bridge, and HA must preserve/check the caller context using the established service path.

The implemented native actions are `light_control_get_status` (response-only capability), `light_control_bind` (HA connection-channel binding), and `light_control_update` (bounded state/result payload). The dev4 HA source defines `atmosfera_echo_hub.report_light_control` for open/command/close; its presence in source/staging does not prove running service acceptance. Payloads are version 1, complete small documents, maximum 2048 UTF-8 bytes, retaining the earlier bounded-detail envelope; reject oversize, wrong types, unknown fields and unsupported versions atomically. Keep IDs within existing 64-character limits, title within 160 UTF-8 bytes, error/status as fixed enums, percentage integer 0..100, sequences 1..2^31−1, and no floats/booleans accepted as integer commands.

The minimal identity tuple is:

`bridge + HA connection channel + open sequence + selection token + slot + stable card ID + layout revision + command sequence`.

- HA generates a fresh random 128-bit channel ID when the actual ESPHome runtime connection epoch changes. It binds the channel to the current runtime/client and clears all older sessions. A node name or an available debug API client alone is insufficient evidence of a current HA channel.
- The device increments an open sequence per requested opening. Its request carries the bound channel, current slot/ID/revision and sequence captured from the validated tile click. HA verifies the currently saved and sent document, visible editable card, explicit control action, current runtime light and exact firmware capability before issuing a new random 128-bit selection token.
- HA's update identifies the pending open sequence and selection. The device ignores an older/replaced response, a changed tile context, an unavailable channel, or a navigation owner that can no longer admit this opening. A successful grant is the only trigger for opening app 6. A grant must not open the app after the user has begun another navigation/gesture.
- The grant contains bounded title/state, known brightness or null, and separate `brightness`, `turn_on`, `turn_off` booleans. State updates carry a monotonic state sequence. Ordinary brightness/state text updates do not replace action identity; a changed card/revision/entity/capability/availability invalidates an active drag and requires a renewed selection.
- One grant lasts 30 seconds on the device's monotonic clock. While that selection is open, HA renews the current validated state at most once per 10 seconds through one owned scheduled callback. Close/disconnect/unload cancels it. No off-screen heartbeat, persistent poll task or unbounded queue. Invalid/missing renewal expires the controls to a disabled state without changing the light.
- The device admits at most one pending command. Command sequence increases within the selection; exhaustion requires reopening. HA stores one in-flight command and the last completed sequence/digest/result. An identical duplicate receives the same pending/result status and is not executed again. Reused sequence with different data is rejected. Older sequences are rejected, even when their full result is no longer retained. A fresh selection prevents a delayed release from an earlier opening of the same card in the same connection/layout.
- A result/update carries the same selection and command sequence. A late result can update its bounded record but cannot reopen a closed app, replace a newer selection or display success for another operation. Close revokes admission immediately; it cannot undo a service already dispatched.

This is a correlation and admission contract, not physical-light proof. Do not reuse only P0 card ID/revision as a numeric-command token.

## Brightness, HA capabilities and command semantics

Use `hass.states` as the eligibility authority, including YAML entities without registry entries. Resolve the selected entity from the current configured card server-side for every command. Require the runtime entity to exist, be `light.*`, not unknown/unavailable, still match the configured card, and expose the required registered service and live descriptor. Recheck after acquiring the per-selection dispatch lock, immediately before the service call; reject after any intervening revision/epoch/session change.

Reuse the existing supported-colour-mode gate for `brightness_pct`; the presence of a `brightness` attribute alone does not prove support. Capability removal during a drag cancels it. An on/off-only light can retain explicit On/Off, with the slider disabled and localized “Brightness unavailable.” Unknown brightness is a real null/“--”; never invent 50%.

| Intent | HA operation |
| --- | --- |
| Released percentage 0 | `light.turn_off` with only HA-resolved entity ID |
| Released integer 1..100 | `light.turn_on`, same entity ID and `brightness_pct` only |
| Explicit Off | `light.turn_off`, independent of the candidate slider value |
| Explicit On | `light.turn_on` without brightness, retaining HA/device restore semantics |

Pointer geometry clamps a finite local ratio to 0..100. The HA boundary strictly rejects malformed/out-of-range values instead of silently clamping hostile input. Convert valid HA brightness 0..255 to a displayed percentage deterministically as `(value*100+127)//255`; a known off state displays 0 while retaining HA's separately reported last-on attribute if needed for later state display. No colour, transition, effect or arbitrary service parameter is accepted in this slice.

Touch-down and motion change only a local candidate. One completed release sends one command; returning to the initial percentage is a no-op. A lost/cancelled press, close, sleep, Voice takeover, unavailable entity, context replacement or known renderer failure before admission emits nothing. A display failure reported after command dispatch cannot undo that dispatch and must not be reported as proof that the light operation failed. Incoming authoritative brightness during a drag is retained in a separate latest-state record and does not pull the thumb away. Release expresses the user's final current intent; a brightness-only external update does not silently retarget the selected entity. Reconcile to the newest authoritative state on cancellation.

After dispatch, use honest fixed labels: local “Preview”, “Sending”, “Waiting for state”, “State matches request”, or a bounded error/timeout. Await the HA service task with a five-second bound; a successful service return means accepted by HA, not a changed lamp. Observe the normal HA state listener for up to eight further seconds. An on/off match and approximately one 8-bit brightness step (one displayed percentage point) may report that HA state matches the request, but never “physical applied.” If the desired state already matched before dispatch, label that distinction; it is not evidence that this command caused a change. Transition/slow-device timeout is “not confirmed,” not proof of failure. No automatic resend after an ambiguous timeout. A retry is a new intentional command with current validation. Disable further command admission while one is pending.

## Rendering without a full redraw for every drag event

Retain the round-panel composition and existing fonts. The proposed regional envelope is 564×112, containing the rail, thumb and candidate percentage/value bubble. Derive its actual bounds from the product widgets and validate circle margins, On/Off hit targets and the bottom close zone in a prototype before implementation. Title/state/errors are bounded and localized. All widgets are created once. Theme/locale/context changes update static native widgets only at a quiescent boundary.

Replace the interactive native slider with a neutral, fixed hit surface whose pressed/value styles do not mutate. The new scalar component owns its pointer capture and exposes a local candidate/release callback. It draws the candidate percentage/value bubble, rail and thumb into one combined bounded regional canvas. This keeps the moving candidate and thumb in the same submitted generation. The separate large native hero shows authoritative/committed state with a clear label; buffer external state during drag and update that hero only at release/cancel/state boundaries. It must not invalidate the full frame on every motion. C++ derives and validates the regional geometry rather than hard-coding product coordinates.

The render worker rasterizes small shapes and cached glyph masks into RGB888 and submits through the existing `LvglComponent::direct_blit_rgb888_async`. It never reads mutable LVGL objects or font-cache state off the owner task; create bounded glyph masks/style snapshots on that task during setup/rebase. A solid black local background and the static caption are composed into the same local canvas, so no raw full-screen background or duplicated app image is needed.

Maintain one latest requested candidate and at most one submitted immutable source. While the scratch canvas is in flight it is never overwritten. The completion callback merely retires the source/wakes the worker; it does not mutate LVGL, call HA or claim scanout success. Recompose the newest value when free, dropping intermediate motion; cap ordinary requests at 30 Hz. Repeated samples at the same integer percentage perform no render. Final release freezes the local intent and requests the latest candidate as a stable visual boundary; the command is emitted once by the owner from the validated release state, not from compositor callbacks. Do not mistake the source-retirement callback for an exact physical-frame acknowledgement or use it to authorize a service.

Use persistent regional carry for this single canvas so unrelated permitted LVGL refreshes do not restore the old number/rail from a native backing tree. The compositor owns that retained copy. At input/session end, stop admission, drain the producer and accepted work, restore the latest native backing values on the LVGL task, retire the region through the existing release API, and perform the established coherent handoff under one explicitly owned pause. Never resume LVGL over mismatched direct bases. A failed drain retains referenced resources and disables the control; it must not free them or allow a stale worker to paint the next app.

Existing requests are internally generation-aware, but the public RGB888 submission has no caller-provided expected generation. For this new control, add a default-disabled expected-base-generation option to its request path if the component cannot prove enqueue/commit identity through the existing barrier. Compare at enqueue and immediately before committing; mismatch retires the source without publishing it. The component separately tags callbacks by its own view generation. Theme/locale, app transition, sleep/Voice, and any full-screen handoff cancel/coalesce outstanding work, drain, recache styles/glyphs, and restart from the new base only after admission. No generic PPA fill/blend enablement change and no CPU full-frame copy workaround.

This removes continuous LVGL invalidations from drag motion. A static native text/status update may still cause a bounded full refresh at state boundaries; that is distinct from one full refresh for every motion event. If the regional path cannot start, show a disabled slider and an explicit local error while keeping valid On/Off available. Do not silently fall back to the expensive live native slider.

## Memory and task budget

The following is a proposed admission budget, not measured allocation evidence:

| Storage | Bound / owner / lifecycle |
| --- | --- |
| Regional RGB888 scratch | 564×112×3 = 189504 bytes; 128-byte-aligned capacity 189568. Scalar component, allocated once and reused; free only after drain at shutdown. |
| Compositor persistent regional copy | At most 189568 bytes for this geometry. Existing compositor allocation/carry path; initialize once before enabling the first drag, account for retained high-water capacity. Existing release invalidates the copy but does not free its allocation. Do not falsely report this as freed on close. |
| Glyph/style cache | Admission cap 64 KiB including candidate digits/percent, unknown and localized caption masks. The native hero uses the existing font owner. Owner-task preparation only; reject unsupported geometry/cache size rather than allocate silently beyond the cap. |
| Render worker | One reusable low-priority worker, maximum 8192-byte stack plus static task metadata, no per-drag task. Try the existing background-affinity policy; never steal audio task priority. |
| Control/session state | Maximum 8192 bytes firmware-side plus widget objects. One selection, one latest state, one candidate, one in-flight command, last-result digest; no history/undo stack on device. HA retains one such bounded session and one timeout/renewal owner per bridge. |

These named dynamic capacities total 461056 bytes before allocator/task metadata and the static widget tree. They fit under a proposed 512 KiB cap for these named resources only; this is not a claim that total app RAM growth is below 512 KiB. The actual glyph size, compiled widget cost, compressed sixth preview, compositor slot reuse/high-water and total/largest free blocks must be recorded before enabling the feature. Exactly one of the four direct-region slots is admitted for this app's canvas. Before its first submission, competing Player/weather/Voice regions must be drained and released, not merely paused, so the existing first-free allocator consistently reuses the first slot across entries. On/Off use static native pressed styling at discrete action boundaries, not additional direct pressed-state slots. If exclusive slot reuse cannot be proved, four retained copies can cost 758272 bytes, plus the 189568-byte scratch and other named resources (1029760 bytes total before metadata): the stated 512 KiB admission fails until slot ownership is fixed or a separately reviewed larger budget is accepted. Do not hide that high-water cost in the display baseline.

No new full-screen RGB888 allocation is permitted. Keep the display pool, two LVGL buffers, three Home slots and one application raw work buffer unchanged. `snapshot_compositor.max_entries` increases 5→6 because registration counts applications; `decoded_slots` stays 1. Inactive preview JPEGs retain existing eviction policy. No app-specific image decoder, raw scroll bitmap, hidden Lottie or periodic full redraw.

## Lifecycle, gestures and recovery

1. Prepare open: cancel Home press, stop tile refresh, release Home weather, quiesce Player/direct regions, suppress global volume activation, and acquire exactly the existing preparation pause. Keep controls disabled. Bind the granted selection while the last transition frame covers native widgets.
2. Opened: set product app ID6 and existing close zone, balance only the owned preparation pause. Start the regional canvas after navigation yields display ownership. Enable input only after its initial state is admitted; no service on opening.
3. Drag: scalar control owns this one pointer until release/cancel. The system bottom close zone remains outside its hit area. A wake touch is consumed by the current wake policy and cannot submit brightness. Reject a second contact and duplicate release for the same captured interaction.
4. Prepare close/Voice interruption/sleep: disable emission first, cancel uncommitted drag, revoke local selection admission, stop worker requests and drain before snapshot capture/handoff. Close never sends the candidate. A previously sent command may finish at HA but cannot reopen the page. Voice restoration adds an explicit app6 case and requires a still-valid renewed grant; otherwise restore a disabled state or Home.
5. Cancelled close: balance the close pause once and restore only current validated interaction. Do not resend, rebuild widgets or revive an old gesture/token. If the selection was revoked, obtain a new grant before enabling controls.
6. Closed: release the control region safely, retain/reuse the documented small buffers, cancel HA renewal/settle observers, reset active-app policy and restore Home weather/global volume/status. Home retains its current page/window. Ordinary display timeout remains enabled; app6 does not inhibit sleep.
7. Disconnect/unload/layout save/entity removal: revoke channel/selection and tasks before replacing listeners. No state/result from an older epoch may enable input, alter a new selection or dispatch. Reconnect requires capability negotiation and a fresh opening; never replay a saved candidate or pending command.

Errors must stay actionable and bounded: unsupported device, unsupported brightness, entity unavailable, selection changed, connection lost, command rejected, service error, result not confirmed, or renderer unavailable. Display the latest known authoritative state separately from any local candidate. Reopening after an error is a fresh validated selection, not an automatic retry.

## Implementation order and acceptance gates

| Gate | Targeted evidence required before moving on |
| --- | --- |
| A — contract/model | Freeze shared fixtures for capabilities/channel/open/state/command/result and v2→v3 migration. Reject invalid sizes/types, hidden/non-light cards, unknown fields, unsupported versions. Existing P0 112 Python/39 JS/41 native host cases remain regression evidence, rerun appropriately after actual edits; their present success does not test this plan. |
| B — HA owner | Unit/adapter tests for 0/1/100, invalid/nonfinite/bool/overflow, unavailable/missing/onoff-only, removed service/capability, unknown YAML-vs-registry eligibility, state update during drag, exact service data/context. Concurrent same sequence executes once; differing duplicate rejects; prior-open/prior-epoch/reordered releases and late callbacks never execute/reopen. Close/unload cancels owned tasks/listeners without cancelling already dispatched physical work as if it could be rolled back. |
| C — native/input | Production C++ host tests with controlled present callbacks for one command/release, zero command from drag/open/state-sync/cancel/close; lost press/second pointer; context-generation replacement; pending buffer immutable until retired; busy coalesces newest value; generation mismatch drops; failed drain keeps resources; app close/reopen never accepts stale completion. Test acceleration absent/disabled as well as enabled. |
| D — configuration/build | Focused schema/codegen checks and complete native ESP-IDF firmware build with app6, max_entries6/decoded_slots1, enabled and default-disabled component configurations. Static circle/text/hit bounds for both locales, 0/100 and unknown; no extra glyph dependency is assumed. Record exact paired source trees and image hashes. |
| E — actual HA | Install the matching local integration using authorized HA access, retain/restorable config options, restart and inspect real logs/capability discovery. Use a permitted dimmable test light and an onoff-only/unsupported fixture where available. Verify one actual HA service call per completed drag and observed HA state separately from light physical behaviour. Test HA disconnect/restart and capability/service removal. Mock server/browser success cannot satisfy this gate. |
| F — flash/runtime/visual | Root flashes the exact built image and independently reads running full ELF identity. On real touch: 0/1/100, fast reversal, slow drag, duplicate/noisy release, On/Off, pending/error/timeout, rapid open-close/cancel, Home2/Home4 return, theme/PL/EN, Voice interruption/return, sleep/wake, Camera/Gallery/Player boundaries. Inspect originals for thumb/number coherence, clipping, pressed contrast, stale pixels, round edges and no leaked regional overlay. |
| G — performance/lifetime | Compare identical baseline/new scenarios: candidate-to-present p95 target ≤100 ms at the requested 30 Hz ceiling; no motion-proportional LVGL full-refresh count; commands exactly one per completed changed drag. Record presents, input age, coalesced renders, loop p95/max, DSI FIFO/strict faults, audio continuity, total/largest free blocks and named allocations. Ten-second sustained drag plus 100 open/close cycles must have bounded retained high-water/no growing leaks; zero new DSI faults and no audio dropout attributed to the change. Baseline-normalized regression thresholds must be agreed from root's current metrics before acceptance, not invented after a run. |

Keep schema/host, complete build, flash identity, HA service/state, screenshots, physical touch/panel timing and audio/performance as separate claims. A still screenshot cannot prove continuous drag performance or physical lamp state.

## Rollout and rollback

Keep the feature disabled until both sides negotiate `light_brightness_v1`. Export the original v2 layout/options and preserve the current local HA package and known-good firmware/source manifests before migrating or flashing. Record a matched P1 integration/firmware pair. Do not overwrite P0 ZIP snapshot2 or its evidence.

Rollback first revokes the channel/selection and drains/releases the renderer, then disables control admission. Restore the preserved v2 options/export if rolling HA code back; v3 must fail explicitly in older code instead of silently dropping a new action. Restore the matching P0 integration package and firmware through root's normal validation procedure. A previously dispatched real-light command is not transactionally reversible: show current HA state and leave any physical correction as an explicit new user action. Never issue an automatic “inverse” brightness command on close, error or rollback.

## Current access and evidence limit

HA dev12 and the explicit v3/revision3 layout are now running. The separate HA12 group-style acceptance is editor-only: 200 Node/250 shim cases, eight original capture files and a scoped zero-call observer do not close any light-control hardware gate. Firmware16 repaired the confirmed glyph-cache stride defect and passed exact running-ELF, Home health, original regional glyphs and one open/close flow. A separate diagnostic drag proved one release-correlated native brightness60 command and one HA turn_on dispatch. The selected Lightener state remained raw202, while the child Zigbee command failed route discovery; resulting state and physical actuation are unconfirmed. No inverse or restoration action was sent. This is diagnostic LVGL input, not physical GT911 proof. The view closed before the state-timeout UI could be observed. Physical touch, lifetime/audio, retained memory, sustained motion and power-action gates remain open. Firmware15 regional glyphs remain a retained visual FAIL, firmware14 was never uploaded, and the earlier failed13 transport attempt remains FAILED. See [live deployment evidence](live-ha-deployment-2026-10-24.md). Root owns deployment/device steps; this plan stores no credential or token.

## Historical P0 documentation audit before live deployment

This audit describes the earlier checkpoint before authorized HA deployment.
Its quoted paths/lines and access limits are historical; the live deployment
record above supplies the later state.

No actionable claim that real HA is already installed/accepted or that all roadmap features are complete was found in the scoped current documents. Independent backend-agent inspection reached the same result:

- `README.md:205–207` explicitly leaves arbitrary pages/resizing/native domain sheets on the roadmap; `:216–221` links matching-version validation limits.
- `docs/development/ha-dashboard-2026-10-24.md:3–5` calls the work local/unreleased/not fully accepted; `:50–51` limits tests to shims/mock; `:59–64` separates packaging from installation and explicitly records the HA access block.
- `docs/architecture/home-assistant-dashboard.md:22–24` says local implemented design is not installed-HA proof; its Evidence section separates host/mock/deployment/build/device acceptance.
- `docs/development/feature-roadmap-2026-10-24.md:246` records P0 progress while explicitly saying real HA is not deployed and other families are unfinished. Historical Baza values remain historical, not acceptance claims for P1.

No documentation edit is requested by this audit. Root is concurrently updating hardware evidence; stale in-progress test timing alone is not reported as a false deployment claim.

## Inspected P0 source anchors from the earlier planning checkpoint

Paths below describe the earlier inspected working tree, not current line-number guarantees or committed P1 changes. Product HEAD at inspection: `65683789d83ceb4510b202ce98979043c8f5e2f6`; fork HEAD: `41e735733078651443b7c0bf56ede4c94f7f5d25`. Both included uncommitted P0 work. `native-light-control.p1-source-manifest.json` records those inspected hashes; later source manifests and the live deployment record supersede its current-state claims.

| Source | Relevant current anchor |
| --- | --- |
| Product `custom_components/atmosfera_echo_hub/layout.py:112–118` | Profile capabilities remain false for native controls/applied ACK. |
| Product `cards.py:394–438`, `:485–503` | Light live action descriptors and per-field execution revalidation. |
| Product `controller.py:654`, `:702`, `:760` | Serialized tile push, epoch/status negotiation, guarded tile dispatch. |
| Product `__init__.py:109–129` | Existing correlated report registration and caller context propagation. |
| Product `modules/common/core.yaml:326–358` | Existing response-capable status/config and tile-config action. No native light channel exists. |
| Product `modules/lvgl/material.yaml:34–70` | Fixed bindings and context-press automation; `:114` existing volume renderer. |
| Product `modules/lvgl/base.yaml:640–715`, `:730–731` | Camera lifecycle reference, application cache max_entries5/decoded_slots1. |
| Product `modules/lvgl/navigation.yaml:432`, `:505–507` | Quiesce helper and global-status app policy. |
| Product `modules/voice_assistant/runtime.yaml:1157–1190` | Explicit previous-application restoration switch. |
| Fork `lvgl_material/material_tile_surface.cpp:322–376`, `:398` | Captured gesture context/readiness; exact refreshed-slot acknowledgement. |
| Fork `lvgl_material/material_direct_marquee.cpp:192–223`, `:229–278`, `:345–445` | In-flight retirement, async source use/coalescing, regional capture/handoff. |
| Fork `lvgl_material/material_direct_volume_overlay.cpp:171`, `:624`, `:875–1024` | Existing bounded resources, exclusive overlay ownership and worker latest-value pattern; do not copy its fallback/full-screen session into this page. |
| Fork `lvgl/lvgl_esphome.h:670–700`, `:730–794` | Actual RGB888 regional APIs, four slots and request shape; no caller expected-generation field today. |
| Fork `lvgl/lvgl_esphome.cpp:4717–4750`, `:5645–5694`, `:5965–6015` | Persistent-copy allocation, RGB888 enqueue guards, release invalidation/retained cache capacity. |
| Fork `lvgl/lvgl_navigation.cpp:564`, `:620`, `:732`; `lvgl/snapshot/__init__.py:255–276` | Owning app state machine and registered-view cache bounds. |

Mandatory architecture/extension/validation/productization documents were read. The plan uses the source-owned graphics and runtime-memory contracts; it does not rely on other projects' marketing or copy their runtime code.

## Native18 run plan and scoped results

Native18 is preserved, compiled and audited. One OTA completed with exit0 at
2026-10-24T22:06:28Z. Its full running ELF, scoped Home1 health and original
screenshot passed on 2026-10-25. Five light-panel transitions completed but
readiness failed; Auto Home Off/Idle30 passed separate scoped checks with owned
cleanup. Native19 is built, audited, flashed and independently identified. Its
first pilot stopped on an unclassified report at the third close; a later failed
instrumented attempt identified a camera-source callback rejected by the helper.
Both failures are preserved. The corrected final pilot passed five owned
open/close pairs and all nine fixed view/scalar/button-readiness observations,
with root-reviewed first/final panel evidence and zero explicit selected-light
On/Off/Toggle calls in the complete paired 180-second observer. Its actual
camera-report count was zero, so live filter interleaving remains untested.
Actual brightness/power/state, physical GT911, sustained drag, FPS/p95, audio and
lifetime acceptance remain open. The
[resumed-day record](validation-2026-10-25.md)
contains actual results; the numbered list below preserves the original run plan. Its source snapshot
contains HA6; separately installed HA7–12 editor packages are not firmware
changes. The earlier unavailability preceded native17 generation. A later ping
or reachable response does not replace the fresh identity required for upload;
an old identity report cannot authorize it.

1. Read the actual MAC, build marker and complete native16 ELF hash on one
   connection. A different identity, failed read or uncertain disconnect stops
   this sequence. Preserve the failed observation separately.
2. Upload the preserved native18 image once, then independently verify its
   complete running ELF. Record upload and identity results separately.
3. Run the bounded Home1 health observation and review original screen captures,
   including the retained weather animation and the smaller weather label.
   Configuration/build success is not a visual result.
4. Select Home4 through the existing navigation controller. Run five
   no-actuator light-panel open/close cycles with the paired HA observer and
   fixed cold diagnostics before/after presentation handoffs. Correlate the
   last current completion's IDs and base generations; a retained tuple alone
   does not prove freshness or readiness. Review originals and matched Home4
   memory samples. Five cycles do not establish latency percentiles or lifetime.
5. Test Settings Auto-Home Off and 30 seconds separately, with a fresh initial
   preference observation, normal application lifecycle and confirmed Settings
   scroll-snapshot ownership. Restore only the value owned by the test after
   independent fresh-state checks. The 40-second bound applies to completion of
   the host's lifecycle observation, not an exact physical presentation time.
6. Resolve power-button readiness before further actuator, sustained-drag,
   audio-concurrency and physical-touch acceptance. An HA command dispatch
   remains separate from the selected provider's state and physical actuation;
   the previous Zigbee route failure is still an external gate.

The prepared helpers and exact evidence are indexed by the current checkpoint
in [the dashboard ledger](ha-dashboard-2026-10-24.md). The original plan now has
separate identity, Home1, diagnostic-cycle and Auto Home evidence. Control
readiness, physical input, sustained motion, audio concurrency and broader
performance acceptance remain open; no result is inferred from prepared code.
