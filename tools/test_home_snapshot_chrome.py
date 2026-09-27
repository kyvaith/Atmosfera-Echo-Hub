"""Check fixed chrome and the frozen weather source during a held Home drag."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from aioesphomeapi import APIClient
from PIL import Image

from test_voice_assistant_ui import call_service, capture_screen, find_services


async def run(args: argparse.Namespace) -> None:
    client = APIClient(args.host, 6053, None, client_info="Home snapshot regression")
    await client.connect(login=True)
    services = await find_services(client)
    held = False
    try:
        async def call(name: str, **data) -> None:
            await call_service(client, services, name, data)

        await call("debug_wake")
        await call("debug_navigation_home", page=1)
        await asyncio.sleep(1)
        live_path = args.output / "live.jpg"
        await capture_screen(client, services, live_path)
        live = Image.open(live_path).convert("RGB")
        await call("debug_navigation_touch", phase=0, x=650, y=400)
        held = True
        for x in (600, 550, 500, 450, 400, 350):
            await call("debug_navigation_touch", phase=1, x=x, y=400)
            await asyncio.sleep(0.07)
        await asyncio.sleep(0.1)
        path = args.output / "held-drag.jpg"
        await capture_screen(client, services, path)
        image = Image.open(path).convert("RGB")

        def count(bounds, predicate) -> int:
            pixels = image.crop(bounds)
            return sum(predicate(pixels.getpixel((x, y)))
                       for y in range(pixels.height) for x in range(pixels.width))

        white = lambda pixel: min(pixel) > 180
        blue = lambda pixel: pixel[2] > 120 and pixel[1] > 90 and pixel[0] < 100

        def glyph_bounds(source, bounds):
            points = [(x, y) for y in range(bounds[1], bounds[3])
                      for x in range(bounds[0], bounds[2])
                      if min(source.getpixel((x, y))) > 200]
            return (min(x for x, y in points), min(y for x, y in points),
                    max(x for x, y in points), max(y for x, y in points)) if points else None

        checks = {
            "fixed_speaker": count((330, 0, 400, 75), white) > 80,
            "fixed_wifi": count((400, 0, 470, 75), white) > 80,
            "no_moving_status_copy": count((0, 0, 250, 60), white) < 20,
            "fixed_indicators": count((330, 730, 470, 755), white) > 80,
            "no_moving_indicator_copy": count((0, 730, 250, 755), white) < 20,
            # Covers the translated weather region, not only the sunny disk.
            # Live HA may select a cloud, rain, or snow asset instead.
            "frozen_weather_visible": count((100, 70, 490, 455),
                                            lambda pixel: blue(pixel) or white(pixel)) > 12000,
            "mic_moves_with_page": count((70, 615, 130, 690), blue) > 80,
            "speaker_geometry_matches_live": glyph_bounds(live, (330, 0, 400, 70)) ==
                glyph_bounds(image, (330, 0, 400, 70)),
            "wifi_geometry_matches_live": glyph_bounds(live, (400, 0, 470, 70)) ==
                glyph_bounds(image, (400, 0, 470, 70)),
        }
        (args.output / "results.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(checks, indent=2), flush=True)
        if not all(checks.values()):
            raise SystemExit(1)
    finally:
        if held:
            await call_service(client, services, "debug_navigation_touch", {"phase": 2, "x": 350, "y": 400})
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(run(parser.parse_args()))
