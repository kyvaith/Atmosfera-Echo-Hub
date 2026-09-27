"""Capture and check fixed Home chrome through real navigation handoffs.

Run after a fresh boot. Small, settled framebuffer regions are intentional:
the low-memory raw capture endpoint is not atomic for moving animations.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from PIL import Image

from call_esphome_service import call_service
from capture_display_region import _capture


async def run(args: argparse.Namespace) -> None:
    results: list[dict[str, object]] = []

    async def service(name: str, data: dict | None = None, wait: float = 1.2) -> None:
        await call_service(args.host, 6053, name, data or {})
        await asyncio.sleep(wait)

    async def capture(name: str, y: int = 0, height: int = 75) -> Image.Image:
        path = args.output / f"{name}.png"
        await _capture(argparse.Namespace(
            destination=path, host=args.host, x=330, y=y,
            width=140, height=height, scale=1, swap_red_blue=True,
        ))
        return Image.open(path).convert("RGB")

    async def check_status(name: str, expected: bool = True) -> None:
        image = await capture(name)
        counts = []
        for bounds in ((0, 0, 70, 75), (70, 0, 140, 75)):
            counts.append(sum(min(pixel) > 190 for pixel in image.crop(bounds).getdata()))
        passed = all(count > 40 for count in counts) if expected else all(count < 10 for count in counts)
        results.append({"case": name, "white_pixels": counts, "expected": expected, "passed": passed})

    await service("debug_wake")
    for page in range(1, 5):
        await service("debug_navigation_home", {"page": page})
        await check_status(f"home-{page}")

    for app in ("player", "settings"):
        await service("debug_navigation_home", {"page": 3})
        await service(f"debug_open_{app}", wait=2.5)
        await check_status(app)
        await service("debug_close_app", wait=2.5)
        await check_status(f"home-3-after-{app}")
        image = await capture(f"home-3-after-{app}-mic", y=688, height=12)
        # At this location page three is blank; the page-one mic has a gray
        # disc and a blue glyph. Avoid its upper edge, where a page tile ends.
        nonblack = sum(max(pixel) > 50 for pixel in image.getdata())
        results.append({"case": f"no-mic-after-{app}", "nonblack_pixels": nonblack,
                        "passed": nonblack < 30})
        await capture(f"home-3-after-{app}-dots", y=730, height=25)

    await service("debug_navigation_home", {"page": 1})
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2), flush=True)
    if not all(result["passed"] for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(run(parser.parse_args()))
