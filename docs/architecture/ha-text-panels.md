# Home Assistant public text editor

This is the optional `text:1` companion contract (profile bit 128). It uses
the existing Panel selection identity independently of Datetime, Info and
Action. The first product policy admits `input_text` helpers with `mode:text`,
absent or null `pattern`, exact integer bounds `0 <= min <= max <= 255` with
`max >= 1`, and printable ASCII plus precomposed Polish letters. Empty text is
valid when `min` is zero. Spaces, case and full Unicode codepoints are preserved;
there is no trim, normalization, coercion or truncation. Combining marks,
newlines, controls, unpaired surrogates and other alphabets are not editable in
this first scope. The generic native mechanism receives the repertoire as
product configuration rather than embedding Polish policy.

## Admission, privacy and wire

The HA domain qualifies mode, pattern and bounds before reading the value.
Password and unknown modes never send their values. Any non-null pattern,
including the empty regex, is outside this initial editor policy. Unsupported
current values also remain null on the panel wire; they cannot be replaced by
blind editing. The literal HA states `unknown` and `unavailable` are reserved
and cannot be saved as text. A missing service leaves a valid value read-only.
The `editable` attribute controls helper configuration, not value permission.

Each grant/state has `panel_type:"text"`, `panel_caps:{min,max,can_set}` and
`panel_state:{source,value,reason}`, plus the existing title, availability,
eligible actions, state sequence, TTL and semantic generation. Fields are closed
and typed; booleans are not integer bounds. Source codes are known=0, unknown=1,
unavailable=2 and unsupported=3. Reasons are none=0, password=1, mode=2,
pattern=3, bounds=4, length=5, encoding=6 and characters=7. Only known carries a
string, including a present empty string; every other source carries null.
Unknown/unavailable have valid numeric bounds and reason none. Unsupported
password/mode/pattern may have numeric or null bounds and cannot set; unsupported
bounds requires both bounds null and cannot set. Length/encoding/characters
require numeric bounds and may advertise the service, but eligible actions
remain zero. Availability means known; eligible action bit 0 means known and
can_set. These codes do not extend the existing generic ControlReason enum.

No raw pattern, hidden source, previous value or source timestamp is sent in
this extension. A public-to-password transition revokes the existing session;
the product must clear labels and the existing App6 compressed preview through
the normal application invalidation/retirement lifecycle before it can be shown
again. A cleared label alone is not sufficient to invalidate a cached preview.

## Ownership and Save

`text_panel_domain.py` owns HA qualification and exact service formatting.
`text_panel_control.py` adds a policy to the existing single CONTROL session,
authorization, lease and shared service fence. It observes semantic source
changes before coalescing. Full exact value, source or reason changes advance
the generation, including A-to-B-to-A. Mode, pattern, bounds and service changes
retire the session. Cosmetic name/icon metadata does not cancel a held draft.

The native owner uses three bounded 1021-byte external-memory buffers for source,
draft and RX staging. The parser finishes validation and releases its document
before the existing owner receive call can emit. The text sidecar is transient;
the generic snapshot and message do not own text strings or grow their existing
728/960-byte storage. Commit happens only after the ordinary identity, sequence,
lease and generation checks and before observer notification. There is no new
task, raw screen buffer or independent snapshot mechanism.

The one absolute command is the existing full selection identity and command
sequence plus `text_version:1`, `op:"set_value"`, exact `value`, and
`expected_state_generation`. Save validates the full draft on release and sends
one `input_text.set_value` with the original authorized user context. Cancel,
close, invalid input and unchanged input send no service call. The existing
results remain pending, HA accepted, state matches, already matched, not
confirmed and rejected (codes 0 through 5). Confirmation requires an observed
matching value in a newer semantic generation after dispatch; a successful
service callback is not enough. STATE precedes a terminal result. The shared
in-flight service fence survives closing the view; late callbacks cannot paint
a subsequent owner and no automatic retry is introduced.

Core 2026.11.0 has inherited text-state pattern validation, unlike the old
2026.7.1 implementation used in earlier project work. Length rejection can
return normally without changing state. A pattern failure may occur after an
internal assignment. The adapter therefore uses conservative admission and
authoritative observations rather than assuming callback success or rollback.

## Editor and boundaries

An explicit v3 entity card uses
`{"kind":"control","control":"panel","property":"text"}`. The HA editor offers
a reviewed conversion from a passive entity/sensor tile. Conversion removes
sensor-only formatting in the local layout draft and supports Undo. The user
still saves the layout separately; no stored layout changes automatically.
The preview is read-only, uses inline vector icons, hides stale values and
checks live privacy attributes before consulting cached catalogue metadata.
An older native peer without Text1 keeps this launcher disabled.

Wire JSON remains at most 2048 UTF-8 bytes. Values have at most 255 codepoints
and 1020 UTF-8 bytes. First-scope escaped ASCII/Polish content uses at most 510
bytes; the generic upper bound leaves room for 255 four-byte scalars. The native
5120-byte parser arena and actual build memory remain separately measured gates.
The fixture corpus in `tools/tests/fixtures/text_panel/` comes from the HA
adapter and is shared with native tests. Host tests cover exact values, privacy,
generation/ABA, permissions, service fences and explicit editor conversion.
Compilation, upload, screenshots, touch behavior, memory and audio evidence
must be recorded for the actual installed firmware/package before claiming
hardware acceptance.

Home Assistant source references: [InputText entity](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/components/input_text/entity.py),
[TextEntity](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/components/text/entity.py),
and [InputText services](https://github.com/home-assistant/core/blob/2026.11.0/homeassistant/components/input_text/services.py).
