# Architecture decisions

This is a compact decision log for choices that have repeatedly affected
stability or performance. Detailed mechanics live in the subsystem documents.

## Display and graphics

### ADR-G01: Three display-owned frame buffers

**Decision:** The MIPI DSI driver allocates three full-screen RGB888 buffers.
LVGL uses two; manual composition acquires the idle member of the same pool.

**Why:** Two buffers left no safe destination while one frame was scanned and
the other was queued/rendered. A third buffer enables frame-boundary handoff
without allocating a separate full-screen compositor target.

**Cost:** 5.49 MiB of PSRAM for display buffers.

**Reconsider only if:** the driver provides an equivalent ownership primitive
with fewer buffers, or a different panel/controller has internal GRAM.

### ADR-G02: LVGL uses `DIRECT` plus `FULL`

**Decision:** Keep `direct_mode: true`, `full_refresh: true`, and
`buffer_size: 100%`.

**Why:** Direct removes a mandatory staging copy. Full refresh gives each LVGL
frame a complete coherent base and eliminated the persistent artifacts seen
with the partial compositor on RGB888 DSI.

**Cost:** A live LVGL refresh redraws a complete frame.

**Reconsider only if:** a partial path passes the full artifact, ownership,
artwork, Assistant, and stress suite with better measured performance.

### ADR-G03: DMA2D copies, PPA transforms

**Decision:** Use DMA2D for 2D memory copies and PPA SRM for image
scale/rotate/mirror. Use explicit PPA blend only on validated paths.

**Why:** This matches the hardware strengths and avoids CPU pixel loops.

**Constraint:** The generic RGB888 PPA fill/blend draw handlers remain
restricted because they have produced horizontal corruption in cached PSRAM.

### ADR-G04: Direct regions for small continuous motion

**Decision:** Wave, marquee, and volume render into bounded local buffers and
submit only their region through a generation-aware compositor.

**Why:** Invalidating a small control over full-screen artwork caused LVGL to
redraw and transfer much more than the changed pixels.

**Cost:** Each direct widget needs explicit pause/drain/resume lifecycle.

### ADR-G05: Hardware JPEG with leased destinations

**Decision:** Use the ESP32-P4 JPEG peripheral for snapshots, artwork, and
gallery images. Decode into reusable leased RGB888 memory and keep the previous
image visible until replacement succeeds.

**Why:** Software decode is slower and adds CPU pressure. Intermediate
full-screen copies consume PSRAM bandwidth and contiguous memory.

**Constraint:** Hardware decode does not reduce the 1.83 MiB decoded image
size.

## Navigation and snapshots

### ADR-N01: Three raw Home pages plus JPEG backing

**Decision:** Keep a three-slot raw window around the current Home page.
Off-window pages are JPEG-backed.

**Why:** Consecutive swipes need current and neighboring pages immediately.
Keeping every page raw would scale PSRAM linearly with page count.

**Cost:** Window changes may require one encode/decode operation.

### ADR-N02: One shared application work buffer

**Decision:** Store inactive app previews compressed and decode the selected
app into one reusable raw full-screen buffer.

**Why:** One raw preview per app would consume 1.83 MiB per application.

**Constraint:** App preview preparation and artwork/gallery decode must be
serialized when they compete for the same PSRAM transfer budget.

### ADR-N03: Settings bitmap exists only while Settings is open

**Decision:** Preload a bounded raw list snapshot on entry, move it directly
during scroll, refresh it in place after changes, and release it on close.

**Why:** Native LVGL list movement was too slow; global retention would waste
up to 8 MiB when Settings is inactive.

### ADR-N04: Declarative registration, explicit policy

**Decision:** Generic navigation owns gestures, transitions, and display
handoff. Product callbacks own app-specific media, voice, gallery, and overlay
policy.

**Why:** This makes the state machine reusable without teaching it every
application's external side effects.

**Migration target:** Move stable repeated policy into focused application
controllers and continue reducing YAML lambdas.

### ADR-N05: Release drained sources before destination admission

**Decision:** Return the retired application transition's external source lease
before native destination preparation or lifecycle callbacks admit another
framebuffer owner. Keep the final frame and regional pause through destination
preparation; display leases still forbid writes to queued/scanned buffers.

**Why:** Camera's native refresh/direct-session callbacks must not compete
with a source pinned by an animation worker that has already finished.

**Status:** R23's source order, main12/12 and bounded Camera/Volume/accent
scenarios passed. The later warm restart attempt2 failed in SDK shutdown, so
R23 is not accepted. One natural DMA repair remains recorded separately. This
source-order contract adds no task, allocation or SDK policy.

## Audio and voice

### ADR-A01: One physical duplex audio owner

**Decision:** `esp_audio_stack` exclusively owns I2S RX/TX. Media, chimes, and
assistant audio enter through speaker/mixer abstractions.

**Why:** Multiple I2S owners caused startup races, missing audio, and format
drift.

### ADR-A02: AEC is on demand

**Decision:** Keep the AFE configured for full duplex, but enable runtime
processing only during active conversation.

**Why:** Idle wake-word detection does not justify the full AFE CPU cost.

### ADR-A03: Post-AFE microphone is the voice source

**Decision:** Wake word, realtime voice, and native fallback consume the
`voice_microphone` produced by the coordinated stack/AFE path.

**Why:** Realtime barge-in needs echo-reduced microphone audio aligned to the
actual playback reference.

### ADR-A04: Single-microphone low-cost mode for now

**Decision:** Use `fd`, `low_cost`, one microphone, AEC on, and SE/NS/AGC off.

**Why:** The dual-microphone enhancement path consumed too much CPU alongside
realtime audio and UI, while NS carried recognition-quality warnings.

**Reconsider only if:** profiling proves a dual-channel hardware/software path
meets audio, UI, and wake-word budgets.

### ADR-A05: Backend owns conversation phase

**Decision:** Device UI and media policy follow backend
`listening/thinking/replying/thanks/idle` messages.

**Why:** Inferring phase from audio activity ended conversations early,
resumed music during follow-up, and broke barge-in.

## Memory and build

### ADR-M01: Bound allocations and release by phase

**Decision:** Persistent pools are allocated once; large app/image caches use
explicit leases and release points.

**Why:** Free-byte totals hid fragmentation and lifetime overlap. Full-screen
RGB888 allocations require a contiguous 1.92 MB block.

### ADR-M02: Serialize large PSRAM operations

**Decision:** Snapshot encode/decode, artwork replacement, app preview work,
and gallery transitions must not run as independent maximum-burst jobs.

**Why:** They share the PSRAM bus with continuous DSI scanout and audio rings.

### ADR-M03: Native ESP-IDF is the reference build

**Decision:** No required behavior may depend on PlatformIO/SCons patch hooks.
Framework integration belongs in versioned components or framework patches
selected by detected IDF version.

**Why:** Platform-specific build tricks were invisible to ESPHome upstream CI
and produced machine-dependent firmware.

### ADR-M04: Acceleration defaults are conservative upstream

**Decision:** New acceleration or behavior-changing options default off in
upstreamable components. The product enables validated options explicitly.

**Why:** Hardware, formats, alignment, and cache behavior differ across boards.

## Restart and coprocessor lifecycle

### ADR-R01: Explicit reset callback at orderly shutdown

**Status:** Bounded R21/R22/R23 software-restart/boot checks passed, with
R22's extra old-image Hosted shutdown request preserved separately. R22 remains
partial/unaccepted; R23 main/addons passed but the later second warm restart
failed, so R23 is unaccepted and physical cold checks were not requested.

**Decision:** A default-off reusable SDIO component owns one IDF shutdown
callback using SDK reset-pin/polarity metadata. Product configuration enables
it explicitly. Setup registers and validates the callback without changing
GPIO. The shutdown callback changes only the native reset control and requests
a nominal 1 ms ROM delay; it performs no RPC, Hosted teardown or SDIO draining.

**Why:** A normal App shutdown and a direct Hosted `esp_restart` do not share
all higher-level WiFi cleanup, while both can reach IDF shutdown handlers.
The bounded local callback keeps this experiment out of YAML state machines
and avoids adding an RPC dependency during transport/peripheral teardown.

**Boundary:** No GPIO hold or continuity through ROM is promised. Once-only
execution is not cross-core restart serialization; current-boot getters are
not persistent shutdown history. Hardware watchdog/panic resets may bypass
the callback. This does not accept R21 or explain R20's separate watchdog.
Keep the IRAM panic placement diagnostic and SDK error-preservation contract
independent; validate each exact final image on hardware.


### ADR-R02: Default-off, guarded SDK cache-safe restart patch

**Decision:** Keep the P4 orderly-restart change behind
`enable_cache_safe_restart: false` by default. Permit the product to opt in only
with native ESP-IDF5.5.5. Gate the owning SDK source through a generated global
Kconfig option, preserve the disabled code path and reject unknown source hashes.

**Why:** The R23 warm restart campaign exposed a real shutdown Store access fault.
The opt-in change targets the owning P4 shutdown path while preserving
display/application ownership and Hosted/C6 policy. It stalls the other core,
waits on the four cache-sync ENA bits with fences before writeback, and adds no
RTC reset fallback, task or buffer. Source, compiler-object/final-ELF, image,
runtime and physical-power evidence must remain distinct.

This is a local implementation of the stall/cache-idle mechanism described by
Espressif in issue19171. No verified released upstream fix commit has been
identified for a backport claim; source-level similarity is not release provenance.
The patch changes the shared low-level SDK restart/cache path, also reached by
IDF5.5.5 panic_restart. Local hardware evidence exercises orderly software
requests; panic recovery is untested and direct hardware reset is unaffected.

**Status:** R24 exact source/native/ELF checks, initial boot, six bounded
normal software restarts and the twelve-step main suite passed. Its long warm
and physical cold campaigns were not run. R25 keeps this SDK path unchanged;
its initial OTA/boot, first five plus separate persisted restart, main twelve
and specified app/accent addons passed. All fifty controlled software
restarts plus the separate persisted restart and final health passed. The user
confirmed five physical all-power/USB-off cycles. Five distinct captured POWERON
startups have four paired API health checks and a separate late fifth check;
five complete ROM windows are not proved. Both cold monitor deadlines and the
matched-overcast host cardinality failure remain preserved. See validation.md
for this bounded R25 checkpoint; R24 remains a precursor and R23 remains rejected.

## UI implementation

### ADR-U01: Heavy logic belongs in components

**Decision:** YAML describes composition and policy. Buffer management,
per-frame geometry, navigation, and cross-task state belong in reusable C++.

**Why:** Large lambdas were hard to test, duplicated behavior, and encouraged
hardcoded product dimensions.

### ADR-U02: Shared Roboto and Material Symbols

**Decision:** Product text uses shared Roboto variants and standard icons use
Material Symbols Rounded.

**Why:** It keeps typography consistent with the Wear OS Material 3 direction
and avoids unnecessary PNG icon assets.

### ADR-U03: No automatic optimization by visibility

**Decision:** A new page, app, list, or direct widget must be explicitly
registered with its owning controller.

**Why:** Automatic discovery cannot infer lifecycle, external side effects,
snapshot invalidation, or safe buffer release.

