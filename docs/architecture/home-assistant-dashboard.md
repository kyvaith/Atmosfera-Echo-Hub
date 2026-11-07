# Home Assistant dashboard configuration

HA81 adds an explicit Remote activity mode through the existing reviewed v3
Choice setup. Core supplies ACTIVITY4/activity_list/current_activity. Off can
enter as negotiated known empty; on with unknown activity stays unavailable.
The backend alone resolves the exact remote.turn_on(activity) target; ordinary
service cards still reject activity data. The editor offers one accessible
activity option with Confirm/Undo/Save and uses the existing metadata cadence.
Home keeps the power summary. [Evidence and limits](../development/remote-activity-design-2026-11-01.md).

HA79 adds explicit Remote turn_on/turn_off setup. New Remote cards are passive
until configured. Core power is independent of optional learning/activity flags;
only exact on/off states and an actual registered service admit execution.
An already completed transition is disabled. Existing press-context generations,
snapshots and state subscriptions own presentation; no native buffer/task/timer
or protocol field is added. The editor uses the existing larger M3 operation
options with Undo and explicit Save. [Scope and evidence](../development/remote-power-design-2026-11-01.md).

HA77 aligns the duration preview with the existing native compact formatter
and HA registry precision. It also displays an unavailable saved Vacuum room
explicitly without silently selecting another target. These changes add no
polling or native behavior. [Evidence](../development/duration-preview-design-2026-11-01.md).

HA75 adds explicit standard Vacuum action setup through the existing service
cards. Six localized wrapping options select a draft action with Undo and an
explicit Save, preserving inspector scroll when selecting. Metadata advertises
supported commands separately from current execution eligibility; actual
state/features/services are checked again at device tap. New robot cards are
passive. Native45's existing press availability generations and snapshots own
device presentation, with no new field, task or framebuffer. Standard Polish
vacuum returning text is shortened to fit the compiled136px caption; specific
entity translations retain priority. [Scoped evidence](../development/validation-2026-11-01.md).

HA76 adds one mapped HA room per Vacuum card. The existing service-card data
stores an exact area ID; Core's own area_mapping resolves it to vendor segments.
The editor never defaults to the first room, edits only the draft and has an
explicit room refresh. Up to32registered mapped areas have names rather than
raw segment IDs. Its selected Vacuum metadata refresh reuses the existing5s
status cadence and pending/epoch fences. Two backend registry listeners are
owned only while visible area cards exist; mapping/area removal can therefore
disable an ordinary native press without a state_changed event. They share
the tile debounce and are removed on rebind/unload. Device ownership, snapshots
and buffer counts are unchanged. [Design and limits](../development/vacuum-area-design-2026-11-01.md).

The Atmosfera Core integration owns configuration, live entity discovery,
capability checks and Home Assistant service dispatch. Its authenticated admin
panel is a client of the HA WebSocket API. ESPHome owns the fixed widget pool,
input and presentation; product YAML supplies its geometry and page membership.

### Stateless automation buttons (HA33)

An explicit v3 Action card with `action: {kind: event}` and an empty entity
binding creates one discoverable Event entity linked to the existing device.
The bridge owns authorization, current slot/card/revision checks and the private
entity callback. The fixed public `atmosfera_echo_hub_event` is informational;
it cannot drive the Event entity itself. No service target or custom event name
is stored in a card. See the [bounded contract](../development/tile-events-design-2026-10-30.md).

Only visible declared event cards have active entity bindings, at most14.
Moves and renames preserve the stable card/registry identity; hiding/removal
retires the callback. Core retains normal registry history. Previous presses
are not restored at rebind/reload. A state automation should exclude
`unknown`/`unavailable` so attribute changes and lifecycle transitions do not
simulate a press. Existing snapshot tiles own all device pixels and touch
arbitration; this feature adds no native widget, task or framebuffer.

## Management decision

Use the existing HA Core custom integration and its administrator-only sidebar
panel. It can reuse HA authentication, runtime entity states, area registries,
translations and service-call permission context. Versioned config-entry options
remain the durable authority, and the existing ESPHome API connection delivers
the bounded projection. This avoids a second device configuration server and
keeps the editor independent of firmware compilation.

The editor's accent mirror is scoped to the current ESPHome connection. HA52
also reads Core's existing typed TextState cache after attaching its one observer,
because Core may already have consumed the initial preference event. Match the
discovered TextInfo/device/key, reject stale/missing/invalid data, and retain any
newer synchronous callback. This seeds only the preview; saved options, the legacy
wire/locale handler, device preferences and subscription count retain behavior.
Actual device/API/browser parity after a Core restart is recorded in
`ha52-accent-scoped-acceptance.json` in the 31 October evidence directory.

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

HA40 formats only actual `sensor`/`device_class: date` calendar values as
DD.MM.YYYY in Polish or YYYY-MM-DD in English. It validates exact ASCII input
and Gregorian bounds, preserves exact user state labels and explicit outages,
and never applies numeric precision or timezone conversion to a calendar date.
Other domains and timestamp semantics are unchanged. The device receives the
existing bounded caption; no native field, widget, task or subscription is
added. The preview shares the strict calendar cases. The
[31 October record](../development/validation-2026-10-31.md) separates device
and visual acceptance from live browser interaction.

HA42 also admits passive `input_datetime` helpers: date-only, time-only and
combined local literals, with strict boolean capabilities and valid Gregorian
date/clock bounds. Seconds are preserved; the timestamp attribute is not used
for timezone conversion. Exact user labels retain priority. Only information
cards with no action are admitted, including raw/legacy resolver paths.
The optional trusted `datetime_text_slots` capability identifies slots
3/5/8/9/10/11/12. These have Roboto16 captions at least 172 px wide; the outer
tile width alone is insufficient. The first hardware campaign exposed clipping
in a 136 px caption. The editor now gates assignment, move/swap, clipboard,
draft/import and save on the same capability; absence fails closed. No firmware
field, task, timer, subscription or pixel buffer was added.

HA26 extends the optional active-state palette to read-only binary information.
Only exact on uses the configured role. Its optional auto icon resolves existing
compiled window/presence glyphs from the live device class; manual icons remain
fixed. This metadata survives the layout normalizer, but adds no native wire
field, object, font, task or framebuffer. HA entity translations retain priority;
only stock Polish presence Home/Away falls back to the product's Polish labels.
Sensor cards remain non-executable, including explicit raw/legacy actions.
The browser patches existing icon/role nodes on state changes and keeps one
draft/history owner. Runtime and visual evidence is in the continuation record.

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

The `echo-hub-m3-v1` profile retains the original sixteen bindings for older
firmware. A display with the response-capable carousel action exposes five
registered pages and thirty-two bindings. Slots 0 and 1 remain hidden
compatibility definitions. Slots 2..15 keep their original widgets and slots
16..31 belong to Tools. Each page has fixed geometry.

The editor saves the ordered list of visible page IDs as `home_order` in the
same revision as the card definitions. Home stays first and Apps stays
visible. Moving or hiding a page preserves its card IDs and settings. HA
retries a busy route update once the display can accept it. The device maps
that route to the existing widget roots and three-slot snapshot cache. The
versioned document is bounded to 32 KiB. The source model defines the exact
schema and WebSocket commands.

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

## Editor catalogue freshness

Numeric information cards can opt into `display_precision` (integer 0..6).
HA overrides only this projection's numeric formatting; registry options,
source units, other cards and Number controls remain unchanged. Text/date and
duration semantics retain the previous formatter. The compatibility normalizer
preserves the option, and the wire still contains only bounded subtitle text.
The editor's explicit precision preview accepts decimal text without a float
conversion, uses half-even rounding and reuses at most fourteen locale/precision
formatters. An absent override retains HA's frontend formatter. This adds no
native widget, field, task, timer or pixel buffer.

`state_color` is an optional HA document flag for entity cards in the light,
switch, input_boolean and fan domains. It defaults off. HA projects the selected
palette only for the exact observed `on` state and the existing surface role
otherwise; it never changes the user's selected palette or predicts a command
result. The compatibility normalizer must preserve the flag before projection.
No new wire field or firmware capability is needed. Existing tile bindings,
accent override and changed-slot snapshot lifecycle own the resulting pixels.
The editor applies the same policy to live state, patches CSS on existing nodes
and preserves the flag through draft/clipboard/export lifecycles. No timer,
subscription, raw allocation or action authority is introduced.

The frontend owns live state labels through the current `hass.states` map.
It patches text and availability classes on existing library labels rather than
replacing rows, preserving focus, drag state, draft history and selection.
Catalogue metadata and allowed capabilities remain server-owned; frontend state
must not invent actions or bypass server policy.

A weak reference map associates each fetched metadata object with the HA state
object visible when its request started. The existing five-second status cadence
refreshes stale metadata, including attribute-only changes, and coalesces pending
requests. Entry/selection epochs reject obsolete responses. Refresh is deferred
during drag, carry, confirmation, save, or focus inside the entity list; labels
continue to update without replacing focused controls. A selected entity outside
the current catalogue filter uses a bounded separate query. These references
reset when the user or device changes. No new timer, subscription, firmware
poller, native task, pixel allocation or snapshot owner is introduced.

## Firmware buffers and invalidation

Explicit v3 Choice cards share the existing detail owner. Catalogue metadata
exposes the complete bounded option list and a nullable current index. Projection
requires both negotiated native Choice and a currently valid full HA option
domain/service; an invalid list removes control routing and disables negotiated
ordinary press, so it cannot fall through to a default action. Unknown current
state can open the disabled detail without inventing option0. The editor reviews
conversion, preserves exact option values and performs no service from preview.
The [Choice contract](../development/choice-selection-design-2026-10-30.md)
records first-slice limits, generations, locale policy and hardware acceptance.

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

## Passive reported Calendar event

HA68 projects only CalendarEntity.event public state fields to the existing
wide slot12 text. Core owns event scheduling and local timezone conversion.
The integration owns bounded plain-text captions (PL/EN,40characters); no event
descriptions, locations or URLs enter the projection. Server metadata includes
the exact bounded observation; the editor uses a caption only while matching
that observation, otherwise Unknown until the existing5s catalog refresh.
Placement is validated server-side and in editor assignment/move/import paths.
Calendar actions remain none even for legacy/raw service requests. Existing
state subscriptions and presentation own updates; no new timer/native buffer.
Off-window snapshot work remains deferred until normal navigation; projection
readiness is distinct from visible capture readiness.
[Scoped validation](../development/calendar-next-design-2026-10-31.md).

## Passive Person state and wide-row caption geometry

HA70 adds passive Person state/zone in slot12. Core alone resolves trackers;
the product never forwards account IDs, coordinates, tracker/source attributes
or pictures. Cached HA translations take precedence for home/not_home; bounded
PL/EN fallback remains. Custom zones keep their names after plain-text cleanup.
The existing metadata cadence supplies exact-state captions, and a mismatch
shows Unknown. Missing runtime state in the editor shows Offline. Optional
state color uses exact home only; no action resolver accepts this domain.

The wide tile is440px but its Roboto16 subtitle is290px. Product module
caption_width.py holds319 advances/ink extents extracted from the hash-pinned
native45 font, enforcing288px plus40characters with visible ellipsis for Person
and Calendar. No font engine, new poller, native allocation or display task.
Regenerate and validate this table whenever typography or geometry changes;
the bound does not add unsupported glyphs to firmware. Existing navigation owns
off-window capture deferral. [Scoped acceptance](../development/person-presence-design-2026-10-31.md).

HA83 explicit media mute uses ordinary context press and existing admission
generation, no new native protocol/session/buffer/task. Public service requires
is_volume_muted bool, Core provider receives mute bool. Only opposite observed
target on powered capable bit8 source acts. Caption prefixes translated HA
boolean with mute context; default Play/Pause/title remains unchanged. See
../development/media-mute-design-2026-11-01.md for source pins and scoped proof.

HA85 media source is an HA-owned source_list/source facet using existing
Choice/session/fence and native45 buffers. SELECT_SOURCE2048, active state,
registered service and exact bounded option are rechecked; missing current
source is never first/empty.1..8names/32UTF8bytes, no silent truncation.
No new native protocol, app, allocation, task or subscription. See
../development/media-source-design-2026-11-01.md for Core pins and scoped proof.

HA87 repeat facet uses Core off/one/all and REPEAT_SET262144 through existing
Choice/session/fence. Normalize Core StrEnum only after exact membership;
unknown is never off/first. Native compact subtitles have136px Roboto16 budget;
HA87 uses measured compact captions shared with editor, preserving exact raw
service values and full Choice labels. No native protocol/buffer/task change.
See ../development/media-repeat-design-2026-11-01.md for scoped evidence.

HA88 extends measured136px compact captions to media source Home summaries
and editor preview. Choice labels and raw service targets remain exact; caption
truncation must never become command truncation. Metadata is bound to current
source/index. Native45 ownership/buffers/protocol/session are unchanged.

HA89 explicit shuffle_set bool uses existing ordinary context press, not a
new control session. SHUFFLE_SET32768, powered state, observed strictbool,
registered service and opposite target are rechecked. HA translations and136px
compact captions describe feedback, never predicted playback. No native
protocol,buffer,task,subscription change. See media-shuffle design for evidence.

HA90 relative volume_up/down maps to the existing ordinary context press. The
active source must report finite non-bool volume0..1, Core VOLUME_SET4 or
VOLUME_STEP1024 and a registered service. Endpoints inhibit only the exhausted
direction; configuration remains possible. HA sends entity_id alone, leaving
the provider/Core step and clamping in charge. PL/EN compact percentages are
observed presentation, not absolute targets. No NumericDomain/grid or native
control-kind change. Native46 adds raw deferred-press identity protection;
see the volume and deferred-tap design documents for acceptance boundaries.

HA91 adds media_player Choice/propertysound_mode on the existing app6 owner.
Require actual SELECT_SOUND_MODE65536, a registered select_sound_mode and1..8
distinct live rawnames up to32UTF8bytes. Observed current index, session and
authorization fences remain owners; missing mode never selects the first item.
Recheck exact list membership at dispatch and pass sound_mode alone with entity_id.
Localized compact captions are presentation only. No new native message,buffer,
task,timer or subscription. See media-sound-mode design for scoped qualification.

HA92 adds explicit media_player.media_stop under actual STOP4096.
Configure for known playback/power states; admit runtime only while playing,
paused or buffering. The observed-state caption uses HA translations first,
bounded PL/EN fallback and136px metrics. Dispatch contains entity_id alone;
provider feedback owns state. Existing native46 raw deferred-tap generation
rejects held caption ABA. No native message, buffer, task, timer or subscription.
See the media-stop design for scoped qualification and physical test boundaries.

HA93 adds an ordinary fixed media_player.volume_set action, requiring actual
VOLUME_SET4 and finite observed volume_level0..1 on active playback/power states.
The editor converts its displayed percent to volume_level, without quantizing
the source. The Home caption remains observed; an exactly matching target
disables press. Core/provider feedback owns the result. This reuses native46
ordinary context press; no Number domain/wire, native allocations or I2S changes.
Full continuous volume controls require a separate raw-observation contract.
See the media-volume-target design for the scoped runtime/browser qualification.
