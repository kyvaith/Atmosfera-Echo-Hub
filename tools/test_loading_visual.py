"""Capture bounded loader and first-image states, checking API responsiveness."""

import argparse
import asyncio
from pathlib import Path

from aioesphomeapi import APIClient

from test_voice_assistant_ui import call_service, capture_screen, find_services


async def run(args):
    client = APIClient(args.host, 6053, None, client_info="M3 loader regression")
    await client.connect(login=True)
    try:
        services = await find_services(client)
        await call_service(client, services, "debug_close_app")
        await asyncio.sleep(2)
        await call_service(client, services, "debug_wake")
        await call_service(client, services, f"debug_open_{args.app}")
        await asyncio.sleep(1.2)
        await capture_screen(client, services, args.output / "loader.jpg")
        await asyncio.sleep(12)
        await client.device_info()
        await capture_screen(client, services, args.output / "first-image.jpg")
        await call_service(client, services, "debug_close_app")
        await asyncio.sleep(3)
        await client.device_info()
        print(f"PASS: {args.app} loader/first-image/close captured without API loss", flush=True)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--app", choices=("immich", "camera"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(run(parser.parse_args()))
