"""Run a bounded native-API UI scenario while recording device logs."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from aioesphomeapi import APIClient


async def run(args: argparse.Namespace) -> None:
    client = APIClient(args.host, 6053, None, client_info="Atmosfera UI probe")
    await client.connect(login=True)
    try:
        _, services = await client.list_entities_services()
        available = {service.name: service for service in services}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as output:
            def log(message) -> None:
                line = message.message.decode("utf-8", errors="replace")
                output.write(line + "\n")
                output.flush()
                print(line, flush=True)

            unsubscribe = client.subscribe_logs(log, log_level=5, dump_config=False)
            try:
                for step in json.loads(args.steps):
                    name = step["service"]
                    marker = f"PROBE: {name} {step.get('data', {})}"
                    print(marker, flush=True)
                    output.write(marker + "\n")
                    await client.execute_service(available[name], step.get("data", {}))
                    await asyncio.sleep(step.get("wait", 2))
            finally:
                unsubscribe()
    finally:
        await client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--steps", required=True, help="JSON list of service/data/wait objects")
    asyncio.run(run(parser.parse_args()))
