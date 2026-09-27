#!/usr/bin/env python3
"""Call an ESPHome native API user service for repeatable device diagnostics."""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any

from aioesphomeapi import APIClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("service", help="ESPHome user service name")
    parser.add_argument("--host", default="atmosfera-echo-hub.local")
    parser.add_argument("--port", type=int, default=6053)
    parser.add_argument("--data", default="{}", help="JSON object with service arguments")
    parser.add_argument(
        "--arg",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="Service argument; booleans and integers are converted automatically",
    )
    return parser.parse_args()


def parse_value(value: str) -> Any:
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value


async def call_service(host: str, port: int, name: str, data: dict[str, Any]) -> None:
    client = APIClient(host, port, None, client_info="Atmosfera diagnostics")
    await client.connect(login=True)
    try:
        _, services = await client.list_entities_services()
        service = next((item for item in services if item.name == name), None)
        if service is None:
            available = ", ".join(sorted(item.name for item in services))
            raise RuntimeError(f"ESPHome service {name!r} was not found. Available: {available}")
        await client.execute_service(service, data)
        print(f"Called {name} on {host}:{port}")
    finally:
        await client.disconnect()


def main() -> None:
    args = parse_args()
    data = json.loads(args.data)
    if not isinstance(data, dict):
        raise ValueError("--data must contain a JSON object")
    for argument in args.arg:
        name, separator, value = argument.partition("=")
        if not separator or not name:
            raise ValueError(f"Invalid --arg value: {argument!r}")
        data[name] = parse_value(value)
    asyncio.run(call_service(args.host, args.port, args.service, data))


if __name__ == "__main__":
    main()
