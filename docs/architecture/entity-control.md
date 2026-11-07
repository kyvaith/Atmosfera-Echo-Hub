# Entity control detail

## Optional Light detail and Climate panel

HA110 adds independently channel-bound detail profiles through
`entity_detail_get_features` / `entity_detail_bind_features`. The existing
Panel-v1 handshake still lists only Timer, Remote and Power. Old Light,
Number and Choice profiles retain their wire and policies. New Light cards
explicitly save `control: light, detail: 1`; their native open marker must
match that saved profile. Climate uses `control: panel, property: climate`
and requires its separate negotiated flag.

One shared selection, authorization slot and service fence owns all facets.
A read-only `facet` request selects one bounded main/numeric/choice view;
the matching state and `facet_result` receipt carry a monotonic view sequence.
Navigation never dispatches a service and is rejected while a service is
pending. Closing retains the existing rule: it retires the view but cannot
undo a call already dispatched to HA. No additional task, subscription,
service queue or framebuffer is introduced by the HA adapter.

Only one complete8-option catalogue is sent to native. HA retains exact
canonical service values and sends unique bounded labels; invalid translated
labels fall back to the complete canonical catalogue. Unknown is distinct
from an explicitly empty effect/program. The600px thermostat can consume an
exact numeric facet without impersonating Number. Actual mode/target changes
advance semantic generation; current measurements and HVAC activity remain
display observations and do not invalidate a held target. Range-only and
display-only Climate retain actual metadata and supported mode controls;
there is no guessed step, unit, hysteresis or autonomous heating loop.

See [the HA110 contract](../development/light-climate-detail-2026-11-04.md).
Host verification, firmware compilation and device acceptance are separate
claims; this adapter description does not itself establish hardware acceptance.

## Remote activity adapter

HA81 maps explicit v3 choice/property:activity to the existing single Choice
owner and app6. Require Core ACTIVITY4, registered remote.turn_on and the
bounded live activity_list. Off is known empty even when current_activity
retains a previous name; it uses the negotiated empty_choice_version1. On
requires a known current index; unknown/unavailable never selects an option.
The owner issues one exact remote.turn_on(activity), rechecks the live list
and generation and observes feedback. Static ordinary service cards retain
their no-data Remote power contract. Home reports power; the detail reports
the activity. No native transport, task, timer, subscription or buffer changes.
See [scoped evidence](../development/remote-activity-design-2026-11-01.md).

## Number current-value feedback

The Number presenter distinguishes a retained successful command result from
current value availability. When an idle/confirmed value becomes unavailable,
the value is `--`, both steps stay disabled and the native caption uses optional
text-provider ID16 (`number_control.current_unavailable` in the product). Pending
and error feedback keeps precedence. The protocol owner retains its last result;
recovering the source does not invent another command or reset its history.
Older text providers use the bounded English fallback. No buffer, worker, timer,
subscription or display ownership changes are involved. Native45's hardware
acceptance is recorded separately in the current development checkpoint.

## Climate target humidity adapter

HA64 extends the same v3 Number/propertyhumidity to Climate with actual
TARGET_HUMIDITY4, registered set_humidity and exact reported min/max/optional
integerstep. Reuse humidity_domain; omittedstep uses Core's integer granularity1.
Known HVAC modes includingauto/off/heat_cool can retain an independent target.
current_humidity never supplies that target; unknown/off-grid disables input.
Same Number owner/generation/authorization/service fence maps one step to one
exactintclimate.set_humidity, withoutHVAC/temperaturefields. No nativebuffer/
task/timer/subscription/protocol changes. See [scoped acceptance](../development/climate-humidity-design-2026-10-31.md).

## Humidifier target adapter

HA59/60 maps explicit v3 `number/property: humidity` to existing Number/app6.
The target is `humidity`, independently of `current_humidity`, mode and power.
Require reported integral bounds0..100 and an exact positive integral optional
step. An absent step uses Core's integer service granularity1; present None or
fractional metadata is rejected. The existing lattice retains a fractional tail
outside its last valid step. Unknown/off-grid targets or unknown power disable
input. Domain changes revoke the selection; its old lease cannot regain input.
The existing owner issues only `humidifier.set_humidity` with an exact int.
No native timer/task/buffer or polling subscription is added. MQTT fixtures and
separate actual final-source editor proof passed in HA60/native45/157; physical
actuator and long-duration gates remain independent. See the
[design/acceptance](../development/humidifier-humidity-design-2026-10-31.md).

## Precise light color-temperature adapter

HA62 maps v3 Number/propertycolor_temp_kelvin to app6 with exact1K granularity
from Core's integer service. Require reported color_temp support and actual
integral bounds within the product1000..20000K admission range. Current value
exists only while on/color_modecolor_temp; off/other-mode/missing/fractional/
out-of-range/outage disables input. No retained or converted color is fabricated.
Only exactint light.turn_on(color_temp_kelvin) is issued, through the existing
generation/authorization/service fence. State feedback may differ due to a lamp's
quantization; acceptance alone is not a match. No native buffer/task/protocol/
timer/subscription changes. See [scoped acceptance](../development/light-color-temperature-design-2026-10-31.md).
The broad slider and RGB remain separate W08 work.

## Light effect adapter

HA61 maps explicit v3 Choice/propertyeffect to app6 and its existing eight rows.
Require actual EFFECT4, a registered turn_on service and the complete bounded
effect_list. Explicit None while on/off is a negotiated known-empty selection;
missing, invalid and retained nonempty off values are unavailable. HA cached
labels are presentation only; dispatch uses the exact raw effect name. An effect
can activate a light; editor review states this explicitly. Core profiles/defaults
may also apply. The existing owner/generation/authorization/service fence remains
in charge, with no new native buffer, task, timer, protocol or subscription.
See the [scoped acceptance](../development/light-effects-design-2026-10-31.md).

## Fan speed adapter

HA63 uses v3 Choice/propertypercentage for1..7 actual loaded FanEntity speeds
plus0. Require SET_SPEED1, a registered set_percentage service, actualspeed_count
and reportedpercentage_step==100/count. Core's public percentage helpers own
the uneven mapping and checked roundtrip. Captured canonical values dispatch as
exactint; labels only append%. Current reportedpercentage is independent of
power/preset, never rounded or inferred. Count/step/capability changes revoke;
Core omits step on outage, requiring a fresh selection after recovery. The editor
warns that speed can start/stop a fan. Same Choice owner/fence/app6/eight rows;
no native buffer/task/timer/subscription/protocol changes. See [scoped acceptance](../development/fan-speed-design-2026-10-31.md).

## Fan preset adapter

HA43 adapts available fans with a known current preset to the existing generic
choice policy and app6. `preset_modes` supplies the complete bounded catalogue;
`preset_mode` supplies the observed index, independently of on/off power. Require
PRESET_MODE8 and the live registered `fan.set_preset_mode` service. Resolve the
service/field from product policy, never from a native client. The same lease,
semantic generation, authorization and single service fence remain owners.
List changes and loss of the feature revoke the selection; unknown/unavailable
does not expose a retained preset as current. Native40/HA45 additionally admits
an explicitly present None through negotiated empty-choice version1. The native
owner keeps an out-of-range sentinel and no candidate until an actual option is
selected; commands carry nullable expected_index. Public report decoding accepts
the structural extension, then the matched owner revalidates channel negotiation.
Missing/malformed/off-list values never become manual mode. Default fan toggle
is unchanged.

No native envelope, widget, timer, task or pixel-buffer change. The real MQTT
fixture, independent broker receipt before feedback, native screenshots, clean
browser Undo and55FPS post-feature route are recorded in the
[31 October validation](../development/validation-2026-10-31.md).
Manual-mode acceptance adds actual MQTT command-before-feedback, PL/EN originals,
browser review/Undo, exact cleanup127 and54 source FPS with no failed frames.
No new framebuffer, task or subscription was added. Physical fan movement and
speed/direction remain separate gates.

## Fan oscillation tile

HA46 adds explicit v3 `fan_oscillation`. Existing context-press and
press-enabled version1 negotiation owns touch admission. HA resolves the
opposite of the current strict Boolean `oscillating` at dispatch, with a live
fan state, OSCILLATE feature and service. Missing/malformed values disable it;
there is no inferred false and no power service side effect. Captions and active
palette describe oscillation independently of fan power. Ordinary fixed service
actions and presets retain behavior. No native task, buffer, timer or protocol
is added. Actual MQTT, device/browser originals and cleanup129 are accepted;
physical motor movement remains a separate gate.

## Fan direction choice

HA47 adds explicit fan choice `property: direction`; ordinary fan choice still
means preset. HA owns canonical forward/reverse and DIRECTION4/service checks.
The existing app6 and choice protocol receive localized labels and indices;
only the captured HA domain can map an index to a canonical service value.
Direction state is independent of on/off power. Null/malformed/outage cannot
become forward or manual. Labels join the captured capability fingerprint;
device locale changes reuse the existing coalesced state refresh and revoke a
selection whose labels changed. State ABA advances the existing generation.
No new native field, task, buffer, timer or subscription is added. MQTT,
device/browser originals, cleanup131 and54sourceFPS/failed0 passed; see the
[design and acceptance](../development/fan-direction-design-2026-10-31.md).

## Single climate target

HA50 adds explicit Number `property: temperature` for a single Climate target.
HA reads the actual target, feature1 without range2, explicit min/max/step,
registered service and loaded native/display units. Only matching°C or°F enters
the exact numeric domain; normalize Core's StrEnum to plain text after equality
checks. Unknown/off-grid/auto/range/outage never invent a target. The existing
number generation, authorization and service fence map one step to one absolute
set_temperature without hvac_mode. Unit changes reuse the existing coalesced
refresh and revoke incompatible selections. No native task/buffer/codec change.
See the [scoped acceptance and limitations](../development/climate-temperature-design-2026-10-31.md).

The thermostat view is an optional presentation of the same Number selection.
HA negotiates it once for the bound channel through
`entity_thermostat_get_features`. The snapshot carries a bounded set of
display-unit temperatures, provider HVAC activity and a dial position. An
unavailable numeric domain disables both step buttons while retaining the
provider's display data. An editable selection keeps the same absolute command,
semantic generation, authorization and feedback checks.

The thermostat uses widgets in the existing App 6 root. A version 2 peer can
advertise a draggable knob in the granted state. The LVGL task owns one
captured contact and renders only changes to the snapped preview index. The
view uses the same navigation handoff as Number. On release, the owner sends
one absolute lattice index with the captured index and semantic generation.
HA validates both against the selected Climate entity before dispatch.
Cancellation or an incompatible state update retires the contact. The dial
adds no timer, draw task or framebuffer. An older peer keeps the original
snapshot and step behavior.

## Climate HVAC mode choice

HA51 adds explicit Choice `property: hvac_mode`. HA owns the complete bounded
standard mode list, canonical service codes and observed index; normalize known
Core string enums before the exact domain. Entity translations in the device
locale provide labels, with bounded PL/EN fallback for missing/invalid/duplicate
translations. Labels join the capability fingerprint and never supply service
values. The existing generation/fence/authorization and app6 remain owners.
Catalogue or locale change revokes the selection; unknown/outage cannot select0.
No native task, timer, codec or buffer is added. Real four-mode MQTT/device/browser
acceptance and cleanup135 are in the [mode design](../development/climate-hvac-choice-design-2026-10-31.md).

## Climate program/preset choice

HA53 adds explicit Choice `property: preset_mode`, with feature16 and the exact
registered climate.set_preset_mode service. Current program is an attribute,
separate from HVAC state and target temperature. A real `none` catalogue option
has an ordinary index. Explicit None or inactive none absent from the catalogue
uses only negotiated empty-choice1; unknown/missing/off-list never does. Labels
prefer cached HA attribute translations and bounded distinct PL/EN fallbacks.
Canonical service strings remain untouched. The same single HA owner/app6,
state and capability fences and native40 lifecycle apply. No new native task,
timer, raw buffer or codec. See [design and evidence](../development/climate-preset-choice-design-2026-10-31.md).

## Climate fan and swing choices

HA54/55 add climate-only Choice properties fan_mode (feature8) and swing_mode
(feature32), each using its exact live attribute/list/service and HA attribute
translations. Current None/missing/off-list/outage is unavailable, never empty.
Do not infer a percentage or another axis. SWING_HORIZONTAL_MODE512 is distinct
and cannot grant swing32. HA56 separately adds swing_horizontal_mode512, with
its own exact live list/current attribute/service and service-editor whitelist;
32 without512 cannot grant horizontal. Real custom provider strings retained. The existing event-loop HA owner and native40/app6
retain all bounded state and lifecycle; no native buffer/task/timer/codec added.
List/labels/generations/service/auth checks revoke stale or held commands.
Actual MQTT/browser/originals/performance/cleanup139 and141 receipts cover these
facets; HA56 adds cleanup143 and15originals for independent horizontal.
Physical HVAC remains separate. See [fan](../development/climate-fan-choice-design-2026-10-31.md)
and [swing](../development/climate-swing-choice-design-2026-10-31.md) contracts.

## Humidifier compact power

HA57 admits humidifier/dehumidifier entities. Default compact press reads actual
known on/off and resolves the opposite registered turn_on/off, with no mode or
humidity field. Context identity/revision, connected current configuration and
negotiated press-enabled1 remain required; old reports are refused. This follows
current-state ordinary compact-tap policy, not detail-grant replay semantics.
HA projection/event-loop owner and native40's existing bounded Home slot window
own all data; no native task/buffer/lifecycle added. HA state translations and
bounded PLEN fallback, opt-in active-state colors reuse existing roles/contrast.
Actual MQTT, both classes, mode-feature0, negative cases, Home images/browser and
cleanup147/performance evidence: [power contract](../development/humidifier-power-design-2026-10-31.md).
HA58 adds explicit mode Choice with MODES1, actual bounded available_modes/mode
and set_mode; no power/humidity command. None is unknown, never manual. Real
None reset and sticky-bit empty-list revocation, originals/browser/cleanup149 and
performance are accepted in the [mode contract](../development/humidifier-mode-design-2026-10-31.md).
Target humidity remains separate. Installed Core MQTT has a sticky
Modes bit after list removal; never use that flag without validating actual list.

## Cover and priority Stop

The Cover view reuses app6, its existing application work buffer, the one
entity-control owner, lease and input lifecycle. Three fixed LVGL buttons expose
Open, Stop and Close; authoritative HA state may include an integer position.
Unknown position is never synthesized. Position/tilt setters remain separate
roadmap work. No additional native task or full-screen allocation is introduced.

The local native37/HA39 priority extension leaves every `entity_control_v1`
envelope unchanged. Optional typed API actions query feature version1 and bind
it to the exact new channel. Both peers reject stale or mismatched acceptance;
rebind/disconnect clears it. The fork defaults `priority_stop` to false. HA39
keeps Cover passive without acceptance, while other controls keep working.

An admitted Stop can replace one ordinary pending movement. HA cancels the old
local authorization/observer, preserves a service already dispatched, and waits
only its bounded dispatch fence before freshly authorizing Stop. Late movement
results cannot revive the previous command. A movement not yet sent stays
canceled. There is one bounded successor, no automatic retry and no implicit
Stop when closing the view. A held negotiated Stop survives ordinary position
updates; unavailable state, metadata change and lifecycle loss still retire it.
The device's Stop deadline is28s; ordinary commands retain13s.

The [design and test gates](../development/cover-priority-stop-design-2026-10-30.md)
distinguish host checks, software round trips and physical motor acceptance.
HA39 is installed; native37 full build and hardware acceptance are pending.

HA27 adds Automation's default enable/disable action to the existing ordinary
tile policy. Exact off resolves turn_on; exact on resolves turn_off with
stop_actions=false, allowing an existing run to finish. It never infers trigger.
Explicit trigger and turn_off expose optional strict skip_condition and
stop_actions booleans. Omitted explicit parameters retain HA's existing defaults;
the editor explains them and localizes the three service labels. Unknown,
missing, unavailable, unsupported, read-only and stale card/revision contexts
fail closed. The existing negotiated ordinary availability is reused. Palette
on means enabled triggers, not a running sequence or successful command.
The existing HA session/context and resolver own dispatch; firmware's pool,
buffers, tasks and protocol are unchanged. Original native31 images, actual
isolated automation/helper execution, cleanup and measured performance are in
the [continuation record](../development/validation-2026-10-30-continuation.md).

HA22 adds an optional typed `timer.start` preset: `duration` is a whole number
of seconds in 1..86400. The editor labels its unit in PL/EN and explains that
an empty field omits the parameter. Static validation and the live resolver
reject invalid duration data; dispatch preserves the caller's context and the
existing card/revision guard. A default or explicit no-duration start still
resumes HA's retained remaining time. Explicit cancel retains its existing
service and now displays a localized action prompt; preset prompts include
the configured duration. Prompts describe the next action, never command success.
There is no new native timer, task, field, buffer or per-second tile refresh.
Local countdown and a shared Timer detail remain separate work.

Native31/HA22 passes one isolated 90-second preset, pause by the QA provider,
native resume retaining 88 seconds, native cancel, original screenshots and
guarded cleanup to the original sixteen cards at revision 22. The HA service
observer sees exactly start(duration=90), pause, start(no duration), cancel.
Normal Home input -> Settings -> Home retains 54 FPS with a contiguous borrowed
scroll buffer. See [current evidence and limits](../development/validation-2026-10-30.md).

Current native26/HA19 retains the two-assignment cached-result reset on a fully
accepted new GRANT. The common owner resets result/reason with the command
sequence; renewals and close-cancel retain current feedback. The isolated Number
before/after native25 hardware campaign and its31-FPS Settings comparison pass
with original-image review. Native26 also passes PL/EN/PL Number originals and
one31-FPS Settings comparison. The temporary locale fixture is removed after an
owned five-field inverse and actual unbound/closed proof at clean layout12.
User humidity6/Light7 positions are retained.
See [current validation](../development/validation-2026-10-25.md).

HA18 extends the existing ordinary-action availability policy from input_button
to button/scene/script without firmware fields or buffers. One public HA
predicate delegates to the existing action resolver and is reused by card
projection and initial capability negotiation. Existing unknown-first
button/input_button/Scene states remain executable; unknown Script stays blocked.
Script modes, service authorization and dispatch are unchanged. The isolated
Scene campaign on native26 passes disabled/restore-while-held suppression and
one fresh action with actual virtual-Boolean feedback. The exact five-field
inverse and both fixture deletions pass at clean layout14, preserving human
positions. Two post-install matching Settings cycles retain31 source FPS,
failed0 and released owned buffers; a transient largest-block drop recovers on
repeat. Mixed whole-loop CPU windows are not a controlled comparison. Scope is in
[today's validation](../development/validation-2026-10-26.md). This does not
implement the complete ordinary-action pending/error/result lifecycle.

Installed HA19 also makes a default Timer tile state-aware: idle->start,
active->pause and paused->start without duration. Installed Core Timer semantics
preserve remaining time on resume; presentation shows the next default action
in the selected PL/EN language. HA resolves the live operation at report arrival,
not a new operation token captured at finger-down. The existing optional
availability/captured-context behavior is reused. Local countdown, Timer detail
and full command-result UX are separate work. Native diagnostic input and actual
isolated HA Timer remaining/deadline feedback pass; owned inverse/cancel/delete
restore clean layout16. A Settings comparison with the same muted microphone
workload retains31 source FPS/49frames, average31330us/max33244us and failed0;
owned work buffers are released. The original unmuted microphone is restored.
Whole-install memory/global CPU, physical touch, audio and lifetime remain open:
most of the measured memory difference predates the Timer fixture, and later
voice/microphone lifecycle is not isolated. See today's validation.

Earlier native24/HA16 passed its full build/input audit, one OTA, full running
ELF, 60-second Home1 health, normal controller Home1->2->3->4 route and the scoped
ordinary input_button availability/HA feedback campaign. Three matching Settings
cycles retained 31 source-rendered FPS with zero failed frames. Root acceptance is
`w01-native24-availability-root-acceptance-v1.json` (SHA
`5f1456dd497de5413628034dfa6a7b1186cade5c85e16ffc7facb3216048ae67`).
The temporary input_button was unbound by a five-field inverse Save from
layout 7 to 8, then deleted by its exact helper ID after native readback. Human
humidity slot 6 and Light slot 7 positions are retained; see the validation record. This does not accept physical GT911, a household
actuator, all ordinary-action pending/error UX, audio or long-duration lifetime.

### Earlier native23/HA15 checkpoint

Earlier native23/HA15 has passed complete build/input audit, OTA, full running
identity and60-second Home1 health. Original images confirm restored Polish
weather and the Number value/unit/labels. One owned Number open/close passed
without commands; the earlier isolated0→0.25 native/HA feedback pass belongs to22.
Tests used revision5 after the user's DnD: humidity6, isolated Light7 and Number15.
Current revision6 restores only the six QA fields, retains those positions and
the original sensor card15, and has no remaining owned QA fixtures.
The corrected revision5 Light Off/On/brightness60 sequence passed three native
state_matches, exact paired HA service/state feedback and original-image review.
Isolated Number min/max and two signed fractional steps also passed native, HA
feedback and original review. Two scoped Settings cycles each rendered31 FPS
with failed0; free memory plateaued and the largest block recovered on repeat.
These do not prove physical input, held-domain changes, audio or lifetime. See [current validation](../development/validation-2026-10-25.md) for
separate scopes and retained failures.

Previous scoped Power checkpoint: native21. The native Power presentation
fence below passed host regressions, complete build/input audit, one OTA, fresh
full identity, Home1 health, original images and five ready open/close pairs.
One separate On test emitted exactly one command and reached already_matched
with both buttons still ready. A paired180-second HA observer saw zero explicit
selected-light services and unchanged on/raw202. The user confirms this entity
has no available physical lamp; this is software UI/NoOp acceptance only.
HA14 was active at that checkpoint with source/storage/API/browser-read verification; Number22 was
subsequently flashed and native23 now runs its product-only boot-locale correction. Native20's failed stale-base
On test remains the retained negative control; its initiating request is unlogged.
See the current validation record for exact evidence and performance limits.

Historical HA13 checkpoint (2026-10-25): HA13 was installed with twenty-two-file package
and canonical parity, unchanged full config entry and working layout/catalogue
APIs. Five owned native19 cycles and nine cold readiness observations passed
after that deployment, with original image review and zero explicit selected-light
services in the paired observer. The old command feedback persists on reopening
and remains a separate behavioral finding. The following earlier checkpoints
retain their original scope; see the resumed-day validation record.

W03 adds an explicitly selected light detail in application 6: On/Off and one
brightness scalar. As of 2026-10-24, firmware v16 passed its complete running-ELF
identity check, visible Home health and the original app6 glyph review. One
open/close completed in 19.510 seconds with zero explicit selected-light On/Off dispatches in
the paired HA observer. HA dev12 is now active with the reviewed v3/revision3
layout. A separate diagnostic drag completed in 13.360 seconds: exactly one
current brightness60 command followed its owned release, and HA observed one
`light.turn_on` with `brightness_pct:60`. The reported state stayed on/raw202;
Zigbee2MQTT recorded `NwkRouteDiscoveryFailed (0xd0)` for the selected provider's
child command. Software dispatch is proved; the resulting HA state and physical
actuation remain **unconfirmed due to the external Zigbee route failure**.
No inverse or restoration command was sent. The regional candidate60 and
HA-accepted status do not replace the authoritative hero79. The view closed
before its eight-second state-observation timeout, so timeout presentation was
not exercised by that run.

The v16 per-glyph scratch/bounds fix passed real-font tests and removed the
regional numeric corruption in the individually reviewed original image.
The v15 original glyph failure, failed12 Home and failed13 report attempt remain
FAILED; firmware14 was never uploaded. Physical GT911 input, sustained motion,
lifetime/audio and total retained-memory acceptance remain separate gates under
[validation](../development/validation.md) and the
[live deployment record](../development/live-ha-deployment-2026-10-24.md).
Local source adoption is not Git publication or full end-to-end acceptance.

The later five-cycle native16 pilot completed its owned open/close pairs without
actuation, but its last original shows disabled power buttons. Control readiness
is unresolved; neither a settled application nor a retained regional image is
a readiness acknowledgement. Native17 provides explicit owner/widget diagnostics
for investigation. It compiled and passed its compiler-input audit but has not
been flashed because the device became unavailable before OTA. Native18 completed
one OTA with exit0 at 2026-10-24T22:06:28Z. Its full running ELF, scoped Home1
health and original screenshot passed on 2026-10-25. The five-cycle light pilot
completed its transitions but failed readiness in cycles 3–5; Auto Home passed
separate scoped Off/Idle30 checks. Physical input, sustained drag, audio and
performance acceptance remain open; see the
[resumed-day validation](../development/validation-2026-10-25.md). Native18
source contains HA6; the later HA7–12 editor packages are separate installations. HA12's
group-style acceptance (200 Node/250 shim tests, eight original capture files,
zero explicit selected-light calls in a scoped 180-second observer) adds no
native control contract or readiness proof. No Save/entity action was used in
that draft-only test; see the deployment record for its exact limits.

Local native19 source adopts a product-owned policy in the existing boot hook,
after persisted settings and before the first application preview. Public
`lv_obj_remove_theme` calls remove only MAIN DEFAULT/PRESSED theme entries from
the two On/Off buttons. Declared styles, 80% pressed opacity, focus and disabled
behavior remain; the inherited extra pressed black recolor35 is intentionally
removed. Generation equality checks, buffers and tasks are unchanged. Native19
is built, audited, flashed and independently identified. The original interrupted
campaigns remain failed; a diagnostic reproduction identified an unrelated
camera report rejected by the harness. With exact passive-camera recognition,
five owned pairs and nine fixed ready observations passed, with original visual
review and unchanged memory capacities. Physical actuation, sustained dragging,
audio and broad performance acceptance remain open; see the
[current hardware record](../development/validation-2026-10-25.md). Native18's
failed cold samples remain the negative control.

## Ownership and admission

The HA shared `ControlSessionOwner` keeps authorization, channel/token/revision
correlation, lease, deduplication, one outstanding service fence and ordered
reconciliation. HA14 negotiates one generic Light/Number connection mode and
multiplexes the domain hooks through that same owner. The exact legacy Light
codec/API fallback remains available; an advertised but refused generic mode
must not silently downgrade. Generic messages add explicit control kind and
remain bounded to2048 UTF-8 bytes.

`numeric_domain.py` uses exact minimum-anchored micro-unit arithmetic, six
fractional places and at most one million intervals. Unknown/off-grid remains
null and zero remains numeric. Number captures index and semantic generation
on press; release emits at most one step. HA rechecks the live domain/index/
generation and permissions before the selected Number domain's `set_value`. State precedes its
terminal result; lease renewal alone does not cancel an unchanged intent.
The [Number contract](../development/number-stepper-design-2026-10-25.md) retains
the detailed opt-in, ABA and pending-result rules and remaining acceptance gates.

HA34 extends that exact Number policy from input_number helpers to device
`number` entities. The saved action remains explicit `control: number`, with no
implicit action fallback. Catalogue, open and dispatch independently require the
selected entity's own domain service (`number.set_value` or
`input_number.set_value`); one cannot substitute for the other. Live min/max/step,
unit and current value use the existing bounded exact decimal lattice and
semantic generation. The shared owner, service fence, app6, widgets and view
lifecycle are unchanged. HA34/native35 device acceptance covers an actual ESPHome Number,30→35→30,
held value ABA, four warm reopenings and browser review/Undo.
[Evidence and limits](../development/validation-2026-10-30-continuation.md).

HA31/native35 add the opt-in Choice profile to that same owner and app6. HA
policy hooks validate select/input_select options and dispatch exact
`select_option` values through the existing service fence. A complete list has
1..8 distinct printable values, each at most32 UTF-8 bytes; invalid lists are
passive, never truncated. Exact reserved unknown/unavailable values are rejected.
Current unknown/off-list state remains unknown and disables input. Native glyph
validation disables the complete chooser when it cannot display an option.

Eight preallocated option buttons hold one local candidate. Apply captures the
current index, candidate and semantic generation and emits one command. State
ABA cancels a held contact; list mutation revokes the session. A revoked view
stays disabled with a reopen explanation until the normal application close.
The product locale policy instead deliberately closes app6 before rebuilding
locale snapshots. Old two-kind peers remain accepted without gaining Choice.

Choice does not use the Scalar worker and adds no worker or pixel buffer. It
reuses application6, the existing shared raw work buffer and compressed preview
lifecycle. Its reusable colors come from configured active/neutral widget styles;
resolution and geometry stay in product composition. The product header uses
ellipsis while the option row wraps its exact display value. See the
[bounded Choice contract and device evidence](../development/choice-selection-design-2026-10-30.md).

Native26 adds an optional Number text-provider role15 for the display
separator. Only an exact comma with an available non-placeholder value-font
glyph changes the existing label's transient copy; otherwise it retains a dot.
Canonical numeric text, owner snapshots, index/generation and protocol remain
unchanged. The existing LVGL task and label own this presentation; no pixel
buffer, field, task or font asset is added. Full build/input audit, actual flash
and running identity, PL0,25/EN0.25/PL0,25 originals and one Settings comparison
pass separately. Fresh actual unbound proof, exact locale-helper cleanup and the
restored Home4 original/browser also pass at clean layout12.

| Owner | Sources | Responsibility |
| --- | --- | --- |
| HA shared session (canonical local source) | `control_session.py` | One authorization/selection/command/service lifecycle and ordered reconciliation |
| HA domain and transport | `light_control.py`, `entity_control.py`, `entity_control_codec.py`, transport, controller, layout/cards and `numeric_domain.py` | Explicit configuration, domain eligibility/service policy, live capabilities and permissions, connection epoch and caller Context |
| Reusable native control | `lvgl_material/material_entity_control*`, `entity_control.py` | Strict protocol/codec, selection, lease, pointer input, command/result sequence and view generation |
| Native view lifecycle (Phase A source) | Component-owned `ControlViewLifecycle`; public Scalar proxy | Captured admitted/closing/overlay generations, navigation admission and one close-cancel recovery |
| Regional renderer | `material_direct_scalar_control.*`, `material_scalar_raster.*`, `direct_scalar.py` | Cached styles/glyphs, latest candidate, one RGB888 canvas/worker, source retirement and snapshot handoff |
| Navigation/compositor | `lvgl` navigation and direct-region owners | Transition admission, expected base generation, framebuffer leases and coherent LVGL/DSI handoff |
| Product | `modules/lvgl/light_control.yaml` (legacy), opt-in `entity_control_number.yaml`, `pages/light_control.yaml`, Material/navigation/theme/i18n and media/Voice policies | App6 composition, captured-generation opening, scene fences, locale and notification/Voice/sleep decisions |

Reusable code contains no HA service names, entity IDs or product coordinates.
The new components default off; product admission defaults false. The preserved
validation builds explicitly override admission to true. An exact capability and
bind exchange plus an explicit v3 Light/Number control action are required. Existing
v2/default actions do not migrate implicitly. A marked control never falls back
to an ordinary toggle when unsupported or disabled.

The strict `light_brightness_v1` protocol is bounded to 2048 UTF-8 bytes. Channel,
open sequence, selection token, card ID/revision and command sequence distinguish
connection, opening and interaction. The 30-second lease, duplicate suppression,
live revalidation and unload/disconnect guards belong to the session owners.
Correlation and client-name hints are not authentication or encrypted-transport
proof; HA retains its actual permission and Context checks.

Device reports use raw ESPHome action data for the node name and JSON payload.
The immediate script owns a string copy until the synchronous send completes.
Do not pass JSON through `data_template`: Home Assistant may convert valid JSON
text into an object before service validation. Keep the strict text schema and
2048-byte limit.

### Ordinary input_button availability (native24 / HA16)

HA owns live availability policy. TileBinding owns the flag, press generation
and captured input; navigation owns the cached page images.

Reusable `MaterialTileSurface.action_availability` defaults off. An explicitly
enabled product advertises integer `press_enabled_version: 1`; HA16 sends the
optional strict Boolean `press_enabled` for ordinary input_button cards only.
It cannot be mixed with a Light/Number `control_kind`. Old/disabled capability0
keeps its prior wire behavior. The existing contextual card ID/revision contract,
Light/Number session codec, fixed object pool and navigation snapshot gates remain.

HA resolves the action against the live entity/service policy again at dispatch.
An existing input_button in `unknown` state has no press timestamp yet and may be
pressed; a missing/unavailable entity is disabled. The Boolean is availability,
not a pending command or a service-result acknowledgement. Other ordinary action
domains do not gain a complete pending/error/result lifecycle from this slice.

Native availability changes invalidate the captured press/context generation.
Disabling cancels the owned LVGL input before adding DISABLED; the input waits for
release, so false->true while held cannot revive the old contact. Only the
availability layer's own DISABLED state is removed on recovery. The existing Home
tap-defer/snapshot-ready/quiet gates remain; no new controller runtime hook, pixel
buffer, worker or display ownership path is added. A new contact can dispatch once
when current context and HA policy both allow it.

Actual P4 DWARF shows 8 extra bytes per TileBinding, 128 bytes for 16 bindings and
no MaterialTileSurface object-size increase. Linker static RAM remains 295544
bytes. This is a static layout cost, excluding allocator/capacity overhead; it is
not a heap, leak or lifetime proof. Original disabled/enabled Home4 images and
three scoped Settings cycles are recorded in the current validation section.

## Input and rendering

Motion changes a bounded latest-value mailbox and local rail/value bubble; it
does not update native labels or call HA on every event. One worker coalesces
intent with a nominal configured 34 ms interval, rounded up to scheduler ticks;
this is not a hard wall-clock cadence guarantee. Fonts/styles are cached on the
owner task; the worker does not access LVGL
or font objects. The numeric hero changes at authoritative state/release
boundaries. Unknown brightness remains `--`, without a fabricated thumb value;
on/off-only capabilities disable brightness. A known on/off state with brightness
capability can admit a deliberate absolute intent from real motion.

One changed, current release emits one HA command; cancel/lost input emits none.
Explicit On restores the light without inventing brightness, and brightness 0
means Off for this light adapter. These semantics are not a generic number API.
HA service acceptance and a matching reported state do not prove physical effect.

Opening captures the granted selection generation before the asynchronous product
script. It rechecks that generation before NAV admission and after actual open
and settlement; it must never read a new generation late to authorize old work.
The renderer additionally requires matching request and nonzero base generations.
State/result boundaries flush native labels before publishing the new base.
Queued/carry results and source retirement are software ownership evidence,
not physical scanout ACKs. Retirement means the caller can reclaim that source,
including when work was dropped; it is not proof that its pixels were displayed.

### Native Power presentation fence

The existing component-owned lifecycle captures the On/Off pointer's selection
generation. Before LVGL presents its native pressed style, the Scalar backend
stops and drains its existing worker and consumes the preceding completion
against the unchanged request/base-generation checks. Its persistent regional
carry stays registered; no pixel buffer, task or framebuffer copy is added.

While that pointer owns the fence, authoritative state continues to update the
owner but cannot submit another regional frame. Release emits the ordinary
single command. The lifecycle's existing owner loop then flushes the final native
boundary and publishes the latest current candidate once against the new base.
Cancellation, selection replacement, overlays, navigation and failed drains
retain their captured-generation and fail-closed behavior. Stale completions do
not become successful merely because they coincide with native input.

Only a ready concurrent renderer advertises this fence. A native-only backend,
disabled Scalar or failed acceleration setup must not acquire a latch that would
depend on Scalar being looped. The no-acceleration regression covers two
successive power commands and terminal reconciliation with no Scalar loop.
Real-LVGL host tests cover changed/unchanged state around native pressed flushes,
both retirement orders, cancellation and a real in-flight worker drain. These
ordering tests are separate from P4 scanout, timing and physical actuation proof.

## Scene and close lifecycle

The opt-in NAV `try_open_application`, `try_close_application`, `try_show_home`,
`try_refresh_home` and `try_prepare_application_snapshots` return real admission
results. Product must branch on false before changing the scene; a void callback,
script wait or log message is not a barrier. Admission is not settlement.
`suspend_for_snapshot(250)`, `resume(captured_generation)` and style refresh use
the renderer's actual quiescence/generation checks. Low-level widget and snapshot
entry points remain caller-owned.

`require_primary_slot` admits a request to the existing compositor slot 0. It is
**not a lifetime lease** that prevents a later legacy producer from submitting.
Product therefore stops, drains and releases competing Weather, Player wave,
artwork, marquee and Volume presenters, and fences their periodic, HA-state,
delayed and physical-entry paths for the whole app6 session, including transition
and close-cancel preview. A temporary global pause is balanced before Scalar
runs; paused direct-region submission is not a working renderer.

For close/capture, revoke input, stop the producer and wait for its in-flight
source to retire. Acquire only the caller's counted pause, pass the real barrier
and sole-lease check, then perform coherent DSI/LVGL handoff. Capture into the
same free regional canvas, release its direct region and expose a read-only
native image alias. The alias adds no second pixel buffer. Hide/flush it and drop
its image-cache references before the worker can overwrite the canvas. Consume
only the owned pause. A failed drain/handoff retains required references and
refuses transition rather than freeing a still-borrowed source.

The Phase A source extraction keeps one `ControlViewLifecycle` inside
`MaterialEntityControlComponent`. It owns the four existing admitted, overlay,
closing and cancelled-close generation words and the existing lifecycle
callbacks. Scalar remains the owner of the canvas, worker, in-flight source,
framebuffer/pause leases, alias and real quiescence/handoff. Its public
resume/suspend methods and registered navigation guard forward into the bridge;
the bridge is driven at the original Scalar loop position. It adds no scheduler,
queue, raw surface, frame copy or protocol/configuration change. A default-disabled
presenter does not attach or drive another presenter's lifecycle; a second enabled
backend for the same control is rejected rather than silently replacing it.
Native20 compilation and target object sizes are now measured separately from
host proof; its On-input failure above prevents overall power-control acceptance.

Actual close revokes the captured view generation. Only native close-cancel
recovery may resume that still-current, visible, settled and unexpired selection;
YAML must not duplicate it. Failed product preparation keeps its owned IO/touch
suppression until verified cleanup. Notification, Volume, media auto-open,
theme/locale, Voice and sleep paths must not bypass that latch. An explicit new
contact may retry its cleanup; it does not force readiness or clear native
uncertainty. A system notification ends the light selection, obtains a true
close/drain and waits for settlement before showing. Dismissal does not resume
the old selector; reopening needs a fresh grant. Voice/sleep follow the same
ownership rule; an external backlight-Off callback cannot undo an electrical
change already requested.

## Bounded memory and diagnostics

App6 reuses the existing single raw application work slot; compressed-preview
metadata rises to six entries with one decoded slot. No extra full-screen
framebuffer or compositor pool slot is introduced. The proposed 564x112 region
has these nominal named capacities:

| Storage | Bytes |
| --- | ---: |
| RGB888 source canvas, 128-byte aligned | 189,568 |
| Reserved glyph masks | 49,152 |
| Allocated worker stack | 8,192 |
| Scalar-owned subtotal | 246,912 |
| Same-sized copy in the existing global persistent slot | 189,568 |
| Nominal named total | 436,480 |

The total includes that nominal global copy, not its possible larger retained
capacity from Weather or other previous geometry. It excludes Component/codec,
widget/callback/task/transport metadata, allocator overhead and transient costs.
Release invalidates a slot but does not imply heap shrinkage. The 512 KiB
whole-session target is **not accepted** from this calculation or build result.
Setup-time capacities are reused across selections; closing a view is not a
promise of allocator release. A retained shutdown stack remains counted.

Explicit memory diagnostics count Scalar canvas, reserved glyph capacity and
allocated stack once, with used glyph bytes separately. The native direct-buffer
diagnostic reports all four global capacity rows, including invalid retained
slots; do not add the global copy twice. No diagnostic poll/task is added.
Target PSRAM/internal-RAM, largest block and stack high-water, repeated open/close,
Weather/audio regression, original screenshots and physical touch still require
their own evidence. See [runtime memory](runtime-memory.md) and the
[extension guide](../development/extending-ui.md).

### Optional Scalar performance observations

`direct_scalar.performance_metrics` defaults to false. When no instance enables
it, generated defines exclude its state, clock reads and hooks. The v17 test
image explicitly enables it; canonical product defaults remain false. This is
not a zero-cost claim for mixed enabled/disabled instances or the product API
registration itself.

The owner publishes a bounded logical-origin timestamp with the latest request.
The existing worker owns cumulative counters and separate drag/stable latency
histograms. A finite seqlock snapshot is read only while the producer is quiet;
busy or inconsistent observations return unavailable rather than reset/retry.
No new worker, timer, pixel buffer or per-frame log is added. A full cold read
emits all 129 bins for each histogram; phase percentiles require bin deltas.
The reported upper-bound p95 is unavailable without samples or in the overflow
bucket. It is not an exact continuous percentile.

Measured latency ends at an accepted source retirement. It includes worker
wakeup, but does not measure GT911, VSYNC, scanout or input-to-photon latency.
Observed origins, submissions, BUSY responses, retirements, accepted/unconfirmed
results, superseded requests and value deduplication remain distinct counters.
A deduplicated value does not invent a presentation sample.

Product `debug_scalar_performance(phase)` is an explicit cold diagnostic: its
1..32-character ASCII phase is copied before logging, and no borrowed API
string is retained. Owner readiness, actual On/Off disabled flags, renderer
quiescence and direct-base generation precede the optional histograms. Structure
sizes and the calling task's lifetime minimum free stack are separate evidence;
the latter is not the Scalar worker's stack measurement. Collect these outside
timed gestures. Native17 device/performance acceptance is still pending.

After source17, canonical code also retains a metrics-only last-current owner
decision: request/selection, completed/current base and accepted/success flags.
This adds at most 32 bytes to the optional component state, not a pixel buffer
or a new allocation call. It survives cancellation and can be logged even when
histograms are unavailable. It can belong to an older view; correlate selection
and request IDs before drawing a conclusion. It was not part of the preserved
native17 image and has no target acceptance yet.

## Vacuum suction adapter

HA65 admits explicit v3 Choice/property `fan_speed` for vacuum only. It needs
FAN_SPEED32, the registered set_fan_speed service and 1..8 distinct printable
raw fan_speed_list names of at most32 UTF-8 bytes. A known activity and an exact
current fan_speed identify the observed option. Missing/null/off-list/outage
never become a default or a known-empty preset. HA attribute translations and
PL/EN fallback labels remain presentation only; collisions use raw labels.
The shared Choice owner maps one admitted index to one exact raw service value.
It sends no additional start/pause/dock command. No new native resources or
wire schema. [Scoped acceptance](../development/vacuum-fan-speed-design-2026-10-31.md).

## Cover opening percentage adapter

HA66 adds explicit v3 Number/property `position` for Cover with SET_POSITION4,
registered set_cover_position, and Core's canonical0..100 integer percent domain.
Only a reported current_position in a known cover state supplies the observation;
tilt, open/closed labels, missing/null/fractional values never infer a position.
Reuse the Number owner/ABA generation and existing renderer. Each admitted step
sends one integer position; no extra open/close/stop/tilt command. Matching the
reported position does not assert a physically stopped motor. Core owns vendor
range normalization. No new native resources or wire schema.
[Scoped acceptance](../development/cover-position-design-2026-10-31.md).

## Independent Cover slat tilt adapter

HA67 reuses Number for explicit v3 property `tilt_position`, requiring
SET_TILT_POSITION128 and set_cover_tilt_position. Only current_tilt_position
supplies the canonical0..100 integer percent observation; current_position and
cover state labels never infer it. Same Number owner, generation and service
fence; one integer tilt_position call per admitted step, no primary movement
or implicit stop. Core owns raw vendor range conversion. No native resources
or wire changes. [Scoped acceptance](../development/cover-tilt-design-2026-10-31.md).

## Explicit ordinary mower actions

HA73 reuses ordinary service cards and negotiated press_enabled for explicit
start_mowing/pause/dock. Product module mower_actions.py owns the conservative
state/feature admission table; Core/provider owns state and service execution.
Supported configuration operations are distinct from currently eligible ones.
The live resolver checks admission again and never substitutes a default start.
Core IntFlag capabilities remain valid integers; bool is rejected. Existing
native availability generations cancel held/dragged stale gestures. A held
finger may defer snapshot capture; admission projection is observable then,
while actual visible capture is fenced only after release. No new native task,
buffer or protocol. [Scoped validation](../development/mower-actions-design-2026-10-31.md).

## Explicit ordinary vacuum actions

HA75 uses the same ordinary service-card and negotiated availability path for
start/resume, pause, stop, return_to_base, locate and clean_spot. Product module
vacuum_actions.py admits actual Core capabilities and an explicit activity
table, separately from supported configuration operations. No command is
inferred for a new/default card. Core/provider feedback remains authoritative;
the live resolver rechecks admission. Locate can remain usable in a reported
error without admitting movement. Existing suction Choice controls retain
their independent policy. The native task, protocol, buffers and snapshot
lifecycle are unchanged. See [design](../development/vacuum-actions-design-2026-11-01.md)
and [scoped acceptance](../development/validation-2026-11-01.md).

### One mapped HA area per card

HA76 additionally admits vacuum.clean_area with one explicit cleaning_area_id.
Core owns area_mapping and segment dispatch; the browser uses actual HA area
names, and vendor segment IDs are absent from device projection. The live
resolver rechecks the real feature, service, current mapping, area and activity.
Registry-only mapping changes reuse the existing tile push; two filtered HA
listeners exist only while visible area cards are configured and are removed
on rebind/unload. No new native protocol, task, timer or buffer. Core's MQTT
feature-only publication issue is documented separately; it never authorizes
Atmosfera to infer a missing published capability.
See [bounded design](../development/vacuum-area-design-2026-11-01.md).

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

## Negotiated combined Cover panel

Candidate87/HA107 extends the existing Cover kind3 and shared App6 owner through
an optional channel-bound `cover_panel_version: 1` handshake, after the existing
priority Stop handshake. Legacy peers retain their exact v1 fields and commands.
The negotiated extension carries actual device class, independently nullable
tilt position and five additional capabilities: primary position, open/close/stop
tilt and tilt position. Every capability requires both its Core bit and service.
Primary position remains the existing outer observation. No missing position,
class, endpoint or separate tilt-motion state is inferred.

Both numeric rails use integer0..100 absolute targets, one command on release;
HA owns provider normalization. The existing lease, authorization, generation
and service fence apply. Position, tilt and primary state ABA cancel normal held
movement. Matching-axis Stop may supersede one pending motion only; Stop never
crosses between primary and tilt families. Known feedback may preserve a held
Stop, but unknown state or changed metadata revokes it. Closing does not stop.
Standard HA has no independent tilt-stopped observation: StopTilt cannot claim
`state_matches` from an unchanged position or service return.

The integration adds no native task or framebuffer and no second control owner.
The product composes two optional native axis groups and actual-class SVGs in
the existing application. Existing scalar position/tilt adapters remain usable.
See [the contract and validation scope](../development/cover-panel-design-2026-11-04.md).

## Dedicated robot and mower panels

Candidate88/HA108 appends opt-in kind6 `robot` to the same App6 session owner.
The `robot_type` discriminator selects Vacuum or Lawn Mower product composition;
HA retains the existing domain-specific capability/service/activity admission.
The device receives fixed operation bits, current eligibility, exact bounded
suction names and at most eight complete mapped room names. HA keeps room IDs,
vendor segments and the mapping fingerprint. An unsupported room catalogue
disables only that facet; existing fixed-area adapters are unchanged.

One explicit room choice plus confirmation submits one exact HA area command.
Mapping changes and A-B-A events revoke the selection through the existing
filtered registry listeners, including while authorization awaits. Battery is
optional actual source telemetry; it neither invents charging nor cancels held
actions. Normal command generations include activity, suction and eligibility.
Eligible Stop/Pause interrupts reuse the single bounded predecessor fence.

Robot Locate and Area have no standard effect-specific observed postcondition.
Their bounded terminal `service_completed` means the awaited HA callback
returned successfully, with UI copy "Polecenie przyjęte przez HA". It is never
motor, sound or selected-room confirmation. Exceptions/timeouts remain failures
or unconfirmed. Legacy codecs reject this status; the generic owner hook is
disabled by default. No new native task or framebuffer is introduced.
See [the Robot contract](../development/robot-panel-design-2026-11-04.md).

## Panel kind7 families

The optional Panel kind7 adds Timer/Remote/Power to the same session, App6
renderer lifetime and service fence. Its strict family capability is negotiated
separately by entity_panel_get_features/entity_panel_bind_features and bound to
the current channel. No extra task, polling subscription or full-screen buffer
is owned by a family. The existing HA state subscription and lease renewal
supply observations; Timer's visible countdown uses configured HA time and the
existing component loop at most once per second. Countdown/sample changes do
not cancel a held control, while authoritative phase/deadline/duration ABA does.

Timer set_duration is a repeatable restart and terminates only with callback
completion semantics, never an inferred timer-finished event or unchanged
active-state proof. Remote and Power retain absolute, source-confirmed commands.
See [Panel design](../development/panel-kind7-design-2026-11-04.md) for fields,
scope and the separate pending Action-to-Camera handoff. Host checks do not
establish firmware or physical-device acceptance.

## Light detail and Climate facets

Candidate90c/HA110 keeps the same selection, App6 owner and service fence.
An optional channel-bound detail handshake independently admits explicit
Light detail and Climate Panel launchers. Existing Light, Number and the
exact Timer/Remote/Power Panel-v1 negotiation retain their previous shapes.
Existing saved launchers are not silently reinterpreted.

Only one numeric facet or bounded catalogue is active. Parameters is a local
capability menu, not five retained sessions. Read-only facet requests carry
the complete identity and view sequence; a matching snapshot and readiness
receipt precede input. Commands also bind the semantic generation and exact
observed index. Measured climate temperature/humidity and activity telemetry
do not cancel a held target gesture; authoritative target, mode, domain or
catalogue changes do. A drag previews locally and submits one absolute
command on release. Missing step, unit or genuine Kelvin observation never
produces invented edit bounds or a default value.

Light suspends and drains its existing direct scalar region before a native
facet replaces its base. Climate reuses the existing large native thermostat
arc; neither family adds a framebuffer, worker or polling timer. Native90b
also removes one redundant outgoing ControlMessage stack copy: the private
emitter marks its caller-owned message generic in place, while the public
const synchronous sink, reentry guard and strict serializer validation stay
unchanged. The caller retains message ownership for the entire callback.

Candidate90c schedules an in-app facet handoff as one captured intent in the
existing component loop, outside the LVGL RELEASE callback. It retains only
selection/state generation, source/target facet, view sequence and a bounded
deadline. It neither queues requests nor retries a failed transfer. The same
admitted generation remains available to close the application while the
presenter changes. After the correlated result or timeout, the selected root
is updated before exactly one resume attempt. A stale intent is discarded;
a failed drain retires the selection through the existing close path. The
target ABI cost is16B in the existing component;
there is no new task, image buffer, codec arena or wire field.

After an explicit Detail selection is revoked, its visible application keeps
an unknown hero/state and hides the inherited Scalar hit region, including any
retained presentation alias. Cancelling the renderer still precedes this
visibility change; only the existing presenter drains and retires a borrowed
source. Hiding its parent neither frees the canvas nor changes framebuffer
ownership. The saved pre-Detail widget flags remain owned by this retired view
until a fresh GRANT restores them before the next control family initializes.
A pending or cancelled OPEN cannot reveal an old value or initialize another
family's widgets against that temporary mask. The next valid Scalar resume
removes its alias through the existing quiescent handoff.

Native Detail facets do not require Scalar readiness. A numeric hit rail keeps
its configured transparency when disabled. Unknown Climate observations replace
an idle historical success caption, while pending commands and errors retain
their precedence. Decimal localization changes displayed text only; wire values
and the target lattice remain canonical.

Color1 adds an optional color facet to this same Light Detail selection and
channel after its own query/bind handshake; it consumes no Extra profile. Its
H/S rails edit a bounded local draft, so release does not send a light command:
the explicit Apply action does. A powered color-temperature source can seed
the view and exposes an explicit switch-to-color action. HA alone preserves
the captured raw brightness. Existing view/semantic-generation and authorization
fences apply, including source ABA retirement. The optional product composition,
swatch ownership and separate evidence boundaries are documented in
[Light Detail Color1](ha-light-color.md).

Range1 independently extends the same Climate Detail selection after a supported
query response and current-channel bind. It reuses the existing Climate root,
600px dial, knob and +/- controls. Two additional product objects supply a
Range/Back launcher; the existing Mode/Parameters controls become Lower/Upper
only inside Range. The selected endpoint is local UI state. Existing pointer,
view and semantic-generation fences protect the source pair and the single
preview index; release sends one absolute pair, while entry/selection/Back,
unchanged input and cancellation send nothing. Source pair/mode/raw-preset
changes retire held input; current-temperature/activity telemetry does not.
The HA adapter alone resolves the numeric lattice and publishes the paired
service. See [Climate Range1](ha-climate-range.md) for eligibility, unit
qualification, confirmation and the separate demo-provider boundary.

The source-only P4 probe for104 places the96 B Range payload inside the existing
variant: Snapshot728 B, Message960 B, Detail296 B and owner1160 B remain unchanged;
the component grows11664→11680 B (+16). This is a relocatable target-object
measurement, not final linked static RAM or live heap. Two new LVGL objects and
retained shared inset styling avoid another dial subtree, task or raw framebuffer.
Public LVGL and source/schema checks remain separate from build, OTA, boot
and device evidence. The104 hardware batch passed paired-input/restore checks with a qualified
MAIN display follow-up, closed by the separate105 device/visual acceptance. The
existing low/high metadata must not become an editable scalar target or an
invented knob position. The105 presenter formats the known ordered pair in
MAIN only for available heat_cool without a scalar target. It measures the
complete string with the existing font/spacing/content bounds; a long pair
uses the localized Range caption, keeping exact values in the limits row.
No font state, widget, wire value, variant, input or buffer is added. The105
build, linked audit, OTA and bounded device route passed; five original
screenshots verified MAIN/Range/Back, the original scalar and restored Home.
No static RAM growth was linked; flash grows512 B and the changed function
frame16 B. Qualified first boot retains the known recovered mixer allocation
retry. See the resume checkpoint for the distinct104/105 records and limits.

See [composition and scoped validation](../development/light-climate-detail-panels.md).
Full build, first boot and device acceptance remain separate records; the
latest state is in the development resume checkpoint.

## Optional read-only Agenda

Agenda1 extends the existing Info/App6 owner and channel, without adding a ninth
Extra profile. Optional response-only query and current-channel bind follow Info1;
the reusable option defaults off. An explicit `property: agenda` launcher leaves
legacy Calendar info unchanged. HA retains at most sixteen events from a fixed
seven-day window; native retains one event in the existing Extra variant. Core
owns calendar fetching and the existing bridge task coalesces source callbacks.

PAGE is a read request, never COMMAND or a provider service. Current Read
authorization, source object/registry identity, selection and generation fence
new reads. Native waits for both matching STATE and receipt; timeout does not
retry. Semantic list replacement retires held input and resets the index. Closing
unsubscribes and releases HA cache; empty/error/retired views clear old event text.
See [read-only Agenda](ha-agenda-panels.md) for dates, excerpts and exact limits.

Product 106 reuses Calendar labels/SVG/status and adds only Previous/Next buttons
with two labels; no full-screen buffer, scroll list or animation task. The source
P4 probe measures Agenda 340 B, unchanged Snapshot 728 B/Message 960 B/codec 5152 B,
owner+24 B and component+48 B total. These are ABI measurements, not linked RAM
or live heap claims. Host public-LVGL/config checks and full106 compilation/linked audit passed.
The linked106 delta is +256 B static RAM and +25072 B flash; it is separate
from the ABI probe and live heap. The first106 chime boot failed in mixer
retirement, before HA127 installation or Agenda device acceptance. Frozen107
retains all Agenda inputs and repairs only audio session ownership. Its full
build/linked, first boot and five software restarts subsequently passed scoped
checks. HA127 is now installed, and one explicit slot12 migration produced
layout399. Six read-only PAGE requests and seven original event/reopen images
passed partial behavior/visual checks; the127 editor showed the saved Agenda
action with no draft. Native107 then panicked on App6→Home before the final
Settings/performance/audio batch. The original FAIL is retained. A35s read-only
recovery observation confirmed107/127/399/Home1 without new faults; this is not
full Agenda acceptance or a memory/performance guarantee. See the
[current checkpoint](../development/resume-2026-11-05-datetime.md).

## One typed family payload

Native91 retains one conditional `std::variant` payload in each control snapshot
and message instead of storing every family at once. Legacy Light uses the
empty alternative; other families use their own bounded value type. The owner,
incoming decoder, and synchronous outgoing message keep their existing
lifetimes. There is no new heap allocation, task, framebuffer, or wire field.

Reads use nullable typed access. Requested identity does not establish the
payload type: an OPEN pending for Detail can still retain the preceding Number
payload until GRANT. Decode validates a candidate before committing the new
alternative. A view must reacquire typed access after any callback or handoff
that can replace the owner's payload; no reference survives that boundary.

The exact native91 linked build reduces static DIRAM by1792B versus90e. The
minimum conservative stack margin in the six reviewed paths is5856B, versus
560B previously; that is a scoped call-path audit, not a global stack bound.
These firmware totals overlap component-size savings and must not be added to
them. Device acceptance and source hashes are recorded in the
[resume checkpoint](../development/resume-2026-11-04-panels.md).
