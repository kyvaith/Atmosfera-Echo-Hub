# Display flash investigation, 7 November 2026

Status: the minimal native114 correction is qualified and adopted for the
observed regression. The same-firmware comparison recorded nine DSI underruns
with the legacy largest-block query and zero with the fast query. Subsequent
bounded114,115 and117 interaction routes recorded none. Detailed evidence,
failed candidates and remaining startup/Agenda limitations are preserved below.
Feature work resumed after114 qualification; see the latest resume checkpoint.

The reproduced trigger was the largest-free-block heap query: its full heap
walk held a critical section for approximately11–23 ms, delaying service of the
DSI descriptor ring. The selected fast query preserves the requested size
semantics and limits the search to the relevant highest occupied TLSF bin.
Measured JPEG/API query maxima fell to56/36 us. The earlier cache-chunking
experiment did not remove the underruns and is not part of the adopted fix.

The user reports a short blue frame mainly during interaction, followed by
the same view, without the boot animation. The initial device identity was
native109, layout399, ELF
`e679aeb10b33cae33cf7d456b88b97245bec569f9f62c3658811080dbf43b9d5`.

## Current-device evidence

- `C:/aeh-build/blue-flash-20261107/baseline109-first/report.json`: a 30-second
  passive observation on Home3 recorded one new DSI underrun and an INVALID
  descriptor recovery counter increase from 90 to 91. A sleeping Home snapshot
  refresh was adjacent. No Lottie task/region was active, and no restart or
  processor exception occurred. This excludes active weather animation as a
  necessary condition for this particular failure.
- `C:/aeh-build/blue-flash-20261107/interaction109-first/report.json`: normal
  synthetic Home contacts, Home1 through Home5 and back, and two declarative
  Settings open/close cycles completed with display errors. The report is
  deliberately `OBSERVED_WITH_DISPLAY_EVENTS_PENDING_REVIEW`, not PASS.
  Original 800x800 JPEG captures of Home5, Settings and Home1 are adjacent.
  These still images show the settled views; they cannot establish the absence
  of a transient blue frame. Screenshot intervals are recorded separately.
- The interaction route uses the existing LVGL listener, not physical GT911
  input. Settings close uses its registered application lifecycle.

## Historical correction

The source/log audit under
`C:/aeh-build/blue-flash-20261107/history-audit/` found interaction-time
underruns in native96 on 5 November and in native97 on 6 November. Previous
55 FPS / zero-error Settings results described that sub-route; they did not
establish zero errors throughout the complete UART recording. Counts from
different routes are not comparable failure rates. OTA recordings can include
old-firmware output before the new boot, and repeated first-invalid records
must not be counted as new invalid descriptors.

## Candidate mechanism and ownership

Actual IDF 5.5.6 performs a complete M2C cache invalidation inside one critical
section. The existing C2M chunk option does not split M2C. Several display
paths invalidate a full RGB888 frame; the DSI two-descriptor ring meanwhile
requires timely interrupt service. This is a source-supported hypothesis,
not yet measured proof of the initiating cause.

The proposed experiment divides aligned M2C ranges into bounded pieces,
without changing C2M, image format, scanout timing, buffer count or ownership.
The existing caller must retain ownership throughout; a completed DMA write
must precede post-DMA invalidation, and presentation must remain after cache
completion. No CPU framebuffer-copy workaround is proposed. The option must
default to disabled outside the product experiment, and diagnostics must not
log from inside the cache critical section.

Admission requires focused checks, full native compilation, OTA boot evidence,
the same bounded interaction route, original screenshots and whole-route DSI,
memory and timing review. The separate native107 Agenda heap fault and
native109 startup-log classification limits remain open; neither is silently
closed by this display investigation.

## Candidate110 build result

The isolated candidate adds a default-off bounded M2C helper and explicit
`debug_cache_sync` diagnostics. Product configuration selects16KiB. Five host
variants passed, including the C header and actual C++ helper, and full product
configuration passed. The full P4 build failed because the new helper omitted
`esp_private/esp_cache_private.h`, which declares `esp_cache_get_alignment` in
the actual SDK. The host stub had incorrectly declared that function in the
public cache header. Candidate110 was **not flashed**.

The failed source remains at `C:/aeh-build/native110-sources`, with manifest
`C:/aeh-build/notification-cards-20261102/source-v110-build.json` (SHA256
`7eb75de42784b249eabe8841e1fa8eecd5f357ef97cb774402235688bcf569e8`).
Its compile report is `compile-native110-process.json` beside that manifest;
exit1 and source-after-verification are preserved. Candidate110a will carry
the explicit missing include and undergo a real P4 translation-unit check
before another complete build. The currently running device remains109.

## Candidate110a: built, first boot failed, automatic rollback confirmed

The corrected helper passed the actual P4 translation-unit check and full
firmware compilation. Source manifest `source-v110a-build.json` SHA256 is
`e30716b02f4b70785779489c80789aa7e9a60fe6016e3acf41614a1b7e56b5ea`;
ELF is `2ace1eb01a949fec89979337f4dab1303b6642070a83069e439061c0932046a1`.
The preserved artifact is `D:/aeh-build/native-context-v110a/manifest.json`
(SHA256 `ff54191126de88924fbd1eb6c2cc28318a703ac4facb4e7f369b0ef758b54650`).
Static RAM311782 bytes is136 bytes above109; image8685204 bytes.

One OTA succeeded on7 November09:45 UTC, but the first boot aborted immediately
after `pthread: Failed to create task!` and the Sendspin protocol-start refusal,
before the hub retry marker. Test actions stopped. The failed report and original
UART are in `C:/aeh-build/blue-flash-20261107/native110a-firstboot/`; no automatic
second upload was attempted. The guard closed UART too early to retain the whole
panic stack; future boot observers must keep a passive UART tail after stopping
all stimuli.

Exact-ELF decoding identifies `std::__throw_system_error(22)` followed by the SDK's
exception-allocation abort stub. Errno22 is independently recovered from the
saved register and exact abort/exception prologues; the calling return address
is beyond the truncated UART. This is not evidence of a display crash or of
unchecked `std::thread` startup returning: the separate linked audit confirms
the checked Sendspin thread paths and SDK inputs match109. The precise throwing
cleanup caller remains under investigation. Do not classify the new exception
as an accepted resource retry.

The read-only `recovery110a-first/report.json` confirms automatic rollback to109
with two full identity readings20 seconds apart, layout399, stable230399 audio
transmit frames, enabled/unmuted amplifier and active wake-word detection. There
was no new hard fault/reset during that observation. No110a navigation route or
screenshots were performed. The screen-fix A/B remains unexecuted, and no runtime
candidate files have been adopted into the canonical repositories.

## Diagnostic111 plan

Use110a's isolated cache experiment with chunking disabled at boot. Add only
default-off, failure-only ROM diagnostics around pthread mutex initialization,
locking and the system-error throw: preserve return codes and original behavior,
record the failing caller, and allocate no diagnostic heap or task. P4 eagerly
initializes `std::mutex`, but its constructor ignores a failed initializer; a
later lock on a zero handle can return22. This is a consistent hypothesis, not
the established failing object. The Sendspin cleanup has multiple mutex users.

The OTA observer must retain at least three seconds of passive UART after a
failure while issuing no further device stimuli. A successful boot is required
before the same-firmware0/16KiB cache comparison. The failed110a evidence and
109 rollback remain separate. Do not ship a stop-before-start shortcut as a
proven repair or begin new features while these failures remain unresolved.

Diagnostic111 full native build completed on7 November10:18 UTC. Configuration,
583 generated-source/250 ESPHome-unit audits and selected actual-ELF callsite
checks passed. Cache chunk0 and both diagnostic defines are present; the real
Sendspin constructor and stop paths call the wrappers, which delegate to SDK
originals. This is instrumentation, not a startup repair. Same-object internal
pthread calls may bypass GNU linker wrapping; successful wrapped calls also have
additional call overhead.

Source `source-v111-build.json` SHA256:
`fe84e4c47d6f1a8a1b3e182dd1bd4b4899b856aeeac82342cc328baea77a7299`.
ELF: `edf5a82ad5372481e6a218370ce298342f78d0ca2e910bee7c6a0659b9014d85`.
Artifact `D:/aeh-build/native-context-v111/manifest.json` SHA256:
`803c0ceb98c0b8a84790b7db923e946f83cb98e5804b059f352e9ccd5a18b571`.
Static RAM311782 bytes, image8685348 bytes. No managed-SDK changes from110a.
The one-attempt OTA and first-boot result are recorded separately under
`C:/aeh-build/blue-flash-20261107/native111-firstboot/`.

111 OTA succeeded. Its first boot completed the audio/wake lifecycle after one
qualified protocol-worker resource retry, without a synchronization-failure
marker, processor exception or rollback. Two SDK underruns occurred in the new
boot. The overall report is `OBSERVED_AUDIO_WAKE_WITH_DISPLAY_EVENTS_NOT_ACCEPTED`;
the intermittent110a exception remains unresolved.

The matched111 interaction routes `interaction111-off-first` and
`interaction111-on-first` both completed and restored chunk0. They recorded7
versus8 SDK underrun messages respectively (Home2/1; Settings4/7; an additional
off-route observation1). Observed IRQ deltas6/7 exclude the first cumulative
sample; invalid-descriptor deltas21/21. Do not add these correlated counters to
the SDK totals. All six screenshot intervals had zero SDK underrun messages.
The three original JPEGs in each directory were visually inspected: Home5 and
Settings rendered, with different retained Settings scroll positions. The off
Home1 capture includes the moon icon; the on Home1 capture has no visible weather
icon above the condition capsule. Do not describe both Home1 images as a clean
visual pass. Final verification must include visible weather and successful
capture as well as scanout counters. Still images cannot establish animation
continuity or absence of transient scanout errors.

Home compositor summaries were32–40 FPS off and33–40 on; Settings scroll53/54 FPS
(79 frames, zero failed frames each). This does not establish a speed gain.
M2C diagnostics showed zero errors/ISR/outer-critical calls; almost all call
windows had zero correlated underruns, with one on-route Settings-open exception.
Whole-call maxima include scheduling/preemption and are not measured critical
section durations. **The cache-chunk candidate is not an established repair and
must not be adopted as one.** Next investigate heap-query/interrupt latency while
retaining the original failures and the currently running diagnostic identity.

`quiet-rpc111c-first` completed32 read-only calls in four alternating status/
carousel windows on awake, idle Home1 with no active direct region. Each window
recorded zero SDK underrun messages and no new IRQ-counter sample; no hard fault
occurred. Stable pending bits4/30 belong to off-page tiles; Home1 bits0/1 remained
ready. RPC durations include transport/serialization and cannot measure the heap
critical section. Repeated queries warm metadata, so this negative quiet test
does not exclude a long query under UI load. Earlier attempts `quiet-rpc111-first`
and `quiet-rpc111b-first` stopped before any window because the test wrongly
required global readiness and then assumed three direct-region registry slots
instead of the actual four. Their separate stopped receipts remain intact.

Diagnostic112 will measure only the existing JPEG output-admission and carousel
status largest-block queries. Fixed counters/timestamps, no new task or heap,
no per-query logs, default-off upstream. It preserves the returned value and
original call exactly once. No allocator optimization is admitted before this
measurement; any future fast allocation path must account for failure callbacks
and fallback semantics.

112 complete native compilation/configuration and final linked-callsite audit
passed. Build ended7 November10:51:52 UTC;585 generated-source files,251 ESPHome
translation units,2354 compile commands. Source SHA256
`ffe510bf75320e11d638e9d62d6d9884a9a9b18f8d8562b62b9d16d1a65b705f`;
ELF `f3622ac27b40d308967d38a6336572aa00740c0693655261262709cc70fa3bb3`.
Preserved artifact `D:/aeh-build/native-context-v112/manifest.json` SHA256
`444ba2bb67488921faf4bca25c273d42d32b3171af06610747bae5a3c0aead0a`.
Static RAM312054 bytes (+272 versus111, including new API); image8690324 bytes.
The helper alone uses161 bytes of fixed state; its measurement path performs no
new allocation or task creation. Managed SDK remains unchanged. One controlled
OTA from111 has its separate receipt under `native112-firstboot` in the audit
directory; compile/link success alone does not qualify hardware behavior.

112 OTA succeeded but its first-boot observer stopped as
`FAILED_NO_AUTOMATIC_RETRY`/`UNCLASSIFIED_SENDSPIN_BOOT_WINDOW`: the pthread
resource error lacks its specific worker/client caller line. The hub logged
retry1 and then running1. No synchronization failure, abort or Guru was recorded.
Do not widen the classifier or overwrite the failed receipt SHA256
`0a67fe9f36646ef1a0e1c26ce341c1054859835a8d3200a962a90056730c404a`
(raw `8bb4fe4bac726c6ba74c2ef09808d2819520b0fb49411f735dcdafbbc25e23bc`).
Separate `current112-after-unclassified-first` observation confirmed112/399 twice
over20seconds,230399 audio frames, enabled/unmuted amplifier and wake detection,
without a new hard fault/reset. This justified a bounded diagnostic route, not
full startup qualification or adoption.

`interaction112-first` completed all13 motion/Settings stages, but **stopped**
when the final Home1 screenshot returned `no stable presented framebuffer`.
Home5 and Settings originals were captured and visually inspected. No final
Home1 JPEG exists. No processor hard fault occurred; synthetic contact was
released, profiling/heap measurement disabled and cachechunk0 restored.
Whole-route SDK errors10: Home3, Settings6 and final-capture1. Observed IRQdelta9
excludes the first cumulative count; invaliddelta24. Do not call this PASS.

Measured largest-block queries are materially long: JPEG source0 had26 calls,
296.784ms total and15.803ms maximum; API source1 had16 calls,207.989ms total and
18.950ms maximum. Every measured call took at least8ms. Settings close alone performed
11 JPEG queries totaling approximately124ms per cycle. Source0 had2 event overlaps
and source1 had4; these are overlapping observation windows, not unique causal
error counts or exact interrupt-masked times. Several display errors had no
immediate overlap. Results warrant same-firmware testing of a bounded metadata
query, but do not establish that it explains every blue flash.

Candidate113 is being prepared in isolation: default-off, hash-checked SDK5.5.6
option with an initially-disabled runtime toggle. It obtains the same rounded
largest-block result from TLSF free-list bitmaps while preserving capability
iteration and task-owner deductions; allocation/free/JPEG policies stay intact.
The retained112 measurements will compare both branches. The preliminary32-bit
host equivalence test had329099 matches after312000 allocator operations and
covered2516334 aligned sizes; that is algorithm evidence, not hardware acceptance.

113 delivery frozen at `history-audit/candidate113/manifest.json` SHA256
`57717232fd7954866ea416aff55ce275990d9f30c00401e260aba51a0ac9710c`.
Actual SDK on/off P4 compilation, exact public-API aggregation/toggle tests
(1.28million queries), lock/fallback tests and installer guards passed. A duplicate
helper evaluation through the MAX macro in the first draft was caught and fixed
before freezing. The failed draft test is preserved separately.

Root started full113 native build on7 November11:12 UTC. Source manifest SHA256
`7769a54792286bb84c89793a58687bae7d6c312c97710528ddd61965b7774760`.
Native CMake installed the six reviewed heap SDK postimages in the shared5.5.6
framework; all six originals are preserved in `native113-sdk-before` under the
audit directory. The installer validates every path/hash before writes, rejects
unknown source, uses an exclusive installer lock and is idempotent. No other
build using this SDK was active at admission. Managed Sendspin inputs remain
unchanged. The build-only component junction now targets native113-sources;
canonical product/fork runtime files remain untouched.113 is not yet qualified
for device acceptance; consult its separate compile/OTA/route receipts.

113 compiled successfully at11:25:41 UTC, image8691572 bytes. ELF SHA256
`507ad087a5fdc302a911bc3ea58ea861087217178b191d263e727cb8c8dec7a9`;
selected generated/linked checks passed (`native113-final-link/report.json`,
SHA256 `6c1b7b5e6c5357cda847d84f07fc5169f144af35c8e422012dabd30e32b0177d`).
The first preservation step stopped on a changed pngle cache path. Its old/new
15-file trees were byte-identical (version1.1.0); actual project and compiler
origins were checked. The original failed preparation receipt and input audit
are retained under `finalize113-preserved-failure`. A separate reviewed wrapper
allowed only this exact path relocation and retained all other original guards;
no recompilation or dependency upgrade occurred.

Preserved113 artifact manifest SHA256
`4c372d359a871a29fa4d289e141a49254eacf850589a52d931b678d784b15503`
at `D:/aeh-build/native-context-v113/manifest.json`. One controlled OTA from112
has started with the existing strict startup observer and UART failure tail.
Fast-query runtime selection still defaults to false in113; this is an A/B
diagnostic build, not production adoption.

113 OTA succeeded once (11:30:48–11:32:13 UTC). First boot remained
`UNCLASSIFIED_SENDSPIN_BOOT_WINDOW`: one pthread task-allocation failure lacked
the specific worker/client line; hub retry1 then running1 was recorded. No
hard fault occurred. Preserve `native113-firstboot/first-boot.json` SHA256
`8d8211339c31cfdb0b66322e8d3eb07a033232856e8f08e85418cbd7232aadb0`
and raw UART `a92397534df37e4efc45e3375fdc39787c7be794f6cd74d9247e44d7fafb38fa`.
The separate20-second read-only `current113-after-unclassified-first` observation
confirmed113/399 twice,230399 transmitted audio frames, amplifier enabled and
unmuted, wake detection active, no hard fault/reset. This permits diagnostic
A/B interaction; it does not turn the failed first-boot classification into PASS.

## 113 same-firmware comparison and selected114 candidate

Both routes completed13 motion/Settings stages and3 original JPEG captures.
The legacy route recorded9 SDK underruns (Home5, Settings3, capture1); the fast
route recorded none, with no new IRQ/invalid/DSIMEM event in any segment.
Neither route recorded a processor hard fault or restart. The root inspected
all6 original JPEGs: complete clocks, visible moon/condition, legible Home5 and
Settings. Settings retained a different initial scroll position; these are not
pixel-identical sessions or proof of every animation phase.

JPEG query totals were294.016ms/26 calls/max16.085ms for legacy versus
0.737ms/24 calls/max56us for fast. API totals were235.236ms/16 calls/max23.008ms
versus0.413ms/16 calls/max36us. Home compositor median36.5→40FPS; Settings54→54FPS.
These are bounded route measurements, not physical scanout or long-duration
stability claims. Full pinned data: `paired113-summary.json`, SHA256
`20dbc83f95df7281bde545493a5a6ba97ba61b4b2f91d611eefe44b3478d3e38`.
Both routes restored the prior fast-query flag=false and disabled instrumentation.

Root selected minimal candidate114 based on109, excluding110–113 cache chunking,
mutex wrappers, heap timing and new debug services. Only the default-off SDK
option/patch and product activation are retained. Product startup1001 selects
the fast query before JPEG BUS1000; original startup600 is semantically unchanged.
No allocation/free policy, display buffer, audio transport or task ownership changes.
The conditional source review passed; actual114 startup remains to be tested.

Frozen114 delivery SHA256
`147474b6671e461c6848727d1b46e92f2148abebc1a9fd6bdda79bef10c52d9c`;
source manifest SHA256
`92a7126377afe11d7b00565c1fcbdc53c7aed4c81ff99149cb731d9aa861a0cd`.
Full native configuration/build started using the existing six SDK postimages.
One initial preparation preflight rejected a manifest field-name mismatch
(`sdk_required_postimages` versus frozen `sdk_required`); correcting only that
input lookup allowed the original guards to pass. No source/image was changed
by the rejected preflight. Canonical runtime files are not adopted yet.

114 full configuration and compile passed (11:42:16–11:56:12 UTC). Static RAM
311654 bytes; image8681380 bytes. Source/input audit:580 files,248 ESPHome units,
2351 compile commands. Artifact `D:/aeh-build/native-context-v114/manifest.json`
SHA256 `6361111195def317a219fcb3eb6479b71d4e1e13bf322cff81aa9543d312d999`;
ELF `76b3c37a3f576aad8bd802b066392fd1200b1c542ff81b6f559fdad570bef226`.

The first link guard incorrectly expected the custom PPA header in generated
component sources. Follow-up inspection confirmed the real path: the generated
`lv_draw_ppa_wrapper.cpp` includes the frozen local C files through the build-only
component junction. The managed LVGL PPA header is a different, inactive draw
unit (`LV_USE_PPA=0`), not a replacement for that custom header. Corrected guard
`check114d_linked.py` verifies the wrapper, resolved include path, unchanged109
header, actual compiled wrapper and linked heap functions. Its report SHA256 is
`389dd6cecea4e77d02359c223f713beddea6d6275171d4530fe5561a8e65cde4`.
Earlier incorrect guards are retained; no firmware source changed or recompile
was needed. Generated startup1001 calls the setter with true;600 is preserved.
One controlled114 OTA from113 has now started. Hardware qualification is pending.

## Native114 device qualification

One OTA completed at12:00:52 UTC. The boot recorded no DSI event, hard fault or
rollback. Full startup PCM reached230399/230399 frames, with the amplifier enabled
and unmuted; wake detection remained active for35.107s. It was not a strict clean
boot: SsProto retried once and the known pre-chime mixer stack allocation recovered.
Both owners and the successful recovery were present in UART. No acoustic listening
claim is made. First-boot receipt SHA256
`bcd03d8bbbf4f65f10bf39c2fd31113b17d39601f04519ad872af2732d946f65`.

The native114 Home/Settings route completed8 Home swipes, two Settings open/close
cycles, a Settings scroll and three original JPEG captures. It recorded no DSI or
hard-fault event. Home compositor33–41FPS, median37.5; Settings54FPS/79 frames,
zero failed frames. The three original images were visually inspected: complete
clock/weather, legible Home5 and Settings. Report SHA256
`751764fa225c42df3a158a9d012f158d8ba47b4d214dde8d69bd55a52b3da402`.

The bounded Agenda route completed six page commands, seven original JPEGs,
two closes and a reopen, returning to Home1. HA remained127/Core2026.11.0,
layout399; no provider commands, layout/config writes, DSI events or hard faults.
The first route attempt stopped before opening on a historical fixture-key mismatch
(`profiles` versus `panel_extra_profiles`); the minimal corrected helper and both
reports are retained. It did not require a firmware change.

An initial visual concern about a disappearing Agenda heading was incorrect.
Decoded RGB pixels in the upper160 rows are byte-identical in all seven114 and
seven107 originals (SHA256
`2740aaf3212d23427e6f5dbd85d24f180d183b816b636801422b268c319b324d`).
The original images contain the title and status icons. No rendering fix was made.
The original concern remains in the first summary; separate corrected summary
`native114-closed-summary-corrected.json` SHA256
`6c8e3c82f4ac49f02b90ae50d3c40fdeb5c8ff92d44a049ac6972fbe3f13cd39`
and pixel audit SHA256
`d3e50d100393132952c2d6cb4e07b32b645d518c4c378fb33c6306252bc78d97`
document the correction.

Three software restarts were invoked separately. Cycles1 and2 passed the bounded
digital-audio/wake test with230399 transmitted frames and no DSI/hard-fault event;
both recovered explicit startup resource retries. Cycle3 is preserved as
`FAILED_NO_AUTOMATIC_RETRY`: `First-boot observation has a gap`. Its closed UART
has one expected reset, no hard fault/DSI event, and an owned SsProto retry1 followed
by running1. This is not counted as a third passed restart. Raw cycle3 SHA256
`019baa9905882658bb20f05851826d8cafbed9767743dbe6524f7c467c8185d6`.
A separate read-only current-health observation is required before continuing.

That separate20-second observation completed at12:21:31 UTC on114/layout399:
230399 transmitted PCM frames, amplifier enabled/unmuted, wake active at both
endpoints, no DSI event, hard fault or reset. Its receipt SHA256 is
`752523d226f29788eca6cebe1a309dd4bb53bc332ef1dc138046a001db10d7e3`.
This supports continued development, without relabelling cycle3 as passed.

The six minimal114 runtime files and two focused pytest files were adopted into
the canonical local repositories after rechecking every preimage and preserving
their prior bytes and Git status. No unrelated dirty source or index was changed.
All23 focused tests passed again against the adopted fork. Adoption receipt:
`C:/aeh-build/blue-flash-20261107/canonical114-adoption/report.json`.

These bounded114 results support the largest-block fix for the observed display
regression. They do not retroactively resolve the historical Agenda107 TLSF fault,
110a abort, failed113 first-boot classification, or every startup resource warning.
