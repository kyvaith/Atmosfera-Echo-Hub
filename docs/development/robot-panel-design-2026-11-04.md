# Robot panels — candidate88 / HA108 proposed contract

Approved contract implemented in the HA108 backend after candidate87 source
capture. Parent approved the eight-room bound and Robot-only service completion.
Native/product device acceptance remains separate; no device qualification is
implied by the backend host test checkpoint.

## Scope and ownership

Append one optional kind6 `robot` to the existing entity_control_v1 capability.
Use one shared ControlSessionOwner, one App6 lifetime and service fence, one
native Robot primitive with `robot_type: vacuum|lawn_mower`. Product owns separate
SVGs, labels and layouts so each device has a recognisable view. No framebuffer,
native task, permanent timer, second command queue or arbitrary service executor.
Old kind lists and codecs remain exact when Robot is not configured.

Product action: `{"kind":"control","control":"robot"}` on either domain.
Native capability negotiation through the existing kind list is sufficient;
this new kind has no legacy renderer to negotiate separately. One default-off
`robot_controller` configuration registers its reusable widgets and callbacks.

### HA editor catalogue

Profile adds `schema_robot_control: true` and includes `robot` in
`schema_control_types`. Transport exposes `robot_control_supported` through
the existing negotiated `control_kinds`. Catalogue adds exactly:

```json
"robot_control": {
  "version":1,
  "robot_type":"vacuum",
  "caps":{"actions":63,"speeds":["min","medium","high","max"],"areas":["Salon"]},
  "catalogue_fingerprint":"<64 lowercase hex SHA256>",
  "area_reason":null,
  "state":{"activity":"docked","available":true,"speed_index":1,
           "battery_percent":null,"eligible_actions":49,"area_enabled":true}
}
```

Fingerprint includes actual type/actions/speeds and private area IDs/segment
mapping/name, so editor capability review can detect a changed mapping even if
labels remain equal. It is not an authorization token. `area_reason` is null
when supported, otherwise `unsupported`, `no_mapped_areas`, `too_many_areas`,
or `area_labels_unsupported`. A missing room facet does not disable the panel.
Editor selection requires at least one supported action or valid suction/room
facet, the matching negotiated kind, and current source metadata; unknown state
is a separate runtime disabled presentation. Review caps/type/fingerprint;
routine observed activity/battery changes must not reset the draft.

Existing standard action admission stays authoritative in `vacuum_actions.py`
and `mower_actions.py`; exact suction options reuse `ChoiceDomain`. Existing
fixed-area service adapters stay intact. No changes to Player/Camera/Voice/Gallery.

## Exact snapshot fields

Existing identity, title, state_seq, ttl_ms and state_generation fields remain.
Robot grant/state adds exactly these fields:

```json
{
  "robot_type":"vacuum",
  "activity":"docked",
  "available":true,
  "speed_index":1,
  "battery_percent":null,
  "robot_caps":{
    "actions":63,
    "speeds":["min","medium","high","max"],
    "areas":["Salon","Kuchnia"]
  },
  "eligible_actions":49,
  "area_enabled":true
}
```

Actions are a strict integer bit mask, with fixed meanings:

| Bit | Wire operation | Vacuum service | Mower service |
|---:|---|---|---|
| 1 | start | start | start_mowing |
| 2 | pause | pause | pause |
| 4 | stop | stop | unsupported in installed Core2026.7.1 |
| 8 | dock | return_to_base | dock |
| 16 | locate | locate | unsupported |
| 32 | spot | clean_spot | unsupported |

`robot_caps.actions` is0..63 for Vacuum and a subset of11 (1|2|8) for Mower.
Every bit requires the existing domain capability AND registered service.
`eligible_actions` is a subset of supported actions calculated using the exact
existing activity/admission table, not the more permissive browser heuristics.
The sample docked Vacuum eligible49 means Start+Locate+Spot with all three
capabilities exposed. The protocol does not infer a default operation.

Vacuum activity is cleaning/docked/idle/paused/returning/error/unknown. Mower
activity is mowing/docked/paused/returning/error/unknown. `available` means a
recognised actual domain activity, including error, not necessarily actionable.
Unknown/unavailable collapses to unknown, availablefalse, eligible0,
speed_indexnull, battery_percentnull, area_enabledfalse. Preserve actual caps
when metadata remains valid so an outage disables rather than changes identity.

`speeds` contains the complete exact catalogue:0..8 distinct strings, each
1..32UTF8bytes, using existing Choice validation and FAN_SPEED32/service.
Invalid/oversize catalogue becomes[] and disables only suction. `speed_index`
is a strict in-range integer or null; no fabricated first option. Suction is
enabled only while available and the actual current index is known, preserving
the existing Choice admission, including its existing treatment of error state.
Mower requires speeds[], speed_indexnull and areas[].

`battery_percent` is a strict integer0..100 or null from an actual published
source attribute, never inferred from docked or from a missing property. Do
not invent a battery entity. Initial implementation may display a valid
entity-owned `battery_level`; modern same-device sensor discovery remains a
separate source-binding extension. No charging inference or icon is included.
Battery-only updates publish state_seq but do not bump semantic generation or
cancel a held command. Missing/fractional/invalid battery remains null.

## Mapped room selector

Reuse existing `vacuum_areas.py`: CLEAN_AREA16384, registered clean_area,
entity-registry vacuum.area_mapping and real HA area-registry names. Vendor
segment IDs and raw HA area IDs remain on HA. Wire sends the complete list of
names, in one immutable selected catalogue; command index resolves to that
exact current HA area_id. Keep a private fingerprint of the mapped segment
lists so mapping A-B-A cannot escape detection merely because names stayed equal.

Bound initial native catalogue to0..8 exact unique printable names, each
1..32UTF8bytes. More than8, overlong/ambiguous names, malformed mapping or no
usable mapping disables only this facet (areas[]). No first-eight truncation,
name rewriting, fallback room or inferred segment. HA editor metadata carries
an explicit reason such as `too_many_areas`, `area_labels_unsupported`, or
`no_mapped_areas`; no claim that all32 possible existing mappings fit this wire.
All existing fixed-area adapters continue supporting their existing32-map limit.

`area_enabled` is true only with a complete nonempty catalogue and existing
area-command admission (docked/idle/paused). The on-device picker starts with no
selection; selecting one room previews it, then an explicit labelled Start
button sends one `area` command. It never starts by opening the picker or by
defaulting to the first row. No multiple-area selection in this contract.

Registry edits may happen without state_changed. Extend the existing two
filtered registry listeners for visible Robot Vacuum cards/selected entity;
feed the same coalesced publisher and immediately observe/revoke a changed
selected catalogue, including changes during an authorization await. Remove
listeners under the existing unload/rebind lifecycle. No polling loop.

## Commands, result semantics and lifetime

Button commands carry `op` from the six fixed names and
`expected_state_generation`; they have no target. `speed` and `area` additionally
carry strict integer `target_index`0..7. The native pointer captures the exact
operation at press: a visible Start button cannot turn a held gesture into Pause.
Apply the existing channel/token/revision/lease, exact sequence, authorization,
metadata and service dispatch fences. Revalidate the real service and source
admission immediately before dispatch. No optimistic state or synthesized motor
activity. Repeated held touch, drag, close/reopen or duplicate envelopes never
repeat a service. Closing never dispatches Stop, Pause or Dock.

Type, supported actions, suction catalogue or room mapping changes revoke the
selection. Activity, suction index and eligible-operation ABA advance semantic
generation and cancel ordinary held movement/settings gestures. Display-only
battery changes do not. Unknown feedback disables commands.

Keep a single bounded priority successor for an actual eligible interrupt:
Vacuum Stop/Pause may supersede pending Start/Spot/Dock/Area; Mower Pause may
supersede pending Start/Dock. Never supersede suction/Locate, never chain a
second successor, never run services in parallel. Reuse Cover's predecessor
fence mechanics, not its domain predicates. An interrupt must still be enabled
by actual current activity; do not assume a pending start already moved the
robot. Interrupt capture may retain nonfuture generation through known feedback
while the same interrupt remains eligible. Metadata/unknown/authorization loss
cancels it. Normal Start/Dock/Spot/Area/Speed remain strict generation-bound.

Expected feedback: Start/Spot -> cleaning (Mower start -> mowing);
Pause -> paused; Vacuum Stop -> idle; Dock -> returning or docked; Speed -> exact
raw selected fan_speed. A match confirms reported HA activity only, not motor
movement, a cleaned room, arrival at the dock, or a physical sound. Never suppress
Locate as already_matched: it has no observable standard postcondition.

For Robot Locate and Area only, introduce terminal `service_completed` with reasonnone,
published only after the awaited blocking HA service callback succeeds. Native
clears pending and shows **"Polecenie przyjęte przez HA"**, never "Wykonano" or
"Zlokalizowano". A callback exception remains rejected/service_error; timeout
remains not_confirmed/service_timeout and cannot be retried automatically.
Area has no standard room-specific observed postcondition: generic cleaning
cannot confirm which room was selected. Display that activity separately.
`service_completed` is forbidden for every legacy control kind and other Robot
operation. Add a default-off owner completion hook; do not broaden the legacy
Light codec. Existing accepted/confirmed statuses remain unchanged elsewhere.

## Product view and migration

Vacuum: original SVG robot illustration, translated observed state, optional
actual battery, primary Start/Pause button, Stop and Dock controls, secondary
Locate/Spot chips, suction choice and mapped-room picker only when supported.
Mower: distinct SVG body/deck/wheels or Material mower icon, observed state,
Start/Pause and Dock. No synthetic Stop, maps, battery, progress or schedules.
Use accent-derived M3 surfaces and existing known contrast. Static SVG/state
changes only initially; do not copy continuous web SVG/CSS animation to LVGL.

Migrate only slot10 existing mower service -> Robot launcher, slot22 existing
Vacuum start -> Robot launcher, and hide duplicate suction slot23 after full
panel acceptance. Preserve entity IDs and every other layout field/card/order.
No action on carousel tap except opening the selected dedicated view.

## Source checks, mocks and acceptance

Repo sources verified read-only: `vacuum_actions.py`, `mower_actions.py`,
`vacuum_areas.py`, `choice_domain.py`, cards/controller metadata and listeners,
`tools/ha_demo/atmosfera_demo/entities.py`, custom `lawn_mower.py`, demo layout.

The owned Vacuum is Core demo index0 (`vacuum_1`), with min/medium/high/max and
real clean_area implementation. It offers five segment names. Its dock routine
publishes returning then schedules docked30s later; don't mistake that scheduled
callback for an unintended new command. Locate invokes HA persistent notification
and changes mock activity to idle; that is demo behavior, not proof of a buzzer.
The owned mower only changes its simulated activity and advertises bits1|2|4.
Live registry mapping/current source identities still require parent read-only
verification before migration; no child has altered or queried live HA here.

Core references: [installed-tag Vacuum](https://raw.githubusercontent.com/home-assistant/core/2026.7.1/homeassistant/components/vacuum/__init__.py),
[demo provider](https://raw.githubusercontent.com/home-assistant/core/2026.7.1/homeassistant/components/demo/vacuum.py),
[installed-tag Mower](https://raw.githubusercontent.com/home-assistant/core/2026.7.1/homeassistant/components/lawn_mower/const.py).
Current dev adds Mower STOP8/idle; this package deliberately keeps the installed
policy and does not infer new services:
[dev Mower](https://raw.githubusercontent.com/home-assistant/core/dev/homeassistant/components/lawn_mower/const.py).

HA UI inspiration: [Vacuum controls](https://raw.githubusercontent.com/home-assistant/frontend/dev/src/dialogs/more-info/controls/more-info-vacuum.ts),
[Mower controls](https://raw.githubusercontent.com/home-assistant/frontend/dev/src/dialogs/more-info/controls/more-info-lawn_mower.ts),
[Vacuum SVG](https://raw.githubusercontent.com/home-assistant/frontend/dev/src/state-control/vacuum/ha-state-control-vacuum-status.ts),
[Mower SVG](https://raw.githubusercontent.com/home-assistant/frontend/dev/src/state-control/lawn_mower/ha-state-control-lawn_mower-status.ts).
Use these for hierarchy and recognisable forms; draw product SVGs rather than
copying web animation/glow/filter pipelines.

Host acceptance: all action capability/service/activity combinations; unknown,
error and partial support; both exact option catalogues; complete8 bounds and
9 rejection; maxUTF8/escaping within2048/arena; mapping/area rename/delete ABA
across await; held Start cannot morph to Pause; same-owner interrupt ordering;
unauthorized/expired/close/rebind and duplicate services; battery-only update;
Locate/Area callback success/failure/timeout, and old codecs rejecting new terminal.

Device acceptance: immutable firmware/editor/source IDs; saved fresh layout;
real mock service-event ledger before feedback, no passive actions; all Vacuum
and Mower controls, exact suction and mapped-room command; supported-only widgets;
unavailable/error/no-map/oversize catalogue; physical-display screenshots,
close/reopen, original source restoration, route performance/heap/DSI checks in
one batch. Host tests, flash, screenshots, touch injection and physical motor
behavior are separate claims. No physical robots are established by these mocks.

## HA implementation checkpoint

Full host suite:911 passed,2 skipped,4370 subtests in25.40s. Receipt:
`C:/aeh-build/device-panels-20261104/ha108-full-tests.txt`.
Focused Robot coverage includes actual domain admission, complete room limits,
max escaped wire, strict legacy terminal isolation, callback success/failure/
timeout, area registry ABA, no passive action, single exact service dispatch,
battery-only update, authorization/close races and the shared interrupt fence.

Parent read-only live receipt `robot-live-source107.json` established layout351,
Vacuum features32700 and four actual suction names, mapped HA area atmosfera_demo
to simulated living_room, plus mower features7. Neither source publishes battery.
No backend agent performed live writes or physical hardware actions. The current
Cover87 boot issue is being handled separately from this frozen Robot backend;
Robot build/flash, screenshots and performance remain pending.
