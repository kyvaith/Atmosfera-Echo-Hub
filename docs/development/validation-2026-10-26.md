# Resumed validation 2026-10-26

This resumes the [2026-10-25 report](validation-2026-10-25.md#raport-stanu-na-koniec-dnia)
and the exact outside-Git checkpoint at
`C:\aeh-build\feature-wave2-20261024\end-of-day-20261025-checkpoint-v1.json`.
Nothing has been committed or pushed. Existing dirty source trees are retained.

## Initial current observations

Both repositories remain on `feature/ha-dashboard-2026-10-24`, with product HEAD
`65683789d83ceb4510b202ce98979043c8f5e2f6` and fork HEAD
`41e735733078651443b7c0bf56ede4c94f7f5d25`. At the initial observation, source
and installed integration were HA17; HA18 had not yet been adopted or installed.

The first read found the device offline in HA, unreachable at its known IP and
without a Windows USB port. Both failed read-only receipts are retained under
`C:\aeh-build\feature-wave2-20261024\resume-20261026`. The user then reported
an intermittent cable and restored the connection. COM5 appeared. A fresh
authenticated HA read passes for layout12, available device, accepted12 and
the exact HA17 frontend bytes; its temporary refresh token is revoked.
Receipt SHA is
`86f01be688fdf6c309efedd48aec37eac75ae839a15696d198c581587821548f`.

The native read after the cable change observes app/nav/selected/pending0,
renderer quiescent1 and Home1. It deliberately fails the old Home4-only closure
gate; this is a starting-page mismatch, not evidence of a firmware crash.
No input, preference change, reset, firmware upload or HA service/layout write
was dispatched during those initial resume observations.

## Work in progress

The current12 controller-only Home1 to Home4 route passes: 18 dispatched samples,
three released/settled streams, no active or uncertain stream, zero child-input
or entity commands and no sticky fault. Its actual receipt SHA is
`cb79877a4a3bb96d0c44597d4b00a24d917e09cf9b6ebe8f3ce1d47553fa0cbc`.
Fresh readonly Home4/owner-closed evidence derives input continuity from that
actual route and the period after it. It does not falsely claim no controller
input since yesterday's Locale test. Historical clean10 and temporary QA11
validators are not used as current layout proof.

One matching Settings cycle under HA17 also passes: 49 frames, 31 source FPS,
average31327us, maximum32751us, failed0, DSI underflow0 and unsafe0/0/0. The
pre-HA17 reference is 49/31/31296us/33067us/failed0. After close, free PSRAM is
7497KiB, largest block3840KiB, internal52KiB and app_work/scroll/close0. The
cold pre-sample includes1792KiB of hidden weather allocation, absent after
Settings; it is not a matching warm baseline for retained-memory attribution.
The post free difference is+15KiB with different JPEG backing. No regression
is observed in this single matching source-scroll cycle; this does not prove
panel FPS, p95, audio continuity, heap lifetime or absence of leaks.

Root reviewed the original restored Home4 image: readable tiles/contrast,
blue accent, Humidity6/Light7/W domu15 retained, no visible corruption. The
five preferences and off HUD remain unchanged, with no NV preference/entity
write. Report SHA is
`b7bbb76b4c522518ece5d8b01354bf7b6594c6552154211383489e0b97f91b26`;
root acceptance SHA is
`c6d01aefb5ac28d1357e6b2846c006ec30d3e6b69dd52034f0f671bfa3efaebd`.
The dedicated post-HA17 Settings item from the prior stop is now closed.

HA18 ordinary-action availability has independent source review CLEAN. Its
frozen proposal manifest is
`b29b939cb6ac5d5902d3910a7bac8a4278e088ab411126cdac130979dca9f49c`.
It adds one HA policy predicate for input_button/button/scene/script and uses it
in presentation and first-send negotiation. The existing live action resolver,
Script behavior, capability/epoch guards and native protocol remain unchanged.
Its 22 availability tests and 301 retained regression tests have their existing
recorded PASS; these have not been broadly rerun just for resuming work.

The offline HA18 package is now built, with25 public members: four changed
(two runtime owners and version/cache metadata) and21 unchanged, including raw
JavaScript and palette code. One availability test stream stays outside the
ZIP. Manifest SHA is
`70881be357c1230cd1f30bc76d239fa9b40fe28be3a968b77eab0a12cee3dd93`;
ZIP SHA is
`68c1a5c5f59b7cd76cfeed39560439c2467b87ff8ae42eb7ba150f66df597ae2`.
Package construction alone does not adopt canonical source or install the integration.

HA owns eligibility and service dispatch. The existing ESPHome binding owns the
Boolean, captured context generation, release cancellation and Home snapshot
gate. This candidate adds no firmware field, task, image buffer, font or
protocol version.

## Actual HA18 installation and isolated Scene campaign

Canonical HA18 adoption subsequently passes: all25 public sources equal the
package, four public files and one test changed, and26 preimages are retained.
Actual staging checks19 installed-container imports. Atomic activation retains
the previous25 sources, performs one HA restart, and passes source/storage
verification at09:37:49UTC. Entry/data/options remain byte-equivalent, with
layout12 and the same16 cards/three cameras. Actual authenticated API, native26
Home4 closure and editor18 browser checks pass. Original browser image reviewed;
save/undo/redo disabled and Humidity6/Light7/W domu15 unchanged. Installation-only
root receipt is `resume-20261026/ha18-installation-root-acceptance-v1.json`, SHA
`d7a7b12e8ef4d51099851fbb6fd8f37c89fb2376e1166e219b82b40a126dd614`.
No firmware source, build or upload was required for these HA-only changes.

At09:48UTC, a separately reviewed finite provisioner creates exactly one owned
virtual Boolean and dynamic Scene and temporarily changes only five fields on
stable card15, retaining all positions. Normal layout CAS12->13 is accepted.
Receipt SHA `8c16cff65667fefa0f51633687bc96eb107316429f6bdf80ed148651cfdd4054`.
The actor finishes at09:49:24UTC: six accepted pointer samples/three released
streams; disabled tap and restore-while-held produce no selected action. One
fresh tap produces exactly one current native contextual report, one Scene
service, its one implicit Boolean service and actual off->on feedback sharing
the HA context. Auth is revoked and no sticky fault/input uncertainty remains.
The two REST writes are controlled Scene state-projection fault injection,
not provider availability or physical household actuator evidence.

Both original JPEGs contain the complete readable Home4. The conversation image
preview appeared to show only the changed Scene tile; independent original-byte
decode confirms every other tile/header/footer is pixel-identical. Outside the
expanded Scene mask only179 pixels differ, at most2/255, with no difference>8.
Capture-source/log review finds a stable presented full-frame JPEG, no fatal/reset
or DSI recovery. This does not identify the exact image-preview mechanism or prove
physical animation. Campaign root review SHA is
`a33daf401136849f1420bd41dccc1b6070304861abc5a3fdbf92dfb7e349a706`;
actual actor SHA is `14a56702990f4846e3c49c335e8bddb850d58e5ca0cdeb245d2b4c226516cbf6`.

The separate five-field inverse13->14 passes, retaining current human positions
and every unrelated field (receipt `5565158b0c3cf44bf4c315b952f19e9b10865952ad6053c5e636eb9e1c408433`).
Fresh full16 native readback proves the ordinary card restored/unbound, owner
closed and accepted14 (`a278eba1bdeb08136176bdaec31105f2fcf627fcc7027c2ccd48301ef615e11e`).
One exact Scene delete and one exact Boolean delete then pass, with two complete
loaded-layout reference scans, state/registry/definition absence and revoked
temporary auth; no activation/provider/native command or retry occurs during
cleanup. Delete receipt SHA is
`01a7d3ac66905997a2f47aa3b869875b110dfb17226fd040b4aaef8837c27b9b`.
Browser confirms saved/sent/accepted14, clean draft with Save/Undo/Redo disabled,
and original Humidity6/Light7/W domu15. Its original screenshot is retained under
`resume-20261026/ha18-clean14-editor-original.png`.

Two post-HA18 matching Settings cycles pass, each with49 frames/31 source FPS,
failed0 and DSI underflow/unsafe0. Average31302/31343us and max32947/32979us compare
with pre-update HA17 average31327us/max32751us. Each cycle owns one open, one
benchmark and one close, leaves the five preferences/HUD unchanged and writes
no NV preference or entity command. Both final originals have SHA
`e96796ae2ff6ae53d78c775ca0d8c19ccdd443716546d066f341b26760c6fbc9`;
root reviewed the complete readable restored Home4.

Free PSRAM7497->7503->7500KiB and internal52KiB remain stable; app_work/scroll/close
all return to0. The first largest-block drop4032->2240KiB prompted the second
cycle, whose2688->4096KiB recovery excludes a sustained drop in this finite test.
Different JPEG backing explains the few-KiB free variation. This accepts finite
source-scroll and close/release behavior, not physical panel FPS, per-frame p95,
audio, long-duration leak/lifetime or physical touch.

Whole LVGL `perf1s` CPU/loop/flush windows are higher than the earlier HA17 window
and are **not accepted as a controlled CPU comparison**. Independent source audit
finds enabling logging does not reset its counters. Ordinary-loop resets happen
independently of logging; manual/direct scroll early returns can defer them, so
the first reported window may also include prior/open-transition work. The
reported CPU estimate is handler wall time minus flush, including waits or
preemption; it is not measured task CPU. No firmware change is justified by
these mixed windows alone. Detailed timeline investigation remains separately
recorded outside Git.

Scoped HA18 root acceptance SHA is
`eff912a4ac90cb08ae15ae0f93765502b0da2032767aac3bdcea5a0ae06c2081`.
Its explicit limits include whole-window CPU/p95/audio/lifetime. A separate next
proposal addresses the currently inert default Timer tap; its current progress
is recorded below and no Timer fixture exists yet.

## Timer HA19: actual device campaign and cleanup pass

The narrowly scoped Timer default-action proposal adds idle->Start,
active->Pause and paused->Resume through the existing HA action resolver and
optional availability Boolean. Its commands contain only entity_id, never a
duration. Exact installed Core2026.7.1 Timer source confirms start without a
positive duration preserves paused remaining time. Core ServiceRegistry source
also confirms call_service emits original service_data, before schema defaults
are exposed through the internal ServiceCall. Fourteen focused source tests,
165 relevant HA shim tests and independent full source review pass. No native
protocol, field, task, font, per-second timer or image buffer is added.

Actual offline package19 at10:16:36UTC has25 public members: cards.py and
version/cache metadata change,22 public members are unchanged, and one existing
test stays outside the ZIP. Manifest SHA
`c6fdb3c03d55f56881378a9719f1737b4d40c9a22e61bec988bc7c6e5186fcab`;
ZIP `1db3ff2e0fa5622a5ab569bb2e98c445e987d754484d6c09f04552799b13bcbd`.

Canonical source adoption passes at10:20:59UTC, retaining26 preimages/afterimages
and writing exactly three public files plus one existing test. All25 public
sources equal package19. Adoption receipt SHA
`2f4c57705f482177d7f3f59938b5410bc1dbab299d1d463f7ce03b8621f9a1f5`.
Subsequent HA19 staging checks19 real-container imports; one atomic activation
retains the exact25-source HA18 rollback and performs one HA restart. Actual
source/storage verification at10:27:15UTC passes, with all25 installed sources
equal to19 package and selected entry/data/options unchanged (layout14,16cards,
three cameras). Verification SHA
`dd49be28f3df2b3de8dd949ca880fc0b4399e0e14ed3eca771968a67d2bb9620`.
Real API observes accepted14/available and exact frontend19 asset bytes; clean
browser reload retains Humidity6/Light7/W domu15. Source/storage/API/browser-only
installation root receipt SHA
`1307fdbdc81f066d2c1f047f625764f0f1c3a790ad022e66d4f0a291a6adb5ef`.
Its fresh native closure and Timer campaign remain separate, pending proof.

The first fresh readonly native sample at10:36:28UTC confirms full running26
ELF/revision14, app/nav/selected/pending0, quiescent renderer and no sticky fault,
but observes Home3 rather than the required Home4. It therefore correctly fails
the fixed Home4 closure gate and is retained as FAILED_READONLY_NO_RETRY, with
zero inputs or provider/helper mutation. A normal controller Home3->Home4 route
and fresh proof after that route are being prepared. Earlier no-input-since-last-
Settings lineage must not be asserted after this new route. The user later
reported possible earlier swiping without certainty; the cause of Home3 stays
unresolved, with no software-fault or physical-absence attribution.

At10:55:22UTC one normal controller Home3->Home4 route passes:6 footer samples,
one released/settled stream, one explicit wake, no child action/fault/uncertainty
and clear target context. Receipt SHA
`3b8d765291a093c1f81efa2b76ae5f5b0f50e6ebb2f4fcdee842d4f714f55266`.
These are controller completions, not physical touch ACKs. Fresh cold proof after
that route passes at14 (`f3bbbfca748286ad77962b8b1ac40c660b6a89eceaf7eb361844821f9b0ed934`).

One owned12-hour restore-false Timer is then created and only five fields of
stable card15 are temporarily changed through normal CAS14->15. Actual fixture
SHA `5e1e6f56e3cb1c7c47fe4b663340b2d22e83b15341b53da849cc7e7765f75ae6`.
The native campaign passes at10:58:24UTC:10 accepted native diagnostic pointer
samples/five released streams and three contextual reports. Disabled tap and
restore-while-held produce no action. Fresh taps produce precisely native-owned
timer.start/pause/start with matching actual idle->active->paused->active states
and HA contexts. Pause and resume retain11:59:54; resumed deadline22:58:16UTC
equals the resume time plus that remaining value, rather than12hours. The actor
sends no direct provider/cancel or preference command. Two owned REST writes are
availability fault injection, not real provider failure. Actual actor SHA
`a7d367405a5e1043ea235a0c4e48f9375c1870341a11dfaf95b4b70e1ecacdc9`.

Four originals are reviewed: disabled, running Wstrzymaj, paused Wznów and
resumed Wstrzymaj. Start/resume JPEGs are byte-identical; all591744 pixels outside
the expanded Timer mask in paused/resumed originals are also identical. Saved
originals contain full Home4 even when the conversation preview shows a delta.
Campaign visual/feedback root review SHA
`8713fcf620ce7c200d3910c2f2785fc08ebe3745df530e9603c98eafa94c28c7`.

Exact five-field inverse15->16 passes with unrelated data/positions retained
(`6b09e838d5837355992e76a0e07cc24f78ce4e1a1ff869200fc4ac192d45c8c5`).
Fresh native full16/closed/unbound proof passes
(`782c3a05a1fca6acb70fc7c8bab5c3fc46958b192888e148f6a2399c53863dca`).
One explicit owned cancel then reaches exact idle/cancelled metadata, followed
by one exact collection delete, two complete loaded-layout reference scans and
definition/state/registry absence; temporary auth revoked, no retry/uncertainty.
Delete SHA `c68a152599fc07ffd4ad71cc84d89607be76ba9cae66c8b75ef545654d52cf5b`.
The matching Settings comparison and its limits are recorded below.

This is not a full Timer countdown/detail/result implementation. Timer services and normal helper collection are already loaded
in the real HA; a read-only preflight finds zero existing helpers and the exact
owned QA identifier absent, with temporary auth revoked. No helper or provider
action was created by that preflight.

## HA19 matched workload and scoped checkpoint

The first post-HA19 Settings run completed46 source frames/29FPS,
average33278us/max40713us, failed0. It had the microphone unmuted, while the
earlier HA18 samples were muted; wake-word/audio work therefore differed.
The unmatched result remains evidence and is not presented as a controlled
regression. A first temporary mute was restored without benchmarking because
the Voice UI was open. A second mute, one existing idle-guarded nonpointer UI
close and a fresh native closure allowed a matched run. These two finite
mute/restore pairs made four preference writes outside the benchmark itself;
the benchmark made zero preference writes. The original unmuted state was
restored and fresh HA readback confirms both players/satellite idle.

The matched cycle completes49 source frames/31FPS, average31330us/max33244us,
failed0. Its average lies within the earlier HA18 range31302–31343us. DSI unsafe
diagnostics remain zero and owned application/scroll/close buffers are released.
The original Home4 capture was reviewed. This accepts source-rendered Settings
scroll performance for the matched scenario, not whole-task CPU or frame p95.
Mixed profiler windows and 32-bit runtime-counter rollover risk prevent a
whole-CPU comparison; neither implies an instantaneous100% CPU observation.

Whole-install memory is still qualified. The matched post-sample has7129KiB
free PSRAM versus7500KiB in the earlier HA18 post-sample, about16KiB less
internal memory and four more tasks. Pre-Timer route logs already contain
308–309KiB residual difference/internal−16KiB and the238208-byte retained
overlay. The Timer-through-first-Settings interval adds only3–4KiB residual;
a later59KiB spans subsequent Voice/microphone lifecycle. This narrows timing,
but neither attributes all memory nor proves leak-free lifetime.

Scoped root checkpoint SHA
`301155645ba05261b232a566982e412f495cabd847635faa1d16dee9ce52bfd1`
joins installation, actual Timer contexts/remaining, originals, inverse/delete,
matched scroll and fresh current native/API/browser16. Full running ELF26 is
unchanged; Home4 is closed/unbound/quiescent, no pending command or sticky fault.
Browser Save/Undo/Redo are disabled and human positions are preserved. Closure
does not claim snapshot/input readiness or absence of physical contact.
Countdown/detail/cancel UX, physical touch/actuator, audio and lifetime remain
open. No firmware compile/upload or Git commit/push occurred today.

## HA20 Sun local source/package checkpoint

The passive Sun tile projects the nearest future aware next_rising/next_setting
from HA in HA's timezone. PL/EN compact DD.MM HH:MM captions fit the preserved
native26 font in admitted normal text places; reserved/large value places are
refused in the server and editor. No native field, task, font, image allocation,
astronomy implementation or per-second poller is added. A filtered owned HA
config listener uses the existing coalesced push for timezone-only changes.

Offline package20 has25 public members,7 changed/18 unchanged; three existing
tests and one architecture document stay outside its ZIP. Manifest SHA
`931374c0af33b40f35bc4594d223516a6fcc80037a3439e1a626e7f8f29eb85d`;
ZIP `cb95dd620dbb48469a8436e5558697c835fd88a993810c53893eaebd6b002fe8`.
Actual canonical adoption preserves29 before/afterimages and changes11 existing
paths; receipt `ecac0c81a36a8ea3f996e6b5ed8f8f6230c2395a0016fafda307d3dca0cca8fd`.
Post-adoption canonical182 HA plus33 availability/Timer tests and219 Node tests
pass. The first combined unittest invocation used an incompatible module path
for the availability tests and failed its import; discovery with the existing
test directory then passes. Deployment and device/visual/performance acceptance
are still pending at this checkpoint.

At12:55–12:56UTC actual HA20 staging passes19 real-container imports and three
pure Sun formatter cases in the same Core2026.7.1 process. One atomic source
exchange retains exact HA19 rollback and requests one HA restart. Read-only
verification confirms all25 installed sources match package20, old25 rollback
is retained and full entry/data/options remain unchanged at16/16cards/3cameras.
Storage/source receipt SHA
`38f9ad899aac0053a6e868b3340c87e5736c59227b37504d32a854b1c910b83b`.
Actual API observes accepted16 and exact20 frontend bytes. Clean browser reload
retains disabled Save/Undo/Redo and Humidity6/Light7/W domu15. Installation-only
root receipt `bed46ab85efebad1c4e31d90b29a5c43f30a00002026b8dda45b89f2a6a3f288`
does not yet accept native Sun presentation/cleanup/performance.

A bounded read of only sun.sun and sensor.indoor_temperature confirms both are
real current HA states. The indoor source remains20.6; its existing binding is
not a missing-source placeholder and must be restored after the owned QA test.
Sun exposes aware future next_rising/next_setting and HA Europe/Warsaw.

The clean browser also exposes a Light preview discrepancy: library state
unknown but preview On. HA19/HA20 stateText methods are byte-identical and pass
unknown to the optional HA frontend formatter. A separate source-only guard
proposal leaves canonical/installed20 untouched. Its meaningful regression
fails against old bytes (219pass/1fail: On versus Unknown) and passes with the
guard (220pass), covering PL/EN and malformed live values while preserving known
state formatting. This is host evidence, not an actual-frontend fix acceptance.

A later fresh read at13:09:46UTC observes light.swiatlo_1 on (HA change time
13:08:38UTC), while a fresh browser observation still shows library unknown and
Controls preview On. The confirmed current discrepancy is a stale catalogue
snapshot versus a live preview, not proof that HA formatted unknown as On.
The defensive guard proposal is therefore parked; it does not fix catalogue
refresh and must not be reported as the solution to this observation. Official
HA frontend compute_state_display also handles unknown/unavailable explicitly;
its current source is context, not a verified pin of this installed frontend.
