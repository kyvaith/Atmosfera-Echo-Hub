# Home Assistant date and time editor

This is the optional `datetime:1` companion contract. Source and host tests are
separate from full firmware, upload, touch, audio and screenshot acceptance.
The profile is independent from Info1, Info Context1 and Action2. Existing
profiles and passive date/time tiles keep their current behavior.

An explicit v3 entity card uses
`{"kind":"control","control":"panel","property":"datetime"}`. Converting a
passive sensor card requires an editor review; the conversion removes
sensor-only formatting. No saved layout is converted automatically.

## Ownership and values

The existing single entity-control session, App6 lifecycle, authorization and
service fence own this editor. `datetime_panel_domain.py` owns exact HA value
admission and service formatting; `datetime_panel_control.py` supplies the
typed policy. The existing state subscription observes every semantic event
before snapshot coalescing. No polling task or additional frame buffer is
introduced by the HA integration.

The three modes are date, time, and combined date/time. A value is exactly six
nullable integer fields: year, month, day, hour, minute and second. Absent
components are null, never inferred. Years 1 through 9999 use Gregorian
validation. Seconds remain visible and are preserved. Unknown/unavailable
observations clear all six values; a missing service exposes a read-only view.

HA source admission checks both the raw state and component attributes. Padded
and platform-unpadded source years describe the same year. Outbound years are
always explicitly padded to four digits. Booleans, floats, coerced strings,
leap seconds, invalid dates and mismatched attributes are not accepted as
integer values. There is no silent date clamping or rollover.

These are calendar and wall-clock values, not UTC instants. The combined mode
may display the HA timezone as context; date-only and time-only have no zone.
The editor does not invent a DST fold selector or change a wall value into an
instant. The separately normalized `updated_text` is the current HA observation
timestamp, not a timestamp derived from the helper value.

## Local edit and one Save

The native owner keeps one bounded local draft and one active numeric field.
The numeric accept key only changes the draft. Save validates the complete
effective tuple, including valid active digits, and emits one absolute command
on release. It does not require a separate numeric accept first. Invalid input
remains visible; Cancel, close, or a semantic source change discard the draft.

Mode/service capability changes retire the session. Source/tuple changes
increment the semantic generation, including A-to-B-to-A events before the next
snapshot. Title, timezone, observation timestamp and lease renewal are metadata
and do not cancel a held draft. The wire remains bounded to 2048 bytes.

The command has the existing full selection identity, command sequence and
expected state generation, plus `datetime_version:1`, `op:"set_datetime"` and
the six-field target. Its null mask must match the admitted mode. The HA policy
checks CONTROL permission and the shared service fence before sending one
`input_datetime.set_datetime` call with `date`, `time`, or both. It sends no
timestamp, arbitrary service data or user-supplied timezone.

An equal pre-dispatch target returns `already_matched` without a service call.
After dispatch, success requires a newer semantic generation and the complete
observed target tuple. A service callback alone is not confirmation. The current
STATE precedes the terminal result; results use the existing 0–5 statuses,
never Action's completion/dispatched extensions. Retired callbacks cannot reopen
or paint a later view.

Host coverage is in `tools/tests/test_datetime_panels.py`; shared examples and
backend-generated catalogue observations are under
`tools/tests/fixtures/datetime_panel/`. Hardware evidence is recorded separately
for the actual firmware and HA package installed for acceptance.
