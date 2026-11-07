# Person and Sun information panels

These two panels extend the existing read-only Info family. The saved action is
`{kind: control, control: panel, property: info}`. An editable `sensor` or
`entity` card may explicitly launch the panel; existing passive cards keep
their placement rules. No layout is converted automatically.

`info_context:1` requires `info:1` in the independent Extra negotiation. An
offer or bind with the extension alone is invalid and must preserve the
previous binding. Both capabilities are required for Person/Sun grants and
states. Other Info types, Lock, Media and Action retain their existing wire
contracts. The native feature defaults to disabled upstream.

HA owns presence interpretation, translations, timezone conversion and source
validation. Person exposes home, away, or the complete custom zone name and
its last state change. Sun exposes the authoritative horizon phase, next rise
and set, elevation and azimuth. The Sun runtime entity is valid even without
an entity-registry entry. Neither panel sends commands. Read authorization,
selection identity, lease renewal and subscription lifetimes reuse the
existing Info owner; no new polling task is added.

Unknown and unavailable observations clear domain values while retaining the
current HA observation timestamp. Missing, invalid, oversized and stale fields
are explicit, never plausible zeroes or silently truncated values. A future
Sun instant is compared at full source precision before normalization. Dates
on the wire use local time with a validated numeric UTC offset and seconds;
the UI shows localized day/month/year and minutes, with offset and timezone
separate. Presence `last_changed` is not substituted with `last_updated`.

Angles retain their exact bounded decimal string (24 UTF-8 bytes). The grammar
is `[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?`, with exact
ranges −90..90 and 0..360. The renderer may localize a decimal separator for
display, but may not round the source into a fabricated observation. The
protocol contains no location coordinates, pictures, tracker IDs or HA tokens.

The native view uses the existing bounded Extra variant and App6 lifecycle.
No image buffer, framebuffer owner, service fence or media lifecycle is added.
Host contract checks live in `tools/tests/test_info_context.py`, alongside
portable frozen wire and actual adapter metadata fixtures. These checks do
not establish device performance or physical UI correctness; compilation,
OTA, original screenshots and device measurements remain separate evidence.
