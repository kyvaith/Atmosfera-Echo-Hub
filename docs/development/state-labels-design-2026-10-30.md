# Per-card state descriptions — CTL-017

Status: HA35/native35 bounded device/original-image/browser/cleanup acceptance
passed. Restored layout83,16 cards/3 cameras/8 preferences,54FPS/failed0.
[Evidence and limits](validation-2026-10-30-continuation.md).

Information cards may store an optional `state_labels` dictionary: at most eight
exact raw states and literal display labels, each1–32 UTF-8 bytes. Printable
Unicode and normal spaces are allowed; control/format characters, blank fields,
duplicate rows and mappings for unknown/unavailable are rejected. No wildcard,
HTML interpretation, template evaluation or service data. Empty mappings are
removed by canonical validation. User descriptions are user content, like titles;
they are not automatically translated.

Only editable Sensor cards for sensor/binary_sensor/number/input_number/select/
input_select are eligible. Source states and metadata remain unchanged. Exact
matching happens before ordinary formatting; unmatched values keep HA formatting.
Missing/unknown/unavailable retain standard outage messages. Raw binary state
still determines automatic icons and active color. Mapping a numeric value
deliberately replaces its normal unit/precision display for that exact value.

HA owns validation, persistence and presentation text. Existing source
subscriptions and native changed-slot snapshots own updates; no new entity,
subscription, native field, task, timer or pixel buffer is added. Firmware still
receives only the final bounded subtitle.

The editor provides an eight-row M3 dialog. Changes remain in the review until
confirmation, then form one undoable draft edit. Confirmation fences device,
user, card, profile, saved revision and draft. Typed fields keep focus. Clear,
copy, move, import/export and recovery preserve the optional property; changing
to an incompatible type removes it in the same undoable operation.

Acceptance: host validation/formatter/preview/Undo/stale-review tests, actual
browser entry and edit, actual helper raw-state changes mapped on device,
unmapped/outage messages, passive taps, off-screen refresh, original screenshots,
cleanup and normal Settings FPS/memory. No firmware rebuild/OTA is implied by
this HA-only adapter; installed native35 identity must still be verified.
