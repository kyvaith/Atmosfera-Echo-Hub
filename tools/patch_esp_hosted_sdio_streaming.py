"""Bound ESP-Hosted SDIO reads and isolate RX buffers from display PSRAM."""

# ruff: noqa: F821
# pylint: disable=undefined-variable
from contextlib import suppress
from pathlib import Path

env = None
with suppress(NameError):
    Import("env")  # type: ignore[name-defined]


LIMIT_MARKER = "CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE"
YIELD_MARKER = "let lower-priority application tasks run"
LEGACY_YIELD_BLOCK = """\t\t\tif (data_left != 0) {
\t\t\t\t// Preserve the streaming frame and its SDIO lock, but give the
\t\t\t\t// memory fabric a scheduling boundary between physical reads.
\t\t\t\ttaskYIELD();
\t\t\t}
"""
SCHEDULER_BOUNDARY_BLOCK = """\t\t\tif (data_left != 0) {
\t\t\t\t/* This task runs above ESPHome's loop task. taskYIELD() only
\t\t\t\t * admits equal-priority tasks, so it could still starve LVGL and
\t\t\t\t * trip the task watchdog during sustained RX. Block for one tick
\t\t\t\t * to let lower-priority application tasks run between CMD53 reads. */
\t\t\t\tvTaskDelay(1);
\t\t\t}
"""
FRAME_BOUNDARY_MARKER = "Release the high-priority SDIO task after each complete network frame"
RX_DISPATCH_BOUNDARY_MARKER = (
    "Release the high-priority SDIO dispatch task after each queued packet"
)
RX_INTERNAL_MARKER = "CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_INTERNAL_MEMPOOL"
COMMON_INTERNAL_MARKER = "CONFIG_ESPHOME_ESP_HOSTED_COMMON_INTERNAL_MEMPOOL"
FIFO_GUARD_MARKER = "extern bool esphome_mipi_dsi_wait_vblank_fifo_margin"
FIFO_GUARD_STRICT_MARKER = "DSI vblank guard needed"
FIFO_HELPER_MARKER = "static void sdio_wait_for_dsi_window(size_t transfer_bytes, bool block_transfer)"
FIFO_CONTROL_GUARD_MARKER = "Protect the SDIO control-plane transaction"
FIFO_TX_GUARD_MARKER = "Protect each physical TX payload transaction"
FIFO_RX_COPY_GUARD_MARKER = "Protect the post-SDIO RX copy into the network-owned buffer"
SDIO_TRANSFER_DIAGNOSTICS_MARKER = "Record actual CMD53 occupancy for DSI diagnostics"
RX_NETWORK_INTERNAL_EXPERIMENT = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_NETWORK_INTERNAL) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_NETWORK_INTERNAL
\t\t\t\t/* lwIP retains this payload as a zero-copy PBUF_REF. Keep it in
\t\t\t\t * internal RAM so later TCP/HTTP reads cannot starve DSI's PSRAM
\t\t\t\t * scanout after the physical SDIO transaction has completed. */
\t\t\t\tuint8_t * copy_payload = (uint8_t *)heap_caps_malloc(
\t\t\t\t\tbuf_handle->payload_len, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
#else
\t\t\t\tuint8_t * copy_payload = (uint8_t *)g_h.funcs->_h_malloc(buf_handle->payload_len);
#endif
"""
RX_NETWORK_UPSTREAM_ALLOC = """\t\t\t\tuint8_t * copy_payload = (uint8_t *)g_h.funcs->_h_malloc(buf_handle->payload_len);
"""
RX_NETWORK_INTERNAL_MARKER = "Keep network-owned payloads in internal RAM"
RX_NETWORK_INTERNAL_REPLACEMENT = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_NETWORK_INTERNAL) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_NETWORK_INTERNAL
\t\t\t\t/* Keep network-owned payloads in internal RAM whenever possible. The
\t\t\t\t * physical CMD53 transaction already terminates in an internal DMA
\t\t\t\t * buffer; copying its packet into PSRAM is the stage that competes
\t\t\t\t * with the continuously scanned DSI framebuffer. */
\t\t\t\tuint8_t * copy_payload = (uint8_t *)heap_caps_malloc(
\t\t\t\t\tbuf_handle->payload_len, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
\t\t\t\tif (copy_payload == NULL) {
\t\t\t\t\tcopy_payload = (uint8_t *)g_h.funcs->_h_malloc(buf_handle->payload_len);
\t\t\t\t}
#else
\t\t\t\tuint8_t * copy_payload = (uint8_t *)g_h.funcs->_h_malloc(buf_handle->payload_len);
#endif
"""
POOL_DIAGNOSTICS_MARKER = "ESP-Hosted SDIO RX pool allocation"
STREAM_BUFFER_DIAGNOSTICS_MARKER = "ESP-Hosted SDIO stream buffer"
STREAM_BUFFER_INTERNAL_MARKER = "CONFIG_ESPHOME_ESP_HOSTED_SDIO_STREAM_INTERNAL_MAX"
RX_POOL_PRIORITY_MARKER = "Allocate the raw SDIO RX pool before queue objects"
INCREMENTAL_RX_MARKER = "sdio_incremental_stream_feed"
READ_ANCHOR = """\t\tdo {\n\t\t\tlen_to_read = data_left;\n"""
READ_REPLACEMENT = """\t\tdo {\n\t\t\tlen_to_read = data_left;\n\n#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE > 0
\t\t\tif (len_to_read > CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE) {
\t\t\t\tlen_to_read = CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE;
\t\t\t}
#endif
"""
FIFO_DECLARATION_ANCHOR = """static const char TAG[] = "H_SDIO_DRV";
"""
FIFO_DECLARATION_LEGACY = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
extern bool esphome_mipi_dsi_wait_fifo_margin(uint32_t min_depth,
\tuint32_t timeout_us) __attribute__((weak));
#endif

static const char TAG[] = "H_SDIO_DRV";
"""
FIFO_DECLARATION_VBLANK_V1 = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
extern bool esphome_mipi_dsi_wait_fifo_margin(uint32_t min_depth,
\tuint32_t timeout_us) __attribute__((weak));
extern bool esphome_mipi_dsi_wait_vblank_fifo_margin(uint32_t min_depth,
\tuint32_t timeout_us, uint32_t window_start_us,
\tuint32_t window_end_us) __attribute__((weak));
#endif

static const char TAG[] = "H_SDIO_DRV";
"""
FIFO_DECLARATION_VBLANK_V2 = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
extern bool esphome_mipi_dsi_wait_fifo_margin(uint32_t min_depth,
\tuint32_t timeout_us) __attribute__((weak));
extern bool esphome_mipi_dsi_wait_vblank_fifo_margin(uint32_t min_depth,
\tuint32_t timeout_us, uint32_t window_start_us,
\tuint32_t window_end_us) __attribute__((weak));
extern bool esphome_mipi_dsi_vblank_guard_active(void) __attribute__((weak));
#endif

static const char TAG[] = "H_SDIO_DRV";
"""
FIFO_DECLARATION_RESERVATION_V3 = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
extern bool esphome_mipi_dsi_wait_fifo_margin(uint32_t min_depth,
\tuint32_t timeout_us) __attribute__((weak));
extern bool esphome_mipi_dsi_wait_vblank_fifo_margin(uint32_t min_depth,
\tuint32_t timeout_us, uint32_t window_start_us,
\tuint32_t window_end_us, uint32_t reservation_us) __attribute__((weak));
extern bool esphome_mipi_dsi_vblank_guard_active(void) __attribute__((weak));
#endif

static const char TAG[] = "H_SDIO_DRV";
"""
FIFO_DECLARATION_REPLACEMENT = FIFO_DECLARATION_RESERVATION_V3.replace(
    "extern bool esphome_mipi_dsi_vblank_guard_active(void) __attribute__((weak));\n",
    """extern bool esphome_mipi_dsi_vblank_guard_active(void) __attribute__((weak));
extern void esphome_mipi_dsi_note_sdio_guard(uint32_t wait_us,
\tuint32_t transfer_bytes, bool ready) __attribute__((weak));
extern void esphome_mipi_dsi_note_sdio_transfer(uint32_t duration_us,
\tuint32_t transfer_bytes, bool tx) __attribute__((weak));
""",
    1,
)
FIFO_HELPER_ANCHOR = """static const char TAG[] = "H_SDIO_DRV";
"""
FIFO_HELPER_LEGACY = """static const char TAG[] = "H_SDIO_DRV";

static void sdio_wait_for_dsi_window(void)
{
#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
\tif (esphome_mipi_dsi_vblank_guard_active == NULL ||
\t\t!esphome_mipi_dsi_vblank_guard_active()) {
\t\treturn;
\t}

\tuint32_t dsi_guard_timeouts = 0;
\tbool dsi_window_ready = false;
\tdo {
\t\tif (esphome_mipi_dsi_wait_vblank_fifo_margin != NULL) {
\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_vblank_fifo_margin(
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\t20000, 40, 560);
\t\t} else if (esphome_mipi_dsi_wait_fifo_margin != NULL) {
\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_fifo_margin(
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_WAIT_US);
\t\t} else {
\t\t\tdsi_window_ready = true;
\t\t}
\t\tif (!dsi_window_ready && ++dsi_guard_timeouts == 5) {
\t\t\tESP_LOGW(TAG, "DSI vblank guard needed five wait windows");
\t\t}
\t} while (!dsi_window_ready && esphome_mipi_dsi_vblank_guard_active());
#endif
}
"""
FIFO_HELPER_V2 = """static const char TAG[] = "H_SDIO_DRV";

static void sdio_wait_for_dsi_window(size_t transfer_bytes, bool block_transfer)
{
#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
\tif (esphome_mipi_dsi_vblank_guard_active == NULL ||
\t\t!esphome_mipi_dsi_vblank_guard_active()) {
\t\treturn;
\t}

\t/* Account for the complete physical CMD53 transfer, not just its start.
\t * A fixed latest-start timestamp allowed a large transfer to begin near
\t * the end of vertical blanking and continue into active DSI scanout. */
\tsize_t physical_bytes = transfer_bytes == 0 ? 1 : transfer_bytes;
\tif (block_transfer) {
\t\tphysical_bytes = ((physical_bytes + ESP_BLOCK_SIZE - 1) / ESP_BLOCK_SIZE) * ESP_BLOCK_SIZE;
\t}
\tconst uint32_t bus_width = H_SDIO_BUS_WIDTH > 0 ? H_SDIO_BUS_WIDTH : 1;
\tconst uint64_t clocks_per_second = (uint64_t) H_SDIO_CLOCK_FREQ_KHZ * 1000ULL * bus_width;
\tconst uint32_t wire_time_us = (uint32_t) ((physical_bytes * 8ULL * 1000000ULL +
\t\tclocks_per_second - 1) / clocks_per_second);
\t/* Driver/DMA dispatch and shared-AXI contention make the observed bus
\t * occupancy longer than the ideal wire time. Reserving twice the ideal
\t * duration plus 48 us still leaves several 512-byte transfers per blank. */
\tconst uint32_t completion_reserve_us = 48U + 2U * wire_time_us;
\tconst uint32_t window_end_us = completion_reserve_us < 440U ? 560U - completion_reserve_us : 120U;

\tuint32_t dsi_guard_timeouts = 0;
\tbool dsi_window_ready = false;
\tdo {
\t\tif (esphome_mipi_dsi_wait_vblank_fifo_margin != NULL) {
\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_vblank_fifo_margin(
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\t20000, 40, window_end_us);
\t\t} else if (esphome_mipi_dsi_wait_fifo_margin != NULL) {
\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_fifo_margin(
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_WAIT_US);
\t\t} else {
\t\t\tdsi_window_ready = true;
\t\t}
\t\tif (!dsi_window_ready && ++dsi_guard_timeouts == 5) {
\t\t\tESP_LOGW(TAG, "DSI vblank guard needed five wait windows");
\t\t}
\t} while (!dsi_window_ready && esphome_mipi_dsi_vblank_guard_active());
#else
\t(void) transfer_bytes;
\t(void) block_transfer;
#endif
}
"""
FIFO_HELPER_RESERVATION_V3 = """static const char TAG[] = "H_SDIO_DRV";

static void sdio_wait_for_dsi_window(size_t transfer_bytes, bool block_transfer)
{
#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
\tif (esphome_mipi_dsi_vblank_guard_active == NULL ||
\t\t!esphome_mipi_dsi_vblank_guard_active()) {
\t\treturn;
\t}

\t/* Reserve the complete physical CMD53 occupancy inside vertical blanking.
\t * The reservation is shared by RX, TX and control transactions so several
\t * short commands cannot all start in the same window and collectively run
\t * into active DSI scanout. */
\tsize_t physical_bytes = transfer_bytes == 0 ? 1 : transfer_bytes;
\tif (block_transfer) {
\t\tphysical_bytes = ((physical_bytes + ESP_BLOCK_SIZE - 1) / ESP_BLOCK_SIZE) * ESP_BLOCK_SIZE;
\t}
\tconst uint32_t bus_width = H_SDIO_BUS_WIDTH > 0 ? H_SDIO_BUS_WIDTH : 1;
\tconst uint64_t clocks_per_second = (uint64_t) H_SDIO_CLOCK_FREQ_KHZ * 1000ULL * bus_width;
\tconst uint32_t wire_time_us = (uint32_t) ((physical_bytes * 8ULL * 1000000ULL +
\t\tclocks_per_second - 1) / clocks_per_second);
\tconst uint32_t estimated_occupancy_us = 48U + 2U * wire_time_us;
\tconst uint32_t reservation_us = estimated_occupancy_us < 96U ? 96U : estimated_occupancy_us;
\tconst uint32_t window_start_us = 40U;
\tconst uint32_t window_limit_us = 560U;
\tconst uint32_t usable_window_us = window_limit_us - window_start_us;
\tconst uint32_t bounded_reservation_us =
\t\treservation_us < usable_window_us ? reservation_us : usable_window_us;
\tconst uint32_t window_end_us = window_limit_us - bounded_reservation_us;

\tuint32_t dsi_guard_timeouts = 0;
\tbool dsi_window_ready = false;
\tdo {
\t\tif (esphome_mipi_dsi_wait_vblank_fifo_margin != NULL) {
\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_vblank_fifo_margin(
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\t20000, window_start_us, window_end_us, bounded_reservation_us);
\t\t} else if (esphome_mipi_dsi_wait_fifo_margin != NULL) {
\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_fifo_margin(
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_WAIT_US);
\t\t} else {
\t\t\tdsi_window_ready = true;
\t\t}
\t\tif (!dsi_window_ready && ++dsi_guard_timeouts == 5) {
\t\t\tESP_LOGW(TAG, "DSI vblank guard needed five wait windows");
\t\t}
\t} while (!dsi_window_ready && esphome_mipi_dsi_vblank_guard_active());
#else
\t(void) transfer_bytes;
\t(void) block_transfer;
#endif
}
"""
FIFO_HELPER_REPLACEMENT = FIFO_HELPER_RESERVATION_V3.replace(
    "\tuint32_t dsi_guard_timeouts = 0;\n\tbool dsi_window_ready = false;\n",
    """\tconst int64_t dsi_guard_started_us = esp_timer_get_time();
\tuint32_t dsi_guard_timeouts = 0;
\tbool dsi_window_ready = false;
""",
    1,
).replace(
    "\t} while (!dsi_window_ready && esphome_mipi_dsi_vblank_guard_active());\n",
    """\t} while (!dsi_window_ready && esphome_mipi_dsi_vblank_guard_active());
\tif (esphome_mipi_dsi_note_sdio_guard != NULL) {
\t\tconst uint32_t wait_us = (uint32_t) (esp_timer_get_time() - dsi_guard_started_us);
\t\tesphome_mipi_dsi_note_sdio_guard(wait_us, (uint32_t) physical_bytes, dsi_window_ready);
\t}
""",
    1,
)
FIFO_HELPER_UNBOUNDED_RESERVATION = FIFO_HELPER_REPLACEMENT
FIFO_HELPER_BOUNDED_RESERVATION = FIFO_HELPER_UNBOUNDED_RESERVATION.replace(
    """\tuint32_t dsi_guard_timeouts = 0;
\tbool dsi_window_ready = false;
\tdo {
\t\tif (esphome_mipi_dsi_wait_vblank_fifo_margin != NULL) {
\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_vblank_fifo_margin(
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\t20000, window_start_us, window_end_us, bounded_reservation_us);
\t\t} else if (esphome_mipi_dsi_wait_fifo_margin != NULL) {
\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_fifo_margin(
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_WAIT_US);
\t\t} else {
\t\t\tdsi_window_ready = true;
\t\t}
\t\tif (!dsi_window_ready && ++dsi_guard_timeouts == 5) {
\t\t\tESP_LOGW(TAG, "DSI vblank guard needed five wait windows");
\t\t}
\t} while (!dsi_window_ready && esphome_mipi_dsi_vblank_guard_active());
""",
    """\t/* One attempt already spans a complete display frame. Bound the
\t * outer retry loop so a high-priority SDIO task cannot monopolize both
\t * cores indefinitely when the requested FIFO threshold is unavailable. */
\tconst uint32_t max_guard_attempts = 3;
\tuint32_t dsi_guard_timeouts = 0;
\tbool dsi_window_ready = false;
\tdo {
\t\tif (esphome_mipi_dsi_wait_vblank_fifo_margin != NULL) {
\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_vblank_fifo_margin(
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\t20000, window_start_us, window_end_us, bounded_reservation_us);
\t\t} else if (esphome_mipi_dsi_wait_fifo_margin != NULL) {
\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_fifo_margin(
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_WAIT_US);
\t\t} else {
\t\t\tdsi_window_ready = true;
\t\t}
\t\tif (!dsi_window_ready) {
\t\t\tdsi_guard_timeouts++;
\t\t\tvTaskDelay(1);
\t\t}
\t} while (!dsi_window_ready && esphome_mipi_dsi_vblank_guard_active() &&
\t\tdsi_guard_timeouts < max_guard_attempts);
""",
    1,
)
FIFO_HELPER_REPLACEMENT = FIFO_HELPER_UNBOUNDED_RESERVATION

TX_TRANSACTION_ANCHOR = """#if H_SDIO_TX_BLOCK_ONLY_XFER
\t\t\t/* Extend the transfer length to do block only transfers.
\t\t\t * This is safe as slave only reads up to data_left, which
\t\t\t * is not changed here. Rest of data is discarded by
\t\t\t * slave.
\t\t\t */
\t\t\tuint32_t block_send_len = ((len_to_send + ESP_BLOCK_SIZE - 1) / ESP_BLOCK_SIZE) * ESP_BLOCK_SIZE;

\t\t\tret = g_h.funcs->_h_sdio_write_block(sdio_handle, ESP_SLAVE_CMD53_END_ADDR - data_left,
\t\t\t\tpos, block_send_len, ACQUIRE_LOCK);
#else
\t\t\tret = g_h.funcs->_h_sdio_write_block(sdio_handle, ESP_SLAVE_CMD53_END_ADDR - data_left,
\t\t\t\tpos, len_to_send, ACQUIRE_LOCK);
#endif
"""
TX_TRANSACTION_REPLACEMENT = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
\t\t\t/* Record actual CMD53 occupancy for DSI diagnostics. */
\t\t\tconst int64_t dsi_sdio_tx_started_us = esp_timer_get_time();
#endif
#if H_SDIO_TX_BLOCK_ONLY_XFER
\t\t\t/* Extend the transfer length to do block only transfers.
\t\t\t * This is safe as slave only reads up to data_left, which
\t\t\t * is not changed here. Rest of data is discarded by
\t\t\t * slave.
\t\t\t */
\t\t\tuint32_t block_send_len = ((len_to_send + ESP_BLOCK_SIZE - 1) / ESP_BLOCK_SIZE) * ESP_BLOCK_SIZE;

\t\t\tret = g_h.funcs->_h_sdio_write_block(sdio_handle, ESP_SLAVE_CMD53_END_ADDR - data_left,
\t\t\t\tpos, block_send_len, ACQUIRE_LOCK);
#else
\t\t\tret = g_h.funcs->_h_sdio_write_block(sdio_handle, ESP_SLAVE_CMD53_END_ADDR - data_left,
\t\t\t\tpos, len_to_send, ACQUIRE_LOCK);
#endif
#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
\t\t\tif (esphome_mipi_dsi_note_sdio_transfer != NULL) {
\t\t\t\tesphome_mipi_dsi_note_sdio_transfer(
\t\t\t\t\t(uint32_t) (esp_timer_get_time() - dsi_sdio_tx_started_us), len_to_send, true);
\t\t\t}
#endif
"""

RX_TRANSACTION_ANCHOR = """#if H_SDIO_RX_BLOCK_ONLY_XFER
\t\t\t/* Extend the transfer length to do block only transfers.
\t\t\t * This is safe as slave will pad data with 0, which we
\t\t\t * will ignore.
\t\t\t */
\t\t\tuint32_t block_read_len = ((len_to_read + ESP_BLOCK_SIZE - 1) / ESP_BLOCK_SIZE) * ESP_BLOCK_SIZE;
\t\t\tret = g_h.funcs->_h_sdio_read_block(sdio_handle,
\t\t\t\t\tESP_SLAVE_CMD53_END_ADDR - data_left,
\t\t\t\t\tpos, block_read_len, ACQUIRE_LOCK);
#else
\t\t\tret = g_h.funcs->_h_sdio_read_block(sdio_handle,
\t\t\t\t\tESP_SLAVE_CMD53_END_ADDR - data_left,
\t\t\t\t\tpos, len_to_read, ACQUIRE_LOCK);
#endif
"""
RX_TRANSACTION_REPLACEMENT = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
\t\t\t/* Record actual CMD53 occupancy for DSI diagnostics. */
\t\t\tconst int64_t dsi_sdio_rx_started_us = esp_timer_get_time();
#endif
#if H_SDIO_RX_BLOCK_ONLY_XFER
\t\t\t/* Extend the transfer length to do block only transfers.
\t\t\t * This is safe as slave will pad data with 0, which we
\t\t\t * will ignore.
\t\t\t */
\t\t\tuint32_t block_read_len = ((len_to_read + ESP_BLOCK_SIZE - 1) / ESP_BLOCK_SIZE) * ESP_BLOCK_SIZE;
\t\t\tret = g_h.funcs->_h_sdio_read_block(sdio_handle,
\t\t\t\t\tESP_SLAVE_CMD53_END_ADDR - data_left,
\t\t\t\t\tpos, block_read_len, ACQUIRE_LOCK);
#else
\t\t\tret = g_h.funcs->_h_sdio_read_block(sdio_handle,
\t\t\t\t\tESP_SLAVE_CMD53_END_ADDR - data_left,
\t\t\t\t\tpos, len_to_read, ACQUIRE_LOCK);
#endif
#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
\t\t\tif (esphome_mipi_dsi_note_sdio_transfer != NULL) {
\t\t\t\tesphome_mipi_dsi_note_sdio_transfer(
\t\t\t\t\t(uint32_t) (esp_timer_get_time() - dsi_sdio_rx_started_us), len_to_read, false);
\t\t\t}
#endif
"""
FIFO_GUARD_ANCHOR = """#if H_SDIO_RX_BLOCK_ONLY_XFER
\t\t\t/* Extend the transfer length to do block only transfers.
"""
FIFO_GUARD_LEGACY = """#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
\t\t\tif (esphome_mipi_dsi_wait_fifo_margin != NULL) {
\t\t\t\tesphome_mipi_dsi_wait_fifo_margin(
\t\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_WAIT_US);
\t\t\t}
#endif

#if H_SDIO_RX_BLOCK_ONLY_XFER
\t\t\t/* Extend the transfer length to do block only transfers.
"""
FIFO_GUARD_VBLANK_V1 = """#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
\t\t\tif (esphome_mipi_dsi_wait_vblank_fifo_margin != NULL) {
\t\t\t\tesphome_mipi_dsi_wait_vblank_fifo_margin(
\t\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\t\t20000, 40, 560);
\t\t\t} else
\t\t\tif (esphome_mipi_dsi_wait_fifo_margin != NULL) {
\t\t\t\tesphome_mipi_dsi_wait_fifo_margin(
\t\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_WAIT_US);
\t\t\t}
#endif

#if H_SDIO_RX_BLOCK_ONLY_XFER
\t\t\t/* Extend the transfer length to do block only transfers.
"""
FIFO_GUARD_STRICT_V2 = """#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN > 0
\t\t\tif (esphome_mipi_dsi_vblank_guard_active != NULL &&
\t\t\t\tesphome_mipi_dsi_vblank_guard_active()) {
\t\t\t\tuint32_t dsi_guard_timeouts = 0;
\t\t\t\tbool dsi_window_ready = false;
\t\t\t\tdo {
\t\t\t\t\tif (esphome_mipi_dsi_wait_vblank_fifo_margin != NULL) {
\t\t\t\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_vblank_fifo_margin(
\t\t\t\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\t\t\t\t20000, 40, 560);
\t\t\t\t\t} else if (esphome_mipi_dsi_wait_fifo_margin != NULL) {
\t\t\t\t\t\tdsi_window_ready = esphome_mipi_dsi_wait_fifo_margin(
\t\t\t\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_MIN,
\t\t\t\t\t\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_DSI_FIFO_WAIT_US);
\t\t\t\t\t} else {
\t\t\t\t\t\tdsi_window_ready = true;
\t\t\t\t\t}
\t\t\t\t\tif (!dsi_window_ready && ++dsi_guard_timeouts == 5) {
\t\t\t\t\t\tESP_LOGW(TAG, "DSI vblank guard needed five wait windows");
\t\t\t\t\t}
\t\t\t\t} while (!dsi_window_ready &&
\t\t\t\t\tesphome_mipi_dsi_vblank_guard_active());
\t\t\t}
#endif

#if H_SDIO_RX_BLOCK_ONLY_XFER
\t\t\t/* Extend the transfer length to do block only transfers.
"""
FIFO_GUARD_REPLACEMENT = """\t\t\t/* Protect each physical RX payload transaction. */
\t\t\tsdio_wait_for_dsi_window(len_to_read, true);

#if H_SDIO_RX_BLOCK_ONLY_XFER
\t\t\t/* Extend the transfer length to do block only transfers.
"""
FIFO_GUARD_LEGACY_CALL = """\t\t\t/* Protect each physical RX payload transaction. */
\t\t\tsdio_wait_for_dsi_window();
"""
CONTROL_WRAPPER_ANCHORS = (
    """\treturn g_h.funcs->_h_sdio_write_reg(sdio_handle, HOST_TO_SLAVE_INTR, &intr_mask,
\t\tsizeof(intr_mask), ACQUIRE_LOCK);
""",
    """\treturn g_h.funcs->_h_sdio_read_reg(sdio_handle, ESP_SLAVE_INT_RAW_REG, (uint8_t *)interrupts,
\t\tsizeof(uint32_t), ACQUIRE_LOCK);
""",
    """\treturn g_h.funcs->_h_sdio_write_reg(sdio_handle, ESP_SLAVE_INT_CLR_REG, (uint8_t *)&interrupts,
\t\tsizeof(uint32_t), ACQUIRE_LOCK);
""",
    """\tret = g_h.funcs->_h_sdio_read_reg(sdio_handle, ESP_SLAVE_TOKEN_RDATA, (uint8_t *)&len,
\t\tsizeof(len), is_lock_needed);
""",
    """\treturn g_h.funcs->_h_sdio_read_reg(sdio_handle, ESP_SLAVE_INT_RAW_REG, buf, REG_BUF_LEN, ACQUIRE_LOCK);
""",
    """\tret = g_h.funcs->_h_sdio_read_reg(sdio_handle, ESP_SLAVE_PACKET_LEN_REG,
\t\t(uint8_t *)&len, sizeof(len), is_lock_needed);
""",
)
CONTROL_WRAPPER_LEGACY_REPLACEMENTS = tuple(
    "\t/* Protect the SDIO control-plane transaction. */\n"
    "\tsdio_wait_for_dsi_window();\n" + anchor
    for anchor in CONTROL_WRAPPER_ANCHORS
)
CONTROL_WRAPPER_SIZES = (
    "sizeof(intr_mask)",
    "sizeof(uint32_t)",
    "sizeof(uint32_t)",
    "sizeof(len)",
    "REG_BUF_LEN",
    "sizeof(len)",
)
CONTROL_WRAPPER_REPLACEMENTS = tuple(
    "\t/* Protect the SDIO control-plane transaction. */\n"
    f"\tsdio_wait_for_dsi_window({size}, false);\n" + anchor
    for anchor, size in zip(CONTROL_WRAPPER_ANCHORS, CONTROL_WRAPPER_SIZES)
)
TX_GUARD_ANCHOR = """\t\tdo {
\t\t\tlen_to_send = data_left;

#if H_SDIO_TX_BLOCK_ONLY_XFER
"""
TX_GUARD_REPLACEMENT = """\t\tdo {
\t\t\tlen_to_send = data_left;

\t\t\t/* Protect each physical TX payload transaction. */
\t\t\tsdio_wait_for_dsi_window(len_to_send, true);

#if H_SDIO_TX_BLOCK_ONLY_XFER
"""
TX_GUARD_LEGACY_CALL = """\t\t\t/* Protect each physical TX payload transaction. */
\t\t\tsdio_wait_for_dsi_window();
"""
TX_GUARD_CURRENT_CALL = """\t\t\t/* Protect each physical TX payload transaction. */
\t\t\tsdio_wait_for_dsi_window(len_to_send, true);

"""
RX_GUARD_CURRENT_CALL = """\t\t\t/* Protect each physical RX payload transaction. */
\t\t\tsdio_wait_for_dsi_window(len_to_read, true);

"""
RX_COPY_GUARD_ANCHOR = """\t\t\t\tassert(buf_handle->payload);
\t\t\t\tmemcpy(copy_payload, buf_handle->payload, buf_handle->payload_len);
"""
RX_COPY_GUARD_LEGACY_REPLACEMENT = """\t\t\t\tassert(buf_handle->payload);
\t\t\t\t/* The destination is network-owned and, for MTU-sized packets, is
\t\t\t\t * normally allocated in PSRAM. Reserve a separate display-safe
\t\t\t\t * window: the physical SDIO read may have consumed the previous one. */
\t\t\t\t/* Protect the post-SDIO RX copy into the network-owned buffer. */
\t\t\t\tsdio_wait_for_dsi_window(buf_handle->payload_len, false);
\t\t\t\tmemcpy(copy_payload, buf_handle->payload, buf_handle->payload_len);
"""
RX_COPY_GUARD_REPLACEMENT = """\t\t\t\tassert(buf_handle->payload);
\t\t\t\t/* Only a fallback allocation in external RAM competes with DSI.
\t\t\t\t * CMD53 itself and internal-memory copies use separate paths and must
\t\t\t\t * not be delayed behind the display's vblank scheduler. */
\t\t\t\t/* Protect the post-SDIO RX copy into the network-owned buffer. */
\t\t\t\tif (esp_ptr_external_ram(copy_payload)) {
\t\t\t\t\tsdio_wait_for_dsi_window(buf_handle->payload_len, false);
\t\t\t\t}
\t\t\t\tmemcpy(copy_payload, buf_handle->payload, buf_handle->payload_len);
"""
MODE_ANCHOR = """#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE
\tESP_LOGI(TAG, "SDIO Host operating in STREAMING MODE");
"""
MODE_REPLACEMENT = """#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE
\tESP_LOGI(TAG, "SDIO Host operating in STREAMING MODE");
#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE > 0
\tESP_LOGI(TAG, "SDIO streaming RX transaction limit: %u bytes",
\t\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE);
#endif
"""
ADVANCE_ANCHOR = """\t\t\tdata_left -= len_to_read;\n\t\t\tpos += len_to_read;\n"""
ADVANCE_REPLACEMENT = """\t\t\tdata_left -= len_to_read;\n\t\t\tpos += len_to_read;
#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE > 0
""" + SCHEDULER_BOUNDARY_BLOCK + """#endif
"""
FRAME_BOUNDARY_ANCHOR = """\t\tSDIO_DRV_UNLOCK();

\t\t//TODO: unclear, on failure case
"""
FRAME_BOUNDARY_REPLACEMENT = """\t\tSDIO_DRV_UNLOCK();

#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE > 0
\t\t/* Release the high-priority SDIO task after each complete network frame.
\t\t * taskYIELD() only admits equal-priority tasks, so sustained SendSpin RX
\t\t * could monopolize the memory fabric for seconds even though every CMD53
\t\t * transfer individually passed the DSI FIFO guard. One RTOS tick here is
\t\t * outside the SDIO lock and still leaves ample throughput for lossless
\t\t * audio while giving DSI/LVGL a deterministic recovery window. */
\t\tvTaskDelay(1);
#endif

\t\t//TODO: unclear, on failure case
"""
RX_DISPATCH_BOUNDARY_ANCHOR = """\t\tif (!buf_handle->payload_zcopy) {
\t\t\tH_FREE_PTR_WITH_FUNC(buf_handle->free_buf_handle,
\t\t\t\tbuf_handle->priv_buffer_handle);
\t\t}
\t}
}
"""
RX_DISPATCH_BOUNDARY_REPLACEMENT = """\t\tif (!buf_handle->payload_zcopy) {
\t\t\tH_FREE_PTR_WITH_FUNC(buf_handle->free_buf_handle,
\t\t\t\tbuf_handle->priv_buffer_handle);
\t\t}

#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE > 0
\t\t/* Release the high-priority SDIO dispatch task after each queued packet.
\t\t * The queue semaphore can remain ready indefinitely under sustained Wi-Fi
\t\t * RX, otherwise this priority-23 task can starve ESPHome's loop task even
\t\t * though the physical SDIO reader already yields between frames. */
\t\tvTaskDelay(1);
#endif
\t}
}
"""
INCLUDE_ANCHOR = """#include "transport_util.h"\n"""
INCLUDE_REPLACEMENT = """#include "transport_util.h"
#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_INTERNAL_MEMPOOL) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_INTERNAL_MEMPOOL
#include "esp_heap_caps.h"
#include "esp_memory_utils.h"
#include "esp_rom_sys.h"
#endif
"""
MEMPOOL_FUNCTION_ANCHOR = """static inline void sdio_mempool_create(int tx_q_size, int rx_q_size)
{
"""
MEMPOOL_FUNCTION_REPLACEMENT = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_INTERNAL_MEMPOOL) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_INTERNAL_MEMPOOL
static void *sdio_rx_internal_malloc(size_t size, hosted_mem_cap_t cap)
{
\tuint32_t caps = MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT;
\tif (cap == HOSTED_MEM_CAP_DMA) {
\t\tcaps |= MALLOC_CAP_DMA;
\t}
\tvoid *ptr = heap_caps_aligned_alloc(HOSTED_MEM_ALIGNMENT_64, size, caps);
\tif (!ptr) {
\t\t/* Preserve the upstream fallback if internal DMA RAM is fragmented. */
\t\tptr = transport_util_malloc(size, cap);
\t}
\treturn ptr;
}
#endif

static inline void sdio_mempool_create(int tx_q_size, int rx_q_size)
{
"""
MEMPOOL_FUNCTION_WITH_DIAGNOSTICS = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_INTERNAL_MEMPOOL) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_INTERNAL_MEMPOOL
static void *sdio_rx_internal_malloc(size_t size, hosted_mem_cap_t cap)
{
\tuint32_t caps = MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT;
\tif (cap == HOSTED_MEM_CAP_DMA) {
\t\tcaps |= MALLOC_CAP_DMA;
\t}
\tbool used_fallback = false;
\tvoid *ptr = heap_caps_aligned_alloc(HOSTED_MEM_ALIGNMENT_64, size, caps);
\tif (!ptr) {
\t\t/* Preserve the upstream fallback if internal DMA RAM is fragmented. */
\t\tused_fallback = true;
\t\tptr = transport_util_malloc(size, cap);
\t}
\tesp_rom_printf("ESP-Hosted SDIO RX pool allocation: %u bytes, memory=%s, ptr=%p\\n",
\t\t(unsigned) size, used_fallback ? "fallback" : "internal DMA", ptr);
\treturn ptr;
}
#endif

static inline void sdio_mempool_create(int tx_q_size, int rx_q_size)
{
"""
MEMPOOL_ALLOC_ANCHOR = """\t\t.malloc = transport_util_malloc,\n\t\t.calloc = transport_util_calloc,\n"""
MEMPOOL_ALLOC_REPLACEMENT = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_INTERNAL_MEMPOOL) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_INTERNAL_MEMPOOL
\t\t.malloc = sdio_rx_internal_malloc,
#else
\t\t.malloc = transport_util_malloc,
#endif
\t\t.calloc = transport_util_calloc,
"""
COMMON_INCLUDE_ANCHOR = """#include "transport_util.h"\n"""
COMMON_INCLUDE_REPLACEMENT = """#include "transport_util.h"
#if defined(CONFIG_ESPHOME_ESP_HOSTED_COMMON_INTERNAL_MEMPOOL) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_COMMON_INTERNAL_MEMPOOL
#include "esp_heap_caps.h"
#include "esp_rom_sys.h"
#endif
"""
COMMON_FUNCTION_ANCHOR = """static hosted_mempool_t * transport_drv_common_mempool_create(void)
{
"""
COMMON_FUNCTION_REPLACEMENT = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_COMMON_INTERNAL_MEMPOOL) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_COMMON_INTERNAL_MEMPOOL
static void *transport_common_internal_malloc(size_t size, hosted_mem_cap_t cap)
{
\tuint32_t caps = MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT;
\tif (cap == HOSTED_MEM_CAP_DMA) {
\t\tcaps |= MALLOC_CAP_DMA;
\t}
\tvoid *ptr = heap_caps_aligned_alloc(HOSTED_MEM_ALIGNMENT_64, size, caps);
\tif (!ptr) {
\t\tptr = transport_util_malloc(size, cap);
\t}
\treturn ptr;
}
#endif

static hosted_mempool_t * transport_drv_common_mempool_create(void)
{
"""
COMMON_FUNCTION_WITH_DIAGNOSTICS = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_COMMON_INTERNAL_MEMPOOL) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_COMMON_INTERNAL_MEMPOOL
static void *transport_common_internal_malloc(size_t size, hosted_mem_cap_t cap)
{
\tuint32_t caps = MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT;
\tif (cap == HOSTED_MEM_CAP_DMA) {
\t\tcaps |= MALLOC_CAP_DMA;
\t}
\tbool used_fallback = false;
\tvoid *ptr = heap_caps_aligned_alloc(HOSTED_MEM_ALIGNMENT_64, size, caps);
\tif (!ptr) {
\t\tused_fallback = true;
\t\tptr = transport_util_malloc(size, cap);
\t}
\tesp_rom_printf("ESP-Hosted common RX pool allocation: %u bytes, memory=%s, ptr=%p\\n",
\t\t(unsigned) size, used_fallback ? "fallback" : "internal DMA", ptr);
\treturn ptr;
}
#endif

static hosted_mempool_t * transport_drv_common_mempool_create(void)
{
"""
COMMON_ALLOC_ANCHOR = """\t\t\t.malloc = transport_util_malloc,
\t\t\t.calloc = transport_util_calloc,
"""
COMMON_ALLOC_REPLACEMENT = """#if defined(CONFIG_ESPHOME_ESP_HOSTED_COMMON_INTERNAL_MEMPOOL) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_COMMON_INTERNAL_MEMPOOL
\t\t\t.malloc = transport_common_internal_malloc,
#else
\t\t\t.malloc = transport_util_malloc,
#endif
\t\t\t.calloc = transport_util_calloc,
"""
STREAM_BUFFER_ALLOC_ANCHOR = """\t\t*buf = (uint8_t *)g_h.funcs->_h_malloc_align(len, HOSTED_MEM_ALIGNMENT_64);
\t\tassert(*buf);
\t\tdouble_buf.buffer[index].buf_size = len;
"""
STREAM_BUFFER_ALLOC_DIAGNOSTIC = """\t\t*buf = (uint8_t *)g_h.funcs->_h_malloc_align(len, HOSTED_MEM_ALIGNMENT_64);
\t\tassert(*buf);
\t\tesp_rom_printf("ESP-Hosted SDIO stream buffer[%d]: %u bytes, memory=%s, ptr=%p\\n",
\t\t\tindex, (unsigned) len, esp_ptr_external_ram(*buf) ? "PSRAM" :
\t\t\t(esp_ptr_internal(*buf) ? "internal" : "other"), *buf);
\t\tdouble_buf.buffer[index].buf_size = len;
"""
STREAM_BUFFER_ALLOC_REPLACEMENT = """\t\tuint8_t *new_buf = NULL;
#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_STREAM_INTERNAL_MAX) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_STREAM_INTERNAL_MAX > 0
\t\tif (len <= CONFIG_ESPHOME_ESP_HOSTED_SDIO_STREAM_INTERNAL_MAX) {
\t\t\tnew_buf = (uint8_t *)heap_caps_aligned_alloc(
\t\t\t\tHOSTED_MEM_ALIGNMENT_64, len,
\t\t\t\tMALLOC_CAP_INTERNAL | MALLOC_CAP_DMA | MALLOC_CAP_8BIT);
\t\t}
#endif
\t\tif (new_buf == NULL) {
\t\t\tnew_buf = (uint8_t *)g_h.funcs->_h_malloc_align(
\t\t\t\tlen, HOSTED_MEM_ALIGNMENT_64);
\t\t}
\t\t*buf = new_buf;
\t\tassert(*buf);
\t\tesp_rom_printf("ESP-Hosted SDIO stream buffer[%d]: %u bytes, memory=%s, ptr=%p\\n",
\t\t\tindex, (unsigned) len, esp_ptr_external_ram(*buf) ? "PSRAM" :
\t\t\t(esp_ptr_internal(*buf) ? "internal" : "other"), *buf);
\t\tdouble_buf.buffer[index].buf_size = len;
"""
RX_POOL_LATE_ANCHOR = """\n\tsdio_mempool_create(tx_queue_size, rx_queue_size);\n"""
RX_POOL_EARLY_ANCHOR = """\t/* register callback */\n\n"""
RX_POOL_EARLY_REPLACEMENT = """\t/* register callback */

	/* Allocate the raw SDIO RX pool before queue objects fragment internal RAM. */
	sdio_mempool_create(tx_queue_size, rx_queue_size);

"""
MEMPOOL_FUNCTION_WITH_EARLY_DIAGNOSTICS = (
    MEMPOOL_FUNCTION_WITH_DIAGNOSTICS.replace(
        '\tesp_rom_printf("ESP-Hosted SDIO RX pool allocation: %u bytes, memory=%s, ptr=%p\\n",\n'
        '\t\t(unsigned) size, used_fallback ? "fallback" : "internal DMA", ptr);',
        '\tESP_EARLY_LOGW(TAG, "ESP-Hosted SDIO RX pool allocation: %u bytes, memory=%s",\n'
        '\t\t(unsigned) size, used_fallback ? "fallback" : "internal DMA");',
    )
)
COMMON_FUNCTION_WITH_EARLY_DIAGNOSTICS = (
    COMMON_FUNCTION_WITH_DIAGNOSTICS.replace(
        '\tesp_rom_printf("ESP-Hosted common RX pool allocation: %u bytes, memory=%s, ptr=%p\\n",\n'
        '\t\t(unsigned) size, used_fallback ? "fallback" : "internal DMA", ptr);',
        '\tESP_EARLY_LOGW(TAG, "ESP-Hosted common RX pool allocation: %u bytes, memory=%s",\n'
        '\t\t(unsigned) size, used_fallback ? "fallback" : "internal DMA");',
    )
)

INCREMENTAL_HELPER_ANCHOR = """\treturn ESP_OK;
}
#endif

// double buffer task to transfer data from the current buffer to the queue
"""
INCREMENTAL_HELPER_REPLACEMENT = """\treturn ESP_OK;
}

#if defined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX
typedef struct {
\tuint8_t *packet;
\tuint32_t packet_bytes;
\tuint32_t packet_size;
\tbool failed;
} sdio_incremental_stream_t;

static uint8_t sdio_incremental_rx_chunk[CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE]
\t__attribute__((aligned(HOSTED_MEM_ALIGNMENT_64)));

static bool sdio_incremental_stream_feed(sdio_incremental_stream_t *stream,
\t\tconst uint8_t *data, uint32_t data_len)
{
\twhile (data_len != 0) {
\t\tif (stream->packet == NULL) {
\t\t\tstream->packet = sdio_buffer_alloc(MEMSET_REQUIRED);
\t\t\tif (stream->packet == NULL) {
\t\t\t\tif (!mempool_oom_logged) {
\t\t\t\t\tESP_LOGW(TAG, "mempool OOM start (incremental RX)");
\t\t\t\t\tmempool_oom_logged = true;
\t\t\t\t}
\t\t\t\tstream->failed = true;
\t\t\t\treturn false;
\t\t\t}
\t\t\tstream->packet_bytes = 0;
\t\t\tstream->packet_size = 0;
\t\t}

\t\tif (stream->packet_size == 0) {
\t\t\tconst uint32_t header_left = sizeof(struct esp_payload_header) - stream->packet_bytes;
\t\t\tconst uint32_t copy_len = H_MIN(data_len, header_left);
\t\t\tmemcpy(stream->packet + stream->packet_bytes, data, copy_len);
\t\t\tstream->packet_bytes += copy_len;
\t\t\tdata += copy_len;
\t\t\tdata_len -= copy_len;

\t\t\tif (stream->packet_bytes < sizeof(struct esp_payload_header)) {
\t\t\t\tcontinue;
\t\t\t}

\t\t\tstruct esp_payload_header *header = (struct esp_payload_header *) stream->packet;
\t\t\tconst uint16_t payload_len = le16toh(header->len);
\t\t\tconst uint16_t payload_offset = le16toh(header->offset);
\t\t\tif (payload_len == 0 || payload_len > MAX_PAYLOAD_SIZE ||
\t\t\t\tpayload_offset != sizeof(struct esp_payload_header)) {
\t\t\t\tESP_LOGE(TAG, "invalid incremental RX header: len=%u offset=%u",
\t\t\t\t\tpayload_len, payload_offset);
\t\t\t\tsdio_buffer_free(stream->packet);
\t\t\t\tstream->packet = NULL;
\t\t\t\tstream->failed = true;
\t\t\t\treturn false;
\t\t\t}
\t\t\tstream->packet_size = payload_len + payload_offset;
\t\t}

\t\tconst uint32_t packet_left = stream->packet_size - stream->packet_bytes;
\t\tconst uint32_t copy_len = H_MIN(data_len, packet_left);
\t\tmemcpy(stream->packet + stream->packet_bytes, data, copy_len);
\t\tstream->packet_bytes += copy_len;
\t\tdata += copy_len;
\t\tdata_len -= copy_len;

\t\tif (stream->packet_bytes == stream->packet_size) {
\t\t\tuint16_t payload_len = 0;
\t\t\tuint16_t payload_offset = 0;
\t\t\tif (!is_valid_sdio_rx_packet(stream->packet, &payload_len, &payload_offset) ||
\t\t\t\tsdio_push_pkt_to_queue(stream->packet, payload_len, payload_offset) != ESP_OK) {
\t\t\t\tsdio_buffer_free(stream->packet);
\t\t\t\tstream->packet = NULL;
\t\t\t\tstream->failed = true;
\t\t\t\treturn false;
\t\t\t}
\t\t\tstream->packet = NULL;
\t\t\tstream->packet_bytes = 0;
\t\t\tstream->packet_size = 0;
\t\t\tif (mempool_oom_logged) {
\t\t\t\tESP_LOGW(TAG, "mempool OOM end");
\t\t\t\tmempool_oom_logged = false;
\t\t\t}
\t\t}
\t}
\treturn true;
}

static bool sdio_incremental_stream_finish(sdio_incremental_stream_t *stream, bool transport_ok)
{
\tconst bool complete = transport_ok && !stream->failed && stream->packet == NULL &&
\t\tstream->packet_bytes == 0;
\tif (!complete && transport_ok && !stream->failed) {
\t\tESP_LOGE(TAG, "truncated incremental RX packet: received=%lu expected=%lu",
\t\t\t(unsigned long) stream->packet_bytes, (unsigned long) stream->packet_size);
\t}
\tif (stream->packet != NULL) {
\t\tsdio_buffer_free(stream->packet);
\t}
\tmemset(stream, 0, sizeof(*stream));
\treturn complete;
}
#endif
#endif

// double buffer task to transfer data from the current buffer to the queue
"""

INCREMENTAL_LOCAL_ANCHOR = """\tuint32_t interrupts;

#if DO_COMBINED_REG_READ
"""
INCREMENTAL_LOCAL_REPLACEMENT = """\tuint32_t interrupts;
#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX
\tsdio_incremental_stream_t incremental_stream = {0};
#endif

#if DO_COMBINED_REG_READ
"""

INCREMENTAL_BUFFER_ANCHOR = """\t\t/* Allocate rx buffer */
\t\trxbuff = sdio_rx_get_buffer(len_from_slave);
\t\tassert(rxbuff);

\t\tdata_left = len_from_slave;
\t\tpos = rxbuff;
"""
INCREMENTAL_BUFFER_REPLACEMENT = """\t\t/* Incremental mode avoids the large, reallocating stream double buffer. */
#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX
\t\tmemset(&incremental_stream, 0, sizeof(incremental_stream));
\t\trxbuff = sdio_incremental_rx_chunk;
#else
\t\trxbuff = sdio_rx_get_buffer(len_from_slave);
\t\tassert(rxbuff);
#endif

\t\tdata_left = len_from_slave;
\t\tpos = rxbuff;
"""

INCREMENTAL_ADVANCE_ANCHOR = """\t\t\tdata_left -= len_to_read;
\t\t\tpos += len_to_read;
#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE > 0
""" + SCHEDULER_BOUNDARY_BLOCK + """#endif
"""
INCREMENTAL_ADVANCE_REPLACEMENT = """#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX
\t\t\tif (!sdio_incremental_stream_feed(&incremental_stream, pos, len_to_read)) {
\t\t\t\tret = ESP_FAIL;
\t\t\t\tbreak;
\t\t\t}
#endif
\t\t\tdata_left -= len_to_read;
#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX
\t\t\tpos = rxbuff;
#else
\t\t\tpos += len_to_read;
#endif
#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_RX_CHUNK_SIZE > 0
""" + SCHEDULER_BOUNDARY_BLOCK + """#endif
"""

INCREMENTAL_HANDOFF_ANCHOR = """\t\tif (unlikely(ret))
\t\t\tcontinue;

\t\tif (double_buf.read_index < 0) {
\t\t\tdouble_buf.read_index = double_buf.write_index;
\t\t\tdouble_buf.read_data_len = len_from_slave;
\t\t\tdouble_buf.write_index = (double_buf.write_index) ? 0 : 1;
\t\t\t// trigger task to copy data to queue
\t\t\tg_h.funcs->_h_post_semaphore(sem_double_buf_xfer_data);
\t\t} else {
\t\t\t// error: task to copy data to queue still running
\t\t\tsdio_rx_free_buffer(rxbuff);
\t\t\tESP_LOGE(TAG, "task still writing Rx data to queue!");
\t\t\t// don't send data to task, or update write_index
\t\t}
"""
INCREMENTAL_HANDOFF_REPLACEMENT = """#if H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX
\t\tif (!sdio_incremental_stream_finish(&incremental_stream, ret == ESP_OK)) {
\t\t\tret = ESP_FAIL;
\t\t}
\t\tif (unlikely(ret))
\t\t\tcontinue;
#else
\t\tif (unlikely(ret))
\t\t\tcontinue;

\t\tif (double_buf.read_index < 0) {
\t\t\tdouble_buf.read_index = double_buf.write_index;
\t\t\tdouble_buf.read_data_len = len_from_slave;
\t\t\tdouble_buf.write_index = (double_buf.write_index) ? 0 : 1;
\t\t\t// trigger task to copy data to queue
\t\t\tg_h.funcs->_h_post_semaphore(sem_double_buf_xfer_data);
\t\t} else {
\t\t\t// error: task to copy data to queue still running
\t\t\tsdio_rx_free_buffer(rxbuff);
\t\t\tESP_LOGE(TAG, "task still writing Rx data to queue!");
\t\t\t// don't send data to task, or update write_index
\t\t}
#endif
"""

INCREMENTAL_TASK_ANCHOR = """\tsem_double_buf_xfer_data = g_h.funcs->_h_create_semaphore(1);
\tassert(sem_double_buf_xfer_data);
\tg_h.funcs->_h_get_semaphore(sem_double_buf_xfer_data, 0);

\tsdio_rx_buf_thread = g_h.funcs->_h_thread_create("sdio_rx_buf",
\t\tDFLT_TASK_PRIO, RX_BUF_TASK_STACK_SIZE, sdio_data_to_rx_buf_task, NULL);
"""
INCREMENTAL_TASK_REPLACEMENT = """#if !(H_SDIO_HOST_RX_MODE == H_SDIO_HOST_STREAMING_MODE && \\
\tdefined(CONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX) && \\
\tCONFIG_ESPHOME_ESP_HOSTED_SDIO_INCREMENTAL_RX)
\tsem_double_buf_xfer_data = g_h.funcs->_h_create_semaphore(1);
\tassert(sem_double_buf_xfer_data);
\tg_h.funcs->_h_get_semaphore(sem_double_buf_xfer_data, 0);

\tsdio_rx_buf_thread = g_h.funcs->_h_thread_create("sdio_rx_buf",
\t\tDFLT_TASK_PRIO, RX_BUF_TASK_STACK_SIZE, sdio_data_to_rx_buf_task, NULL);
#endif
"""


def main() -> None:
    project_dir = Path(env.subst("$PROJECT_DIR"))
    target = (
        project_dir
        / "managed_components"
        / "espressif__esp_hosted"
        / "host"
        / "drivers"
        / "transport"
        / "sdio"
        / "sdio_drv.c"
    )
    if not target.exists():
        raise RuntimeError(
            "ESP-Hosted SDIO source was not found; managed-component layout needs review"
        )

    common_target = (
        project_dir
        / "managed_components"
        / "espressif__esp_hosted"
        / "host"
        / "drivers"
        / "transport"
        / "transport_drv.c"
    )
    if not common_target.exists():
        raise RuntimeError(
            "ESP-Hosted common transport source was not found; managed-component layout needs review"
        )

    text = target.read_text(encoding="utf-8")
    timing_include_changed = False
    if '#include "esp_timer.h"' not in text:
        include_anchor = '#include "esp_hosted_event.h"\n'
        if include_anchor not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO include anchor changed; timing diagnostics need review"
            )
        text = text.replace(
            include_anchor, include_anchor + '#include "esp_timer.h"\n', 1
        )
        timing_include_changed = True
    if '#include "esp_memory_utils.h"' not in text and '#include "esp_heap_caps.h"' in text:
        text = text.replace(
            '#include "esp_heap_caps.h"\n',
            '#include "esp_heap_caps.h"\n#include "esp_memory_utils.h"\n#include "esp_rom_sys.h"\n',
            1,
        )
    fifo_migrated = False
    if FIFO_DECLARATION_LEGACY in text:
        text = text.replace(FIFO_DECLARATION_LEGACY, FIFO_DECLARATION_REPLACEMENT, 1)
        fifo_migrated = True
    elif FIFO_DECLARATION_VBLANK_V1 in text:
        text = text.replace(FIFO_DECLARATION_VBLANK_V1, FIFO_DECLARATION_REPLACEMENT, 1)
        fifo_migrated = True
    elif FIFO_DECLARATION_VBLANK_V2 in text:
        text = text.replace(FIFO_DECLARATION_VBLANK_V2, FIFO_DECLARATION_REPLACEMENT, 1)
        fifo_migrated = True
    elif FIFO_DECLARATION_RESERVATION_V3 in text:
        text = text.replace(FIFO_DECLARATION_RESERVATION_V3, FIFO_DECLARATION_REPLACEMENT, 1)
        fifo_migrated = True
    if FIFO_GUARD_LEGACY in text:
        text = text.replace(FIFO_GUARD_LEGACY, FIFO_GUARD_REPLACEMENT, 1)
        fifo_migrated = True
    elif FIFO_GUARD_VBLANK_V1 in text:
        text = text.replace(FIFO_GUARD_VBLANK_V1, FIFO_GUARD_REPLACEMENT, 1)
        fifo_migrated = True
    elif FIFO_GUARD_STRICT_V2 in text:
        text = text.replace(FIFO_GUARD_STRICT_V2, FIFO_GUARD_REPLACEMENT, 1)
        fifo_migrated = True

    # Migrate a build tree already patched by the previous fixed-window
    # version. PlatformIO retains managed components between incremental
    # builds, so changing only the fresh-source replacement would otherwise
    # leave the old guard active on the device.
    if FIFO_HELPER_LEGACY in text:
        text = text.replace(FIFO_HELPER_LEGACY, FIFO_HELPER_REPLACEMENT, 1)
        fifo_migrated = True
    elif FIFO_HELPER_V2 in text:
        text = text.replace(FIFO_HELPER_V2, FIFO_HELPER_REPLACEMENT, 1)
        fifo_migrated = True
    elif FIFO_HELPER_BOUNDED_RESERVATION in text:
        text = text.replace(
            FIFO_HELPER_BOUNDED_RESERVATION, FIFO_HELPER_REPLACEMENT, 1
        )
        fifo_migrated = True
    elif FIFO_HELPER_RESERVATION_V3 in text:
        text = text.replace(FIFO_HELPER_RESERVATION_V3, FIFO_HELPER_REPLACEMENT, 1)
        fifo_migrated = True
    if FIFO_GUARD_LEGACY_CALL in text:
        text = text.replace(FIFO_GUARD_LEGACY_CALL, FIFO_GUARD_REPLACEMENT.split("\n\n#if", 1)[0] + "\n", 1)
        fifo_migrated = True
    if TX_GUARD_LEGACY_CALL in text:
        text = text.replace(
            TX_GUARD_LEGACY_CALL,
            TX_GUARD_LEGACY_CALL.replace(
                "sdio_wait_for_dsi_window();", "sdio_wait_for_dsi_window(len_to_send, true);"
            ),
            1,
        )
        fifo_migrated = True
    # Upgrade persistent build trees from the earlier all-or-nothing experiment
    # to the bounded internal-payload path used by the current build.
    if RX_NETWORK_INTERNAL_EXPERIMENT in text:
        text = text.replace(
            RX_NETWORK_INTERNAL_EXPERIMENT, RX_NETWORK_INTERNAL_REPLACEMENT, 1
        )
        fifo_migrated = True
    if LEGACY_YIELD_BLOCK in text:
        text = text.replace(LEGACY_YIELD_BLOCK, SCHEDULER_BOUNDARY_BLOCK)
        fifo_migrated = True
    for legacy, replacement in zip(CONTROL_WRAPPER_LEGACY_REPLACEMENTS, CONTROL_WRAPPER_REPLACEMENTS):
        if legacy in text:
            text = text.replace(legacy, replacement.split("\n", 2)[2], 1)
            fifo_migrated = True
    # Register accesses and physical CMD53 transfers terminate in internal DMA
    # memory. Guarding them delayed the priority-23 hosted tasks for many display
    # frames and then released traffic in bursts. Keep the vblank guard only on
    # the fallback network-payload copy whose destination is actually in PSRAM.
    for guarded, unguarded in zip(CONTROL_WRAPPER_REPLACEMENTS, CONTROL_WRAPPER_ANCHORS):
        if guarded in text:
            text = text.replace(guarded, unguarded, 1)
            fifo_migrated = True
    if TX_GUARD_REPLACEMENT in text:
        text = text.replace(TX_GUARD_REPLACEMENT, TX_GUARD_ANCHOR, 1)
        fifo_migrated = True
    if FIFO_GUARD_REPLACEMENT in text:
        text = text.replace(FIFO_GUARD_REPLACEMENT, FIFO_GUARD_ANCHOR, 1)
        fifo_migrated = True
    if TX_GUARD_CURRENT_CALL in text:
        text = text.replace(TX_GUARD_CURRENT_CALL, "", 1)
        fifo_migrated = True
    if RX_GUARD_CURRENT_CALL in text:
        text = text.replace(RX_GUARD_CURRENT_CALL, "", 1)
        fifo_migrated = True
    if RX_COPY_GUARD_LEGACY_REPLACEMENT in text:
        text = text.replace(
            RX_COPY_GUARD_LEGACY_REPLACEMENT, RX_COPY_GUARD_REPLACEMENT, 1
        )
        fifo_migrated = True

    has_limit = LIMIT_MARKER in text
    has_yield = YIELD_MARKER in text
    has_frame_boundary = FRAME_BOUNDARY_MARKER in text
    has_rx_dispatch_boundary = RX_DISPATCH_BOUNDARY_MARKER in text
    has_internal_rx = RX_INTERNAL_MARKER in text
    has_fifo_guard = FIFO_GUARD_MARKER in text
    has_fifo_helper = FIFO_HELPER_MARKER in text
    has_rx_copy_guard = FIFO_RX_COPY_GUARD_MARKER in text
    has_network_internal = RX_NETWORK_INTERNAL_MARKER in text
    has_incremental_rx = INCREMENTAL_RX_MARKER in text
    has_transfer_diagnostics = SDIO_TRANSFER_DIAGNOSTICS_MARKER in text
    sdio_changed = timing_include_changed or fifo_migrated or not (
        has_limit
        and has_yield
        and has_frame_boundary
        and has_rx_dispatch_boundary
        and has_internal_rx
        and has_fifo_guard
        and has_fifo_helper
        and has_rx_copy_guard
        and has_network_internal
        and has_incremental_rx
        and has_transfer_diagnostics
    )

    if not has_fifo_helper:
        if FIFO_HELPER_ANCHOR not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO TAG anchor changed; DSI window helper needs review"
            )
        text = text.replace(FIFO_HELPER_ANCHOR, FIFO_HELPER_REPLACEMENT, 1)

    if not has_transfer_diagnostics:
        if TX_TRANSACTION_ANCHOR not in text or RX_TRANSACTION_ANCHOR not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO transaction anchors changed; timing diagnostics need review"
            )
        text = text.replace(TX_TRANSACTION_ANCHOR, TX_TRANSACTION_REPLACEMENT, 1)
        text = text.replace(RX_TRANSACTION_ANCHOR, RX_TRANSACTION_REPLACEMENT, 1)
        sdio_changed = True

    if not has_rx_copy_guard:
        if RX_COPY_GUARD_ANCHOR not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO RX handoff changed; post-read copy guard needs review"
            )
        text = text.replace(
            RX_COPY_GUARD_ANCHOR, RX_COPY_GUARD_REPLACEMENT, 1
        )

    if not has_network_internal:
        if RX_NETWORK_UPSTREAM_ALLOC not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO network payload allocator changed; internal payload path needs review"
            )
        text = text.replace(
            RX_NETWORK_UPSTREAM_ALLOC, RX_NETWORK_INTERNAL_REPLACEMENT, 1
        )

    if not has_rx_dispatch_boundary:
        if RX_DISPATCH_BOUNDARY_ANCHOR not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO RX dispatch tail changed; scheduler boundary needs review"
            )
        text = text.replace(
            RX_DISPATCH_BOUNDARY_ANCHOR,
            RX_DISPATCH_BOUNDARY_REPLACEMENT,
            1,
        )

    if not has_limit:
        if READ_ANCHOR not in text or MODE_ANCHOR not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO read/log anchors changed; streaming patch needs review"
            )
        text = text.replace(READ_ANCHOR, READ_REPLACEMENT, 1)
        text = text.replace(MODE_ANCHOR, MODE_REPLACEMENT, 1)

    if not has_yield:
        if ADVANCE_ANCHOR not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO advance anchor changed; streaming patch needs review"
            )
        text = text.replace(ADVANCE_ANCHOR, ADVANCE_REPLACEMENT, 1)

    if not has_frame_boundary:
        if FRAME_BOUNDARY_ANCHOR not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO RX unlock anchor changed; scheduler boundary needs review"
            )
        text = text.replace(
            FRAME_BOUNDARY_ANCHOR, FRAME_BOUNDARY_REPLACEMENT, 1
        )

    if not has_internal_rx:
        if (
            INCLUDE_ANCHOR not in text
            or MEMPOOL_FUNCTION_ANCHOR not in text
            or MEMPOOL_ALLOC_ANCHOR not in text
        ):
            raise RuntimeError(
                "ESP-Hosted SDIO mempool anchors changed; internal RX patch needs review"
            )
        text = text.replace(INCLUDE_ANCHOR, INCLUDE_REPLACEMENT, 1)
        text = text.replace(
            MEMPOOL_FUNCTION_ANCHOR, MEMPOOL_FUNCTION_REPLACEMENT, 1
        )
        text = text.replace(MEMPOOL_ALLOC_ANCHOR, MEMPOOL_ALLOC_REPLACEMENT, 1)

    if POOL_DIAGNOSTICS_MARKER not in text:
        if MEMPOOL_FUNCTION_REPLACEMENT not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO allocator changed; pool diagnostics need review"
            )
        text = text.replace(
            MEMPOOL_FUNCTION_REPLACEMENT,
            MEMPOOL_FUNCTION_WITH_DIAGNOSTICS,
            1,
        )
        sdio_changed = True
    elif MEMPOOL_FUNCTION_WITH_EARLY_DIAGNOSTICS in text:
        text = text.replace(
            MEMPOOL_FUNCTION_WITH_EARLY_DIAGNOSTICS,
            MEMPOOL_FUNCTION_WITH_DIAGNOSTICS,
            1,
        )
        sdio_changed = True

    if STREAM_BUFFER_INTERNAL_MARKER not in text:
        if STREAM_BUFFER_ALLOC_DIAGNOSTIC in text:
            text = text.replace(
                STREAM_BUFFER_ALLOC_DIAGNOSTIC,
                STREAM_BUFFER_ALLOC_REPLACEMENT,
                1,
            )
        elif STREAM_BUFFER_ALLOC_ANCHOR in text:
            text = text.replace(
                STREAM_BUFFER_ALLOC_ANCHOR, STREAM_BUFFER_ALLOC_REPLACEMENT, 1
            )
        else:
            raise RuntimeError(
                "ESP-Hosted SDIO stream buffer allocator changed; internal-memory patch needs review"
            )
        sdio_changed = True

    if RX_POOL_PRIORITY_MARKER not in text:
        if RX_POOL_LATE_ANCHOR not in text or RX_POOL_EARLY_ANCHOR not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO init anchors changed; RX-pool priority patch needs review"
            )
        # Remove the original late allocation before inserting the identical call
        # near the start of bus setup, otherwise replace() could match the new call.
        text = text.replace(RX_POOL_LATE_ANCHOR, "\n", 1)
        text = text.replace(
            RX_POOL_EARLY_ANCHOR, RX_POOL_EARLY_REPLACEMENT, 1
        )
        sdio_changed = True

    if not has_incremental_rx:
        incremental_anchors = (
            INCREMENTAL_HELPER_ANCHOR,
            INCREMENTAL_LOCAL_ANCHOR,
            INCREMENTAL_BUFFER_ANCHOR,
            INCREMENTAL_ADVANCE_ANCHOR,
            INCREMENTAL_HANDOFF_ANCHOR,
            INCREMENTAL_TASK_ANCHOR,
        )
        if any(anchor not in text for anchor in incremental_anchors):
            raise RuntimeError(
                "ESP-Hosted SDIO streaming anchors changed; incremental RX patch needs review"
            )
        text = text.replace(
            INCREMENTAL_HELPER_ANCHOR, INCREMENTAL_HELPER_REPLACEMENT, 1
        )
        text = text.replace(
            INCREMENTAL_LOCAL_ANCHOR, INCREMENTAL_LOCAL_REPLACEMENT, 1
        )
        text = text.replace(
            INCREMENTAL_BUFFER_ANCHOR, INCREMENTAL_BUFFER_REPLACEMENT, 1
        )
        text = text.replace(
            INCREMENTAL_ADVANCE_ANCHOR, INCREMENTAL_ADVANCE_REPLACEMENT, 1
        )
        text = text.replace(
            INCREMENTAL_HANDOFF_ANCHOR, INCREMENTAL_HANDOFF_REPLACEMENT, 1
        )
        text = text.replace(
            INCREMENTAL_TASK_ANCHOR, INCREMENTAL_TASK_REPLACEMENT, 1
        )
        sdio_changed = True

    if not has_fifo_guard:
        if FIFO_DECLARATION_ANCHOR not in text:
            raise RuntimeError(
                "ESP-Hosted SDIO DSI FIFO declaration anchor changed; patch needs review"
            )
        text = text.replace(
            FIFO_DECLARATION_ANCHOR, FIFO_DECLARATION_REPLACEMENT, 1
        )
        sdio_changed = True

    if sdio_changed:
        target.write_text(text, encoding="utf-8")

    common_text = common_target.read_text(encoding="utf-8")
    if '#include "esp_rom_sys.h"' not in common_text and '#include "esp_heap_caps.h"' in common_text:
        common_text = common_text.replace(
            '#include "esp_heap_caps.h"\n',
            '#include "esp_heap_caps.h"\n#include "esp_rom_sys.h"\n',
            1,
        )
    common_changed = COMMON_INTERNAL_MARKER not in common_text
    if common_changed:
        if (
            COMMON_INCLUDE_ANCHOR not in common_text
            or COMMON_FUNCTION_ANCHOR not in common_text
            or COMMON_ALLOC_ANCHOR not in common_text
        ):
            raise RuntimeError(
                "ESP-Hosted common mempool anchors changed; internal network pool patch needs review"
            )
        common_text = common_text.replace(
            COMMON_INCLUDE_ANCHOR, COMMON_INCLUDE_REPLACEMENT, 1
        )
        common_text = common_text.replace(
            COMMON_FUNCTION_ANCHOR, COMMON_FUNCTION_REPLACEMENT, 1
        )
        common_text = common_text.replace(
            COMMON_ALLOC_ANCHOR, COMMON_ALLOC_REPLACEMENT, 1
        )
        common_target.write_text(common_text, encoding="utf-8")

    if "ESP-Hosted common RX pool allocation" not in common_text:
        if COMMON_FUNCTION_REPLACEMENT not in common_text:
            raise RuntimeError(
                "ESP-Hosted common allocator changed; pool diagnostics need review"
            )
        common_text = common_text.replace(
            COMMON_FUNCTION_REPLACEMENT,
            COMMON_FUNCTION_WITH_DIAGNOSTICS,
            1,
        )
        common_changed = True
    elif COMMON_FUNCTION_WITH_EARLY_DIAGNOSTICS in common_text:
        common_text = common_text.replace(
            COMMON_FUNCTION_WITH_EARLY_DIAGNOSTICS,
            COMMON_FUNCTION_WITH_DIAGNOSTICS,
            1,
        )
        common_changed = True

    if common_changed:
        common_target.write_text(common_text, encoding="utf-8")

    print(
        "ESP-Hosted SDIO streaming patch: incremental internal-RAM RX and bounded FIFO-aware transactions"
    )


if env is not None:
    main()
