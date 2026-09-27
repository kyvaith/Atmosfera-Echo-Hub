"""Exercise shared resources without reconnecting across application handoffs."""

import argparse
import asyncio
import json
from pathlib import Path

from aioesphomeapi import APIClient, MediaPlayerCommand, MediaPlayerInfo, MediaPlayerState
from PIL import Image

from test_voice_assistant_ui import call_service, capture_screen, find_services


def has_media(path):
    with Image.open(path) as source:
        image = source.convert("RGB")
        width, height = image.size
        pixels = [
            image.getpixel((x, y))
            for y in range(height // 4, height * 3 // 4, 8)
            for x in range(width // 4, width * 3 // 4, 8)
            if abs(x - width // 2) > width // 8 or abs(y - height // 2) > height // 8
        ]
        return sum(max(pixel) > 24 for pixel in pixels) / len(pixels) > 0.25


async def run(args):
    args.output.mkdir(parents=True, exist_ok=True)
    client = APIClient(args.host, 6053, None, client_info="Mixed app lifecycle")
    results = []
    await client.connect(login=True)
    try:
        services = await find_services(client)
        entities, _ = await client.list_entities_services()
        player = next((entity for entity in entities if isinstance(entity, MediaPlayerInfo)
                       and entity.name == "Sendspin Group"), None)
        states = {}
        client.subscribe_states(lambda state: states.update({state.key: state}))
        if args.start_music and player is None:
            raise AssertionError("Sendspin Group is unavailable")
        for cycle in range(args.cycles):
            await call_service(client, services, "debug_close_app")
            await asyncio.sleep(2)
            await call_service(client, services, "debug_navigation_home", {"page": (1, 4, 2)[cycle % 3]})
            await asyncio.sleep(2)
            for app in ("voice", "settings", "player", "camera", "immich"):
                name = f"{cycle + 1}-{app}"
                await call_service(client, services, "debug_close_app")
                await asyncio.sleep(2)
                await call_service(client, services, "debug_wake")
                await call_service(client, services, f"debug_open_{app}")
                await asyncio.sleep(18 if app in ("camera", "immich") else 4)
                if args.start_music and app == "player":
                    client.media_player_command(player.key, command=MediaPlayerCommand.PLAY)
                    await asyncio.sleep(15)
                    state = states.get(player.key)
                    if state is None or state.state != MediaPlayerState.PLAYING:
                        raise AssertionError(f"{name}: Music Assistant did not start playback: {state}")
                    await call_service(client, services, "debug_player_state")
                    await capture_screen(client, services, args.output / f"{name}.jpg")
                await client.device_info()
                await call_service(client, services, "debug_log_memory", {"phase": name})
                if app in ("camera", "immich"):
                    path = args.output / f"{name}.jpg"
                    await capture_screen(client, services, path)
                    if not has_media(path):
                        raise AssertionError(f"{name}: no media outside loader region")
                await call_service(client, services, "debug_close_app")
                await asyncio.sleep(3)
                await client.device_info()
                results.append({"case": name, "passed": True})
                print(f"PASS {name}", flush=True)
    finally:
        (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--start-music", action="store_true", help="Resume the configured queue on each Player visit")
    parser.add_argument("--output", type=Path, required=True)
    asyncio.run(run(parser.parse_args()))
