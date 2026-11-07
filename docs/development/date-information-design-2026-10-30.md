# Calendar-date information cards

Status,31October: implemented as HA40 on native39. Strict formatting, real MQTT
source, PL/EN, malformed/outage states, passive taps, offscreen updates, exact
cleanup, screenshots and53-FPS post-feature route passed. The editor has273
host tests; live browser acceptance remains pending desktop confirmation.
See [the acceptance record](validation-2026-10-31.md). This closes only the
passive calendar-date slice of W10.

HA owns normalization of a sensor whose declared device_class is `date`.
This is a calendar date, distinct from a timezone-aware `timestamp`; the public
[HA sensor contract](https://contributors.home-assistant.io/core/entities/sensor/#device-classes)
defines those separately. This slice must not change timestamp, uptime, enum,
Scene/Button action timestamps, the main clock or any system timezone.

Accept exactly ASCII YYYY-MM-DD and validate Gregorian month/day/leap-year
bounds. Show DD.MM.YYYY in Polish and YYYY-MM-DD in English. Missing, malformed,
unknown and unavailable input stays explicit. Existing exact state-label
overrides retain priority. Card precision cannot turn a date into a number.

Use the existing HA formatter and passive sensor projection. The editor should
apply the same strict calendar rule in its current preview locale. No layout or
native protocol change, new font, task, timer, subscription or framebuffer is
needed; ten ASCII characters fit the existing bounded caption contract, with
actual pixel fit still requiring device review.

Host gates: leap years including1900/2000, valid years0001/9999, invalid dates,
Unicode digits, extra bytes/whitespace, mapping overrides and unaffected ordinary
numeric/text/action paths; PL/EN preview consistency. Device gate: an owned real
MQTT date sensor, native projection and original screenshots for valid/invalid
and unavailable states, passive taps without service dispatch, off-screen
updates, exact binding inverse and fixture cleanup. Preserve16cards,3cameras,
8preferences, normal Home completeness, warm memory and54-FPS baseline.
