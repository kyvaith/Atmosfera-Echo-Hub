"""Versioned card contract shared by Home Assistant and the display."""

from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.area_registry import async_get as async_get_area_registry
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.translation import (
    async_get_cached_translations,
    async_translate_state,
)

from .formatting import binary_fallback, display_language, sensor_text, state_label, sun_event_text
from .layout import (
    ACTION_FIELDS,
    NO_DATA_SERVICES,
    SLOT_COUNT,
    SUPPORTED_DOMAINS,
    LayoutError,
    migrate_legacy,
    validate_action,
    validate_field,
    validate_layout,
)
from .text import plain_text
from .numeric_domain import NumericDomain, NumericDomainError


def _number_control_metadata(hass, state):
    """Public exact metadata for explicit editor choice; never service authority."""
    if not state.entity_id.startswith("input_number.") or not hass.services.has_service("input_number", "set_value"):
        return {}
    try:
        domain = NumericDomain.from_ha(state.attributes)
    except NumericDomainError:
        return {}
    return {"number_control": {"domain": domain.descriptor(), "index": domain.observed_index(state.state)}}

CARD_CONTRACT_VERSION = 1
CARD_SLOT_COUNT = SLOT_COUNT
_TIMESTAMP_ACTION_DOMAINS = frozenset(("button", "input_button", "scene"))
_ACTION_AVAILABILITY_DOMAINS = frozenset(("input_button", "button", "scene", "script", "timer"))

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
    "sensor": "\ue1ff",
    "door": "\uf1b4",
    "presence": "\uf0d3",
    "clock": "\ue8b5",
    "webhook": "\ue157",
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
    def lighten(amount):
        return ((min(255, r + amount) << 16) |
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
        for key in ("id", "type", "action"):
            if key in raw:
                by_slot[slot][key] = deepcopy(raw[key])
    return [by_slot[slot] for slot in sorted(by_slot)]


def card_entity_ids(cards: list[dict[str, Any]]) -> list[str]:
    """Return unique entity IDs used by cards."""
    return list(dict.fromkeys(card["entity_id"] for card in cards if card["entity_id"]))


def entry_layout(options: Any, data: Any) -> dict[str, Any]:
    """Read v2 configuration or migrate the existing slot configuration once."""
    options, data = options or {}, data or {}
    raw = options.get("home_layout", data.get("home_layout"))
    if raw is not None:
        return validate_layout(raw)
    return migrate_legacy(normalize_cards(options.get("tiles", data.get("tiles"))))


def _translate_state_for_locale(
    hass: HomeAssistant, state: State, language: str | None,
    *, semantic_fallback: str | None = None,
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
    if semantic_fallback is None and (
        language is None or language == hass.config.language.lower().split("-", 1)[0]
    ):
        return async_translate_state(
            hass,
            state.state,
            domain,
            platform,
            translation_key,
            device_class,
        )

    language = language or hass.config.language
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
    # A specific HA entity/device-class translation wins. If only a generic
    # on/off translation is cached, retain the known class's meaning instead.
    if semantic_fallback is not None:
        return semantic_fallback
    key = f"component.{domain}.entity_component._.state.{state.state}"
    return translations.get(key, state.state)


def _state_subtitle(
    hass: HomeAssistant, state: State | None, language: str | None = None
) -> str:
    display_locale = language or hass.config.language
    if state is None:
        return state_label("unavailable", display_locale)
    if not isinstance(state.state, str):
        return state_label("unknown", display_locale)
    if state.state in ("unknown", "unavailable"):
        return state_label(state.state, display_locale)
    domain = state.entity_id.partition(".")[0]
    attributes = state.attributes
    if domain == "sun":
        return sun_event_text(state.state, attributes, getattr(hass.config, "time_zone", None), display_locale)
    if domain == "climate":
        value = attributes.get("current_temperature", attributes.get("temperature"))
        unit = attributes.get("temperature_unit", "")
        if value is not None:
            return plain_text(f"{value} {unit}", 40)
    if domain == "fan" and attributes.get("percentage") is not None:
        return plain_text(f"{attributes['percentage']}%", 40)
    if domain in {"sensor", "number", "input_number"}:
        options = None
        if domain == "sensor":
            entry = async_get_entity_registry(hass).async_get(state.entity_id)
            options = getattr(entry, "options", None)
        formatted = sensor_text(
            state.state, attributes.get("unit_of_measurement", ""),
            attributes.get("device_class"), display_locale, options,
        )
        if formatted is not None:
            return formatted
    if domain == "media_player":
        return plain_text(attributes.get("media_title") or state.state.title(), 40)
    fallback = binary_fallback(state.state, attributes.get("device_class"), display_locale) if domain == "binary_sensor" else None
    translated = _translate_state_for_locale(hass, state, language, semantic_fallback=fallback)
    if not translated or translated == state.state:
        translated = state.state.replace("_", " ").title()
    return plain_text(translated, 40)


def _state_allows_action(state: State | None) -> bool:
    """An unpressed button/unactivated scene has no timestamp, not an outage."""
    if state is None or not isinstance(state.state, str) or state.state == "unavailable":
        return False
    return state.state != "unknown" or state.entity_id.partition(".")[0] in _TIMESTAMP_ACTION_DOMAINS


def _card_subtitle(hass: HomeAssistant, card: dict[str, Any], state: State | None,
                   language: str | None) -> str:
    """Describe a validated one-shot action, never optimistic execution state."""
    domain = card["entity_id"].partition(".")[0]
    if domain == "timer" and card.get("action", {"kind": "default"}) == {"kind": "default"} and not card.get("service"):
        action = resolve_action(hass, card)
        if action is not None and action.domain == "timer":
            polish = display_language(language or hass.config.language) == "pl"
            labels = {"idle": ("Start", "Uruchom"), "active": ("Pause", "Wstrzymaj"), "paused": ("Resume", "Wznów")}
            return labels[state.state][polish]
    if domain in _TIMESTAMP_ACTION_DOMAINS or domain == "script":
        action = resolve_action(hass, card)
        polish = display_language(language or hass.config.language) == "pl"
        if action is not None:
            if domain in {"button", "input_button"} and action.domain == domain and action.service == "press":
                return "Naciśnij" if polish else "Press"
            if domain in {"scene", "script"} and action.domain in {domain, "homeassistant"} and action.service == "turn_on":
                return "Uruchom" if polish else "Run"
    return _state_subtitle(hass, state, language)


def ordinary_action_availability(card: dict[str, Any]) -> bool:
    """Whether a card participates in negotiated ordinary-action availability.

    Execution eligibility remains the live resolver's responsibility.
    """
    return (card["entity_id"].partition(".")[0] in _ACTION_AVAILABILITY_DOMAINS
            and card.get("action", {}).get("kind") != "control")


def presentation_payload(
    hass: HomeAssistant,
    cards: list[dict[str, Any]],
    accent_color: Any = "36BCF0",
    language: str | None = None,
    *, light_control_supported: bool = False, number_control_supported: bool = False,
    press_enabled_supported: bool = False,
) -> dict[str, Any]:
    """Build the compact payload consumed by the fixed LVGL object pool."""
    accent = normalize_accent(accent_color)
    palettes = derive_palette(accent)
    rendered: list[dict[str, Any]] = []
    by_slot = {card["slot"]: card for card in cards}
    for slot in range(CARD_SLOT_COUNT):
        card = by_slot.get(slot)
        if card is None:
            # Firmware leaves omitted bindings untouched. Explicitly hide
            # every unassigned slot so moves/removals cannot retain stale UI.
            rendered.append({"slot": slot, "id": "", "visible": False})
            continue
        background, foreground = palettes[card["palette"]]
        state = hass.states.get(card["entity_id"]) if card["entity_id"] else None
        rendered.append(
            {
                "slot": card["slot"],
                "id": card.get("id", ""),
                "visible": card["visible"] and slot >= 2,
                "icon": ICONS[card["icon"]],
                "title": card["title"],
                "subtitle": _card_subtitle(hass, card, state, language),
                # Keep the role in the wire contract.  The embedded renderer
                # derives the actual colors from the current accent seed.
                "palette": card["palette"],
                "background": background,
                "foreground": foreground,
            }
        )
        if card.get("action", {}).get("kind") == "control":
            control = card["action"].get("control")
            supported = light_control_supported if control == "light" else number_control_supported if control == "number" else False
            if supported and rendered[-1]["visible"]:
                rendered[-1]["control_kind"] = control
            else:
                rendered[-1]["subtitle"] = ("Urządzenie bez obsługi" if display_language(language or hass.config.language) == "pl"
                                             else "Unsupported device")
        elif press_enabled_supported is True and ordinary_action_availability(card):
            # Action availability is HA policy, not a service-result acknowledgement.
            rendered[-1]["press_enabled"] = resolve_action(hass, card) is not None
    return {
        "version": CARD_CONTRACT_VERSION,
        "theme": {"accent": accent},
        "cards": rendered,
    }


def resolve_action(hass: HomeAssistant, card: dict[str, Any]) -> CardAction | None:
    """Resolve a configured or conservative default action for one card."""
    entity_id = card["entity_id"]
    if not entity_id or not card.get("visible", True) or card.get("slot", 0) < 2:
        return None
    domain = entity_id.partition(".")[0]
    if domain == "sun":
        return None  # Passive data only, including raw/legacy configured service attempts.
    state = hass.states.get(entity_id)
    if not _state_allows_action(state):
        return None
    configured = card.get("action")
    if configured is None:
        configured = ({"kind": "service", "service": card["service"], "data": {}}
                      if card.get("service") else {"kind": "default"})
    try:
        action = validate_action(configured, entity_id)
        if card.get("type") == "sensor" or action["kind"] == "none":
            return None
        if action["kind"] == "default":
            if domain in {"button", "input_button"}:
                service = f"{domain}.press"
            elif domain in {"scene", "script"}:
                service = f"{domain}.turn_on"
            elif domain in {"light", "switch", "input_boolean", "fan"}:
                service = f"{domain}.toggle"
            elif domain == "media_player":
                service = "media_player.media_play_pause"
            elif domain == "timer":
                operation = {"idle": "start", "active": "pause", "paused": "start"}.get(state.state)
                if operation is None:
                    return None
                # Installed Core timer.start with no duration preserves paused remaining time.
                service = f"timer.{operation}"
            else:
                # Opening covers or unlocking/disarming must never be an
                # inferred default for an unconfirmed compact tile tap.
                return None
            action = {"kind": "service", "service": service, "data": {}}
        validate_live_action(hass, state, action)
    except LayoutError:
        return None
    action_domain, service = action["service"].split(".", 1)
    return CardAction(action_domain, service, {ATTR_ENTITY_ID: entity_id, **action["data"]})


def _finite(value: Any, fallback: float) -> float:
    try:
        return float(value) if type(value) in (int, float) and math.isfinite(value) else fallback
    except OverflowError:
        return fallback


def entity_actions(hass: HomeAssistant, state: State) -> list[dict[str, Any]]:
    """Return only non-secret descriptors of services supported by this entity."""
    domain = state.entity_id.split(".", 1)[0]
    if domain == "sun":
        return []
    attrs = state.attributes
    features = attrs.get("supported_features", 0)
    # Runtime HA state attributes may retain IntFlag values before JSON
    # serialization; treating only exact int as valid hides real controls.
    features = int(features) if isinstance(features, int) and not isinstance(features, bool) else 0
    services = set(NO_DATA_SERVICES) | set(ACTION_FIELDS)
    result = []
    # Feature values are the HA 2026.7.1 public entity feature contract.
    cover_features = {
        "open_cover": 1, "close_cover": 2, "set_cover_position": 4, "stop_cover": 8,
        "open_cover_tilt": 16, "close_cover_tilt": 32, "stop_cover_tilt": 64,
        "set_cover_tilt_position": 128,
    }
    fan_features = {
        "set_percentage": 1, "oscillate": 2, "set_direction": 4, "set_preset_mode": 8,
        "turn_off": 16, "turn_on": 32, "toggle": 16 if state.state == "on" else 32,
    }
    climate_features = {"set_preset_mode": 16, "set_fan_mode": 8, "set_swing_mode": 32}
    media_features = {
        "media_pause": 1, "media_play": 16384, "media_previous_track": 16,
        "media_next_track": 32, "turn_on": 128, "turn_off": 256,
        "media_play_pause": 1 if state.state == "playing" else 16384,
    }
    vacuum_features = {
        "start": 8192, "pause": 4, "stop": 8, "return_to_base": 16,
        "locate": 512, "clean_spot": 1024,
    }
    mower_features = {"start_mowing": 1, "pause": 2, "dock": 4}
    for full_service in sorted(services):
        service_domain, service = full_service.split(".", 1)
        if service_domain != domain or not hass.services.has_service(domain, service):
            continue
        if domain == "cover" and not features & cover_features.get(service, 0):
            continue
        if domain == "fan" and service in fan_features and not features & fan_features[service]:
            continue
        if domain == "climate" and service in climate_features and not features & climate_features[service]:
            continue
        feature_gate = {
            "media_player": media_features, "vacuum": vacuum_features,
            "lawn_mower": mower_features,
        }.get(domain)
        if feature_gate is not None and not features & feature_gate.get(service, 0):
            continue
        fields = deepcopy(ACTION_FIELDS.get(full_service, {}))
        if domain == "light" and service == "turn_on":
            modes = set(attrs.get("supported_color_modes") or [])
            if not modes - {"onoff", "unknown"}:
                fields.pop("brightness_pct", None)
            if "color_temp" not in modes:
                fields.pop("color_temp_kelvin", None)
            else:
                fields["color_temp_kelvin"].update(
                    min=_finite(attrs.get("min_color_temp_kelvin"), 2000),
                    max=_finite(attrs.get("max_color_temp_kelvin"), 6500),
                )
            if not modes.intersection({"rgb", "rgbw", "rgbww", "hs", "xy"}):
                fields.pop("rgb_color", None)
        if full_service in {"number.set_value", "input_number.set_value"}:
            if "min" not in attrs or "max" not in attrs:
                continue
            fields["value"].update(min=_finite(attrs["min"], 0), max=_finite(attrs["max"], 100),
                                   step=_finite(attrs.get("step"), 1))
        if full_service == "climate.set_temperature":
            fields = {
                name: schema for name, schema in fields.items()
                if (name == "temperature" and features & 1) or (name != "temperature" and features & 2)
            }
            if not fields:
                continue
            for schema in fields.values():
                schema.update(min=_finite(attrs.get("min_temp"), 7),
                              max=_finite(attrs.get("max_temp"), 35),
                              step=_finite(attrs.get("target_temp_step"), 1))
        option_fields = {
            "select.select_option": ("option", "options"),
            "input_select.select_option": ("option", "options"),
            "fan.set_preset_mode": ("preset_mode", "preset_modes"),
            "climate.set_hvac_mode": ("hvac_mode", "hvac_modes"),
            "climate.set_preset_mode": ("preset_mode", "preset_modes"),
            "climate.set_fan_mode": ("fan_mode", "fan_modes"),
            "climate.set_swing_mode": ("swing_mode", "swing_modes"),
        }
        if full_service in option_fields:
            field, attribute = option_fields[full_service]
            choices = [value for value in attrs.get(attribute, [])
                       if isinstance(value, str) and 0 < len(value) <= 128][:128]
            if not choices:
                continue
            fields[field] = {"type": "select", "options": choices, "required": True}
        if domain == "alarm_control_panel" or (domain == "lock" and service != "lock"):
            continue
        result.append({"service": full_service, "fields": fields})
    return result


def validate_live_action(hass: HomeAssistant, state: State, action: dict[str, Any]) -> None:
    """Recheck live capabilities before dispatch without performing an action."""
    service = action["service"]
    descriptors = {item["service"]: item for item in entity_actions(hass, state)}
    if service.startswith("homeassistant.") and not action["data"]:
        equivalent = f"{state.entity_id.split('.', 1)[0]}.{service.split('.', 1)[1]}"
        if equivalent in descriptors and hass.services.has_service("homeassistant", service.split(".", 1)[1]):
            return
    descriptor = descriptors.get(service)
    if descriptor is None:
        raise LayoutError("unsupported_action", "Entity does not support this action")
    for name, value in action["data"].items():
        schema = descriptor["fields"].get(name)
        if schema is None:
            raise LayoutError("invalid_action_data", f"Entity does not support {name}")
        validate_field(value, schema, name)


def entity_catalogue(hass: HomeAssistant, query: str = "", domains: list[str] | None = None,
                     limit: int = 200, area_id: str | None = None) -> dict[str, Any]:
    """Read runtime entities and local registry area metadata without subscriptions."""
    if area_id is not None and (not isinstance(area_id, str) or len(area_id) > 256):
        raise LayoutError("invalid_filter", "Area filter must be a string of at most 256 characters")
    entity_registry = async_get_entity_registry(hass)
    device_registry = async_get_device_registry(hass)
    area_registry = async_get_area_registry(hass)
    device_areas: dict[str, str | None] = {}
    resolved_areas: dict[str, tuple[str | None, str | None]] = {}

    def entity_area(entity_id: str) -> tuple[str | None, str | None]:
        entry = entity_registry.async_get(entity_id)
        if entry is None:
            # YAML entities remain eligible. State attributes are not registry
            # ownership and must not fabricate an area/device relationship.
            return None, None
        assigned = entry.area_id
        if assigned is None and entry.device_id is not None:
            if entry.device_id not in device_areas:
                device = device_registry.async_get(entry.device_id)
                device_areas[entry.device_id] = device.area_id if device is not None else None
            assigned = device_areas[entry.device_id]
        if assigned is None:
            return None, None
        if assigned not in resolved_areas:
            area = area_registry.async_get_area(assigned)
            # A stale explicit override is unassigned, not an invitation to
            # silently choose the device's different area.
            resolved_areas[assigned] = (
                (area.id, plain_text(area.name, 80)) if area is not None else (None, None)
            )
        return resolved_areas[assigned]

    query = query.casefold()
    requested = set(domains or SUPPORTED_DOMAINS) & SUPPORTED_DOMAINS
    matches = []
    areas = {}
    for state in hass.states.async_all():
        domain = state.entity_id.split(".", 1)[0]
        if domain not in SUPPORTED_DOMAINS:
            continue
        assigned, area_name = entity_area(state.entity_id)
        if assigned is not None:
            areas[assigned] = {"area_id": assigned, "area_name": area_name}
        if domain not in requested or (area_id is not None and (assigned or "") != area_id):
            continue
        if query and query not in state.entity_id.casefold() and query not in str(state.attributes.get("friendly_name", "")).casefold():
            continue
        matches.append((state, assigned, area_name))
    matches.sort(key=lambda item: item[0].entity_id)
    facets = sorted(areas.values(), key=lambda item: (item["area_name"].casefold(), item["area_id"]))
    return {
        "entities": [{
            "entity_id": state.entity_id,
            "name": plain_text(state.attributes.get("friendly_name") or state.entity_id, 80),
            "domain": state.entity_id.split(".", 1)[0],
            "state": plain_text(state.state, 80),
            "available": _state_allows_action(state),
            "area_id": assigned, "area_name": area_name,
            "actions": entity_actions(hass, state),
            **_number_control_metadata(hass, state),
        } for state, assigned, area_name in matches[:limit]],
        "total": len(matches), "truncated": len(matches) > limit,
        # Stable facets precede all filters/limits and never enumerate registry
        # entries missing from runtime states. Bound response size explicitly.
        "areas": facets[:500], "area_total": len(facets), "areas_truncated": len(facets) > 500,
    }
