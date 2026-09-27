#!/usr/bin/env python3
"""Apply the Atmosfera accent and outline treatment to weather Lottie assets."""

from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
from typing import Any


OUTLINE_NAME = "Atmosfera outline"
SHAPE_TYPES = {"el", "rc", "sh", "sr"}
RAY_WIDTH_SCALE = 0.55
RAY_GEOMETRY_MARKER = "aeh-ray-width-v1"


def parse_hex_color(value: str) -> list[float]:
    value = value.removeprefix("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError("colors must use six hexadecimal digits")
    try:
        return [int(value[index : index + 2], 16) / 255.0 for index in (0, 2, 4)]
    except ValueError as err:
        raise argparse.ArgumentTypeError("colors must use six hexadecimal digits") from err


def read_static_color(item: dict[str, Any]) -> list[float] | None:
    value = item.get("c", {}).get("k")
    if (
        isinstance(value, list)
        and len(value) >= 3
        and all(isinstance(channel, (int, float)) for channel in value[:3])
    ):
        return [float(channel) for channel in value]
    return None


def recolor_value(value: Any, color: list[float]) -> None:
    if isinstance(value, list):
        if len(value) >= 3 and all(isinstance(channel, (int, float)) for channel in value[:3]):
            value[:3] = color
            return
        for child in value:
            recolor_value(child, color)
    elif isinstance(value, dict):
        for key in ("k", "s", "e"):
            if key in value:
                recolor_value(value[key], color)


def recolor(item: dict[str, Any], color: list[float]) -> None:
    color_property = item.get("c")
    if isinstance(color_property, dict):
        recolor_value(color_property, color)


def is_neutral_highlight(color: list[float] | None) -> bool:
    return color is not None and min(color[:3]) >= 0.85 and max(color[:3]) - min(color[:3]) <= 0.08


def scalar_value(property_value: Any, fallback: float) -> float:
    if not isinstance(property_value, dict):
        return fallback
    value = property_value.get("k")
    if isinstance(value, (int, float)):
        return float(value)
    return fallback


def _transform_absolute_point(point: list[Any], center: tuple[float, float], radial: tuple[float, float],
                              tangent: tuple[float, float], width_scale: float) -> None:
    if len(point) < 2 or not all(isinstance(value, (int, float)) for value in point[:2]):
        return
    dx = float(point[0]) - center[0]
    dy = float(point[1]) - center[1]
    radial_distance = dx * radial[0] + dy * radial[1]
    # Keep the radial position unchanged and compress only the tangential
    # width. The explicit projection avoids changing the ray length or its
    # distance from the weather icon's center.
    tangent_distance = dx * tangent[0] + dy * tangent[1]
    point[0] = center[0] + radial_distance * radial[0] + tangent_distance * width_scale * tangent[0]
    point[1] = center[1] + radial_distance * radial[1] + tangent_distance * width_scale * tangent[1]


def _transform_relative_vector(vector: list[Any], radial: tuple[float, float], tangent: tuple[float, float],
                               width_scale: float) -> None:
    if len(vector) < 2 or not all(isinstance(value, (int, float)) for value in vector[:2]):
        return
    radial_distance = float(vector[0]) * radial[0] + float(vector[1]) * radial[1]
    tangent_distance = float(vector[0]) * tangent[0] + float(vector[1]) * tangent[1]
    vector[0] = radial_distance * radial[0] + tangent_distance * width_scale * tangent[0]
    vector[1] = radial_distance * radial[1] + tangent_distance * width_scale * tangent[1]


def _narrow_path_value(path_value: dict[str, Any], width_scale: float) -> bool:
    vertices = path_value.get("v")
    if not isinstance(vertices, list):
        return False
    valid_vertices = [point for point in vertices if isinstance(point, list) and len(point) >= 2 and
                      all(isinstance(value, (int, float)) for value in point[:2])]
    if not valid_vertices:
        return False

    # Weather assets use a 128 x 128 composition. The center is deliberately
    # kept in source coordinates so the same transform works for every ray.
    center = (64.0, 64.0)
    centroid = (
        sum(float(point[0]) for point in valid_vertices) / len(valid_vertices),
        sum(float(point[1]) for point in valid_vertices) / len(valid_vertices),
    )
    radial_x = centroid[0] - center[0]
    radial_y = centroid[1] - center[1]
    radial_length = math.hypot(radial_x, radial_y)
    if radial_length < 0.001:
        return False
    radial = (radial_x / radial_length, radial_y / radial_length)
    tangent = (-radial[1], radial[0])

    for point in vertices:
        if isinstance(point, list):
            _transform_absolute_point(point, center, radial, tangent, width_scale)
    for key in ("i", "o"):
        vectors = path_value.get(key)
        if isinstance(vectors, list):
            for vector in vectors:
                if isinstance(vector, list):
                    _transform_relative_vector(vector, radial, tangent, width_scale)
    return True


def _narrow_ray_group(group: dict[str, Any], width_scale: float, marker: str) -> None:
    if group.get(RAY_GEOMETRY_MARKER) == marker:
        return
    changed = False
    for item in group.get("it", []):
        if not isinstance(item, dict) or item.get("ty") != "sh":
            continue
        key = item.get("ks", {}).get("k")
        if isinstance(key, dict):
            changed = _narrow_path_value(key, width_scale) or changed
        elif isinstance(key, list):
            for keyframe in key:
                if not isinstance(keyframe, dict):
                    continue
                for endpoint in ("s", "e"):
                    values = keyframe.get(endpoint)
                    if isinstance(values, list):
                        for path_value in values:
                            if isinstance(path_value, dict):
                                changed = _narrow_path_value(path_value, width_scale) or changed
    if changed:
        group[RAY_GEOMETRY_MARKER] = marker


def make_outline(width: float, color: list[float], template: dict[str, Any] | None = None) -> dict[str, Any]:
    outline = copy.deepcopy(template) if template is not None else {}
    outline.update(
        {
            "ty": "st",
            "nm": OUTLINE_NAME,
            "c": {"a": 0, "k": [*color, 1]},
            "o": {"a": 0, "k": 100},
            "w": {"a": 0, "k": width},
            "lc": 2,
            "lj": 2,
            "ml": 4,
        }
    )
    return outline


def style_group(group: dict[str, Any], accent: list[float], outline: list[float], outline_width: float,
                narrow_rays: bool, ray_width_scale: float, ray_marker: str) -> None:
    items = group.get("it")
    if not isinstance(items, list):
        return

    for item in items:
        if isinstance(item, dict) and item.get("ty") == "gr":
            style_group(item, accent, outline, outline_width, narrow_rays, ray_width_scale, ray_marker)

    if narrow_rays:
        _narrow_ray_group(group, ray_width_scale, ray_marker)

    # Generated outlines are replaced on every run, making the operation
    # idempotent and allowing a later accent-token update in place.
    items[:] = [
        item
        for item in items
        if not (isinstance(item, dict) and item.get("ty") == "st" and item.get("nm") == OUTLINE_NAME)
    ]

    has_geometry = any(isinstance(item, dict) and item.get("ty") in SHAPE_TYPES for item in items)
    fills = [item for item in items if isinstance(item, dict) and item.get("ty") == "fl"]
    strokes = [item for item in items if isinstance(item, dict) and item.get("ty") == "st"]

    for fill in fills:
        if not is_neutral_highlight(read_static_color(fill)):
            recolor(fill, accent)

    for stroke in strokes:
        if not is_neutral_highlight(read_static_color(stroke)):
            recolor(stroke, accent)

    if not has_geometry:
        return

    transform_index = next(
        (index for index, item in enumerate(items) if isinstance(item, dict) and item.get("ty") == "tr"),
        len(items),
    )
    if strokes:
        # Stroke-only details such as rain and fog keep their original visual
        # stroke and receive a wider black stroke underneath it.
        visual = strokes[0]
        visual_width = scalar_value(visual.get("w"), 1.0)
        visual_index = items.index(visual)
        items.insert(visual_index, make_outline(visual_width + 2.0 * outline_width, outline, visual))
    elif fills:
        # Filled shapes use the same source-space outline thickness as the SVG
        # in the reference slide. Round joins avoid sharp corners after scale.
        items.insert(transform_index, make_outline(outline_width, outline))


def style_document(document: dict[str, Any], accent: list[float], outline: list[float], outline_width: float,
                   ray_width_scale: float) -> None:
    ray_marker = f"{RAY_GEOMETRY_MARKER}:{ray_width_scale:g}"

    def walk(value: Any, in_rays_layer: bool = False) -> None:
        if isinstance(value, dict):
            if value.get("ty") == "gr":
                style_group(value, accent, outline, outline_width, in_rays_layer, ray_width_scale, ray_marker)
                return
            in_rays_layer = in_rays_layer or value.get("nm") == "Rays"
            for child in value.values():
                walk(child, in_rays_layer)
        elif isinstance(value, list):
            for child in value:
                walk(child, in_rays_layer)

    walk(document)


def serialize(document: dict[str, Any]) -> str:
    return json.dumps(document, ensure_ascii=False, separators=(",", ":")) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=Path("assets/animations/weather"))
    parser.add_argument("--accent", type=parse_hex_color, default=parse_hex_color("36BCF0"))
    parser.add_argument("--outline", type=parse_hex_color, default=parse_hex_color("0D0D0D"))
    parser.add_argument("--outline-width", type=float, default=2.6)
    parser.add_argument("--ray-width-scale", type=float, default=RAY_WIDTH_SCALE)
    parser.add_argument("--check", action="store_true", help="fail when an asset is not in generated form")
    args = parser.parse_args()

    changed: list[Path] = []
    for path in sorted(args.directory.glob("*.json")):
        original = path.read_text(encoding="utf-8")
        document = json.loads(original)
        style_document(document, args.accent, args.outline, args.outline_width, args.ray_width_scale)
        generated = serialize(document)
        if generated != original:
            changed.append(path)
            if not args.check:
                path.write_text(generated, encoding="utf-8", newline="\n")

    if args.check and changed:
        names = ", ".join(path.name for path in changed)
        raise SystemExit(f"weather assets need regeneration: {names}")
    verb = "checked" if args.check else "styled"
    print(f"{verb} {len(list(args.directory.glob('*.json')))} weather animations; changed={len(changed)}")


if __name__ == "__main__":
    main()
