#!/usr/bin/env python3
"""Capture a low-memory, downsampled region from the presented DSI frame."""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
from pathlib import Path
from typing import Any

from aioesphomeapi import APIClient


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--x", type=int, default=0)
    parser.add_argument("--y", type=int, default=0)
    parser.add_argument("--width", type=int, default=800)
    parser.add_argument("--height", type=int, default=800)
    parser.add_argument("--scale", type=int, default=2)
    parser.add_argument(
        "--swap-red-blue",
        action="store_true",
        help="Swap framebuffer red and blue channels in the output image.",
    )
    return parser.parse_args()


def _response_data(response: Any) -> dict[str, Any]:
    for attribute in ("data", "response"):
        value = getattr(response, attribute, None)
        if isinstance(value, dict):
            return value
    raw = getattr(response, "response_data", None)
    if isinstance(raw, bytes):
        return json.loads(raw.decode("utf-8"))
    if isinstance(response, dict):
        return response
    raise RuntimeError(f"Unexpected ESPHome response type: {type(response)!r}")


async def _capture(args: argparse.Namespace) -> None:
    client = APIClient(args.host, 6053, None, client_info="Atmosfera region capture")
    await client.connect(login=True)
    try:
        _, services = await client.list_entities_services()
        service = next(
            (item for item in services if item.name == "debug_capture_region_raw"),
            None,
        )
        if service is None:
            raise RuntimeError("debug_capture_region_raw is unavailable")

        output = bytearray()
        total_size: int | None = None
        output_width = 0
        output_height = 0
        while total_size is None or len(output) < total_size:
            response = await client.execute_service(
                service,
                {
                    "x": args.x,
                    "y": args.y,
                    "width": args.width,
                    "height": args.height,
                    "scale": args.scale,
                    "offset": len(output),
                },
                return_response=True,
                timeout=30.0,
            )
            data = _response_data(response)
            if error := data.get("error"):
                raise RuntimeError(str(error))
            chunk = base64.b64decode(str(data.get("data_b64") or ""))
            if not chunk:
                raise RuntimeError(f"empty chunk at offset {len(output)}")
            output.extend(chunk)
            total_size = int(data["total_size"])
            output_width = int(data["width"])
            output_height = int(data["height"])

        if args.swap_red_blue:
            for offset in range(0, len(output), 3):
                output[offset], output[offset + 2] = output[offset + 2], output[offset]

        try:
            from PIL import Image
        except ImportError as err:
            raise RuntimeError("Pillow is required to save the capture") from err
        args.destination.parent.mkdir(parents=True, exist_ok=True)
        Image.frombytes("RGB", (output_width, output_height), bytes(output)).save(
            args.destination
        )
        print(
            f"Captured {output_width}x{output_height} RGB888 to {args.destination}"
        )
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(_capture(_arguments()))
