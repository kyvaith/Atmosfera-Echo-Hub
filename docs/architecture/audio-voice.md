# Audio and voice architecture

The device has one coordinated duplex audio transport. Music, local chimes,
assistant playback, microphone capture, and AEC share the same physical I2S
clock domain and must not create independent hardware owners.

## Hardware topology

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
6. Server phase and transcript messages update the overlay.
7. Incoming 24 kHz mono TTS enters a PSRAM playback ring.
8. `assistant_speaker` resamples to the 48 kHz mixer/output path.
9. During reply, microphone streaming remains active for barge-in.
10. Final cleanup disables AFE, restores idle wake words, and resumes media if
    the conversation actually ended.

The playback ring defaults to a 300 ms prebuffer. The backend may tune this at
runtime. The goal is to absorb network jitter without delaying the first audio
more than necessary.

The microphone callback is gated while no conversation is active. It does not
retain or replay pre-roll, so wake chimes and their acoustic tail cannot leak
into the next Pipecat turn. Speech should begin when the listening state is
visible.

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
| `listening` | Listening overlay and user transcript | AFE on, mic streaming |
| `thinking` | Thinking state; keep Assistant visible | AFE on, media remains paused |
| `replying` | Answering state and assistant transcript | TTS playing, mic still streaming |
| `thanks` | Short completion state | Drain output, then cleanup |
| error/not ready | Error state and chime | Stop broken session, return to idle wake if possible |

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
