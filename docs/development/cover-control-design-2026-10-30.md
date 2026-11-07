# Cover detail â€” W05 / CTL-005 first slice

Status: native36 is installed after full configuration/build, source-input audit,
preserved recovery artifacts, one OTA and exact ELF/marker verification. HA38
is installed with the IntFlag metadata fix described below. Baseline Home route
passes54FPS/79frames/failed0; two originals are complete, no new DSI event.
Native39tests/383subtests and HA492Python(3skip)/270JS pass. This is still
**device acceptance in progress, not full W05 completion**.

The first isolated MQTT attempt stopped before any native Cover command because
real HA `supported_features` retains `CoverEntityFeature` (`IntFlag`) in memory.
The initial strict plain-int check omitted Cover metadata and left the card
passive. Accept integer flags, reject bool/out-of-range/non-integers, and retain
strict boolean wire capabilities. A new IntFlag regression test passes. Exact
fixture cleanup and original16cards/3cameras/8preferences succeeded at layout87;
12 existing automation definitions match. Repeat the round trip on HA38.

One older native35 bridge-underrun remains unexplained; repeated normal routes
and12captures/eight Home round trips/90seconds idle showed no recurrence. No
DSI/ownership/acceleration path was changed by Cover. A no-fault repeat is not
a diagnosis or a fix. Preserve the failed run separately.

## First behavior

An explicit v3 Entity card for `cover.*` can opt into `control: cover`, opening
the existing shared app6. Three fixed native M3 buttons provide Open, Stop and
Close, plus authoritative motion/state and optional reported position. There
is no invented position, optimistic motor state or repeated command. Position
and tilt adjustment follow in separate slices.

This is a distinct control kind, not a Select pretending to be a momentary
action. Existing Light/Number/Choice codecs, old peer negotiation and ordinary
configured actions retain their behavior. Unsupported peers keep the explicit
card passive; no toggle fallback. Cover capability defaults disabled upstream.

## Ownership and bounds

HA validates actual supported_features and each domain service, owns the one
shared session/service fence, authorizes the caller and rechecks the complete
binding before dispatch. A bounded policy adapter uses current state, optional
integer0..100 position and allowed operations. Metadata ABA retires selection;
semantic state ABA advances generation and retires a held native contact.

Only known available states admit action buttons. Open/Close reflect whether
that operation is already observed; Stop requires observed movement and actual
STOP support. Observing opening/closing can confirm that HA reports the requested
movement, without claiming arrival or physical motor verification. Stop is
confirmed by a subsequently reported stationary state. Timeout never retries.

Reusable C++ owns the typed Cover state/input/command lifecycle. Product YAML
supplies a small fixed Cover widget group and translation/color references in
the existing application. Keep separate Cover/Choice child groups with explicit
mutual retirement before activating either. No new app, task, timer, raw image
or framebuffer; keep the single shared application work buffer and JPEG preview.
No per-open allocation or per-frame native redraw for a static state.

## Validation and isolated provider

Before code: inspect generic owner/codec/view lifecycle and all caller branches;
read both root guides. Add strict protocol/negotiation tests, metadata/value ABA,
authorization races, one-service fencing, duplicate/noop/unknown/endpoints and
real LVGL input/handoff tests. Validate full config, build, preserve/hash/audit
all inputs, flash once and verify full ELF plus preferences before runtime QA.

Hardware QA will use one uniquely named MQTT Cover and an owned HA automation
on private QA topics. Confirm broker and registry absence first; no household
cover or topic is targeted. Command messages drive explicit reported motion and
terminal states through the standard MQTT provider, with no optimistic mode.
See [MQTT Cover](https://www.home-assistant.io/integrations/cover.mqtt/) and
[MQTT discovery](https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery).
Use the installed Core2026.7.1 implementation as the compatibility reference.

Verify exact native/HA/MQTT commands, real provider state, stale/held/unknown and
capability mutation, original screenshots, browser review/Undo and repeated warm
handoffs among all control kinds. Preserve all original16 cards/3 cameras/8
preferences. Unbind and remove only the exact QA automation/discovery/registry
records created by this campaign. Existing automation definitions must match
their preflight backup. Compare normal Settings FPS, memory, DSI diagnostics and
media paths. Physical motor, audio load and lifetime remain distinct gates.

### Endpoint semantics

HA `open` also describes a partially open cover. Do not disable Open or return
already_matched solely for that state: a stationary reported position100 can
confirm the open endpoint; absent position remains unknown. Open stays usable
on a stationary partial/unknown-position cover. Opening suppresses duplicate
Open; Closing suppresses duplicate Close. A stationary closed state admits a
Close noop, and a stationary state admits a Stop noop. Reversing movement remains
possible even when the last position still equals an endpoint. A post-command
motion/state observation can confirm movement; it must not claim physical arrival.

## Required next slice: urgent Stop

The initial native36/HA37 candidate intentionally tests ordinary Open/Stop/Close
using the existing single-command owner. It is **not full W05 acceptance**:
ordinary pending currently disables Stop. Do not mark CTL-005 done or claim a
physical motor stop. The fixture is an isolated non-optimistic MQTT provider.

Before moving beyond W05, implement the plan's bounded priority Stop: one
successor only, cancel unsent movement, retain order after any already-started
HA service, replace the old observation without waiting its state timeout,
and ignore late old results. Keep metadata/selection/permission fences and
bounded lease; never send an old movement after Stop. Test slow authorization,
slow service, observation timeout, duplicate Stop, close/reopen and disconnect.
Position/tilt remain separate capability-based slices. A real motor's movement
and stopping need a designated physical Cover; MQTT feedback proves the software
round trip only.
