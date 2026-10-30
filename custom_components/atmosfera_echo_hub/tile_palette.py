"""Bounded preview colors matching MaterialTileSurface, independent of HA state."""

from __future__ import annotations
import re


def observed_accent(value: object) -> str | None:
    """Normalize the bounded device text value; configuration fallback is separate."""
    if type(value) is not str or len(value) not in (6, 7):
        return None
    text = value.removeprefix("#")
    return text.upper() if re.fullmatch(r"[0-9A-Fa-f]{6}", text) else None


def derive_tile_palette(accent: int) -> dict[str, tuple[int, int]]:
    """Use the native tile role offsets and contrast of each resulting surface."""
    if type(accent) is not int or not 0 <= accent <= 0xFFFFFF:
        raise ValueError("Expected one bounded RGB integer")
    r, g, b = (accent >> 16) & 255, (accent >> 8) & 255, accent & 255
    rgb = {
        "primary": (r, g, b),
        "secondary": (min(255, r + 28), min(255, g + 20), min(255, b + 10)),
        "tertiary": (min(255, r + 8), min(255, g + 38), min(255, b + 38)),
        "surface": (r // 5, g // 5, b // 5),
        "primary_container": (min(255, r + 58), min(255, g + 58), min(255, b + 58)),
    }
    return {
        name: (
            (red << 16) | (green << 8) | blue,
            0x071018 if red * 299 + green * 587 + blue * 114 > 150000 else 0xFFFFFF,
        )
        for name, (red, green, blue) in rgb.items()
    }
