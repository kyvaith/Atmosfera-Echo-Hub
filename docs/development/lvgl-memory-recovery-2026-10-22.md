# LVGL latency and memory recovery, 2026-10-22

**Current result: normal11 has completed the bounded hardware regression suite.**
The subsequently published checkpoint is identified in the
[2026-10-24 publication record](publication-2026-10-24.md). Its hardware evidence
remains dated 2026-10-22; publication is not another hardware test.
Its exact image, matched measurements and coverage are recorded in
[Normal11 hardware result](#normal11-hardware-result). This is not cold-power,
real Sendspin playback or successful provider/acoustic-dialogue acceptance.
The preceding failed images below remain rejected and their evidence is retained.

The candidate named `final4` recovered memory
and improved handler latency, and passed its first matrix and five warm starts.
A further weather repetition then recorded one real DSI bridge underrun at
`2026-10-22T14:30:43.403164Z`, tick `168483`, bridge/raw `0x1`, FIFO `9`.
That failed run is retained and blocks a blanket stability pass. Its sticky
failure also prevented weather/logging restoration. Subsequent diagnostics and
any replacement image must be documented separately; earlier passes do not
erase this event.

Candidate5 also remains **unaccepted**. Its subsequent application matrix
recorded a recovered DMA invalid-descriptor event (`0x2011`, tick `872382`)
during Gallery, then an unfed `loopTask` watchdog after Settings language/close.
The device rebooted itself. The idle-task PC retained by the crash handler
does not identify the blocked loop's stack or establish the lock owner. The
matrix and post-reboot forensic evidence are preserved separately; its earlier
weather, Camera and 18-return passes do not cover this later failure.

This is the local follow-up to the [official ESPHome integration](esphome-upstream-2026-10-22.md).
The source bases are companion `d0b129d9002cea38083549fbbbf197e8819cc49b`
and product `880c2379dc0718c86771e0ef10ad815b0174bf8e`. Changes in this
follow-up were uncommitted during validation and were subsequently published
at the user's request on 2026-10-24. Exact source manifests, compiler
artifacts and device evidence are retained separately.

## What the higher LVGL number measured

The original `perf1s loop=` expression is unchanged: accumulated wall time
inside `lv_timer_handler()` minus explicit flush time. It includes preemption
and waits. It is neither one application-loop iteration nor scheduler CPU time.

A lightweight, default-off `lvgl.handler_diagnostics` option separates the
recursive global-lock wait from handler body wall time and counts calls without
rendering. It adds no task, image or trace buffer. The instrumented comparison
changed only the live sunny worker priority in the same firmware and boot:

| Same-image experiment | Priority 2 | Priority 1 | Priority 2 again |
| --- | ---: | ---: | ---: |
| Median accumulated handler wall, normalized per second | 59.19 ms | 10.54 ms | 48.67 ms |
| Median handler calls per reporting window | 13 | 44 | 12.5 |
| Median maximum handler body duration per window | 21.77 ms | 1.24 ms | 22.04 ms |
| Median aggregate global-lock wait per window | 105 us | 1,016 us | 95.5 us |
| Median sunny rendered FPS in complete two-second windows | 49.64 | 46.29 | 49.80 |

The higher-priority, CPU-bound sun rasterizer could preempt the UI thread on
the same core. Even handler calls without a render accumulated approximately a
whole raster's wall time. The call count fell rather than grew, excluding
extra idle polling as the main cause. The lower-priority trial had one genuine
native invalidation; its large duration remains in the evidence rather than
being silently removed. These are wall and rendered-frame counters, not
physical panel FPS or measured audible continuity.

The inline application loop, scheduler wakeups and task-notification ownership
also differ from R25. The controlled experiment isolates the priority effect;
it does not identify one upstream commit as the sole trigger. The official
notification-index isolation is retained.

## Preserve the picture while making scheduling fair

Lottie now accepts a per-widget `task_priority`, default 2. The product's nine
CPU-bound weather animations select 1. Other widgets, task affinity, stack
size, animation phase and framebuffer ownership stay unchanged.

The first combined device candidate changed only clear-day priority. It fixed
sunny handler stalls without losing raster throughput, but exposed the same
phase-sensitive preemption with the unchanged priority-2 cloudy worker:
7 of 10 early no-render windows had body maxima over 10 ms, compared with 1 of
8 baseline windows. Its 16–18 ms stalls matched the unchanged approximately
17 ms cloudy raster bursts; outer-lock waits and raster work did not grow.
This candidate is retained as an intermediate, not a blanket performance pass.
The final product applies the same fair scheduling policy to all weather
workers. The final hardware results below must confirm that broader policy.

Simply lowering priority cost roughly 7% of median rendered throughput in the
trial. The radial renderer therefore avoids redundant clears only when the
new ray rectangle cannot touch the retained sun disk. All previous ray bounds
are still cleared. A conservative arithmetic guard keeps the complete legacy
clear behavior when the old signed-Q8 circle arithmetic is not provably safe.
No resolution constant, additional surface or quality reduction is introduced.

The naive clear removal was rejected after pixel differences at small sizes.
The first geometry-only variant was also rejected at 1024 pixels. The accepted
variant passes 100 actual C++ oracle cases: 39,264 frames and 3,217,384,899
pixel comparisons, with zero differences or added disk errors. Cases include
309/360 phase grids, alternating buffers, reverse/skipped/wrapped frames,
restart, recolor, odd strides, non-square and large geometry. Large fallback
cases also preserve the exact original clear-byte counts. Host execution
establishes pixel equivalence; actual P4 throughput is a separate device gate.

## Account for the memory increase

Sendspin 0.9.3 originally reserved 993,616 more persistent bytes than R25's
600,000-byte audio ring. Some shared-protocol storage is required, but the
compressed-codec rate assumption overestimated receive hold overhead for the
product's PCM-only formats, and artwork assembly remained allocated while idle.

| Allocation | Integrated checkpoint | Local policy | Idle delta |
| --- | ---: | ---: | ---: |
| Sendspin shared receive ring | 1,331,472 B | 1,006,864 B | -324,608 B PSRAM |
| Sendspin encoded artwork assembly | 262,144 B | 0 while idle; same 262,144 B cap | -262,144 B PSRAM |
| Hub HTTP/protocol/artwork task stacks | 15,872 B internal | Same sizes in PSRAM | +15,872 B PSRAM; -15,872 B internal |
| Camera encoded input and HTTP read storage | 768,000 + 8,192 B | 0 while stopped; same active sizes | -776,192 B PSRAM |

The source-level net idle recovery is **1,347,072 B PSRAM (1,315.5 KiB)**
and **15,872 B internal RAM (15.5 KiB)**. Actual free and largest-block values
also depend on scene, retained previews, network state and allocation history.

Sendspin's default-off `optimize_memory` policy preserves the 600,000-byte
audio quota, advertised ring-item capacity, artwork cap, receive backpressure,
ordering and acknowledgement gate. Compressed or invalid formats keep the
conservative rate assumption. Artwork assembly remains owned by the artwork
thread through ASSEMBLING/READY and the synchronous decode callback; main-thread
acknowledgements never free it. Allocation failure discards only the new cover.
The media-source sync task retains its internal stack.

The native integration accepts only the reviewed 0.9.3 owner hashes, validates
all owners before any write, and is idempotent. The disabled feature preserves
the complete original source behavior. A narrow Git ignore exception ensures
the new CMake component is included in a normal source inventory; a packaging
test reproduces and prevents the originally omitted-file failure.

Camera's default-off `release_input_buffers_on_stop` policy is enabled in the
product. Only the stream worker admits and releases its inputs. Stop signals
the worker; it does not free memory while HTTP, parsing or JPEG consumption can
still read it. The worker disconnects and resets the parser before release,
and reacquires the same capacity before reconnecting. Half-allocation failure
rolls back and retries. Atomic accounting avoids reading freed pointer state.
The existing static-component destructor assumption remains unchanged.

## Source and host checks

The focused campaigns cover 120 Sendspin checks, 17 Camera checks, 30 LVGL
configuration/lifecycle/diagnostic checks and 100 pixel-oracle cases, without
skips. The later packaging checks are reported separately rather than added to
overlapping totals. Independent reviews replay the three Sendspin source
transformations and Camera ownership paths. Whole firmware and actual device
results must be read separately below.

## Earlier final4 image: measured gains, subsequently rejected

Final4 is the normal product configuration, with handler diagnostics disabled.
Native ESP-IDF compilation completed successfully, followed by all 79 original
artifact checks and 27 combined checks, including all nine generated weather
priorities, guarded Sendspin owners, Camera input lifetime, PIE restart code,
unchanged display buffers and diagnostics absent from the linked image. All
32 changed runtime/test/package files match the canonical repositories. Later
documentation edits are identified separately from compiled runtime sources.

| Final image identity | Value |
| --- | --- |
| Compilation marker | `2026-10-22 16:04:47 +0200` |
| Config hash | `0x0abd8272` |
| ELF SHA256 | `a8721c2972df40d559709ac71bf88ac1d646bc61bb062e581faa4d259e93e14c` |
| OTA SHA256 | `3a876bed7c0d06691b9e4efefa6c906cd2c55e38bbd5ceebdfee6db8c93c07d4` |
| OTA size | 7,769,088 B |

The hash-checked OTA transfer succeeded. Independent API/UART marker checks
and the new boot sequence confirm the new image started; upload success alone
is not counted as boot validation. All 55 sampled boot regions were inspected:
the stroke grows, the complete mark remains stable, and the background matches
the accent. A transition sample joins independently read chunks and is not an
atomic screenshot. The complete Home screenshot and its controls were checked.

The final weather comparison uses the unchanged frozen helper and normal
build18 as its reference: both images have handler diagnostics **off**. The
earlier same-image priority experiment remains the causal diagnostic evidence;
its firmware-duration and call counters are not invented for the normal image.

| Matched weather measurement | Build18 | Final4 |
| --- | ---: | ---: |
| Sunny early zero-invalidation/flush accumulated handler wall, raw median | 49,814 us | 10,292 us |
| Sunny median reported longest handler call, integer ms | 22 | 0 |
| Cloudy early zero-invalidation/flush accumulated handler wall, raw median | 7,881 us | 8,210 us |
| Cloudy largest reported handler call in those selected windows, integer ms | 16 | 0 |
| Sunny rendered FPS, complete capture-free raster windows | 48.857 | 50.528 |
| Cloudy rendered FPS, complete capture-free raster windows | 26.965 | 26.326 |
| Sunny matched navigation-cycle busy CPU | 42.05% | 40.60% |
| Cloudy matched navigation-cycle busy CPU | 28.25% | 28.45% |

Sunny accumulated wall falls 79.3%. Cloudy no-draw stalls disappear; its raw
accumulated median is 4.2% higher, with every selected final maximum below the
1 ms reporting resolution. The exact paired cloudy throughput is 2.37% lower
(0.64 FPS), within the separately recorded 26.17–26.97 FPS baseline range;
this is retained explicitly rather than called a zero-cost change. These are
rendered counters, not physical panel FPS. CPU samples average matched
navigation cycles, including retained-frame periods. Reception-time-normalized
wall estimates are labelled estimates; host-log jitter has no proven bound.

| Matched scene memory | Build18 | Final4 |
| --- | ---: | ---: |
| Sunny free PSRAM | 4,626 KiB | 6,002 KiB |
| Cloudy free PSRAM | 3,949 KiB | 5,323 KiB |
| Largest free PSRAM block, either scene | 2,432 KiB | 4,032 KiB |
| Sunny free internal RAM | 30 KiB | 50 KiB |
| Cloudy free internal RAM | 36 KiB | 57 KiB |
| Home raw slots | 5,625 KiB | 5,625 KiB |

Free PSRAM rises 1,374–1,376 KiB. Source-derived buffer recovery, encoded JPEG
size differences (52 KiB here), network/cache history and integer diagnostics
are accounted separately; the measured delta is not attributed entirely to
one allocation. The same-instrumentation diagnostic2→3b comparison independently
recovered 1,374–1,378 KiB and 15 KiB internal RAM. Actual JPG description,
microphone, paging, status and background ROIs match their baseline decoded
pixels, as does the sunny artwork. Cloudy artwork has a small retained-phase
difference (mean error 0.553/255; 1.23% of pixels differ by more than 12).
The clock naturally changes with time. Both weather scenes were viewed.

The first final4 application matrix completed 12 cases and 33 screenshots; three
Camera cycles released all 776,192 input bytes after close with stable warmed
memory. Three embedded audio files produced PLAYING→IDLE. One real Voice attempt
after that workload and five actual warm-reset/Voice cycles completed without
extra resets, fatal failures or DSI errors in their own bounded windows. Gemini
rejected all real conversations because prepaid credits were exhausted.

The subsequent `final4-weather-repeat-after-warm` failed on the real bridge IRQ
above during the first cloudy Home2→Home1 return, approximately 1.04 seconds
after the return action. Native full-display drawing and resumed direct regions
occurred in the same reporting window, on a source path that permits their
parallel execution. This is a diagnostic lead, not yet a proven cause. No reset or panic
occurred. `dsi_under=0` in another window cannot cancel the lifetime IRQ total.

The original held-Settings helper also failed an obsolete nine-segment assertion:
the restored headroom allowed the intended contiguous 2,297,603-byte allocation
for a 1,436×800 RGB565 snapshot. A separately validated external helper accepts
both exact contiguous and partitioned layouts; held-frame coverage still needs
its successful rerun. Two unchanged Settings row glyphs are missing from the
pre-existing font list; this cosmetic issue is outside this runtime delta.

## Candidate5 replacement: earlier passes, subsequently rejected

Candidate5 adds the default-off reusable
`lvgl.direct_region_full_refresh_barrier` option, enabled by the product. For an
actual display-wide invalidation it keeps the existing SRM mutex and native
target reservation through `REFR_READY`. A second check before `RENDER_START`
handles full-display promotion during layout. Partial refreshes retain their
previous concurrency; display deletion runs the same cleanup. No task, image
buffer, CPU copy, clock or memory-QoS policy was added. The bounded
`full_barrier` counter proves use of this path, not the initiating cause of the
earlier underrun. The reviewed compact-output DMA copy uses its own lock and
completion semaphore and does not reacquire this SRM mutex.

The new lifecycle/schema fixtures pass independently, including default-off,
partial/full/late-full areas and abort cleanup. Native ESP-IDF compilation and
all 79 artifact plus 29 combined checks pass. The latter include the enabled
barrier and linked implementation, all weather priorities, unchanged display
buffers and absent handler diagnostics. All 36 changed runtime, package and
test inputs match the canonical repositories; subsequent documentation differs
from the frozen build by design.

| Candidate5 identity | Value |
| --- | --- |
| Compilation marker | `2026-10-22 16:47:44 +0200` |
| Config hash | `0xbff84d70` |
| ELF SHA256 | `44791d79b63e6b2713837411c9c1324ff2e03eca1d17823d6119d33122f51df0` |
| OTA SHA256 | `7214942a2a134e56549470cdbec9bbf32a94b5a246294665cfecbc1ed93b3945` |
| OTA size | 7,769,520 B |
| Source manifest SHA256 | `e4a85bd8bd243069adbd780a175b6b9d9409d42c403ac5ffa58519e9a5efb6ee` |

The immutable hash-checked OTA transfer succeeded, and API/UART identity and
boot evidence independently confirm the new image. All 55 boot samples were
inspected; the stroke grows and remains stable before Home, with the original
non-atomic handoff sample retained. The full Home image is coherent.

| Matched normal-image measurement | Build18 | Candidate5 |
| --- | ---: | ---: |
| Sunny early no-invalidation/flush accumulated handler wall, raw median | 49,814 us | 11,177.5 us |
| Sunny median reported longest call, integer ms | 22 | 1 |
| Cloudy early no-invalidation/flush accumulated handler wall, raw median | 7,881 us | 7,311 us |
| Cloudy largest reported call in those selected windows, integer ms | 16 | 0 |
| Sunny rendered FPS, capture-free raster windows | 48.857 | 49.857 |
| Cloudy rendered FPS, capture-free raster windows | 26.965 | 26.266 |
| Sunny matched navigation-cycle busy CPU | 42.05% | 40.35% |
| Sunny free PSRAM | 4,626 KiB | 6,009 KiB |
| Cloudy free PSRAM | 3,949 KiB | 5,329 KiB |
| Sunny free internal RAM | 30 KiB | 50 KiB |
| Cloudy free internal RAM | 36 KiB | 57 KiB |
| Home raw slots | 5,625 KiB | 5,625 KiB |

The selected sunny accumulated wall falls 77.6%; the old cloudy no-draw stalls
are absent. Native cloudy refresh rows still include 44–48 ms maxima while
actually invalidating/flushing pixels; those are not no-draw stalls. Sunny
rendered throughput rises 2.05%, while cloudy is 2.59% lower (0.70 FPS); this
small paired cost is explicit. Memory, CPU and FPS comparisons use the same
frozen helper and diagnostics-off images. Different ambient weather/cache
history is excluded from the matched scene attribution. Non-clock weather,
description, controls and background image ROIs match the preceding image.

A separate 12-cloudy/6-sunny Home2-to-Home1 stress completes all 18 returns with
73 fresh barrier hits, zero refresh fallbacks, 211 zero DSI samples and 10 zero
DMA recovery samples. Its 192,162-byte UART slice contains no underrun, reset or
fatal failure. Weather and logging preferences are restored, and Home retains
three raw slots. The first Camera lifecycle campaign also completes three
active-to-idle releases of all 776,192 input bytes with a stable warmed plateau.
Camera throughput attribution and the remaining application, held-scroll,
post-workload audio, five warm-start and post-warm weather gates remain open
until their separate evidence below is recorded. Frame-late and publication
rejection warnings remain in the evidence; these runs are not called warning-free.

The later candidate5 matrix failed. The first DMA invalid descriptor/recovery
appears at API time `15:06:30.991579Z` (delivered by UART at
`15:06:31.667001Z`) during Gallery loading/artwork local open, before Camera was
opened. The existing test helper did not classify that counter as fatal, so its
Gallery and subsequent individual pass labels are not valid clean-hardware
claims. A separate strict wrapper now treats nonzero invalid/recovery/error
status as sticky failure; the original helper and failed report are unchanged.

After Settings language/scroll/close, the last successful identity and final
`debug_navigation_home(page=1)` send occur at `15:08:55.451Z`. At
`15:09:25.051532Z`, watchdog output identifies unfed `loopTask` on CPU1 while
both CPUs run idle tasks. The retained PC decodes to `esp_cpu_wait_for_intr`
and `prvIdleTask`, not the waiting loop's call stack. This establishes blocked
or suspended progress, not a particular semaphore or hardware cause. Source
review has not proved an SRM-to-LVGL lock cycle. SDK PPA completion and several
display/global-lock paths still contain unbounded waits requiring task stacks
to distinguish them. No automatic reset was commanded by the test.

The failure is sealed in `candidate5-matrix-failure-review-v2/failure-proof.json`,
including 556,599 UART bytes across 359 verified chunks through the ensuing
boot. Post-reboot collection preserves the retained fault and actual settings.
A separately bound cleanup restores the saved six preferences, changing only
Performance Logs and accent, and fresh-verifies all ten relevant entities.
It sends no reset or error-counter clear. Diagnostic6 preparation enables only
ESP-IDF UART task core dumps through an external component/configuration;
canonical runtime sources remain unchanged. Its build, upload, reproduction
and conclusions are separate from production acceptance.

## Diagnostic6: actual blocked operation

Diagnostic6 changes only external core-dump configuration/component wiring from
the frozen candidate5 runtime. It is not a production image. Its marker is
`2026-10-22 17:15:57 +0200`, config `0x380d3592`, ELF SHA256
`5f246115c6a6969e621d9d72dfece59f88b6bb5cc0f2d7166ad84f1232031db9`
and OTA SHA256
`94c2d0ce75c989e10619a286c32df249780056d55eeaf5bcf520a5268411d674`
(7,775,760 B). Native UART/ELF/CRC32 and task capture are linked; configured
dump stack is 2,048 B, actual SDK allocation 2,148 B. No flash/whole-DRAM dump
is enabled. The hash-checked OTA, exact API/UART identity and 55 boot samples
are verified separately from the following failed reproduction.

The isolated theme test opens no Gallery or Camera and reproduces the watchdog
in its first cycle. Unlike the first failed matrix, this fresh boot has no
recorded preceding DSI IRQ or DMA-invalid/recovery event. The last sent action
is Player open; the actual call stack confirms execution reached its prepare
callback. The decoded `loopTask` waits in:

`ppa_do_operation` completion semaphore → `ppa_do_scale_rotate_mirror` →
`lv_draw_ppa_img_srm` band submission → native LVGL refresh →
`ui_clear_interaction_press` → `LvglNavigation::open_application`.

The region worker is idle, the SW draw worker waits for work, Camera is idle and
the Sendspin workers wait for input/events. This identifies the immediate
blocking site; it does not prove which missing PPA completion mechanism caused
it. The earlier idle-PC-only diagnosis could not identify this path.

The actual 47,312-byte core has independently matching CRC32 `bfbbec7c`, and
Espressif's loader plus GDB reconcile 41 unique task notes, TCBs and backtraces.
The SDK's unused envelope counts are correctly zero; this version has no newer
TaskInfo notes. Earlier rejected parser assumptions remain preserved. The core
contains the actual nine-character app-hash prefix `5f246115c`; full local ELF
hash and OTA descriptor binding are verified independently, not invented from
that short note. Raw stack/core files remain private local diagnostics.

Numeric-only inspection identifies the final SRM band: RGB888 source 384×384,
block 356×32 at (0,352), destination 800×800 at (444,420), scale 1:1 and rotation
zero. Both rectangles are in bounds. Its macro-block FIFO tail equals 1,536
bits, while the current SDK workaround tests strictly below that limit. This
is a candidate hardware edge requiring a same-image experiment. The related
[Espressif issue 19023](https://github.com/espressif/esp-idf/issues/19023) and
[official rotation fix](https://github.com/espressif/esp-idf/commit/469aa16)
do not establish the cause of this unrotated transaction.

Source/build inspection also finds a separate native integration defect:
`lvgl_build_filter.py` returns from its SDK PPA cache patch when no PlatformIO
environment is present. The native CMake path patches LVGL sources but not
those SDK cache calls. Actual compile commands compile the unchanged SDK
`ppa_srm.c`, despite the generated DMA-source ownership option. Repair and
validation of that native hook are tracked independently from the PPA stall
experiment. Bulk M2C critical spans are a separate candidate for the earlier
Gallery descriptor-service deadline; no measured interrupt gap proves that
causality yet.

## Diagnostic7: controlled PPA observation

Diagnostic7 retains the diagnostic6 runtime and adds only a default-disabled
SDK wait journal and a narrowly eligible, volatile SRM bypass experiment. Its
marker is `2026-10-22 17:49:29 +0200`, config `0xaf0d55aa`, ELF SHA256
`018e8e09e5d14b25d8c2c752fdd222118be7eb72fe9a7b25733bca0d74aa7651`
and OTA SHA256
`b3c88f96405fed40caeae0a7eac69309e222f49ab590ea9bdb9aa286a5ee2ea0`
(7,779,792 B). The native PPA cache integration repair is deliberately excluded
from this image. The journal observes terminal DMA2D events and the original
blocking wait; it does not retire, cancel, reset or falsely complete an
operation. The bypass test changes only a subsequent unrotated, unmirrored,
1:1 RGB888 SRM operation whose calculated FIFO tail equals 1,536 bits.

The hash-checked OTA completed, and the independent boot review verifies 55
region captures, contour growth and hold, and the final Home image. Its bounded
UART extent has one planned software reset and no watchdog, DSI underrun or
DMA-invalid/recovery event. Existing startup errors/warnings remain recorded;
this is boot evidence, not production acceptance or a successful PPA A/B result.

The first auto-mode campaign completed its first cycle and the theme portion
of its second cycle without reproducing the PPA stall. Its second restoration
then failed the host cache-readiness gate. The original report remains failed.
Independent source review identifies an observability defect: that gate only
recognizes the boot diagnostic window, whose static logging budget expires
after four preparations. A fresh native prepared-window record and completed
accent batch are present, while the parser reports `window=None`. The native
`compressed-total` field includes raw slots; it is not JPEG-only consumption.
Separate forensic collection and a zero-write cleanup fresh-verify the original
six preferences. A new, separately tested gate must recognize the native
successful preparation record while preserving window, ordering, raw-slot,
ownership and sticky hardware-error checks. Neither this harness failure nor
one clean cycle establishes the proposed FIFO-tail workaround.

With the separately validated observation gate, three AUTO cycles, one FORCE
cycle and one final AUTO cycle complete on the same diagnostic7 image. The
five cycles preserve the frozen theme actions and restore all six preferences
and the three-slot Home window. All 55 JPEGs have separate visual review.
FORCE is actually exercised 391 times: 48 before its cycle and 343 during it.
AUTO adds no forced operations. Each campaign's independently bounded UART
slice has no watchdog, reset, core dump, PPA wait over one second, strict DSI
fault or other native error; intentional error-level numeric stats are retained
separately. The API verifies marker/MAC, with full ELF binding supplied by the
separate native and OTA/boot evidence. These bounds do not turn an absent
control failure into proof of the FIFO-tail hypothesis. No production bypass
change is admitted from this experiment.

## Diagnostic8 preparation

The next experiment adds the reviewed native PPA cache-hook integration repair
and a separate, default-disabled cache/DMA timing observer. It keeps cache
chunking and the normal FIFO-tail decision unchanged. The observer retains
356 B of fixed internal metadata, measures actual invalidation HAL bodies and
DSI callback/rearm spacing, and latches the first invalid descriptor before
existing recovery. It has no periodic task or ISR logging. Critical-body time
excludes spinlock acquisition and is not a complete IRQ-off measurement;
callback gaps are service spacing, not hardware-event-to-ISR latency.

Two private SDK translation units retain their original component targets and
basenames; shared SDK cache/DPI inputs are not replaced by the observer. Actual
native compile flags, source counts, IRAM/DRAM placement and generated code
must pass inspection before flashing. The first configuration rejects a schema
dependency on the platform name instead of the `display` domain. Its 13 inputs,
failed log and manifest are preserved. A separately reviewed one-file8.1 schema
overlay corrects that declaration and validates the required MIPI DSI platform;
full product configuration then passes. A subsequent native configure rejects
the external IDF component directory basename;8.2 corrects that packaging only.
The next compile exposes Windows backslashes in the added GCC response-file
include paths;8.3 expresses those four additions as normalized per-source
compiler options. Failed inputs and logs remain preserved separately. Neither
correction changes the runtime observer or product policy.

The successful native8.3 image has marker `2026-10-22 18:37:23 +0200`, config
`0x48815f00`, ELF SHA256
`6f2ae02d174372275679b1ff83404657a1a70851bdad037c5ef1e7ea910afe1d`
and OTA SHA256
`81ed147f67de7f37ae713214bfdd5184cd60f7dfb81dcc88869c76f0a15745cb`
(7,768,608 B). The common audit passes73 checks, including all11,631 frozen
fork sources,213 product inputs and the explicit overlay lineage. Separate
source/object/link audits verify the three real SDK PPA cache-call compositions,
the strong LVGL ownership hook, exactly two private timing translation units,
unchanged optimization/ABI flags, and the356-byte state in internal DRAM. The
observer's critical/ISR paths and timer calls resolve to internal IRAM/ROM.
These are static admission gates; production acceptance remains open.

The one hash-checked OTA finishes at `17:02:30Z`. Same-boot serial output binds
the device to ESP32-P4 revision1.0 and the exact new marker. All55 boot-region
captures and the final800×800 Home JPEG pass independent structural/visual
review: the line advances, holds and hands off to Home. Chunked region captures
can span presented frames and do not measure physical FPS.

The strict12-case application/theme/language matrix then completes with33 JPEGs
and restored preferences at `17:08:25Z`. Both explicit timing reads pass their
fresh-record and channel0 gates. Measured invalidation count rises from110,604
to1,176,419, but its cumulative maximum remains18,872 cycles at360MHz, or
52.422us, from a76,800-byte operation during boot. DSI callback count rises
from5,480 to44,459; cumulative entry spacing rises from11,429 to14,633us and
entry-to-rearm maximum from24 to25us. Neither read has a latched first fault.
These cumulative maxima cannot be assigned to a particular screen, are not a
hardware IRQ-latency measurement, and do not prove the initiating cause of the
earlier failures. They provide no justification for a global cache-chunking or
FIFO-equality workaround. The normal replacement image must remove all added
diagnostic state and repeat actual-device performance and stability validation.

## Final9 normal image: rejected

The plain product entrypoint is regenerated with the admitted8.3 runtime source
maps and no external diagnostic overlay. Real SDKCONFIG equals the generated
normal input before IDF expansion. The final graph compiles the original SDK
cache/DPI units, excludes coreDump and has no timing, PPA wait journal, FIFO
override or handler-profiler symbols. The native cache-hook repair remains
active. No global cache-chunking or FIFO-equality workaround is enabled.

The complete native build has marker `2026-10-22 19:09:31 +0200`, config
`0xbff84d70`, ELF SHA256
`8a9a5a84c89e0a5027cde0d3dedae12b2f03d803c3105945eded74118a8b6a77`
and OTA SHA256
`e9ebadba94eff189b43f3c05bde2d03e3f10ec56d6604552bff474b052743094`
(7,770,128 B). All79 original native checks,29 combined ownership/memory/PIE
checks and21 normal-only gates pass. A separate actual source/object/link audit
verifies the PPA hooks with diagnostics OFF. Frozen source manifest SHA256 is
`41f2367058202bc3c34d66949818d41ad4e5eff6421948a2e6aa29994ee7fdfb`;
preserved native manifest is
`1a258540ec6777c55404016afba35bb94d0b40a674d6d01bbde219d7935e03de`.

The single hash-checked OTA finishes at `17:20:34Z`. Its55 boot-region captures
complete at `17:21:08Z` and pass independent structural/visual review. The
subsequent matrix fails in Gallery, before its later scenarios or supplemental
performance/lifecycle tests can run. API first fault is `17:23:28.473765Z`,
corroborated by UART at `17:23:28.564665Z`. The first invalid descriptor has
tick172344, block count20402, event`0x2011` (invalid LLI, destination complete,
block done). Both descriptors have VALID clear and retain coherent source
addresses and next links. Existing recovery resumes real callbacks; it does not
make this a stability pass. No unplanned reset, watchdog or bridge underrun is
recorded in the independently frozen failed-matrix interval. Further sends and
routine restoration stop on the sticky fault. Separate read-only forensics and
explicit preference restoration retain the original failed verdict and counters.

Diagnostic8-versus9 is not an isolated diagnostic-ON/OFF experiment:8 first
decodes512×911 (padded512×912,933,888 B), whereas9 starts with1620×911
(padded1632×912,2,976,768 B), then requests the smaller prefetch.8 encounters
the large geometry only after a first image is already active. CoreDump removal
also reduces the normal per-core ISR stack from2,096 to1,536 B and removes its
task wrapper. Other audio/radio/cache/interrupt/optimization settings and
ownership setters match. None of these static differences proves causality.
A deterministic large-first workload and additional critical-section timing
remain required. Final9 is not accepted production firmware.

## Matched Gallery workload and critical-section investigation

The exact preserved diagnostic8 image is reflashed without rebuilding. A bounded
local fixture forwards the original JPEG bytes and presents one original metadata
object per request, forcing the failed9 large-first/small-prefetch order. The
original image parser otherwise chooses a random item, so merely returning a
two-item catalog would not control this variable. The fixture changes only the
runtime Immich server URL and saves all16 original settings privately.

Both actual decodes have the required geometry and active state:1620x911 with
active=-1, followed by512x911 with active=0. The native DMA counters remain zero.
However, the controller's8-second observation tail admits a third catalog
request; the two-asset fixture refuses it and the product retries the previous
URL. The controller therefore fails its exact-order assertion. This is a failed
bounded observation, not a firmware acceptance pass. A separate read-only
timing collection retains the evidence. Cache invalidation maximum is18,988
cycles at360MHz (52.744us); no first DSI fault is latched. An explicitly bound
cleanup then closes Gallery, restores the original URL with one write and
freshly verifies all16 original settings. The failed report remains unchanged.

The second image's approximately27-second served-to-decode delay is intentional
prefetch scheduling: decode is deferred until near the30-second slide deadline.
Its observed JPEG decode burst itself takes approximately106ms. This must not
be reported as a27-second decode regression.

A further external diagnostic10 overlay adds bounded, per-core measurements of
outer FreeRTOS critical sections, including caller PC, lock address and start/end
timestamps. It retains the original critical-section behavior, arms only after
timer initialization and latches both cores' records at the first DSI fault.
The combined fixed diagnostic state is968 B; no production allocation, task,
timeout, descriptor recovery or FIFO workaround is introduced. Host source and
collector checks pass. Actual native artifact, IRAM/DRAM and hardware admission
remain required; this observer does not establish a runtime fix.

Diagnostic10 compiles with marker `2026-10-22 19:46:30 +0200`, config
`0x5d82b0ea`, ELF SHA256
`b9308219ee46127cf02778cecd68b75375b4db9fbdd5b89b5a9636a9c64251a4`
and OTA SHA256
`3622bdce72a124b46e9bc54d1285373117f749e22673700aa1ca632c0e5d4475`
(7,771,616 B). All84 common gates and the independent three-unit source,
compiler-option, IRAM/ROM and968-byte internal-DRAM audits pass. Its55 boot
captures pass visual review. The short-tail deterministic pair then completes
with both actual decodes, zero DMA faults and all16 original Immich settings
freshly restored. These bounded passes do not override the next failure.

The subsequent full matrix fails again in Gallery, retaining18 JPEGs and stopping
all further routine sends. The first-invalid latch now provides an incident
timeline in device microseconds:

| Event | Start | End | Duration |
| --- | ---: | ---: | ---: |
| First core1 heap-info critical section |310828996|310837559|8563us|
| Real DSI callback/rearm |310837563|310837566|3us|
| Next core1 heap-info critical section |310837855|310846375|8520us|
| First invalid-descriptor callback |310846380|—|5us after unlock|

Both task critical sections use the same heap mutex and caller
`multi_heap_get_info_impl`; the subsequent active critical span belongs to the
current shared interrupt dispatcher, not the preceding task exclusion. The
measured DSI callback half-period is8372us. The second8520us exclusion therefore
crosses a descriptor-rearm deadline for this actual phase. Both descriptor VALID
bits are clear at the first event`0x2011`. Cache synchronization is inactive at
the latch, with a cumulative maximum of approximately56us. The critical observer
includes lock acquisition and work under that lock; it does not separate mutex
waiting from the TLSF traversal itself or measure every raw interrupt-mask path.

The source/API timeline places the failure immediately after the next artwork
update starts and before its HTTP response header. At INFO,
`ArtworkImage::log_state_("request-start")` still performs unused internal,
PSRAM and aggregate-largest-block queries, then acquires the retired-buffer
mutex, although its DEBUG message is compiled out. Actual ELF disassembly
confirms those queries. The two consecutive walks and phase align with that
specific diagnostic path; the observer does not retain its outer C++ stack.
Separate forensics preserve the first fault and a coherent post-recovery image.
The original preferences are explicitly restored afterward. Diagnostic10 remains
a failed matrix image, not production acceptance.

Two narrowly scoped fixes are prepared for controlled hardware comparison:
compile the entire artwork diagnostic body only when DEBUG exists, and avoid
LVGL's largest-internal-block walk when size or cheap aggregate-free checks
already reject internal placement. The latter retains64-byte alignment,
the4KiB preference ceiling,96KiB headroom and allocation fallbacks. Its headroom
observations remain advisory under concurrent allocation/free, as before;
the cheap added observation may conservatively choose PSRAM. Actual extracted
method tests cover40 diagnostic cases and14,784 allocator cases. No display
buffer, task, ownership or recovery policy changes. Hardware comparison and a
normal image without the observer remain pending.

The longer pre-reset record of rejected10 also contains a real bridge underrun
at `18:03:45.096116Z`, tick370925, after its first timing collection and before
the separate forensic screenshot and preference restoration. It is retained as
a second event, not dismissed as repetition of the first invalid-descriptor
counter. No cause for this later IRQ is inferred from the earlier latch.

## Controlled diagnostic10.1: two heap-query guards

The same observer,14 external inputs, SDK configuration, generated main,
compile commands and audio/display ownership configuration are retained. Only
the two reviewed CPP guards change. Marker is `2026-10-22 20:08:15 +0200`,
config `0x5d82b0ea`, ELF SHA256
`6f613061f529cd54798b0156d1b575fac457907d1ea4523f1be99cae9134b276`
and OTA SHA256
`70bbaf861dcbf9e99f2d3380c43d6709916310ecbd8c4c79ba443ee5aa796a82`
(7,771,488 B). The comparative native audit passes66 checks; the first audit's
metadata-only pyelftools error and original artifacts remain preserved. Separate
new-ELF audits confirm the same three SDK observers and968-byte state, an INFO
artwork diagnostic method reduced to a2-byte return, and native LVGL branches
that precede its expensive largest-block query.

The55 boot captures pass review. The matched large-first/small-prefetch pair
passes with the same real JPEG bytes, action sequence and all16 settings freshly
restored. Core1's maximum remains its original boot record4656us after the pair;
the unguarded10 maximum had grown from4574 to8551us during prefetch. This means
no newly completed core1 critical span exceeded4656us during this guarded pair;
it does not imply that all heap queries or interrupt exclusions disappeared.

The full12-case matrix passes with33 reviewed screenshots, correct color and
language restoration,3raw Home slots and no sticky DMA/DSI fault. Its largest
remaining core1 exclusion is8534us during `gallery-next-photo.jpg` capture,
between the paused and before-resume phases. The encoder explicitly asks for
the largest PSRAM block to plan a bounded output allocation. This is necessary
allocation planning, unlike the unused artwork DEBUG statistics. The recorded
caller does not supply a complete outer stack. An optimistic replacement
allocation was not promoted: a failed probe can invoke failure hooks or abort
under supported SDK policies even if a smaller allocation would have succeeded.
The read-only bitmap-query investigation also introduces no SDK/runtime patch.

A subsequent natural Gallery hold records110.019s with zero API requests,
screenshots or preference writes during the cadence,3 subsequent actual decodes
and3 completed transitions. End screenshots, native presentation counters,
healthy close, all16 unchanged settings and3raw Home slots pass. The following
timing read has no first fault and retains the same earlier8534us screenshot
maximum. These are bounded diagnostic passes. A plain normal build without
timing observers, PPA wait journal or coreDump must still pass native admission,
flashing and complete performance/lifecycle/stability validation.

## Normal11 hardware result

The normal image was compiled with marker `2026-10-22 20:32:14 +0200` and
config `0xbff84d70`. ELF SHA256 is
`0f8dcc6163460dcc7cd83fd5a057d2a25e32db06a3e03d4c79abee2ed7a4d88d`;
OTA SHA256 is
`58277ba99e84c2fd8390da2a4ce523ff5003bca9d00dbf961c827d87241881c5`
(7,770,000 B). Source manifest is `237c05ad…698c310`, preserved native manifest
`797daf3e…4d987a3`. The native audit passes 79 original, 29 combined and 26
normal/guard checks. Independent disassembly verifies the actual PPA cache
hooks, the INFO artwork return and LVGL's lazy heap-query branches. Timing
observers, critical-section probes, PPA wait journal, FIFO override and core
dump are disabled. No experimental display pool, extra task or raw screen is
introduced by these two final guards.

One hash-pinned OTA call succeeded. The 55 boot captures, full 12-case/33-image
matrix, 110-second natural Gallery cadence, three Camera cycles, held Settings,
three local playback cycles, real Voice startup, five software restarts with
Voice cleanup, repeated weather benchmark and 18 Home returns completed.
Screenshots and saved identities were reviewed separately from machine checks.
The Gallery cadence had no explicit helper API requests or captures, and
recorded three subsequent decodes and three completed fades. The 18 returns
contained no captures during the cycle cadence. The final 25-second health
check verifies restored original preferences, retains three raw Home slots,
and finds no application work/scroll allocation or Camera input allocation.
The final source PNG shows coherent blue/Polish rainy Home at 21:13.

The comparison below uses baseline18 and the final weather run after the fifth
software restart and its bounded Voice open/close. Gallery, Camera and Settings
were not opened during that final boot. This reduces cache-history differences;
it does not make heap fragmentation, network timing or live image content
identical to baseline.

| Measure | Sunny: baseline18 → normal11 | Cloudy: baseline18 → normal11 |
| --- | ---: | ---: |
| Accumulated LVGL handler wall per elapsed second, all selected windows | 49.72 → 21.07 ms/s | 15.11 → 10.38 ms/s |
| Windows without invalidation/flush | 57.14 → 12.18 ms/s | 9.62 → 9.21 ms/s |
| Task busy, median | 42.05 → 38.45% | 28.25 → 26.30% |
| Completed raster frames / firmware elapsed time | 48.857 → 48.830 FPS | 26.965 → 26.303 FPS |
| Free PSRAM | 4626 → 5940 KiB | 3949 → 5262 KiB |
| Free internal RAM | 30 → 49 KiB | 36 → 55 KiB |
| Largest PSRAM block | 2432 → 4608 KiB | 2432 → 4096 KiB |

The first row is a duration-weighted sum, not a median or time per frame:
sunny 622292 us / 12.515806 s versus 261804 us / 12.425321 s (12 windows each),
cloudy 234169 us / 15.500158 s versus 147770 us / 14.236801 s (15/14 windows).
Complete capture-free intervals and actual adjacent receipt durations are used;
the full analysis retains raw counters and sensitivity to reporting delay.
Raster FPS is not a physical-panel measurement. No selected raster report has
a missed publication.

There are explicit residual differences: cloudy raster throughput is 2.46%
lower, and its early no-draw phase is 10.03 versus 9.62 ms/s (+4.19%). A native
sunny refresh reaches 141 ms near the minute change. The first normal11 weather
run, after the application matrix/Gallery, has cloudy 16.63 versus 15.11 ms/s
and a 149 ms native peak; that earlier result remains preserved. Navigation's
separate stress maximum is 159 ms. These observations do not establish a
speedup for every window or identify the clock update as their sole cause.

Fixed idle allocations fall by 1,347,072 B (1315.5 KiB) of PSRAM and 15,872 B
(15.5 KiB) of internal RAM: Sendspin saves 570,880 B net PSRAM after moving
its three selected stacks, and Camera releases 776,192 B after stop. The
measured free-PSRAM gains of 1314/1313 KiB are separate evidence. In the matched
final run, JPEG cache is 885 versus 875 KiB and raw Home remains 5625 KiB.
The earlier post-application run had 1923 KiB of JPEGs. This is real occupied
memory: the shared 24-entry cache includes Home backing and application
previews, and settled stored results are compacted to their encoded length.
Its aggregate does not identify how much belongs to Home or Gallery. Cache
population and Q100 image entropy must not be confused with fixed-buffer growth.

Camera presents 258 frames over 16.881639 s (15.283 presentations/s), from three
fresh 5.604/5.631/5.647 s intervals. Active input capacity is 776,192 B and becomes
zero after each close; other retained Camera owners are not claimed to be zero.
Eight JPEG decode samples have median 41.456 ms, range 39.352–43.245 ms. Historical
live-content measurements are not an identical-input decoder benchmark.

The final image has no reported watchdog, panic, unplanned reset or DSI/DMA
fault in the completed campaign windows. The all-visual closure index
`normal11-all-visual-closure.json` (`79ebd031…654e24`) binds 12 separate reviews,
76 full-panel JPEGs and 55 boot-region captures. Whole closed-UART integrity
passes in `uart-session2-closed-normal11-independent-review/independent-proof.json`
(`9fd573c5…0916aa5`): all 4,083 chunks / 3,624,123 bytes match their offsets and
hashes, with one open/close and no reconnect or collector error. The collector
finishes at `2026-10-22T19:13:58.458087Z`. All 11 ROM banners map to six controlled
OTA changes and five normal11 software restarts. The current-image epoch begins
at `18:45:46.519594Z`; the following five resets are all planned and hash-bound.
The port is subsequently opened exclusively with DTR/RTS false and closed, with
zero data reads, writes or reset commands.

The combined closed-UART supplemental review
`final11-supplementals-closed-uart2-independent-review/independent-proof.json`
(`45d11a1d…96571e5`) verifies all eight supplemental campaigns and final health
against that one immutable collector copy: nine exact report windows, 653 API
marker/MAC observations, 40 original capture hashes and 241 zero-recovery
samples. Only the warm-start window contains the five planned resets. All
eight strict policies finish with no sticky fault or refused command. The final
quiet interval is 25.013 s with no commands/captures, and its three owner samples
retain 5409 KiB free / 4608 KiB largest PSRAM, with zero final free-memory delta.

The closed historical record refines rejected-image accounting: final9 has one
recovery; diagnostic10 has six recovery-counter increases retaining one sticky
first-invalid identity, plus the separate bridge underrun. A single retained
first latch is not proof of only one recovery. Earlier failed reports remain
unchanged; the timing observation at the first event is not assigned as the
cause of every later event. None of those historical faults belongs to normal11.

All results are bounded:
physical power-removal cycles and real Music Assistant/Sendspin playback were
unavailable; Gemini prepaid-credit exhaustion prevents successful provider
conversation and acoustic full-duplex validation. Local playback/AFE/microphone
transport and cleanup do not prove audibility or acoustic echo cancellation.
Publication is recorded separately from these runtime measurements.

Normal-image evidence under the local evidence root includes:

- `final11-preserved/manifest.json` on D: and `final11-ppa-cache-independent-audit`.
- `final11-boot`, `final11-matrix`, `final11-gallery-long-hold` and their separate reviews.
- `final11-camera`, `final11-held`, `final11-chimes`, `final11-real-voice`, `final11-warm-voice`.
- `final11-post-warm-weather-independent-performance-memory-review.json` (`890d5838…74110b`).
- `final11-camera-independent-elapsed-performance-memory-review.json` (`6e3b2e39…4dcf9a4`).
- `final11-snapshot-jpeg-accounting-source-review.json` (`6fec35c1…27b854`).
- `final11-post-warm-return-stress`, `final11-final-health` and their separate reviews.

## Local evidence

Evidence is under `C:/aeh-build/lvgl-ram-regression-20261022` and
`D:/aeh-build/lvgl-ram-regression-20261022`:

- `baseline18-weather`, `baseline-diagnostic2-weather` and their untouched logs.
- `priority-diagnostic2-aba1` and its complete-window analyses.
- `lvgl-source-validation-proof-v2-final.json` and `radial-pixel-final-arithmetic-proof.json`.
- `sendspin-memory-source-proof.json`, `sendspin-independent-three-owner-review.json`
  and `sendspin-native-package-closure-proof.json`.
- `camera-input-lifecycle-proof.json` and `camera-input-independent-source-review.json`.
- `candidate3b-source-manifest.json`; failed configure's source archives and log
  remain separate from every flashed image.

Prior cold starts belong to R25. Current physical power-removal testing remains
unperformed because the user was unavailable. The user also could not start an
isolated Music Assistant stream, so real Sendspin PCM/artwork receive/playback
testing remains unperformed. A successful Gemini conversation and acoustic
duplex remain unproved because the provider has exhausted credits.
