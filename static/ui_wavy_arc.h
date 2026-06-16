#pragma once

#include "lvgl.h"

#include <math.h>

namespace atmosfera_ui {
namespace {

constexpr uint32_t WAVE_ARC_POINT_COUNT = 112;
constexpr float DEG_TO_RAD = 0.017453292519943295769f;

struct WavyArcState {
  lv_obj_t *arc{nullptr};
  bool registered{false};
  float value_pct{0.0f};
  float start_deg{-90.0f};
  float span_deg{359.0f};
  float waves{9.0f};
  float phase_deg{0.0f};
  float amplitude_px{5.0f};
  int32_t line_width{11};
  lv_color_t base_color{lv_color_hex(0x25182F)};
  lv_color_t progress_color{lv_color_hex(0xEDD9F9)};
  lv_point_precise_t base_points[WAVE_ARC_POINT_COUNT];
  lv_point_precise_t progress_points[WAVE_ARC_POINT_COUNT];
};

static WavyArcState media_wavy_arc;

static void draw_wavy_arc_line(lv_layer_t *layer, WavyArcState *state, float value_pct, lv_color_t color,
                               lv_point_precise_t *points) {
  if (layer == nullptr || state == nullptr || state->arc == nullptr || value_pct <= 0.0f) {
    return;
  }

  lv_area_t area;
  lv_obj_get_coords(state->arc, &area);
  const int32_t obj_w = area.x2 - area.x1 + 1;
  const int32_t obj_h = area.y2 - area.y1 + 1;
  const float cx = static_cast<float>(area.x1 + area.x2) * 0.5f;
  const float cy = static_cast<float>(area.y1 + area.y2) * 0.5f;
  const float base_radius =
      (static_cast<float>(obj_w < obj_h ? obj_w : obj_h) * 0.5f) -
      static_cast<float>(state->line_width) - state->amplitude_px - 4.0f;

  if (base_radius <= 1.0f) {
    return;
  }

  if (value_pct > 100.0f) {
    value_pct = 100.0f;
  }
  const float visible_span = state->span_deg * (value_pct / 100.0f);
  const float phase = state->phase_deg * DEG_TO_RAD;

  for (uint32_t i = 0; i < WAVE_ARC_POINT_COUNT; i++) {
    const float t = static_cast<float>(i) / static_cast<float>(WAVE_ARC_POINT_COUNT - 1);
    const float angle_rad = (state->start_deg + visible_span * t) * DEG_TO_RAD;
    const float wave = sinf((2.0f * 3.14159265358979323846f * state->waves * t) + phase);
    const float r = base_radius + (state->amplitude_px * wave);
    points[i].x = static_cast<lv_value_precise_t>(cx + cosf(angle_rad) * r);
    points[i].y = static_cast<lv_value_precise_t>(cy + sinf(angle_rad) * r);
  }

  lv_draw_line_dsc_t dsc;
  lv_draw_line_dsc_init(&dsc);
  dsc.points = points;
  dsc.point_cnt = WAVE_ARC_POINT_COUNT;
  dsc.color = color;
  dsc.opa = LV_OPA_COVER;
  dsc.width = state->line_width;
  dsc.round_start = 1;
  dsc.round_end = 1;
  lv_draw_line(layer, &dsc);
}

static void media_wavy_arc_event_cb(lv_event_t *event) {
  auto *state = static_cast<WavyArcState *>(lv_event_get_user_data(event));
  if (state == nullptr) {
    return;
  }

  const lv_event_code_t code = lv_event_get_code(event);
  if (code == LV_EVENT_REFR_EXT_DRAW_SIZE) {
    lv_event_set_ext_draw_size(event, state->line_width + static_cast<int32_t>(state->amplitude_px) + 6);
    return;
  }

  if (code != LV_EVENT_DRAW_POST) {
    return;
  }

  lv_layer_t *layer = lv_event_get_layer(event);
  draw_wavy_arc_line(layer, state, 100.0f, state->base_color, state->base_points);
  draw_wavy_arc_line(layer, state, state->value_pct, state->progress_color, state->progress_points);
}

}  // namespace

inline void media_wavy_arc_init(lv_obj_t *arc) {
  if (arc == nullptr) {
    return;
  }

  auto &state = media_wavy_arc;
  if (!state.registered || state.arc != arc) {
    state.arc = arc;
    state.registered = true;
    lv_obj_add_event_cb(arc, media_wavy_arc_event_cb, LV_EVENT_ALL, &state);
  }

  lv_obj_set_style_arc_opa(arc, LV_OPA_TRANSP, LV_PART_MAIN);
  lv_obj_set_style_arc_opa(arc, LV_OPA_TRANSP, LV_PART_INDICATOR);
  lv_obj_remove_style(arc, nullptr, LV_PART_KNOB);
  lv_obj_remove_flag(arc, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_invalidate(arc);
}

inline void media_wavy_arc_set_value(int progress) {
  auto &state = media_wavy_arc;
  if (progress < 0) {
    progress = 0;
  } else if (progress > 100) {
    progress = 100;
  }
  state.value_pct = static_cast<float>(progress);
  if (state.arc != nullptr) {
    lv_obj_invalidate(state.arc);
  }
}

}  // namespace atmosfera_ui
