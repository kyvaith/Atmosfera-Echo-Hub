"""Exercise repeated microphone/assistant lifecycles without hiding API resets."""

import argparse
import asyncio
from pathlib import Path

from aioesphomeapi import APIClient

from test_voice_assistant_ui import call_service, capture_screen, find_services


async def run(args):
    await asyncio.sleep(args.initial_wait)
    client = APIClient(args.host, 6053, None, client_info="Voice reopen regression")
    await client.connect(login=True)
    try:
        services = await find_services(client)
        await call_service(client, services, "debug_close_app")
        await asyncio.sleep(2)
        await call_service(client, services, "debug_navigation_home", {"page": args.page})
        await asyncio.sleep(2)
        for index in range(args.iterations):
            await call_service(client, services, args.open_service)
            await asyncio.sleep(4)
            # Unlike fire-and-forget debug actions, this request fails if the
            # device reset or stopped servicing the native API.
            await client.device_info()
            if index == args.iterations - 1:
                await capture_screen(client, services, args.output / "last-open.jpg")
            await call_service(client, services, "debug_close_app")
            await asyncio.sleep(2)
            await client.device_info()
            print(f"PASS: {args.open_service} open/close {index + 1}/{args.iterations}", flush=True)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--open-service", default="debug_open_voice")
    parser.add_argument("--initial-wait", type=float, default=0)
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(run(parser.parse_args()))
