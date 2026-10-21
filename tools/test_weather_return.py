"""Capture the retained weather bridge across a real carousel gesture.

Atomic captures pause the presenter briefly, so this checks missing content,
not an unbiased animation FPS or physical touchscreen latency measurement.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from pathlib import Path

from aioesphomeapi import APIClient
from PIL import Image

from test_voice_assistant_ui import call_service, capture_screen, find_services


async def run(args):
    client = APIClient(args.host, 6053, None, client_info="Weather return regression")
    await client.connect(login=True)
    services = await find_services(client)
    results = []
    logs = []
    unsubscribe = client.subscribe_logs(
        lambda message: logs.append(message.message.decode("utf-8", "replace")),
        log_level=5,
        dump_config=False,
    )
    try:
        async def call(name, **data):
            await call_service(client, services, name, data)

        async def swipe(start, end, *, hold=False):
            await call("debug_navigation_touch", phase=0, x=start, y=400)
            for step in range(1, 17):
                x = round(start + (end - start) * step / 16)
                await call("debug_navigation_touch", phase=1, x=x, y=400)
                await asyncio.sleep(0.025)
            if not hold:
                await call("debug_navigation_touch", phase=2, x=end, y=400)

        def weather_pixels(path, offset=0):
            picture = Image.open(path).convert("RGB")
            # Artwork starts to the right of the clock. Count all bright
            # colors so a pastel or user-selected accent remains testable.
            # The source snapshot ends at x=800 even when the widget extends
            # past that edge; move that same visible rectangle with the drag.
            crop = picture.crop((444 + offset, 68, 800 + offset, 452))
            return sum(max(rgb) > 100 for rgb in crop.getdata())

        await call("debug_close_app")
        await asyncio.sleep(1)
        await call("debug_wake")
        await call("debug_navigation_home", page=1)
        await asyncio.sleep(7)
        baseline_path = args.output / "baseline.jpg"
        await capture_screen(client, services, baseline_path)
        baseline_pixels = weather_pixels(baseline_path)
        if baseline_pixels < 1000:
            raise AssertionError(f"Weather absent from baseline: {baseline_pixels} bright pixels")
        for cycle in range(3):
            await swipe(700, 520, hold=True)
            await asyncio.sleep(0.2)
            path = args.output / f"outgoing-held-{cycle}.jpg"
            phase = f"weather-return-held-{cycle}"
            log_start = len(logs)
            await call("debug_direct_buffer_state", phase=phase)
            await asyncio.sleep(0.1)
            states = re.findall(rf"{re.escape(phase)} .*?swipe=(\d+)", "\n".join(logs[log_start:]))
            moving_snapshot = bool(states and states[-1] == "1")
            await capture_screen(client, services, path)
            visible = weather_pixels(path, -180)
            # The shifted crop overlaps the stationary clock if the gesture
            # failed to start. Require the moving compositor as well as pixels.
            results.append({"capture": path.name, "scenario": "outgoing-held", "weather_pixels": visible,
                            "baseline_pixels": baseline_pixels, "moving_snapshot": moving_snapshot,
                            "present": moving_snapshot and visible > baseline_pixels * 0.65})
            await call("debug_navigation_touch", phase=1, x=120, y=400)
            await call("debug_navigation_touch", phase=2, x=120, y=400)
            await asyncio.sleep(1)
            await swipe(120, 700)
            await asyncio.sleep(0.45)
            for frame in range(3):
                path = args.output / f"return-{cycle}-{frame}.jpg"
                await capture_screen(client, services, path)
                visible = weather_pixels(path)
                results.append({"capture": path.name, "scenario": "return", "weather_pixels": visible,
                                "present": visible > 1000})
                await asyncio.sleep(0.1)
            await asyncio.sleep(6)
        print(json.dumps(results, indent=2))
        if not all(item["present"] for item in results):
            raise SystemExit(1)
    finally:
        (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        (args.output / "device.log").write_text("\n".join(logs) + "\n", encoding="utf-8")
        unsubscribe()
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    arguments.output.mkdir(parents=True, exist_ok=True)
    asyncio.run(run(arguments))
