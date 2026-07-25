# Graphics and display pipeline

This document explains where pixels are produced, which accelerator moves
them, who owns each frame buffer, and why the firmware uses both PPA and
DMA2D.

## Validated display configuration

| Property | Value |
| --- | --- |
| Panel | Waveshare ESP32-P4 3.4-inch round panel |
| Logical size | 800x800 |
| Panel output | RGB888, 24 bits per pixel |
| LVGL color depth | 32-bit color semantics |
| LVGL render mode | `DIRECT` plus `FULL` |
| LVGL refresh period | 10 ms |
| Display clock | 48 MHz |
| DSI lane bitrate | 1.5 Gbps |
| Frame buffers | Three, allocated and owned by the DSI display driver |
| LVGL buffers | Driver frame buffers 0 and 1 |
| Manual-compositor buffer | The currently idle member of the same three-buffer set |
| Byte order | `little_endian`, read from LVGL configuration |

LVGL uses 32-bit color semantics for widgets and sources that need alpha.
The panel scans RGB888, so the final display buffers use three bytes per pixel.
This distinction is important: an ARGB8888 source may be blended into an
RGB888 destination, but the display does not scan a four-byte framebuffer.

## Pixel path

```mermaid
flowchart LR
    OBJECTS["LVGL object tree"]
    DIRECT_WIDGET["Direct widgets<br/>wave, marquee, volume"]
    SNAPSHOT["Home/app/settings snapshots"]
    IMAGE["Artwork and gallery JPEG"]
    LOTTIE["Lottie/ThorVG"]

    SW["LVGL software draw"]
    PPA["ESP32-P4 PPA<br/>SRM, selected blend"]
    DMA2D["ESP32-P4 DMA2D<br/>2D memory copies"]
    JPEG["Hardware JPEG<br/>decode/encode"]

    FB0["DSI frame buffer 0"]
    FB1["DSI frame buffer 1"]
    FB2["DSI frame buffer 2"]
    SCAN["DSI scanout"]

    OBJECTS --> SW
    OBJECTS --> PPA
    DIRECT_WIDGET --> PPA
    SNAPSHOT --> PPA
    SNAPSHOT --> DMA2D
    IMAGE --> JPEG
    JPEG --> PPA
    LOTTIE --> PPA

    SW --> FB0
    SW --> FB1
    PPA --> FB0
    PPA --> FB1
    PPA --> FB2
    DMA2D --> FB0
    DMA2D --> FB1
    DMA2D --> FB2

    FB0 --> SCAN
    FB1 --> SCAN
    FB2 --> SCAN
```

The arrows show possible paths, not simultaneous writes. Buffer ownership
decides which destination is legal for a particular frame.

## Why `DIRECT` and `FULL`

`DIRECT` means LVGL draws into display-driver frame buffers rather than a
separate software staging buffer. It removes a mandatory full-frame copy.

`FULL` means every LVGL refresh produces a complete coherent frame. It costs
more rendering than partial invalidation, but it makes a buffer safe to scan
without copying unchanged areas from another frame. This has proven more
stable on the current RGB888 DSI path than the previous partial-compositor
experiments.

These flags do not mean that every animation must traverse the LVGL object
tree. Snapshot and direct-region compositors can acquire an idle DSI buffer,
compose a complete frame there, and present it manually.

## Triple-buffer ownership

At 800x800 RGB888, one frame buffer is:

```text
800 * 800 * 3 = 1,920,000 bytes = 1.83 MiB
```

The three display-owned buffers therefore occupy 5,760,000 bytes, or about
5.49 MiB.

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Rendering: acquire idle buffer
    Rendering --> Staged: cache sync completed
    Staged --> Queued: queue at frame boundary
    Queued --> Active: DSI begins scanout
    Active --> Idle: next frame becomes active
```

The driver tracks presented, active, queued, and staged indices atomically.
Manual rendering may only acquire a buffer that is none of those active
ownership states.

LVGL normally uses buffers 0 and 1. Buffer 2 is not a fourth hidden copy: it is
the third member of the same display-owned pool and provides an idle target for
snapshot and direct composition. After a manual frame is presented,
`realign_direct_buffer_after_manual_present()` reconnects LVGL to a coherent
base.

In `FULL` mode the next LVGL frame can redraw the entire destination, so a
manual frame does not always need to be copied back into both LVGL buffers. A
caller may request synchronization when the following renderer needs the same
base immediately. Skipping synchronization is valid only when the next owner
guarantees a complete redraw.

## Accelerator responsibilities

### DMA2D

DMA2D is used for deterministic 2D memory movement:

- copying RGB888 spans and complete frames;
- asynchronous LVGL flush/staging work;
- selected application transition operations;
- hardware JPEG support and associated color conversion through the IDF
  integration patch;
- synchronizing complete bases when a consumer explicitly needs it.

The current M2M path batches aligned spans and uses internal-memory
descriptors. Cache synchronization surrounds DMA access. DMA2D is preferred
when the operation is fundamentally a copy and does not require geometric
sampling or alpha composition.

### PPA SRM

PPA scale/rotate/mirror is used for:

- RGB888 snapshot movement;
- image scaling and rotation;
- gallery pan and Ken Burns style transforms;
- direct-region copies;
- Lottie XRGB/ARGB conversion to the RGB888 display target;
- application transition geometry where supported.

SRM is the preferred accelerator for transformed images because it performs
sampling and destination writes without making the CPU touch every pixel.

### PPA blend

PPA blend is used only on validated explicit paths, such as compositing an
ARGB888 direct widget over an RGB888 base.

The generic LVGL RGB888 fill and blend draw-unit handlers remain restricted.
On ESP32-P4 they have produced short horizontal artifacts in cached PSRAM.
`use_ppa_blend: true` therefore means the capability is compiled and safe
explicit paths may use it; it does not mean every LVGL RGB888 blend operation
is routed through hardware.

Masked, rounded, unsupported, or small operations may still fall back to the
LVGL software renderer. This is intentional.

### Selection table

| Operation | Preferred engine | Reason |
| --- | --- | --- |
| Full RGB888 frame copy | DMA2D | Simple 2D copy with bounded descriptors |
| RGB888 image pan/scale/rotate | PPA SRM | Hardware geometric transform |
| ARGB8888 overlay on RGB888 base | Explicit PPA blend | Alpha composition without CPU pixel loop |
| Generic rounded LVGL widget | LVGL software or validated PPA path | Masks and RGB888 correctness take priority |
| JPEG decode/encode | ESP32-P4 JPEG peripheral | Avoid software codec and extra color pass |
| Home/app snapshot movement | PPA/DMA2D direct compositor | Avoid LVGL tree redraw |

## Direct-region compositor

The direct-region compositor updates a small dynamic region while preserving
the rest of the active frame. It is used by the wavy media control, marquee,
and volume overlay.

It owns:

- four registered region slots;
- an eight-request queue;
- a 6 KiB worker stack;
- a generation number for each DSI buffer;
- a barrier used by page and application handoff.

```mermaid
sequenceDiagram
    participant Widget as Direct widget worker
    participant Region as Direct-region compositor
    participant DSI as MIPI DSI driver

    Widget->>Region: submit region and generation
    Region->>DSI: acquire idle frame buffer
    Region->>Region: copy current base if generation is stale
    Region->>Region: PPA copy/blend updated regions
    Region->>DSI: cache sync and queue frame
    DSI-->>Region: frame boundary/presented
```

The generation mechanism prevents a region rendered over an old base from
being presented after LVGL or navigation has changed the screen. Before a
snapshot, page switch, or app transition, navigation pauses the region
compositor and waits on its barrier. Resuming increments the base generation.

No additional full-screen region buffer exists. The compositor uses the three
DSI buffers and bounded per-widget sources.

## Hardware JPEG path

Artwork, gallery images, and compressed snapshots use the ESP32-P4 JPEG
peripheral. The important rules are:

- derive RGB order and byte order from display/LVGL configuration;
- decode into a reusable destination with known stride and capacity;
- avoid an intermediate full-screen RGB buffer when the destination can be
  leased directly;
- synchronize only the written range before PPA, DMA2D, or DSI consumes it;
- keep the old image valid until the replacement is completely decoded;
- publish the new source atomically, then refresh the affected LVGL/direct
  region;
- release the replaced buffer only after no display or worker still references
  it.

The current artwork path reuses active buffer capacity and the gallery keeps a
bounded encoded buffer. A decoded 800x800 RGB888 image still costs 1.83 MiB;
hardware JPEG reduces codec CPU time and compressed storage, not the size of
the displayed pixels.

## Lottie and vector animation

The Lottie JSON is small, but rendering is not free. ThorVG expands the vector
scene into working data and ultimately produces raster pixels. The boot
animation can optionally pre-render frames to PSRAM for stable playback. That
cache is approximately 11 MiB for the current asset and is deliberately:

1. allocated while PSRAM is still contiguous;
2. used for one-shot boot playback;
3. reduced to the final retained frame;
4. released before Home and application caches are completed.

PPA can accelerate conversion and presentation of opaque or alpha frames, but
it does not execute the Lottie vector scene itself. Smooth vector playback
therefore requires either bounded pre-rendering or a sufficiently light scene.

## Cache coherency rules

PSRAM is cached. Hardware engines and the CPU do not automatically see the
same bytes at the same instant.

Use the direction that matches ownership:

- CPU produced data, hardware will read: write back CPU cache to memory.
- Hardware produced data, CPU will read: invalidate CPU cache after hardware
  completion.
- Hardware produced data, another hardware engine will read: wait for the
  producer, synchronize the written range as required by the IDF API, then
  start the consumer.

Never synchronize an arbitrary full buffer merely because a small region
changed. Excessive cache operations consume the same PSRAM bandwidth needed by
DSI scanout.

## Failure signatures

| Symptom | First suspects |
| --- | --- |
| Blue full-screen flash | DSI starvation, illegal buffer ownership, missing frame acknowledgement, or excessive PSRAM/cache traffic |
| Horizontal short lines | RGB888 PPA fill/blend path, stale cache lines, wrong stride, or writing an active frame |
| Random horizontal split | Buffer switch before producer completion or incorrect frame stride |
| Correct frame after touching screen | Source changed without the required LVGL/direct refresh |
| Shifted image | DSI timing/mode mismatch, wrong stride, or source crop coordinates |
| Correct first image, corrupt replacements | Old/new buffer lifetime overlap or incomplete invalidation |
| Animation good until artwork update | Competing PSRAM transfer or direct-region base generation mismatch |

Do not hide these faults with a slower global burst setting until ownership and
coherency have been proven correct.

## Source map

Reusable implementation lives in the ESPHome integration tree:

- `esphome/components/mipi_dsi/mipi_dsi.cpp`
- `esphome/components/mipi_dsi/mipi_dsi.h`
- `esphome/components/lvgl/lvgl_esphome.cpp`
- `esphome/components/lvgl/dma2d_m2m_copy.cpp`
- `esphome/components/lvgl/ppa/`
- `esphome/components/lvgl/lottie_loader.h`
- `esphome/components/lvgl_material/`
- `esphome/components/esp32_jpeg/`

Product configuration lives in:

- `modules/hardware/display.yaml`
- `modules/lvgl/base.yaml`
- `modules/lvgl/material.yaml`
- `modules/player/artwork.yaml`
- `modules/immich/`

