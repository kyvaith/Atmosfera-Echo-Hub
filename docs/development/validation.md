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
python -m esphome config atmosfera-echo-hub.yaml
```

Complete compile:

```powershell
python -m esphome compile atmosfera-echo-hub.yaml
```

USB upload:

```powershell
python -m esphome upload atmosfera-echo-hub.yaml --device COM5
```

Serial logs:

```powershell
python -m esphome logs atmosfera-echo-hub.yaml --device COM5
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

