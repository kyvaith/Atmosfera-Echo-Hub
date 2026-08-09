#!/usr/bin/env python3
"""Exercise and capture the on-device voice assistant UI over ESPHome API."""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import math
from pathlib import Path
import time
from typing import Any

import aioesphomeapi


async def find_services(client: aioesphomeapi.APIClient) -> dict[str, Any]:
    _, services = await client.list_entities_services()
    return {service.name: service for service in services}


async def set_switch(
    client: aioesphomeapi.APIClient,
    object_id: str,
    state: bool,
) -> None:
    entities, _ = await client.list_entities_services()
    for entity in entities:
        if getattr(entity, "object_id", "") == object_id:
            client.switch_command(entity.key, state)
            return
    raise RuntimeError(f"ESPHome switch {object_id!r} is unavailable")


async def call_service(
    client: aioesphomeapi.APIClient,
    services: dict[str, Any],
    name: str,
    data: dict[str, Any] | None = None,
    *,
    response: bool = False,
) -> Any:
    service = services.get(name)
    if service is None:
        available = ", ".join(sorted(services))
        raise RuntimeError(f"ESPHome service {name!r} is unavailable; got: {available}")
    return await client.execute_service(
        service,
        data or {},
        return_response=True if response else None,
        timeout=30.0,
    )


def response_data(response: Any) -> dict[str, Any]:
    if response is None:
        return {}
    for attribute in ("data", "response"):
        value = getattr(response, attribute, None)
        if isinstance(value, dict):
            return value
    raw = getattr(response, "response_data", None)
    if isinstance(raw, bytes):
        return json.loads(raw.decode("utf-8"))
    if isinstance(response, dict):
        return response
    raise RuntimeError(f"Unexpected ESPHome response type: {type(response)!r}: {response!r}")


async def capture_screen(
    client: aioesphomeapi.APIClient,
    services: dict[str, Any],
    destination: Path,
) -> None:
    chunks: list[str] = []
    offset = 0
    total_size: int | None = None
    while total_size is None or offset < total_size:
        response = await call_service(
            client,
            services,
            "debug_capture_screen",
            {"offset": offset},
            response=True,
        )
        data = response_data(response)
        if error := data.get("error"):
            raise RuntimeError(f"Framebuffer capture failed: {error}")
        chunk = str(data.get("jpeg_base64_chunk", ""))
        if not chunk:
            raise RuntimeError(f"Framebuffer capture returned no data at offset {offset}")
        chunks.append(chunk)
        offset += len(chunk)
        total_size = int(data["total_size"])

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(base64.b64decode("".join(chunks)))


async def exercise_motion(
    client: aioesphomeapi.APIClient,
    services: dict[str, Any],
    duration: float,
    rate_hz: float,
    transcript_mode: str,
) -> None:
    interval = 1.0 / rate_hz
    start = time.monotonic()
    next_update = start
    sent = 0
    user_words = "Jak będzie dziś wyglądała pogoda w Warszawie i czy potrzebuję parasola".split()
    assistant_words = (
        "Dziś będzie przeważnie słonecznie temperatura sięgnie dwudziestu czterech "
        "stopni a parasol nie będzie potrzebny"
    ).split()
    while True:
        now = time.monotonic()
        elapsed = now - start
        if elapsed >= duration:
            break

        # Speech-like modulation exercises both small idle waves and energetic peaks.
        gate = 0.16 if int(elapsed * 1.7) % 7 == 0 else 1.0
        level = gate * max(
            0.03,
            min(
                1.0,
                0.50
                + 0.30 * math.sin(elapsed * 11.7)
                + 0.16 * math.sin(elapsed * 23.1),
            ),
        )
        listening = elapsed < duration / 2.0
        phase_elapsed = elapsed if listening else elapsed - duration / 2.0
        words = user_words if listening else assistant_words
        word_index = min(len(words) - 1, int(phase_elapsed / 0.12))
        if transcript_mode == "word":
            transcript = words[word_index]
        elif transcript_mode == "phrase":
            phrase_end = min(len(words), ((word_index // 6) + 1) * 6)
            transcript = " ".join(words[:phrase_end])
        else:
            transcript = (
                "Test płynności wejścia audio"
                if listening
                else "Test płynności odpowiedzi audio"
            )
        await call_service(
            client,
            services,
            "debug_voice_visual_state",
            {
                "phase": "Listening" if listening else "Answering",
                "user_text": transcript if listening else "",
                "assistant_text": "" if listening else transcript,
                "input_level": level if listening else 0.0,
                "output_level": 0.0 if listening else level,
            },
        )
        sent += 1
        next_update += interval
        await asyncio.sleep(max(0.0, next_update - time.monotonic()))

    elapsed = time.monotonic() - start
    print(
        f"Motion benchmark: sent={sent} elapsed={elapsed:.3f}s "
        f"input_rate={sent / elapsed:.1f}Hz transcript_mode={transcript_mode}",
        flush=True,
    )


async def run(args: argparse.Namespace) -> None:
    client = aioesphomeapi.APIClient(
        args.host,
        args.port,
        args.password,
        client_info="Atmosfera voice UI test",
    )
    await client.connect(login=True)
    unsubscribe_logs = None
    try:
        services = await find_services(client)
        print(f"Connected to {args.host}; {len(services)} user services available", flush=True)
        if args.profile:
            log_markers = (
                "lvgl_material.voice",
                "lvgl.region",
                "dsi",
                "took a long time",
                "voice_wave",
            )

            def on_log(message: Any) -> None:
                text = bytes(message.message).decode("utf-8", errors="replace").strip()
                if any(marker in text for marker in log_markers):
                    print(text, flush=True)

            unsubscribe_logs = client.subscribe_logs(
                on_log,
                log_level=aioesphomeapi.LogLevel.LOG_LEVEL_VERBOSE,
                dump_config=False,
            )
            await set_switch(client, "performance_logs", True)
            await asyncio.sleep(0.3)

        await call_service(client, services, "debug_show_voice_visual")
        await asyncio.sleep(0.8)

        if args.motion_seconds > 0:
            await exercise_motion(
                client,
                services,
                args.motion_seconds,
                args.motion_hz,
                args.transcript_mode,
            )
            await asyncio.sleep(2.5)

        scenarios = () if args.skip_captures else (
            (
                "listening",
                "Listening",
                "Jak b\u0119dzie dzi\u015b wygl\u0105da\u0142a pogoda?",
                "",
                0.72,
                0.0,
            ),
            (
                "thinking",
                "Thinking",
                "Jak b\u0119dzie dzi\u015b wygl\u0105da\u0142a pogoda?",
                "",
                0.0,
                0.0,
            ),
            (
                "answering",
                "Answering",
                "Jak b\u0119dzie dzi\u015b wygl\u0105da\u0142a pogoda?",
                "Dzi\u015b b\u0119dzie s\u0142onecznie i ciep\u0142o. Temperatura si\u0119gnie dwudziestu czterech stopni.",
                0.0,
                0.78,
            ),
        )
        for filename, phase, user_text, assistant_text, input_level, output_level in scenarios:
            await call_service(
                client,
                services,
                "debug_voice_visual_state",
                {
                    "phase": phase,
                    "user_text": user_text,
                    "assistant_text": assistant_text,
                    "input_level": input_level,
                    "output_level": output_level,
                },
            )
            await asyncio.sleep(args.settle)
            destination = args.output / f"voice-{filename}.jpg"
            await capture_screen(client, services, destination)
            print(f"Captured {phase}: {destination}", flush=True)

        if not args.skip_captures:
            follow_up_states = (
                (
                    "Listening",
                    "A jak b\u0119dzie jutro?",
                    "Dzi\u015b b\u0119dzie s\u0142onecznie i ciep\u0142o. Temperatura si\u0119gnie dwudziestu czterech stopni.",
                    0.65,
                    0.0,
                ),
                (
                    "Answering",
                    "A jak b\u0119dzie jutro?",
                    "Jutro pojawi si\u0119 wi\u0119cej chmur, ale nadal b\u0119dzie ciep\u0142o.",
                    0.0,
                    0.72,
                ),
            )
            for phase, user_text, assistant_text, input_level, output_level in follow_up_states:
                await call_service(
                    client,
                    services,
                    "debug_voice_visual_state",
                    {
                        "phase": phase,
                        "user_text": user_text,
                        "assistant_text": assistant_text,
                        "input_level": input_level,
                        "output_level": output_level,
                    },
                )
                await asyncio.sleep(args.settle)

            destination = args.output / "voice-follow-up-answering.jpg"
            await capture_screen(client, services, destination)
            print(f"Captured follow-up dialog: {destination}", flush=True)
    finally:
        if args.profile:
            try:
                await set_switch(client, "performance_logs", False)
            except Exception as err:
                print(f"Warning: could not disable performance logs: {err}", flush=True)
        if unsubscribe_logs is not None:
            unsubscribe_logs()
        try:
            services = await find_services(client)
            await call_service(client, services, "debug_hide_voice_visual")
        except Exception as err:  # Keep teardown from hiding the real test result.
            print(f"Warning: could not hide synthetic voice UI: {err}", flush=True)
        await client.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="192.168.88.82")
    parser.add_argument("--port", type=int, default=6053)
    parser.add_argument("--password", default="")
    parser.add_argument("--settle", type=float, default=0.8)
    parser.add_argument("--output", type=Path, default=Path(".tmp-voice-ui"))
    parser.add_argument("--motion-seconds", type=float, default=0.0)
    parser.add_argument("--motion-hz", type=float, default=30.0)
    parser.add_argument(
        "--transcript-mode",
        choices=("static", "word", "phrase"),
        default="static",
    )
    parser.add_argument("--profile", action="store_true")
    parser.add_argument("--skip-captures", action="store_true")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
