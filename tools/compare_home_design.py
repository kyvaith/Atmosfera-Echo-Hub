#!/usr/bin/env python3
"""Compare a device capture with a design aligned to its physical screen bounds."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance


def compare(reference: Path, capture: Path, bounds: tuple[int, int, int, int], output: Path) -> None:
    actual = Image.open(capture).convert("RGB")
    design = Image.open(reference).convert("RGB").crop(bounds).resize(actual.size, Image.Resampling.LANCZOS)
    mask = Image.new("L", actual.size)
    ImageDraw.Draw(mask).ellipse((0, 0, actual.width - 1, actual.height - 1), fill=255)
    outside = Image.new("RGB", actual.size, "white")
    design = Image.composite(design, outside, mask)
    actual = Image.composite(actual, outside, mask)
    overlay = Image.blend(design, actual, 0.5)
    difference = ImageEnhance.Contrast(ImageChops.difference(design, actual)).enhance(2)
    result = Image.new("RGB", (actual.width * 2, actual.height * 2), "white")
    for tile, position in zip(
        (design, actual, overlay, difference),
        ((0, 0), (actual.width, 0), (0, actual.height), (actual.width, actual.height)),
        strict=True,
    ):
        result.paste(tile, position)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--screen-bounds", type=int, nargs=4, required=True, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    compare(args.reference, args.capture, tuple(args.screen_bounds), args.output)
