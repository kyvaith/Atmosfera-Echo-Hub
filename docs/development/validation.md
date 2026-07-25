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

### Home navigation

- Swipe pages 1 -> 2 -> 3 -> 4 without pausing.
- Swipe back 4 -> 3 -> 2 -> 1.
- Test edge bounce on pages 1 and 4.
- Start a swipe on every tappable tile; no tile may open.
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
- Verify momentum and top/bottom bounce.
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
- Open queue, speaker grouping, and volume overlay.
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
- Interrupt TTS and verify direct `replying -> listening`.
- End by voice and by the on-screen close button.
- Verify AFE is disabled and normal wake word restored after final cleanup.
- Verify music pauses/ducks once and resumes only after final conversation end.
- Test backend disconnect and repeated failure recovery.

### Immich

- First image after boot.
- Portrait and landscape images.
- Next/previous navigation.
- Prefetch and transition to several distinct assets.
- Direct pan in both axes.
- Optional fade-through-black mode.
- Close while prefetch/decode is active.
- Verify decoded image and transition buffers are released.

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

