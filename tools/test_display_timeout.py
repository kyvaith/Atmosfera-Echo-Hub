"""Verify Home inactivity while weather runs, restoring the user's timeout."""

import argparse
import asyncio

from aioesphomeapi import APIClient

from test_voice_assistant_ui import call_service, find_services


async def run(args):
    client = APIClient(args.host, 6053, None, client_info="Display timeout regression")
    await client.connect(login=True)
    original = None
    try:
        entities, _ = await client.list_entities_services()
        keys = {entity.object_id: entity.key for entity in entities}
        states = {}
        client.subscribe_states(lambda state: states.__setitem__(state.key, state))
        await asyncio.sleep(1)
        timeout_key = keys["display_timeout"]
        light_key = keys["display_backlight"]
        original = states[timeout_key].state
        services = await find_services(client)
        await call_service(client, services, "debug_close_app")
        await asyncio.sleep(1)
        await call_service(client, services, "debug_navigation_home", {"page": 1})
        client.number_command(timeout_key, 30)
        await call_service(client, services, "debug_wake")
        await asyncio.sleep(2)
        assert states[light_key].state, "Home did not wake"
        await asyncio.sleep(35)
        assert not states[light_key].state, "Weather/redraw kept Home awake past its timeout"
        print("PASS: Home blanked after 30s despite weather animation")
        await asyncio.sleep(50)
        print("Background snapshot refresh observation window complete")
        await call_service(client, services, "debug_wake")
        await asyncio.sleep(2)
        assert states[light_key].state, "Home did not wake again"
    finally:
        if original is not None:
            client.number_command(timeout_key, original)
            await asyncio.sleep(0.2)
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    asyncio.run(run(parser.parse_args()))
