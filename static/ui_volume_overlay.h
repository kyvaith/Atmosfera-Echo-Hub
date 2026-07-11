#pragma once

#include <cmath>
#include "lvgl.h"

namespace atmosfera_ui {

constexpr float kVolumeOverlayCenterX = 400.0f;
constexpr float kVolumeOverlayCenterY = 400.0f;
constexpr float kVolumeOverlayArcRadius = 357.5f;

inline int clamp_volume_pct(int pct) {
  if (pct < 0) return 0;
  if (pct > 100) return 100;
  return pct;
}

inline void volume_overlay_update_visual(lv_obj_t *arc, lv_obj_t *knob, lv_obj_t *label, int value_pct, int visual_pct) {
  value_pct = clamp_volume_pct(value_pct);
  visual_pct = clamp_volume_pct(visual_pct);

  if (arc != nullptr) {
    lv_arc_set_value(arc, visual_pct);
  }

  if (label != nullptr) {
    char buf[8];
    snprintf(buf, sizeof(buf), "%d%%", value_pct);
    lv_label_set_text(label, buf);
  }

  if (knob != nullptr) {
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
