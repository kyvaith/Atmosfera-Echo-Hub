# Audio and voice architecture

The device has one coordinated duplex audio transport. Music, local chimes,
assistant playback, microphone capture, and AEC share the same physical I2S
clock domain and must not create independent hardware owners.

## Hardware topology

### Provider errors and diagnostic hooks

Gemini Live can fail while entering its connection context, before its receive
loop has installed error handling. The Pipecat adapter forwards this failure as
an urgent `provider_connection_error`, remembers it across a satellite wake,
and clears it only after `provider-ready`. The ESPHome receiver stops the broken
session, cancels no-speech/follow-up timers, and publishes a readable error.
The 2026-09-19 live server returned depleted prepaid credits; this is distinct
from microphone ingress or transcript rendering failure.

The diagnostic fix is present in the local Pipecat source and was tested in
the running HA add-on container on 2026-09-19. It is a reversible container
hotfix, not a new published add-on release: recreating/upgrading that container
from its old image will remove the deployed copy until a release is built.

Voice UI diagnostics must open the registered application. Revealing only its
top-layer widget leaves `ui_active_app` and weather ownership unchanged and can
falsely suggest missing transcripts. The text path is checked separately from
successful cloud inference.

Local chimes now use `device-startup.flac`, `confirm.flac`, and `error.flac`,
converted from the supplied desktop WAVs and embedded through `audio_file`.
They retain the shared decoder/mixer path; no independent I2S owner is created.

The display timeout uses the last user interaction, not LVGL redraw activity.
A physical touch cancels automatic return-to-blank after voice. Active voice,
Gallery, and Camera temporarily inhibit blanking without moving the timestamp.

| Function | Configuration |
| --- | --- |
| I2S sample rate | 48 kHz |
| Processed microphone rate | 16 kHz |
| Sample and slot width | 16 bit |
| Bus mode | Four-slot TDM |
| Microphone codec | ES7210 at `0x40` |
| Output codec | ES8311 at `0x18` |
| Microphone slots | 0 and 2 |
| Playback-reference slot | 1 |
| AEC reference alignment | Previous frame |
| Amplifier enable | GPIO53, default off |
| Physical output | Mono |

The current AFE configuration uses one microphone in `mr` input format. The
board exposes more microphone data, but multi-microphone separation is not
enabled because the measured CPU cost conflicted with realtime output and UI.

## Audio graph

```mermaid
flowchart LR
    MICS["ES7210 microphone/TDM slots"]
    REF["Playback reference<br/>TDM slot 1"]
    STACK["esp_audio_stack<br/>48 kHz I2S owner"]
    AFE["ESP AFE fd_low_cost<br/>AEC enabled on demand"]
    MIC16["voice_microphone<br/>16 kHz mono"]
    WAKE["micro_wake_word"]
    REALTIME["va_pipecat uplink"]
    NATIVE["ESPHome voice_assistant fallback"]

    SENDSPIN["SendSpin PCM<br/>48 kHz mono"]
    LOCAL["Local FLAC chimes"]
    TTS["Realtime/native TTS"]
    MEDIA_RESAMPLE["media_speaker"]
    VA_RESAMPLE["assistant_speaker<br/>24 kHz input to 48 kHz"]
    MIXER["audio_mixer"]
    DAC["ES8311 and amplifier"]

    MICS --> STACK
    REF --> STACK
    STACK --> AFE
    AFE --> MIC16
    MIC16 --> WAKE
    MIC16 --> REALTIME
    MIC16 --> NATIVE

    SENDSPIN --> MEDIA_RESAMPLE
    LOCAL --> VA_RESAMPLE
    TTS --> VA_RESAMPLE
    MEDIA_RESAMPLE --> MIXER
    VA_RESAMPLE --> MIXER
    MIXER --> STACK
    STACK --> DAC
    STACK --> REF
```

`esp_audio_stack` is the only physical I2S owner. The speaker abstraction,
mixer, and resamplers feed it through bounded ring buffers.

## Full duplex and AEC

Full duplex means:

1. microphone frames continue arriving while music or assistant audio plays;
2. the exact playback signal is provided as a reference to the AFE;
3. the AFE subtracts echo and emits post-AEC microphone audio;
4. the voice transport may keep transmitting microphone data during TTS;
5. near-end speech can interrupt the assistant.

It does not mean separate, unsynchronized input and output peripherals.

The playback reference comes from the TDM reference slot and uses the previous
frame for timing alignment. AEC is enabled in the AFE configuration but its
runtime switch is normally off. Enabling `voice_audio_processing_switch`
activates processing for a conversation without rebuilding the hardware
pipeline.

Noise suppression, speech enhancement, AGC, and continuous local VAD are
disabled. Reasons:

- ESP-SR warns that NS may reduce recognition accuracy;
- multi-microphone BSS/SE consumed too much CPU in the current workload;
- continuous VAD kept a background microphone consumer active and could starve
  the post-AFE path;
- the realtime backend already performs semantic and server-side VAD.

## Idle versus conversation

```mermaid
stateDiagram-v2
    [*] --> IdleWake
    IdleWake: Wake word active
    IdleWake: AFE/AEC runtime switch off
    IdleWake --> Opening: wake word or manual start
    Opening: Pause/duck media
    Opening: Enable AFE/AEC
    Opening: Open assistant UI and realtime session
    Opening --> Listening
    Listening --> Thinking: server processing/tool call
    Listening --> Replying: response starts
    Thinking --> Replying
    Replying --> Listening: barge-in or follow-up
    Replying --> Thanks: conversation completes
    Listening --> Error: transport/session failure
    Thanks --> IdleWake: release session and restore media
    Error --> IdleWake: cleanup and restore wake word
```

The expensive processing path is active only between `Opening` and final
cleanup. Idle wake-word detection continues to consume microphone frames, but
does not require the full AFE feature set.

## Realtime conversation flow

The primary conversational transport is the external `va_pipecat` component:

1. A wake word or manual Assistant tile opens the registered Voice app.
2. Music is paused or ducked according to product policy.
3. AFE/AEC is enabled.
4. The persistent, authenticated Pipecat WebSocket is already warm and a new
   wake turn begins.
5. `voice_microphone` streams 16 kHz mono PCM through a PSRAM uplink ring.
6. Server phase, transcript, and normalized PCM-envelope events update the
   assistant presentation.
7. Incoming 24 kHz mono TTS enters a PSRAM playback ring.
8. `assistant_speaker` resamples to the 48 kHz mixer/output path.
9. During reply, microphone streaming remains active for barge-in.
10. Final cleanup disables AFE, restores idle wake words, and resumes media if
    the conversation actually ended.

The playback ring defaults to a 300 ms prebuffer. The backend may tune this at
runtime. The goal is to absorb network jitter without delaying the first audio
more than necessary.

The backend endpoint is provisioned automatically. `va_pipecat` registers a
hidden native API action, and the Pipecat Assist add-on sends the complete
authenticated WebSocket URL after discovering the device in Home Assistant.
The token is not stored in an HA text entity or logged by the firmware. A
periodic re-provision makes device and Home Assistant restarts self-healing.

The microphone callback is gated while no conversation is active. It does not
retain or replay pre-roll, so wake chimes and their acoustic tail cannot leak
into the next Pipecat turn. Speech should begin when the listening state is
visible.

## Voice assistant presentation

The Voice application is a full-screen black scene with no on-screen controls.
It is closed only through the normal application-close gesture, which also
terminates the Pipecat session. The visual hierarchy is:

1. a small phase label at the top (`Listening`, `Thinking`, `Answering`,
   `Thanks`, or an error state);
2. a bounded rolling dialog in large centered paragraphs;
3. a three-line purple waveform over a bottom-anchored purple gradient.

The dialog keeps at most three paragraphs: the immediately preceding assistant
answer in white, the current user turn in gray, and the current assistant
answer in white. When a follow-up starts, the older user paragraph is removed,
the preceding assistant answer moves up, and the new user paragraph enters
below it. This preserves conversational order without allocating an unbounded
history or another display-sized surface. If the three blocks exceed the text
region, they are bottom-aligned so the newest turn remains visible.

Navigation is the sole owner of Voice visibility. A wake word must open the
registered `voice_application` through `lvgl.navigation.open`; it must not
directly unhide the overlay or activate the waveform. This guarantees that the
black LVGL surface has completed its transition before the direct presenter can
draw and that the close gesture owns an active application even before the user
speaks.

Backend phase and transcript callbacks only update content inside an already
open Voice application. A local close sets `voice_assistant_stop_requested`
before sending `end_session()`, so delayed `listening`, `replying`, transcript,
or idle callbacks cannot reopen the scene while navigation returns to Home.
Clear that latch only when a new navigation-owned Voice opening begins.

A wake-word opening records whether the backlight was off before `display_wake`
runs. A terminal Pipecat reply enters `thanks`; the device component keeps that
state visible for 1200 ms and then emits `idle`. This terminal `idle` closes the
navigation-owned Voice application. Only after the close transition completes
may the backlight return to its recorded off state. A Voice session opened from
an already-lit display returns to Home without changing display power. Manual
tile and diagnostic opens always count as display-on origins.

The Pipecat bridge must not expose raw model tokens as display events. It
normalizes cumulative and token-style sources, accumulates each RTVI observer
(`bot-output`, transcription, TTS text, and LLM text) independently, selects
one authoritative source by priority, and emits cumulative phrases: four words
for user partials and six
words for assistant partials, or earlier at punctuation and at turn end. A
pending final phrase may share one protocol message with the following phase;
the ESPHome parser therefore processes both fields instead of returning after
the transcript. This preserves the final words without briefly losing the
`listening`, `thanks`, or terminal transition. Never append chunks from two
assistant observers to one accumulator: differing chunk boundaries and
punctuation can otherwise duplicate a complete clause on the device.

Device-side transcript updates remain latest-wins and are committed at most
every 100 ms. A new paragraph fades and translates into place over seven 33 ms
steps; the bounded dialog shifts upward in the same animation, while cumulative
phrase continuations update in place. Streaming text therefore does not restart
the entrance animation or create a second raster pass.

The ESP-IDF WebSocket client can deliver one JSON text message in multiple data
events. `va_pipecat` must assemble text events by `payload_offset` and
`payload_len`, including opcode-zero continuation frames, and call the JSON
parser only after the complete payload is present. Parsing each data event as a
standalone message silently drops longer transcript updates while binary audio
continues to work, producing the misleading symptom of audible answers with no
captions.

The declarative LVGL phase and transcript labels define geometry, fonts,
colors, and wrapping only. After setup the material presenter hides them and
owns two fixed RGB888 direct regions: one for status and one for the complete
transcript panel. It rasterizes UTF-8 glyphs with the configured immutable LVGL
fonts into reusable PSRAM buffers and submits only those regions through the
regional PPA presenter. The entrance fade and vertical translation are also
drawn inside the transcript region. The wave frame is scheduled before phrase
rasterization so a 30-45 ms PSRAM text pass cannot postpone the independent
wave worker. Live text must never be switched back to native label updates: in
RGB888 DIRECT mode that invalidates a large native area, runs font/layout work
in the LVGL loop, and stalls the independent wave. The presenter never
allocates a full-screen text buffer or allocates per phrase.

Animated transcript frames remain ordinary asynchronous regional updates. Once
the paragraph animation becomes idle, the final transcript submission is a
stable boundary: the compositor drains pending work and carries that rectangle
to every idle DSI framebuffer. This prevents a later framebuffer rotation from
revealing an older text state without retaining another 680x360 PSRAM copy.

`va_pipecat.on_audio_level` publishes separate normalized input and output PCM
envelopes. The presenter selects input while listening and output while
speaking, applies its own attack/release smoothing, and falls back to a slow
breathing wave during thinking or silence. It never reads PCM directly.

The waveform is not an LVGL object tree animation. A low-priority raster worker
builds one 660x190 RGB888 region in two reusable presentation slots while the
regional PPA compositor runs on the other core. The renderer owns exactly one
backdrop and two in-flight buffers (1,128,600 bytes total) for its lifetime,
does not allocate per frame, and coalesces work when both slots are busy. Each
slot tracks the rows touched by its previous wave and restores only that dirty
vertical span from the immutable backdrop before reuse; copying the complete
660x190 backdrop every frame wastes PSRAM bandwidth. Stopping the application
drains both slots before releasing the direct region.

At the validated 30 Hz setting, the dynamic Listening/Answering benchmark
presents 60-61 frames per two seconds with request, render, and submit counts
equal and no slot starvation. Dynamic raster work averages roughly 10-13 ms
and regional presentation roughly 9 ms. With the real microphone and AFE
active, the presenter remains at about 30 FPS and raster work averages 5-6 ms.
The media-player direct presenters must be quiesced before Voice takes the
region queue; deliberately running both workloads reduced the wave to roughly
15-23 FPS. A full-screen diagnostic JPEG capture is a separate stress
operation and must not be included in these steady-state figures.

Native LVGL text invalidation is expensive in RGB888 DIRECT mode. Before the
direct text regions, a synthetic word-at-a-time stream reduced the wave to
5.4-22.9 FPS and produced 187-283 ms LVGL loop spikes; even phrase updates
caused 116-161 ms stalls. With phrase batching and direct text presentation,
the cumulative-phrase benchmark keeps the wave at 28.8-30.4 FPS after the
initial full-page handoff, bounds the LVGL loop to 1-8 ms, and reports zero
native invalidated areas, zero native invalidated pixels, and zero DSI
underruns. The one-time first acquisition of the three direct regions measured
23.3 FPS and is tracked separately from streaming phrase updates. Phrase
batching remains part of the wire contract because it avoids unnecessary
raster submissions, while the direct regions remove the full-screen LVGL
refresh from the critical path.

```mermaid
flowchart LR
    PCM_IN["Post-AEC microphone PCM"] --> ENV_IN["Input envelope"]
    PCM_OUT["Assistant PCM"] --> ENV_OUT["Output envelope"]
    PHASE["Pipecat phase"] --> UI["Material voice presenter"]
    TEXT["Streaming transcripts"] --> UI
    ENV_IN --> UI
    ENV_OUT --> UI
    UI --> RASTER["Reusable RGB888 wave buffers"]
    RASTER --> PPA["Direct-region PPA presentation"]
    PPA --> DSI["DSI frame-boundary handoff"]
```

## Barge-in

During `replying`, post-AEC microphone audio is still transmitted. When speech
is detected:

1. the device sends an interrupt;
2. pending assistant audio is flushed or suppressed;
3. the backend cancels the active response;
4. phase moves directly to `listening`;
5. user audio continues in the same session.

There must not be an intermediate `idle` phase between `replying` and a valid
follow-up. `idle` means the conversation has ended and may resume music, which
would contaminate the next microphone turn.

The `stop` wake-word model is enabled only where product policy needs a spoken
conversation stop. A manual close must call session termination, stop
assistant output, disable AFE, and restore the normal wake-word model.

## Phase ownership

The backend owns conversational phases:

| Phase | UI | Audio policy |
| --- | --- | --- |
| `idle` | Assistant hidden after cleanup | AFE off, normal wake word active, media may resume |
| `listening` | Listening scene and user transcript | AFE on, mic streaming |
| `thinking` | Thinking state; keep Assistant visible | AFE on, media remains paused |
| `replying` | Answering scene and assistant transcript | TTS playing, mic still streaming |
| `thanks` | Short completion state | Drain output, then cleanup |
| error/not ready | Error state and chime | Stop broken session, return to idle wake if possible |

These phases also own display power policy. While Voice is active and the
backend reports `waiting`, `listening`, `thinking`, or `replying`, sleep is
inhibited without modifying the last-interaction timestamp. A manual closing
gesture updates that timestamp and clears wake-from-dark restore intent. After
closing, Home uses the normal touch-based timeout. A stale backend phase must
not keep Home awake after the conversation view has closed.

The device must not invent a `thinking` transition merely because no audio is
currently playing. It follows the backend phase message.

## Native Home Assistant fallback

The ESPHome `voice_assistant` component remains configured for Home Assistant
Assist fallback behavior, timers, and compatibility. It uses the same
post-AFE microphone and assistant speaker. It is not allowed to compete with
the realtime session for microphone or output ownership.

Only one session controller may be active. Product scripts arbitrate wake word,
realtime, and native paths.

## Mixer and media policy

The mixer has two sources:

- `media_mixing_input`, with a 100 ms source buffer;
- `assistant_mixing_input`, with a 1000 ms source buffer.

SendSpin requests lossless mono PCM at 48 kHz. This avoids decoding stereo FLAC
on the P4 only to downmix it later. The SendSpin source owns a bounded 600,000
byte PSRAM buffer and an adjustable initial synchronization delay.

Announcements and assistant audio use the assistant source and duck media by
20 dB. Media is unducked only after:

- assistant output is drained;
- the conversation is truly idle;
- no timer announcement is active.

## Local sounds and amplifier sequencing

Boot, listening, and error sounds are local FLAC assets exposed through
ESPHome's `audio_file` and `media_source.audio_file` components. They use the
same announcement pipeline as voice output; there is no separate ad hoc codec
or I2S writer.

The 2026-09-19 user-provided WAV files are encoded losslessly as mono 48 kHz,
16-bit FLAC to match the mixer, with no runtime sample-rate conversion:

| Event | Asset | Duration | Encoded bytes |
| --- | --- | ---: | ---: |
| Startup, during the final boot phase | `device-startup.flac` | 4.800 s | 180689 |
| Assistant invocation | `confirm.flac` | 2.467 s | 49349 |
| Assistant error | `error.flac` | 2.396 s | 50220 |

The boot sound completes before the existing backlight fade-out. The wait is
bounded at six seconds; a broken audio source must not trap the boot sequence.

The amplifier defaults off. It may be enabled only after:

- I2C codecs are configured;
- I2S channels and DMA buffers exist;
- the output chain has been primed or is ready to receive silence/audio.

This ordering avoids the boot pop caused by exposing codec and DMA startup
transients to the physical speaker.

## Task placement

| Task | Core | Priority | Purpose |
| --- | --- | --- | --- |
| Audio stack | Core 0 by default | 19 | I2S RX/TX and frame processing |
| AFE feed manager | Core 0 | 10 | Move physical frames into ESP-SR |
| AFE processing/fetch | Core 1 | 10 | AEC and processed microphone output |
| Realtime playback drain | Unpinned | 11 | Drain 24 kHz TTS into assistant speaker |
| Realtime microphone TX | Unpinned | 6 | Send microphone chunks over WebSocket |

The audio task is above lwIP priority 18 but below WiFi priority 23. Do not
raise UI workers above it. Visual work may drop/coalesce frames; audio cannot
drop timing deadlines without audible corruption.

## Buffer rules

- Audio rings may live in PSRAM, but I2S DMA descriptors and hardware DMA
  buffers require suitable internal/DMA-capable memory.
- Audio callbacks must not allocate, log verbosely, perform HTTP work, or call
  LVGL.
- Cross-task state is atomic or passed through bounded queues/rings.
- Flush requests are executed by the audio owner, not by concurrently mutating
  ring-buffer internals from the main loop.
- Start/stop must wait for the audio task state machine rather than repeatedly
  creating and deleting I2S tasks.
- AEC reference and microphone frames must remain aligned; changing channel or
  slot mappings requires a loopback test.

## Failure signatures

### Repeated microphone sessions

Static FreeRTOS tasks must not reuse their TCB or free their stack while the
task is still current on either core. A stopped event, or even `eSuspended`,
can be observed before the other core has finished its context switch. The
shared `StaticTask::destroy()` now suspends the task and waits for it to leave
both cores before deletion. This follows the IDF `vTaskDeleteWithCaps` lifetime
rule and is important when microWakeWord is stopped for a conversation.

The direct AFE fetch task keeps its static TCB and stack between sessions. It
suspends after finishing a fetch and is resumed only after that suspension is
observed. Do not self-delete and recreate it in the same static TCB: deferred
IDLE cleanup can still reference that storage. Changing only the AFE task did
not eliminate the observed repeated-open watchdog; keep that distinction in
the validation record.

| Symptom | First suspects |
| --- | --- |
| Wake word works, conversation mic is silent | AFE runtime switch, consumer ownership, stale ring, or session not committing mic |
| Assistant voice is high-pitched | 24/48 kHz format mismatch or duplicate resampling |
| TTS breaks up | Playback prebuffer, audio task starvation, WiFi delivery, or ring underrun |
| Music breaks up only during voice | AFE CPU load, incorrect media pause/duck policy, or PSRAM contention |
| Assistant hears itself | Missing/wrong playback reference, AEC disabled, or reference-frame misalignment |
| Barge-in switches to listening but hears nothing | Output not flushed, mic gate not reopened, or backend immediately sends idle |
| Boot pop | Amplifier enabled before codec/I2S stabilization |
| `Cannot receive audio, buffer is full` | Output not drained or stale session/audio generation |

## Source map

Reusable implementation:

- `esphome/components/audio_processor/`
- `esphome/components/esp_afe/`
- `esphome/components/esp_audio_stack/`
- `pipecat-homeassistant/components/va_pipecat/`
- `esphome/components/sendspin/`

Product configuration and policy:

- `modules/hardware/audio.yaml`
- `modules/voice_assistant/runtime.yaml`
- `modules/player/runtime.yaml`

## Boot chime and media-volume restoration (2026-09-21)

The boot sequence owns the audio-ready gate. Assistant listening/confirmation
and error chimes must require all of the following:

- `boot_sequence_done`;
- `boot_audio_ready`;
- `!ui_snapshot_io_busy`;
- the normal user-facing switch/condition.

This prevents a backend/provider error received while the device is still
building the first Home snapshots from playing an assistant error sound over
the startup sound. It does not hide the provider error from logs.

When Assistant releases the media player, restore the requested device volume
before calling `media_player.play`. Restoring only after the first media
buffer is queued can leave the first part of the resumed stream at the
announcement ducking level. The fix logs requested percentage, output volume,
hot-output volume, and master gain together so a percentage/curve problem can
be separated from a stale mixer state. In the 2026-09-21 COM5 run a 50%
request was restored before playback (`output=0.060`, `hot=0.060`,
`master=1.000`).
