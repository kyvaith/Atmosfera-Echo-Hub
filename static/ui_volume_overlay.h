#pragma once

#include <algorithm>
#include <cmath>
#include <cstring>
#include <cstdlib>
#include "lvgl.h"

#ifdef ESP_PLATFORM
#include "esp_heap_caps.h"
#endif

extern "C" bool lvgl_esphome_direct_blit_rgb888(const uint8_t *src, int src_stride, int x, int y, int width,
                                                 int height);
extern "C" bool lvgl_esphome_direct_capture_rgb888(uint8_t *dst, int dst_stride, int x, int y, int width,
                                                    int height);

namespace atmosfera_ui {

constexpr float kVolumeOverlayCenterX = 400.0f;
constexpr float kVolumeOverlayCenterY = 400.0f;
constexpr float kVolumeOverlayArcRadius = 357.5f;
constexpr int kVolumeOverlayWidth = 800;
constexpr int kVolumeOverlayHeight = 800;
constexpr int kVolumeOverlayCaptureHeight = 480;

struct VolumeOverlayDirectState {
  lv_color_t *original{nullptr};
  lv_color_t *background{nullptr};
  lv_color_t *scratch{nullptr};
  lv_draw_buf_t *glyph_buffer{nullptr};
  lv_obj_t *arc{nullptr};
  lv_obj_t *knob{nullptr};
  lv_obj_t *label{nullptr};
  const lv_font_t *font{nullptr};
  float point_x[101]{};
  float point_y[101]{};
  int visual_pct{-1};
  int value_pct{-1};
  int letter_space{0};
  bool prepared{false};
  bool active{false};
  bool presented{false};
};

struct VolumeOverlayVisualCache {
  lv_obj_t *arc{nullptr};
  lv_obj_t *knob{nullptr};
  lv_obj_t *label{nullptr};
  int value_pct{-1};
  int visual_pct{-1};
};

static VolumeOverlayDirectState volume_overlay_direct_state;
static VolumeOverlayVisualCache volume_overlay_visual_cache;

inline int clamp_volume_pct(int pct) {
  if (pct < 0) return 0;
  if (pct > 100) return 100;
  return pct;
}

inline void volume_overlay_reset_visual_cache() {
  volume_overlay_visual_cache = {};
  volume_overlay_visual_cache.value_pct = -1;
  volume_overlay_visual_cache.visual_pct = -1;
}

inline void volume_overlay_blend(lv_color_t &dst, uint8_t red, uint8_t green, uint8_t blue, float coverage);
inline void volume_overlay_point_for_pct(int pct, float &x, float &y);

inline void volume_overlay_direct_end(bool restore_screen = true) {
  auto &state = volume_overlay_direct_state;
  if (restore_screen && state.presented && state.original != nullptr) {
    lvgl_esphome_direct_blit_rgb888(reinterpret_cast<const uint8_t *>(state.original),
                                    kVolumeOverlayWidth * (int) sizeof(lv_color_t), 0, 0,
                                    kVolumeOverlayWidth, kVolumeOverlayHeight);
  }
  if (state.arc != nullptr) lv_obj_clear_flag(state.arc, LV_OBJ_FLAG_HIDDEN);
  if (state.knob != nullptr) lv_obj_clear_flag(state.knob, LV_OBJ_FLAG_HIDDEN);
  if (state.label != nullptr) lv_obj_clear_flag(state.label, LV_OBJ_FLAG_HIDDEN);
  if (state.glyph_buffer != nullptr) lv_draw_buf_destroy(state.glyph_buffer);
#ifdef ESP_PLATFORM
  if (state.original != nullptr) heap_caps_free(state.original);
  if (state.background != nullptr) heap_caps_free(state.background);
  if (state.scratch != nullptr) heap_caps_free(state.scratch);
#else
  std::free(state.original);
  std::free(state.background);
  std::free(state.scratch);
#endif
  state = {};
  state.visual_pct = -1;
  state.value_pct = -1;
  volume_overlay_reset_visual_cache();
}

inline float volume_overlay_coverage_sq(float distance_sq, float radius) {
  const float inner = radius - 0.75f;
  const float outer = radius + 0.75f;
  const float inner_sq = inner * inner;
  const float outer_sq = outer * outer;
  if (distance_sq <= inner_sq) return 1.0f;
  if (distance_sq >= outer_sq) return 0.0f;
  return (outer_sq - distance_sq) / (outer_sq - inner_sq);
}

inline void volume_overlay_draw_capsule(lv_color_t *buffer, int stride, int origin_x, int origin_y,
                                        int width, int height, float ax, float ay, float bx, float by,
                                        float radius, uint8_t red, uint8_t green, uint8_t blue) {
  const float min_x_f = std::min(ax, bx) - radius - 1.0f;
  const float max_x_f = std::max(ax, bx) + radius + 1.0f;
  const float min_y_f = std::min(ay, by) - radius - 1.0f;
  const float max_y_f = std::max(ay, by) + radius + 1.0f;
  const int x1 = std::max(origin_x, (int) floorf(min_x_f));
  const int y1 = std::max(origin_y, (int) floorf(min_y_f));
  const int x2 = std::min(origin_x + width - 1, (int) ceilf(max_x_f));
  const int y2 = std::min(origin_y + height - 1, (int) ceilf(max_y_f));
  if (x1 > x2 || y1 > y2) return;

  const float vx = bx - ax;
  const float vy = by - ay;
  const float length_sq = vx * vx + vy * vy;
  for (int screen_y = y1; screen_y <= y2; screen_y++) {
    lv_color_t *row = buffer + (size_t) (screen_y - origin_y) * stride;
    for (int screen_x = x1; screen_x <= x2; screen_x++) {
      const float px = (float) screen_x + 0.5f;
      const float py = (float) screen_y + 0.5f;
      float t = 0.0f;
      if (length_sq > 0.0f) {
        t = ((px - ax) * vx + (py - ay) * vy) / length_sq;
        t = std::clamp(t, 0.0f, 1.0f);
      }
      const float dx = px - (ax + t * vx);
      const float dy = py - (ay + t * vy);
      volume_overlay_blend(row[screen_x - origin_x], red, green, blue,
                           volume_overlay_coverage_sq(dx * dx + dy * dy, radius));
    }
  }
}

inline void volume_overlay_draw_disc(lv_color_t *buffer, int stride, int origin_x, int origin_y,
                                     int width, int height, float cx, float cy, float radius,
                                     uint8_t red, uint8_t green, uint8_t blue) {
  volume_overlay_draw_capsule(buffer, stride, origin_x, origin_y, width, height,
                              cx, cy, cx, cy, radius, red, green, blue);
}

inline bool volume_overlay_direct_prepare(lv_obj_t *arc, lv_obj_t *knob, lv_obj_t *label) {
  auto &state = volume_overlay_direct_state;
  volume_overlay_direct_end();
  static_assert(sizeof(lv_color_t) == 3, "The regional volume compositor requires RGB888");
  constexpr size_t background_pixel_count = (size_t) kVolumeOverlayWidth * kVolumeOverlayHeight;
  constexpr size_t background_byte_count = background_pixel_count * sizeof(lv_color_t);
  constexpr size_t scratch_pixel_count = (size_t) kVolumeOverlayWidth * kVolumeOverlayCaptureHeight;
  constexpr size_t scratch_byte_count = scratch_pixel_count * sizeof(lv_color_t);
  constexpr size_t original_pixel_count = (size_t) kVolumeOverlayWidth * kVolumeOverlayHeight;
  constexpr size_t original_byte_count = original_pixel_count * sizeof(lv_color_t);
#ifdef ESP_PLATFORM
  state.original = static_cast<lv_color_t *>(
      heap_caps_malloc(original_byte_count, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
  state.background = static_cast<lv_color_t *>(
      heap_caps_malloc(background_byte_count, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
  state.scratch = static_cast<lv_color_t *>(
      heap_caps_malloc(scratch_byte_count, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
#else
  state.original = static_cast<lv_color_t *>(std::malloc(original_byte_count));
  state.background = static_cast<lv_color_t *>(std::malloc(background_byte_count));
  state.scratch = static_cast<lv_color_t *>(std::malloc(scratch_byte_count));
#endif
  state.glyph_buffer = lv_draw_buf_create(128, 160, LV_COLOR_FORMAT_A8, LV_STRIDE_AUTO);
  state.arc = arc;
  state.knob = knob;
  state.label = label;
  state.font = label != nullptr ? lv_obj_get_style_text_font(label, LV_PART_MAIN) : nullptr;
  state.letter_space = label != nullptr ? lv_obj_get_style_text_letter_space(label, LV_PART_MAIN) : 0;
  if (state.original == nullptr || state.background == nullptr || state.scratch == nullptr ||
      state.glyph_buffer == nullptr || state.font == nullptr ||
      !lvgl_esphome_direct_capture_rgb888(reinterpret_cast<uint8_t *>(state.original),
                                          kVolumeOverlayWidth * (int) sizeof(lv_color_t), 0, 0,
                                          kVolumeOverlayWidth, kVolumeOverlayHeight)) {
    volume_overlay_direct_end(false);
    return false;
  }

  memcpy(state.background, state.original, background_byte_count);

  for (int pct = 0; pct <= 100; pct++) {
    volume_overlay_point_for_pct(pct, state.point_x[pct], state.point_y[pct]);
  }

  // Prepare the expensive capture and dimming while the long-press timer is
  // running. Activation then needs only a tiny clock-area patch and PPA blits.
  uint8_t dim_lut[256];
  for (int value = 0; value < 256; value++) {
    dim_lut[value] = (uint8_t) ((value * 28 + 50) / 100);
  }
  for (size_t i = 0; i < background_pixel_count; i++) {
    state.background[i].red = dim_lut[state.background[i].red];
    state.background[i].green = dim_lut[state.background[i].green];
    state.background[i].blue = dim_lut[state.background[i].blue];
  }
  for (int pct = 0; pct < 100; pct++) {
    volume_overlay_draw_capsule(state.background, kVolumeOverlayWidth, 0, 0,
                                kVolumeOverlayWidth, kVolumeOverlayCaptureHeight,
                                state.point_x[pct], state.point_y[pct],
                                state.point_x[pct + 1], state.point_y[pct + 1],
                                7.5f, 0x38, 0x29, 0x49);
  }
  state.prepared = true;
  state.visual_pct = -1;
  state.value_pct = -1;
  volume_overlay_reset_visual_cache();
  return true;
}

inline bool volume_overlay_direct_begin(lv_obj_t *arc, lv_obj_t *knob, lv_obj_t *label) {
  auto &state = volume_overlay_direct_state;
  if (!state.prepared || state.arc != arc || state.knob != knob || state.label != label) {
    if (!volume_overlay_direct_prepare(arc, knob, label)) return false;
  }

  if (arc != nullptr) lv_obj_add_flag(arc, LV_OBJ_FLAG_HIDDEN);
  if (knob != nullptr) lv_obj_add_flag(knob, LV_OBJ_FLAG_HIDDEN);
  if (label != nullptr) lv_obj_add_flag(label, LV_OBJ_FLAG_HIDDEN);

  // The clock is hidden immediately before activation. Refresh only its old
  // footprint in the prepared frame instead of recapturing 800x800.
  constexpr int clock_x = 280;
  constexpr int clock_y = 0;
  constexpr int clock_width = 240;
  constexpr int clock_height = 84;
  lv_color_t *clock_target = state.original + (size_t) clock_y * kVolumeOverlayWidth + clock_x;
  if (!lvgl_esphome_direct_capture_rgb888(reinterpret_cast<uint8_t *>(clock_target),
                                           kVolumeOverlayWidth * (int) sizeof(lv_color_t),
                                           clock_x, clock_y, clock_width, clock_height)) {
    volume_overlay_direct_end(false);
    return false;
  }
  uint8_t dim_lut[256];
  for (int value = 0; value < 256; value++) {
    dim_lut[value] = (uint8_t) ((value * 28 + 50) / 100);
  }
  for (int y = clock_y; y < clock_y + clock_height; y++) {
    for (int x = clock_x; x < clock_x + clock_width; x++) {
      const lv_color_t source = state.original[(size_t) y * kVolumeOverlayWidth + x];
      lv_color_t &dest = state.background[(size_t) y * kVolumeOverlayWidth + x];
      dest.red = dim_lut[source.red];
      dest.green = dim_lut[source.green];
      dest.blue = dim_lut[source.blue];
    }
  }
  // Only the top-center part of the pre-rendered track was covered when the
  // clock disappeared. Redraw that short section instead of all 100 segments.
  for (int pct = 30; pct < 70; pct++) {
    volume_overlay_draw_capsule(state.background, kVolumeOverlayWidth, 0, 0,
                                kVolumeOverlayWidth, kVolumeOverlayCaptureHeight,
                                state.point_x[pct], state.point_y[pct],
                                state.point_x[pct + 1], state.point_y[pct + 1],
                                7.5f, 0x38, 0x29, 0x49);
  }

  state.active = true;
  // The LVGL preview is populated before direct mode starts. Its values are
  // therefore identical to the first direct frame; without clearing both
  // caches that frame is treated as a no-op and the percentage appears only
  // after the finger moves.
  state.visual_pct = -1;
  state.value_pct = -1;
  volume_overlay_reset_visual_cache();
  if (!lvgl_esphome_direct_blit_rgb888(reinterpret_cast<const uint8_t *>(state.background),
                                        kVolumeOverlayWidth * (int) sizeof(lv_color_t), 0, 0,
                                        kVolumeOverlayWidth, kVolumeOverlayHeight)) {
    volume_overlay_direct_end(false);
    return false;
  }
  state.presented = true;

  return true;
}

inline void volume_overlay_direct_cancel_prepare() {
  if (!volume_overlay_direct_state.active) volume_overlay_direct_end(false);
}

inline bool volume_overlay_direct_is_active() { return volume_overlay_direct_state.active; }

inline void volume_overlay_blend(lv_color_t &dst, uint8_t red, uint8_t green, uint8_t blue, float coverage) {
  if (coverage <= 0.0f) return;
  const int alpha = std::clamp((int) lroundf(coverage * 255.0f), 0, 255);
  dst.red = (uint8_t) (((int) dst.red * (255 - alpha) + (int) red * alpha + 127) / 255);
  dst.green = (uint8_t) (((int) dst.green * (255 - alpha) + (int) green * alpha + 127) / 255);
  dst.blue = (uint8_t) (((int) dst.blue * (255 - alpha) + (int) blue * alpha + 127) / 255);
}

inline void volume_overlay_point_for_pct(int pct, float &x, float &y) {
  constexpr float kPi = 3.14159265358979323846f;
  const float angle = (180.0f + (float) clamp_volume_pct(pct) * 1.8f) * kPi / 180.0f;
  x = kVolumeOverlayCenterX + cosf(angle) * kVolumeOverlayArcRadius;
  y = kVolumeOverlayCenterY + sinf(angle) * kVolumeOverlayArcRadius;
}

inline bool volume_overlay_direct_draw_value(int value_pct) {
  auto &state = volume_overlay_direct_state;
  if (!state.active || state.font == nullptr || state.glyph_buffer == nullptr) return false;
  value_pct = clamp_volume_pct(value_pct);
  if (value_pct == state.value_pct) return true;

  constexpr int label_x = 180;
  constexpr int label_y = 320;
  constexpr int label_width = 440;
  constexpr int label_height = 160;
  for (int y = 0; y < label_height; y++) {
    memcpy(state.scratch + (size_t) y * label_width,
           state.background + (size_t) (label_y + y) * kVolumeOverlayWidth + label_x,
           (size_t) label_width * sizeof(lv_color_t));
  }

  char text[8];
  snprintf(text, sizeof(text), "%d%%", value_pct);
  lv_font_glyph_dsc_t glyphs[4]{};
  int glyph_count = 0;
  int text_width = 0;
  for (int i = 0; text[i] != '\0' && glyph_count < 4; i++) {
    const uint32_t next = text[i + 1] == '\0' ? 0 : (uint8_t) text[i + 1];
    if (!lv_font_get_glyph_dsc(state.font, &glyphs[glyph_count], (uint8_t) text[i], next)) continue;
    text_width += glyphs[glyph_count].adv_w;
    if (text[i + 1] != '\0') text_width += state.letter_space;
    glyph_count++;
  }

  int pen_x = 400 - text_width / 2;
  const int line_y = 400 - state.font->line_height / 2;
  for (int i = 0; i < glyph_count; i++) {
    auto &glyph = glyphs[i];
    const auto *draw_buf = static_cast<const lv_draw_buf_t *>(lv_font_get_glyph_bitmap(&glyph, state.glyph_buffer));
    if (draw_buf != nullptr && glyph.box_w > 0 && glyph.box_h > 0) {
      const int glyph_x = pen_x + glyph.ofs_x;
      const int glyph_y = line_y + (state.font->line_height - state.font->base_line) - glyph.box_h - glyph.ofs_y;
      const int glyph_stride = lv_draw_buf_width_to_stride(glyph.box_w, LV_COLOR_FORMAT_A8);
      for (int gy = 0; gy < glyph.box_h; gy++) {
        const int screen_y = glyph_y + gy;
        if (screen_y < label_y || screen_y >= label_y + label_height) continue;
        const uint8_t *alpha_row = draw_buf->data + (size_t) gy * glyph_stride;
        lv_color_t *dest_row = state.scratch + (size_t) (screen_y - label_y) * label_width;
        for (int gx = 0; gx < glyph.box_w; gx++) {
          const int screen_x = glyph_x + gx;
          if (screen_x < label_x || screen_x >= label_x + label_width) continue;
          volume_overlay_blend(dest_row[screen_x - label_x], 0xF5, 0xEE, 0xFB, alpha_row[gx] / 255.0f);
        }
      }
    }
    pen_x += glyph.adv_w + state.letter_space;
    lv_font_glyph_release_draw_data(&glyph);
  }

  if (!lvgl_esphome_direct_blit_rgb888(reinterpret_cast<const uint8_t *>(state.scratch),
                                        label_width * (int) sizeof(lv_color_t), label_x, label_y,
                                        label_width, label_height)) {
    volume_overlay_direct_end();
    return false;
  }
  state.value_pct = value_pct;
  return true;
}

inline bool volume_overlay_direct_update(int visual_pct, int value_pct) {
  auto &state = volume_overlay_direct_state;
  if (!state.active || state.background == nullptr || state.scratch == nullptr) return false;
  visual_pct = clamp_volume_pct(visual_pct);
  value_pct = clamp_volume_pct(value_pct);
  if (visual_pct == state.visual_pct) return volume_overlay_direct_draw_value(value_pct);

  const int old_pct = state.visual_pct < 0 ? 0 : state.visual_pct;
  const float old_x = state.point_x[old_pct];
  const float old_y = state.point_y[old_pct];
  const float new_x = state.point_x[visual_pct];
  const float new_y = state.point_y[visual_pct];

  constexpr int margin = 38;
  int x1 = (int) floorf(std::min(old_x, new_x)) - margin;
  int y1 = (int) floorf(std::min(old_y, new_y)) - margin;
  int x2 = (int) ceilf(std::max(old_x, new_x)) + margin;
  int y2 = (int) ceilf(std::max(old_y, new_y)) + margin;
  if (std::min(old_pct, visual_pct) <= 50 && std::max(old_pct, visual_pct) >= 50) {
    x1 = std::min(x1, (int) floorf(kVolumeOverlayCenterX) - margin);
    x2 = std::max(x2, (int) ceilf(kVolumeOverlayCenterX) + margin);
    y1 = std::min(y1, (int) floorf(kVolumeOverlayCenterY - kVolumeOverlayArcRadius) - margin);
  }
  x1 = std::clamp(x1, 0, kVolumeOverlayWidth - 1);
  y1 = std::clamp(y1, 0, kVolumeOverlayCaptureHeight - 1);
  x2 = std::clamp(x2, x1, kVolumeOverlayWidth - 1);
  y2 = std::clamp(y2, y1, kVolumeOverlayCaptureHeight - 1);
  const int width = x2 - x1 + 1;
  const int height = y2 - y1 + 1;

  // Restore only the portion touched by the old/new progress endpoint.
  for (int local_y = 0; local_y < height; local_y++) {
    const int screen_y = y1 + local_y;
    memcpy(state.scratch + (size_t) local_y * width,
           state.background + (size_t) screen_y * kVolumeOverlayWidth + x1,
           (size_t) width * sizeof(lv_color_t));
  }

  // Repaint the bright portion clipped to the restored rectangle. The loop
  // has only 100 cheap segment checks; rasterization occurs for intersecting
  // segments only and contains no per-pixel trigonometry.
  for (int pct = 0; pct < visual_pct; pct++) {
    volume_overlay_draw_capsule(state.scratch, width, x1, y1, width, height,
                                state.point_x[pct], state.point_y[pct],
                                state.point_x[pct + 1], state.point_y[pct + 1],
                                7.5f, 0xF5, 0xEE, 0xFB);
  }
  volume_overlay_draw_disc(state.scratch, width, x1, y1, width, height,
                           new_x, new_y, 28.0f, 0xFF, 0xFF, 0xFF);

  if (!lvgl_esphome_direct_blit_rgb888(reinterpret_cast<const uint8_t *>(state.scratch),
                                        width * (int) sizeof(lv_color_t), x1, y1, width, height)) {
    volume_overlay_direct_end();
    return false;
  }
  state.visual_pct = visual_pct;
  return volume_overlay_direct_draw_value(value_pct);
}

inline void volume_overlay_update_visual(lv_obj_t *arc, lv_obj_t *knob, lv_obj_t *label, int value_pct, int visual_pct) {
  value_pct = clamp_volume_pct(value_pct);
  visual_pct = clamp_volume_pct(visual_pct);

  auto &cache = volume_overlay_visual_cache;
  if (arc == cache.arc && knob == cache.knob && label == cache.label && value_pct == cache.value_pct &&
      visual_pct == cache.visual_pct) {
    return;
  }
  cache.arc = arc;
  cache.knob = knob;
  cache.label = label;
  cache.value_pct = value_pct;
  cache.visual_pct = visual_pct;

  const bool direct_presented = volume_overlay_direct_update(visual_pct, value_pct);
  if (!direct_presented && arc != nullptr) {
    lv_arc_set_value(arc, visual_pct);
  }

  if (!direct_presented && label != nullptr) {
    char buf[8];
    snprintf(buf, sizeof(buf), "%d%%", value_pct);
    lv_label_set_text(label, buf);
  }

  if (!direct_presented && knob != nullptr) {
    constexpr float kPi = 3.14159265358979323846f;
    const float angle = (180.0f + (float) visual_pct * 1.8f) * kPi / 180.0f;
    const int knob_w = lv_obj_get_width(knob);
    const int knob_h = lv_obj_get_height(knob);
    const int x = (int) lroundf(kVolumeOverlayCenterX + cosf(angle) * kVolumeOverlayArcRadius - (float) knob_w * 0.5f);
    const int y = (int) lroundf(kVolumeOverlayCenterY + sinf(angle) * kVolumeOverlayArcRadius - (float) knob_h * 0.5f);
    lv_obj_set_pos(knob, x, y);
  }
}

inline void volume_overlay_update(lv_obj_t *arc, lv_obj_t *knob, lv_obj_t *label, int value_pct, int knob_pct) {
  volume_overlay_update_visual(arc, knob, label, value_pct, knob_pct);
}

inline int volume_arc_pct_from_x(int touch_x) {
  constexpr float kPi = 3.14159265358979323846f;
  float ratio = ((float) touch_x - kVolumeOverlayCenterX) / kVolumeOverlayArcRadius;
  if (ratio < -1.0f) ratio = -1.0f;
  if (ratio > 1.0f) ratio = 1.0f;
  const float angle = 360.0f - acosf(ratio) * 180.0f / kPi;
  return clamp_volume_pct((int) lroundf((angle - 180.0f) / 1.8f));
}

inline int volume_arc_pct_from_point(int touch_x, int touch_y) {
  constexpr float kPi = 3.14159265358979323846f;

  float angle = atan2f((float) touch_y - kVolumeOverlayCenterY, (float) touch_x - kVolumeOverlayCenterX) * 180.0f / kPi;
  if (angle < 0.0f) angle += 360.0f;

  // The control is the top semicircle. If the finger slips below the center,
  // keep the value on the nearest end instead of wrapping through the bottom.
  if (angle < 180.0f) {
    angle = touch_x < (int) kVolumeOverlayCenterX ? 180.0f : 360.0f;
  }
  if (angle > 360.0f) angle = 360.0f;

  return clamp_volume_pct((int) lroundf((angle - 180.0f) / 1.8f));
}

inline void volume_overlay_update_drag_point(
    lv_obj_t *arc, lv_obj_t *knob, lv_obj_t *label, int value_pct, int visual_pct, int touch_x, int touch_y) {
  (void) touch_x;
  (void) touch_y;
  volume_overlay_update_visual(arc, knob, label, value_pct, visual_pct);
}

inline int volume_drag_value_from_x(int touch_x, int start_x, int start_pct) {
  const int touch_pct = volume_arc_pct_from_x(touch_x);
  const int start_touch_pct = volume_arc_pct_from_x(start_x);
  start_pct = clamp_volume_pct(start_pct);

  if (touch_pct >= start_touch_pct) {
    const int span = 100 - start_touch_pct;
    if (span <= 0) return 100;
    return clamp_volume_pct(start_pct + ((touch_pct - start_touch_pct) * (100 - start_pct) + span / 2) / span);
  }

  const int span = start_touch_pct;
  if (span <= 0) return 0;
  return clamp_volume_pct(start_pct - ((start_touch_pct - touch_pct) * start_pct + span / 2) / span);
}

inline int volume_drag_value_from_visual_pct(int visual_pct, int start_pct) {
  visual_pct = clamp_volume_pct(visual_pct);
  start_pct = clamp_volume_pct(start_pct);

  if (visual_pct >= 50) {
    return clamp_volume_pct(start_pct + ((visual_pct - 50) * (100 - start_pct) + 25) / 50);
  }

  return clamp_volume_pct(start_pct - ((50 - visual_pct) * start_pct + 25) / 50);
}

inline int volume_knob_pct_from_x(int touch_x) {
  return volume_arc_pct_from_x(touch_x);
}

}  // namespace atmosfera_ui
