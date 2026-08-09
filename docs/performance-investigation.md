# Performance Investigation Notes

This file keeps a short audit trail for display and artwork performance work.
Every hypothesis should have a measurable outcome before it is kept.

## Artwork Blue Flash

### Current Baseline

- LVGL runs in full/direct mode with a full-size buffer.
- The player artwork is 800x800 RGB565 and is drawn under LVGL overlays.
- Hardware JPEG decoding writes the decoded frame directly into the active artwork image buffer.
- The project keeps `CONFIG_ESPHOME_JPEG_DMA2D_BURST_LENGTH` isolated to the JPEG path.
- Global LVGL/PPA burst length is not overridden.

### Checked

- Global `CONFIG_LV_PPA_BURST_LENGTH` reduction was tested and rejected because it risks lowering general LVGL performance and did not prove a fix.
- PPA SRM source cache sync was measured and was not the dominant cost.
- DSI FIFO can hit zero around artwork update windows even when the standard underrun flag is not raised.
- Placeholder/image color order is correct with little-endian RGB565.
- Plain 1:1 opaque artwork no longer routes through PPA SRM; logs show `srm=0`, but FIFO can still hit zero during hardware JPEG output.
- A two-widget LVGL crossfade was rejected. It invalidated about 3.5 Mpix per
  transition, used 22-25% CPU, and produced 151-168 ms maximum LVGL loops.
- The first direct-scene presenter rendered the active screen in 223-255 ms and
  produced 13-16 PPA blend frames over 632-675 ms. The complete player scene
  now also includes global LVGL layers and preserves live direct regions. Two
  real PLAYING-state artwork swaps prepared in 338-346 ms and produced 10-11
  PPA frames over 668-721 ms, with no DSI underrun or restart. The wave returned
  to about 59 submitted frames/s after each transition instead of being hidden
  for its duration. Idle CPU returned to 1-3%. Visual confirmation on the panel
  remains part of the hardware acceptance test.
- The wavy control no longer converts its 244x244 artwork crop to RGB888 or
  rebuilds all three ARGB wave buffers for each cover. Three RGB565 crops keep
  active, in-flight and next generations separate, and PPA blends RGB565 with
  the background-independent ARGB overlay directly. A four-cover PLAYING-state
  stress test completed every crossfade successfully with no backdrop/handoff
  timeout or restart. During a transition the wave produced 22-64 renders per
  two-second sample and returned to 112-118 afterwards. Its visible cadence is
  still bounded by the 11-12 full-screen crossfade frames over about 0.7 s.
- The incoming scene capture now excludes the native wavy-progress object
  because the direct-region compositor preserves the same wave as ARGB. Four
  consecutive 800x800 artwork swaps advanced the private backdrop generations
  from 6/6 through 9/9; an awake PLAYING-state swap reached 13/13 with no DSI
  underrun. Artwork backdrop replacement uses a mandatory renderer lock, while
  ordinary animation frames retain their short, coalescing try-lock.

### Active Hypothesis

Artwork changes still create too much PSRAM/DMA traffic during display scanout.
The next fixes should reduce duplicated transfers or isolate DMA pressure around the artwork path, not globally slow LVGL.

### Next Checks

- Verify whether full-screen artwork redraw uses PPA SRM even when scale/rotation are 1:1.
- Keep DSI FIFO diagnostics around JPEG decode, LVGL image source swap, and first redraw.
- Compare blue flashes with and without active-buffer JPEG decode using the same firmware baseline.
- Avoid extra staging copies for complete SendSpin JPEG payloads.
- Do not route plain 1:1 opaque images through PPA SRM; reserve SRM for real scale/rotate/mirror work.
- Test JPEG-only DMA2D burst length `1` to reduce PSRAM bus pressure during 800x800 hardware decode.
