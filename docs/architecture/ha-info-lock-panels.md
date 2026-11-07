# HA Info / Lock panels

This contract is deployed as HA112 with native92a and layout356, following the
separate storage91 checkpoint. The device batch passed five family views and
their observation/Lock scenarios; all17 original screenshots passed review.
Evidence: `C:/aeh-build/device-panels-20261104/extra92a-device-first/report.json`
and `visual92a-extra-review/review.json` beside it. Mock feedback is not proof
of physical actuation. Alarm is read-only and Calendar shows one event, not a
complete agenda. Existing Player, Camera, Gallery, Voice and notifications are
outside this panel change. The editor caption correction was deployed separately
and verified in the browser. The current resume checkpoint tracks a subsequently
detected wake-word startup fault in92a and the92b reservation fix; the panel batch
does not imply that overall runtime qualification has passed.

## Ownership and lifecycle

`ExtraPanelPolicy` extends the existing entity-control owner and Panel kind7.
It does not create a second connection, selection, service task, authorization
queue or timer. The current selection retains one bounded domain/observation;
existing state events and renewal update it. Close, rebind and disconnect retire
the same owner. No pixels, framebuffers or new device workers are introduced by
this HA patch. Native storage must use the approved shared-family storage before
these variants are integrated; the HA DOM budget is not a native stack proof.

Saved actions are explicit:

```json
{"kind":"control","control":"panel","property":"info"}
{"kind":"control","control":"panel","property":"lock"}
```

Info accepts sensor/binary_sensor/calendar/alarm_control_panel entities, on
sensor or entity cards. Lock accepts only lock entities and entity cards.
No existing none/default/service action silently changes meaning. Projection
disables the launcher until its exact profile is negotiated. Passive Info opens
and renews with HA `POLICY_READ`; the default read callback denies. Lock and all
existing control families continue to use `POLICY_CONTROL`. Every command in an
Info selection is rejected, even with an old Lock operation/token. The existing
principal, epoch/runtime, channel, slot/card/revision, authorization-await and
single service-fence checks remain in force.

## Independent optional negotiation

The exact old Panel-v1 list timer/remote/power and the separate Detail90 feature
envelopes remain unchanged. Optional actions `entity_panel_extra_query` and
`entity_panel_extra_bind` each take one string `payload` and return a response.
After the generic kind7 channel bind, HA offers:

```json
{"v":1,"type":"entity_panel_extra_v1","channel":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","profiles":[{"name":"info","version":1},{"name":"lock","version":1}]}
```

Query returns the same exact keys with a supported subset. Bind sends a
nonempty subset and returns the same keys plus `accepted:true`, echoing that
exact subset. A negative bind has `accepted:false,profiles:[]`. All replies
must match the current channel and still-current connection. Failed/missing
optional negotiation disables only these profiles. The native query is
read-only and bind is atomic and idle-only; a rejected bind must preserve any
previous valid binding. No last-query cache is required natively: native checks
its configured versions, and HA separately checks the returned offer subset.

Profile lists are sorted, unique, at most8 entries; names match
`[a-z][a-z0-9_]{0,23}`, versions are strict integers1..255. Query permits an
empty offer, bind does not. Unknown/version-mismatched offers are omitted by
native query and rejected by bind. Malformed/stale native query returns an
empty offer; channel echo must be either validated32hex or empty. Closed keys,
types, duplicates and the512-byte UTF8 limit remain strict. The maximum query
is496 bytes and maximum successful bind reply is exactly512 bytes, excluding
NUL. A C string buffer would require513 bytes; an existing JsonObject response
avoids a new local buffer. Do not add fields to this envelope.

## Closed state variants and text policy

The grant/state envelope remains the existing kind7 identity, state_seq,
ttl_ms, title, panel_type, panel_caps, panel_state, available, eligible_actions
and state_generation. Maximum payload2048 UTF8 bytes, existing arena5120.
`title` retains its existing160-byte metadata policy.

Info caps: `{"info_type":"sensor|binary_sensor|calendar|alarm","device_class":null}`.
The union spelling above documents alternatives, not a literal wire value.
Sensor/Binary may instead carry the real HA class token, ASCII<=32; unknown or
malformed classes map to null. Calendar/Alarm class is null. Caps changes revoke
the selection; they are not telemetry.

Every state contains `source:known|unknown|unavailable` and `updated_text`<=48
UTF8 bytes. The latter is actual HA last_updated converted into HA's configured
time zone, or empty when no valid timestamp/zone exists. It means **HA update**,
not physical measurement freshness. `available` is true iff source is known.
Missing entities use existing entity_unavailable retirement.

| Info type | Additional exact state fields |
| --- | --- |
| sensor | value_status; value_text<=96; unit_text<=24 |
| binary_sensor | text_status; state_text<=96; active:null/bool |
| alarm | text_status; state_text<=96; phase |
| calendar | event; active:null/bool; summary<=128; start_text<=40; end_text<=40; zone_text<=48; all_day:null/bool; location<=96; description<=64; truncated_fields integer0..7 |

All limits are UTF8 bytes after plain-text normalization. Sensor value_status
and Binary/Alarm text_status are exactly value/empty/invalid/too_long/unknown.
Only value permits nonempty text. Empty is a real empty source representation;
invalid, too_long and unknown carry an empty value/state text. No prefix or
truncation mask is used for sensor values, units or Binary/Alarm states. A
too-long unit makes the sensor representation unsupported/too_long too.
Numeric sensor representations with units/state_class must be finite; the
original full decimal representation is preserved, never rounded to fit.
Native must fit/wrap the complete result using configured glyphs, or show an
explicit presentation error. It must not silently DOT/CLIP a full value.

Binary active comes only from actual on/off. On an unrecognized known source,
active is null and text_status invalid. HA translations are reused without the
tile caption's truncation. The owned fixture's actual moisture class uses HA's
class translation, with Mokro/Sucho (Wet/Dry) as the local fallback, never an
invented door/contact state. A legitimate HA translation takes precedence.

Alarm phase is disarmed/armed_home/armed_away/armed_night/armed_vacation/
armed_custom_bypass/pending/arming/disarming/triggered/unknown. An unrecognized
known source has unknown phase and invalid text. It is a passive alarm view:
there are no arm/disarm/trigger/PIN operations.

Calendar event is present/none/invalid/unknown. Unknown/unavailable clears all
event text, active/all_day become null and the mask is0. Known none requires
off with no event fields; partial or malformed fields produce invalid, not
none. Present requires actual message/all_day/start_time/end_time plus a valid
HA zone. Core's already-local full wall timestamps are retained, never treated
as UTC; timed events retain both complete dates across a DST fold. All-day end
is exclusive in Core and is presented as an inclusive last date. Empty optional
location/description are permitted. Only summary/location/description can be
bounded excerpts ending in an ellipsis, with respective mask bits1/2/4 and a
visible excerpt indication. Dates, time zone and state are never excerpts.

## Lock only and truthful results

Lock caps are exactly `{"lock":true|false}` from actual registered lock.lock.
There is no supported_features bit required for basic locking. State adds only
phase locked/unlocked/locking/unlocking/open/opening/jammed/unknown. Lack of
lock capability still permits a passive view. Eligible bit1 is set only when
source is known, lock exists and phase is unlocked/open/jammed; otherwise0.

The only additional command is op lock plus expected_state_generation, inside
the existing closed command envelope. No target, code, PIN, toggle, unlock or
open field is accepted. Service dispatch remains exactly lock.lock with the
selected entity and actual HA Context, after existing validate_live_action.
Native captures the absolute intent at press and commits once at release.

Info generation changes only with source-knownness; ordinary observations
advance state_seq without cancelling a gesture. Lock generation additionally
tracks phase, including ABA; update-time-only changes do not affect intent.
Only an actual fresh locked observation after dispatch can yield state_matches.
A completed callback without that observation remains not_confirmed after the
existing deadline. It is not mechanical proof and never service_completed.
Already locked is observational, not a reason to fabricate successful action.

## Metadata for the editor

`device_profile.schema_panel_extra_profiles` is the two profile objects above;
`schema_panel_types` stays the original three families. Bridge status exposes
`panel_extra_profiles` only after the current channel's successful bind.
Catalogue entries add:

```text
extra_panel: {version:1, panel_type:"info"|"lock", caps:<exact descriptor>,
              fingerprint:<64hex>, state:<exact closed state>,
              available:<bool>, eligible_actions:<0|1>}
```

Fingerprint covers family/type/class/capability, not phase, values or update
time. Editor selection/review revalidates the current source metadata and
negotiated profile; a cached screenshot is not control authority. HA112 provides
explicit Info/Lock launcher choices and full observation details in the editor.
The separate device batch verifies the native views; browser preview is not a
substitute for that evidence.

## Wire/DOM evidence and limits

Generated fixtures use maximal identity/revision/sequence, maximal escaped
unique text values (avoiding ArduinoJson string deduplication shortcuts), and
the actual production allocator/pool settings. Host probes are x86 and x86_64,
not a RISC-V firmware/stack/hardware measurement.

| Variant | Wire bytes | Host32 arena /5120 | Host64 arena /5120 |
| --- | ---: | ---: | ---: |
| Sensor | 1281 | 2672 | 4384 |
| Binary | 1239 | 2624 | 4320 |
| Alarm | 1216 | 2600 | 4320 |
| Calendar | 1950 | 3216 | 5088 |
| Lock | 947 | 2296 | 3888 |
| Extra query | 496 | 1712 | 3024 |
| Extra bind success | 512 | 1712 | 3024 |

Calendar has only32 bytes of host64 arena margin. Do not grow the contract.
These probes demonstrate DOM parsing capacity, not acceptance by a future
native strict decoder or LVGL rendering. Native must consume the same generated
fixtures before integration and remeasure final stack/storage.

## Owned migration and validation boundary

`tools/extra_panel_migration.py` is an offline pure planner. It changes only
actions at slots2/3/11/12/13. Required proof is runtime entity/source plus
search/related to one loaded atmosfera_demo config_entry; a registry record,
when present, must agree. A familiar entity prefix alone is insufficient.
Calendar/Lock may legitimately lack registry entries. The optional moisture
title/icon correction is explicit and off by default.

Re-read ownership and the full current layout immediately before applying;
compare the full reviewed document and expected revision using the existing
layout CAS. HA assigns the successor revision. Preserve every other card,
hidden duplicate and page order. Rollback is allowed only when the whole current
layout still exactly equals the accepted successor; do not overwrite later user
changes. No migration, synthetic states or device service is executed by this
patch's tests/planner. The historical ownership snapshot is test evidence, not
permission to skip a fresh check.

Host tests cover closed codec/duplicates/limits, optional negotiation fallbacks,
read-vs-control authorization, no Info dispatch, Lock exact service/feedback,
ABA/reconnect/capability loss, and owned CAS/rollback. Hardware acceptance still
requires the complete native build, OTA, source/ownership-fenced demo scenarios,
original screenshots, safe close/reopen, UART and memory/FPS comparison. Real
locks and alarms are excluded from mutation tests.

## Optional Person/Sun context

The original Info1 contract remains unchanged. The separate optional
`info_context:1` profile requires Info1 and admits Person and Sun as two more
read-only Info types. Both profiles must be negotiated before those types may
enter the existing owner. An invalid extension-only bind preserves the prior
binding. Other Info types and Lock retain their current payloads and policies.

See the [Person/Sun contract](../development/person-sun-info-panels.md) for
bounded fields, exact numeric grammar, unavailable-state clearing, HA timezone
ownership and minute-level date presentation. This addition does not introduce
a command, poller, task or framebuffer. Explicit launchers are configured
separately; existing passive cards and the saved layout are not converted.
Host codec and adapter checks are independent of the subsequent full firmware,
device screenshots and performance acceptance.
