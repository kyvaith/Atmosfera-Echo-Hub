# Home Assistant Text panel

The existing App6 entity-control view offers an opt-in `text:1` profile for
`input_text`. Home tiles remain launchers. The Home Assistant adapter owns
eligibility, source privacy, bounds and the one `input_text.set_value` service
call. The generic ESPHome owner owns the authoritative source, local draft,
codepoint cursor, release fences and pending command identity. Product YAML
owns the 800×800 composition, labels, keyboard repertoire and key maps.

The first product repertoire is printable ASCII plus the eighteen precomposed
Polish letters. This is not unrestricted Unicode editing. Password mode,
non-null patterns, malformed limits, controls, unsupported characters and
unavailable values are read only; withheld source text never crosses the wire.
Length limits count Unicode codepoints, not bytes or grapheme clusters. The
adapter policy follows the installed Home Assistant Core version, rather than
reinterpreting Python patterns on the device.

The overview has six static lines and explicit up/down controls to inspect the
complete value. Edit uses three lines, a stationary caret and three native
button matrices. Shift selects case, `123` cycles two symbol pages, and `ąć`
selects a one-shot Polish row. Tapping the text moves the codepoint cursor;
left/right move one codepoint and up/down preserve the horizontal position.
Backspace removes one complete codepoint. Spaces are retained exactly. There
is no trim, normalization, hidden truncation or automatic save.

Only a valid, changed draft enables Save. Cancel restores the observed source
and stays in the overview. A semantic source change cancels held input and the
draft; a metadata-only update preserves them. Each key is captured on press and
applied on release, with selection, source generation, revision, pointer and
map-generation fences. Sliding between matrix keys cancels that press. The
existing bottom-edge gesture closes App6.

The owner sidecar is 3108 bytes on ESP32-P4, including three fixed 1021-byte
source/draft/RX arrays. The UI sidecar is 1540 bytes: a 1027-byte visible pool and
256 16-bit line offsets, including alignment. Both allocate explicitly in
external RAM once during setup. If allocation fails, Text is not advertised;
other profiles remain available. The 40 LVGL objects, component metadata and
one setup-created single-application vector have separate costs. LVGL small
objects can use internal RAM; their real cost must be measured on the device.

The presenter has no worker, polling timer, cursor blink, animated scroll or
new full-screen buffer. An unchanged render signature retains label contents;
unchanged palettes and matrix control flags do not invalidate the display.
The keyboard has 26 pseudo-buttons in three objects; all six maps retain the
same row counts. Static labels and scalar maps live for the component lifetime.

On Text retirement, static label pointers are detached before the visible pool
is zeroed. The native owner clears all source/draft/RX buffers. Every Text close
and privacy revocation marks the existing App6 compressed preview for retirement,
because a closed panel has no HA subscription that could report later password
mode changes. A pending retirement blocks a new App6 selection. The existing
component loop retries a product callback through the navigation controller's
registered subset capture path, using the existing display-buffer preparation
and CAPTURE admission. Only App6 is refreshed; no all-application recapture,
new raw allocation or alternate snapshot mechanism is introduced. Success
clears the pending flag. Busy navigation or another active application defers
the refresh until the existing ownership guards permit it.

Host coverage uses actual public LVGL pointer events, geometry, styles and
button matrices, with explicit host font/allocation facades. Product source
font coverage checks all 113 admitted scalars, key labels and localized text.
The host font facade also rejects codepoints absent from the actual generated
319-glyph product subset. Its advances remain approximations, so generated
font dimensions and hardware screenshots are independent evidence. The
counter's full runtime string is asserted, including its middle-dot and en-dash
separators. Native99 exposed why checking a separately authored sample is not
enough: a double-encoded literal contained an unavailable U+00AC and disabled
Text readiness. The99a correction uses explicit UTF-8 bytes and its regression
test fails when linked with the original99 presenter.
Configuration, generated-input checks, full firmware build, device memory/FPS,
HA services and screenshots remain separate acceptance stages.
