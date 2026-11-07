# Resume: native117 / HA131 accepted with known boot limitation

Checkpoint, 7 November 2026. Native117 and HA131 were adopted locally with
backups and journals; no commit, push or shutdown was performed. Recheck live
identity before device/HA writes and keep one owner of COM/OTA operations.

## Current state

- Accepted canonical runtime: native117 and HA131. Fast-heap114 and Statistics115
  are adopted; preserve dirty work in both canonical repositories.
- Last closed live observation: native117 / HA0.4.0.dev131. The117 feature route
  and focused Stop route restored original slot13 Info at layout410/Home1,
  with both owned scripts idle.
  Separate current health, feature and Home/Settings routes have no observed
  DSI/hard faults; root reviewed 14 original images across those routes.
- Owned effect helper is `params116:false`, retained after the explicit verified
  device commands. Do not reset it or replay a command to manufacture an
  untouched baseline.
- Native116 was not accepted/adopted. Final native117 and HA131 are adopted.
- Native117 full build/link and one OTA completed. First-boot qualifier is FAILED;
  later passive health and bounded feature/motion scenarios passed their checks.
  The separate focused post-Stop check confirms active Run and terminal caption
  after a one-second settle. Root then adopted 25 firmware and 18 HA files.

The repositories are `C:/Users/kyvai/atmosfera-echo-hub` and
`C:/Users/kyvai/kyvaith-esphome`. Frozen116 sources are
`C:/aeh-build/native116-sources`; frozen117 is now
`C:/aeh-build/native117-sources`. Source117 manifestSHA is
`25414706542cf3d79f857b44d0096fab046a5dc4f80ac53079aeaec288bb9468`;
use `prepare117-c-receipt.json`. D: preparation failed on exFAT allocation
overhead before changing the junction or building. Root preserved its partial
tree/ZIP/receipt, then moved two closed diagnostics with verified bytes to D:.
Details: `actionparams117-ack-work/build117-recovery-note.md` and
`diagnostic-relocation.json`. No canonical data was deleted. Root-only OTA uses
`panel_flash117_c.py`; earlier flash helper variants are unused. Full117 compile
ran14:44:53–14:57:56 UTC: RAM312078 B unchanged from116,
firmware8723208 B (+704 B from116).
Final artifactSHA `b2bfa345dbcc871b32ed5b063ae0e686930a32a538e8a68321f462dbb8b5ca02`;
ELF `52c9234b6bf0911434a2c53ce8598dc0074caccaef5f7f418f75f7eec202f077`.
The first linked-check invocation used an incorrect output-directory argument;
its separate error is preserved. The corrected report at
`native117-linked-first/report.json` passed without changing firmware.

Native116 source manifest:
`C:/aeh-build/notification-cards-20261102/source-v116-build.json`
SHA `60446945f25f78711ef0bcdae005d8c1dbaea7ae5d43624c47c05127c392edce`.
Artifact `D:/aeh-build/native-context-v116/manifest.json`
SHA `f2d5a68dcf07e26c4e6e88afc6b2bf2b628976f2ae67c79f6146c926244a1722`.
ELF `bef83f0a404e8ed9500a81a0de0a6bc0834043323a6813c2e291d3fe89922bc4`.

## Preserve these outcomes

Native116 full build/link succeeded and one OTA completed. Its first-boot
`FAILED_NO_AUTOMATIC_RETRY / UNCLASSIFIED_SENDSPIN_BOOT_WINDOW` is still failed.
Later 20-second passive observations recorded 230399 PCM frames, amplifier/wake
ready and no DSI/hard faults; they do not establish acoustic or clean-boot proof.
Native115 already had known mixer/Sendspin recovery; no new worker attribution
for the generic116 pthread failure has been proven.

Native117 likewise uploaded once and its qualifier failed at
`UNCLASSIFIED_SENDSPIN_BOOT_WINDOW` despite recovery to running with retry1.
Keep `native117-firstboot/first-boot.json` failed. No additional OTA or
test-induced reboot was attempted; the firmware's own worker retry is separate.
The separate `current117-first/report.json` then recorded20 seconds, three
230399-frame/amp/wake-ready samples, zero DSI/hard faults and coherent Home
reviewed by root. Its weather is `partly-cloudy-night`, confirmed in boot UART;
previous115/116 comparison states used `partly-cloudy-day`. Memory differences
are not automatically a Params cost or gain, and no extra weather A/B was run.

The closed117 feature route verified required False, required True, default
False and one Stop; all four explicit commands matched their intended service
and native receipt. Original Info restored at408; helper remainsfalse. Eight
feature originals, three performance originals and one health original were
reviewed by root. The earlier post-Stop JPEG is consistent with the preceding neutral/HA-accepted frame
while owner diagnostics already report ready/idle/state_matches. Unchanged117
real-LVGL Stop/state/result and suspend/resume test passes active Run restoration;
no firmware fix was justified, and physical P4 final-frame latency remains
unmeasured. A separate focused check then sent exactly one default-False Run and
one Stop, captured after a one-second settle and restored Info at410/Home1. Root
reviewed both originals: active Run/terminal caption and coherent Home. No
DSI/hard faults or cleanup errors occurred. This closes the settled visual gate,
without claiming a stale frame impossible or measuring exact presentation latency.

Comparable bounded motion: Home median37.5 FPS and Settings54 FPS in115 and117,
zero compositor failures/DSI/hard faults,18 stable audio samples.117's worst Home
frame50.136 ms is below115's98.279 ms, but different weather/cache state prevents
an intrinsic performance-gain claim. See `interaction117-vs115-summary.json`.

HA131's single-restart deployment observer failed on an incorrect false-vs-null
expectation. Separate read-only reconciliation passed; no second restart was
needed. The actual editor exposed Params1 only after compatible116 connected.
Root reviewed the field/default hint then undid the local draft: zero Save and
zero script commands from the browser.

The native116 device feature route failed after one correctly dispatched Run(false):
the native owner refused its terminal receipt and remained pending. Do not rerun
that command blindly. Reconciliationv3 later performed one guarded restore to405
with zero services/retries. Earlier failed reconciliation reports remain intact.

The apparent erased Action header was a preview problem: original decoded ROIs
are identical. No display/DIRECT patch is needed from those images. A separate
immediate Home capture really lacked weather pixels (0 bright pixels in weather
ROI); UART shows capture before the weather worker starts. The later settled
same116 image has 27544 pixels in that ROI and no DSI/fault. This is not persistent
blanking evidence and does not close a transition-retention question.

## Adopted corrections and preserved evidence

1. ACK117: admit `service_dispatched` for the exact pending negotiated Params1
   Script Run; ordinary Action2 and Stop semantics unchanged. Delivery:
   `C:/aeh-build/blue-flash-20261107/actionparams117-ack-work/delivery-v1/manifest.json`
   SHA `a09cafbb09f40cfe1e21ed00b4ad95dae7987643a90d431630c973325b24ab81`.
2. Appearance117: neutral Run while UNSET/unready/pending, active only after final
   admission; Stop/ordinary Action unchanged. Delivery:
   `C:/aeh-build/blue-flash-20261107/actionparams117-visual-work/delivery-v1/manifest.json`
   SHA `da3278481d7f6988de191330099b390d281385fd94ff972e4829e29251eb4482`.

The combined scope is two runtime C++ files plus three tests. No new object,
buffer, task, timer, SDK change or display transport change. Focused negative
controls, owner/legacy/real-LVGL tests and both actual P4 units pass. These are
not hardware results. The separate full 117 build/link has now passed. Root-only prepare/flash/linked/route
helpers are in `C:/aeh-build/blue-flash-20261107/`; use the final merged manifest
and exact new artifact rather than substituting116 adoption helpers.

Root completed explicit canonical117/HA131 adoption of the exact final25/18
files. Preserve `canonical117-adoption/report.json`,
`ha131-native117-canonical-adoption/report.json` and
`native117-root-acceptance.json`. The bounded form, focused Stop, original
screenshots, Home/Settings route and guarded restore are closed; do not repeat
hardware tests merely to improve the report. Continue the next scoped feature
from this checkpoint, rechecking live identity first.
Camera/Gallery/Player/Assistant engines remain unchanged. No Git push without
the user's instruction. Detailed current evidence and known limitations are in
`acceptance-action-parameters-2026-11-07.md` beside this checkpoint.
