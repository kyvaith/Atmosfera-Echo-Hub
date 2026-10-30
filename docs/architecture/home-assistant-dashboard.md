# Home Assistant dashboard configuration

The Atmosfera Core integration owns configuration, live entity discovery,
capability checks and Home Assistant service dispatch. Its authenticated admin
panel is a client of the HA WebSocket API. ESPHome owns the fixed widget pool,
input and presentation; product YAML supplies its geometry and page membership.

## Management decision

Use the existing HA Core custom integration and its administrator-only sidebar
panel. It can reuse HA authentication, runtime entity states, area registries,
translations and service-call permission context. Versioned config-entry options
remain the durable authority, and the existing ESPHome API connection delivers
the bounded projection. This avoids a second device configuration server and
keeps the editor independent of firmware compilation.

A separate build/flash add-on may become useful for future multi-profile build
queues, but is not needed to arrange the current fixed widget pool. A browser
runtime/WASM preview is a separate roadmap item. The current preview reproduces
the trusted product geometry and state formatting; it is not the ESP32 renderer.

The current dev19 package is installed in the user's HA. The25 installed public
sources match its package; activation preserves entry/data/options and uses the
existing ESPHome connection. Its source/storage/API/browser/native checkpoints
are recorded in [current validation](../development/validation-2026-10-26.md).
Dev19 adds state-aware default Timer actions to the existing tile/resolver:
idle starts, active pauses, paused resumes through start without a duration.
This first control slice adds no periodic countdown push or native protocol;
its isolated device campaign passes native Start/Pause/Resume and actual HA
remaining/deadline feedback, with exact cleanup at16. Performance scope and
remaining countdown/detail work stay separate in the validation record.
The earlier dev12/version3 revision3 deployment remains historical evidence in
[the initial deployment record](../development/live-ha-deployment-2026-10-24.md).
Feature-specific service dispatch, physical input and performance acceptance
remain separate from installation.

## Configuration and ownership

`custom_components/atmosfera_echo_hub/layout.py` is the bounded, runtime-independent
model and trusted product-profile definition. `cards.py` projects HA states and
narrows the action catalogue using live entity capabilities and registered
services. `panel.py` validates complete saves/imports and commits one config-entry
options update with an expected revision. Stable card IDs survive slot moves.

The entity library combines query, domain and area filters before applying its
result limit. Request-local HA entity/device/area registry lookups supply optional
area metadata; a valid explicit entity area overrides its device area. Runtime
states remain the eligibility source, including YAML entities without registry
entries. Facets and truncation are explicit; filtering does not add device-side
subscriptions or move configuration authority into the browser.

The current `echo-hub-m3-v1` profile has sixteen bindings. Slots 0 and 1 remain
hidden compatibility definitions; slots 2..15 use existing Security and Controls
widgets. It does not admit new pages, resizing or a dynamic LVGL tree. The
versioned document is bounded to 32 KiB. The source model defines exact schema,
limits and WebSocket command fields; this document does not duplicate them.

The editor can copy or move one card into an empty compatible place. Its
clipboard is one in-memory deep copy scoped to user, entry and complete profile.
Copy creates a fresh identity per paste. Cut leaves the source in place until
Paste validates its original slot, unique ID and complete unchanged snapshot,
then calls the existing move kernel once. The move retains identity and consumes
the cut intent; one undo reverses the whole move. Occupied, hidden, reserved or
incompatible targets and oversized documents fail without changing either card. An edit
to the source requires cutting it again; unrelated edits remain intact.
Escape, editor detachment, a changed context or explicit HA disconnection clears
the clipboard. Device offline status still permits layout editing. Clipboard
intent is not persisted; an accepted move uses the ordinary draft/history path.
Neither operation executes actions or saves implicitly.

Explicit multi-selection keeps at most fourteen stable card IDs in component
memory, scoped to user, entry and complete profile. Hidden cards remain
selectable; empty and reserved places do not. The existing two editable pages
share the selection. Show/Hide validates the full candidate byte bound and
changes only visibility through one existing draft transaction. Repeated
visibility values create no history. Delete reviews titles/place numbers, then
revalidates the selected complete card snapshots, scope, slots, versions and
saved/server revisions before one filter transaction; unrelated draft edits
are retained. One Undo/Redo restores the entire group and ends selection mode.
Context changes, explicit HA disconnect or accepted document replacement clear
the ephemeral selection. It adds no storage field, subscription, WS request,
device buffer or task. Save remains explicit.

Group Copy shares that single discriminated clipboard with single-card Copy
and Cut; it is not an additional cache. It deep-copies up to fourteen cards in
profile page/slot order and ends selection. Later source edits do not change
the copied values. Paste opens an explicit, initially unassigned destination
selector for every card. Only distinct empty compatible places are eligible;
occupied hidden places still block a copy. The review pins the complete
clipboard, context, document version and saved/server revisions. It validates
the complete current UTF-8 candidate before one existing draft transaction.
Fresh IDs are generated only on confirmation, checked against current cards,
copied source IDs and each other; any failure rejects the complete group.
One Undo removes all copies while retaining unrelated later source edits. Copy
intent remains available for another paste, but mappings belong only to that
review. Native SELECTs participate in modal focus wrapping; Cancel preserves
intent and restores Paste focus. This adds no service, storage, polling,
firmware buffer or worker, and never saves automatically.

Group Cut captures the same bounded group plus its source epoch, layout version
and saved/server revision. Sources stay in place until confirmation. Before an
occupied source slot can become a destination, every captured source must still
have its exact complete snapshot, unique ID and unique slot in the current
draft. Destinations may then be empty or belong to that validated group; hidden
unselected cards remain occupied. A precomputed ID-to-destination map changes
only slots in one traversal of the current array, preserving identities, typed
data, order and unrelated edits. Full-capacity swaps and cycles need no temporary
card or UUID. One Undo reverses a changed group; success consumes the cut intent.
An all-same mapping is a successful no-op that consumes intent without changing
history, dirty state or a retained redo branch. Both success paths repaint the
destination tabs and preview before focusing the first mapped card. A changed
source refuses the complete group with an explicit request to cut it again.

Group style uses one owned review of at most fourteen selected complete cards.
One native SELECT offers Leave unchanged plus the five existing semantic palette
tokens (`primary`, `primary_container`, `secondary`, `surface`, `tertiary`) under
readable English/Polish labels. Leave unchanged/cleared choice cannot confirm.
Confirmation revalidates complete source snapshots, membership, context/profile,
epoch, document version and saved/server revisions before applying only palette
by stable ID to the current draft in one existing transaction. Hidden selection,
slots, array order, visibility, typed actions and unrelated edits are preserved.
All-same values close as a friendly no-op without history, dirty or redo churn.
Cancel retains selection and restores style-action focus; Escape ends selection
and clears the review. Native SELECT focus participates in modal Tab wrapping.
It adds no model field, raw RGB/theme authority, backend/schema/native change,
UUID, service, subscription or timer. Actual HA12/200 Node acceptance and its
eight original capture files are scoped in the deployment record; a natural
wait's preserved DOM/focus is not proof of an individual polling response.

Profile readouts describe the HA layout definition; they are not a
native firmware-version or capability probe. Status shows cached received
revision and snapshot readiness separately from physical applied confirmation.
Late polls cannot replace a newer completed Save or Reload transaction.

The same collapsed panel also shows bounded public identity fields from the
selected HA device-registry entry: name, manufacturer, model and stored software
version. This is read-only metadata returned with the existing layout query;
it adds no polling, storage, device action or native capability negotiation.
An unavailable device keeps its last stored values with an explicit caveat.
Missing registry entries and fields remain unknown. This readout does not
replace the independently verified full running ELF used for hardware QA.

Legacy options migrate deterministically. Unknown custom services and unsafe
implicit lock/cover actions become passive rather than silently mapping to an
unrelated operation. A removed entity may retain its configuration, but runtime
execution must revalidate the live state, registered service and parameters.
Configured action parameters are fixed tap presets, not native sliders.

Exports retain entity IDs required to restore a layout. They omit integration
entry/device IDs, credentials, camera URLs and runtime attributes. Import is a
dry run until explicitly saved, and incompatible profiles fail atomically.

## Passive solar information

The product profile advertises `sun_text_slots` for passive `sun.*` information.
The current profile admits the twelve ordinary text places (2–12 and 15) and
excludes the two large-value places 13/14. This is HA product-geometry metadata,
not a negotiated native capability or a new layout/wire version. The editor uses
that same list for assignment, moves/swaps, copy/cut and group destinations,
stored drafts, import and Save; absent capability metadata does not admit Sun.
The server independently requires a sensor/information card with `kind: none`
and a permitted place. Its live resolver and action catalogue keep Sun passive,
even if a raw or legacy card attempts a service/default/control action.

HA remains the authority for `next_rising`/`next_setting` instants. Both bounded,
aware future timestamps must be valid and distinct before the formatter selects
the earlier UTC instant. It retains the full date/year for comparisons and
converts through HA's configured timezone; missing, malformed, stale, unknown or
unavailable data never becomes an invented event. The compact display uses PL
`Wsch.`/`Zach.` or EN `Rise`/`Set`, followed by absolute `DD.MM HH:MM` in 24-hour
time. It has no relative day label, local astronomy or countdown. Existing
Roboto16 glyph advances bound these captions to 131 px against the narrowest 136 px
text label; the Roboto34 large-value labels cannot fit every event caption.

The existing selected-entity listener and coalesced tile sender own updates.
A single core-config listener in the bridge's existing `_unsubscribers` lifecycle
reprojects visible Sun captions on `time_zone` changes: the installed HA Sun
entity can keep its UTC attributes unchanged when its latitude/longitude/
elevation observer is unchanged. The callback schedules the existing tile push,
does not restart cameras or write configuration, and is removed on shutdown.
No new poller, font, native widget/task, buffer or snapshot owner is introduced.
Sunpath graphs, elevation and automatic theme remain separate future work.

## State and delivery lifecycle

`CameraBridge` retains its existing name but owns separate camera and tile
subscriptions. A layout-only options change replaces tile entity listeners and
coalesces a new tile push without restarting cameras or changing their options.
The existing debounce and serial send lock bound state bursts. Connection epochs
invalidate deduplication and prevent an old connection from claiming delivery.
Unload cancels owned tasks and removes owned listeners.
Source-status rechecks are limited to three coalesced owned attempts with
0.3/0.8/1.5-second delays, cancelled on a new revision, disconnect or unload. Legitimate
off-window work never starts an unbounded polling loop or a forced hidden render.

The native wire remains version 1. A complete projection includes all sixteen
slots, including `visible: false` entries for vacant places. This is required:
the existing reusable material component leaves omitted slots unchanged.
Optional revision/profile and per-card ID metadata identify the HA document.
The response-capable `home_tiles_get_status` explicitly advertises the correlated
press protocol. Its configured revision is a source-acceptance acknowledgement;
pending masks describe visual and context snapshot work. Saved means committed
in HA, sent means the API call completed, accepted means read back from the
firmware model. Applied remains null: none of these proves physical scanout.

Negotiated presses report slot, card ID and revision. HA rejects a mismatch
against the current saved/sent layout and does not permit a legacy slot-only
report to bypass a negotiated connection. Old firmware keeps the legacy path
with a pending/disconnected guard; it cannot provide the same correlation.
Native bindings capture a context generation at press and reject a changed
identity, revision, visibility or protocol mode before click.

Visual readiness and action-context readiness are separate. A title, state or
palette update marks pixels pending without disabling an otherwise current
action. Changing identity, document revision, protocol mode or visibility gates
that context until its visible page has been refreshed. The product acknowledges
the exact refreshed slot mask synchronously on the same LVGL task. This avoids
both stale actions after a move and repeated input suppression during ordinary
sensor updates. Off-window pending slots are allowed and do not force hidden
pages to render.

HA service-call context is preserved when an HA caller reports a tile press.
Native ESPHome-origin calls retain HA's existing device/system context. The
preview never calls entity services; capability discovery is read-only.

## Firmware buffers and invalidation

`modules/lvgl/material.yaml` registers the precompiled widgets with
`lvgl_material.MaterialTileSurface`. Configuration changes are applied on the
main firmware/LVGL task. No new worker, framebuffer or raw application snapshot
is introduced. The new data bindings add only small labels, including two hidden
icon anchors for the existing large-value sensor/time compositions.

The product supplies its local accent preference through the optional
`lvgl_material.tiles.configure.accent_override`. The component validates the
complete payload before projecting a single effective palette. It must not
temporarily apply HA's retained accent and then recolor the same tiles back to
the device preference: even identical final pixels would invalidate all their
snapshots on each state update. Without the option, the reusable component keeps
its existing themed and legacy custom-RGB behavior. The override adds no
persistent theme owner or pixel buffer.

The product refresh script coalesces a changed-slot bit mask, waits for idle
navigation, and patches changed regions on the visible Home page. Pending bits
for other pages remain until they become visible. It never renders a hidden
page just to refresh it. Home continues to own three raw RGB888 slots plus
compressed backing; display ownership and direct-region barriers are unchanged.
When a card becomes hidden, its retained geometry still identifies the rectangle
whose visible background must replace old cached pixels. Skipping that rectangle
would leave a ghost card in navigation snapshots. The product pending mask also
tracks this erasure; status reports its union with the component's visible-slot
mask. A zero mask is software snapshot readiness, not physical scanout proof.
HA owns managed-card titles, including window and presence. Product locale
refresh must not replace them with static translated placeholder text.

`home_tiles_get_config` exports only the current presentation model for bounded
readback and guarded QA restoration. `home_tiles_get_status` includes the full
running ELF SHA-256 so device evidence can be tied to the preserved native image.
Neither endpoint exports entity credentials or configured HA actions.

## Evidence

See the [implementation and validation record](../development/ha-dashboard-2026-10-24.md).
Host tests with HA adapters, a mock browser, actual HA deployment, complete
native compilation, device flash, screenshots and performance are separate
acceptance levels. Successful model tests do not establish end-to-end operation.
