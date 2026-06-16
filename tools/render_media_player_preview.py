from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import math


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "images" / "figma"
OUT = ROOT / ".tmp_media_player_preview.png"

SCREEN = 800
TEXT = (0xF5, 0xEE, 0xFB, 255)
BUTTON_TINT = (0xF5, 0xEE, 0xFB, int(255 * 0.16))


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts") / name,
        Path("C:/Windows/Fonts/Roboto-Regular.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size)


ROBOTO = "Roboto-Regular.ttf"
ROBOTO_BOLD = "Roboto-Bold.ttf"


def open_rgba(name: str) -> Image.Image:
    return Image.open(ASSET_DIR / name).convert("RGBA")


def paste_center(base: Image.Image, layer: Image.Image, cx: int, cy: int) -> None:
    x = int(round(cx - layer.width / 2))
    y = int(round(cy - layer.height / 2))
    base.alpha_composite(layer, (x, y))


def rounded_button(width: int = 147, height: int = 107, radius: int = 53) -> Image.Image:
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ImageDraw.Draw(image).rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=BUTTON_TINT)
    return image


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill=TEXT,
) -> None:
    box = draw.textbbox((0, 0), text, font=fnt)
    w = box[2] - box[0]
    h = box[3] - box[1]
    draw.text((xy[0] - w / 2, xy[1] - h / 2 - box[1]), text, font=fnt, fill=fill)


def draw_left_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.FreeTypeFont,
    fill=TEXT,
) -> None:
    draw.text(xy, text, font=fnt, fill=fill)


def draw_wavy_arc(draw: ImageDraw.ImageDraw, bbox: tuple[int, int, int, int], progress: int) -> None:
    cx = (bbox[0] + bbox[2]) / 2
    cy = (bbox[1] + bbox[3]) / 2
    radius = (bbox[2] - bbox[0]) / 2 - 17

    def points(value_pct: float) -> list[tuple[float, float]]:
        span = 359 * max(0, min(100, value_pct)) / 100
        out = []
        for i in range(112):
            t = i / 111
            angle = math.radians(-90 + span * t)
            wave = math.sin(2 * math.pi * 9 * t)
            r = radius + 5 * wave
            out.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
        return out

    draw.line(points(100), fill=(0x25, 0x18, 0x2F, 255), width=11, joint="curve")
    if progress > 0:
        draw.line(points(progress), fill=(0xED, 0xD9, 0xF9, 255), width=11, joint="curve")


def render(progress: int, playing: bool, title: str, artist: str) -> Image.Image:
    frame = open_rgba("media_artwork_figma_composed_800.png")
    draw = ImageDraw.Draw(frame)

    draw_centered_text(draw, (400, 36), "9:30", font(ROBOTO, 40))
    draw.ellipse((207, 92, 260, 145), fill=(0xEA, 0xDD, 0xFF, 255))
    draw_centered_text(draw, (233, 119), "⚡", font("segoeui.ttf", 30), fill=(0x21, 0x00, 0x5D, 255))
    draw_left_text(draw, (280, 78), title, font(ROBOTO_BOLD, 53))
    draw_centered_text(draw, (400, 172), artist, font(ROBOTO, 47))

    for cx, icon in [(147, "|◀"), (653, "▶|")]:
        draw.rounded_rectangle((cx - 80, 295, cx + 80, 505), radius=80, fill=(0xD9, 0xC2, 0xFF, 255))
        draw_centered_text(draw, (cx, 400), icon, font(ROBOTO_BOLD, 54), fill=(0x3F, 0x00, 0x6B, 255))

    draw_wavy_arc(draw, (267, 267, 533, 533), progress)
    draw.ellipse((304, 304, 496, 496), fill=(0xE4, 0xC2, 0xFF, 255))
    draw_centered_text(draw, (400, 398), "Ⅱ" if playing else "▶", font(ROBOTO_BOLD, 84), fill=(0x40, 0x00, 0x60, 255))

    for cx, cy, icon in [
        (182, 613, "≡♪"),
        (400, 693, "🔊"),
        (618, 613, "⋮"),
    ]:
        button = rounded_button()
        paste_center(frame, button, cx, cy)
        draw_centered_text(draw, (cx, cy), icon, font("segoeui.ttf", 54), fill=TEXT)

    dot = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    ImageDraw.Draw(dot).ellipse((0, 0, 19, 19), fill=TEXT)
    paste_center(frame, dot, 383, 783)
    dim_dot = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    ImageDraw.Draw(dim_dot).ellipse((0, 0, 19, 19), fill=(0x8E, 0x91, 0x8F, 255))
    paste_center(frame, dim_dot, 417, 783)
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--progress", type=int, default=42)
    parser.add_argument("--paused", action="store_true")
    parser.add_argument("--title", default="Song Name")
    parser.add_argument("--artist", default="Artist name")
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    render(args.progress, not args.paused, args.title, args.artist).save(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
