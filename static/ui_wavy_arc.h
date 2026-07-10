#pragma once

#include "lvgl.h"

#include <math.h>

namespace atmosfera_ui {
namespace {

constexpr uint32_t WAVE_ARC_POINT_COUNT = 88;
constexpr uint32_t WAVE_BLOB_POINT_COUNT = 56;
constexpr uint32_t WAVE_BLOB_RING_COUNT = 9;
constexpr float DEG_TO_RAD = 0.017453292519943295769f;

struct WavyArcState {
  lv_obj_t *arc{nullptr};
  bool registered{false};
  float value_pct{0.0f};
  float start_deg{-90.0f};
  float span_deg{330.0f};
  float waves{10.0f};
  float phase_deg{0.0f};
  bool playing{false};
  float amplitude_px{7.0f};
  float progress_gap_deg{9.0f};
  int32_t line_width{13};
  float blob_radius_px{82.0f};
  float ring_margin_px{22.0f};
  lv_color_t base_color{lv_color_hex(0x25182F)};
  lv_color_t progress_color{lv_color_hex(0xEDD9F9)};
  lv_color_t fill_color{lv_color_hex(0xE4C2FF)};
  lv_point_precise_t base_points[WAVE_ARC_POINT_COUNT];
  lv_point_precise_t progress_points[WAVE_ARC_POINT_COUNT];
  lv_point_precise_t blob_points[WAVE_BLOB_RING_COUNT][WAVE_BLOB_POINT_COUNT];
};

static WavyArcState media_wavy_arc;

static float media_wave_at(WavyArcState *state, float angle_rad) {
  return sinf((state->waves * angle_rad) + (state->phase_deg * DEG_TO_RAD));
}

static void get_arc_center(WavyArcState *state, float *cx, float *cy, int32_t *obj_w, int32_t *obj_h) {
  lv_area_t area;
  lv_obj_get_coords(state->arc, &area);
  *obj_w = area.x2 - area.x1 + 1;
  *obj_h = area.y2 - area.y1 + 1;
  *cx = static_cast<float>(area.x1 + area.x2) * 0.5f;
  *cy = static_cast<float>(area.y1 + area.y2) * 0.5f;
}

static void draw_wavy_blob(lv_layer_t *layer, WavyArcState *state) {
  if (layer == nullptr || state == nullptr || state->arc == nullptr) {
    return;
  }

  float cx = 0.0f;
  float cy = 0.0f;
  int32_t obj_w = 0;
  int32_t obj_h = 0;
  get_arc_center(state, &cx, &cy, &obj_w, &obj_h);

  const float max_radius =
      (static_cast<float>(obj_w < obj_h ? obj_w : obj_h) * 0.5f) -
      static_cast<float>(state->line_width) - state->amplitude_px - 24.0f;
  float blob_radius = state->blob_radius_px;
  if (blob_radius > max_radius) {
    blob_radius = max_radius;
  }
  if (blob_radius <= 1.0f) {
    return;
  }

  const float ring_step = blob_radius / static_cast<float>(WAVE_BLOB_RING_COUNT);
  const int32_t ring_width = static_cast<int32_t>(ring_step + 3.5f);

  for (uint32_t ring = 0; ring < WAVE_BLOB_RING_COUNT; ring++) {
    const float radius = ring_step * static_cast<float>(ring + 1);
    const float amp = state->amplitude_px * (radius / blob_radius);
    auto *points = state->blob_points[ring];

    for (uint32_t i = 0; i < WAVE_BLOB_POINT_COUNT; i++) {
      const float t = static_cast<float>(i) / static_cast<float>(WAVE_BLOB_POINT_COUNT - 1);
      const float angle_rad = 360.0f * t * DEG_TO_RAD;
      const float wave = media_wave_at(state, angle_rad);
      const float r = radius + (amp * wave);
      points[i].x = static_cast<lv_value_precise_t>(cx + cosf(angle_rad) * r);
      points[i].y = static_cast<lv_value_precise_t>(cy + sinf(angle_rad) * r);
    }

    lv_draw_line_dsc_t dsc;
    lv_draw_line_dsc_init(&dsc);
    dsc.points = points;
    dsc.point_cnt = WAVE_BLOB_POINT_COUNT;
    dsc.color = state->fill_color;
    dsc.opa = LV_OPA_COVER;
    dsc.width = ring_width;
    dsc.round_start = 1;
    dsc.round_end = 1;
    lv_draw_line(layer, &dsc);
  }
}

static void draw_wavy_arc_line(lv_layer_t *layer, WavyArcState *state, float value_pct, lv_color_t color,
                               lv_point_precise_t *points) {
  if (layer == nullptr || state == nullptr || state->arc == nullptr || value_pct <= 0.0f) {
    return;
  }

  float cx = 0.0f;
  float cy = 0.0f;
  int32_t obj_w = 0;
  int32_t obj_h = 0;
  get_arc_center(state, &cx, &cy, &obj_w, &obj_h);
  const float base_radius =
      (static_cast<float>(obj_w < obj_h ? obj_w : obj_h) * 0.5f) -
      static_cast<float>(state->line_width) - state->amplitude_px - 4.0f;
  const float blob_radius =
      state->blob_radius_px + state->ring_margin_px + (static_cast<float>(state->line_width) * 0.5f);

  if (base_radius <= 1.0f || blob_radius <= 1.0f) {
    return;
  }

  if (value_pct > 100.0f) {
    value_pct = 100.0f;
  }
  float visible_span = state->span_deg * (value_pct / 100.0f);
  if (value_pct > 0.0f && value_pct < 100.0f && visible_span > state->progress_gap_deg) {
    visible_span -= state->progress_gap_deg;
  }

  for (uint32_t i = 0; i < WAVE_ARC_POINT_COUNT; i++) {
    const float t = static_cast<float>(i) / static_cast<float>(WAVE_ARC_POINT_COUNT - 1);
    const float angle_rad = (state->start_deg + visible_span * t) * DEG_TO_RAD;
    const float wave = media_wave_at(state, angle_rad);
    float r = blob_radius + (state->amplitude_px * wave);
    if (r > base_radius) {
      r = base_radius;
    }
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
  draw_wavy_blob(layer, state);
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

inline void media_wavy_arc_set_playing(bool playing) {
  auto &state = media_wavy_arc;
  if (state.playing == playing) {
    return;
  }
  state.playing = playing;
  if (state.arc != nullptr) {
    lv_obj_invalidate(state.arc);
  }
}

inline void media_wavy_arc_tick(float degrees) {
  auto &state = media_wavy_arc;
  if (!state.playing || state.arc == nullptr) {
    return;
  }
  state.phase_deg += degrees;
  while (state.phase_deg >= 360.0f) {
    state.phase_deg -= 360.0f;
  }
  while (state.phase_deg < 0.0f) {
    state.phase_deg += 360.0f;
  }
  lv_obj_invalidate(state.arc);
}

}  // namespace atmosfera_ui
