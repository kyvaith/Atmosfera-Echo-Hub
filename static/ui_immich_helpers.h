#pragma once

#include <algorithm>
#include <cstdlib>
#include <string>
#include <vector>

#include "esp_random.h"
#include "esphome/components/json/json_util.h"

namespace atmosfera_ui {

struct ImmichPhoto {
  std::string asset_id;
  std::string image_url;
  std::string date;
  std::string location;
  std::string person;
  bool is_portrait{false};
  bool orientation_known{false};
};

inline std::string immich_trim_url(std::string url) {
  while (!url.empty() && (url.back() == '/' || url.back() == ' ')) url.pop_back();
  while (!url.empty() && url.front() == ' ') url.erase(url.begin());
  return url;
}

inline bool immich_valid_base_url(const std::string &url) {
  return url.rfind("http://", 0) == 0 || url.rfind("https://", 0) == 0;
}

inline std::vector<std::string> immich_split_csv(const std::string &csv) {
  std::vector<std::string> out;
  size_t start = 0;
  while (start < csv.size()) {
    size_t end = csv.find(',', start);
    if (end == std::string::npos) end = csv.size();
    size_t s = start;
    size_t e = end;
    while (s < e && csv[s] == ' ') s++;
    while (e > s && csv[e - 1] == ' ') e--;
    if (s < e) out.emplace_back(csv.substr(s, e - s));
    start = end + 1;
  }
  return out;
}

inline std::string immich_pick_csv(const std::string &csv) {
  auto values = immich_split_csv(csv);
  if (values.empty()) return "";
  if (values.size() == 1) return values[0];
  return values[esp_random() % values.size()];
}

inline std::string immich_json_array_from_csv(const std::string &csv) {
  auto values = immich_split_csv(csv);
  std::string body = "[";
  for (size_t i = 0; i < values.size(); i++) {
    if (i != 0) body += ",";
    body += "\"" + values[i] + "\"";
  }
  body += "]";
  return body;
}

inline std::string immich_search_body(int size, const std::string &source, const std::string &album_ids,
                                      const std::string &person_ids, const std::string &tag_ids,
                                      const std::string &date_from, const std::string &date_to) {
  std::string body = "{\"size\":" + std::to_string(size) +
                     ",\"type\":\"IMAGE\",\"visibility\":\"timeline\",\"withExif\":true,\"withPeople\":true";
  if (!date_from.empty()) body += ",\"takenAfter\":\"" + date_from + "T00:00:00.000Z\"";
  if (!date_to.empty()) body += ",\"takenBefore\":\"" + date_to + "T23:59:59.999Z\"";
  if (source == "Favorites") {
    body += ",\"isFavorite\":true";
  } else if (source == "Album") {
    body += ",\"albumIds\":" + immich_json_array_from_csv(album_ids);
  } else if (source == "Person") {
    const std::string person = immich_pick_csv(person_ids);
    if (!person.empty()) body += ",\"personIds\":[\"" + person + "\"]";
  } else if (source == "Tag") {
    body += ",\"tagIds\":" + immich_json_array_from_csv(tag_ids);
  }
  body += "}";
  return body;
}

inline bool immich_source_ready(const std::string &source, const std::string &album_ids,
                                const std::string &person_ids, const std::string &tag_ids) {
  if (source == "Album") return !immich_split_csv(album_ids).empty();
  if (source == "Person") return !immich_split_csv(person_ids).empty();
  if (source == "Tag") return !immich_split_csv(tag_ids).empty();
  return true;
}

inline bool immich_orientation_matches(const ImmichPhoto &photo, const std::string &filter) {
  // The ESP32-P4 hardware JPEG path currently fails on Immich portrait thumbnails
  // such as 450x801. In the default mixed mode prefer hardware-decodable
  // landscape assets instead of falling back to software decode on-device.
  if (filter == "Any" || filter.empty()) return !photo.orientation_known || !photo.is_portrait;
  if (!photo.orientation_known) return false;
  if (filter == "Portrait Only") return photo.is_portrait;
  if (filter == "Landscape Only") return !photo.is_portrait;
  return true;
}

inline std::string immich_parse_date(const std::string &raw) {
  if (raw.size() < 10) return "";
  return raw.substr(0, 10);
}

inline std::string immich_parse_asset_object(JsonObject asset, const std::string &base_url, ImmichPhoto *out) {
  if (out == nullptr || asset.isNull() || !asset["id"].is<const char *>()) return "";
  out->asset_id = asset["id"].as<std::string>();
  // Immich's preview is a display-native JPEG (800 px on the long edge in the
  // default server configuration). It preserves all pixels the panel can show
  // while avoiding a multi-megabyte intermediate for the original image.
  // Cover-cropping remains on the ESP32-P4 PPA path.
  // Immich previews are commonly only 800 px on their longest edge. On the
  // round 800x800 panel a landscape preview must then be enlarged from about
  // 800x450, which visibly softens it. Request the original-resolution JPEG;
  // the hardware decoder still crops/scales directly into the display-sized
  // RGB565 surface.
  out->image_url = base_url + "/api/assets/" + out->asset_id + "/original";
  out->date = asset["localDateTime"].is<const char *>() ? immich_parse_date(asset["localDateTime"].as<std::string>()) : "";

  JsonObject exif = asset["exifInfo"].as<JsonObject>();
  if (!exif.isNull()) {
    std::string city = exif["city"].is<const char *>() ? exif["city"].as<std::string>() : "";
    std::string country = exif["country"].is<const char *>() ? exif["country"].as<std::string>() : "";
    if (!city.empty() && !country.empty()) out->location = city + ", " + country;
    else out->location = !city.empty() ? city : country;

    int w = exif["exifImageWidth"].is<int>() ? exif["exifImageWidth"].as<int>() : 0;
    int h = exif["exifImageHeight"].is<int>() ? exif["exifImageHeight"].as<int>() : 0;
    std::string orientation = exif["orientation"].is<const char *>() ? exif["orientation"].as<std::string>() : "";
    if (orientation == "5" || orientation == "6" || orientation == "7" || orientation == "8") std::swap(w, h);
    if (w > 0 && h > 0) {
      out->orientation_known = true;
      out->is_portrait = h > w;
    }
  }

  JsonArray people = asset["people"].as<JsonArray>();
  if (!people.isNull() && people.size() > 0) {
    JsonObject person = people[0].as<JsonObject>();
    if (person["name"].is<const char *>()) out->person = person["name"].as<std::string>();
  }
  return out->image_url;
}

inline bool immich_parse_asset_response(const std::string &body, const std::string &base_url,
                                        const std::string &orientation_filter, ImmichPhoto *out,
                                        const std::string &avoid_asset_id = "") {
  if (out == nullptr) return false;
  auto doc = esphome::json::parse_json(body);
  if (doc.isNull()) return false;

  ImmichPhoto fallback;
  bool has_fallback = false;
  auto try_asset = [&](JsonObject obj) -> bool {
    ImmichPhoto candidate;
    if (immich_parse_asset_object(obj, base_url, &candidate).empty()) return false;
    if (!immich_orientation_matches(candidate, orientation_filter)) return false;
    if (!has_fallback) {
      fallback = candidate;
      has_fallback = true;
    }
    if (!avoid_asset_id.empty() && candidate.asset_id == avoid_asset_id) return false;
    *out = candidate;
    return true;
  };

  if (doc.is<JsonArray>()) {
    JsonArray arr = doc.as<JsonArray>();
    for (size_t i = 0; i < arr.size(); i++) {
      if (try_asset(arr[i].as<JsonObject>())) return true;
    }
    if (has_fallback) {
      *out = fallback;
      return true;
    }
    return false;
  }

  if (doc.is<JsonObject>()) {
    JsonObject root = doc.as<JsonObject>();
    JsonObject assets = root["assets"].as<JsonObject>();
    JsonArray items;
    if (!assets.isNull()) items = assets["items"].as<JsonArray>();
    if (!items.isNull()) {
      for (size_t i = 0; i < items.size(); i++) {
        if (try_asset(items[i].as<JsonObject>())) return true;
      }
      if (has_fallback) {
        *out = fallback;
        return true;
      }
      return false;
    }
    return try_asset(root);
  }

  return false;
}

inline bool immich_parse_memory_response(const std::string &body, const std::string &base_url, ImmichPhoto *out) {
  if (out == nullptr) return false;
  auto doc = esphome::json::parse_json(body);
  if (doc.isNull() || !doc.is<JsonArray>()) return false;
  std::vector<JsonObject> candidates;
  JsonArray memories = doc.as<JsonArray>();
  for (size_t m = 0; m < memories.size(); m++) {
    JsonObject mem = memories[m].as<JsonObject>();
    JsonArray assets = mem["assets"].as<JsonArray>();
    if (assets.isNull()) continue;
    for (size_t a = 0; a < assets.size(); a++) {
      JsonObject asset = assets[a].as<JsonObject>();
      if (asset["type"].is<const char *>() && asset["type"].as<std::string>() != "IMAGE") continue;
      candidates.push_back(asset);
    }
  }
  if (candidates.empty()) return false;
  return !immich_parse_asset_object(candidates[esp_random() % candidates.size()], base_url, out).empty();
}

}  // namespace atmosfera_ui
