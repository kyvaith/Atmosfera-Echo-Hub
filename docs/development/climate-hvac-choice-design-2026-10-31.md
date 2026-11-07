# Explicit climate HVAC mode choice

Next W07 slice: v3 Climate Entity action
`{"kind":"control","control":"choice","property":"hvac_mode"}`. HA owns the
complete current hvac_modes catalogue, the observed mode and set_hvac_mode.
Only the seven standard HVAC mode codes are admitted, with1..8 exact distinct
options; normalize HA's known string-enum values at this semantic boundary.
Unknown/off-list/outage never selects option0. No additional feature bit is
invented for the standard mode service. Temperature, preset, fan and swing
remain separate controls.

Native presentation reuses choice/app6 and indices. HA entity translations in
the device locale supply labels when available; bounded project PL/EN labels
cover missing/oversized/duplicate translations. Labels are never service values.
The captured immutable canonical domain resolves a chosen index after fresh
list/state/generation/layout/authorization checks. Exact domain/label changes
revoke a selection, including metadata/state ABA and locale changes.

Editor admission is explicit and reviewed, draft-only and undoable. Existing
default Climate tap and single-temperature Number action retain their meanings.
No new native task, timer, subscription, framebuffer, codec or firmware is added.
Run schema/enum/translation/owner/dispatch/regression tests. Then use an owned
real MQTT climate: choose/cancel/no-op/Apply, actual mode command before provider
feedback, zero target-temperature commands, list/availability/ABA/locale cases,
PL/EN originals, actual browser review/Undo, exact cleanup and matched performance.
Physical HVAC and whole-product audio/cold-start acceptance remain separate.

Primary contract: [HA Climate entity](https://contributors.home-assistant.io/core/entities/climate/),
checked31 October2026; installed Core/MQTT source pins are recorded in the
[temperature design](climate-temperature-design-2026-10-31.md).

HA51/native40 scoped acceptance:570Python(3skipped)/292Node,35 installed/pinned
files; four real heat/auto/cool/off mode commands observed before provider
feedback, zero target-temperature commands. Candidate/cancel/no-op, held mode
ABA, reordered/reduced catalogues, outage/recovery and PL/EN passed. Fifteen
device originals and browser review/Confirm/twoUndo/noSave were inspected;
cleanup135 preserved16cards/3cameras/eight preferences. Normal route80frames/
54sourceFPS/avg16266us/max24959us/failed0; PSRAM4810KiB/largest2688/internal21/
JPEG927; app_work/scroll/close0. Receipt `ha51-hvac-scoped-acceptance.json`.

That campaign separately exposed an editor accent startup-mirror issue, with
actual native AEE2FF but HA preview36BCF0. HA52 closes it without changing the
HVAC dispatcher: typed fresh Core cache seeds only the connection-scoped preview.
Actual device/API/browser now agree on AEE2FF after restart, with no preference
or option writes;54sourceFPS/failed0 again. Receipt `ha52-accent-scoped-acceptance.json`.
Physical HVAC and long audio/cold-start acceptance remain separate.
