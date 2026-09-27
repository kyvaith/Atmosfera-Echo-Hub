#!/usr/bin/env python3
"""Exercise Home visibility epochs and capture atomic device frames for visual QA."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import aioesphomeapi

from test_voice_assistant_ui import call_service, capture_screen, find_services


async def run(host: str, output: Path) -> None:
    client = aioesphomeapi.APIClient(host, 6053, None, client_info="Atmosfera Home visual QA")
    await client.connect(login=True)
    try:
        services = await find_services(client)

        async def call(name: str, **kwargs) -> None:
            await call_service(client, services, name, kwargs)

        async def capture(name: str) -> None:
            await capture_screen(client, services, output / f"{name}.jpg")
            print(f"Captured {name}", flush=True)

        await call("debug_wake")
        await call("debug_navigation_home", page=2)
        await asyncio.sleep(1)
        await call("debug_navigation_home", page=1)
        await asyncio.sleep(1.2)
        await capture("weather-early")
        await asyncio.sleep(1.4)
        await capture("weather-middle")
        await asyncio.sleep(6)
        await capture("home-retained")

        for page in (2, 3, 4):
            await call("debug_navigation_home", page=page)
            await asyncio.sleep(1.2)
            await capture(f"home-{page}")

        await call("debug_navigation_home", page=1)
        await asyncio.sleep(0.8)
        await call("debug_volume_overlay")
        await asyncio.sleep(0.15)
        await capture("volume-over-weather")
        await asyncio.sleep(7)
        await capture("home-after-volume")

        for app in ("player", "settings"):
            await call(f"debug_open_{app}")
            await asyncio.sleep(0.15)
            await call("debug_snapshot_app_state", phase=f"m3-{app}-opening")
            await asyncio.sleep(1.5)
            await capture(app)
            await call("debug_close_app")
            await asyncio.sleep(0.15)
            await call("debug_snapshot_app_state", phase=f"m3-{app}-closing")
            await asyncio.sleep(7)
            await capture(f"home-after-{app}")

        await call("debug_log_memory", phase="m3-home-qa-complete")
        print("Sequence complete; inspect the JPEGs and the COM log. This is not automatic visual approval.")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    asyncio.run(run(args.host, args.output))
