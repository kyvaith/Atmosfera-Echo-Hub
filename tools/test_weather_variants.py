"""Measure every weather scene on hardware, without captures during FPS windows.

Snapshots are taken after playback, not while measuring. API gestures do not
measure the physical GT911 input latency. Restore live HA weather in finally.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import re

from aioesphomeapi import APIClient

from test_voice_assistant_ui import call_service, capture_screen, find_services

VARIANTS = (
    ("clear-day", "sunny", True),
    ("clear-night", "clear-night", False),
    ("partly-cloudy-day", "partlycloudy", True),
    ("partly-cloudy-night", "partlycloudy", False),
    ("overcast", "cloudy", True),
    ("rain", "rainy", True),
    ("snow", "snowy", True),
    ("thunderstorms", "lightning", True),
    ("fog", "fog", True),
)
PERF = re.compile(r"perf2s:.*?elapsed_ms=(\d+).*?frames=(\d+).*?raster_avg=(\d+)us")
CACHE = re.compile(r"cache2s:.*?frames=(\d+).*?direct=(\d+).*?avg=(\d+)us")


async def run(args):
    args.output.mkdir(parents=True, exist_ok=True)
    client = APIClient(args.host, 6053, None, client_info="Weather variants benchmark")
    await client.connect(login=True)
    services = await find_services(client)
    results = []
    samples = []
    measuring = False
    log_file = (args.output / "device.log").open("w", encoding="utf-8")

    def on_log(message):
        line = message.message.decode("utf-8", errors="replace")
        log_file.write(line + "\n")
        log_file.flush()
        if measuring:
            if match := PERF.search(line):
                elapsed, frames, raster_us = map(int, match.groups())
                samples.append({"source": "perf2s", "frames": frames, "elapsed_ms": elapsed,
                                "fps": frames * 1000 / elapsed, "raster_us": raster_us})
            elif match := CACHE.search(line):
                frames, direct, avg_us = map(int, match.groups())
                samples.append({"source": "cache2s", "frames": frames, "elapsed_ms": 2000,
                                "fps": frames / 2, "direct": direct, "raster_us": avg_us})

    unsubscribe = client.subscribe_logs(on_log, log_level=5, dump_config=False)

    async def call(name, **data):
        await call_service(client, services, name, data)

    try:
        await asyncio.sleep(2)
        await call("debug_close_app")
        await asyncio.sleep(2)
        await call("debug_navigation_home", page=1)
        await asyncio.sleep(2)
        for cycle in range(args.cycles):
            for name, condition, is_day in VARIANTS:
                if args.variant and name not in args.variant:
                    continue
                if cycle:
                    await call("debug_open_settings")
                    await asyncio.sleep(2)
                    await call("debug_close_app")
                    await asyncio.sleep(2)
                await call("debug_wake")
                samples.clear()
                measuring = True
                await call("debug_weather_variant", condition=condition, is_day=is_day)
                await asyncio.sleep(8)
                measuring = False
                item = {"variant": name, "cycle": cycle, "samples": list(samples)}
                item["fps"] = (sum(s["frames"] for s in samples) * 1000 /
                               sum(s["elapsed_ms"] for s in samples)) if samples else 0
                results.append(item)
                print(json.dumps(item), flush=True)
                if not args.no_capture:
                    await capture_screen(client, services, args.output / f"{cycle}-{name}.jpg")
                await call("debug_log_memory", phase=f"weather-{name}-{cycle}")
                await asyncio.sleep(1)
    finally:
        measuring = False
        await call("debug_weather_state")
        await asyncio.sleep(1)
        unsubscribe()
        log_file.close()
        await client.disconnect()
        (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    if not results or any(item["fps"] < args.min_fps for item in results):
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cycles", type=int, default=2)
    parser.add_argument("--variant", action="append")
    parser.add_argument("--no-capture", action="store_true",
                        help="Do not capture the framebuffer between variants")
    parser.add_argument("--min-fps", type=float, default=30)
    asyncio.run(run(parser.parse_args()))
