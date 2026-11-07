# ActionParams1 acceptance — 7 November 2026

Native117/HA131 is accepted and adopted for the bounded feature, screenshot and
motion scope described here, with the known first-boot limitation retained.
Root adopted exactly 25 firmware and 18 HA source/test files with backups and
journals. The last closed live state is original slot13 Info at410/Home1.
Native116 feature acceptance remains rejected.

The form supports exactly one required Boolean script field. Existing Action2
cards and Stop retain their prior behavior. The owned test scripts affect only
`input_text.atmosfera_params116_result`; household actions are not test targets.

## Evidence and known limits

| Scope | Observed result |
| --- | --- |
| HA131 backend/editor focused tests | 325 Python tests, 214 subtests and 545 editor tests passed in the frozen HA delivery. |
| Native116 host/codegen and actual P4 units | Passed; component +32 B, snapshot/message/parser arena unchanged, feature-off sizes unchanged. |
| Native116 full build and linked guard | Passed; 312,078 B static RAM, 8,722,504 B firmware. A generated-comment observer-count failure was preserved and corrected without changing firmware source. |
| HA131 deployment | One planned restart. Original observer FAIL retained (expected false instead of inapplicable null); separate read-only reconciliation passed. |
| Native116 OTA and first boot | One upload succeeded. `FAILED_NO_AUTOMATIC_RETRY / UNCLASSIFIED_SENDSPIN_BOOT_WINDOW` remains failed; no second OTA was attempted. |
| Separate native116 current health | Two separate 20-second passive observations showed 230399 PCM frames, amplifier and wake readiness, no observed DSI/hard faults, and coherent settled Home originals reviewed by root. Digital counters are not acoustic proof or a clean-boot claim. |
| Actual HA editor | Form absent with native115; appeared after 116 without reload/reselection. Root reviewed required field/missing-default hint and used two Undo operations. Original Info card restored in the draft, Save disabled; zero layout saves/script commands. |
| Native116 feature route | UNSET blocked Run; choice, held-press cancel and close/reopen produced no services. Exactly one explicit False Run caused one matching service and helper write. Native terminal ACK stayed pending, so the route stopped and remains FAILED. |
| Native117 ACK correction | Actual 116 negative control reproduced rejected `service_dispatched`; focused owner/codec enabled/disabled/legacy tests passed after the narrow correction. |
| Native117 disabled appearance | Actual LVGL RGB888/DIRECT host test reproduced the unclear 116 palette; 27 scenarios passed after correction, including neutral/active/pending Run, stable header pixels and zero extra flushes over five unchanged refreshes. |
| Native117 P4 units | Both changed runtime translation units compiled. This is not a complete firmware build or device test. |
| Native117 full build/link | Passed;312,078 B static RAM (unchanged from116),8,723,208 B firmware (+704 B). Full compilation ran14:44:53–14:57:56 UTC. Final linked guard verified exact117 source/ELF. |
| Native117 OTA and first boot | One upload succeeded. The qualifier remains `FAILED_NO_AUTOMATIC_RETRY / UNCLASSIFIED_SENDSPIN_BOOT_WINDOW`; recovered retry1 does not constitute a clean boot. |
| Separate native117 current health | Closed20-second passive observation, three stable230399-frame audio samples, amplifier/wake ready, zero observed DSI/hard faults. Root reviewed original Home clock/weather. No restart or second OTA. |
| Native117 feature route | Three explicit Run commands (required false, required true, default false) each produced one guarded direct service and terminal result7. One Stop used the ordinary service without parameter fields and reached state_matches/result2. No DSI/hard faults or cleanup errors. |
| Native117 original images | Root reviewed 14 originals: 8 feature, 3 Home/Settings, 1 passive-health and 2 focused Stop/restore images. UNSET Run is neutral `(35,46,50)` versus selected `(197,235,255)`; original header ROIs remain coherent. |
| Native117 Home/Settings | Same13-stage route,8 Home swipes and one Settings scroll across2 opens/closes. Home median37.5 FPS and Settings54 FPS match115;0 compositor failures,0 observed DSI/hard faults and18 unchanged digital-audio samples. |
| Focused post-Stop settled screenshot | Passed: exactly one default-False Run and one ordinary Stop; after one-second settle, original JPEG shows active Run and the terminal state-matches caption. Root reviewed both this and coherent restored Home. No DSI/hard faults, cleanup errors, OTA or full-route repeat. |
| Canonical117/HA131 adoption | Root adopted the exact 25 firmware and 18 HA files. Preimage backups, per-file guards and journals are preserved in the separate adoption receipts. No commit or push. |

The first117 preparation on D: stopped before the build junction changed or
compilation began: exFAT's262144-byte allocation units exhausted available space
while copying many small source files. The partial tree and failed receipt were
preserved; root verified a ZIP and moved the original partial tree to
`failed117-exfat-stage/partial-sources`. Two closed diagnostic files were moved
to D: with byte hashes preserved, freeing sufficient C: space. The final source
is `C:/aeh-build/native117-sources`, manifestSHA
`25414706542cf3d79f857b44d0096fab046a5dc4f80ac53079aeaec288bb9468`.
See `actionparams117-ack-work/build117-recovery-note.md` and
`diagnostic-relocation.json`; no canonical sources were deleted. This storage
preparation failure is separate from firmware compilation or device behavior.

The first linked-check invocation supplied a directory instead of a report
filename and stopped before any report or firmware write. The preserved
`native117-linked-invocation-error.json` records that operator error. The corrected
invocation produced `native117-linked-first/report.json`, status
`VERIFIED_GENERATED_AND_LINKED_PRODUCTION117`; no rebuild or source change was
needed. Artifact manifest SHA is
`b2bfa345dbcc871b32ed5b063ae0e686930a32a538e8a68321f462dbb8b5ca02`;
ELF SHA is `52c9234b6bf0911434a2c53ce8598dc0074caccaef5f7f418f75f7eec202f077`.

The117 feature route restored its two temporary card variants and original Info
card through revisions406,407,408. It made only the four planned control commands;
the final owned helper remains `params116:false`. It did not reset the effect
history or retry uncertain commands. Root's pixel review is separately pinned
in `native117-image-review.json`.

The post-Stop screenshot has neutral Run and the earlier HA-accepted status while
the immediately preceding diagnostic already reports idle/state_matches,
pending0, defaultfalse and ready1. The capture reads the current stable presented
frame; it neither forces a new LVGL refresh nor invokes the navigation readiness
suspension. This is consistent with capturing the preceding presented frame.
An isolated test using unchanged117 runtime and real LVGL passed the precise
Stop→HA_ACCEPTED→idle→STATE_MATCHES sequence: Run changes from neutral/pending
to active with a changed presented pixel and terminal caption. A separate
suspend/resume also restores active Run/defaultfalse, with no extra command and
no additional flush on five unchanged refreshes. This refutes the proposed
persistent readiness/style defect in that tested path, but does not measure
physical P4 terminal-presentation latency. No further firmware patch was made.

A separate focused hardware check closed the visual uncertainty without changing
firmware. It issued exactly one default-False Run and one legacy Stop, preserved
the same selection/default, waited one second after terminal readiness, then
captured the original presented JPEG. Root reviewed active light Run and the
terminal state-matches caption. The final Home original also has coherent clock
and night weather. CAS restored the original Info card at revision410, both
scripts were idle, and the helper remained false. There were no DSI/hard faults
or cleanup errors. This confirms the settled final appearance in that check;
it does not measure the exact terminal-to-presentation latency. The older JPEG
and its original report remain unchanged.

## Native116 failure and recovery boundaries

The Run(false) command, direct script service and helper value `params116:false`
shared the same HA context. The provider effect was real; native
`command_pending=1/action_result=0` persisted after running then idle. The owner
had omitted negotiated Params Script Run from its dispatch-only terminal branch.
Native117 corrects only that branch. Stop receives no Boolean fields, and ordinary
Action2 Script Run does not gain dispatch-only semantics.

The blocked116 Run button used the same active background `(197,235,255)` as
selected Run. Native117 uses the existing neutral palette until final readiness
and owner admission permit Run. No display or memory ownership changes accompany
these two corrections.

An initial tool preview suggested missing upper content after Yes. Decoded pixels
of all three original JPEGs prove that header/icons, symbol/status and last-use
regions are identical. Their shared RGB hashes are retained in
`actionparams117-visual-work/original-jpeg-roi-proof.json`. No repaint or DIRECT
fix was made from that preview impression.

The first two reconciliation attempts made no device or layout changes. The
separate v3 reconciliation passed: no service or retry, one guarded slot restore
from revision404 to405, scripts idle and Home1. The owned helper remains false;
it was not reset to conceal the completed effect. The original route FAIL and
all reconciliation receipts are preserved.

The immediate restored-Home JPEG genuinely had zero bright weather pixels in
ROI `[450,120,800,390]`. Its UART places capture before the weather task starts.
The subsequent passive 20-second observation on the same116/layout405 has 27544
pixels with `max(R,G,B)>100` in that ROI, with no DSI/hard faults. The earlier
current116 image had 27600. This shows the captured blank was not persistent in
the later observation; it does not qualify the transition's retained-frame
behavior or claim a new weather fix. Exact image hashes and decoded ROI counts
are pinned in this draft's `weather-roi.json`.

## Accepted baseline and remaining limitations

Native114's production fast-largest-heap query preserves TLSF allocation-size
semantics while avoiding a long critical-section heap walk. Same-firmware113
comparison measured query windows of 11–23 ms versus 23–56 us and 9 versus 0 SDK
underrun messages. The accepted114 route had no observed DSI messages in bounded
Home/Settings/Agenda checks; this is not a universal stability or 60 FPS claim.

Statistics115/HA129 and the HA130 asset-version alignment are adopted. The ready
CPU Statistics route had two opens/closes and three original JPEGs reviewed by
root. The bounded115 Home/Settings route had no observed DSI/hard faults. Empty,
unsupported, midnight/unit/time-zone transitions and physical touch are separate
coverage. The retained partly-cloudy weather versus clear-night state on the
same115 firmware explained 825676 B PSRAM and 13672 B internal-memory difference;
do not attribute unmatched-weather heap differences to a new panel. Its original
weather-route observer FAIL remains preserved alongside independent final health.

Firstboot115 already required mixer/Sendspin recovery and was not strict-clean.
The native116 and117 generic pthread failures have no proven worker attribution;
both unclassified first-boot records remain failed. The separate117 observation
is healthy at exact ELF117/layout405; its original report retains the pending-visual
status because root's successful image review is a separate human observation.
The117 weather binding explicitly selects `partly-cloudy-night` (UART line212),
whereas115/116 comparison states used `partly-cloudy-day`. Different retained
weather resources confound cross-firmware memory/FPS comparisons; no additional
weather experiment was requested or performed. A later healthy device does not
turn either boot record into a clean boot. No physical
audio, long-term leak, universal display or physical 60 FPS guarantee is made.

The exact115→117 motion comparison is `interaction117-vs115-summary.json`.
Worst observed Home frame was98.279→50.136 ms, Home-associated loop maximum
107.313→6.225 ms, and Settings worst frame22.263→21.425 ms. These are separate
sequential routes, not proof of an intrinsic speedup. Route-start free memory
changed by+64456 B PSRAM/+10068 B internal; within117 it changed+68592/-868 B.
Largest PSRAM block changed with cache lifecycle. Night/day assets differ
(8822/23613 source bytes); source file size is not renderer memory. Attribute
neither free-heap gains nor timing differences to Params without matched state.

## Adoption and continuation

Root completed scoped acceptance in `native117-root-acceptance.json`, then adopted
25 final firmware and 18 HA131 files. Receipts are
`canonical117-adoption/report.json` and
`ha131-native117-canonical-adoption/report.json`. All earlier failed records are
preserved. Feature/visual/motion checks and the focused settled-Stop check are
complete. Known first-boot, physical touch/acoustic, long-term and exact frame
latency limitations remain; they are not pending repeats of this acceptance.
Continue future features from native117/HA131 after rechecking live identity.
No Git push is authorized.

Primary local inputs are pinned in `C:/aeh-build/blue-flash-20261107/docs117-close/manifest.json`.
The root review at `native116-root-review-1.json` records the browser observations;
the final passive report still says pending visual because root reviewed its
original image separately. Preserve original report statuses unchanged.
