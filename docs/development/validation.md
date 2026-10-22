# Validation and regression testing

Every runtime change must be validated at the layer it affects. A clean
configuration and successful compile are necessary, but display ownership,
cache coherency, touch arbitration, audio timing, and memory lifetime require
hardware testing.

## Test levels

| Level | Purpose |
| --- | --- |
| Schema/config | Catch invalid YAML, missing IDs, and component dependency errors |
| Focused component build | Catch feature guards, framework versions, and isolated compile failures |
| Full firmware build | Catch integration, partition, IRAM/DIRAM, and generated-code issues |
| Flash/boot | Validate bootloader, IDF, panel, codecs, and persistent settings |
| Scenario test | Validate visible behavior and lifecycle |
| Stress test | Expose races, fragmentation, starvation, and stale ownership |

## Product commands

Run from the product checkout with the intended ESPHome environment active.

Configuration validation:

```powershell
python -m esphome --toolchain esp-idf config atmosfera-echo-hub.yaml
```

Complete compile:

```powershell
python -m esphome --toolchain esp-idf compile atmosfera-echo-hub.yaml
```

USB upload:

```powershell
python -m esphome --toolchain esp-idf upload atmosfera-echo-hub.yaml --device COM5
```

Serial logs:

```powershell
python -m esphome --toolchain esp-idf logs atmosfera-echo-hub.yaml --device COM5
```

Use a factory image when bootloader, partition table, flash mode, or
framework-level DSI behavior changed. A normal app upload is sufficient for
ordinary YAML and component code changes when the partition layout is
unchanged.

## ESPHome component checks

When changing the companion ESPHome fork:

1. Read its root `AGENTS.md`.
2. Run formatter/linter only on changed files.
3. Run the focused component tests and target compile configurations.
4. Verify both native ESP-IDF and the supported ESPHome schema path.
5. Do not rely on PlatformIO-only flags or pre-build patch behavior.

At minimum, test a component with optional acceleration disabled and enabled
when its schema exposes that choice. Reusable components must compile without
the Atmosfera product configuration.

## Required hardware regression matrix

### Boot and display

- Five cold power boots.
- Five software restarts.
- Backlight remains off until the first valid frame.
- Boot Lottie starts from the expected first frame and reaches the final
  ESPHome mark.
- No blue/black flash during boot-to-Home handoff.
- No boot with backlight on and no image.
- Brightness fade is smooth and does not starve animation.
- After boot, leave the device untouched for the configured display timeout and
  verify one `backlight.diag: timeout off` event.
- Leave the sleeping device untouched long enough to catch isolated GT911 noise;
  the backlight must not wake without a coherent contact.
- Verify the timeout is inhibited only by an active Voice conversation, an
  enabled Immich slideshow, or the Camera preview. After each protected state
  ends, verify that a full fresh timeout elapses before sleep.
- Verify an idle/error Voice screen and a paused Immich slideshow still sleep.

### Home navigation

- Swipe pages 1 -> 2 -> 3 -> 4 without pausing.
- Swipe back 4 -> 3 -> 2 -> 1.
- Test edge bounce on pages 1 and 4.
- Start a swipe on every tappable tile; no tile may open.
- Tap each tile without movement; it must still show pressed feedback and open
  exactly once.
- Touch an in-flight settle and reverse it back to the previous page.
- Touch an in-flight settle and continue through to the following page without
  a position reset or native-LVGL flash.
- Verify page indicator and clock stay fixed and correct.
- Change Home content, then verify the next snapshot contains the new state.
- Repeat swipes while music and artwork replacement are active.

### Applications

For Player, Settings, Voice, and Immich:

- First open after boot.
- Close and immediate reopen.
- Ten repeated open/close cycles.
- Cancel a close gesture before threshold.
- Complete a close gesture after threshold.
- Verify no stale app border, black dot, old Home page, or live-widget flash.
- Verify direct workers stop before close and resume only after open.

### Settings

- Open and immediately scroll.
- Start scroll over every switch/button; no accidental activation.
- With a zero-pixel start threshold, a stationary touch must still click once,
  while the first vertical coordinate change must suppress the native press.
- Verify momentum and top/bottom bounce.
- During momentum, touch again and drag in the opposite direction; motion must
  continue from the currently presented frame without a jump or recapture.
- Change a setting and scroll again; snapshot must show the new value.
- Verify no delayed hover flash after release.
- Close Settings and confirm its raw scroll buffers are released.

### Player and artwork

- Start playback from idle.
- Play, pause, next, and previous.
- Replace artwork repeatedly using radio streams and fixed-duration tracks.
- Verify correct RGB order, crop, and full-screen placement.
- Verify no blue flash during JPEG decode/presentation.
- Verify wavy progress remains smooth during artwork replacement.
- While an artwork replacement is in flight, open queue, speaker grouping, and
  volume overlay. Confirm each becomes visible and display invalidation remains
  enabled after the transition.
- Open the volume overlay from Home, Player, Voice, Gallery (moving and paused),
  and Camera. Confirm the clock disappears immediately and remains absent for
  the complete gesture, including from a frozen direct-scene background.
- Let a long title complete one marquee cycle. Confirm it returns to the exact
  initial position, remains still, and does not resume frame submissions.
- Confirm direct Player controls never appear above another app.
- Close Player while the wave and marquee are active.

### Audio

- Local boot chime.
- SendSpin playback for at least 15 minutes.
- Start and stop playback repeatedly.
- Check for boot pop and codec/I2S restart noise.
- Verify media remains continuous during ordinary LVGL activity.
- Verify no `time_burst` failure escalates into a lost endpoint.

### Voice

- Wake from idle.
- Ask a simple question and a tool/MCP question.
- Verify `listening -> thinking -> replying`.
- Verify the user transcript enters in gray and the assistant transcript enters
  below it in white without restarting the animation for every text delta.
- Verify backend wire events contain cumulative phrases rather than individual
  words. Test punctuation, a short final fragment, duplicate transcript
  sources, and a final transcript carried in the same message as the next
  phase.
- Exercise a transcript JSON message larger than the WebSocket receive chunk.
  Require complete device callbacks for both roles and no `WS text fragment out
  of order` or oversized-message warning; audible TTS alone is not sufficient.
- Verify the waveform breathes during silence, follows microphone energy while
  listening, and follows assistant PCM while replying.
- Interrupt TTS and verify direct `replying -> listening`.
- End by voice and by the application-close gesture; the Voice scene has no
  on-screen buttons.
- Verify AFE is disabled and normal wake word restored after final cleanup.
- Verify music pauses/ducks once and resumes only after final conversation end.
- Test backend disconnect and repeated failure recovery.
- With performance logs enabled, require at least 59 submitted waveform frames
  per two seconds at the 30 Hz setting, no rejected steady-state presentations,
  no DSI underruns, and no per-frame allocation growth.
- Run `python tools/test_voice_assistant_ui.py --output .tmp-voice-ui` to capture
  isolated Listening, Thinking, and Answering scenes without starting a real
  conversation. Treat full-screen JPEG capture timing separately from the
  steady waveform benchmark.
- Run `python tools/test_voice_assistant_ui.py --motion-seconds 12 --motion-hz
  30 --transcript-mode phrase --profile --skip-captures` for a repeatable
  dynamic-envelope and cumulative-phrase benchmark. Use `--transcript-mode
  word` only as a deliberate stress comparison; it is not the production wire
  contract.
  After the one-time full-page opening handoff, require request/render/submit
  parity, 28-31 FPS, `no_slot=0`, no rejected steady-state presentations, a
  1-8 ms maximum LVGL loop, zero native
  invalidated areas/pixels while text animates, and no DSI underruns. Status
  and transcript changes must be logged by the material direct-text presenter;
  a native LVGL label refresh is a regression.
- Set Display Timeout temporarily to 15 seconds, start a real Pipecat session,
  and verify the backlight remains on after at least 20 seconds in `waiting`,
  `listening`, `thinking`, or `replying`. Close the session, restore the prior
  setting, and verify the ordinary timeout starts from a fresh epoch.

### Immich

- First image after boot.
- Portrait and landscape images.
- Next/previous navigation.
- Prefetch and transition to several distinct assets.
- Direct pan in both axes.
- Optional fade-through-black mode.
- With fade enabled, verify fade-out starts during the final part of pan rather
  than after motion has stopped.
- Tap during pan and verify controls appear over the exact current frame: no
  recenter, transform restart, stripes, or white horizontal lines.
- Verify the title is the Immich album name and the subtitle is the photo date
  in `YYYY-MM-DD` form. The original asset filename must not be displayed.
- Close while prefetch/decode is active.
- Verify decoded image and transition buffers are released.

### Camera

- Open while SendSpin is playing: playback pauses before camera decode starts.
- Close and verify playback resumes only if Camera initiated the pause.
- Test one native 800x800 MJPEG source and verify decoded/presented counters,
  frame rate, drops, and JPEG/presentation durations.
- Test an unavailable native stream and verify the HA proxy falls back without
  committing an empty successful response or leaving a blank frame.

### Boot and player presentation

- Verify the boot chime starts with the ESPHome wordmark and finishes before
  the display begins fading out.
- Verify the expensive Home/application snapshot caches finish behind the
  opaque boot overlay before fade-out. While the panel is fully black, only
  switch the already-prepared Home tree, then fade in without a blue or
  intermediate LVGL frame.
- Start playback from the initial player placeholder and verify that the first
  artwork crossfades rather than appearing abruptly.
- Verify later artwork changes still crossfade with the wave and marquee live.
- Verify the song title keeps at least 15 px of visible clearance from both
  circular display edges.

## Diagnostics to capture

For graphics changes, capture:

- FPS and maximum LVGL loop time;
- DSI active/queued/staged buffer indices;
- frame-buffer addresses and alignment;
- DSI FIFO minimum, zero count, and underrun count;
- DMA2D/PPA/JPEG operation duration and errors;
- direct-region queue depth and generation;
- internal and PSRAM free/largest blocks;
- snapshot cache window and dirty state.

For audio/voice changes, capture:

- audio stack state and I2S hardware state;
- AFE feed/fetch drops and ring occupancy;
- speaker and microphone ring occupancy;
- realtime playback/uplink queue and dropped bytes;
- WiFi RSSI and connectivity;
- phase transitions and session generation.

Keep verbose diagnostics behind settings or compile-time flags. They must
default off in production.

## Performance comparison

Use the same action and duration before comparing builds. Suggested controlled
tests:

| Test | Duration | Primary metrics |
| --- | ---: | --- |
| Synthetic Home swipe | 10 s | FPS, compose time, DSI FIFO minimum |
| Settings continuous scroll | 10 s | FPS, start latency, settle latency |
| Artwork replacement | 10 changes | JPEG time, blue flashes, wave FPS |
| Gallery pan | 30 s | frame interval, PPA time, transition gap |
| Voice full duplex | 3 turns | audio drops, reply jitter, barge-in latency |

Record commit hashes for both product and ESPHome trees. Do not compare one
build with diagnostics enabled against another with diagnostics disabled.

## Artifact triage

Use the visible pattern to narrow the layer:

| Pattern | Likely layer |
| --- | --- |
| Full blue frame | DSI starvation/ownership |
| Full black frame | Backlight/frame readiness or explicit black fallback |
| Stable horizontal corruption | Stride, RGB888 PPA operation, or cache range |
| Corruption only during press | Direct state layer or stale display base |
| Correct after touch | Missing invalidation/refresh |
| First app open corrupt, later opens correct | Boot preview/work-buffer lifetime |
| Crash after repeated open/close | Use-after-free, leaked work buffer, or undrained worker |
| Audio breaks while graphics move | Task priority or shared PSRAM bandwidth |

Do not stack speculative fallbacks. Revert unsuccessful experiments before
testing the next hypothesis.

### 2026-09-15 boot lease validation

The boot snapshot preparation and application lifecycle were tested on ESP32-P4
over COM5 with ESP-IDF 5.5.5. The tested sequence was a complete boot, Home
idle observation, Settings open/close, and Player open/state/close. The build
was flashed directly over serial and the written image hash was verified.

The run showed `rejected=0` for the tested application transitions and no
`DIRECT frame boundary timed out` after boot preparation. DSI stress reported
`brg_under=0`, `host_under=0`, and `fifo_zero=0`. These checks validate DSI
ownership and lifecycle for this sequence; they do not prove absence of visual
artifacts in every native LVGL widget or cover long-duration media stress.

### 2026-09-15 fixed chrome and weather cache validation

The current COM5 image was compiled with ESP-IDF 5.5.5 and flashed directly
over serial. The written image SHA-256 is
`04688ED617E3A524B1E51129BB7D3770F97E8F81A54DCEDAFAAE2FC05D0E8A1A`.

The Home status bar is owned by fixed chrome: Home keeps its icons outside the
moving page roots, while Player and Settings use the global layer. The snapshot
compositor applies the same masks only at handoff, so periodic status polling
does not reorder objects or invalidate a full screen. Home pages 1-4, Player,
Settings, and return from Camera, Immich, and Assistant were captured after the
flash. The media captures show valid camera/photo frames and the assistant
capture shows both transcript paragraphs with a visible phase label.

Weather is prepared inside its page subtree before the boot snapshot. While the
live Lottie object is running, the carousel uses the prepared frozen frame. A
weather data update refreshes only the native temperature/condition chip as an
in-place full-stride band (`800x114` in the tested layout), rather than making
another full-frame snapshot. The band took approximately 75 ms in the current
serial log; subsequent weather rendering stabilized at about 42-43 FPS.

The same serial run reported `dsi_under=0` and no reset/backtrace. This is a
bounded transition and media smoke test, not proof against every long-duration
native LVGL stress case. Live Gemini speech/text remains a backend validation
blocker when the provider reports depleted prepayment credits; the device
transport and UI were verified with the local protocol test.

### 2026-09-19 Home, media, and conversation regression pass

Source trees are the modified product checkout based on `0cdaa2e` and the
modified ESPHome checkout based on `85aece2b9`. These HEADs alone do not identify
the firmware: both contain uncommitted changes. The native IDF 5.5.5 build
`2026-09-19 17:56:43 +0200`, config `0x8a422a40`, was flashed over COM5 with
verified image SHA-256
`797F4F10C3FD4BB4D4F7786C0F6C4DFF4409C0BC1D2D7E6F572FFCCDA7AF8F2E`.

Hardware evidence under `C:/aeh-build/20260919-*`:

| Check | Result | Evidence |
| --- | --- | --- |
| Three mixed app cycles, Voice/Settings/Player/Camera/Gallery | 15/15 completed without API loss or reboot; Player actually playing | `home-region-mixed/results.json` |
| Held Home drag, fixed icons/dots, moving mic and weather | 9/9, including identical native/snapshot Wi-Fi bounds | `region-snapshot-chrome/results.json` |
| Three returns Home 2 to Home 1 | Weather present in all nine captures | `region-weather-return/results.json` |
| Home 1-4, Player/Settings and return to Home 3 | 10/10; no page-one mic on page three | `region-home-chrome/results.json` |
| Full-size Gallery with retained Player artwork | Hardware JPEG succeeds; Home raw slots restored after close | `home-region-com.log` |
| Pipecat protocol and transport unit tests | 29 passed | `python -m unittest discover -s tests -p 'test_va_pipecat*.py'` |

The weather pixel test originally assumed a blue sun. Live HA selected a white
cloud; visual inspection confirmed the frame was present. Its criterion now
accepts both weather colors inside the translated weather-only region. This
test correction is not a firmware fix. Atomic screenshot capture briefly
pauses presentation, so these captures prove retained content and geometry,
not absence of every single-frame glitch.

Measured steady ranges in this run: Player wave about 54-55 FPS during music,
horizontal full-size Gallery pan about 38-39 FPS, camera presentation about
11-14 FPS. The generic cloudy ThorVG path remains around 9-10 FPS; the earlier
42-43 FPS weather number belongs to the specialized sunny renderer and must
not be reported as the performance of every weather condition. DSI counters
remained zero in this bounded run, with no assert/panic or failed allocation.
Physical finger latency and pressed-state replay were not measured by the
synthetic navigation API.

Rejected/intermediate failures and their concrete fixes:

- A repeated Assistant close into cloudy Home produced `tlsf_free: block
  already marked as free`. The decoded stack led through `lv_canvas_set_buffer`
  on the Lottie raster worker into LVGL's event list. Native frame publication
  now uses a one-frame pointer mailbox consumed by the ESPHome main loop;
  worker-side `lv_lock()` alone did not serialize YAML actions.
- A 1620x911 JPEG needed 2,976,768 bytes of contiguous decoded storage while
  the largest free block was only 1,856 KiB. Free total alone was misleading.
  Gallery now releases the two unused raw Home neighbours while retaining
  current Home and all compressed backing. It restores the three raw slots
  after close. The current 800x800 Player artwork remains resident.
- Full Home recapture on a clock change took about 984 ms and could omit the
  promoted weather canvas. The clock now patches only its merged region;
  observed updates were about 119-221 ms, outside active touch/navigation.
- The generic Gemini SDK setup error overwrote the actionable provider cause.
  Both `message` and `error` fields are normalized before suppression. Live HA
  now retains the depleted-prepayment explanation across a subsequent wake.

The Gallery requests `fullsize` through the original-asset endpoint, not the
smaller preview. Tests included source JPEG 1620x911 and the existing native
RGB565/PPA display path. This is not a claim that arbitrary full-resolution
phone originals fit the bounded P4 memory pool.

The Pipecat changes are in local source and the running add-on container, not
a published release. The configured Gemini project still returns depleted
prepaid credits, so real cloud inference/audio/text cannot be marked passed.
Synthetic transcript rendering is a separate check. See `audio-voice.md` for
the hotfix lifetime and the embedded FLAC assets.

#### Final timeout-policy image

The final image removes the artificial interaction timestamp update on an
automatic Assistant close. It was fully compiled, flashed over COM5, and
verified: build `2026-09-19 18:06:47 +0200`, config `0x2e78afd4`, SHA-256
`AF6AAA05D5973B9AA1D5E5B046B3F60EA51C3A1C89BFBFE489D50DD536F75FAA`.
The native API reported that exact compilation time after the tests.

`20260919-final-tests.log` records three additional Voice open/close cycles,
four synthetic transcript captures, Home inactivity, both loader/first-image
flows, all nine held-snapshot checks, and nine weather-return captures. All
completed successfully. `20260919-final-com.log` recorded Home blanking at
30,116 ms idle and sleeping refreshes of pages 2, 3, and 4. No panic, failed
allocation, or nonzero DSI underrun counter was found in this run. Camera and
Gallery captures contain decoded media, not only a loader. The actual server
error is legible in `20260919-final-voice-error/last-open.jpg`; synthetic Polish
user/assistant paragraphs and phase labels are visible in
`20260919-final-transcripts/voice-answering.jpg`.

Residual performance issue: after repeated app lifecycles the general cloudy
Lottie path measured about 4.5-6 FPS, below its initial 9-10 FPS. Retained-frame
correctness is fixed, but this path is not yet an ultra-smooth renderer. Do not
hide that result behind the sunny renderer's FPS or reduce asset resolution to
make the benchmark look better. The 96x96 M3 Camera/Gallery loaders separately
measured 54-59 FPS. Physical gesture latency, audible chime quality, and
long-duration unattended stability remain outside this bounded automated pass.

## Release gate

A productization checkpoint may replace the known-good baseline only when:

- config and complete compile pass;
- no new warning comes from changed components;
- all relevant hardware scenarios pass;
- memory largest-block values remain within budget;
- no display artifacts or blue flashes are observed;
- audio and voice remain continuous;
- documentation matches the implemented ownership model.

### 2026-09-21 fix14 COM5 pass

The firmware was compiled with ESP-IDF 5.5.5 and flashed directly over COM5;
OTA was not used. The build was the first one after moving the Player artwork
backdrop conversion to the wavy-progress render worker and fixing its initial
setup fallback so it never calls `xSemaphoreTake()` with a null semaphore.

| Check | Result | Evidence |
| --- | --- | --- |
| Home pages, Player, Settings, return to Home | PASS | `C:/aeh-build/fix14-home-chrome` |
| Weather return 2 -> 1, repeated captures | 9/9 with weather present | `C:/aeh-build/fix14-weather-return` |
| Voice, Settings, Player, Camera, Immich lifecycle with music | 5/5 | `C:/aeh-build/fix14-mixed-logged2` |
| Runtime reset/assert scan | none found | `C:/aeh-build/20260921-fix14-runtime.log` |
| DSI underrun scan | no nonzero underrun counter | same runtime log |
| Player waveform worker | 80-103 renders / 2 s in steady windows | same runtime log |
| Media resume volume | requested 50% restored before play | `audio.volume` entries in same log |

The run also showed hardware JPEG/RGB565 artwork adoption. The backend still
reported `Gemini: prepaid credits exhausted`; that is an external Pipecat/
provider condition, not a firmware display failure. Automated navigation does
not prove latency of a real finger drag or absence of a sub-frame visual flash;
those remain manual acceptance checks.

### 2026-10-20 boot, weather and application stability

Evidence is retained in `C:/aeh-build/stability-20261020`. Rejected candidates
and their logs remain separate from the final firmware and source hashes.
No commit or push is part of this validation.

The original persisted store-access fault resolved to `lv_anim_set_duration`
through `lv_lottie_set_src_data`. Buffer/task cleanup had discarded the timing
metadata while retaining the parsed ThorVG scene. Resource lifetime now keeps
those states together and recreates the timing descriptor defensively.

A rapid-close run then exposed a separate pause-lease leak: an application
closed during opening skipped its `on_opened` release. Navigation now finishes
that lifecycle and defers the coalesced close until the next tick. Worker job
start/completion publication and direct-region callback barriers preserve the
same ownership boundary.

The R5 color test deliberately caught another failure. A worker-side native
refresh overlapped a main-loop theme snapshot. `lv_inv_area` asserted because
`rendering_in_progress` was already set; the default assertion loop eventually
triggered the task watchdog. This was not evidence of an allocation failure.
Both finite-completion helpers and retained-color repaint now lend their
private raster source through the existing one-frame mailbox. Conversion,
canvas mutation, handoff, and native refresh belong to the main loop.

The selected RGB is reapplied after scene reload. A completed animation is
repainted at its retained phase; its clock is not restarted. The sunny renderer
also invalidates its static center. A color publication schedules a regional
cache refresh from the committed canvas. Weather swipe capture separately
copies the visible artwork from scanout into the existing Home raw slot.

R6 compiles with ESP-IDF 5.5.5, build `2026-10-20 20:27:17 +0200`, config
`0xae34800c`. Static RAM is 281,184 bytes; application flash is 7,551,400 bytes.
The factory image SHA-256 is
`e5c04b7e000199e6ae4aa4146b145e9cb511ccaaf4c6c3b8b52661071f36ce31`.
Generated component sources match the active fork; the source manifest and
recoverable source copies are retained with the evidence. Five navigation
schema tests and the 28-token/nine-asset geometry check pass. The authored C++
lifecycle tests were not executed on a host compiler.

After physical USB reconnection, R6 flashed successfully with hash verification.
Its six retained-color checks, three theme reload checks, and repeated
application/navigation stress completed. Matched cloudy rendering measured
26.28 FPS over 24.35 seconds, compared with 22.90 FPS for R4; raster cost was
17.38 ms versus 17.25 ms. These are bounded candidate-to-candidate measurements,
not the performance of every weather condition. R6 was rejected because sunny
rendering slept almost an entire six-second cycle between frames.

R7 calculates its next deadline from the current animation timeline, rather
than a previously published frame. An offline boundary sweep checked 12,001
positions, including wraparound and retained phase. Its product changes also
bind the Action tile title to its actual object and place the generated dark
rain/fog outlines behind their bright strokes, matching ThorVG paint order.
R7 boot capture contains 18 distinct pixel states and a completed trace retained
unchanged for 3.86 seconds on the selected `#AEE2FF` background. That establishes
progress and final-frame retention, not a 60 FPS playback measurement.

**R7 is not an accepted release.** Its first Gallery lifecycle stopped physical
display progress while the native API remained responsive. The slideshow
accepted 43 frames before rejecting subsequent submissions. All three
framebuffers remained active, queued, or staged; close correctly refused to
release those owned buffers. The artwork timeout's `fifo_min=832` is its
configured required threshold, not a measured FIFO depth. A later DSI stress
sample reports an actual minimum of zero and repeated zero-depth samples.
CPU was approximately
96.5% idle, with no reboot or DSI bridge-underrun report. The absence of those
reports does not exclude a DW-GDMA invalid-descriptor interrupt. Additional
read-only ring/channel diagnostics are required before choosing a repair.

R8 diagnostics compiled and flashed successfully. Four 32-second Gallery
lifecycles, the six-assertion palette/Assistant/Gallery sequence, and nine
weather variants completed without an invalid-LLI event. Sunny measured
46.07 FPS. These normal runs did not reproduce the R7 freeze. R8i then tested
bounded interrupt-signal masking at 25 and 30 ms on idle Home; rendering and
block counters continued, with zero invalid events. These results reject the
assumption that delayed IRQ service automatically invalidates this ring's
memory descriptors. Channel CTL VALID and descriptor-memory VALID are separate
states. No speculative invalid-LLI recovery is part of this candidate.

R8i later failed the mixed lifecycle stress. After the second Gallery close,
opening Player stopped the main loop before its normal handoff/preparation
messages. The 30-second watchdog reset `loopTask` while CPU 1 ran `IDLE1`.
The printed registers/stack therefore describe the idle task, not the blocked
loop task. The persisted generic "instruction address misaligned" label must
not be used as the cause of this watchdog event.

R8e is a diagnostic candidate with UART ELF core dumps for up to 64 tasks and
a dedicated 2 KiB panic stack. First/last DMA fatal status is also retained
before SDK interrupt clearing for explicit runtime state queries. The SDK's
generated dual-DRAM linker script resolves the annotated-global dump bounds
to an empty high region, despite placing those 32 bytes in low DRAM. Therefore
the fatal globals are not available as runtime evidence in these dumps; the
executable's initialized zeros are not a substitute. Task contexts and stacks
are captured independently and remain usable. Full dumps and their exact ELF
must stay local and separate from an accepted release.

R5 remains rejected for the reproduced rendering assertion. Results from R4
or R6 must not be reported as final R7 hardware validation. The current voice
backend also reports depleted Gemini prepaid credits, so UI lifecycle tests
do not establish successful cloud conversation or audio continuity.

#### R9-R11 recovery evidence and remaining release blockers

The immutable packages, ELF files, source backups and source/SDK hashes are in
`C:/aeh-build/stability-20261020/diagnostic-r9`, `diagnostic-r10` and
`diagnostic-r11`. Each directory contains its matching
`validated-source-hashes-rN.json`; a manifest's initial `hardware_validation:
pending` field is not the later test result. Runtime results are recorded in
`r9-final-stability-evidence.json`, `r10-final-stability-evidence.json` and
`r11-interim-blocker-evidence.json` under the same evidence root.

| Candidate | Factory image SHA-256 | Bounded result |
| --- | --- | --- |
| R9 | `cec30d82996b3c5f628b854988459471ebb309772c7464ae2e5de57f1267b0cb` | Diagnostic fault tests and three normal lifecycle batches completed. |
| R10 | `202baccf3f81d703a9cd5c95c4e2f2ad3287306b093c92a634fb8e18d6a2f730` | All ten scripted suites, including persisted boot, completed. |
| R11 | `625a75d8ac88ac0d3ac464d36930db826f33f3e1fb33251d6292e7e6ce37e05e` | First nine suites completed; persisted boot is blocked by unexpected resets. |

Natural R8e evidence finally captured the stopped ring: fatal status `0x2011`,
both descriptor-memory VALID bits clear, the channel still enabled and no AXI
error. The existing generic ISR then treated the coincident BLOCK_DONE as an
ordinary completion without resuming the invalid ring. The production repair
validates the halted phase, descriptor links and framebuffer sources, preserves
active/staged/pending ownership, publishes the coherent descriptor pair and
issues explicit hardware resume. It suppresses that same IRQ's stale ordinary
completion; it does not allocate or copy a replacement full-screen buffer.

R9's eight forced faults and four additional phase probes each recovered once,
with zero rejected repairs. Those first-event latches sampled slot 1 only.
The independent contract model covered 12 accepted phase permutations and 20
rejection cases; it is not execution of the production C on a host. Three
normal R9 batches then completed 96 application launches, with pause/depth
`0/0` at every endpoint and no persistent display halt or watchdog reset.
They included two natural repairs and one bridge underrun coincident with the
first invalid latch. The first latch already had FIFO zero and bridge RAW one
before repair. Their order or causal direction within the same millisecond is
not established.

Both repair phases now have physical evidence. R9/R10 captured slot 1 with a
staged top half from B, old active bottom half from A and pending work still
owned. R11 later captured natural slot 0 with a coherent active pair at tick
463417. Its subsequent block count advanced from 55174 to 55396 by tick
465281, with recovered/rejected `1/0`. That event had no bridge-underrun IRQ.
See `r9-natural-recovery-522624`, `r10-natural-recovery-465622` and
`r11-natural-recovery-463417` for exact source geometry, register windows and
hashes. The earlier negative interrupt-delay experiment must not be used to
exclude this naturally observed invalid-ring state.

The durable framework patch also backports four official Espressif PPA fixes:
`c1cec26bbd1e36ceb19143257ecac65e0a67bbcf`,
`7339ee882f779d40d4e01ca40a089178b8505351`,
`e87e0b31d96c24d20f3b6e8167b7e5ae811c89c0` and
`54a57a735192c4733b62dacf20cc74030ef39d30`. They cover engine queue
serialization, blocking transaction reuse, enqueue-failure lifetime and
blocking callback behavior. The offline oracle reproduced the four upstream
diffs exactly and checked idempotence and rejection before partial writes;
see `ppa-upstream-backport/validation-after-root-sdk-apply.json`. These are
concrete upstream races, but no captured blocked-loop stack proves that they
caused the original R8i watchdog.

R10's ten completed suites cover boot trace, palette, retained weather theme,
sunny playback, nine variants, 32 normal/rapid application launches, weather
return, raw motion, matched performance and persisted accent boot. This is
not a zero-physical-error claim: that boot recorded two bridge IRQs, one during
boot validation and one coincident with a successfully repaired natural ring
halt. The later planned persisted reboot had no additional event in its
validation window. JPEG screenshot pause began 1232 ms after the first boot
IRQ; earlier raw diagnostic reads existed, but their causation is unproven.
The two exact windows are retained separately. R10 removes both temporary DMA
fault actions, component wrappers and SDK injection helpers, including their
removal when reapplying to an older patched SDK. Normal UART core capture is
disabled; read-only ring diagnostics and production recovery remain.

R9 endpoint memory is quantified in `r9-memory-endpoint-comparison.json`.
Across the three batches, PSRAM occupancy grew 80 KiB, of which 73 KiB was
accounted retained JPEG capacity; residual occupancy changed 7 KiB. Internal
occupancy had zero net change, while the largest PSRAM block increased from
1856 to 2016 KiB. Raw/application-work/scroll/close buffers were zero at every
endpoint. This excludes an extra retained full-screen buffer in those states,
not every possible long-duration leak or content-dependent cache increase.

**R11 is not an accepted release.** Nine scripted suites, including its
32-launch stress, completed before the persisted-boot test. That epoch recorded
one successful natural slot-0 repair and five later bridge IRQs; the bridge
events were not coincident with the invalid latch. After one planned restart,
unrequested `SW_CPU_RESET` boots repeated, including safe-mode boots. The ROM
SavedPC resolves to `esp_restart_noos_inner` and interrupted GPIO functions;
it is not a caller stack and does not identify the initiating component.
No initiating panic/watchdog text was captured. SDK log forwarding/filtering
can hide original SDK errors, so their absence does not exclude a transport
reset. Cause remains unproven. Exact ELF decoding and local serial prefixes
are in `r11-persisted-double-reset`; no full-matrix or reboot-success claim may
be inferred from the preceding nine PASS entries.

The warmed performance issue also remains open. Matched cloudy Lottie counters
measured 22.71 FPS in R10 and 22.61 FPS in R11 versus 26.28 FPS in R6; weighted
raster costs were approximately 17.39, 17.31 and 17.38 ms respectively. These
are summed rendered-frame/elapsed-time counters, not independent VSYNC
presentation measurements. Workload history and the earlier natural repair
were not isolated by a completed fresh-boot R11 comparison. See
`performance-analysis-r10.txt` and `performance-analysis-r11.json`. Neither
successful sunny playback nor the nine-variant sweep establishes absence of
this warmed regression.

## Current stability checkpoint: R25, 2026-10-21

This is a bounded source/build and hardware checkpoint, not final release acceptance.
The listed software campaigns and human-confirmed cold five are closed.
Keep source/build, exact ELF, flash identity, scripted checks, selected visual
review and physical power evidence as separate claims.

### Source and build identity

R25 marker: `2026-10-21 15:12:37 +0200`; final ELF SHA256:
`98caff20d55fa0efee77f1bb2336fc9d8fd4bc9c844ead0f6b399eb69710bc91`.
The immutable source manifest SHA256 is
`e5d555ec0dfcd3ea2385e6e2992b5d52ae7cc15d18fc8c2bca41b3fd8cf9d3e1`.
Configuration/full native compilation passed; RAM is 291946 bytes (+8 versus
R24). Reported Flash usage is 7,630,788 bytes (+352); the actual OTA/application
image is 7,631,232 bytes (+352). The extra 8-byte heap-start marker in section
sums is not another runtime payload allocation.

Only two product files change from R24: `modules/lvgl/pages/tiles_m3.yaml`
and `modules/lvgl/navigation.yaml`. Eight existing clock labels share
`home_clock_refresh_region` at x0/y71/412×548; IDs, absolute glyph positions
and painter order are preserved. The existing multi-region refresh receives
one container/count 1 and preserves hidden/pending/wait 40 ms/dirty behavior.
No new raw surface, copy, worker, fork/SDK code or SDK configuration change is added.

The actual generated main diff was root reviewed against the frozen proposal;
source scope verifies 184 preserved R24/R25 paths. SDK, fork, SDK configuration,
generated defines and non-application image bytes are unchanged from R24.
The independent package inventory verified 92 current source/build paths,
45 helpers, two external helpers and preserved firmware/compiler artifacts.

### Rejected predecessor and restart mechanism

R23 passed its bounded main/addon checks but was rejected after its second
warmed shutdown raised a real core1 Store access fault. Exact final-ELF/SDK
analysis localized the failure to the orderly P4 restart/cache path. Its earlier
rendering passes do not clear that restart failure.

R24 adds a default-off, exact-IDF5.5.5 P4 SDK patch, explicitly enabled by the
product. It stalls the other core without the earlier reset, then waits for
four cache-sync ENA bits to clear, with fences, before writeback. Disabled
behavior is preserved; there is no timeout/RTC-reset fallback or new buffer/task.
This is a local implementation of the mechanism described in
[Espressif issue19171](https://github.com/espressif/esp-idf/issues/19171), not a
verified released-fix backport. R24 configuration/build/ELF, initial boot,
main 12 and six bounded normal software restarts passed; its long warm and
physical cold campaigns were not run. R25 keeps this SDK path unchanged.

Detailed R13–R22 iteration chronology and numbers stay in frozen evidence,
rather than this mandatory guide. Keep the reusable runtime contracts in the
architecture documents; do not turn old successful intervals into acceptance
of an image that later failed.

### Completed R25 main checks

Initial app-only OTA from the exact retained R24 image passed. A captured
changing Sky boot trace and initial Home passed; root viewed partial 007 and
completed 025. First-five controlled restarts and the main persisted-accent
restart each have exact retained hash/UART evidence: normal caller 0x400c81e6,
six normal requests across those earlier checks. Persisted tick 860441 has one ROM and no
extra Hosted request. Its late identical completed boot JPEGs are not motion
proof; initial OTA's changing trace is the separate drawing evidence.

All twelve main steps passed at 13:37:28.346880 UTC. Stress covered 32 application
launches, 24 page changes and ten rapid cycles. Weather after stress and 45 sparse
motion captures in 15.256 seconds completed (ten distinct raw hashes, not physical
FPS). Intermediate slot counts were unavailable for weather-theme and variants;
their other native ownership fields were idle. Missing counts are not zero or
an orphan diagnosis. Later stress/warm/persisted endpoints explicitly show 0/4.
Fresh through warm share one normal API epoch; persisted restart splits it.

The header regression observed a natural fresh merged scanout at 13:25:00.092294
UTC after 50.716 seconds: regions 1/area 0,71 412x548, took 5605 us. Existing Swipe
logs were enabled/restored; no forced clock update or UI recovery was sent.
All 12 before/return JPEG cases preserve 658 fixed white pixels (Jaccard 1.0)
and have 0 old moving-header pixels. The actual R24 negative retains 389 moved
pixels and is rejected. Root viewed outgoing-held-1 and return-1-2 with visible
Sun artwork, preserved clock overlap and one fixed header.

### Rendering and memory evidence

Clear-day fresh/warm rendered FPS is 47.40156/48.05216; warm is 1.373% above fresh
and 0.577% above R24's same-scene warm. Fresh frame/time totals 1152/24303 ms use
11 complete API rows plus one actual partial UART row 96 frames/2096 ms. Raster/
render and publish-miss fields cover 11 only; all 12 publish total is UNKNOWN.
Warm totals 1157/24078 ms have 12 complete rows and publish-miss 0. No missing field
is invented. Regional samples have independent coverage; raw records retain it.

Fresh 10/warm 3 timing warnings remain. Neither measurement interval adds a
DMA/bridge/allocation/restart event; warm's endpoint invalid/recovered/rejected
is 0/0/0. Whole-UART/transport auditing is separate from this bounded observation.
Nine weather variants passed one-cycle perf2s checks. Clear-day is about 47 FPS,
snow 20.978 FPS versus R24's 20.685; do not compare different assets or use 47 FPS as
a universal weather rate. Clear-night and fog have different 2/3 sample coverage;
their descriptive comparisons are not equal-count pairs.

R25 warm free PSRAM 4947→4950 KiB/largest 2944 differs from R24's 5455/largest2496.
Retained snapshot/JPEG totals are 7069/1444 KiB versus 6512/887 KiB. The displayed
JPEG difference 557 KiB is aggregate exact-size encoded payload capacity, not a
retained 1→1.5 MiB scratch bucket. Per-entry Home/app/Gallery attribution is not
logged at INFO and remains unknown. Shared raw app work/scroll/close are 0;
weather 1792 KiB is visible and other Lottie 0. Stability is within the saved
window, not equal memory across histories or a leak test.

### Application and accent addons

Camera/Volume passed an initial 3-case preflight and a separate full 3-cycle
7-case run (four Camera, three Volume, including Camera after Volume retirement).
Actual presented-counter rates were 12.034–12.685 FPS initially and 9.921–10.423 FPS
later; live input/network cadence was not controlled, so these are not an
identical-rate or regression claim. Joint exclusive-session/INFO-worker/native-
invalidation-off/no-fallback/retirement checks passed.

Targeted Volume accent passed Sky/Lavender/restored Sky; active and inactive
core median maximum error is 1 RGB value each (v2 threshold 4). Natural warm
accent passed 35 state scenarios/56 captures on one connection. Both actual
changes recorded `attempt=1/3 invalidate=1 home=1 apps=1 pending=0`, then idle
endpoints; unchanged initial Sky is not a new refresh. That run has no recorded
cache warning, hard fault, transport event or reconnect.

Root viewed selected Lavender Player, Apps, Security and Controls, restored
Sky Player, real Camera water/rocks, and the Lavender Volume arc/dark track.
These selected views show refreshed Play colors, correct Controls page and
contrasting selected tile text. They do not claim all captured images were
visually reviewed or unavailable HA entities functionally tested.

### Preserved matched-overcast tool failure

The later helper **FAILED its host 12-complete-row assertion**; original
`result.passed=false` is retained. Workload/exact-marker checks completed and
current HA sunny weather/Performance Logs=false were restored. This was not a
firmware assertion or reboot. Protocol device.log lines 97–300 exclude three
warmup rows and contain 11 complete rows 592/22281 ms=26.56972 FPS.

UART preserves one actual additional partial row 55 frames/2129 ms, cut after
`publish_missed`; all 11 complete tuples match in order. Frame/time recovery
is 647/24410 ms=26.50553 FPS across 12 actual windows; raster/render/publish remain
11 complete only. All 12 publish total is UNKNOWN. This rate is 0.0134% below
R23's exact same-scene 26.5090894 FPS, with different warmed histories. It is
separate offline counter evidence, not a retroactive helper PASS or physical FPS.
No benchmark rerun replaced the failed result. The saved interval has three
timing warnings and no disconnect/fatal/restart/DMA/bridge/allocation event.

### Remaining acceptance gates

The additional 45 controlled restarts completed 45/45. Independent frozen UART/API
proof verifies 50 controlled restarts (first 5 plus 45) and the separate persisted
restart: 51 R25 requests and 51 ROM boots, exact retained full hash/caller each,
with no extra/Hosted/panic/watchdog/SDIO fault. The old R24 OTA shutdown is
separately excluded. All 50 Home JPEGs were structurally recomputed; the minimum
post-reconnect healthy interval was 28.157 seconds. These are repeated planned
boots, not one uninterrupted uptime or 45 repetitions of the full app workload.

Final health passed: exact marker, Sky restored, original Gallery URL restored,
fault actions absent, native ownership/retirement idle. Root viewed home-final
clock 16:23/Sky/Sun 16C with correct geometry/weather. Raw header 658/indicators 268
were separately checked; viewer icon omission is not missing-chrome evidence.
Selected direct views and structural masks remain different claims.

Five physical cycles are confirmed by two direct user replies to the all-power,
including USB, off >=10s procedure. Off time was human reported, not measured.
Two bounded UART sessions captured five distinct R25 POWERON startups; early USB
enumeration prefixes were missed, so five complete ROM windows are NOT PROVED.
Four paired API reconnect observations (01..04) each have >=30s stable health and
a Home JPEG. The fifth startup preceded the second monitor's deadline; a separate
late-only probe then passed 30.009s with reset1, idle Home/slots0 and a fifth JPEG,
viewed by root (17:56/Moon14C/Sky). It adds no physical cycle or API edge pair.
Both 900s API monitors retain FAILED_OR_INCOMPLETE/TimeoutError, not firmware
assertions. Their deadlines do not erase the captured startup/health evidence.
All collectors closed before this editorial update. This update changes no
firmware or diagnostic helper.
The original postdocs admission scope stays immutable historical evidence; this
four-document factual reconciliation has separate before/after hashes.

### Evidence map

All local frozen evidence is under `C:\aeh-build\stability-20261021`.

- `diagnostic-r25`, `r25-build-identity.json`, `r25-source-scope-proof`,
  `r25-generated-main-review.json`, `r25-package-independent-review`.
- `r25-controlled-restarts`, `r25-warm45-independent-uart-audit`,
  `r25-restart-aggregate-independent-proof`, `final-health-r25`,
  `r25-persisted-independent-uart-audit`,
  `r25-main-complete-evidence`, `r25-completed.json`.
- `r25-performance-evidence`, `r25-memory-cache-evidence`,
  `r25-variant-performance-evidence`, `r25-matched-overcast-evidence`.
- `r25-camera-volume-accent-evidence`, `r25-warm-accent-evidence`,
  `weather-r25-before-stress/header-wrapper-result.json`.
- Rejected R23: `r23-candidate-rejection-stop`, `r23-warm-attempt2-panic-transport`,
  `r23-matched-overcast-evidence`. Bounded R24: `diagnostic-r24`,
  `r24-completed.json`, `r24-persisted-independent-uart-audit`.
- Cold power: `cold-power-r25-20261021-1519-utc-api` and paired `-uart`,
  `cold-power-r25-20261021-1539-utc-api` and paired `-uart`,
  `cold-power-r25-late-health-05`, `r25-cold-five-direct-user-confirmation.json`,
  `r25-cold-five-cross-window-independent-proof/proof.json`,
  `r25-cold-five-root-assessment.json`.
- Earlier detailed iterations remain in `documentation-overlay-r25-main-addons`
  and their underlying frozen evidence; no rejected checkpoint is discarded.

### 2026-10-22 official ESPHome integration

The current automated checkpoint uses ESPHome `2026.11.0-dev`, ESP-IDF `5.5.6`
and candidate18, marker `2026-10-22 14:08:01 +0200`. Its exact source, ELF/OTA
hashes, normal-merge history, component checks, 12-case device matrix, reviewed
screenshots, supplemental ownership/media tests, paired R25 measurements and
five software-start/real-Voice cycles are recorded in the
[upstream integration report](esphome-upstream-2026-10-22.md).

This is validation in the recorded automated scope. Current-image physical
power-removal cycles were not performed because the user was unavailable;
R25's earlier five cycles do not cover this image. Gemini credits prevent a
successful acoustic conversation. Lower memory headroom and the unexplained
increase in accumulated LVGL-handler wall time remain explicit limitations.
Rejected earlier images and the unknown initiating causes of their historical
watchdog/DSI events remain preserved rather than cleared by later tests.
