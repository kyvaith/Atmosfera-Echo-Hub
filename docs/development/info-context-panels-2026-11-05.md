# Person and Sun in the existing Info view

This product composition is an isolated candidate for native96/HA117. Its
configuration and source-font checks are separate from the eventual complete
firmware, display, memory and Home Assistant acceptance. Existing Player,
Camera, Gallery, Voice, notifications and all control panels are unchanged.

## Contract and ownership

The existing `info:1` and its four types remain unchanged. The optional
`info_context:1` extension admits Person5 and Sun6 only while both profiles
are bound. These are read-only Info/App6 selections; all commands are rejected.
No new endpoint, worker, task, timer or framebuffer is added. Existing state
subscription, lease renewal, close and retirement own the observation and view.
The upstream option defaults off; this product explicitly enables it.

The product owns18 static objects/references: Person6 and Sun12, including two
official Material Symbols SVGs. Native owns typed state, complete-fit rendering
and date formatting. The product supplies no runtime state machine or service
lambda. Existing Extra text IDs0–63 stay stable;64–92 add29 PL/EN keys. The
combined immutable i18n table now has1024 entries, derived from configuration.
Existing Roboto fonts are reused; there are no new font sizes or bitmap assets.

Person shows the whole admitted HA presence result. Home/Away are translated
by HA with a language-pack fallback; a named zone preserves its full case and
text. Only semantic `home` gets the accent surface. Unknown/unavailable clears
previous state emphasis. `Stan HA od` means HA last_changed, not proven physical
arrival time. Tracker arbitration, GPS, photos and maps remain Home Assistant's
responsibility; no such fields are transmitted in this extension. Existing
custom state-label eligibility is unchanged and does not include Person/Sun.

Sun shows the admitted above/below-horizon phase, next sunrise and sunset, then
elevation and azimuth. One invalid/missing attribute does not erase the others.
The device does not infer night, recalculate astronomy, draw an invented path,
or show a countdown. Exact numeric precision is retained; no clipped or unitless
value may masquerade as a complete reading. The280px value columns accommodate
the bounded24-byte numeric text and degree symbol in the existing20px font.

HA validates aware timestamps and compares future events in UTC at full source
precision before normalizing the wire to local seconds plus offset. Native
formats only these admitted fields, for example `6 listopada 2026 · 06:42`
with `UTC+01:00` on a separate line. The timezone name is separate. The same
friendly formatter is used for common `updated_text` only on the new two types;
the previous four Info types retain their presentation. UI precision is a minute,
not a claim of second-level measurement. DST folds remain distinguishable by
offset; full dates handle distant polar events and year boundaries. Unknown,
invalid, too-long and stale have natural language fallbacks, never raw enum text.

## Composition and validation boundary

Person uses a172px tonal circle and112px person vector, a large state area with
normal/compact font fallback, then HA state-change time and timezone. Sun uses
a96px vector, horizon phase, two calm date rows and two small angle columns.
There are no action buttons or decorative charts. Both keep the existing shared
title, update and status positions and close with the existing bottom gesture.
SVG foreground is set explicitly by its owner; inherited text color alone is
insufficient when an SVG object has a local theme style.

The product checks pin source fonts, all93 Extra text bindings, the18-object
geometry, month names/offsets/date lines and the native SVG parser. Config-only
true/false checks do not establish runtime behavior. Actual-P4 size/stack/DOM,
complete firmware, original screenshots, unknown/date cases, old Calendar/Lock
retirement, wake-word continuity and one matched performance route remain
separate gates. No canonical layout or person-state migration is automatic.

Icon sources are the official Google Material Symbols `person` and `sunny`:
https://github.com/google/material-design-icons/tree/master/symbols/web
Their relative/smooth paths are expanded to supported absolute paths without
changing geometry. The adjacent info-context-LICENSE.txt retains Apache-2.0.
