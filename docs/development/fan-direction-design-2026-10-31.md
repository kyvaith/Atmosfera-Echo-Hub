# Explicit fan direction choice

Next W06 slice: an explicit v3 fan action
`{"kind":"control","control":"choice","property":"direction"}`. Existing fan
choice without the property remains preset selection. The trusted HA profile
advertises the new semantic facet; no new native codec or control kind is needed.

HA owns two canonical values, forward/reverse, the DIRECTION4 capability and
the registered fan.set_direction service. Require a live on/off fan and a known
exact direction. Missing/None/malformed/outage never become forward or manual.
Native labels are localized Do przodu/Wstecz or Forward/Reverse, while service
values remain canonical. An index is resolved only against the captured immutable
domain, after current state, generation, layout, authorization and service fences.
Language changes invalidate an in-flight selection instead of reusing old labels.

Reuse the single choice owner, app6, bounded widgets, existing task/renewal and
application buffer. No native source, full-screen allocation, subscription or
polling task is added. Editor review is explicit, draft-only and undoable. Preview
cannot send a direction or power command. Speed, presets and oscillation retain
their independent behavior.

Validate schema, metadata, real dispatch/canonical values, direction ABA,
capability/service/language loss, authorization, stale index and deduplication.
Then install the pinned HA package and exercise an owned real MQTT fan on native40:
candidate/cancel/no-op/Apply, actual broker command before provider feedback,
matching state/result, PL/EN originals, actual editor review/Undo, exact inverse
cleanup and matched Home/Settings performance. Physical motor motion is separate.

Primary contract: [HA fan entity](https://contributors.home-assistant.io/core/entities/fan/),
checked31 October2026; confirm MQTT commands against installed Core2026.7.1.

Accepted HA47/native40:555Python(3skipped)/286Node, focused static checks and
34 installed/source hashes. Real MQTT reverse command observed before provider
feedback, exactly one fan.set_direction and zero power commands; candidate,
cancel/no-op, held direction ABA, outage/capability loss, PL/EN, ten original
captures and actual browser review/Confirm/twoUndo/noSave passed. Exact cleanup131
preserved16cards/3cameras/eight preferences. Normal route81frames/54sourceFPS/
avg15998us/max23975us/failed0; PSRAM4828KiB/largest3200KiB/internal22KiB,
JPEG913KiB, app_work/scroll/close0. Receipt `ha47-direction-scoped-acceptance.json`
in the 31 October evidence directory. No native rebuild was needed; native40's
full ELF was reverified. No physical motor movement or long audio acceptance.
