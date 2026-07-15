#pragma once

#include <algorithm>
#include <climits>
#include <cstring>
#include <cstdlib>

#include "lvgl.h"

#ifdef ESP_PLATFORM
#include "esp_heap_caps.h"
#endif

extern "C" bool lvgl_esphome_direct_blit_rgb888(const uint8_t *src, int src_stride, int x, int y, int width,
                                                 int height);
namespace atmosfera_ui {

struct TitleMarqueeDirectState {
  lv_obj_t *label{nullptr};
  lv_draw_buf_t *text{nullptr};
  lv_color_t *background{nullptr};
  lv_color_t *scratch{nullptr};
  int screen_x{0};
  int screen_y{0};
  int width{0};
  int height{0};
  int source_x_offset{0};
  int source_y_offset{0};
  int last_x{INT_MIN};
  bool active{false};
};

static TitleMarqueeDirectState title_marquee_direct_state;

inline void title_marquee_direct_end(bool restore_native = true) {
  auto &state = title_marquee_direct_state;
  if (restore_native && state.label != nullptr) {
    lv_obj_set_x(state.label, 0);
    lv_obj_clear_flag(state.label, LV_OBJ_FLAG_HIDDEN);
  }
  if (state.text != nullptr) lv_draw_buf_destroy(state.text);
#ifdef ESP_PLATFORM
  if (state.background != nullptr) heap_caps_free(state.background);
  if (state.scratch != nullptr) heap_caps_free(state.scratch);
#else
  std::free(state.background);
  std::free(state.scratch);
#endif
  state = {};
  state.last_x = INT_MIN;
}

inline bool title_marquee_direct_update(int offset_x) {
  auto &state = title_marquee_direct_state;
  if (!state.active || state.text == nullptr || state.background == nullptr || state.scratch == nullptr) return false;
  if (offset_x == state.last_x) return true;

  const size_t row_bytes = (size_t) state.width * sizeof(lv_color_t);
  for (int y = 0; y < state.height; y++) {
    memcpy(state.scratch + (size_t) y * state.width,
           state.background + (size_t) y * state.width, row_bytes);
  }

  for (int y = 0; y < state.height; y++) {
    const int source_y = y + state.source_y_offset;
    if (source_y < 0 || source_y >= (int) state.text->header.h) continue;
    const uint8_t *source_row = state.text->data + (size_t) source_y * state.text->header.stride;
    lv_color_t *dest_row = state.scratch + (size_t) y * state.width;
    for (int x = 0; x < state.width; x++) {
      const int source_x = x - offset_x + state.source_x_offset;
      if (source_x < 0 || source_x >= (int) state.text->header.w) continue;
      lv_color32_t source;
      memcpy(&source, source_row + (size_t) source_x * sizeof(source), sizeof(source));
      if (source.alpha == 0) continue;
      lv_color_t &dest = dest_row[x];
      const int alpha = source.alpha;
      dest.red = (uint8_t) (((int) dest.red * (255 - alpha) + (int) source.red * alpha + 127) / 255);
      dest.green = (uint8_t) (((int) dest.green * (255 - alpha) + (int) source.green * alpha + 127) / 255);
      dest.blue = (uint8_t) (((int) dest.blue * (255 - alpha) + (int) source.blue * alpha + 127) / 255);
    }
  }

  if (!lvgl_esphome_direct_blit_rgb888(reinterpret_cast<const uint8_t *>(state.scratch),
                                        state.width * (int) sizeof(lv_color_t), state.screen_x, state.screen_y,
                                        state.width, state.height)) {
    title_marquee_direct_end(true);
    return false;
  }
  state.last_x = offset_x;
  return true;
}

inline bool title_marquee_direct_begin(lv_obj_t *label, int screen_x, int screen_y, int width, int height) {
  title_marquee_direct_end(true);
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
  state.scratch = static_cast<lv_color_t *>(
      heap_caps_malloc(pixel_count * sizeof(lv_color_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
#else
  state.background = static_cast<lv_color_t *>(std::malloc(pixel_count * sizeof(lv_color_t)));
  state.scratch = static_cast<lv_color_t *>(std::malloc(pixel_count * sizeof(lv_color_t)));
#endif
  if (state.text == nullptr || state.text->header.cf != LV_COLOR_FORMAT_ARGB8888 ||
      state.background == nullptr || state.scratch == nullptr) {
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

  // Render the strip below the title into an off-screen snapshot. The previous
  // implementation hid the label, refreshed the live display and captured the
  // cleared framebuffer; that necessarily exposed a blank strip before the
  // first marquee frame and looked like a jump/flash.
  // Hiding the native label normally invalidates its old area. That queued
  // redraw can run after the first direct-compositor frame and briefly erase
  // it, which looks like a flash followed by a one-pixel jump. The compositor
  // owns this strip until title_marquee_direct_end(), so suppress only this
  // invalidation while changing visibility.
  lv_display_t *display = lv_obj_get_display(label);
  const bool invalidation_enabled = display != nullptr && lv_display_is_invalidation_enabled(display);
  if (invalidation_enabled) lv_display_enable_invalidation(display, false);
  lv_obj_add_flag(label, LV_OBJ_FLAG_HIDDEN);
  if (invalidation_enabled) lv_display_enable_invalidation(display, true);
  lv_obj_t *viewport = lv_obj_get_parent(label);
  lv_draw_buf_t *background_snapshot =
      viewport != nullptr ? lv_snapshot_take(viewport, LV_COLOR_FORMAT_RGB888) : nullptr;
  if (background_snapshot == nullptr || background_snapshot->header.cf != LV_COLOR_FORMAT_RGB888 ||
      background_snapshot->header.w < width || background_snapshot->header.h < height) {
    if (background_snapshot != nullptr) lv_draw_buf_destroy(background_snapshot);
    title_marquee_direct_end(true);
    return false;
  }
  for (int y = 0; y < height; y++) {
    memcpy(state.background + (size_t) y * width,
           background_snapshot->data + (size_t) y * background_snapshot->header.stride,
           (size_t) width * sizeof(lv_color_t));
  }
  lv_draw_buf_destroy(background_snapshot);

  state.active = true;
  state.last_x = INT_MIN;
  if (!title_marquee_direct_update(0)) return false;
  return true;
}

inline bool title_marquee_direct_is_active() { return title_marquee_direct_state.active; }

}  // namespace atmosfera_ui
