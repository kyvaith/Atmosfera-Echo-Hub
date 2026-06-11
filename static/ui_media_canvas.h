#pragma once

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdint>

namespace atmosfera_ui {

static constexpr int MEDIA_MAIN_CANVAS = 267;
static constexpr float MEDIA_MAIN_CENTER = (MEDIA_MAIN_CANVAS - 1) * 0.5f;
static constexpr float MEDIA_SCALE = 3.3333333f;
static constexpr float MEDIA_PI = 3.14159265358979323846f;
static constexpr int MEDIA_MAX_PATH_POINTS = 420;

struct MediaPoint {
  float x;
  float y;
};

struct MediaCubic {
  float x1;
  float y1;
  float x2;
  float y2;
  float x3;
  float y3;
};

static constexpr MediaPoint shape_start = {25.140100f, 2.250200f};
static constexpr MediaCubic shape_curves[] = {
    {28.241500f, -0.750069f, 33.163500f, -0.750067f, 36.264800f, 2.250200f},
    {36.264800f, 2.250200f, 36.544300f, 2.520550f, 36.544300f, 2.520550f},
    {38.317800f, 4.236230f, 40.783800f, 5.037490f, 43.227000f, 4.691900f},
    {43.227000f, 4.691900f, 43.612000f, 4.637450f, 43.612000f, 4.637450f},
    {47.884600f, 4.033120f, 51.866600f, 6.926190f, 52.612100f, 11.176400f},
    {52.612100f, 11.176400f, 52.679300f, 11.559400f, 52.679300f, 11.559400f},
    {53.105600f, 13.989800f, 54.629700f, 16.087500f, 56.809400f, 17.244100f},
    {56.809400f, 17.244100f, 57.152900f, 17.426300f, 57.152900f, 17.426300f},
    {60.964700f, 19.448700f, 62.485700f, 24.129800f, 60.590600f, 28.006500f},
    {60.590600f, 28.006500f, 60.419900f, 28.355800f, 60.419900f, 28.355800f},
    {59.336200f, 30.572700f, 59.336200f, 33.165600f, 60.419900f, 35.382500f},
    {60.419900f, 35.382500f, 60.590600f, 35.731800f, 60.590600f, 35.731800f},
    {62.485700f, 39.608500f, 60.964700f, 44.289600f, 57.152900f, 46.312100f},
    {57.152900f, 46.312100f, 56.809400f, 46.494300f, 56.809400f, 46.494300f},
    {54.629700f, 47.650800f, 53.105600f, 49.748500f, 52.679300f, 52.179000f},
    {52.679300f, 52.179000f, 52.612100f, 52.561900f, 52.612100f, 52.561900f},
    {51.866600f, 56.812200f, 47.884600f, 59.705200f, 43.612000f, 59.100900f},
    {43.612000f, 59.100900f, 43.227000f, 59.046400f, 43.227000f, 59.046400f},
    {40.783800f, 58.700900f, 38.317800f, 59.502100f, 36.544300f, 61.217800f},
    {36.544300f, 61.217800f, 36.264800f, 61.488100f, 36.264800f, 61.488100f},
    {33.163400f, 64.488400f, 28.241500f, 64.488400f, 25.140100f, 61.488100f},
    {25.140100f, 61.488100f, 24.860700f, 61.217800f, 24.860700f, 61.217800f},
    {23.087200f, 59.502100f, 20.621100f, 58.700900f, 18.177900f, 59.046400f},
    {18.177900f, 59.046400f, 17.792900f, 59.100900f, 17.792900f, 59.100900f},
    {13.520300f, 59.705200f, 9.538380f, 56.812200f, 8.792830f, 52.561900f},
    {8.792830f, 52.561900f, 8.725650f, 52.179000f, 8.725650f, 52.179000f},
    {8.299320f, 49.748500f, 6.775240f, 47.650800f, 4.595480f, 46.494300f},
    {4.595480f, 46.494300f, 4.252020f, 46.312100f, 4.252020f, 46.312100f},
    {0.440213f, 44.289600f, -1.080760f, 39.608500f, 0.814293f, 35.731800f},
    {0.814293f, 35.731800f, 0.985045f, 35.382500f, 0.985045f, 35.382500f},
    {2.068720f, 33.165600f, 2.068720f, 30.572700f, 0.985044f, 28.355800f},
    {0.985044f, 28.355800f, 0.814291f, 28.006500f, 0.814291f, 28.006500f},
    {-1.080760f, 24.129800f, 0.440215f, 19.448700f, 4.252020f, 17.426300f},
    {4.252020f, 17.426300f, 4.595480f, 17.244100f, 4.595480f, 17.244100f},
    {6.775240f, 16.087500f, 8.299320f, 13.989800f, 8.725650f, 11.559400f},
    {8.725650f, 11.559400f, 8.792830f, 11.176400f, 8.792830f, 11.176400f},
    {9.538380f, 6.926180f, 13.520300f, 4.033120f, 17.792900f, 4.637450f},
    {17.792900f, 4.637450f, 18.177900f, 4.691900f, 18.177900f, 4.691900f},
    {20.621100f, 5.037490f, 23.087200f, 4.236230f, 24.860700f, 2.520540f},
    {24.860700f, 2.520540f, 25.140100f, 2.250200f, 25.140100f, 2.250200f},
};

static constexpr MediaPoint progress_start = {39.348900f, 0.249827f};
static constexpr MediaCubic progress_curves[] = {
    {39.827400f, -0.018619f, 40.389300f, -0.057566f, 40.922900f, 0.070354f},
    {42.631600f, 0.479969f, 44.264300f, 1.293440f, 45.669300f, 2.514000f},
    {47.827500f, 4.388730f, 50.612700f, 5.367270f, 53.455400f, 5.264000f},
    {53.455400f, 5.264000f, 54.024800f, 5.228850f, 54.024800f, 5.228850f},
    {59.609200f, 4.742360f, 64.700500f, 8.441130f, 65.963200f, 13.902700f},
    {66.650200f, 16.873700f, 68.514000f, 19.438700f, 71.127300f, 21.010100f},
    {75.931000f, 23.898900f, 77.875300f, 29.883700f, 75.686900f, 35.044300f},
    {74.496300f, 37.851600f, 74.496400f, 41.022100f, 75.686900f, 43.829400f},
    {77.875600f, 48.990100f, 75.931100f, 54.975700f, 71.127300f, 57.864600f},
    {71.127300f, 57.864600f, 70.645900f, 58.170300f, 70.645900f, 58.170300f},
    {68.285200f, 59.757700f, 66.607300f, 62.186600f, 65.963200f, 64.972000f},
    {65.963200f, 64.972000f, 65.833400f, 65.478800f, 65.833400f, 65.478800f},
    {64.428200f, 70.493700f, 59.749800f, 73.892400f, 54.546200f, 73.679000f},
    {54.546200f, 73.679000f, 54.024800f, 73.645800f, 54.024800f, 73.645800f},
    {50.987000f, 73.381000f, 47.971300f, 74.361000f, 45.669300f, 76.360700f},
    {45.669300f, 76.360700f, 45.266000f, 76.694700f, 45.266000f, 76.694700f},
    {41.181600f, 79.925600f, 35.399100f, 79.925700f, 31.314800f, 76.694700f},
    {31.314800f, 76.694700f, 30.912500f, 76.360700f, 30.912500f, 76.360700f},
    {28.610500f, 74.360900f, 25.594800f, 73.381200f, 22.557000f, 73.645800f},
    {22.557000f, 73.645800f, 22.034500f, 73.679000f, 22.034500f, 73.679000f},
    {16.831100f, 73.892300f, 12.153500f, 70.493600f, 10.748400f, 65.478800f},
    {10.748400f, 65.478800f, 10.618500f, 64.972000f, 10.618500f, 64.972000f},
    {9.974540f, 62.186700f, 8.296390f, 59.757700f, 5.935900f, 58.170300f},
    {5.935900f, 58.170300f, 5.454450f, 57.864600f, 5.454450f, 57.864600f},
    {0.800206f, 55.066100f, -1.170010f, 49.361700f, 0.701521f, 44.315800f},
    {0.701521f, 44.315800f, 0.894880f, 43.829400f, 0.894880f, 43.829400f},
    {2.010800f, 41.197600f, 2.080580f, 38.246200f, 1.103860f, 35.574600f},
    {1.103860f, 35.574600f, 0.894880f, 35.044300f, 0.894880f, 35.044300f},
    {-1.225480f, 30.044700f, 0.532378f, 24.271600f, 5.012070f, 21.289400f},
    {5.012070f, 21.289400f, 5.454450f, 21.010100f, 5.454450f, 21.010100f},
    {5.516160f, 20.973000f, 5.577420f, 20.935300f, 5.638220f, 20.897000f},
    {6.523890f, 20.339500f, 7.577650f, 19.917200f, 8.529650f, 20.351900f},
    {9.935120f, 20.993600f, 9.787990f, 22.869700f, 8.532120f, 23.769700f},
    {8.203710f, 24.005000f, 7.864840f, 24.228000f, 7.515970f, 24.437800f},
    {4.419820f, 26.299500f, 3.165990f, 30.156800f, 4.576520f, 33.482800f},
    {6.190460f, 37.288300f, 6.190370f, 41.586400f, 4.576520f, 45.391900f},
    {3.166170f, 48.717900f, 4.419910f, 52.575200f, 7.515970f, 54.436900f},
    {11.058200f, 56.567000f, 13.584800f, 60.043500f, 14.516000f, 64.070600f},
    {15.329800f, 67.590500f, 18.610300f, 69.974200f, 22.209300f, 69.660500f},
    {26.327300f, 69.301600f, 30.415000f, 70.630300f, 33.535500f, 73.341200f},
    {36.262800f, 75.710300f, 40.319000f, 75.710400f, 43.046200f, 73.341200f},
    {46.166700f, 70.630600f, 50.253700f, 69.301700f, 54.371400f, 69.660500f},
    {57.970400f, 69.974000f, 61.252000f, 67.590400f, 62.065800f, 64.070600f},
    {62.997000f, 60.043500f, 65.523400f, 56.566900f, 69.065800f, 54.436900f},
    {72.161600f, 52.575100f, 73.414700f, 48.717800f, 72.004300f, 45.391900f},
    {70.390300f, 41.586400f, 70.390300f, 37.288300f, 72.004300f, 33.482800f},
    {73.414600f, 30.156900f, 72.161700f, 26.299500f, 69.065800f, 24.437800f},
    {65.523200f, 22.307700f, 62.996900f, 18.830500f, 62.065800f, 14.803100f},
    {61.251900f, 11.283500f, 57.970200f, 8.899730f, 54.371400f, 9.213220f},
    {50.253700f, 9.572070f, 46.166700f, 8.244140f, 43.046200f, 5.533530f},
    {42.515000f, 5.072030f, 41.933400f, 4.700560f, 41.320900f, 4.419030f},
    {39.290400f, 3.485660f, 37.399800f, 1.343130f, 39.348900f, 0.249827f},
};

static constexpr MediaPoint base_start = {20.613800f, 0.571805f};
static constexpr MediaCubic base_curves[] = {
    {21.543700f, -0.236071f, 22.981600f, -0.216709f, 23.655300f, 0.814637f},
    {23.951100f, 1.267500f, 24.177800f, 1.776450f, 24.316900f, 2.330590f},
    {24.381600f, 2.588140f, 24.249500f, 2.848060f, 24.027300f, 2.993450f},
    {23.753800f, 3.172390f, 23.489700f, 3.371720f, 23.236900f, 3.591340f},
    {20.116300f, 6.302150f, 16.028600f, 7.629930f, 11.910700f, 7.271020f},
    {8.311770f, 6.957390f, 5.031260f, 9.341220f, 4.217320f, 12.860900f},
    {4.120640f, 13.279000f, 4.006570f, 13.691100f, 3.875900f, 14.096400f},
    {3.396370f, 15.583500f, 1.638390f, 16.313800f, 0.578649f, 15.165600f},
    {0.538065f, 15.121600f, 0.498449f, 15.077100f, 0.459795f, 15.032000f},
    {-0.126881f, 14.348300f, -0.069839f, 13.378600f, 0.177281f, 12.512200f},
    {0.177281f, 12.512200f, 0.319860f, 11.960500f, 0.319860f, 11.960500f},
    {1.582610f, 6.498670f, 6.673630f, 2.799800f, 12.258300f, 3.286650f},
    {15.106300f, 3.534820f, 17.934200f, 2.688520f, 20.173400f, 0.934110f},
    {20.173400f, 0.934110f, 20.613800f, 0.571805f, 20.613800f, 0.571805f},
};

inline void media_canvas_set_px(lv_obj_t *canvas, int x, int y, uint32_t rgb, lv_opa_t opa = LV_OPA_COVER) {
  if (x < 0 || y < 0 || x >= MEDIA_MAIN_CANVAS || y >= MEDIA_MAIN_CANVAS || opa == LV_OPA_TRANSP) return;
  lv_canvas_set_px(canvas, x, y, lv_color_hex(rgb), opa);
}

inline MediaPoint media_transform_point(float x, float y, float offset_x, float offset_y) {
  return {offset_x + x * MEDIA_SCALE, offset_y + y * MEDIA_SCALE};
}

inline MediaPoint media_cubic_at(const MediaPoint &p0, const MediaCubic &c, float t, float offset_x, float offset_y) {
  const float u = 1.0f - t;
  const float x = (u * u * u * p0.x) + (3.0f * u * u * t * c.x1) + (3.0f * u * t * t * c.x2) + (t * t * t * c.x3);
  const float y = (u * u * u * p0.y) + (3.0f * u * u * t * c.y1) + (3.0f * u * t * t * c.y2) + (t * t * t * c.y3);
  return media_transform_point(x, y, offset_x, offset_y);
}

inline int media_flatten_path(const MediaPoint &start, const MediaCubic *curves, std::size_t curve_count,
                              float offset_x, float offset_y, MediaPoint *points, int max_points) {
  int count = 0;
  MediaPoint current = start;
  points[count++] = media_transform_point(current.x, current.y, offset_x, offset_y);
  for (std::size_t i = 0; i < curve_count && count < max_points; i++) {
    const MediaCubic &c = curves[i];
    for (int step = 1; step <= 5 && count < max_points; step++) {
      points[count++] = media_cubic_at(current, c, step / 5.0f, offset_x, offset_y);
    }
    current = {c.x3, c.y3};
  }
  return count;
}

inline bool media_point_in_polygon(const MediaPoint *points, int count, float x, float y) {
  bool inside = false;
  for (int i = 0, j = count - 1; i < count; j = i++) {
    const float yi = points[i].y;
    const float yj = points[j].y;
    const bool intersects = ((yi > y) != (yj > y)) &&
                            (x < (points[j].x - points[i].x) * (y - yi) / (yj - yi + 0.00001f) + points[i].x);
    if (intersects) inside = !inside;
  }
  return inside;
}

inline float media_clockwise_fraction(float x, float y) {
  const float theta = std::atan2(y - MEDIA_MAIN_CENTER, x - MEDIA_MAIN_CENTER);
  return std::fmod(theta + MEDIA_PI * 0.5f + MEDIA_PI * 2.0f, MEDIA_PI * 2.0f) / (MEDIA_PI * 2.0f);
}

inline void media_draw_path(lv_obj_t *canvas, const MediaPoint &start, const MediaCubic *curves, std::size_t curve_count,
                            float offset_x, float offset_y, uint32_t color, float progress_clip = -1.0f) {
  MediaPoint points[MEDIA_MAX_PATH_POINTS];
  const int count = media_flatten_path(start, curves, curve_count, offset_x, offset_y, points, MEDIA_MAX_PATH_POINTS);
  if (count < 3) return;

  float min_x = points[0].x;
  float max_x = points[0].x;
  float min_y = points[0].y;
  float max_y = points[0].y;
  for (int i = 1; i < count; i++) {
    if (points[i].x < min_x) min_x = points[i].x;
    if (points[i].x > max_x) max_x = points[i].x;
    if (points[i].y < min_y) min_y = points[i].y;
    if (points[i].y > max_y) max_y = points[i].y;
  }

  const int x0 = std::max(0, static_cast<int>(std::floor(min_x)) - 1);
  const int y0 = std::max(0, static_cast<int>(std::floor(min_y)) - 1);
  const int x1 = std::min(MEDIA_MAIN_CANVAS - 1, static_cast<int>(std::ceil(max_x)) + 1);
  const int y1 = std::min(MEDIA_MAIN_CANVAS - 1, static_cast<int>(std::ceil(max_y)) + 1);
  static constexpr float samples[4][2] = {{0.25f, 0.25f}, {0.75f, 0.25f}, {0.25f, 0.75f}, {0.75f, 0.75f}};

  for (int y = y0; y <= y1; y++) {
    for (int x = x0; x <= x1; x++) {
      int covered = 0;
      for (const auto &sample : samples) {
        const float sx = x + sample[0];
        const float sy = y + sample[1];
        if (progress_clip >= 0.0f && media_clockwise_fraction(sx, sy) > progress_clip) continue;
        if (media_point_in_polygon(points, count, sx, sy)) covered++;
      }
      if (covered > 0) {
        media_canvas_set_px(canvas, x, y, color, static_cast<lv_opa_t>((255 * covered) / 4));
      }
    }
  }
}

inline bool media_inside_round_rect(float x, float y, float left, float top, float right, float bottom, float radius) {
  const float cx = x < left + radius ? left + radius : (x > right - radius ? right - radius : x);
  const float cy = y < top + radius ? top + radius : (y > bottom - radius ? bottom - radius : y);
  const float dx = x - cx;
  const float dy = y - cy;
  return dx * dx + dy * dy <= radius * radius;
}

inline void media_draw_pause_icon(lv_obj_t *canvas, uint32_t color) {
  for (int y = 96; y <= 171; y++) {
    for (int x = 103; x <= 164; x++) {
      const float px = x + 0.5f;
      const float py = y + 0.5f;
      if (media_inside_round_rect(px, py, 108.0f, 102.0f, 126.0f, 165.0f, 8.5f) ||
          media_inside_round_rect(px, py, 141.0f, 102.0f, 159.0f, 165.0f, 8.5f)) {
        media_canvas_set_px(canvas, x, y, color);
      }
    }
  }
}

inline void media_draw_play_icon(lv_obj_t *canvas, uint32_t color) {
  for (int y = 96; y <= 171; y++) {
    for (int x = 104; x <= 171; x++) {
      const float px = x + 0.5f;
      const float py = y + 0.5f;
      const float ax = 112.0f;
      const float ay = 99.0f;
      const float bx = 112.0f;
      const float by = 168.0f;
      const float cx = 166.0f;
      const float cy = 133.5f;
      const float e0 = (px - ax) * (by - ay) - (py - ay) * (bx - ax);
      const float e1 = (px - bx) * (cy - by) - (py - by) * (cx - bx);
      const float e2 = (px - cx) * (ay - cy) - (py - cy) * (ax - cx);
      if ((e0 <= 0.0f && e1 <= 0.0f && e2 <= 0.0f) || (e0 >= 0.0f && e1 >= 0.0f && e2 >= 0.0f)) {
        media_canvas_set_px(canvas, x, y, color);
      }
    }
  }
}

inline void draw_media_main_control(lv_obj_t *canvas, int progress_percent, bool playing) {
  if (canvas == nullptr) return;
  if (progress_percent < 0) progress_percent = 0;
  if (progress_percent > 100) progress_percent = 100;

  lv_canvas_fill_bg(canvas, lv_color_hex(0x000000), LV_OPA_TRANSP);

  const float progress = progress_percent / 100.0f;
  const uint32_t shape_color = 0xE4C2FF;
  const uint32_t progress_color = 0xEDD9F9;
  const uint32_t progress_base_color = 0x2D2136;
  const uint32_t icon_color = 0x37005F;

  media_draw_path(canvas, progress_start, progress_curves, sizeof(progress_curves) / sizeof(progress_curves[0]),
                  5.75f, 1.60f, progress_base_color);
  media_draw_path(canvas, base_start, base_curves, sizeof(base_curves) / sizeof(base_curves[0]), 39.80f, 7.65f,
                  progress_base_color);
  media_draw_path(canvas, progress_start, progress_curves, sizeof(progress_curves) / sizeof(progress_curves[0]),
                  5.75f, 1.60f, progress_color, progress);
  if (progress > 0.80f) {
    media_draw_path(canvas, base_start, base_curves, sizeof(base_curves) / sizeof(base_curves[0]), 39.80f, 7.65f,
                    progress_color, progress);
  }

  media_draw_path(canvas, shape_start, shape_curves, sizeof(shape_curves) / sizeof(shape_curves[0]), 31.70f, 27.20f,
                  shape_color);

  if (playing) {
    media_draw_pause_icon(canvas, icon_color);
  } else {
    media_draw_play_icon(canvas, icon_color);
  }

  lv_obj_invalidate(canvas);
}

}  // namespace atmosfera_ui
