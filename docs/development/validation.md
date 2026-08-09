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

## Release gate

A productization checkpoint may replace the known-good baseline only when:

- config and complete compile pass;
- no new warning comes from changed components;
- all relevant hardware scenarios pass;
- memory largest-block values remain within budget;
- no display artifacts or blue flashes are observed;
- audio and voice remain continuous;
- documentation matches the implemented ownership model.

