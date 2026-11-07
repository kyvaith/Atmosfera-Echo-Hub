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

from .formatting import MAX_PRECISION, binary_fallback, calendar_date_text, calendar_event_text, datetime_helper_text, display_language, person_state_text, sensor_text, state_label, sun_event_text
from .layout import (
    ACTION_FIELDS,
    NO_DATA_SERVICES,
    PRECISION_DOMAINS,
    SLOT_COUNT,
    CAROUSEL_SLOT_COUNT,
    SUPPORTED_DOMAINS,
    LayoutError,
    is_camera_preview_card,
    migrate_legacy,
    supports_state_color,
    validate_action,
    validate_field,
    validate_layout,
)
from .text import plain_text
from .caption_width import fit_caption, fit_compact_caption
from .numeric_domain import NumericDomainError
from .choice_domain import ChoiceDomain, ChoiceDomainError, choice_domain, choice_is_empty, choice_labels, choice_service, choice_state
from .tile_events import is_event_card, is_event_panel
from .state_labels import mapped_label
from .cover_domain import CoverDomain, CoverDomainError, CoverObservation
from .cover_panel_domain import CoverPanelDomain, CoverPanelObservation, PANEL_OPERATIONS as COVER_PANEL_OPERATIONS, SERVICES as COVER_PANEL_SERVICES
from .fan_oscillation import oscillation_value
from .fan_domain import FanDomain, FanDomainError, FanObservation
from .humidifier_domain import HumidifierDomain, HumidifierDomainError, HumidifierObservation
from .robot_domain import RobotDomain, RobotDomainError, RobotObservation
from .panel_domain import PanelDomain, PanelDomainError, PanelObservation, panel_type
from .extra_panel_domain import CONTEXT_INFO_TYPES, extra_metadata
from .agenda_domain import agenda_metadata
from .statistics_domain import statistics_metadata
from .media_panel_domain import media_metadata
from .action_parameters_domain import ACTION as PARAMETERS_ACTION, action_parameters_metadata
from .action_panel_domain import action_metadata
from .datetime_panel_domain import datetime_metadata
from .text_panel_domain import text_metadata
from .mower_actions import ACTIVITIES as MOWER_ACTIVITIES, command_allowed as mower_command_allowed, supported_operations as mower_supported_operations
from .vacuum_actions import ACTIVITIES as VACUUM_ACTIVITIES, command_allowed as vacuum_command_allowed, supported_operations as vacuum_supported_operations
from .vacuum_areas import area_command_allowed, has_area_capability, mapped_area_ids
from .number_domain import COLOR_TEMPERATURE_ACTION, COVER_POSITION_ACTION, COVER_TILT_ACTION, HUMIDITY_ACTION, TEMPERATURE_ACTION, color_temperature_domain, humidity_domain, number_domain, number_service, number_state, thermostat_snapshot


def _number_control_metadata(hass, state, property=None):
    """Public exact metadata for explicit editor choice; never service authority."""
    try:
        domain_name, service, _ = number_service(state.entity_id, property)
        if not hass.services.has_service(domain_name, service):
            return {}
        domain = number_domain(hass, state, property)
    except NumericDomainError:
        return {}
    humidity_key = "climate_humidity" if state.entity_id.startswith("climate.") else "humidifier_humidity"
    key = {"tilt_position": "cover_tilt", "position": "cover_position", "temperature": "climate_temperature", "humidity": humidity_key, "color_temp_kelvin": "light_color_temperature"}.get(property, "number_control")
    return {key: {"domain": domain.descriptor(), "index": domain.observed_index(number_state(state, property))}}


def _calendar_next_metadata(state):
    """Bounded authoritative captions with the exact observation they describe."""
    if not state.entity_id.startswith("calendar.") or state.state not in {"on", "off"}:
        return {}
    fields = {}
    for key in ("message", "all_day", "start_time", "end_time"):
        if key not in state.attributes:
            continue
        value = state.attributes[key]
        if key == "all_day":
            if type(value) is not bool:
                return {}
        elif not isinstance(value, str) or (key != "message" and len(value) != 19):
            return {}
        fields[key] = value[:256] if key == "message" else value
    return {"calendar_next": {"state": state.state, "fields": fields,
        "text": {language: calendar_event_text(state.state, state.attributes, language) for language in ("pl", "en")}}}


def _person_subtitle(hass, state, language):
    translated = _translate_state_for_locale(hass, state, language) if state.state in {"home", "not_home"} else None
    return person_state_text(state.state, language, translated)


def _person_presence_metadata(hass, state):
    """Only the reported state and captions; never account, GPS or photo fields."""
    if not state.entity_id.startswith("person.") or not isinstance(state.state, str):
        return {}
    return {"person_presence": {"state": state.state[:256],
        "text": {language: _person_subtitle(hass, state, language) for language in ("pl", "en")}}}


def _media_mute_value(state):
    """Only a reported boolean on a powered, capable player is actionable."""
    if state is None or not state.entity_id.startswith("media_player.") or state.state not in {"on", "idle", "playing", "paused", "buffering"}:
        return None
    features = state.attributes.get("supported_features")
    value = state.attributes.get("is_volume_muted")
    return value if (isinstance(features, int) and not isinstance(features, bool)
        and 0 <= features <= 2**53 - 1 and features & 8 and type(value) is bool) else None


def _media_mute_caption(hass, state, language):
    locale = language or hass.config.language
    if state is None or state.state in {"unknown", "unavailable"}:
        return _state_subtitle(hass, state, locale)
    polish = display_language(locale) == "pl"
    if state.state == "off":
        translated = _translate_state_for_locale(hass, state, locale)
        return plain_text(translated if translated and translated != state.state else ("Wyłączony" if polish else "Off"), 40)
    value = _media_mute_value(state)
    if value is None:
        return state_label("unknown", locale)
    raw = str(value).lower()
    translated = _choice_attribute_label(hass, state, "is_volume_muted", raw, locale)
    return plain_text((("Wyciszenie: " if polish else "Muted: ") + translated) if translated != raw else
        (("Wyciszony" if value else "Dźwięk wł.") if polish else ("Muted" if value else "Sound on")), 40)


def _media_mute_metadata(hass, state):
    value = _media_mute_value(state)
    if value is None or not hass.services.has_service("media_player", "volume_mute"):
        return {}
    return {"media_mute": {"state": state.state, "features": state.attributes["supported_features"], "value": value,
        "text": {language: _media_mute_caption(hass, state, language) for language in ("pl", "en")}}}


def _media_shuffle_value(state):
    """Only a reported boolean on a powered, capable player is actionable."""
    if state is None or not state.entity_id.startswith("media_player.") or state.state not in {"on", "idle", "playing", "paused", "buffering"}:
        return None
    features = state.attributes.get("supported_features")
    value = state.attributes.get("shuffle")
    return value if (isinstance(features, int) and not isinstance(features, bool)
        and 0 <= features <= 2**53 - 1 and features & 32768 and type(value) is bool) else None


def _media_shuffle_caption(hass, state, language):
    locale = language or hass.config.language
    if state is None or state.state in {"unknown", "unavailable"}:
        return _state_subtitle(hass, state, locale)
    polish = display_language(locale) == "pl"
    if state.state == "off":
        translated = _translate_state_for_locale(hass, state, locale)
        return plain_text(translated if translated and translated != state.state else ("Wyłączony" if polish else "Off"), 40)
    value = _media_shuffle_value(state)
    if value is None:
        return state_label("unknown", locale)
    raw = str(value).lower()
    translated = _choice_attribute_label(hass, state, "shuffle", raw, locale)
    return fit_compact_caption(plain_text((("Losowo: " if polish else "Shuffle: ") + translated) if translated != raw else
        (("Losowo" if value else "Po kolei") if polish else ("Shuffle on" if value else "In order")), 40))


def _media_shuffle_metadata(hass, state):
    value = _media_shuffle_value(state)
    if value is None or not hass.services.has_service("media_player", "shuffle_set"):
        return {}
    return {"media_shuffle": {"state": state.state, "features": state.attributes["supported_features"], "value": value,
        "text": {language: _media_shuffle_caption(hass, state, language) for language in ("pl", "en")}}}


def _media_stop_state(state):
    if (state is None or not state.entity_id.startswith("media_player.")
            or state.state not in {"on", "off", "standby", "idle", "playing", "paused", "buffering"}):
        return None
    features = state.attributes.get("supported_features")
    if (not isinstance(features, int) or isinstance(features, bool)
            or not 0 <= features <= 2**53 - 1 or not features & 4096):
        return None
    return state.state


def _media_playback_label(hass, state, language):
    locale = language or hass.config.language
    if state is None or state.state in {"unknown", "unavailable"}:
        return _state_subtitle(hass, state, locale)
    translated = _translate_state_for_locale(hass, state, locale)
    fallback = {"playing": ("Odtwarzanie", "Playing"), "paused": ("Pauza", "Paused"),
                "buffering": ("Buforowanie", "Buffering"), "idle": ("Bezczynny", "Idle"),
                "on": ("Włączony", "On"), "off": ("Wyłączony", "Off"),
                "standby": ("Czuwanie", "Standby")}
    return (translated if translated and translated != state.state
            else fallback.get(state.state, ("Nieznany", "Unknown"))[0 if display_language(locale) == "pl" else 1])


def _media_stop_caption(hass, state, language):
    locale = language or hass.config.language
    if state is None or state.state in {"unknown", "unavailable"}:
        return _state_subtitle(hass, state, locale)
    text = _media_playback_label(hass, state, locale)
    return fit_compact_caption(("Stan: " if display_language(locale) == "pl" else "State: ") + plain_text(text, 40))


def _media_stop_metadata(hass, state):
    power = _media_stop_state(state)
    if power is None or not hass.services.has_service("media_player", "media_stop"):
        return {}
    return {"media_stop": {"state": power, "features": state.attributes["supported_features"],
            "eligible": power in {"playing", "paused", "buffering"},
            "text": {language: _media_stop_caption(hass, state, language) for language in ("pl", "en")}}}


def _media_volume_value(state):
    if state is None or not state.entity_id.startswith("media_player.") or state.state not in {"on", "idle", "playing", "paused", "buffering"}:
        return None
    features, value = state.attributes.get("supported_features"), state.attributes.get("volume_level")
    return value if (isinstance(features, int) and not isinstance(features, bool) and 0 <= features <= 2**53 - 1
        and features & (4 | 1024) and type(value) in (int, float) and 0 <= value <= 1 and math.isfinite(value)) else None


def _media_volume_target_value(state):
    """Absolute volume requires VOLUME_SET; VOLUME_STEP alone is insufficient."""
    value = _media_volume_value(state)
    return value if value is not None and state.attributes["supported_features"] & 4 else None


def _media_volume_target_metadata(hass, state):
    value = _media_volume_target_value(state)
    return ({"media_volume_target": {"state": state.state, "features": state.attributes["supported_features"],
             "value": value, "text": {language: _media_volume_caption(hass, state, language) for language in ("pl", "en")}}}
            if value is not None and hass.services.has_service("media_player", "volume_set") else {})


def _media_volume_target_caption(hass, state, language):
    if state is not None and state.state in {"on", "idle", "playing", "paused", "buffering"} and _media_volume_target_value(state) is None:
        return state_label("unknown", language or hass.config.language)
    return _media_volume_caption(hass, state, language)


def _media_volume_operations(hass, state):
    value = _media_volume_value(state)
    if value is None:
        return ()
    return tuple(operation for operation in ("volume_up", "volume_down")
                 if hass.services.has_service("media_player", operation))


def _media_volume_caption(hass, state, language):
    locale = language or hass.config.language
    if state is None or state.state in {"unknown", "unavailable"}:
        return _state_subtitle(hass, state, locale)
    if state.state == "off":
        text = _translate_state_for_locale(hass, state, locale)
        return plain_text(text if text and text != state.state else ("Wyłączony" if display_language(locale) == "pl" else "Off"), 40)
    value = _media_volume_value(state)
    if value is None:
        return state_label("unknown", locale)
    percent = f"{value * 100:.1f}".rstrip("0").rstrip(".")
    if value > 0 and percent == "0":
        percent = "<0.1"
    elif value < 1 and percent == "100":
        percent = ">99.9"
    polish = display_language(locale) == "pl"
    return fit_compact_caption(("Głośn.: " if polish else "Volume: ") + (percent.replace(".", ",") if polish else percent) + " %")


def _media_volume_metadata(hass, state):
    value = _media_volume_value(state)
    operations = _media_volume_operations(hass, state)
    return ({"media_volume": {"state": state.state, "features": state.attributes["supported_features"], "value": value,
             "operations": list(operations), "text": {language: _media_volume_caption(hass, state, language) for language in ("pl", "en")}}}
            if value is not None and operations else {})


def _media_repeat_caption(hass, state, language):
    locale = language or hass.config.language
    if state is None or state.state in {"unknown", "unavailable"}:
        return _state_subtitle(hass, state, locale)
    try:
        choices = choice_domain(state.entity_id, state.attributes, "repeat")
        index = choices.observed_index(choice_state(state.entity_id, state.state, state.attributes, "repeat"))
        if index is not None:
            prefix = "Powt.: " if display_language(locale) == "pl" else "Repeat: "
            return fit_compact_caption(plain_text(prefix + choice_control_labels(hass, state, choices, "repeat", locale)[index], 40))
    except ChoiceDomainError:
        pass
    return state_label("unknown", locale)


def _media_source_caption(hass, state, language):
    locale = language or hass.config.language
    if state is None or state.state in {"unknown", "unavailable"}:
        return _state_subtitle(hass, state, locale)
    try:
        choices = choice_domain(state.entity_id, state.attributes, "source")
        index = choices.observed_index(choice_state(state.entity_id, state.state, state.attributes, "source"))
        if index is not None:
            return fit_compact_caption(plain_text(choice_control_labels(hass, state, choices, "source", locale)[index], 40))
    except ChoiceDomainError:
        pass
    return state_label("unknown", locale)


def _media_sound_mode_caption(hass, state, language):
    locale = language or hass.config.language
    if state is None or state.state in {"unknown", "unavailable"}:
        return _state_subtitle(hass, state, locale)
    try:
        choices = choice_domain(state.entity_id, state.attributes, "sound_mode")
        index = choices.observed_index(choice_state(state.entity_id, state.state, state.attributes, "sound_mode"))
        if index is not None:
            return fit_compact_caption(("Tryb: " if display_language(language or hass.config.language) == "pl" else "Sound: ") + plain_text(choice_control_labels(hass, state, choices, "sound_mode", locale)[index], 40))
    except ChoiceDomainError:
        pass
    return state_label("unknown", locale)


def _remote_power_allowed(state, operation):
    """Core Remote power needs no feature bit; only observed transitions apply."""
    return (isinstance(state, str) and (state, operation) in
            {("off", "turn_on"), ("on", "turn_off")})


def _remote_power_metadata(hass, state):
    if not state.entity_id.startswith("remote.") or state.state not in {"on", "off"}:
        return {}
    operations = [op for op in ("turn_on", "turn_off") if hass.services.has_service("remote", op)]
    return {"remote_power": {"state": state.state, "supported": operations}} if operations else {}


def _mower_actions_metadata(hass, state):
    if not state.entity_id.startswith("lawn_mower.") or state.state not in MOWER_ACTIVITIES:
        return {}
    operations = [operation for operation in mower_supported_operations(state.attributes)
        if hass.services.has_service("lawn_mower", operation)]
    if not operations:
        return {}
    return {"mower_actions": {"state": state.state, "features": state.attributes["supported_features"],
        "supported": operations, "eligible": [operation for operation in operations if mower_command_allowed(state.state, state.attributes, operation)]}}


def _vacuum_actions_metadata(hass, state):
    if not state.entity_id.startswith("vacuum.") or state.state not in VACUUM_ACTIVITIES:
        return {}
    operations = [operation for operation in vacuum_supported_operations(state.attributes)
        if hass.services.has_service("vacuum", operation)]
    if not operations:
        return {}
    return {"vacuum_actions": {"state": state.state, "features": state.attributes["supported_features"],
        "supported": operations, "eligible": [operation for operation in operations if vacuum_command_allowed(state.state, state.attributes, operation)]}}


def _vacuum_area_metadata(hass, state):
    if (not state.entity_id.startswith("vacuum.") or state.state not in VACUUM_ACTIVITIES
            or not has_area_capability(state.attributes) or not hass.services.has_service("vacuum", "clean_area")):
        return {}
    entry = async_get_entity_registry(hass).async_get(state.entity_id)
    area_registry = async_get_area_registry(hass)
    areas = []
    for area_id in mapped_area_ids(getattr(entry, "options", None)):
        if (area := area_registry.async_get_area(area_id)) is not None:
            areas.append({"id": area_id, "name": plain_text(area.name, 80)})
    if not areas:
        return {}
    return {"vacuum_area": {"state": state.state, "features": state.attributes["supported_features"], "areas": areas}}


def _choice_control_metadata(hass, state, property=None):
    domain = state.entity_id.partition(".")[0]
    if domain == "media_player" and state.state not in {"on", "idle", "playing", "paused", "buffering"}:
        return {}
    if domain == "remote" and state.state not in {"on", "off"}:
        return {}
    try:
        service, _ = choice_service(state.entity_id, property)
        if not hass.services.has_service(domain, service):
            return {}
        choices = choice_domain(state.entity_id, state.attributes, property, hass=hass)
    except ChoiceDomainError:
        return {}
    value = choice_state(state.entity_id, state.state, state.attributes, property)
    key = {"sound_mode": "media_sound_mode", "repeat": "media_repeat", "source": "media_source", "activity": "remote_activity", "fan_speed": "vacuum_fan_speed", "percentage": "fan_speed", "effect": "light_effect", "direction": "fan_direction", "hvac_mode": "climate_hvac_mode", "preset_mode": "climate_preset_mode", "fan_mode": "climate_fan_mode", "swing_mode": "climate_swing_mode", "swing_horizontal_mode": "climate_swing_horizontal_mode", "mode": "humidifier_mode"}.get(property, "choice_control")
    return {key: {"options": list(choices.options), "index": choices.observed_index(value),
                  **({"captions": {language: {"sound_mode": _media_sound_mode_caption, "repeat": _media_repeat_caption, "source": _media_source_caption}[property](hass, state, language) for language in ("pl", "en")}} if property in {"sound_mode", "repeat", "source"} else {}),
                  **({"speed_count": len(choices.options) - 1} if property == "percentage" else {}),
                  **({"empty": True} if choice_is_empty(state.entity_id, state.state, state.attributes, property) else {})}}


def _cover_control_metadata(hass, state):
    if state.entity_id.partition(".")[0] != "cover":
        return {}
    try:
        domain = CoverDomain.from_ha(state.attributes, {
            operation + "_cover": hass.services.has_service("cover", operation + "_cover")
            for operation in ("open", "stop", "close")
        })
    except CoverDomainError:
        return {}
    observed = CoverObservation.from_ha(state.state, state.attributes)
    return {"cover_control": {"caps": domain.descriptor(), "state": observed.state,
                              "position": observed.position, "available": observed.available}}


def _fan_control_metadata(hass, state):
    try:
        domain = FanDomain.from_ha(hass, state)
    except FanDomainError:
        return {}
    return {"fan_control": {"caps": domain.descriptor(), "state": FanObservation.from_ha(state, domain).descriptor()}}


def _cover_panel_metadata(hass, state):
    if not state.entity_id.startswith("cover."):
        return {}
    try:
        domain = CoverPanelDomain.from_ha(state.attributes, {
            name: hass.services.has_service("cover", name) for name in COVER_PANEL_SERVICES.values()
        })
    except CoverDomainError:
        return {}
    observed = CoverPanelObservation.from_ha(state.state, state.attributes)
    return {"cover_panel": {"version": 1, "device_class": domain.device_class,
            "caps": {name: domain.supports(name) for name in sorted(COVER_PANEL_OPERATIONS)},
            "state": {"cover_state": observed.state, "available": observed.available,
                      "position": observed.position, "tilt_position": observed.tilt_position}}}


def _panel_control_metadata(hass, state):
    if panel_type(state.entity_id) is None:
        return {}
    try:
        domain = PanelDomain.from_ha(hass, state)
        observed = PanelObservation.from_ha(state, domain)
    except PanelDomainError:
        return {}
    return {"panel_control": {"version": 1, "panel_type": domain.family, "caps": domain.descriptor(),
                              "state": observed.descriptor(), "available": observed.available,
                              "eligible_actions": observed.eligible(domain)}}


def _detail_control_metadata(hass, state, language=None):
    from .detail_domain import DetailDomain, DetailDomainError
    from .control_session import ProtocolError

    family = state.entity_id.partition(".")[0]
    if family not in {"light", "climate"} or family == "light" and state.state not in {"on", "off"}:
        return {}
    try:
        domain = DetailDomain.from_ha(hass, state, language)
    except (DetailDomainError, ProtocolError):
        return {}
    return {"light_detail" if family == "light" else "climate_panel": domain.metadata(state)}


def _robot_control_metadata(hass, state):
    try:
        domain = RobotDomain.from_ha(hass, state)
    except RobotDomainError:
        return {}
    return {"robot_control": {"version": 1, "robot_type": domain.robot_type,
            "caps": domain.descriptor(), "catalogue_fingerprint": domain.fingerprint,
            "area_reason": domain.area_reason, "state": RobotObservation.from_ha(state, domain).descriptor()}}


def _humidifier_control_metadata(hass, state):
    try:
        domain = HumidifierDomain.from_ha(hass, state)
    except HumidifierDomainError:
        return {}
    return {"humidifier_control": {"caps": domain.descriptor(), "humidity_domain": domain.numeric_descriptor(),
                                  "device_class": domain.device_class,
                                  "state": HumidifierObservation.from_ha(state, domain).descriptor()}}


def _fan_oscillation_metadata(hass, state):
    value = oscillation_value(state.entity_id, state.state, state.attributes)
    return ({"fan_oscillation": {"value": value}}
            if value is not None and hass.services.has_service("fan", "oscillate") else {})

CARD_CONTRACT_VERSION = 1
CARD_SLOT_COUNT = SLOT_COUNT
_TIMESTAMP_ACTION_DOMAINS = frozenset(("button", "input_button", "scene"))
_ACTION_AVAILABILITY_DOMAINS = frozenset(("input_button", "button", "scene", "script", "timer", "automation", "humidifier", "lawn_mower", "vacuum", "remote"))

ICONS = {
    "camera": "\ue04b",
    "vacuum": "\U000F070D",
    "mower": "\U000F11F7",
    "auto": "\ue1ff",  # Resolved from a validated binary sensor before projection.
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

# Resolved auto icons are not additional persisted icon choices.
_AUTO_ICON_GLYPHS = {"humidity": "\ue798"}  # Material Symbols water_drop.

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
        if slot < 0 or slot >= CAROUSEL_SLOT_COUNT:
            continue
        entity_id = plain_text(raw.get("entity_id"), 128)
        domain = entity_id.partition(".")[0]
        if entity_id and domain not in SUPPORTED_DOMAINS:
            continue
        icon = plain_text(raw.get("icon", "action"), 32)
        if icon == "auto" and not (raw.get("type") == "sensor" and domain == "binary_sensor"):
            icon = "action"
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
        for key in ("id", "type", "action", "state_color", "display_precision", "state_labels"):
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
    stock_fallback = domain in {"lawn_mower", "vacuum"} and state.state in {"error", "returning"} and display_language(language or hass.config.language) == "pl"
    if semantic_fallback is None and not stock_fallback and (
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
            translated = translations[key]
            # HA's stock Polish presence resources can fall back to Home/Away.
            # Entity-specific translations above retain their own authority.
            if (domain == "binary_sensor" and device_class == "presence" and display_language(language) == "pl"
                    and semantic_fallback is not None and translated in {"Home", "Away"}):
                return semantic_fallback
            return translated
    # A specific HA entity/device-class translation wins. If only a generic
    # on/off translation is cached, retain the known class's meaning instead.
    if semantic_fallback is not None:
        return semantic_fallback
    key = f"component.{domain}.entity_component._.state.{state.state}"
    translated = translations.get(key, state.state)
    # Stock Core2026.7 Polish mower resources retain these English fallbacks.
    # Specific entity/device-class translations above keep their precedence.
    if domain in {"lawn_mower", "vacuum"} and display_language(language) == "pl":
        # The generic Polish vacuum label is 179px, beyond the 136px caption.
        # Keep this compact semantic variant below entity-specific overrides.
        if domain == "vacuum" and state.state == "returning" and translated == "wraca do stacji dokującej":
            return "Powrót do bazy"
        fallback = {"error": ("Error", "Błąd"), "returning": ("Returning", "Powrót")}.get(state.state)
        if fallback and translated == fallback[0]:
            return fallback[1]
    return translated


def _choice_attribute_label(hass, state, attribute, value, language):
    """Core's attribute translation keys, using the display's selected locale."""
    language = (language or hass.config.language).replace("_", "-").split("-", 1)[0].lower()
    entry = async_get_entity_registry(hass).async_get(state.entity_id)
    platform, translation = getattr(entry, "platform", None), getattr(entry, "translation_key", None)
    entity_domain = state.entity_id.partition(".")[0]
    if platform is not None and translation is not None:
        key = f"component.{platform}.entity.{entity_domain}.{translation}.state_attributes.{attribute}.state.{value}"
        labels = async_get_cached_translations(hass, language, "entity")
        if key in labels:
            return labels[key]
    labels = async_get_cached_translations(hass, language, "entity_component")
    device_class = state.attributes.get("device_class")
    for kind in ((device_class, "_") if device_class is not None else ("_",)):
        key = f"component.{entity_domain}.entity_component.{kind}.state_attributes.{attribute}.state.{value}"
        if key in labels:
            return labels[key]
    return value


def choice_control_labels(hass, state, domain, property, language):
    """HA's cached entity translations are presentation, never command values."""
    fallback = choice_labels(domain, property, language)
    if property not in {"sound_mode", "repeat", "source", "fan_speed", "effect", "hvac_mode", "preset_mode", "fan_mode", "swing_mode", "swing_horizontal_mode", "mode"}:
        return fallback
    if property in {"sound_mode", "repeat", "source", "fan_speed", "effect", "preset_mode", "fan_mode", "swing_mode", "swing_horizontal_mode", "mode"}:
        labels = tuple(_choice_attribute_label(hass, state, property, value, language) for value in domain.options)
    else:
        labels = tuple(_translate_state_for_locale(hass, State(state.entity_id, value, state.attributes), language)
                       for value in domain.options)
    labels = tuple(fallback[index] if label == domain.options[index] else label for index, label in enumerate(labels))
    try:
        ChoiceDomain.from_options(list(labels))
    except ChoiceDomainError:
        return fallback
    return labels


def _state_subtitle(
    hass: HomeAssistant, state: State | None, language: str | None = None, *, precision: int | None = None
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
    if domain == "sensor" and attributes.get("device_class") == "date":
        return calendar_date_text(state.state, display_locale)
    if domain == "input_datetime":
        return datetime_helper_text(state.state, attributes, display_locale)
    if domain == "calendar":
        return calendar_event_text(state.state, attributes, display_locale)
    if domain == "person":
        return _person_subtitle(hass, state, display_locale)
    if (domain == "lawn_mower" and state.state in MOWER_ACTIVITIES
            or domain == "vacuum" and state.state in VACUUM_ACTIVITIES):
        translated = _translate_state_for_locale(hass, state, language)
        if translated and translated != state.state:
            return plain_text(translated, 40)
        polish = display_language(display_locale) == "pl"
        labels = {"docked": ("W bazie", "Docked"), "paused": ("Pauza", "Paused"), "mowing": ("Koszenie", "Mowing"), "cleaning": ("Sprzątanie", "Cleaning"), "idle": ("Bezczynny", "Idle"), "returning": ("Powrót", "Returning"), "error": ("Błąd", "Error")}
        return labels[state.state][0 if polish else 1]
    if domain == "input_text":
        if attributes.get("mode") != "text":
            return "Tekst ukryty" if display_language(display_locale) == "pl" else "Hidden text"
        return " ".join(state.state.split())[:40]
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
        # Card formatting never writes the entity registry or changes source units.
        # Duration/date/text classes retain their existing semantic formatter.
        if type(precision) is int and 0 <= precision <= MAX_PRECISION and attributes.get("device_class") != "duration":
            options = {"sensor": {"display_precision": precision}}
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
        if domain == "humidifier" and state.state in {"on", "off"}:
            polish = display_language(display_locale) == "pl"
            translated = ("Włączony" if state.state == "on" else "Wyłączony") if polish else state.state.title()
        else:
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
    if (state is not None and state.entity_id.startswith("input_text.")
            and state.state not in {"unknown", "unavailable"} and state.attributes.get("mode") != "text"):
        return "Tekst ukryty" if display_language(language or hass.config.language) == "pl" else "Hidden text"
    if state is not None and (mapped := mapped_label(card, state.state)) is not None:
        return mapped
    domain = card["entity_id"].partition(".")[0]
    if domain == "media_player" and card.get("action", {}).get("kind") == "service" and card["action"].get("service") == "media_player.media_stop":
        return _media_stop_caption(hass, state, language)
    if domain == "media_player" and card.get("action", {}).get("kind") == "service" and card["action"].get("service") == "media_player.volume_set":
        return _media_volume_target_caption(hass, state, language)
    if domain == "media_player" and card.get("action", {}).get("kind") == "service" and card["action"].get("service") in {"media_player.volume_up", "media_player.volume_down"}:
        return _media_volume_caption(hass, state, language)
    if domain == "media_player" and card.get("action", {}).get("kind") == "service" and card["action"].get("service") == "media_player.shuffle_set":
        return _media_shuffle_caption(hass, state, language)
    if domain == "media_player" and card.get("action", {}).get("kind") == "service" and card["action"].get("service") == "media_player.volume_mute":
        return _media_mute_caption(hass, state, language)
    if domain == "media_player" and card.get("action") == {"kind": "control", "control": "choice", "property": "repeat"}:
        return _media_repeat_caption(hass, state, language)
    if domain == "media_player" and card.get("action") == {"kind": "control", "control": "choice", "property": "sound_mode"}:
        return _media_sound_mode_caption(hass, state, language)
    if domain == "media_player" and card.get("action") == {"kind": "control", "control": "choice", "property": "source"}:
        return _media_source_caption(hass, state, language)
    if card.get("action") == {"kind": "control", "control": "choice", "property": "fan_speed"}:
        if state is None or state.state in {"unknown", "unavailable"}:
            return _state_subtitle(hass, state, language)
        try:
            choices = choice_domain(state.entity_id, state.attributes, "fan_speed")
            index = choices.observed_index(choice_state(state.entity_id, state.state, state.attributes, "fan_speed"))
            if index is not None:
                return choice_control_labels(hass, state, choices, "fan_speed", language or hass.config.language)[index]
        except ChoiceDomainError:
            pass
        return state_label("unknown", language or hass.config.language)
    if card.get("action") == {"kind": "control", "control": "choice", "property": "effect"}:
        if state is None or state.state in {"unknown", "unavailable"}:
            return _state_subtitle(hass, state, language)
        try:
            choices = choice_domain(state.entity_id, state.attributes, "effect")
            index = choices.observed_index(choice_state(state.entity_id, state.state, state.attributes, "effect"))
            if index is not None:
                return choice_control_labels(hass, state, choices, "effect", language or hass.config.language)[index]
            if choice_is_empty(state.entity_id, state.state, state.attributes, "effect"):
                return "Brak efektu" if display_language(language or hass.config.language) == "pl" else "No effect"
        except ChoiceDomainError:
            pass
        return state_label("unknown", language or hass.config.language)
    if card.get("action") in (TEMPERATURE_ACTION, HUMIDITY_ACTION, COLOR_TEMPERATURE_ACTION, COVER_POSITION_ACTION, COVER_TILT_ACTION):
        if state is None or state.state in {"unknown", "unavailable"}:
            return _state_subtitle(hass, state, language)
        try:
            property = card["action"]["property"]
            numeric = number_domain(hass, state, property)
            index = numeric.observed_index(number_state(state, property))
            if index is not None:
                polish = display_language(language or hass.config.language) == "pl"
                value = str(numeric.value_at(index))
                prefix = ("Pochylenie " if polish else "Tilt ") if property == "tilt_position" else ("Otwarcie " if polish else "Opening ") if property == "position" else "" if property == "color_temp_kelvin" else "Cel " if polish else "Target "
                return prefix + (value.replace(".", ",") if polish else value) + " " + numeric.unit
        except NumericDomainError:
            pass
        return state_label("unknown", language or hass.config.language)
    if card.get("action") == {"kind": "control", "control": "choice", "property": "hvac_mode"}:
        if state is None or state.state in {"unknown", "unavailable"}:
            return _state_subtitle(hass, state, language)
        try:
            domain = choice_domain(state.entity_id, state.attributes, "hvac_mode")
            index = domain.observed_index(choice_state(state.entity_id, state.state, state.attributes, "hvac_mode"))
            if index is not None:
                return choice_control_labels(hass, state, domain, "hvac_mode", language or hass.config.language)[index]
        except ChoiceDomainError:
            pass
        return state_label("unknown", language or hass.config.language)
    if card.get("action") == {"kind": "control", "control": "choice", "property": "preset_mode"}:
        if state is None or state.state in {"unknown", "unavailable"}:
            return _state_subtitle(hass, state, language)
        try:
            domain = choice_domain(state.entity_id, state.attributes, "preset_mode")
            index = domain.observed_index(choice_state(state.entity_id, state.state, state.attributes, "preset_mode"))
            if index is not None:
                return choice_control_labels(hass, state, domain, "preset_mode", language or hass.config.language)[index]
            if choice_is_empty(state.entity_id, state.state, state.attributes, "preset_mode"):
                return "Bez programu" if display_language(language or hass.config.language) == "pl" else "No program"
        except ChoiceDomainError:
            pass
        return state_label("unknown", language or hass.config.language)
    if card.get("action") == {"kind": "control", "control": "choice", "property": "fan_mode"}:
        if state is None or state.state in {"unknown", "unavailable"}:
            return _state_subtitle(hass, state, language)
        try:
            domain = choice_domain(state.entity_id, state.attributes, "fan_mode")
            index = domain.observed_index(choice_state(state.entity_id, state.state, state.attributes, "fan_mode"))
            if index is not None:
                return choice_control_labels(hass, state, domain, "fan_mode", language or hass.config.language)[index]
        except ChoiceDomainError:
            pass
        return state_label("unknown", language or hass.config.language)
    if card.get("action") == {"kind": "control", "control": "choice", "property": "swing_mode"}:
        if state is None or state.state in {"unknown", "unavailable"}:
            return _state_subtitle(hass, state, language)
        try:
            domain = choice_domain(state.entity_id, state.attributes, "swing_mode")
            index = domain.observed_index(choice_state(state.entity_id, state.state, state.attributes, "swing_mode"))
            if index is not None:
                return choice_control_labels(hass, state, domain, "swing_mode", language or hass.config.language)[index]
        except ChoiceDomainError:
            pass
        return state_label("unknown", language or hass.config.language)
    if card.get("action") == {"kind": "control", "control": "choice", "property": "swing_horizontal_mode"}:
        if state is None or state.state in {"unknown", "unavailable"}:
            return _state_subtitle(hass, state, language)
        try:
            domain = choice_domain(state.entity_id, state.attributes, "swing_horizontal_mode")
            index = domain.observed_index(choice_state(state.entity_id, state.state, state.attributes, "swing_horizontal_mode"))
            if index is not None:
                return choice_control_labels(hass, state, domain, "swing_horizontal_mode", language or hass.config.language)[index]
        except ChoiceDomainError:
            pass
        return state_label("unknown", language or hass.config.language)
    if card.get("action") == {"kind": "control", "control": "choice", "property": "mode"}:
        if state is None or state.state in {"unknown", "unavailable"}:
            return _state_subtitle(hass, state, language)
        try:
            domain = choice_domain(state.entity_id, state.attributes, "mode")
            index = domain.observed_index(choice_state(state.entity_id, state.state, state.attributes, "mode"))
            if index is not None:
                return choice_control_labels(hass, state, domain, "mode", language or hass.config.language)[index]
        except ChoiceDomainError:
            pass
        return state_label("unknown", language or hass.config.language)
    if card.get("action") == {"kind": "fan_oscillation"}:
        value = oscillation_value(state.entity_id, state.state, state.attributes) if state is not None else None
        if value is None:
            return state_label("unavailable" if state is None or state.state == "unavailable" else "unknown", language or hass.config.language)
        polish = display_language(language or hass.config.language) == "pl"
        return ("Oscylacja wł." if value else "Oscylacja wył.") if polish else ("Oscillation: on" if value else "Oscillation: off")
    if domain == "fan" and card.get("action", {}).get("kind") == "control" and card["action"].get("control") == "choice":
        if state is None or state.state in {"unknown", "unavailable"}:
            return _state_subtitle(hass, state, language)
        try:
            property = card["action"].get("property")
            choices = choice_domain(state.entity_id, state.attributes, property, hass=hass)
            value = choice_state(state.entity_id, state.state, state.attributes, property)
            index = choices.observed_index(value)
            if index is not None:
                return plain_text(choice_labels(choices, property, language or hass.config.language)[index], 40)
            if choice_is_empty(state.entity_id, state.state, state.attributes, property):
                return "Tryb ręczny" if display_language(language or hass.config.language) == "pl" else "Manual mode"
        except ChoiceDomainError:
            pass
        return state_label("unknown", language or hass.config.language)
    if domain == "automation":
        action = resolve_action(hass, card)
        if action is not None and action.domain == "automation":
            labels = {"turn_on": ("Enable", "Włącz"), "turn_off": ("Disable", "Wyłącz"), "trigger": ("Run", "Uruchom")}
            if action.service in labels:
                return labels[action.service][display_language(language or hass.config.language) == "pl"]
    if domain == "timer" and card.get("action", {}).get("kind") == "service":
        action = resolve_action(hass, card)
        if action is not None and action.domain == "timer":
            polish = display_language(language or hass.config.language) == "pl"
            if action.service == "cancel":
                return "Anuluj" if polish else "Cancel"
            if action.service == "start" and "duration" in action.data:
                seconds = int(action.data["duration"])
                minutes, seconds = divmod(seconds, 60)
                hours, minutes_in_hour = divmod(minutes, 60)
                duration = f"{hours}:{minutes_in_hour:02}:{seconds:02}" if hours else f"{minutes}:{seconds:02}"
                return ("Uruchom " if polish else "Start ") + duration
    if domain == "timer" and card.get("action", {"kind": "default"}) == {"kind": "default"} and not card.get("service"):
        action = resolve_action(hass, card)
        if action is not None and action.domain == "timer":
            polish = display_language(language or hass.config.language) == "pl"
            labels = {"idle": ("Start", "Uruchom"), "active": ("Pause", "Wstrzymaj"), "paused": ("Resume", "Wznów")}
            return labels[state.state][polish]
    if (domain in _TIMESTAMP_ACTION_DOMAINS
            and card.get("action") == {"kind": "control", "control": "panel", "property": "action"}
            and _state_allows_action(state)):
        # This tap opens a view; the entity timestamp is history inside that view.
        return "Otwórz" if display_language(language or hass.config.language) == "pl" else "Open"
    if domain in _TIMESTAMP_ACTION_DOMAINS or domain == "script":
        action = resolve_action(hass, card)
        polish = display_language(language or hass.config.language) == "pl"
        if action is not None:
            if domain in {"button", "input_button"} and action.domain == domain and action.service == "press":
                return "Naciśnij" if polish else "Press"
            if domain in {"scene", "script"} and action.domain in {domain, "homeassistant"} and action.service == "turn_on":
                return "Uruchom" if polish else "Run"
    precision = card.get("display_precision") if card.get("type") == "sensor" and domain in PRECISION_DOMAINS else None
    return _state_subtitle(hass, state, language, precision=precision)


def ordinary_action_availability(card: dict[str, Any]) -> bool:
    """Whether a card participates in negotiated ordinary-action availability.

    Execution eligibility remains the live resolver's responsibility.
    """
    return is_camera_preview_card(card) or (card["entity_id"].startswith("media_player.") and card.get("action", {}).get("kind") == "service" and card["action"].get("service") in {"media_player.volume_set", "media_player.media_stop", "media_player.volume_mute", "media_player.shuffle_set", "media_player.volume_up", "media_player.volume_down"}) or is_event_card(card, visible_only=False) or card.get("action") == {"kind": "fan_oscillation"} or (card["entity_id"].partition(".")[0] in _ACTION_AVAILABILITY_DOMAINS
            and card.get("action", {}).get("kind") != "control")


def presentation_icon(card: dict[str, Any], state: State | None) -> str:
    """Resolve explicit automatic binary icons from the HA device class."""
    if card.get("icon") != "auto":
        return ICONS[card["icon"]]
    device_class = state.attributes.get("device_class") if state is not None else None
    if isinstance(device_class, str):
        if device_class in {"door", "window", "opening", "garage_door"}:
            return ICONS["door"]
        if device_class in {"motion", "occupancy", "presence"}:
            return ICONS["presence"]
        if device_class == "moisture":
            return _AUTO_ICON_GLYPHS["humidity"]
    return ICONS["sensor"]


def presentation_palette(card: dict[str, Any], state: State | None) -> str:
    """An explicit active-state style changes a role, never palette ownership."""
    active = state is not None and state.state == "on"
    if card["entity_id"].startswith("person."):
        active = state is not None and state.state == "home"
    if card.get("action") == {"kind": "fan_oscillation"}:
        active = state is not None and oscillation_value(state.entity_id, state.state, state.attributes) is True
    if (card.get("state_color") is True and supports_state_color(card.get("type"), card["entity_id"])
            and not active):
        return "surface"
    return card["palette"]


def presentation_payload(
    hass: HomeAssistant,
    cards: list[dict[str, Any]],
    accent_color: Any = "36BCF0",
    language: str | None = None,
    *, light_control_supported: bool = False, number_control_supported: bool = False,
    choice_control_supported: bool = False, cover_control_supported: bool = False,
    cover_panel_supported: bool = False,
    fan_control_supported: bool = False, humidifier_control_supported: bool = False,
    robot_control_supported: bool = False, panel_types: tuple[str, ...] = (),
    light_detail_supported: bool = False, climate_panel_supported: bool = False,
    panel_extra_profiles: tuple[str, ...] = (), info_agenda_supported: bool = False, info_statistics_supported: bool = False, action_parameters_supported: bool = False,
    thermostat_supported: bool = False,
    press_enabled_supported: bool = False,
    camera_preview_entities: tuple[str, ...] = (),
    event_press_supported: bool = False, event_card_ids=None, slot_count: int = CARD_SLOT_COUNT,
) -> dict[str, Any]:
    """Build the compact payload consumed by the fixed LVGL object pool."""
    accent = normalize_accent(accent_color)
    palettes = derive_palette(accent)
    rendered: list[dict[str, Any]] = []
    by_slot = {card["slot"]: card for card in cards}
    for slot in range(slot_count):
        card = by_slot.get(slot)
        if card is None:
            # Firmware leaves omitted bindings untouched. Explicitly hide
            # every unassigned slot so moves/removals cannot retain stale UI.
            rendered.append({"slot": slot, "id": "", "visible": False})
            continue
        state = hass.states.get(card["entity_id"]) if card["entity_id"] else None
        palette = presentation_palette(card, state)
        background, foreground = palettes[palette]
        rendered.append(
            {
                "slot": card["slot"],
                "id": card.get("id", ""),
                "visible": card["visible"] and slot >= 2,
                "icon": presentation_icon(card, state),
                "title": card["title"],
                "subtitle": _card_subtitle(hass, card, state, language),
                # Keep the role in the wire contract.  The embedded renderer
                # derives the actual colors from the current accent seed.
                "palette": palette,
                "background": background,
                "foreground": foreground,
            }
        )
        if is_camera_preview_card(card):
            eligible = bool(press_enabled_supported and card["entity_id"] in camera_preview_entities and rendered[-1]["visible"])
            polish = display_language(language or hass.config.language) == "pl"
            rendered[-1]["subtitle"] = (("Otwórz" if polish else "Open") if eligible
                                         else ("Niedostępna" if polish else "Unavailable"))
            if press_enabled_supported:
                rendered[-1]["press_enabled"] = eligible
        elif is_event_card(card, visible_only=False):
            eligible = bool(event_press_supported and card["id"] in (event_card_ids or ()) and rendered[-1]["visible"])
            polish = display_language(language or hass.config.language) == "pl"
            rendered[-1]["subtitle"] = (("Automatyzacja" if polish else "Automation") if eligible
                                         else ("Przycisk niedostępny" if polish else "Button unavailable"))
            if press_enabled_supported:
                rendered[-1]["press_enabled"] = eligible
        elif is_event_panel(card, visible_only=False):
            supported = ("action" in panel_extra_profiles and "tile_event" in panel_extra_profiles
                         and card["id"] in (event_card_ids or ()) and rendered[-1]["visible"])
            polish = display_language(language or hass.config.language) == "pl"
            rendered[-1]["subtitle"] = ("Otwórz" if polish else "Open") if supported else ("Urządzenie bez obsługi" if polish else "Unsupported device")
            if supported:
                rendered[-1]["control_kind"] = "panel"
            elif press_enabled_supported:
                rendered[-1]["press_enabled"] = False
        elif card.get("action", {}).get("kind") == "control":
            control = card["action"].get("control")
            supported = {"light": light_control_supported, "number": number_control_supported,
                         "choice": choice_control_supported, "cover": cover_control_supported,
                         "fan": fan_control_supported, "humidifier": humidifier_control_supported,
                         "robot": robot_control_supported, "panel": card["action"].get("property") in panel_types}.get(control, False)
            detail_profile = card["action"] == {"kind": "control", "control": "light", "detail": 1}
            climate_profile = card["action"] == {"kind": "control", "control": "panel", "property": "climate"}
            extra_profile = control == "panel" and card["action"].get("property") in {"info", "lock", "media", "action", "datetime", "text", "agenda", "statistics"}
            if card["action"] == PARAMETERS_ACTION:
                supported = action_parameters_supported and state is not None and bool(action_parameters_metadata(hass, state))
            elif card["action"].get("property") == "statistics":
                supported = info_statistics_supported and state is not None and bool(statistics_metadata(hass, state))
            elif card["action"].get("property") == "agenda":
                supported = info_agenda_supported and state is not None and bool(agenda_metadata(hass, state))
            elif extra_profile:
                supported = (card["action"]["property"] in panel_extra_profiles
                             and state is not None and bool(({"media": media_metadata, "action": action_metadata, "datetime": datetime_metadata, "text": text_metadata}.get(card["action"]["property"], extra_metadata))(hass, state, language)))
                if card["action"]["property"] == "info" and card["entity_id"].partition(".")[0] in CONTEXT_INFO_TYPES:
                    supported = supported and "info_context" in panel_extra_profiles
            if detail_profile or climate_profile:
                supported = ((light_detail_supported if detail_profile else climate_panel_supported)
                             and state is not None and bool(_detail_control_metadata(hass, state, language)))
            unavailable_choice = (control == "choice" and supported and
                                  (state is None or not _choice_control_metadata(hass, state, card["action"].get("property"))))
            unavailable_cover = (control == "cover" and supported and
                                 (state is None or not (_cover_panel_metadata if cover_panel_supported else _cover_control_metadata)(hass, state)))
            unavailable_fan = (control == "fan" and supported and
                               (state is None or not _fan_control_metadata(hass, state)))
            unavailable_humidifier = (control == "humidifier" and supported and
                                      (state is None or not _humidifier_control_metadata(hass, state)))
            unavailable_panel = (control == "panel" and not climate_profile and not extra_profile and supported and
                                 (state is None or not _panel_control_metadata(hass, state)))
            unavailable_robot = (control == "robot" and supported and
                                 (state is None or not _robot_control_metadata(hass, state)))
            unavailable_temperature = (card["action"] in (TEMPERATURE_ACTION, HUMIDITY_ACTION, COLOR_TEMPERATURE_ACTION, COVER_POSITION_ACTION, COVER_TILT_ACTION) and supported and
                                       (state is None or not _number_control_metadata(hass, state, card["action"]["property"])))
            if unavailable_temperature and thermostat_supported and card["action"] == TEMPERATURE_ACTION and state is not None:
                if view := thermostat_snapshot(hass, state):
                    unavailable_temperature = False
                    if target := view["target"]:
                        polish = display_language(language or hass.config.language) == "pl"
                        target = target.replace(".", ",") if polish else target
                        rendered[-1]["subtitle"] = f"{'Cel' if polish else 'Target'} {target} {view['unit']}"
            supported = supported and not unavailable_choice and not unavailable_cover and not unavailable_fan and not unavailable_humidifier and not unavailable_robot and not unavailable_panel and not unavailable_temperature
            if supported and rendered[-1]["visible"]:
                rendered[-1]["control_kind"] = control
                if detail_profile:
                    rendered[-1]["control_detail_version"] = 1
            else:
                rendered[-1]["subtitle"] = ("Urządzenie bez obsługi" if display_language(language or hass.config.language) == "pl"
                                             else "Unsupported device")
                if unavailable_choice:
                    rendered[-1]["subtitle"] = ("Opcje niedostępne" if display_language(language or hass.config.language) == "pl"
                                                 else "Options unavailable")
                if unavailable_temperature:
                    rendered[-1]["subtitle"] = ("Nastawa niedostępna" if display_language(language or hass.config.language) == "pl" else "Target unavailable")
                if (control in {"choice", "cover", "fan", "humidifier", "robot", "panel"} or unavailable_temperature or detail_profile) and press_enabled_supported:
                    rendered[-1]["press_enabled"] = False
        elif press_enabled_supported is True and ordinary_action_availability(card):
            # Action availability is HA policy, not a service-result acknowledgement.
            rendered[-1]["press_enabled"] = resolve_action(hass, card) is not None
        if slot >= SLOT_COUNT:
            row = rendered[-1]
            action = card["action"]
            subtitle = row["subtitle"]
            if state is not None and action in (COVER_POSITION_ACTION, COVER_TILT_ACTION):
                attribute = "current_position" if action == COVER_POSITION_ACTION else "current_tilt_position"
                value = state.attributes.get(attribute)
                if type(value) in (int, float) and 0 <= value <= 100:
                    subtitle = f"{value:g} %"
            elif state is not None and action.get("service") == "media_player.media_play_pause":
                subtitle = _media_playback_label(hass, state, language)
            row["title"] = fit_caption(row["title"], 100)
            row["subtitle"] = fit_caption(subtitle, 100)
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
    if domain in {"sun", "input_datetime", "calendar", "person", "camera"}:
        return None  # Passive data only, including raw/legacy configured service attempts.
    state = hass.states.get(entity_id)
    if not _state_allows_action(state):
        return None
    if domain == "automation" and state.state not in {"on", "off"}:
        return None
    if domain == "humidifier" and state.state not in {"on", "off"}:
        return None
    configured = card.get("action")
    if configured is None:
        configured = ({"kind": "service", "service": card["service"], "data": {}}
                      if card.get("service") else {"kind": "default"})
    try:
        action = validate_action(configured, entity_id, layout_version=3)
        if card.get("type") == "sensor" or action["kind"] in {"none", "control", "event"}:
            return None
        if action["kind"] == "fan_oscillation":
            value = oscillation_value(entity_id, state.state, state.attributes)
            if value is None:
                return None
            action = {"kind": "service", "service": "fan.oscillate", "data": {"oscillating": not value}}
        if action["kind"] == "default":
            data = {}
            if domain in {"button", "input_button"}:
                service = f"{domain}.press"
            elif domain in {"scene", "script"}:
                service = f"{domain}.turn_on"
            elif domain in {"light", "switch", "input_boolean", "fan"}:
                service = f"{domain}.toggle"
            elif domain == "humidifier":
                service = "humidifier.turn_off" if state.state == "on" else "humidifier.turn_on"
            elif domain == "automation":
                # Enable/disable future triggers; never infer running its actions.
                # Let an already-running sequence finish when disabling by default.
                service = "automation.turn_off" if state.state == "on" else "automation.turn_on"
                data = {"stop_actions": False} if state.state == "on" else {}
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
            action = {"kind": "service", "service": service, "data": data}
        if domain == "media_player" and action["service"] == "media_player.volume_set":
            current = _media_volume_target_value(state)
            if current is None or current == action["data"]["volume_level"]:
                return None
        if domain == "media_player" and action["service"] == "media_player.media_stop" and _media_stop_state(state) not in {"playing", "paused", "buffering"}:
            return None
        if domain == "media_player" and action["service"] in {"media_player.volume_up", "media_player.volume_down"}:
            operation = action["service"].split(".", 1)[1]
            volume = _media_volume_value(state)
            if (operation not in _media_volume_operations(hass, state) or volume is None
                    or operation == "volume_up" and volume >= 1 or operation == "volume_down" and volume <= 0):
                return None
        if domain == "media_player" and action["service"] == "media_player.shuffle_set":
            current = _media_shuffle_value(state)
            if current is None or current is action["data"]["shuffle"]:
                return None
        if domain == "media_player" and action["service"] == "media_player.volume_mute":
            current = _media_mute_value(state)
            if current is None or current is action["data"]["is_volume_muted"]:
                return None
        if domain == "remote":
            action_domain, _, operation = action["service"].partition(".")
            if action_domain != "remote" or not _remote_power_allowed(state.state, operation):
                return None
        if domain == "lawn_mower":
            action_domain, _, operation = action["service"].partition(".")
            if action_domain != "lawn_mower" or not mower_command_allowed(state.state, state.attributes, operation):
                return None
        if domain == "vacuum" and action["service"] == "vacuum.clean_area":
            if not area_command_allowed(state.state, state.attributes):
                return None
        elif domain == "vacuum" and action["service"] != "vacuum.set_fan_speed":
            action_domain, _, operation = action["service"].partition(".")
            if action_domain != "vacuum" or not vacuum_command_allowed(state.state, state.attributes, operation):
                return None
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
    if domain in {"humidifier", "remote"} and state.state not in {"on", "off"}:
        return []
    if domain in {"sun", "input_datetime", "calendar", "person"}:
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
        "set_percentage": 1, "oscillate": 2, "set_direction": 4, "set_preset_mode": 1 | 8,
        "turn_off": 16, "turn_on": 32, "toggle": 16 if state.state == "on" else 32,
    }
    climate_features = {"set_humidity": 4, "set_preset_mode": 16, "set_fan_mode": 8, "set_swing_mode": 32, "set_swing_horizontal_mode": 512}
    media_features = {
        "volume_set": 4, "volume_up": 4 | 1024, "volume_down": 4 | 1024, "shuffle_set": 32768, "repeat_set": 262144, "select_source": 2048, "select_sound_mode": 65536, "volume_mute": 8, "media_pause": 1, "media_play": 16384, "media_previous_track": 16,
        "media_next_track": 32, "media_stop": 4096, "turn_on": 128, "turn_off": 256,
        "media_play_pause": 1 if state.state == "playing" else 16384,
    }
    vacuum_features = {
        "set_fan_speed": 32,
        "clean_area": 16384,
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
        if domain == "humidifier" and service == "set_mode" and not features & 1:
            continue
        feature_gate = {
            "media_player": media_features, "vacuum": vacuum_features,
            "lawn_mower": mower_features,
        }.get(domain)
        if feature_gate is not None and not features & feature_gate.get(service, 0):
            continue
        if domain == "vacuum" and service in vacuum_features and service not in {"set_fan_speed", "clean_area"} and service not in vacuum_supported_operations(attrs):
            continue
        if full_service == "media_player.volume_set" and _media_volume_target_value(state) is None:
            continue
        if full_service == "media_player.media_stop" and _media_stop_state(state) is None:
            continue
        if full_service in {"media_player.volume_up", "media_player.volume_down"} and service not in _media_volume_operations(hass, state):
            continue
        if full_service == "media_player.shuffle_set" and _media_shuffle_value(state) is None:
            continue
        if full_service == "media_player.volume_mute" and _media_mute_value(state) is None:
            continue
        fields = deepcopy(ACTION_FIELDS.get(full_service, {}))
        if full_service == "media_player.repeat_set" and not _choice_control_metadata(hass, state, "repeat"):
            continue
        if full_service == "media_player.select_sound_mode":
            meta = _choice_control_metadata(hass, state, "sound_mode").get("media_sound_mode")
            if meta is None:
                continue
            fields["sound_mode"] = {"type": "select", "required": True, "options": meta["options"]}
        if full_service == "media_player.select_source":
            meta = _choice_control_metadata(hass, state, "source").get("media_source")
            if meta is None:
                continue
            fields["source"] = {"type": "select", "required": True, "options": meta["options"]}
        if full_service == "vacuum.clean_area":
            meta = _vacuum_area_metadata(hass, state).get("vacuum_area")
            if meta is None:
                continue
            fields["cleaning_area_id"] = {"type": "select", "required": True,
                "options": [area["id"] for area in meta["areas"]], "option_labels": [area["name"] for area in meta["areas"]]}
        if domain == "light" and service == "turn_on":
            raw_modes = attrs.get("supported_color_modes")
            modes = (set(raw_modes) if isinstance(raw_modes, (list, tuple, set, frozenset))
                     and all(isinstance(mode, str) for mode in raw_modes) else set())
            if not modes - {"onoff", "unknown"}:
                fields.pop("brightness_pct", None)
            if "color_temp" not in modes:
                fields.pop("color_temp_kelvin", None)
            else:
                try:
                    descriptor = color_temperature_domain(attrs).descriptor()
                except NumericDomainError:
                    fields.pop("color_temp_kelvin", None)
                else:
                    fields["color_temp_kelvin"].update(min=int(descriptor["min"]), max=int(descriptor["max"]), step=1)
            if not modes.intersection({"rgb", "rgbw", "rgbww", "hs", "xy"}):
                fields.pop("rgb_color", None)
            # An optional effect must not remove ordinary power/brightness
            # control when the light has no effect catalogue.
            effect_features = attrs.get("supported_features")
            effects = attrs.get("effect_list")
            if (isinstance(effect_features, int) and not isinstance(effect_features, bool)
                    and effect_features >= 0 and effect_features & 4 and isinstance(effects, (list, tuple))):
                options = [value for value in effects if isinstance(value, str) and 0 < len(value) <= 128][:128]
            else:
                options = []
            if options:
                fields["effect"] = {"type": "select", "options": options, "required": False}
            else:
                fields.pop("effect", None)
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
        if full_service in {"humidifier.set_humidity", "climate.set_humidity"}:
            try:
                descriptor = humidity_domain(attrs).descriptor()
            except NumericDomainError:
                continue
            fields["humidity"].update(min=int(descriptor["min"]), max=int(descriptor["max"]),
                                      step=int(descriptor["step"]))
        option_fields = {
            "vacuum.set_fan_speed": ("fan_speed", "fan_speed_list"),
            "select.select_option": ("option", "options"),
            "input_select.select_option": ("option", "options"),
            "fan.set_preset_mode": ("preset_mode", "preset_modes"),
            "climate.set_hvac_mode": ("hvac_mode", "hvac_modes"),
            "climate.set_preset_mode": ("preset_mode", "preset_modes"),
            "climate.set_fan_mode": ("fan_mode", "fan_modes"),
            "humidifier.set_mode": ("mode", "available_modes"),
            "climate.set_swing_mode": ("swing_mode", "swing_modes"),
            "climate.set_swing_horizontal_mode": ("swing_horizontal_mode", "swing_horizontal_modes"),
        }
        if full_service in option_fields:
            field, attribute = option_fields[full_service]
            options = attrs.get(attribute)
            if not isinstance(options, (list, tuple)):
                continue
            choices = [value for value in options
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
    # Activity is authorized only by the explicit Choice path: static service
    # cards still reject all activity data. Recheck the exact live catalogue.
    if service == "remote.turn_on" and state.entity_id.startswith("remote.") and set(action["data"]) == {"activity"}:
        try:
            domain = choice_domain(state.entity_id, state.attributes, "activity")
        except ChoiceDomainError:
            raise LayoutError("unsupported_action", "Remote activities are unavailable") from None
        value = action["data"]["activity"]
        if (state.state not in {"on", "off"} or not hass.services.has_service("remote", "turn_on")
                or not isinstance(value, str) or value not in domain.options):
            raise LayoutError("unsupported_action", "Remote activity is not currently supported")
        return
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
                     limit: int = 200, area_id: str | None = None, *, camera_entity_ids=()) -> dict[str, Any]:
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
        if domain == "camera" and state.entity_id not in camera_entity_ids:
            continue
        if domain == "input_text" and state.attributes.get("mode") != "text":
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
            **({"camera_preview": {"allowlisted": True, "min_duration": 15, "max_duration": 90}}
               if state.entity_id.startswith("camera.") else {}),
            **_calendar_next_metadata(state),
            **_person_presence_metadata(hass, state),
            **_mower_actions_metadata(hass, state),
            **_vacuum_actions_metadata(hass, state),
            **_remote_power_metadata(hass, state),
            **_media_mute_metadata(hass, state),
            **_media_shuffle_metadata(hass, state),
            **_media_volume_metadata(hass, state),
            **_media_volume_target_metadata(hass, state),
            **_media_stop_metadata(hass, state),
            **_vacuum_area_metadata(hass, state),
            **_number_control_metadata(hass, state),
            **_number_control_metadata(hass, state, "temperature"),
            **_number_control_metadata(hass, state, "humidity"),
            **_number_control_metadata(hass, state, "color_temp_kelvin"),
            **_number_control_metadata(hass, state, "position"),
            **_number_control_metadata(hass, state, "tilt_position"),
            **_choice_control_metadata(hass, state),
            **_choice_control_metadata(hass, state, "direction"),
            **_choice_control_metadata(hass, state, "percentage"),
            **_choice_control_metadata(hass, state, "hvac_mode"),
            **_choice_control_metadata(hass, state, "preset_mode"),
            **_choice_control_metadata(hass, state, "fan_mode"),
            **_choice_control_metadata(hass, state, "swing_mode"),
            **_choice_control_metadata(hass, state, "swing_horizontal_mode"),
            **_choice_control_metadata(hass, state, "mode"),
            **_choice_control_metadata(hass, state, "effect"),
            **_choice_control_metadata(hass, state, "fan_speed"),
            **_choice_control_metadata(hass, state, "activity"),
            **_choice_control_metadata(hass, state, "source"),
            **_choice_control_metadata(hass, state, "sound_mode"),
            **_choice_control_metadata(hass, state, "repeat"),
            **_fan_oscillation_metadata(hass, state),
            **_fan_control_metadata(hass, state),
            **_humidifier_control_metadata(hass, state),
            **_robot_control_metadata(hass, state),
            **_panel_control_metadata(hass, state),
            **extra_metadata(hass, state),
            **agenda_metadata(hass, state),
            **statistics_metadata(hass, state),
            **media_metadata(hass, state),
            **action_metadata(hass, state),
            **action_parameters_metadata(hass, state),
            **datetime_metadata(hass, state),
            **text_metadata(hass, state),
            **_detail_control_metadata(hass, state),
            **_cover_control_metadata(hass, state),
            **_cover_panel_metadata(hass, state),
        } for state, assigned, area_name in matches[:limit]],
        "total": len(matches), "truncated": len(matches) > limit,
        # Stable facets precede all filters/limits and never enumerate registry
        # entries missing from runtime states. Bound response size explicitly.
        "areas": facets[:500], "area_total": len(facets), "areas_truncated": len(facets) > 500,
    }
