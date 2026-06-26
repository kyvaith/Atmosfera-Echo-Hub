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

### Active Hypothesis

Artwork changes still create too much PSRAM/DMA traffic during display scanout.
The next fixes should reduce duplicated transfers or isolate DMA pressure around the artwork path, not globally slow LVGL.

### Next Checks

- Verify whether full-screen artwork redraw uses PPA SRM even when scale/rotation are 1:1.
- Keep DSI FIFO diagnostics around JPEG decode, LVGL image source swap, and first redraw.
- Compare blue flashes with and without active-buffer JPEG decode using the same firmware baseline.
- Avoid extra staging copies for complete SendSpin JPEG payloads.
