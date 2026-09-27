#!/usr/bin/env python3
"""Validate the measured product Home geometry and weather asset contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REFERENCE = {
    "home_clock_x": 40,
    "home_clock_y": 66,
    "home_clock_width": 380,
    "home_clock_height": 390,
    "home_minute_text_x": 43,
    "home_minute_text_y": 256,
    "home_minute_text_width": 380,
    "home_minute_text_height": 390,
    "home_weather_x": 0,
    "home_weather_y": 0,
    "home_weather_width": 800,
    "home_weather_height": 800,
    "home_weather_lottie_x": 402,
    "home_weather_lottie_y": 68,
    "home_weather_lottie_size": 384,
    "home_weather_pill_x": 431,
    "home_weather_pill_y": 489,
    "home_weather_pill_width": 400,
    "home_weather_pill_height": 114,
    "home_mic_x": 356,
    "home_mic_y": 610,
    "home_mic_size": 90,
    "home_page_indicator_x": 352,
    "home_page_indicator_y": 737,
    "home_volume_icon_x": 339,
    "home_wifi_icon_x": 391,
    "home_status_icon_y": 11,
}

LEGACY_CLOCK_IDS = (
    # The old top clock was also exposed through this activation-surface ID.
    # Keep the name forbidden so a future merge cannot accidentally resurrect
    # the obsolete clock contract while retaining the volume gesture.
    "global_time_button",
    "global_clock_suppressed",
    "global_time_activation_anchor",
    "global_time_label",
    "settings_time_label",
    "home_time_label_1",
    "home_time_label_2",
    "home_time_label_3",
    "home_time_label_4",
)

FIRST_PAGE_COMPATIBILITY_WIDGETS = (
    "tile_light_button",
    "tile_climate_button",
    "tile_slider_card",
)


def substitutions(path: Path) -> dict[str, int]:
    result: dict[str, int] = {}
    pattern = re.compile(r"^\s{2}([A-Za-z0-9_]+):\s*['\"]?(-?\d+)['\"]?\s*$", re.MULTILINE)
    for name, value in pattern.findall(path.read_text(encoding="utf-8")):
        result[name] = int(value)
    return result


def walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def validate_assets(directory: Path, accent: tuple[float, float, float], outline: tuple[float, float, float]) -> list[str]:
    errors: list[str] = []
    assets = sorted(directory.glob("*.json"))
    if len(assets) != 9:
        errors.append(f"expected 9 weather JSON assets, found {len(assets)}")
    for path in assets:
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            errors.append(f"{path.name}: invalid JSON: {err}")
            continue
        generated_outlines = [
            item
            for item in walk(document)
            if item.get("ty") == "st" and item.get("nm") == "Atmosfera outline"
        ]
        if not generated_outlines:
            errors.append(f"{path.name}: no generated Atmosfera outline")
        for item in generated_outlines:
            color = item.get("c", {}).get("k")
            if not isinstance(color, list) or len(color) < 3 or tuple(color[:3]) != outline:
                errors.append(f"{path.name}: generated outline has the wrong color")
        for item in walk(document):
            if item.get("ty") not in {"fl", "st"} or item.get("nm") == "Atmosfera outline":
                continue
            color = item.get("c", {}).get("k")
            if not isinstance(color, list) or len(color) < 3:
                continue
            # White cloud/highlight details are intentionally retained.
            neutral = min(color[:3]) >= 0.85 and max(color[:3]) - min(color[:3]) <= 0.08
            if not neutral and tuple(color[:3]) != accent:
                errors.append(f"{path.name}: non-neutral paint is outside the accent token")
    return errors


def validate_source_contract(source_root: Path) -> list[str]:
    errors: list[str] = []
    yaml_files = tuple((source_root / "modules").rglob("*.yaml"))
    for path in yaml_files:
        text = path.read_text(encoding="utf-8")
        for legacy_id in LEGACY_CLOCK_IDS:
            if re.search(rf"\bid:\s*{re.escape(legacy_id)}\b", text):
                errors.append(f"{path}: legacy clock object {legacy_id!r} is still declared")

    page_path = source_root / "modules/lvgl/pages/tiles_m3.yaml"
    page = page_path.read_text(encoding="utf-8")
    for widget_id in FIRST_PAGE_COMPATIBILITY_WIDGETS:
        hidden = re.search(
            rf"\bid:\s*{re.escape(widget_id)}\s*\n\s*hidden:\s*true\b",
            page,
        )
        if hidden is None:
            errors.append(f"{page_path}: compatibility widget {widget_id!r} is not forced hidden")

    material_path = source_root / "modules/lvgl/material.yaml"
    material = material_path.read_text(encoding="utf-8")
    for widget_id in FIRST_PAGE_COMPATIBILITY_WIDGETS[:2]:
        always_hidden = re.search(
            rf"widget:\s*{re.escape(widget_id)}[^\n]*always_hidden:\s*true",
            material,
        )
        if always_hidden is None:
            errors.append(f"{material_path}: compatibility widget {widget_id!r} can be made visible")

    if "id: home_minute_shadow" in page:
        errors.append(f"{page_path}: the obsolete duplicate minute shadow is still declared")
    if "text_font: cherry_bomb_300_outline" not in page:
        errors.append(f"{page_path}: minute text has no registered bitmap contour")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yaml", type=Path, default=Path("atmosfera-echo-hub.yaml"))
    parser.add_argument("--assets", type=Path, default=Path("assets/animations/weather"))
    parser.add_argument("--source-root", type=Path, default=Path("."))
    args = parser.parse_args()

    values = substitutions(args.yaml)
    errors: list[str] = []
    for name, expected in REFERENCE.items():
        actual = values.get(name)
        if actual != expected:
            errors.append(f"{name}: expected {expected}, found {actual}")
    if values.get("display_width") != 800 or values.get("display_height") != 800:
        errors.append("display_width/display_height must remain 800 for the measured reference")

    errors.extend(validate_assets(args.assets, (70 / 255, 177 / 255, 225 / 255), (13 / 255, 13 / 255, 13 / 255)))
    errors.extend(validate_source_contract(args.source_root))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"M3 Home geometry valid: {len(REFERENCE)} measured tokens; weather assets valid: 9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
