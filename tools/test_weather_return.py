"""Capture the retained weather bridge across a real carousel gesture.

Atomic captures pause the presenter briefly, so this checks missing content,
not an unbiased animation FPS or physical touchscreen latency measurement.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from aioesphomeapi import APIClient
from PIL import Image

from test_voice_assistant_ui import call_service, capture_screen, find_services


async def run(args):
    client = APIClient(args.host, 6053, None, client_info="Weather return regression")
    await client.connect(login=True)
    services = await find_services(client)
    results = []
    try:
        async def call(name, **data):
            await call_service(client, services, name, data)

        async def swipe(start, end):
            await call("debug_navigation_touch", phase=0, x=start, y=400)
            for step in range(1, 17):
                x = round(start + (end - start) * step / 16)
                await call("debug_navigation_touch", phase=1, x=x, y=400)
                await asyncio.sleep(0.025)
            await call("debug_navigation_touch", phase=2, x=end, y=400)

        await call("debug_close_app")
        await asyncio.sleep(1)
        await call("debug_wake")
        await call("debug_navigation_home", page=1)
        await asyncio.sleep(7)
        for cycle in range(3):
            await swipe(700, 120)
            await asyncio.sleep(1)
            await swipe(120, 700)
            await asyncio.sleep(0.45)
            for frame in range(3):
                path = args.output / f"return-{cycle}-{frame}.jpg"
                await capture_screen(client, services, path)
                picture = Image.open(path).convert("RGB")
                visible = sum((b > 110 and g > 90 and r < 110) or min(r, g, b) > 180
                              for r, g, b in picture.crop((400, 65, 790, 455)).getdata())
                results.append({"capture": path.name, "weather_pixels": visible, "present": visible > 12000})
                await asyncio.sleep(0.1)
            await asyncio.sleep(6)
        (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(results, indent=2))
        if not all(item["present"] for item in results):
            raise SystemExit(1)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(run(parser.parse_args()))
