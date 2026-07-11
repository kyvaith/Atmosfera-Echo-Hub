#pragma once

#include "lvgl.h"

#include <math.h>
#include <stdint.h>
#include <string.h>

#ifdef ESP_PLATFORM
#include "esp_cache.h"
#include "esp_heap_caps.h"
#endif

namespace atmosfera_ui {
namespace {

constexpr int WAVE_SIZE = 267;
constexpr int WAVE_PIXELS = WAVE_SIZE * WAVE_SIZE;
constexpr int WAVE_BYTES = WAVE_PIXELS * static_cast<int>(sizeof(lv_color32_t));
constexpr int WAVE_CACHE_ALIGN = 128;
constexpr float DEG_TO_RAD = 0.017453292519943295769f;

struct WavyArcState {
  lv_obj_t *arc{nullptr};
  bool registered{false};
  bool buffers_ready{false};
  bool dirty{true};
  int value_permille{0};
  bool playing{false};
  bool pending{false};
  int phase_deg{0};
  int last_rendered_value{-1};
  int last_rendered_phase{-1};
  bool last_rendered_pending{false};
  lv_color32_t *pixels{nullptr};
  uint16_t *radius_q4{nullptr};
  uint16_t *angle_deg{nullptr};
  int16_t sin_q8[360];
  lv_image_dsc_t image{};
};

static WavyArcState media_wavy_arc;

static int align_up(int value, int alignment) {
  return (value + alignment - 1) & ~(alignment - 1);
}

static uint8_t edge_coverage(int32_t distance_q4) {
  if (distance_q4 >= 16) {
    return 255;
  }
  if (distance_q4 <= -16) {
    return 0;
  }
  return static_cast<uint8_t>(((distance_q4 + 16) * 255) / 32);
}

static int angle_delta_cw(int start_deg, int angle_deg) {
  int delta = angle_deg - start_deg;
  while (delta < 0) {
    delta += 360;
  }
  while (delta >= 360) {
    delta -= 360;
  }
  return delta;
}

static bool angle_in_segment(int start_deg, int sweep_deg, int angle_deg) {
  if (sweep_deg <= 0) {
    return false;
  }
  if (sweep_deg >= 360) {
    return true;
  }
  return angle_delta_cw(start_deg, angle_deg) <= sweep_deg;
}

static int angle_distance(int a, int b) {
  int d = a - b;
  while (d < 0) {
    d += 360;
  }
  while (d >= 360) {
    d -= 360;
  }
  return d > 180 ? 360 - d : d;
}

static int iabs_int(int value) {
  return value < 0 ? -value : value;
}

static uint8_t cap_coverage(int radius_q4, int angle, int cap_angle, int cap_radius_q4, int half_width_q4) {
  const int deg = angle_distance(angle, cap_angle);
  if (deg > 5) {
    return 0;
  }
  const int radial_q4 = radius_q4 - cap_radius_q4;
  const int arc_q4 = (cap_radius_q4 * deg * 314) / 18000;
  const int distance_q4 = static_cast<int>(sqrtf(static_cast<float>(radial_q4 * radial_q4 + arc_q4 * arc_q4)));
  return edge_coverage(half_width_q4 - distance_q4);
}

static void sync_pixels_for_draw(WavyArcState *state) {
#ifdef ESP_PLATFORM
  if (state == nullptr || state->pixels == nullptr) {
    return;
  }
  const int aligned_size = align_up(WAVE_BYTES, WAVE_CACHE_ALIGN);
  esp_cache_msync(state->pixels, aligned_size, ESP_CACHE_MSYNC_FLAG_DIR_C2M | ESP_CACHE_MSYNC_FLAG_TYPE_DATA);
#else
  (void) state;
#endif
}

static void init_image_descriptor(WavyArcState *state) {
  memset(&state->image, 0, sizeof(state->image));
  state->image.header.magic = LV_IMAGE_HEADER_MAGIC;
  state->image.header.cf = LV_COLOR_FORMAT_ARGB8888;
  state->image.header.w = WAVE_SIZE;
  state->image.header.h = WAVE_SIZE;
  state->image.header.stride = WAVE_SIZE * sizeof(lv_color32_t);
  state->image.data_size = WAVE_BYTES;
  state->image.data = reinterpret_cast<const uint8_t *>(state->pixels);
}

static bool ensure_buffers(WavyArcState *state) {
  if (state == nullptr) {
    return false;
  }
  if (state->buffers_ready) {
    return true;
  }

#ifdef ESP_PLATFORM
  const int aligned_bytes = align_up(WAVE_BYTES, WAVE_CACHE_ALIGN);
  state->pixels = static_cast<lv_color32_t *>(
      heap_caps_aligned_alloc(WAVE_CACHE_ALIGN, aligned_bytes, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
  state->radius_q4 = static_cast<uint16_t *>(heap_caps_malloc(WAVE_PIXELS * sizeof(uint16_t),
                                                              MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
  state->angle_deg = static_cast<uint16_t *>(heap_caps_malloc(WAVE_PIXELS * sizeof(uint16_t),
                                                              MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT));
#else
  state->pixels = static_cast<lv_color32_t *>(malloc(WAVE_BYTES));
  state->radius_q4 = static_cast<uint16_t *>(malloc(WAVE_PIXELS * sizeof(uint16_t)));
  state->angle_deg = static_cast<uint16_t *>(malloc(WAVE_PIXELS * sizeof(uint16_t)));
#endif

  if (state->pixels == nullptr || state->radius_q4 == nullptr || state->angle_deg == nullptr) {
    return false;
  }

  for (int i = 0; i < 360; i++) {
    state->sin_q8[i] = static_cast<int16_t>(sinf(static_cast<float>(i) * DEG_TO_RAD) * 256.0f);
  }

  const float center = (static_cast<float>(WAVE_SIZE) - 1.0f) * 0.5f;
  for (int y = 0; y < WAVE_SIZE; y++) {
    for (int x = 0; x < WAVE_SIZE; x++) {
      const int idx = y * WAVE_SIZE + x;
      const float dx = (static_cast<float>(x) - center);
      const float dy = (static_cast<float>(y) - center);
      const float radius = sqrtf(dx * dx + dy * dy);
      float angle = atan2f(dy, dx) / DEG_TO_RAD;
      if (angle < 0.0f) {
        angle += 360.0f;
      }
      state->radius_q4[idx] = static_cast<uint16_t>(radius * 16.0f + 0.5f);
      state->angle_deg[idx] = static_cast<uint16_t>(static_cast<int>(angle + 0.5f) % 360);
    }
  }

  init_image_descriptor(state);
  state->buffers_ready = true;
  state->dirty = true;
  return true;
}

static lv_color32_t color_with_alpha(uint8_t red, uint8_t green, uint8_t blue, uint8_t alpha) {
  lv_color32_t color;
  color.red = red;
  color.green = green;
  color.blue = blue;
  color.alpha = alpha;
  return color;
}

static uint8_t scaled_alpha(uint8_t coverage, uint8_t opacity) {
  return static_cast<uint8_t>((static_cast<int>(coverage) * static_cast<int>(opacity) + 127) / 255);
}

static void render_bitmap(WavyArcState *state) {
  if (!ensure_buffers(state)) {
    return;
  }

  const int phase = state->phase_deg;
  const int progress = state->value_permille < 0 ? 0 : (state->value_permille > 1000 ? 1000 : state->value_permille);
  const bool pending = state->pending;
  if (!state->dirty && state->last_rendered_phase == phase && state->last_rendered_value == progress &&
      state->last_rendered_pending == pending) {
    return;
  }

  constexpr int waves = 10;
  constexpr int blob_amplitude_q4 = 4 * 16;
  constexpr int ring_amplitude_q4 = 6 * 16;
  constexpr int blob_radius_q4 = 84 * 16;
  constexpr int ring_radius_q4 = 107 * 16;
  constexpr int ring_half_width_q4 = 6 * 16;
  constexpr int track_start = 270;
  constexpr int split_gap_deg = 12;
  constexpr int min_segment_sweep = 10;
  constexpr int loading_sweep = 18;

  const bool finite_track = progress > 0 && progress < 1000;
  const int finite_available_sweep = 360 - (2 * split_gap_deg);
  const int finite_variable_sweep = finite_available_sweep - (2 * min_segment_sweep);
  const int progress_sweep = finite_track ? (min_segment_sweep + (finite_variable_sweep * progress) / 1000)
                                          : (360 * progress) / 1000;
  const int played_start = track_start;
  const int played_end = (played_start + progress_sweep) % 360;
  const int remaining_start = finite_track ? (played_end + split_gap_deg) % 360 : played_end;
  const int remaining_end = finite_track ? (track_start - split_gap_deg + 360) % 360 : track_start;
  const int played_sweep = progress_sweep;
  const int remaining_sweep = finite_track ? (finite_available_sweep - played_sweep) : (360 - progress_sweep);
  const int loading_start = (track_start + (phase * 5)) % 360;
  const int played_start_wave_index = (played_start * waves + phase) % 360;
  const int played_end_wave_index = (played_end * waves + phase) % 360;
  const int remaining_start_wave_index = (remaining_start * waves + phase) % 360;
  const int remaining_end_wave_index = (remaining_end * waves + phase) % 360;
  const int played_start_radius_q4 =
      ring_radius_q4 +
      (ring_amplitude_q4 *
       state->sin_q8[played_start_wave_index < 0 ? played_start_wave_index + 360 : played_start_wave_index]) /
          256;
  const int played_end_radius_q4 =
      ring_radius_q4 + (ring_amplitude_q4 * state->sin_q8[played_end_wave_index < 0 ? played_end_wave_index + 360
                                                                                    : played_end_wave_index]) /
                           256;
  const int remaining_start_radius_q4 =
      ring_radius_q4 +
      (ring_amplitude_q4 *
       state->sin_q8[remaining_start_wave_index < 0 ? remaining_start_wave_index + 360 : remaining_start_wave_index]) /
          256;
  const int remaining_end_radius_q4 =
      ring_radius_q4 +
      (ring_amplitude_q4 *
       state->sin_q8[remaining_end_wave_index < 0 ? remaining_end_wave_index + 360 : remaining_end_wave_index]) /
          256;
  const lv_color32_t transparent = color_with_alpha(0, 0, 0, 0);

  for (int i = 0; i < WAVE_PIXELS; i++) {
    const int radius = state->radius_q4[i];
    const int angle = state->angle_deg[i];
    const int wave_index = (angle * waves + phase) % 360;
    const int wave_q8 = state->sin_q8[wave_index < 0 ? wave_index + 360 : wave_index];
    const int blob_wave_offset = (blob_amplitude_q4 * wave_q8) / 256;
    const int ring_wave_offset = (ring_amplitude_q4 * wave_q8) / 256;

    const int blob_boundary = blob_radius_q4 + blob_wave_offset;
    const uint8_t fill_alpha = edge_coverage(blob_boundary - radius);

    lv_color32_t out = transparent;
    if (fill_alpha > 0) {
      out = color_with_alpha(0xE4, 0xC2, 0xFF, fill_alpha);
    }

    const bool full_progress = progress >= 1000;
    const bool no_progress = progress <= 0;
    const bool in_played = full_progress || (!no_progress && angle_in_segment(played_start, played_sweep, angle));
    const bool in_remaining = !full_progress && angle_in_segment(remaining_start, remaining_sweep, angle);
    if (in_played || in_remaining) {
      const int ring_boundary = ring_radius_q4 + ring_wave_offset;
      const uint8_t ring_alpha = edge_coverage(ring_half_width_q4 - iabs_int(radius - ring_boundary));
      if (ring_alpha > 0) {
        const bool in_loading = pending && angle_in_segment(loading_start, loading_sweep, angle) &&
                                (full_progress || no_progress || !in_played);
        if (in_loading) {
          out = color_with_alpha(0xF8, 0xEC, 0xFF, scaled_alpha(ring_alpha, 232));
        } else if (in_played) {
          out = color_with_alpha(0xF1, 0xDC, 0xFF, scaled_alpha(ring_alpha, 224));
        } else {
          out = color_with_alpha(0x38, 0x29, 0x49, scaled_alpha(ring_alpha, 220));
        }
      }
    }

    if (finite_track) {
      const int cap_half_width = ring_half_width_q4 - 12;
      const bool before_played_start = angle_delta_cw(angle, played_start) <= 5;
      const bool after_played_end = angle_delta_cw(played_end, angle) <= 5;
      const bool before_remaining_start = angle_delta_cw(angle, remaining_start) <= 5;
      const bool after_remaining_end = angle_delta_cw(remaining_end, angle) <= 5;
      const uint8_t played_start_cap =
          before_played_start ? cap_coverage(radius, angle, played_start, played_start_radius_q4, cap_half_width) : 0;
      const uint8_t played_end_cap =
          after_played_end ? cap_coverage(radius, angle, played_end, played_end_radius_q4, cap_half_width) : 0;
      const uint8_t remaining_start_cap = before_remaining_start
                                              ? cap_coverage(radius, angle, remaining_start, remaining_start_radius_q4,
                                                             cap_half_width)
                                              : 0;
      const uint8_t remaining_end_cap =
          after_remaining_end ? cap_coverage(radius, angle, remaining_end, remaining_end_radius_q4, cap_half_width) : 0;
      const uint8_t played_cap = played_start_cap > played_end_cap ? played_start_cap : played_end_cap;
      const uint8_t remaining_cap =
          remaining_start_cap > remaining_end_cap ? remaining_start_cap : remaining_end_cap;
      if (played_cap > 0 || remaining_cap > 0) {
        if (played_cap >= remaining_cap) {
          out = color_with_alpha(0xF1, 0xDC, 0xFF, scaled_alpha(played_cap, 224));
        } else {
          out = color_with_alpha(0x38, 0x29, 0x49, scaled_alpha(remaining_cap, 220));
        }
      }
    }

    state->pixels[i] = out;
  }

  state->last_rendered_phase = phase;
  state->last_rendered_value = progress;
  state->last_rendered_pending = pending;
  state->dirty = false;
  sync_pixels_for_draw(state);
}

static void draw_bitmap(lv_layer_t *layer, WavyArcState *state) {
  if (layer == nullptr || state == nullptr || state->arc == nullptr) {
    return;
  }

  render_bitmap(state);
  if (!state->buffers_ready || state->pixels == nullptr) {
    return;
  }

  lv_area_t obj_area;
  lv_obj_get_coords(state->arc, &obj_area);
  const int obj_w = obj_area.x2 - obj_area.x1 + 1;
  const int obj_h = obj_area.y2 - obj_area.y1 + 1;
  const int x = obj_area.x1 + (obj_w - WAVE_SIZE) / 2;
  const int y = obj_area.y1 + (obj_h - WAVE_SIZE) / 2;
  lv_area_t img_area;
  img_area.x1 = x;
  img_area.y1 = y;
  img_area.x2 = x + WAVE_SIZE - 1;
  img_area.y2 = y + WAVE_SIZE - 1;

  lv_draw_image_dsc_t dsc;
  lv_draw_image_dsc_init(&dsc);
  dsc.src = &state->image;
  dsc.opa = LV_OPA_COVER;
  dsc.antialias = 0;
  lv_draw_image(layer, &dsc, &img_area);
}

static void media_wavy_arc_event_cb(lv_event_t *event) {
  auto *state = static_cast<WavyArcState *>(lv_event_get_user_data(event));
  if (state == nullptr) {
    return;
  }

  const lv_event_code_t code = lv_event_get_code(event);
  if (code == LV_EVENT_REFR_EXT_DRAW_SIZE) {
    lv_event_set_ext_draw_size(event, 4);
    return;
  }

  if (code == LV_EVENT_DRAW_POST) {
    draw_bitmap(lv_event_get_layer(event), state);
  }
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
  ensure_buffers(&state);
  render_bitmap(&state);
  lv_obj_invalidate(arc);
}

inline void media_wavy_arc_set_value_permille(int progress) {
  auto &state = media_wavy_arc;
  if (progress < 0) {
    progress = 0;
  } else if (progress > 1000) {
    progress = 1000;
  }
  if (state.value_permille == progress) {
    return;
  }
  state.value_permille = progress;
  state.dirty = true;
  render_bitmap(&state);
  if (state.arc != nullptr) {
    lv_obj_invalidate(state.arc);
  }
}

inline void media_wavy_arc_set_value(int progress) {
  media_wavy_arc_set_value_permille(progress * 10);
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

inline void media_wavy_arc_set_pending(bool pending) {
  auto &state = media_wavy_arc;
  if (state.pending == pending) {
    return;
  }
  state.pending = pending;
  state.dirty = true;
  render_bitmap(&state);
  if (state.arc != nullptr) {
    lv_obj_invalidate(state.arc);
  }
}

inline void media_wavy_arc_tick(float degrees) {
  auto &state = media_wavy_arc;
  if ((!state.playing && !state.pending) || state.arc == nullptr) {
    return;
  }
  int step = static_cast<int>(degrees >= 0.0f ? degrees + 0.5f : degrees - 0.5f);
  if (step == 0) {
    step = degrees >= 0.0f ? 1 : -1;
  }
  state.phase_deg += step;
  while (state.phase_deg >= 360) {
    state.phase_deg -= 360;
  }
  while (state.phase_deg < 0) {
    state.phase_deg += 360;
  }
  state.dirty = true;
  render_bitmap(&state);
  lv_obj_invalidate(state.arc);
}

}  // namespace atmosfera_ui
