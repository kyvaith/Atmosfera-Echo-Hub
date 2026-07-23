#pragma once

#include <algorithm>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>

#include "lvgl.h"

#ifdef ESP_PLATFORM
#include "esp_heap_caps.h"
#endif

extern "C" uint8_t lvgl_esphome_direct_blit_rgb888_async(
    const uint8_t *src, int src_stride, int x, int y, int width, int height,
    void (*ready_callback)(void *), void *ready_arg);
extern "C" bool lvgl_esphome_direct_capture_rgb888(
    uint8_t *dst, int dst_stride, int x, int y, int width, int height);
extern "C" void lvgl_esphome_direct_blit_rgb888_release(
    int x, int y, int width, int height);

namespace atmosfera_ui {

struct TransportFeedbackState {
  uint8_t *normal{nullptr};
  uint8_t *pressed{nullptr};
  size_t capacity{0};
  int x{0};
  int y{0};
  int width{0};
  int height{0};
  bool active{false};
  std::atomic<bool> press_in_flight{false};
  std::atomic<bool> restore_in_flight{false};
};

static TransportFeedbackState transport_feedback;

static void transport_press_ready(void *arg) {
  auto *state = static_cast<TransportFeedbackState *>(arg);
  if (state != nullptr) state->press_in_flight.store(false, std::memory_order_release);
}

static void transport_restore_ready(void *arg) {
  auto *state = static_cast<TransportFeedbackState *>(arg);
  if (state != nullptr) state->restore_in_flight.store(false, std::memory_order_release);
}

static bool transport_feedback_ensure_buffers(TransportFeedbackState *state, size_t required) {
  if (state == nullptr) return false;
  if (state->normal != nullptr && state->pressed != nullptr && state->capacity >= required) return true;
  if (state->press_in_flight.load(std::memory_order_acquire) ||
      state->restore_in_flight.load(std::memory_order_acquire)) {
    return false;
  }

  if (state->normal != nullptr) std::free(state->normal);
  if (state->pressed != nullptr) std::free(state->pressed);
  state->normal = nullptr;
  state->pressed = nullptr;
  state->capacity = 0;
#ifdef ESP_PLATFORM
  state->normal = static_cast<uint8_t *>(
      heap_caps_aligned_alloc(64, required, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
  state->pressed = static_cast<uint8_t *>(
      heap_caps_aligned_alloc(64, required, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
#else
  state->normal = static_cast<uint8_t *>(std::malloc(required));
  state->pressed = static_cast<uint8_t *>(std::malloc(required));
#endif
  if (state->normal == nullptr || state->pressed == nullptr) {
    if (state->normal != nullptr) std::free(state->normal);
    if (state->pressed != nullptr) std::free(state->pressed);
    state->normal = nullptr;
    state->pressed = nullptr;
    return false;
  }
  state->capacity = required;
  return true;
}

static bool transport_feedback_inside_pill(int x, int y, int width, int height) {
  const int radius = std::min(width / 2, height / 2);
  if (radius <= 0 || (y >= radius && y < height - radius)) return true;
  const int center_x2 = width - 1;
  const int center_y2 = y < radius ? 2 * radius - 1 : 2 * (height - radius) - 1;
  const int dx2 = 2 * x - center_x2;
  const int dy2 = 2 * y - center_y2;
  const int radius2 = 2 * radius;
  return dx2 * dx2 + dy2 * dy2 <= radius2 * radius2;
}

inline bool media_transport_feedback_begin(lv_obj_t *button) {
  auto &state = transport_feedback;
  if (button == nullptr || state.active ||
      state.press_in_flight.load(std::memory_order_acquire) ||
      state.restore_in_flight.load(std::memory_order_acquire)) {
    return false;
  }

  lv_area_t area{};
  lv_obj_get_coords(button, &area);
  const int width = lv_area_get_width(&area);
  const int height = lv_area_get_height(&area);
  if (width <= 0 || height <= 0) return false;

  constexpr int bytes_per_pixel = 3;
  const int stride = width * bytes_per_pixel;
  const size_t bytes = static_cast<size_t>(stride) * height;
  if (!transport_feedback_ensure_buffers(&state, bytes) ||
      !lvgl_esphome_direct_capture_rgb888(
          state.normal, stride, area.x1, area.y1, width, height)) {
    return false;
  }

  std::memcpy(state.pressed, state.normal, bytes);
  // Material pressed feedback is a 12% dark state layer. Applying the same
  // factor to all channels is independent of the configured RGB byte order.
  for (int py = 0; py < height; py++) {
    for (int px = 0; px < width; px++) {
      if (!transport_feedback_inside_pill(px, py, width, height)) continue;
      uint8_t *pixel = state.pressed + static_cast<size_t>(py * stride + px * bytes_per_pixel);
      pixel[0] = static_cast<uint8_t>((static_cast<unsigned>(pixel[0]) * 88U + 50U) / 100U);
      pixel[1] = static_cast<uint8_t>((static_cast<unsigned>(pixel[1]) * 88U + 50U) / 100U);
      pixel[2] = static_cast<uint8_t>((static_cast<unsigned>(pixel[2]) * 88U + 50U) / 100U);
    }
  }

  state.x = area.x1;
  state.y = area.y1;
  state.width = width;
  state.height = height;
  state.press_in_flight.store(true, std::memory_order_release);
  const uint8_t result = lvgl_esphome_direct_blit_rgb888_async(
      state.pressed, stride, state.x, state.y, width, height,
      transport_press_ready, &state);
  if (result != 2) {
    state.press_in_flight.store(false, std::memory_order_release);
    return false;
  }
  state.active = true;
  return true;
}

inline bool media_transport_feedback_end() {
  auto &state = transport_feedback;
  if (!state.active) return true;
  if (state.restore_in_flight.load(std::memory_order_acquire)) return true;
  if (state.normal == nullptr || state.width <= 0 || state.height <= 0) {
    state.active = false;
    return true;
  }

  state.restore_in_flight.store(true, std::memory_order_release);
  const uint8_t result = lvgl_esphome_direct_blit_rgb888_async(
      state.normal, state.width * 3, state.x, state.y, state.width, state.height,
      transport_restore_ready, &state);
  if (result != 2) {
    state.restore_in_flight.store(false, std::memory_order_release);
    return false;
  }
  state.active = false;
  return true;
}

inline void media_transport_feedback_abandon() {
  auto &state = transport_feedback;
  if (state.width > 0 && state.height > 0) {
    lvgl_esphome_direct_blit_rgb888_release(
        state.x, state.y, state.width, state.height);
  }
  state.active = false;
}

}  // namespace atmosfera_ui
