# Explicit climate program/preset choice

Accepted W07 slice (native40 / HA53 /137): v3 Climate Entity action
`{"kind":"control","control":"choice","property":"preset_mode"}`. HA owns
PRESET_MODE16, the exact bounded preset_modes catalogue, preset_mode and the
registered set_preset_mode service. Do not route this to HVAC mode or temperature.
Programs may change device policy; only the explicitly selected preset service
is sent. Default Climate, target, HVAC, fan and swing controls retain meanings.

An available standard HVAC state with an explicitly present None is known empty.
Core's standard PRESET_NONE string `none` is a normal index when included in the
catalogue; when absent from it, it denotes known inactive. Missing/malformed or
other off-list values remain unknown. Empty selection requires the existing
channel-bound empty-choice version1. It starts without a synthetic option or
candidate and needs a real selection before Apply. This reuses the already
accepted native40 nullable-choice protocol and widgets, with no native change.

Native labels prefer HA's cached entity-specific/generic preset_mode attribute
translations in the device locale, using the actual Core translation key paths.
Short PL/EN standard-preset fallbacks complement exact custom provider names.
Oversized/duplicate/invalid translated labels fall back to distinct bounded
project labels or the original exact names; labels never supply service values.
Captured canonical list/labels, state generation, authorization and one service
fence remain authoritative. Changes/rebind/outage cannot revive a held Apply.

Validate None/none/list membership, missing/off-list/outage, exact custom names,
metadata/state ABA, negotiated/default codecs, translations, service/context and
editor review/history. Then run a real owned MQTT climate and capture command
before provider feedback, no implicit HVAC/target service, negative cases,
PL/EN originals/browser, cleanup and matched performance.

Installed MQTT2026.7.1 automatically inserts `none` into its preset catalogue
and initializes it as a real option. Its ordinary real integration test therefore
uses that option; do not fake a nullable climate state to claim a provider case.
Explicit None/inactive-without-none climate variants need separate evidence:
host policy plus the generic nullable native contract are distinct claims.
Physical HVAC remains separate. No new native framebuffer/task/timer/codec.

Primary installed sources: climate/const.py SHA
19b5136ba111bef0eaa4f7e7016307e89ef7af5258098e9701e8536fe79483cc
defines PRESET_NONE=`none`; helpers/translation.py SHA
77c3d0e29aef99b86d8c597c2c59cf6505d9f6cef310ed2810a4877eaeffb02b
defines the attribute translation paths. MQTT source pin remains in the
[temperature design](climate-temperature-design-2026-10-31.md).

Acceptance: ha53-preset-scoped-acceptance.json in D:\aeh-build\feature-continuation-20261031. 580Python (3skip)/295Node/35source hashes; four real MQTT commands before feedback, zero separate HVAC/target commands, 16 reviewed originals, real browser review/Confirm/twoUndo/noSave, exact inverse137, all preferences restored and faults empty. Post test 79frames/53sourceFPS/avg16348us/max24440us/failed0; no new native task or buffer. Physical HVAC remains unverified.
