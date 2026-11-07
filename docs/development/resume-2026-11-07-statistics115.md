# Historical checkpoint: Statistics115 and Params116 correction

**Superseded by [native117 / HA131](resume-2026-11-07-actionparams117.md).**
The117 build, OTA, bounded feature/motion checks, original-image review and
guarded canonical adoption are complete. The focused settled Stop image passed;
original Info slot13 is restored at layout410/Home1. Firstboot117 remains failed
with later recovered health recorded separately. The paragraphs below preserve
earlier in-progress states and must not be used as the current live identity.

## Active correction checkpoint, 2026-11-07

Latest update: the original Info slot has been restored as layout405 by
`actionparams116-reconciliation-v3/report.json`, with the owned script result
still `params116:false`. A separate passive health check at layout405 passed;
weather is visible after settling. The immediate restoration capture preceded
weather rendering and was blank in that region; retain both originals.

Native117 configuration passed at14:44 UTC and full build is running using
`prepare117.py --receipt prepare117-c-receipt.json`. Source manifest SHA
`25414706542cf3d79f857b44d0096fab046a5dc4f80ac53079aeaec288bb9468`, frozen
source `C:/aeh-build/native117-sources`; the build-only junction now targets it.
No OTA117 has occurred. Live device remains116/HA131/layout405, Home1.
The earlier D: preparation exhausted exFAT due to262144-byte clusters before
compilation or junction change. Its failed receipt and partial copy are
preserved under `C:/aeh-build/blue-flash-20261107/failed117-exfat-stage` (ZIP
and complete moved tree). Two closed diagnostic files were moved intact to
`D:/aeh-build/closed-diagnostics-20261107`; see `diagnostic-relocation.json`.
No project source or earlier result was deleted.

The older state below is historical. Native116 was fully built and flashed
once. Source SHA `60446945f25f78711ef0bcdae005d8c1dbaea7ae5d43624c47c05127c392edce`,
artifact SHA `f2d5a68dcf07e26c4e6e88afc6b2bf2b628976f2ae67c79f6146c926244a1722`,
ELF `bef83f0a404e8ed9500a81a0de0a6bc0834043323a6813c2e291d3fe89922bc4`.
The firstboot remains FAILED/UNCLASSIFIED_SENDSPIN_BOOT_WINDOW. Separate
`current116-first/report.json` observed 20 healthy seconds, all230399 digital
startup audio frames, amplifier/wake ready and coherent original Home JPEG;
this does not reclassify firstboot or establish acoustic output.

`actionparams116-device-first/report.json` failed on a missing terminal Run
receipt. It proves exactly one owned test script Run(false), matching HA
service and helper write `params116:false`. Do not blindly repeat Run.
Last owned state: layout404, slot13 required script, App6 open_seq2. The
original Pomiar card is retained in that report; root is preparing explicit
reconciliation and safe restoration. No observer remains open.

The native owner omitted parameterized script Run from its service-dispatched
receipt condition. A minimal isolated fix is in progress. Canonical runtime
has not adopted116 or HA131; canonical firmware115 and HA130 remain preserved.
An apparent missing header in the image-tool preview was disproven by exact
decoded-pixel ROI comparison; do not patch the display based on that preview.
Both bounded116 observations had zero DSI events and hard faults.

The HA browser draft was undone, with Save disabled, before the device test.
There is no unsaved browser layout draft. Build junction targets native116.
Read `C:/aeh-build/blue-flash-20261107/native116-root-review-1.json` and the newest
closed reports before resuming. No Git commit/push or shutdown is authorized.

## Historical adopted115 checkpoint

Updated 2026-11-07 after local adoption; work remains active at the user's request.
No shutdown, Git commit or push is authorized by this continuation.

## Current live state

- Device192.168.88.82, MAC30:ED:A0:E2:0B:CD, USB COM5; firmware115.
- ELF `a446ef88ab7bb9c99a46ae2da8efcb5dfff67d8b94441ab58d13ca3e51e1f161`.
- Source manifest `C:/aeh-build/notification-cards-20261102/source-v115-build.json`,
  SHA `d28c16063906318e9407797fc5b7e445ce3a4639951a342705d6ddb999868eb4`.
- Artifact `D:/aeh-build/native-context-v115/manifest.json`, SHA
  `b0326304af6b93ab441090b4d51b761df3f8cf37a09796db4909a2fb6862ba3d`.
- HA192.168.88.3:8123, Core2026.11.0, integration0.4.0.dev131.
- Entry `01KZ0TZYXS9GFHT06TXQYQKET7`, provider `01M6K8SV0H7XHJMHW4SD6XACTQ`.
- Layout403, order12345; slot13 is the exact original Info card again.
- Final device view Home1 with actual partly-cloudy-day weather. No serial
  observer remains running. Always recheck live identity before new writes.

Canonical repositories: `C:/Users/kyvai/atmosfera-echo-hub` and
`C:/Users/kyvai/kyvaith-esphome`. They contain substantial pre-existing dirty work.
Firmware115's24 files and HA129's19 sources/tests/fixtures were adopted with
preimage checks and byte backups. Do not reset, clean, stage or rewrite them.
HA130 then changed only the manifest and editor asset version. Its first
post-restart observer failed on a missing readiness key during startup;
`ha130-deployment-first/report.json` remains FAILED. Separate read-only
reconciliation passed: version130, exact versioned editor URL and served JS
hash, native115/layout403 and all protected source/config preimages. No second
restart occurred. The two files were adopted with backups in
`ha130-canonical-adoption/report.json`.
The build component junction still targets the frozen115 source tree; changing
canonical source alone does not change that build.

## Completed, with separate evidence boundaries

1. Blue-flash investigation identified long largest-free-block scans delaying
   the display. The minimal114 fast-query policy is adopted; the paired113
   comparison reduced observed DSI underruns9→0. Display ownership/buffers are
   unchanged. Read [the display report](blue-flash-2026-11-07.md).
2. Statistics115/HA129: explicit read-only24-hour sensor view, actual Recorder
   data, vector graph, CPU and temperature routes, device JPEGs and browser
   review/draft/Undo. Read [the acceptance record](statistics-2026-11-07.md) and
   [architecture](../architecture/ha-sensor-statistics.md).
3. Same-firmware weather comparison explains825676 B PSRAM and13672 B internal
   difference from the old night-weather reference. Home median37.5 FPS and
   Settings54 FPS are unchanged; individual larger peaks remain recorded.

Evidence root: `C:/aeh-build/blue-flash-20261107`.
Final aggregate `display-audit/native115-evidence-closed.json`, SHA
`f26a83533fc3f35533ae2897a5a88d6b6fc18557b385cb456fb9c775c013a67d`.
Final health `weather115-final-health-first/report.json` and original Home JPEG
were reviewed. Complete230399 startup PCM frames, amplifier/wake ready,
unchanged logging preferences and zero DSI/hard faults were observed.

Do not turn these into claims of physical60-FPS, acoustic listening, physical
gesture acceptance, long-term stability or a strict clean boot. Firmware115
used the known mixer/Sendspin resource recovery. Historical Guru107, abort110a,
failed113 classification,114 restart3 observation gap and the weather-helper
transitional-view assertion remain preserved. The latter's separate final
health passed; its original failed receipt was not changed.

## Active next batch

- Offline work is preparing friendly Action last-used labels and shorter Camera
  launcher subtitles. Preserve complete ISO precision/offset on the wire,
  authoritative state and generation fences. Reuse existing month translations,
  existing labels and the Camera engine; no separate cosmetic OTA.
- The reviewed `C:/aeh-build/blue-flash-20261107/script-params116-contract.md`
  permits exactly one required Boolean script field, optional exact Boolean
  default, three existing controls, explicit new card and independent binding.
  Optional/multiple fields remain unsupported. HA backend, native owner and
  editor implementation are proceeding in isolated agent workspaces; nothing
  from this feature is deployed or adopted at this checkpoint.
- HA131 package and editor are frozen for review. Root created only the owned
  `input_text.atmosfera_params116_result` helper, initial `params116:untouched`.
  Two inert script fixtures were accepted by the installed Core schema and
  appended to `/config/scripts.yaml` with an exact preimage, byte backup and
  atomic replacement. One HA131 restart loaded them; neither has been called.
  Existing script bytes and other helpers are unchanged.
  See `actionparams116-helper-create-first/report.json` and
  `actionparams116-scripts-stage-first/report.json` under the evidence root.
  The latter contains the remote backup location. Do not repeat staging.
- HA131 source, served editor, both script metadata records, helper, layout403
  and native115 identity passed separate read-only reconciliation in
  `ha131-reconciliation-first/report.json` (SHA
  `36d8a00fa73f16f12034044057a0c1f36d98ea31591dfd71c655bc853f3dc3c5`).
  Original `ha131-deployment-first/report.json` stays FAILED: its observer
  expected false instead of null for script-inapplicable automation policies.
  There was no second restart. The executed observer is preserved exactly as
  `deploy_ha131.executed12a034.py`; the corrected observer is a separate hash.
  HA131 sources are not yet adopted into canonical.
- Native116 full build is active from frozen source manifest SHA
  `60446945f25f78711ef0bcdae005d8c1dbaea7ae5d43624c47c05127c392edce`.
  Build-only junction now targets native116. No OTA116 has occurred yet.
  IAB has a root-created **unsaved** slot13 script draft for readiness testing;
  undo it before device layout acceptance. Live layout remains403.
- Test exclusively with a narrowly owned real Core demonstration script and
  helper; never infer permission to run an arbitrary household script.
  Continue full native build/OTA/relevant device screenshots for runtime
  changes, batching compatible changes rather than repeating full tests blindly.

Runtime credentials are supplied only through ephemeral environment variables
to the existing authentication helper; do not store or print them in this file.
Root alone owns live HA/device/COM/OTA actions; delegate offline work freely.
