#pragma once

#include <algorithm>
#include <atomic>
#include <climits>
#include <cstring>
#include <cstdlib>

#include "lvgl.h"

#ifdef ESP_PLATFORM
#include "esp_heap_caps.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#endif

extern "C" bool lvgl_esphome_direct_blit_rgb888(const uint8_t *src, int src_stride, int x, int y, int width,
                                                 int height);
extern "C" uint8_t lvgl_esphome_direct_blit_rgb888_async(const uint8_t *src, int src_stride, int x, int y,
                                                           int width, int height, void (*ready_callback)(void *),
                                                           void *ready_arg);
extern "C" uint8_t lvgl_esphome_direct_blend_argb8888_async(
    const uint8_t *background, int background_stride, const uint8_t *foreground, int foreground_stride,
    int foreground_width, int foreground_height, int foreground_x, int foreground_y, int x, int y, int width,
    int height, void (*ready_callback)(void *), void *ready_arg);
extern "C" void lvgl_esphome_direct_blit_rgb888_release(int x, int y, int width, int height);
extern "C" bool lvgl_esphome_direct_capture_rgb888(uint8_t *dst, int dst_stride, int x, int y, int width,
                                                    int height);
#ifdef ESP_PLATFORM
extern "C" uint32_t lvgl_esphome_get_perf_logging_enabled(void);
#endif
namespace atmosfera_ui {

struct TitleMarqueeDirectState {
  lv_obj_t *label{nullptr};
  lv_draw_buf_t *text{nullptr};
  lv_color_t *background{nullptr};
  int screen_x{0};
  int screen_y{0};
  int width{0};
  int height{0};
  int source_x_offset{0};
  int source_y_offset{0};
  int last_x{INT_MIN};
  std::atomic<int> pending_x{INT_MIN};
  std::atomic<bool> active{false};
  bool cleanup_pending{false};
  std::atomic<bool> present_in_flight{false};
  std::atomic<bool> present_complete{false};
#ifdef ESP_PLATFORM
  TaskHandle_t worker_handle{nullptr};
  StackType_t *worker_stack{nullptr};
  StaticTask_t worker_storage{};
  std::atomic<bool> worker_busy{false};
  uint32_t perf_compose_count{0};
  uint64_t perf_compose_total_us{0};
  uint32_t perf_compose_max_us{0};
  uint32_t perf_async_count{0};
  uint32_t perf_busy_count{0};
  uint32_t perf_sync_count{0};
  uint32_t perf_dma_count{0};
  uint64_t perf_dma_total_us{0};
  uint32_t perf_dma_max_us{0};
  int64_t perf_window_start_us{0};
  int64_t present_started_us{0};
#endif
};

static TitleMarqueeDirectState title_marquee_direct_state;

#ifdef ESP_PLATFORM
inline void title_marquee_direct_log_perf(TitleMarqueeDirectState &state, int64_t now_us) {
  if (lvgl_esphome_get_perf_logging_enabled() == 0) return;
  if (state.perf_window_start_us == 0) state.perf_window_start_us = now_us;
  if (now_us - state.perf_window_start_us < 2000000LL) return;

  const uint32_t compose_avg_us = state.perf_compose_count == 0
                                      ? 0
                                      : static_cast<uint32_t>(state.perf_compose_total_us /
                                                              state.perf_compose_count);
  const uint32_t dma_avg_us = state.perf_dma_count == 0
                                  ? 0
                                  : static_cast<uint32_t>(state.perf_dma_total_us / state.perf_dma_count);
  ESP_LOGI("media.marquee",
           "perf2s: compose=%u avg=%uus max=%uus async=%u busy=%u sync=%u dma=%uus max=%uus",
           state.perf_compose_count, compose_avg_us, state.perf_compose_max_us, state.perf_async_count,
           state.perf_busy_count, state.perf_sync_count, dma_avg_us, state.perf_dma_max_us);
  state.perf_compose_count = 0;
  state.perf_compose_total_us = 0;
  state.perf_compose_max_us = 0;
  state.perf_async_count = 0;
  state.perf_busy_count = 0;
  state.perf_sync_count = 0;
  state.perf_dma_count = 0;
  state.perf_dma_total_us = 0;
  state.perf_dma_max_us = 0;
  state.perf_window_start_us = now_us;
}
#endif

inline void title_marquee_direct_release() {
  auto &state = title_marquee_direct_state;
  if (state.text != nullptr) lv_draw_buf_destroy(state.text);
#ifdef ESP_PLATFORM
  if (state.background != nullptr) heap_caps_free(state.background);
#else
  std::free(state.background);
#endif
  state.label = nullptr;
  state.text = nullptr;
  state.background = nullptr;
  state.screen_x = 0;
  state.screen_y = 0;
  state.width = 0;
  state.height = 0;
  state.source_x_offset = 0;
  state.source_y_offset = 0;
  state.last_x = INT_MIN;
  state.pending_x.store(INT_MIN, std::memory_order_release);
  state.active.store(false, std::memory_order_release);
  state.cleanup_pending = false;
  state.present_complete.store(false, std::memory_order_release);
  state.present_in_flight.store(false, std::memory_order_release);
}

inline void title_marquee_direct_service(bool allow_cleanup = true) {
  auto &state = title_marquee_direct_state;
  if (state.present_in_flight.load(std::memory_order_acquire) &&
      state.present_complete.exchange(false, std::memory_order_acq_rel)) {
#ifdef ESP_PLATFORM
    const int64_t now_us = esp_timer_get_time();
    if (state.present_started_us != 0 && lvgl_esphome_get_perf_logging_enabled() != 0) {
      const uint32_t dma_us = static_cast<uint32_t>(now_us - state.present_started_us);
      state.perf_dma_count++;
      state.perf_dma_total_us += dma_us;
      if (dma_us > state.perf_dma_max_us) state.perf_dma_max_us = dma_us;
    }
    state.present_started_us = 0;
#endif
    state.present_in_flight.store(false, std::memory_order_release);
  }
#ifdef ESP_PLATFORM
  title_marquee_direct_log_perf(state, esp_timer_get_time());
#endif
  const bool worker_idle =
#ifdef ESP_PLATFORM
      !state.worker_busy.load(std::memory_order_acquire);
#else
      true;
#endif
  if (allow_cleanup && state.cleanup_pending && !state.present_in_flight.load(std::memory_order_acquire) &&
      worker_idle) {
    title_marquee_direct_release();
  }
}

inline void title_marquee_direct_present_done(void *arg) {
  auto *state = static_cast<TitleMarqueeDirectState *>(arg);
  if (state == nullptr) return;
  state->present_complete.store(true, std::memory_order_release);
#ifdef ESP_PLATFORM
  if (state->worker_handle != nullptr) xTaskNotifyGive(state->worker_handle);
#endif
}

inline void title_marquee_direct_end(bool restore_native = true) {
  auto &state = title_marquee_direct_state;
  const bool was_active = state.active.exchange(false, std::memory_order_acq_rel);
  const int released_x = state.screen_x;
  const int released_y = state.screen_y;
  const int released_width = state.width;
  const int released_height = state.height;
  if (was_active)
    lvgl_esphome_direct_blit_rgb888_release(released_x, released_y, released_width, released_height);
  if (restore_native && state.label != nullptr) {
    lv_obj_set_x(state.label, 0);
    lv_obj_clear_flag(state.label, LV_OBJ_FLAG_HIDDEN);
  }
  state.cleanup_pending = true;
  state.pending_x.store(INT_MIN, std::memory_order_release);
#ifdef ESP_PLATFORM
  if (state.worker_handle != nullptr) xTaskNotifyGive(state.worker_handle);
#endif
  title_marquee_direct_service();
}

inline bool title_marquee_direct_render(int offset_x) {
  auto &state = title_marquee_direct_state;
  if (!state.active.load(std::memory_order_acquire) || state.text == nullptr || state.background == nullptr ||
      state.present_in_flight.load(std::memory_order_acquire))
    return false;
  if (offset_x == state.last_x) return true;

#ifdef ESP_PLATFORM
  const bool perf_enabled = lvgl_esphome_get_perf_logging_enabled() != 0;
  const int64_t compose_started_us = perf_enabled ? esp_timer_get_time() : 0;
#endif
  const int source_x = state.source_x_offset - offset_x;
#ifdef ESP_PLATFORM
  if (perf_enabled) {
    const uint32_t compose_us = static_cast<uint32_t>(esp_timer_get_time() - compose_started_us);
    state.perf_compose_count++;
    state.perf_compose_total_us += compose_us;
    if (compose_us > state.perf_compose_max_us) state.perf_compose_max_us = compose_us;
  }
#endif

  state.present_complete.store(false, std::memory_order_release);
  state.present_in_flight.store(true, std::memory_order_release);
#ifdef ESP_PLATFORM
  state.present_started_us = perf_enabled ? esp_timer_get_time() : 0;
#endif
  const uint8_t async_result = lvgl_esphome_direct_blend_argb8888_async(
      reinterpret_cast<const uint8_t *>(state.background), state.width * (int) sizeof(lv_color_t),
      state.text->data, state.text->header.stride, state.text->header.w, state.text->header.h, source_x,
      state.source_y_offset, state.screen_x, state.screen_y, state.width, state.height,
      title_marquee_direct_present_done, &state);
  if (async_result == 2) {
#ifdef ESP_PLATFORM
    if (perf_enabled) state.perf_async_count++;
#endif
    state.last_x = offset_x;
    return true;
  }
  state.present_in_flight.store(false, std::memory_order_release);
  state.present_complete.store(false, std::memory_order_release);
#ifdef ESP_PLATFORM
  state.present_started_us = 0;
#endif
  if (async_result == 1) {
#ifdef ESP_PLATFORM
    if (perf_enabled) state.perf_busy_count++;
#endif
    int expected = INT_MIN;
    state.pending_x.compare_exchange_strong(expected, offset_x, std::memory_order_acq_rel);
    return true;
  }
#ifdef ESP_PLATFORM
  if (perf_enabled) state.perf_sync_count++;
#endif
  return false;
}

#ifdef ESP_PLATFORM
inline void title_marquee_direct_worker(void *) {
  auto &state = title_marquee_direct_state;
  while (true) {
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    title_marquee_direct_service(false);
    while (state.active.load(std::memory_order_acquire) &&
           !state.present_in_flight.load(std::memory_order_acquire)) {
      const int offset_x = state.pending_x.exchange(INT_MIN, std::memory_order_acq_rel);
      if (offset_x == INT_MIN || offset_x == state.last_x) break;
      state.worker_busy.store(true, std::memory_order_release);
      const bool rendered = title_marquee_direct_render(offset_x);
      state.worker_busy.store(false, std::memory_order_release);
      if (!rendered && state.active.load(std::memory_order_acquire)) {
        int expected = INT_MIN;
        state.pending_x.compare_exchange_strong(expected, offset_x, std::memory_order_acq_rel);
      }
      if (state.present_in_flight.load(std::memory_order_acquire) || !rendered) break;
    }
  }
}

inline bool title_marquee_direct_ensure_worker() {
  auto &state = title_marquee_direct_state;
  if (state.worker_handle != nullptr) return true;
#if CONFIG_FREERTOS_UNICORE
  constexpr BaseType_t worker_core = tskNO_AFFINITY;
#elif defined(CONFIG_ESP_MAIN_TASK_AFFINITY_CPU0) && CONFIG_ESP_MAIN_TASK_AFFINITY_CPU0
  constexpr BaseType_t worker_core = 1;
#elif defined(CONFIG_ESP_MAIN_TASK_AFFINITY_CPU1) && CONFIG_ESP_MAIN_TASK_AFFINITY_CPU1
  constexpr BaseType_t worker_core = 0;
#else
  constexpr BaseType_t worker_core = 1;
#endif
  constexpr uint32_t worker_stack_size = 6144;
  state.worker_stack = static_cast<StackType_t *>(
      heap_caps_aligned_alloc(16, worker_stack_size, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT));
  if (state.worker_stack == nullptr) {
    state.worker_stack = static_cast<StackType_t *>(
        heap_caps_aligned_alloc(16, worker_stack_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
  }
  if (state.worker_stack == nullptr) return false;
  state.worker_handle = xTaskCreateStaticPinnedToCore(title_marquee_direct_worker, "title_marquee",
                                                       worker_stack_size, nullptr, 1, state.worker_stack,
                                                       &state.worker_storage, worker_core);
  if (state.worker_handle == nullptr) {
    heap_caps_free(state.worker_stack);
    state.worker_stack = nullptr;
    return false;
  }
  return true;
}
#endif

inline bool title_marquee_direct_update(int offset_x) {
  auto &state = title_marquee_direct_state;
  title_marquee_direct_service();
  if (!state.active.load(std::memory_order_acquire) || state.text == nullptr || state.background == nullptr)
    return false;
  if (offset_x == state.last_x && !state.present_in_flight.load(std::memory_order_acquire)) return true;
  state.pending_x.store(offset_x, std::memory_order_release);
#ifdef ESP_PLATFORM
  if (state.worker_handle != nullptr) {
    xTaskNotifyGive(state.worker_handle);
    return true;
  }
#endif
  if (state.present_in_flight.load(std::memory_order_acquire)) return true;
  const int pending_x = state.pending_x.exchange(INT_MIN, std::memory_order_acq_rel);
  return pending_x == INT_MIN || title_marquee_direct_render(pending_x);
}

inline bool title_marquee_direct_begin(lv_obj_t *label, int screen_x, int screen_y, int width, int height) {
  title_marquee_direct_service();
  title_marquee_direct_end(true);
  title_marquee_direct_service();
  if (title_marquee_direct_state.cleanup_pending) return false;
  if (label == nullptr || width <= 0 || height <= 0 || lv_obj_get_width(label) <= width) return false;
  static_assert(sizeof(lv_color_t) == 3, "The title marquee compositor requires RGB888");

  auto &state = title_marquee_direct_state;
  state.label = label;
  state.screen_x = screen_x;
  state.screen_y = screen_y;
  state.width = width;
  state.height = height;
  state.text = lv_snapshot_take(label, LV_COLOR_FORMAT_ARGB8888);
  const size_t pixel_count = (size_t) width * height;
#ifdef ESP_PLATFORM
  state.background = static_cast<lv_color_t *>(
      heap_caps_malloc(pixel_count * sizeof(lv_color_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
#else
  state.background = static_cast<lv_color_t *>(std::malloc(pixel_count * sizeof(lv_color_t)));
#endif
  if (state.text == nullptr || state.text->header.cf != LV_COLOR_FORMAT_ARGB8888 ||
      state.background == nullptr) {
    title_marquee_direct_end(true);
    return false;
  }

  // lv_snapshot_take() includes the object's ext_draw_size on every side.
  // Skip that transparent margin in both axes so direct frame zero matches
  // the native label exactly instead of briefly shifting the text right.
  const int label_width = static_cast<int>(lv_obj_get_width(label));
  const int label_height = static_cast<int>(lv_obj_get_height(label));
  state.source_x_offset = std::max(0, (static_cast<int>(state.text->header.w) - label_width) / 2);
  state.source_y_offset = std::max(0, (static_cast<int>(state.text->header.h) - label_height) / 2);

  // Capture only the visible title strip from the already presented DSI frame.
  // First synchronously remove the native title. Capturing before that redraw
  // baked the static label into the background, so the moving title was drawn
  // over a second, stationary copy.
  lv_display_t *display = lv_obj_get_display(label);
  lvgl_esphome_direct_regions_pause(true, 120);
  lv_obj_add_flag(label, LV_OBJ_FLAG_HIDDEN);
  if (display != nullptr) lv_refr_now(display);
  if (!lvgl_esphome_direct_capture_rgb888(reinterpret_cast<uint8_t *>(state.background),
                                           width * static_cast<int>(sizeof(lv_color_t)), screen_x, screen_y,
                                           width, height)) {
    lvgl_esphome_direct_regions_pause(false, 0);
    title_marquee_direct_end(true);
    return false;
  }
  lvgl_esphome_direct_regions_pause(false, 0);

  state.active.store(true, std::memory_order_release);
  state.last_x = INT_MIN;
  // Present frame zero synchronously before handing subsequent positions to
  // the worker. Previously the native label was already gone while the first
  // worker notification was still queued, producing a visible flash.
  if (!title_marquee_direct_render(0)) {
    title_marquee_direct_end(true);
    return false;
  }
  lvgl_esphome_wait_for_direct_frame_presented(40);
#ifdef ESP_PLATFORM
  title_marquee_direct_ensure_worker();
#endif
  return true;
}

inline bool title_marquee_direct_is_active() {
  return title_marquee_direct_state.active.load(std::memory_order_acquire);
}

}  // namespace atmosfera_ui
