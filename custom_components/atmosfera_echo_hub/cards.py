"""Versioned card contract shared by Home Assistant and the display."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.translation import (
    async_get_cached_translations,
    async_translate_state,
)

from .text import plain_text

CARD_CONTRACT_VERSION = 1
CARD_SLOT_COUNT = 11

SUPPORTED_DOMAINS = {
    "alarm_control_panel",
    "binary_sensor",
    "button",
    "climate",
    "cover",
    "fan",
    "input_boolean",
    "light",
    "lock",
    "media_player",
    "number",
    "scene",
    "script",
    "sensor",
    "switch",
}

ICONS = {
    "action": "\ue5d5",
    "alarm": "\ue9e0",
    "climate": "\ue1ff",
    "cover": "\ue88a",
    "fan": "\uf168",
    "light": "\ue0f0",
    "lock": "\ue897",
    "scene": "\ue65f",
    "speed": "\ue429",
    "switch": "\ue8ac",
}

PALETTES = {
    # These are editor/default previews only. Runtime payloads derive every
    # role from the selected accent seed in ``derive_palette``.
    "primary": (0x36BCF0, 0x071018),
    "primary_container": (0x8AD8F8, 0x071018),
    "secondary": (0x4FC3F7, 0x071018),
    "surface": (0x071018, 0xF5F7FA),
    "tertiary": (0x26A69A, 0x071018),
}


def normalize_accent(value: Any) -> int:
    """Return a bounded RGB seed from a HA option or the default blue."""
    if isinstance(value, int):
        return value & 0xFFFFFF
    text = str(value or "36BCF0").strip().lstrip("#")
    try:
        return int(text, 16) & 0xFFFFFF if len(text) == 6 else 0x36BCF0
    except ValueError:
        return 0x36BCF0


def derive_palette(accent: int) -> dict[str, tuple[int, int]]:
    """Derive a compact, deterministic Material-like palette from one seed."""
    r, g, b = (accent >> 16) & 0xFF, (accent >> 8) & 0xFF, accent & 0xFF
    luminance = r * 299 + g * 587 + b * 114
    on_accent = 0x071018 if luminance > 150000 else 0xFFFFFF
    lighten = lambda amount: ((min(255, r + amount) << 16) |
                              (min(255, g + amount) << 8) |
                              min(255, b + amount))
    dark = ((r // 5) << 16) | ((g // 5) << 8) | (b // 5)
    return {
        "primary": (accent, on_accent),
        "secondary": (lighten(28) | 0x101010, on_accent),
        "tertiary": (lighten(38), on_accent),
        "primary_container": (lighten(58), 0x071018),
        "surface": (dark, 0xF5F7FA),
    }

DEFAULT_CARDS: list[dict[str, Any]] = [
    {
        "slot": 0,
        "entity_id": "light.living_room",
        "title": "Lights",
        "icon": "light",
        "palette": "primary",
    },
    {
        "slot": 1,
        "entity_id": "climate.living_room",
        "title": "Climate",
        "icon": "climate",
        "palette": "primary_container",
    },
    {
        "slot": 2,
        "entity_id": "cover.living_room",
        "title": "Cover",
        "icon": "cover",
        "palette": "secondary",
    },
    {
        "slot": 3,
        "entity_id": "lock.front_door",
        "title": "Front door",
        "icon": "lock",
        "palette": "primary",
    },
    {
        "slot": 4,
        "entity_id": "alarm_control_panel.home",
        "title": "Alarm",
        "icon": "alarm",
        "palette": "secondary",
    },
    {
        "slot": 5,
        "entity_id": "cover.garage_door",
        "title": "Garage",
        "icon": "cover",
        "palette": "surface",
    },
    {
        "slot": 6,
        "entity_id": "fan.living_room",
        "title": "Fan",
        "icon": "fan",
        "palette": "secondary",
    },
    {
        "slot": 7,
        "entity_id": "fan.living_room",
        "title": "Speed",
        "icon": "speed",
        "palette": "primary",
    },
    {
        "slot": 8,
        "entity_id": "switch.living_room",
        "title": "Switch",
        "icon": "switch",
        "palette": "surface",
    },
    {
        "slot": 9,
        "entity_id": "scene.relax",
        "title": "Scene",
        "icon": "scene",
        "palette": "tertiary",
    },
    {
        "slot": 10,
        "entity_id": "button.doorbell",
        "title": "Action",
        "icon": "action",
        "palette": "secondary",
    },
]


@dataclass(frozen=True, slots=True)
class CardAction:
    """Validated Home Assistant action invoked by one card."""

    domain: str
    service: str
    data: dict[str, Any]


def normalize_cards(cards: Any) -> list[dict[str, Any]]:
    """Return a bounded, deterministic representation of all card slots."""
    source = cards if isinstance(cards, list) else DEFAULT_CARDS
    by_slot: dict[int, dict[str, Any]] = {}
    for raw in source:
        if not isinstance(raw, dict):
            continue
        try:
            slot = int(raw.get("slot", -1))
        except (TypeError, ValueError):
            continue
        if slot < 0 or slot >= CARD_SLOT_COUNT:
            continue
        entity_id = plain_text(raw.get("entity_id"), 128)
        domain = entity_id.partition(".")[0]
        if entity_id and domain not in SUPPORTED_DOMAINS:
            continue
        icon = plain_text(raw.get("icon", "action"), 32)
        palette = plain_text(raw.get("palette", "surface"), 32)
        by_slot[slot] = {
            "slot": slot,
            "entity_id": entity_id,
            "title": plain_text(raw.get("title") or entity_id.partition(".")[2], 40),
            "icon": icon if icon in ICONS else "action",
            "palette": palette if palette in PALETTES else "surface",
            "service": plain_text(raw.get("service"), 96),
            "visible": bool(raw.get("visible", True)),
        }
    return [by_slot[slot] for slot in sorted(by_slot)]


def card_entity_ids(cards: list[dict[str, Any]]) -> list[str]:
    """Return unique entity IDs used by cards."""
    return list(dict.fromkeys(card["entity_id"] for card in cards if card["entity_id"]))


def _translate_state_for_locale(
    hass: HomeAssistant, state: State, language: str | None
) -> str:
    """Translate a generic entity state using the device display locale.

    Home Assistant's public ``async_translate_state`` intentionally uses the
    server's configured language.  The display can have a different locale,
    so read the same cached backend resources directly when one is supplied.
    """
    language = language.replace("_", "-").split("-", 1)[0].lower() if language else None
    registry_entry = async_get_entity_registry(hass).async_get(state.entity_id)
    platform = registry_entry.platform if registry_entry is not None else None
    translation_key = (
        registry_entry.translation_key if registry_entry is not None else None
    )
    domain = state.entity_id.partition(".")[0]
    device_class = state.attributes.get("device_class")
    if language is None or language == hass.config.language.lower().split("-", 1)[0]:
        return async_translate_state(
            hass,
            state.state,
            domain,
            platform,
            translation_key,
            device_class,
        )

    translations = async_get_cached_translations(hass, language, "entity")
    if platform is not None and translation_key is not None:
        key = (
            f"component.{platform}.entity.{domain}.{translation_key}"
            f".state.{state.state}"
        )
        if key in translations:
            return translations[key]
    translations = async_get_cached_translations(hass, language, "entity_component")
    if device_class is not None:
        key = (
            f"component.{domain}.entity_component.{device_class}"
            f".state.{state.state}"
        )
        if key in translations:
            return translations[key]
    key = f"component.{domain}.entity_component._.state.{state.state}"
    return translations.get(key, state.state)


def _state_subtitle(
    hass: HomeAssistant, state: State | None, language: str | None = None
) -> str:
    if state is None:
        return "Unavailable"
    if state.state in {"unknown", "unavailable"}:
        return state.state.title()
    domain = state.entity_id.partition(".")[0]
    attributes = state.attributes
    if domain == "climate":
        value = attributes.get("current_temperature", attributes.get("temperature"))
        unit = attributes.get("temperature_unit", "")
        if value is not None:
            return plain_text(f"{value} {unit}", 40)
    if domain == "fan" and attributes.get("percentage") is not None:
        return plain_text(f"{attributes['percentage']}%", 40)
    if domain in {"sensor", "number"}:
        unit = attributes.get("unit_of_measurement", "")
        return plain_text(f"{state.state} {unit}", 40)
    if domain == "media_player":
        return plain_text(attributes.get("media_title") or state.state.title(), 40)
    translated = _translate_state_for_locale(hass, state, language)
    if not translated or translated == state.state:
        translated = state.state.replace("_", " ").title()
    return plain_text(translated, 40)


def presentation_payload(
    hass: HomeAssistant,
    cards: list[dict[str, Any]],
    accent_color: Any = "36BCF0",
    language: str | None = None,
) -> dict[str, Any]:
    """Build the compact payload consumed by the fixed LVGL object pool."""
    accent = normalize_accent(accent_color)
    palettes = derive_palette(accent)
    rendered: list[dict[str, Any]] = []
    for card in cards:
        background, foreground = palettes[card["palette"]]
        state = hass.states.get(card["entity_id"]) if card["entity_id"] else None
        rendered.append(
            {
                "slot": card["slot"],
                "visible": card["visible"],
                "icon": ICONS[card["icon"]],
                "title": card["title"],
                "subtitle": _state_subtitle(hass, state, language),
                # Keep the role in the wire contract.  The embedded renderer
                # derives the actual colors from the current accent seed.
                "palette": card["palette"],
                "background": background,
                "foreground": foreground,
            }
        )
    return {
        "version": CARD_CONTRACT_VERSION,
        "theme": {"accent": accent},
        "cards": rendered,
    }


def resolve_action(hass: HomeAssistant, card: dict[str, Any]) -> CardAction | None:
    """Resolve a configured or conservative default action for one card."""
    entity_id = card["entity_id"]
    if not entity_id:
        return None
    domain = entity_id.partition(".")[0]
    configured = card.get("service", "")
    if configured:
        action_domain, separator, service = configured.partition(".")
        if not separator or not hass.services.has_service(action_domain, service):
            return None
        return CardAction(action_domain, service, {ATTR_ENTITY_ID: entity_id})
    if domain == "button":
        return CardAction("button", "press", {ATTR_ENTITY_ID: entity_id})
    if domain in {"scene", "script"}:
        return CardAction(domain, "turn_on", {ATTR_ENTITY_ID: entity_id})
    if domain == "lock":
        state = hass.states.get(entity_id)
        service = "unlock" if state is not None and state.state == "locked" else "lock"
        return CardAction("lock", service, {ATTR_ENTITY_ID: entity_id})
    if domain in {"light", "switch", "input_boolean", "fan", "cover", "media_player"}:
        return CardAction("homeassistant", "toggle", {ATTR_ENTITY_ID: entity_id})
    return None
