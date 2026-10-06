#!/usr/bin/env python3
"""Set the on-device language and accent entities through the ESPHome API.

This is a QA helper for the Atmosfera firmware.  It deliberately addresses
entities by their stable names or object IDs instead of depending on generated
entity keys, which can change when the YAML is regenerated.
"""

from __future__ import annotations

import argparse
import asyncio

from aioesphomeapi import APIClient, SelectInfo, TextInfo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--port", type=int, default=6053)
    parser.add_argument("--password", default=None)
    parser.add_argument("--language", choices=("en-US", "pl-PL"))
    parser.add_argument(
        "--accent",
        help="Six-digit RGB hex value, with or without a leading '#'.",
    )
    args = parser.parse_args()
    if args.language is None and args.accent is None:
        parser.error("provide --language and/or --accent")
    if args.accent is not None:
        accent = args.accent.removeprefix("#")
        if len(accent) != 6:
            parser.error("--accent must contain exactly six hexadecimal digits")
        try:
            int(accent, 16)
        except ValueError:
            parser.error("--accent must contain only hexadecimal digits")
        args.accent = accent.upper()
    return args


async def run(args: argparse.Namespace) -> None:
    client = APIClient(
        args.host,
        args.port,
        args.password,
        client_info="Atmosfera UI preference QA",
    )
    await client.connect(login=True)
    try:
        entities, _ = await client.list_entities_services()
        def find_entity(entity_type: type, name: str, *object_ids: str):
            for entity in entities:
                if isinstance(entity, entity_type) and (
                    entity.name == name or entity.object_id in object_ids
                ):
                    return entity
            available = ", ".join(
                f"{entity.object_id} ({entity.name})"
                for entity in entities
                if isinstance(entity, entity_type)
            )
            raise RuntimeError(f"entity {name!r} was not found; available: {available}")

        if args.language is not None:
            language = find_entity(
                SelectInfo, "Interface Language", "interface_language", "settings_ui_language"
            )
            options = getattr(language, "options", ())
            if options and args.language not in options:
                raise RuntimeError(
                    f"language {args.language!r} is not advertised; options={options!r}"
                )
            client.select_command(language.key, args.language, language.device_id)
            print(f"Set language {args.language} (key={language.key})", flush=True)

        if args.accent is not None:
            accent = find_entity(
                TextInfo,
                "Interface Accent Color",
                "interface_accent_color",
                "settings_accent_color",
            )
            client.text_command(accent.key, args.accent, accent.device_id)
            print(f"Set accent #{args.accent} (key={accent.key})", flush=True)
        # Entity commands are sent synchronously by APIClient.  A short pause
        # gives the device time to persist the value and redraw its snapshot.
        await asyncio.sleep(1.0)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(run(parse_args()))
