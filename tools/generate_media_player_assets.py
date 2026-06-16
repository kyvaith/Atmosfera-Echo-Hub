from __future__ import annotations

import math
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "images" / "figma"

PROGRESS_SIZE = 267
SHAPE_CANVAS = 267
SCALLOP_SIZE = (205, 213)
FIGMA_CONTROL_SIZE = 80.0

COLOR_SHAPE = (228, 194, 255, 255)
COLOR_ICON = (64, 0, 96, 255)
COLOR_PROGRESS_DARK = (38, 27, 48, 210)
COLOR_PROGRESS_LIGHT = (237, 217, 249, 255)


TOKEN_RE = re.compile(r"([MmLlCcZz])|(-?\d+(?:\.\d+)?(?:e[-+]?\d+)?)")


def _path_from_svg(svg_path: Path) -> str:
    text = svg_path.read_text(encoding="utf-8")
    match = re.search(r'\sd="([^"]+)"', text)
    if not match:
        raise ValueError(f"No path data found in {svg_path}")
    return match.group(1)


def _tokens(path_data: str) -> list[str]:
    out: list[str] = []
    for command, number in TOKEN_RE.findall(path_data):
        out.append(command or number)
    return out


def _is_command(token: str) -> bool:
    return len(token) == 1 and token.isalpha()


def _cubic(p0, p1, p2, p3, t: float) -> tuple[float, float]:
    mt = 1.0 - t
    x = (
        mt * mt * mt * p0[0]
        + 3.0 * mt * mt * t * p1[0]
        + 3.0 * mt * t * t * p2[0]
        + t * t * t * p3[0]
    )
    y = (
        mt * mt * mt * p0[1]
        + 3.0 * mt * mt * t * p1[1]
        + 3.0 * mt * t * t * p2[1]
        + t * t * t * p3[1]
    )
    return x, y


def flatten_path(path_data: str, steps: int = 36) -> list[tuple[float, float]]:
    toks = _tokens(path_data)
    i = 0
    cmd = ""
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    points: list[tuple[float, float]] = []

    def read_float() -> float:
        nonlocal i
        value = float(toks[i])
        i += 1
        return value

    while i < len(toks):
        if _is_command(toks[i]):
            cmd = toks[i]
            i += 1

        if cmd in ("M", "m"):
            x, y = read_float(), read_float()
            if cmd == "m":
                x += cur[0]
                y += cur[1]
            cur = start = (x, y)
            points.append(cur)
            cmd = "L" if cmd == "M" else "l"
            continue

        if cmd in ("L", "l"):
            while i < len(toks) and not _is_command(toks[i]):
                x, y = read_float(), read_float()
                if cmd == "l":
                    x += cur[0]
                    y += cur[1]
                cur = (x, y)
                points.append(cur)
            continue

        if cmd in ("C", "c"):
            while i < len(toks) and not _is_command(toks[i]):
                p1 = (read_float(), read_float())
                p2 = (read_float(), read_float())
                p3 = (read_float(), read_float())
                if cmd == "c":
                    p1 = (p1[0] + cur[0], p1[1] + cur[1])
                    p2 = (p2[0] + cur[0], p2[1] + cur[1])
                    p3 = (p3[0] + cur[0], p3[1] + cur[1])
                for step in range(1, steps + 1):
                    points.append(_cubic(cur, p1, p2, p3, step / steps))
                cur = p3
            continue

        if cmd in ("Z", "z"):
            points.append(start)
            continue

        raise ValueError(f"Unsupported SVG path command: {cmd}")

    return points


def _scale_points(points: list[tuple[float, float]], width: int, height: int, scale: int):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    sx = (width * scale - 1) / (max_x - min_x)
    sy = (height * scale - 1) / (max_y - min_y)
    return [((x - min_x) * sx, (y - min_y) * sy) for x, y in points]


def raster_mask(svg_name: str, width: int, height: int, scale: int = 4) -> Image.Image:
    points = flatten_path(_path_from_svg(ASSET_DIR / svg_name))
    scaled = _scale_points(points, width, height, scale)
    mask = Image.new("L", (width * scale, height * scale), 0)
    ImageDraw.Draw(mask).polygon(scaled, fill=255)
    return mask.resize((width, height), Image.Resampling.LANCZOS)


def placed_mask(
    svg_name: str,
    canvas_size: int,
    x: float,
    y: float,
    width: float,
    height: float,
    scale: int = 4,
) -> Image.Image:
    factor = canvas_size / FIGMA_CONTROL_SIZE
    px = round(x * factor)
    py = round(y * factor)
    pw = round(width * factor)
    ph = round(height * factor)
    mask = Image.new("L", (canvas_size, canvas_size), 0)
    layer = Image.new("L", (canvas_size, canvas_size), 0)
    layer.paste(raster_mask(svg_name, pw, ph, scale), (px, py))
    mask = ImageChops.lighter(mask, layer)
    return mask


def color_from_mask(mask: Image.Image, color: tuple[int, int, int, int]) -> Image.Image:
    image = Image.new("RGBA", mask.size, color)
    alpha = mask.point(lambda value: (value * color[3]) // 255)
    image.putalpha(alpha)
    return image


def zero_transparent_rgb(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                pixels[x, y] = (0, 0, 0, 0)
    return image


def progress_wedge_mask(size: int, percent: int, start_deg: float = -95.0) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    if percent <= 0:
        return mask
    if percent >= 100:
        return Image.new("L", (size, size), 255)

    cx = cy = (size - 1) / 2.0
    limit = percent / 100.0
    pixels = mask.load()
    for y in range(size):
        for x in range(size):
            angle = math.degrees(math.atan2(y - cy, x - cx))
            progress = ((angle - start_deg) % 360.0) / 360.0
            if progress <= limit:
                pixels[x, y] = 255
    return mask


def write_progress_frames() -> None:
    progress_mask = placed_mask(
        "media_main_progress.svg",
        PROGRESS_SIZE,
        x=5.536,
        y=4.488,
        width=68.928,
        height=71.224,
        scale=4,
    )
    base_mask = placed_mask(
        "media_main_progress_base.svg",
        PROGRESS_SIZE,
        x=10.728,
        y=2.176,
        width=22.584,
        height=14.984,
        scale=4,
    )
    ring_mask = ImageChops.lighter(progress_mask, base_mask)
    dark = color_from_mask(ring_mask, COLOR_PROGRESS_DARK)
    bright_full = color_from_mask(ring_mask, COLOR_PROGRESS_LIGHT)

    for percent in range(0, 101, 10):
        frame = dark.copy()
        wedge = progress_wedge_mask(PROGRESS_SIZE, percent)
        bright_alpha = Image.composite(bright_full.getchannel("A"), Image.new("L", bright_full.size, 0), wedge)
        bright = bright_full.copy()
        bright.putalpha(Image.composite(bright_alpha, Image.new("L", bright_full.size, 0), ring_mask))
        frame.alpha_composite(bright)
        zero_transparent_rgb(frame).save(
            ASSET_DIR / f"media_main_progress_{percent:03d}.png",
            optimize=True,
        )


def write_button_shapes() -> None:
    scallop_mask = raster_mask("media_main_shape.svg", *SCALLOP_SIZE, scale=4)
    scallop = Image.new("RGBA", (SHAPE_CANVAS, SHAPE_CANVAS), (0, 0, 0, 0))
    scallop.alpha_composite(
        color_from_mask(scallop_mask, COLOR_SHAPE),
        ((SHAPE_CANVAS - SCALLOP_SIZE[0]) // 2, (SHAPE_CANVAS - SCALLOP_SIZE[1]) // 2),
    )
    zero_transparent_rgb(scallop).save(ASSET_DIR / "media_main_shape_playing_267.png", optimize=True)

    paused = Image.new("RGBA", (SHAPE_CANVAS, SHAPE_CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(paused)
    radius = 94
    cx = cy = SHAPE_CANVAS // 2
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=COLOR_SHAPE)
    zero_transparent_rgb(paused).save(ASSET_DIR / "media_main_shape_paused_267.png", optimize=True)

    play = Image.new("RGBA", (107, 107), (0, 0, 0, 0))
    draw = ImageDraw.Draw(play)
    draw.polygon([(41, 30), (41, 77), (76, 53)], fill=COLOR_ICON)
    zero_transparent_rgb(play).save(ASSET_DIR / "media_icon_play_107.png", optimize=True)


def main() -> None:
    write_progress_frames()
    write_button_shapes()


if __name__ == "__main__":
    main()
