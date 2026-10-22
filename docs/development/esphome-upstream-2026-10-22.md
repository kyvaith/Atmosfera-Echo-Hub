# ESPHome upstream integration, 2026-10-22

This branch ports the product to ESPHome `2026.11.0-dev` and the official
recommended ESP-IDF `5.5.6`. Candidate18 passes the recorded automated device
campaign with explicit physical-start, acoustic and diagnostic limitations below.
The previously validated R25 checkpoint remains available independently.

Build13 is rejected after a real Voice watchdog restart, build14 after incomplete
application-preview restoration, build15 after a real DSI bridge underrun
while weather was running following a Voice close, and build16 after weather
failed to reacquire its render surfaces following Camera close. Earlier individual passes
remain valid only for their recorded scenarios. The historical Voice reset and
the build15 underrun have no proven initiating cause yet. Their rejected images
remain separate from the subsequently tested candidate18.

## Source identities

| Source | Commit |
| --- | --- |
| Previous product / R25 | `2903b1cad70d11d6010ee1f7877f2054a7dee51f` |
| Previous companion fork / R25 | `62806b28b7f216a70974e06c6520ae73fecd7cb2` |
| Official ESPHome at integration freeze | `7dace44d61e73a05f71df657bbf18d82a3d45890` |
| Initial integration merge | `f076d67f71ddfbd679d75a95adc23559321456aa` |
| Follow-up official merge | `cc62f65a9b6084ab5a5b960e8908f3170a29970b` |
| Product runtime migration | `7566a0f` |
| Build13 companion runtime | `bf12117b1c` |
| Candidate14 companion runtime | `65e1ad41e2b9622286ba2db6bb92342bdb6c2147` |
| Product PIE backport opt-in | `311ef6488721049ab282baaa591ad953c19e0199` |
| Candidate15 companion runtime | `863c431e076c57ec3284b5b9ad2a5d0257116ef4` |
| Candidate15 Settings allocation policy | `63c968bf27d616cf004efd07b258350a1eef70cc` |
| Candidate16 preference timing diagnostics | `9c8c189111a1af3dbbe7b1790a6f3c4e280cf0fc` |
| Candidate16 diagnostic opt-in | `461cf0578c4c19e54f2f1b38034e85b6afb7f5cb` |
| Candidate18 direct opaque allocation correction | `87e77c353b5979eeb7f44074c229585a2f20c4ea` |
| Final companion source and audit checkpoint | `d0b129d9002cea38083549fbbbf197e8819cc49b` |
| Final official refresh merge | `7a59858e70accb981cea4c667af5b7619b9bb793` |
| Fragmented JPEG output correction | `e2b85ce69f` |
| Bounded scroll partition correction | `4f9a2e7b48` |
| Home raw-window admission correction | `7ccaacc97a` |
| Background backing pause/drain correction | `0ec0a3504d` |
| Bounded Home JPEG preparation recovery | `82025d7e41` |
| Allocation-stage JPEG diagnostics | `bf12117b1c` |

Official ESPHome uses `dev` as its default branch. The companion history contains
all 2,904 official commits since the common ancestor plus the complete previous
fork history. Both input heads are ancestors of the integration; no squash or
forced history replacement is used. The fork's
`docs/upstream-sync-2026-10-22.md` and two CSV inventories record the subsystem
audit, all 423 original fork paths and all 2,904 official commits.

## Product migration

- Use `codecs: [pcm]` for the official Sendspin role and retain the optional
  `supported_channels: [1]` extension for the physical mono output.
- Use the official `micro_wake_word` implementation, which now provides the
  configurable capture duration itself. The product keeps its existing 1,000 ms,
  confirmed in both generated R25 and candidate firmware.
- Preserve the official P4 main-task stack fix: 8,192 bytes rather than the
  previous product override of 4,096 bytes.
- Select ESP-IDF `5.5.6` explicitly. The default-off cache restart, SDMMC error
  preservation and Hosted shutdown extensions accept only the exact reviewed
  `5.5.5` and `5.5.6` releases. Unknown sources or versions are rejected.
- Keep one coherent companion component tree. The default relative source path
  expects the product and `kyvaith-esphome` directories to be siblings.
- The camera source picker uses the companion's explicitly owning dynamic-option
  API. Its copied source names remain valid until the next picker refresh; they
  are not borrowed from the temporary catalog result. The reusable widget owns
  this storage on the LVGL task, without retaining camera URLs.
- Keep upstream LVGL image-format pruning and declare the formats actually
  published by Lottie. Native transparent loaders need premultiplied ARGB8888;
  opaque canvas handoff can need XRGB8888. Direct presentation ownership stays
  unchanged.

The screen remains RGB888 with two LVGL DIRECT buffers and three display-owned
DSI buffers. No additional full-screen surface or independent physical I2S owner
is introduced by this migration. TDM microphone/reference alignment, on-demand
AFE/AEC, direct animations, navigation, snapshots and product UI policy remain
owned by their existing components.

Official standard-I2S duplex and microphone resampling are included in the fork
and have a separate native P4 compile scenario. They do not replace the board's
four-slot TDM and aligned AEC reference. The standard mixer, speaker resampler,
native assistant, wake-word and Sendspin foundations use current upstream code.

## Isolated validation paths

The normal short Windows build directory is
`C:/aeh-build/${name}-productization-idf556`. Override both paths when validating
an isolated companion worktree:

```powershell
python -m esphome --toolchain esp-idf `
  -s esphome_components_path C:/aeh-build/upstream-sync-20261022/esphome/esphome/components `
  -s firmware_build_path D:/aeh-build/upstream-sync-20261022/firmware-idf556 `
  compile atmosfera-echo-hub.yaml
```

Use the candidate's own Python environment and pinned dependencies. An older
editable ESPHome installation can otherwise load a different component tree.
Private `secrets.yaml`, build output, raw device logs and downloaded caches stay
outside source control.

## Validation record

At the integration freeze, the combined focused Python suite passed
**1,540 tests with two skips**. All 91 Python files changed relative to official
`dev` pass Ruff. Two additional native ESP-IDF 5.5.6/P4 builds pass: hardware and
software image paths, and official full-duplex I2S with 48-to-16 kHz microphone
resampling. These smoke images were not flashed. Four new C++ ownership tests
remain unexecuted because their official runner skips Windows.

The subsequent memory and ownership corrections pass 68 additional focused tests. These
compile and execute the production JPEG planner, scroll geometry and admission
helpers on a Windows C++ host, plus source/ownership checks. Thirteen of these
execute the actual background-refresh function with host ownership fakes, testing
timeouts, nested leases and every storage/restore failure exit. The geometry sweep
covers all 637 legal viewport positions; these tests do not emulate FreeRTOS,
PPA or JPEG DMA. The final official API refresh additionally passes 145 API component tests, including
29 optional/default-argument cases. The real product keeps all 51 actions as
required-argument actions and does not enable the optional-argument feature.
The external device harness additionally tests rejection of the actual failed
one-slot Home endpoint and of an incomplete cache after restoring preferences.

The subsequent guarded PIE backport has a separate 67-case campaign: 43 new
schema/codegen and two-file replay cases plus existing restart/SDK guard cases.
These verify exact official enabled regions, byte-identical disabled owners,
idempotence, refusal before mutation and rollback of partial writes. They do not
establish the cause of the first Voice13 watchdog reset. Its exact libraries,
FreeRTOS sources and local TCB layout were independently checked; no unsupported
old-task or notification-slot replacement was made.

The full product build, exact flashed identity, screenshots, matched performance,
audio/application scenarios and restart evidence must be recorded below before
this integration is described as accepted. R25's earlier hardware results do
not validate the merged firmware. Provider-dependent Gemini conversation tests
remain separate from on-device audio and Voice UI checks.

The rejected build13 native product build passes with ESP-IDF 5.5.6. Its immutable marker
is `2026-10-22 12:20:30 +0200`, configuration hash `0x2dbfddd5`.
Its artifact audit passes all 79 checks: 500 copied source files match the
fork and three headers are generated; all 16 reviewed MIPI SDK postimages match;
the linked reset sequence is in IRAM with both cache fences. Hosted 2.12.13's
callback ABI is 284 bytes with the restart member at offset 268; both caller and
library DWARF agree, and the ELF initializer points to the actual SDK restart.
Factory merging preserves the four native flash segments, partition layout and
NVS. Flashing and hardware acceptance are still separate from these checks.

| Artifact | SHA-256 |
| --- | --- |
| ELF | `fd77af1e67f2112a483e4e61152836ecd76a83ab2c4159ec42bb40e1dc3f1549` |
| Factory | `933611d86e414e94b422fab61ba34896bad40d8e56e1323800a1d0ccc179c6a8` |
| OTA | `fd9c8797443e7d2515d66047cdc3c514aefbcf11288b8f7059fce90f2e3ca561` |

## Candidate18 direct opaque allocation correction

The unscaled compact direct opaque Lottie path now omits its unused fourth
display back buffer. The immutable native canvas and two private raster/PPA
targets remain distinct. The first prepared frame and finite retention use
existing hardware conversion; live publication, recoloring, hidden-region drain
and resource release retain their owners. General and scaled paths keep their
existing back buffer. The weather allocation is reduced by 589,824 bytes without
reducing resolution or changing pixel quality.

Sixteen host C++ cases execute the production allocation and lifecycle branches,
including an actual queued source, refusal while in flight, its completion
callback, finite retention, recoloring and cleanup. All pass without skips, with
an independent source/lifetime review. These fakes do not emulate FreeRTOS or
physical PPA/DSI timing. Preliminary build17 copied an earlier version of the
guard and was never flashed; its provenance record remains separate.

Native18 uses companion `87e77c353b5979eeb7f44074c229585a2f20c4ea` and product
`461cf0578c4c19e54f2f1b38034e85b6afb7f5cb`. The complete ESP-IDF 5.5.6 build,
79 strict artifact checks and independent exact PIE-linked instruction check
pass. Static internal RAM remains 281,296 bytes. Marker is
`2026-10-22 14:08:01 +0200`, configuration hash `0x903d0abd`.

| Native18 artifact | SHA-256 |
| --- | --- |
| ELF | `5e8d6baa04d729bb988c15f64df62351f0538f10a20eb85718115415150b87ea` |
| Factory | `818c372f2446c32b59805bf19df4ddb006868ae66c7bba2c426e8ae99c6b7ebe` |
| OTA | `99e88080cc805a2fd06e08f8e50cc9c4d0a00d97d1857c398871421c6034c1a3` |

OTA completed in 59.96 seconds transfer / 61.08 seconds total. Hash-verified UART
captured one planned software reset and successful boot, with TDM/reference and
the local chime initialized. All 55 boot-region samples and the final Home were
reviewed. The sampled stroke advances and retains its completed phase; a
nonatomic capture crossing the final handoff does not prove a physical tear.

Matrix13 completes all twelve machine scenarios and preference restoration.
Its separate full-log contract audit passes and all 33 saved screenshots were
reviewed. The four original and Amber Home pages, Player, Settings, synthetic
Voice UI, Gallery, Camera and alternate-language/restored-Polish Home remain
coherent. Final Home retains three raw slots and a completed application-preview
batch. A single raw-slot admission probe fails and then recovers by releasing
1,686,601 bytes from five eligible previews; this is not a zero-allocation-error
claim. There are no Lottie back-buffer failures, JPEG `NO_MEM`, unexpected resets
or actual DSI IRQs in this bounded matrix.

After Camera closes at 12:15:42.984665 UTC, the weather task starts at
12:15:43.616160; its next sample reports 46 raster frames and 45 regional
submissions with no publish misses or composition failures. Weather uses
1,792 KiB. This establishes resumed work beyond a still screenshot, not physical
scan-out FPS. Settings' later internally owned contiguous path reports roughly
31.15 ms render wall time; the separate paired comparison below uses an attached
contiguous loan on both images.

The fixed 130-second NVS/weather campaign completes 32 Home transitions and
observes two real successful commits, lasting 12,377 and 4,931 microseconds and
writing four entries in total. No DSI IRQ or fatal event is observed, and the
original switches/live weather are restored. Object-not-presented diagnostics
during alternating Home pages remain recorded; these counters do not prove
continuous visibility or physical FPS. The main matrix also contains a successful
139,611-microsecond commit without an observed IRQ; its latency is not discarded.

Held Settings at Y=336 and Y=186 passes actual manual-owner and fresh source-Y
checks. Four images are coherent; the single scroll surface is released on
close and three raw Home slots return. The supplemental Camera test retains
source 0 and advances presentation 652 to 793. Its three images are coherent;
two actual sleeping-Home backing refreshes occur after close, and original
backlight/brightness are restored. This does not test every camera or visually
validate the picker list.

Three embedded chimes each complete an actual PLAYING-to-IDLE cycle through
the official audio-file/resampler/mixer path. A single rapid real Voice launch
after the full pressure sequence activates AFE, opens the microphone/stream,
then closes without watchdog or DSI failure. The current provider returns
`Gemini: prepaid credits exhausted`; successful dialogue, acoustic duplex and
numeric reference alignment are unproven. One weather publication rejection
during cleanup remains preserved; the same renderer subsequently accepts and
drains its pending regional frame, retains frame 309 and refreshes Home. Its
precise rejected admission predicate and native mailbox acknowledgment were not
logged. Original mute and diagnostic switches are restored.

The matched Settings comparison temporarily flashes the untouched R25 OTA and
then returns to the exact same candidate18 OTA without recompilation. Both use
the same frozen three-gesture helper, 55-sample boot capture and at least 30
seconds of post-capture settling (actual intervals 39.83/41.36 seconds). Both
attach the same 2,297,600-byte one-piece surface with zero failed frames. Final
cumulative render wall averages are 31,941 to 31,114 microseconds, 2.59% shorter
in this paired run; this is not a CPU, physical-FPS or statistical claim. Four
Settings stills and both boot Home images are coherent. Missing row glyphs and
subtitle clipping are present in R25 too.

The final matched weather run repeats two scenes and six Home returns. Twelve
regular windows per scene give sunny 47.619 to 47.898 rendered FPS and vector
weather 26.016 to 26.693, with zero publish misses in both versions. All 82
candidate `dsi_under` samples are zero. Four images show intact clock, weather
and normal Home controls. Initial inline JPEG previews falsely appeared to omit
parts of the UI; lossless decodes of the unchanged files confirm the full pixels
in these images and the earlier R25 restored reference.

Stable task-profiler CPU snapshots are slightly lower: sunny busy 43.4/44.0%
to 42.5/42.9%, cloudy 30.8/30.4% to 28.5/28.6%. Final cloudy free PSRAM is
4,316 to 3,950 KiB, largest block 2,816 to 2,112 KiB, and free internal heap
57 to 40 KiB. Lower memory headroom remains a real cost despite the removed
576 KiB Lottie allocation; the bounded Sendspin cost is documented below.

The median `perf1s loop=` counter increases from 5,901 to 43,952.5 microseconds.
Its identical production timing block accumulates wall time inside
`lv_timer_handler` minus flush time over the reporting interval. It measures
neither one ESPHome loop iteration nor FreeRTOS CPU runtime. Draw waits, mutex
waits and callbacks are not timed individually, and the new outer App delay is
outside this measurement. No particular wait cause is proved. Preserve this
unresolved counter increase rather than claim global absence of performance
regressions from the healthy rendering and CPU results.

Five controlled warm starts each complete one real Voice session. The bounded
UART campaign contains exactly five software resets, five successful boot
checkpoints and five actual session starts, with the complete retained ELF hash
matching candidate18 on every cycle. No additional reset, watchdog, DSI IRQ or
allocation failure occurs in that span. Each boot starts muted; the original
four switches match a fresh final readback. Final Home retains three raw slots.
One callback-timeout warning in cycle4 remains recorded; the same renderer later
completes its regional frame, retains frame 309 and refreshes Home before the
next planned reset. This is observed recovery, not proof of its initial cause.

The final JPEG briefly appeared incomplete in the inspection tool. Decoding the
unchanged original into a lossless PNG proves identical RGB bytes with the full
cloud, condition chip and controls. Both that PNG and two later untouched Home
captures show the complete UI, without navigation, wake or cache-regeneration
commands. This inspection-path discrepancy does not establish a firmware fault.

These results do not establish the cause of the historical Voice watchdog and
DSI underrun.
The user cannot perform physical power-removal tests now; R25's earlier five
cold cycles are not reused as candidate18 evidence.

## Rejected candidate16 diagnostic checkpoint

`preferences.sync_diagnostics` defaults to false and can be enabled only on
ESP32; false/default remains valid for every existing platform. The product
explicitly enables it to correlate completed preference work with the DSI IRQ
tick. One INFO line follows each nonempty sync, recording begin/end RTOS ticks,
64-bit microsecond times, aggregate cached/written/failed counts and the commit
result. It logs no preference keys or values and changes no interval, NVS order,
empty fast path, cache guard or return result. End clocks are sampled before
printing. This is an observation mechanism, not a claimed underrun fix.

The independent preference campaign passes 93 checks, including 16 executions
of the actual C++ sync function with diagnostics enabled/disabled and existing
storage regressions. All 94 changed Python files relative to the frozen official
target pass Ruff. Fresh factory configuration validation also passes with the
five CI-only placeholder keys. Native16 passes all 79 strict artifact checks
and the independent PIE-linked instruction check. The generated diagnostic
define is enabled, the interval remains 60,000 ms, all 51 compiled action tables
are unchanged, and static internal RAM remains 281,296 bytes. Marker is
`2026-10-22 13:42:31 +0200`, configuration hash `0x903d0abd`.

| Native16 artifact | SHA-256 |
| --- | --- |
| ELF | `048c70eb7759f4cbfdda19444027247f4d877ff292bda72efd46bd576ef033e8` |
| Factory | `84f5f0e7b61d937b961115baf95593ac62bda3a38aab705e06d97c4eb210bead` |
| OTA | `c0b41c8293403931b0b539d89235e8d29dc714e1b324de7ff3fd4ed3ade5a872` |

OTA and the hash-verified UART boot succeeded. All 55 boot-region samples and
the final Home were reviewed. Matrix12 completed its twelve machine scenarios,
restored the original preferences and three Home slots, and saved 33 coherent
screenshots. Its independent audit nevertheless rejects build16: 21 real
`Display back buffer alloc failed: 589824 bytes` errors occurred after Camera
closed. The retained still weather image hid the missing resumed animation.
The retries released their three temporary surfaces; this is not evidence of
21 accumulating leaks. A later weather restart does not clear that unsampled
failure interval.

A separate fixed 130-second weather/navigation campaign completed 32 Home
transitions and observed two real nonempty NVS syncs, lasting 5,451 and 4,908
microseconds, each writing one entry without failure. No DSI IRQ was recorded.
Original switches and live Home Assistant weather were restored. This bounded
result does not repair or establish the cause of the earlier build15 underrun,
and it does not override build16's weather allocation rejection. Whole-device
acceptance remains pending.

## Rejected candidate15 checkpoint

The native build of companion `863c431e07` and product `63c968bf27` passes
with marker `2026-10-22 13:21:34 +0200`, configuration hash `0x101c805b`.
All 79 strict native artifact checks pass. The independent ELF verifier again
confirms the exact official PIE save/restore instructions and unchanged save-area
layout. Static internal RAM is 281,296 bytes, 10,650 bytes below exact R25 and
16 bytes above build14. This is a static section comparison, not free heap.

| Artifact | SHA-256 |
| --- | --- |
| ELF | `bad582c892d0111ed4f6ac5b0c782e69a103933dd5889b54be1eba15b36b9436` |
| Factory | `b93ff151046ebd9dd54636d547c147b9da9923488490483868e29ca24997eec5` |
| OTA | `291ca5bb604d9110277abc7e8e04b23bb39af21db613dbe6f4c327a9ce4ae298` |

After a completed encode, if both allocations for a compact owned JPEG fail,
the codec can shrink and transfer only scratch owned by that call. The old
caller output remains intact if shrinking fails; borrowed reusable scratch
keeps its original contract. The SDK has completed DMA and payload cache
synchronization before this branch. No additional cache invalidation, quality
reduction, raw frame, eviction or retry is introduced. Twenty host cases execute
the actual publication branch, including moved/failed reallocations and both
normal and nonencrypted PSRAM capabilities; the combined memory/ownership
campaign passes 88 cases without skips.

Settings now uses the existing Home trim operation before attempting its
contiguous loan. A counted regional drain protects the operation; only idle
neighbour raw slots are released after their dirty JPEG backing is saved. The
current Home close source remains resident. Successful trimming invalidates the
four product window metadata fields. The list releases its scroll surface and
returns/releases the Gallery loan before the existing navigation owner rebuilds
three Home slots; a deferred product refresh synchronizes the metadata. The
nine-piece fallback remains available when a contiguous loan still cannot fit.
Final device measurements must distinguish those two paths.

Fresh tracked-product archive validation with five CI-only placeholder keys
passes for the factory configuration. It is config validation only, not a
factory build or an executed GitHub workflow. OTA succeeded in 59.83 s transfer,
60.94 s total. Hash-verified UART captured one planned reset and a successful
boot checkpoint; all 55 regional samples and the final full Home were reviewed.

Matrix11 is FAILED. Seventeen actual screenshots were reviewed without a new
visible artifact, but the synthetic muted Voice case recorded a real bridge
underrun at tick 137278 (`total=1`, `brg=0x00000001`). The Voice close frame
trace had completed approximately 5.5 seconds earlier; weather had resumed and
was publishing normally. No JPEG NO_MEM, completed-scratch recovery or sleeping
Home refresh was logged in that interval. The first Settings opening had
successfully drained/trimmed and attached its exact 2,297,600-byte contiguous
loan; it had returned that loan and rebuilt three Home slots about 20 seconds
before the IRQ. These timings do not establish the underrun's initiating cause.
Later matrix cases, final restoration, matched performance and warm Voice/reset
campaigns were not completed on this image. Physical cold starts remain
unperformed because the user is unavailable.

## Rejected candidate14 checkpoint

The fresh native build of companion `65e1ad41e2` and product `311ef64887`
passes with marker `2026-10-22 12:53:55 +0200`, configuration hash
`0xf55a982f`. The strict native artifact audit again passes 79/79 checks.
A separate independent ELF verifier proves the exact official 82-byte save and
78-byte restore sequences in the actual IRAM PIE handler, absence of the old
sequences, and the unchanged 216-byte PIE/24-byte general save-area layout.
The real guarded SDK owner hashes and enabled Kconfig flag also match.
Static internal RAM is 281,280 bytes; the footprint is two bytes above build13.

| Artifact | SHA-256 |
| --- | --- |
| ELF | `88254e8e5a89de23187688eada4eb7b00b08d934d87f6a6098d3e52475f3336a` |
| Factory | `f59396ae651e5d6d080d3f48df56740d15577c79e65cd3cfad6a1d406364adc2` |
| OTA | `a3532623871d4b4e89059a9a17cd8086b53398a8259caf67db770db141d23248` |

| Current-image scenario | Result |
| --- | --- |
| OTA, exact marker/MAC, boot checkpoint and boot screenshots | Passed; transfer 63.89 s, total 65.00 s; all 55 regional samples and final full Home reviewed |
| Real rapid-unmute Voice attempt | One fresh-boot attempt completed without a reset; AFE and microphone running observed, then provider-credit failure; this does not clear the earlier failure under the full high-pressure sequence |
| Complete matrix with post-restoration readiness | FAILED: matrix10 passed twelve sampled cases and 32 reviewed images, but final application previews remained pending after restoring the original preferences |
| Held Settings and Camera/sleeping-Home supplements | Not run after this image was rejected |
| Three embedded playback cycles | Not run after this image was rejected |
| Matched R25 performance comparison | Not run after this image was rejected |
| Five controlled warm restarts, each with a real rapid-unmute Voice attempt | Not run after this image was rejected |
| Physical cold starts | Not run: user unavailable. Earlier R25 cold cycles do not validate this image |
| Successful provider conversation / acoustic duplex | Unproved: backend reports exhausted Gemini credits; no independent sample-bearing/AEC measurement |

Build14 is rejected for complete acceptance. Its saved restoration log records
eleven JPEG `ESP_ERR_NO_MEM` results, all at `stage=owned_copy`: the encoder
already held the complete 148,995- or 153,606-byte image in a 1,048,448-byte
scratch allocation, but a separate compressed-image allocation failed. Aggregate
free PSRAM was approximately 1.08 MB while the largest block fell to 139,264
bytes. The Home window was ready with three raw slots; application previews
remained `apps=0 pending=1` through the strict 30-second restoration deadline.
The Home-only admission retry cannot repair this application-preview path.
The original failed report and all 32 actual screenshot files remain unchanged;
there is no final restored-Home screenshot. No DSI underrun or fatal error was
observed in the saved matrix span. This does not make the failed cache ready.

## Rejected build13 device record

| Scenario | Build13 evidence |
| --- | --- |
| OTA and running identity | Transfer 60.09 s, total 61.20 s; exact `12:20:30 +0200` marker and device MAC confirmed |
| Fresh boot | Contiguous hash-verified UART prefix, 10:25:33.093–10:26:35.699 UTC; completed boot chime and successful-boot checkpoint, no fatal or underrun |
| Boot visuals | All 55 regional samples plus final full Home reviewed; stroke growth and retained final phase visible. Samples are chunked/non-atomic, not display FPS |
| Complete matrix9 | Twelve cases, 33 screenshot files and 309 exact-image identity checks; every original/accented page, weather freeze/return, Player, Settings, synthetic muted Voice, Gallery and actual Camera presentation |
| Original preferences restored | Fresh window 1–3 `prepared=1`, later `home=1 apps=1 pending=0`, three raw slots (5,625 KiB), and readiness checked again before/after the restored capture |
| Nine-piece Settings | Actual held manual-snapshot frames at Y=336 and Y=186, fresh source/ownership gates, four reviewed captures and nine clean boundary strips |
| Camera picker / sleeping maintenance | Source index 0 retained, presented counter 672 to 855, three reviewed captures; verified backlight-off input followed by actual sleeping Home refreshes on pages 2 and 3, no underrun; original backlight and logging restored |
| Local playback | Three embedded chimes each reached PLAYING then IDLE; no logged audio anomaly; audibility is not independently recorded |
| Real Voice attempt | FAILED: AFE activation followed by HP_SYS_HP_WDT_RESET at 10:34:39.782 UTC; no printed initiating panic/backtrace. Original mute/logging preferences subsequently restored in a separate verified connection |
| Matched performance | Not run after this image was rejected |
| Five controlled warm restarts | Not run after this image was rejected |
| Physical cold starts | Not performed on this merged image; user unavailable. The five earlier R25 cycles are separate evidence |

The full matrix log includes one recovered 1,920,003-byte raw-slot allocation
failure followed by reclamation of 1,481,589 bytes from four idle application
previews and a successful complete-window retry. An earlier JPEG result 259
(`INVALID_STATE`) recovered through its existing bounded retry; this is not an
observed JPEG NO_MEM. Three accent batches needed a second bounded attempt to
finish application previews. The final restoration completed on its first batch.
No JPEG NO_MEM or nonzero DSI underrun/bridge/fatal diagnostic occurred in this
campaign. The new JPEG-NO_MEM reclamation branch therefore has host execution
coverage but was not forced on the device. Duration/late-frame warnings remain
performance observations, not a claim of perfect frame cadence.

## Preserved rejected hardware attempts

The initial merged image built and flashed, but matrix3 exposed persistent
JPEG scratch allocation failures and a Settings surface whose two halves each
needed about 1.15 MB of contiguous PSRAM. The next candidate removed those
observed failures; matrix4 nevertheless remained rejected because Gallery's
return left Home with one of its three required raw slots. The original machine
report did not assert that invariant. Independent log review found 46 failed
full-window reservations, and the final harness now rejects that state.

The fixes preserve pixel quality and ownership: bounded row-aligned Settings
pieces, capacity-aware JPEG scratch, and one admission retry after releasing
only eligible idle compressed app previews. They do not evict Home backing or
an active close source. Matrix4 used a contiguous Settings surface; it does not
prove segmented hardware rendering. The final candidate requires fresh device
coverage of that path and complete Home recovery.

Before the final API refresh, the first OTA attempt of the preceding image
(marker `2026-10-22 10:55:19 +0200`) rolled back to the preceding image.
USB disappeared during the early-boot observation window. A read-only ROM/stub
check confirmed the entire app0 payload MD5 matched the prepared image and OTA
metadata marked that attempt ABORTED. No new-image marker or initiating panic
was captured in that gap. A second OTA with a UART observer that does not reopen
a disconnected port started that exact image and completed its boot trace.
This does not prove the observer caused the earlier reset. Overlapping normal
and Hosted restart requests were observed in both attempts; they alone do not
explain why only the first rolled back. Preserve this event and distinguish
successful later campaigns from a claim that its cause has been resolved.

## Preserved background-refresh rejection

Build11 (marker `2026-10-22 11:28:27 +0200`) passed the complete 12-case
matrix7, including all three Home slots, 33 images and nine-piece Settings.
Its supplemental same-source camera test nevertheless remains failed: one DSI
bridge underrun appeared after Camera closed, alongside a sleeping Home backing
refresh and resumed weather. The source refresh algorithm and product interval
were identical to R25; that does not establish the new binary was unaffected.
No panic or ownership violation was captured, and correct camera stills do not
clear the diagnostic failure.

Source review proved that this backing-maintenance path lacked the required
regional drain at every nested level. The final guard acquires one nested pause
from the page's LVGL component before modifying any raw slot or codec state.
It holds that lease through JPEG work and borrowed-slot restoration, refuses a
120 ms timeout, and balances only its own lease on every return. It adds no raw
surface, allocation, CPU-copy fallback or product coordinates. Host ownership
checks establish this contract; fresh final hardware evidence must separately
assess the observed starvation scenario.

Two initial supplemental attempts exposed test-tool mistakes: requiring regional
pause depth for a retained scroll snapshot, and using a generic application
helper that closes Camera before testing its picker. Those failed reports remain
unchanged. Corrected tests require actual snapshot ownership and fresh source Y,
or an open streaming Camera with same-source presentation progress, respectively.
They do not weaken the DSI failure checks.

## Preserved post-restoration cache rejection

Build12's matrix8 passed its twelve sampled scenarios and retained three raw
Home slots, but the subsequent restoration of the original accent/language
emitted seven real JPEG `ESP_ERR_NO_MEM` results. Its latest window ended
`prepared=0`, and its accent batch ended `home=0 apps=0 pending=1`. The correct
restored still did not establish a usable regenerated cache. That complete
acceptance remains rejected; its original machine report is preserved.

The final candidate gives one synchronous Home preparation a local recovery
budget. An actual JPEG allocation failure may release eligible idle application
previews and retry the same source once, only if bytes were freed. Active
navigation applications, Home backing, close sources and worker readers remain
protected. Background and worker paths receive no recovery context. Previous
JPEG bytes survive a failed replacement. Twenty new checks exercise these
boundaries, including a JPEG-disabled compile/run case, within the 68-case suite.
Error-only stage diagnostics distinguish engine, input, scratch, SDK processing
and owned-copy failures; the older generic error cannot establish which failed.
The external final matrix now also requires a fresh completed cache batch and
three raw slots after restoring the original preferences.

## Initial matched runtime comparison

The R25 and initial candidate run the same two weather scenes and six Home returns.
These are rendered animation counters, not panel scan-out FPS. The regular
capture-free windows show no missed publishes in either firmware.
These measurements precede the memory corrections and do not validate the final
candidate; a new matched run remains required.

| Scene | R25 | Candidate |
| --- | ---: | ---: |
| Sunny rendered FPS | 47.62 | 48.23 |
| Vector weather rendered FPS | 26.02 | 26.84 |
| Final cloudy scheduler busy samples | 30.8%, 30.4% | 28.7%, 28.9% |
| Cloudy free PSRAM | 4,316 KiB | 3,300 KiB |
| Cloudy free internal heap | 57 KiB | 32 KiB |

The higher `perf1s loop=` value measures wall time inside the handler minus only
explicit flush time. It includes preemption and mutex/queue waits; it is not
scheduler CPU consumption. The measuring code is unchanged. The changed wait
distribution was not individually traced, so no specific wait is attributed.

The lower memory headroom is a real, bounded upstream tradeoff. Sendspin 0.9.3
uses a 1,331,472-byte shared inbound ring and eagerly reserves 262,144 bytes for
artwork assembly. Compared with the old 600,000-byte audio ring before lazy
artwork allocation, persistent storage increases by 993,616 bytes (970.33 KiB).
This explains most of the measured roughly 1 MiB residual increase. Do not
silently reduce negotiated artwork capacity or replace the new protocol's
buffering with the old ring. Gallery/camera peak-memory and release tests remain
part of acceptance. Current measurements do not establish a monotonic leak.

LVGL style-cache fields add roughly 4–6 KiB to the existing static widget tree;
the preserved official P4 main-stack fix adds 4 KiB of internal stack. Compiled
build15 static internal RAM decreases by 10,650 bytes overall versus the exact
R25 ELF section accounting. ELF/debug file growth is
not a measurement of heap use.

Raw local evidence for this work is under
`C:/aeh-build/upstream-sync-20261022` and
`D:/aeh-build/upstream-sync-20261022`; the untouched R25 build remains under
`C:/aeh-build/atmosfera-echo-hub-productization-idf555-late-hs`.
