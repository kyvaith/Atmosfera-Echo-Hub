"""Check weather accent after finite playback and after a scene reload.

This hardware regression checks captured colors, not animation FPS. The cloud
variant keeps a neutral cloud and an accent crescent, so the clock cannot make
the artwork-only color check pass accidentally.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from aioesphomeapi import APIClient, TextInfo
from PIL import Image

from test_voice_assistant_ui import call_service, capture_screen, find_services


async def run(args):
    args.output.mkdir(parents=True, exist_ok=True)
    client = APIClient(args.host, 6053, None, client_info="Weather theme regression")
    await client.connect(login=True)
    services = await find_services(client)
    entities, _ = await client.list_entities_services()
    accent = next(entity for entity in entities
                  if isinstance(entity, TextInfo) and entity.name == "Interface Accent Color")
    results = []

    async def call(name, **data):
        await call_service(client, services, name, data)

    async def capture(name, color):
        path = args.output / f"{name}.jpg"
        await capture_screen(client, services, path)
        expected = tuple(int(color[index:index + 2], 16) for index in (0, 2, 4))
        pixels = Image.open(path).convert("RGB").crop((444, 68, 800, 452))
        matches = sum(sum(abs(pixel[channel] - expected[channel]) for channel in range(3)) < 60
                      for pixel in pixels.getdata())
        item = {"capture": path.name, "accent": color, "matching_artwork_pixels": matches,
                "passed": matches > 150}
        results.append(item)
        print(json.dumps(item), flush=True)
        if not item["passed"]:
            raise AssertionError(f"Weather accent missing or stale in {path}")

    try:
        await call("debug_close_app")
        await asyncio.sleep(2)
        await call("debug_wake")
        await call("debug_navigation_home", page=1)
        await call("debug_weather_variant", condition="cloudy", is_day=False)
        client.text_command(accent.key, "FFDB98", accent.device_id)
        await asyncio.sleep(10)
        await capture("completed-cream", "FFDB98")

        # The one-shot has finished. A color change must repaint its retained
        # canvas without requiring another page visit or animation restart.
        client.text_command(accent.key, "D7ACD4", accent.device_id)
        await asyncio.sleep(5)
        await capture("completed-lavender", "D7ACD4")

        # Settings discards the parsed weather scene. Reopening Home must
        # reapply the retained RGB to the newly loaded scene.
        await call("debug_open_settings")
        await asyncio.sleep(3)
        await call("debug_close_app")
        await asyncio.sleep(10)
        await capture("reloaded-lavender", "D7ACD4")
    finally:
        client.text_command(accent.key, args.restore, accent.device_id)
        await call("debug_weather_state")
        (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--restore", default="AEE2FF", help="Accent to restore after the test, as six hex digits")
    asyncio.run(run(parser.parse_args()))
