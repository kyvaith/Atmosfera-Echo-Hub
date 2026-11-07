"""Bounded Home Assistant layout model; no Home Assistant runtime dependency."""

from __future__ import annotations

from copy import deepcopy
import json
import math
import re
from typing import Any

from .text import plain_text
from .formatting import MAX_PRECISION
from .state_labels import eligible as state_labels_eligible, validate_labels

LAYOUT_VERSION = 2
CONTROL_LAYOUT_VERSION = 3
SUPPORTED_LAYOUT_VERSIONS = (LAYOUT_VERSION, CONTROL_LAYOUT_VERSION)
PROFILE_ID = "echo-hub-m3-v1"
SLOT_COUNT = 16
CAROUSEL_SLOT_COUNT = 32
HOME_ORDER = ("home-1", "home-2", "home-3", "home-4", "home-5")
MAX_DOCUMENT_BYTES = 32768
MAX_REVISION = 2**53 - 1
CARD_TYPES = ("entity", "sensor", "action")
STATE_COLOR_DOMAINS = frozenset(("light", "switch", "input_boolean", "fan", "humidifier"))
PRECISION_DOMAINS = frozenset(("sensor", "number", "input_number"))
ICON_NAMES = frozenset(
    ("action", "auto", "alarm", "climate", "cover", "fan", "light", "lock", "scene",
     "speed", "switch", "sensor", "door", "presence", "clock", "webhook", "vacuum", "mower", "camera")
)
PALETTE_NAMES = frozenset(
    ("primary", "primary_container", "secondary", "surface", "tertiary")
)
SUPPORTED_DOMAINS = frozenset(
    ("alarm_control_panel", "automation", "binary_sensor", "button", "calendar", "camera", "climate",
     "cover", "fan", "humidifier", "input_boolean", "input_button", "input_datetime", "input_number", "input_text",
     "input_select", "light", "lock", "media_player", "number", "scene",
     "script", "select", "sensor", "sun", "switch", "timer", "vacuum", "lawn_mower", "person", "remote")
)
# Product-owned text geometry: large-value Roboto34 places cannot fit Sun captions.
SUN_TEXT_SLOTS = tuple(slot for slot in range(2, SLOT_COUNT) if slot not in (13, 14))
# A helper may switch to a 19-character combined value at runtime. Admission
# follows the caption width, not the outer tile: 136/148px captions clip it.
DATETIME_TEXT_SLOTS = (3, 5, 8, 9, 10, 11, 12)
# Forty-character event captions need the existing widest information row.
CALENDAR_TEXT_SLOTS = (12,)
# Custom zone names can fill the same forty-character caption as a Calendar.
PERSON_TEXT_SLOTS = (12,)
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_ENTITY = re.compile(r"^[a-z_][a-z0-9_]*\.[a-z0-9_]+$")
_SERVICE = re.compile(r"^[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*$")


def supports_state_color(card_type: str | None, entity_id: str) -> bool:
    domain = entity_id.partition(".")[0]
    return ((card_type == "entity" and domain in STATE_COLOR_DOMAINS)
            or (card_type in {"entity", "action"} and domain == "automation")
            or (card_type == "sensor" and domain in {"binary_sensor", "person"}))


_SLOT_GEOMETRY = {
    0: ("home-1", 0, 0, 0, 0),
    1: ("home-1", 0, 0, 0, 0),
    2: ("home-2", 55, 176, 220, 248),
    3: ("home-2", 290, 176, 220, 248),
    4: ("home-2", 525, 176, 220, 248),
    5: ("home-2", 94, 462, 296, 116),
    6: ("home-4", 60, 168, 210, 190),
    7: ("home-4", 295, 168, 210, 190),
    8: ("home-4", 58, 392, 216, 116),
    9: ("home-4", 292, 392, 216, 116),
    10: ("home-4", 526, 392, 216, 116),
    11: ("home-2", 410, 462, 296, 116),
    12: ("home-2", 180, 606, 440, 76),
    13: ("home-4", 112, 548, 276, 112),
    14: ("home-4", 412, 548, 276, 112),
    15: ("home-4", 530, 168, 210, 190),
}
_CAROUSEL_GEOMETRY = {
    slot: ("home-5", 92 + (slot - 16) % 4 * 158, 150 + (slot - 16) // 4 * 126, 142, 112)
    for slot in range(SLOT_COUNT, CAROUSEL_SLOT_COUNT)
}


class LayoutError(ValueError):
    """A safe, structured validation error for WebSocket clients."""

    def __init__(self, code: str, message: str, path: str = "") -> None:
        self.code = code
        self.path = path
        super().__init__(f"{path}: {message}" if path else message)


def _integer(value: Any, minimum: int, maximum: int, path: str) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise LayoutError("invalid_layout", f"Expected integer {minimum}..{maximum}", path)
    return value


def parse_report_integer(value: Any, minimum: int, maximum: int, path: str) -> int:
    """Accept native decimal strings without coercing booleans or floats."""
    if isinstance(value, str) and value.isascii() and value.isdecimal() and len(value) <= 16:
        value = int(value)
    return _integer(value, minimum, maximum, path)


def _keys(value: Any, allowed: set[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LayoutError("invalid_layout", "Expected an object", path)
    if extra := set(value) - allowed:
        raise LayoutError("invalid_layout", f"Unknown fields: {', '.join(sorted(extra))}", path)
    return value


def _bounded_json(value: Any) -> None:
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, RecursionError) as err:
        raise LayoutError("invalid_layout", "Expected finite JSON data") from err
    if len(encoded) > MAX_DOCUMENT_BYTES:
        raise LayoutError("payload_too_large", f"Configuration exceeds {MAX_DOCUMENT_BYTES} bytes")


def device_profile(*, carousel: bool = False) -> dict[str, Any]:
    """Return independent metadata for the product's precompiled widget pool."""
    slots = []
    geometry = _SLOT_GEOMETRY | _CAROUSEL_GEOMETRY if carousel else _SLOT_GEOMETRY
    for slot, (page, x, y, width, height) in geometry.items():
        slots.append({
            "slot": slot, "page_id": page, "x": x, "y": y,
            "width": width, "height": height,
            "radius": 72 if slot == 3 else 62 if slot == 7 else min(width, height) // 2,
            "editable": slot >= 2, "hidden": slot < 2, "types": list(CARD_TYPES),
        })
    return {
        "id": PROFILE_ID, "version": 1, "wire_version": 1,
        "layout_versions": list(SUPPORTED_LAYOUT_VERSIONS),
        "schema_control_types": ["light", "number", "choice", "cover", "fan", "humidifier", "robot", "panel"],
        "schema_panel_control": True,
        "schema_panel_types": ["timer", "remote", "power"],
        "schema_panel_extra_profiles": [{"name": "action", "version": 2}, {"name": "datetime", "version": 1}, {"name": "info", "version": 1}, {"name": "info_context", "version": 1}, {"name": "lock", "version": 1}, {"name": "media", "version": 1}, {"name": "text", "version": 1}, {"name": "tile_event", "version": 1}],
        "schema_light_detail": True,
        "schema_climate_panel": True,
        "schema_robot_control": True,
        "schema_humidifier_panel": True,
        "schema_cover_panel": True,
        "schema_fan_panel": True,
        "schema_event_actions": True,
        "schema_camera_preview": True,
        "schema_info_agenda_version": 1,
        "schema_info_statistics_version": 1,
        "schema_action_parameters_version": 1,
        "schema_state_labels": True,
        "schema_fan_oscillation": True,
        "schema_humidifier_power": True,
        "schema_humidifier_mode": True,
        "schema_humidifier_humidity": True,
        "schema_climate_humidity": True,
        "schema_light_color_temperature": True,
        "schema_light_effect": True,
        "schema_fan_direction": True,
        "schema_fan_speed": True,
        "schema_vacuum_fan_speed": True,
        "schema_cover_position": True,
        "schema_cover_tilt": True,
        "schema_calendar_next": True,
        "schema_person_presence": True,
        "schema_mower_actions": True,
        "schema_vacuum_actions": True,
        "schema_vacuum_area": True,
        "schema_remote_power": True,
        "schema_media_mute": True,
        "schema_media_shuffle": True,
        "schema_media_volume_actions": True,
        "schema_media_stop": True,
        "schema_media_volume_target": True,
        "schema_media_source": True,
        "schema_media_sound_mode": True,
        "schema_media_repeat": True,
        "schema_remote_activity": True,
        "schema_climate_temperature": True,
        "schema_climate_hvac_mode": True,
        "schema_climate_preset_mode": True,
        "schema_climate_fan_mode": True,
        "schema_climate_swing_mode": True,
        "schema_climate_swing_horizontal_mode": True,
        "sun_text_slots": list(SUN_TEXT_SLOTS),
        "datetime_text_slots": list(DATETIME_TEXT_SLOTS),
        "calendar_text_slots": list(CALENDAR_TEXT_SLOTS),
        "person_text_slots": list(PERSON_TEXT_SLOTS),
        "width": 800, "height": 800, "max_cards": len(geometry),
        "max_document_bytes": MAX_DOCUMENT_BYTES,
        "pages": [
            {"id": "home-1", "title": "Home", "order": 0, "editable": False},
            {"id": "home-2", "title": "Security", "order": 1, "editable": True},
            {"id": "home-3", "title": "Apps", "order": 2, "editable": False},
            {"id": "home-4", "title": "Controls", "order": 3, "editable": True},
            *([{"id": "home-5", "title": "Tools", "order": 4, "editable": True}] if carousel else []),
        ],
        "slots": slots,
        **({"carousel_order": list(HOME_ORDER)} if carousel else {}),
        "features": {
            "move": True, "resize": False, "custom_pages": False,
            "native_controls": False, "applied_ack": False,
        },
    }


# Product-owned action field types. Runtime narrows ranges/options against the
# live entity capabilities and registered Home Assistant services.
def _number(minimum: float, maximum: float, *, required: bool = True) -> dict[str, Any]:
    return {"type": "number", "min": minimum, "max": maximum, "required": required}


ACTION_FIELDS: dict[str, dict[str, dict[str, Any]]] = {
    "light.turn_on": {
        "effect": {"type": "text", "required": False},
        "brightness_pct": _number(0, 100, required=False),
        "color_temp_kelvin": _number(1000, 20000, required=False),
        "rgb_color": {"type": "rgb", "required": False},
    },
    "fan.set_percentage": {"percentage": _number(0, 100)},
    "vacuum.set_fan_speed": {"fan_speed": {"type": "text", "required": True}},
    "vacuum.clean_area": {"cleaning_area_id": {"type": "text", "required": True}},
    "media_player.repeat_set": {"repeat": {"type": "select", "options": ["off", "one", "all"], "required": True}},
    "media_player.select_source": {"source": {"type": "text", "required": True}},
    "media_player.select_sound_mode": {"sound_mode": {"type": "text", "required": True}},
    "media_player.shuffle_set": {"shuffle": {"type": "boolean", "required": True}},
    "media_player.volume_mute": {"is_volume_muted": {"type": "boolean", "required": True}},
    "fan.oscillate": {"oscillating": {"type": "boolean", "required": True}},
    "fan.set_direction": {"direction": {"type": "select", "options": ["forward", "reverse"], "required": True}},
    "fan.set_preset_mode": {"preset_mode": {"type": "text", "required": True}},
    "cover.set_cover_position": {"position": {**_number(0, 100), "step": 1}},
    "cover.set_cover_tilt_position": {"tilt_position": {**_number(0, 100), "step": 1}},
    "climate.set_temperature": {
        "temperature": _number(-100, 200, required=False),
        "target_temp_low": _number(-100, 200, required=False),
        "target_temp_high": _number(-100, 200, required=False),
    },
    "climate.set_hvac_mode": {"hvac_mode": {"type": "text", "required": True}},
    "climate.set_preset_mode": {"preset_mode": {"type": "text", "required": True}},
    "climate.set_fan_mode": {"fan_mode": {"type": "text", "required": True}},
    "humidifier.set_mode": {"mode": {"type": "text", "required": True}},
    "humidifier.set_humidity": {"humidity": {**_number(0, 100), "step": 1}},
    "climate.set_humidity": {"humidity": {**_number(0, 100), "step": 1}},
    "climate.set_swing_mode": {"swing_mode": {"type": "text", "required": True}},
    "climate.set_swing_horizontal_mode": {"swing_horizontal_mode": {"type": "text", "required": True}},
    "media_player.volume_set": {"volume_level": _number(0, 1)},
    "number.set_value": {"value": _number(-1e12, 1e12)},
    "input_number.set_value": {"value": _number(-1e12, 1e12)},
    "select.select_option": {"option": {"type": "text", "required": True}},
    "input_select.select_option": {"option": {"type": "text", "required": True}},
    "timer.start": {"duration": {**_number(1, 86400, required=False), "step": 1}},
    "automation.trigger": {"skip_condition": {"type": "boolean", "required": False}},
    "automation.turn_off": {"stop_actions": {"type": "boolean", "required": False}},
}
NO_DATA_SERVICES = frozenset(
    ("homeassistant.toggle", "homeassistant.turn_on", "homeassistant.turn_off",
     "light.toggle", "light.turn_off", "switch.toggle", "switch.turn_on", "switch.turn_off",
     "input_boolean.toggle", "input_boolean.turn_on", "input_boolean.turn_off",
     "fan.toggle", "fan.turn_on", "fan.turn_off", "button.press", "input_button.press",
     "humidifier.toggle", "humidifier.turn_on", "humidifier.turn_off",
     "scene.turn_on", "script.turn_on", "script.turn_off", "automation.trigger",
     "automation.turn_on", "automation.turn_off", "cover.open_cover",
     "cover.close_cover", "cover.stop_cover", "cover.open_cover_tilt",
     "cover.close_cover_tilt", "cover.stop_cover_tilt", "lock.lock",
     "media_player.volume_up", "media_player.volume_down", "media_player.media_play_pause", "media_player.media_play", "media_player.media_pause", "media_player.media_stop",
     "media_player.repeat_set", "media_player.select_source", "media_player.select_sound_mode", "media_player.media_next_track", "media_player.media_previous_track",
     "media_player.turn_on", "media_player.turn_off",
     "timer.pause", "timer.cancel", "vacuum.start", "vacuum.pause",
     "vacuum.stop", "vacuum.return_to_base", "vacuum.locate", "vacuum.clean_spot",
     "lawn_mower.start_mowing", "lawn_mower.pause", "lawn_mower.dock",
     "remote.turn_on", "remote.turn_off")
)


def validate_field(value: Any, schema: dict[str, Any], path: str) -> Any:
    """Validate a configured value against a static or live field descriptor."""
    kind = schema["type"]
    if kind == "number":
        try:
            finite = type(value) in (int, float) and math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite:
            raise LayoutError("invalid_action_data", "Expected a finite number", path)
        if not schema.get("min", -math.inf) <= value <= schema.get("max", math.inf):
            raise LayoutError("invalid_action_data", "Number is outside the supported range", path)
        step = schema.get("step")
        if type(step) in (int, float) and math.isfinite(step) and step > 0:
            steps = (value - schema.get("min", 0)) / step
            if not math.isfinite(steps) or not math.isclose(steps, round(steps), rel_tol=0, abs_tol=1e-6):
                raise LayoutError("invalid_action_data", "Number does not match the supported step", path)
    elif kind == "boolean":
        if type(value) is not bool:
            raise LayoutError("invalid_action_data", "Expected a boolean", path)
    elif kind == "rgb":
        if not isinstance(value, list) or len(value) != 3 or any(
            type(channel) is not int or not 0 <= channel <= 255 for channel in value
        ):
            raise LayoutError("invalid_action_data", "Expected three RGB bytes", path)
    elif kind in {"text", "select"}:
        if not isinstance(value, str) or not value or len(value) > 128:
            raise LayoutError("invalid_action_data", "Expected text of 1..128 characters", path)
        if kind == "select" and value not in schema.get("options", []):
            raise LayoutError("invalid_action_data", "Value is not an available option", path)
    else:
        raise LayoutError("invalid_action_data", "Unknown field type", path)
    return deepcopy(value)


def is_camera_preview_card(card: dict[str, Any]) -> bool:
    """Recognize the closed explicit camera launcher; never a provider service."""
    action = card.get("action")
    return (card.get("type") == "entity" and isinstance(card.get("entity_id"), str)
            and card["entity_id"].startswith("camera.") and isinstance(action, dict)
            and set(action) == {"kind", "duration_seconds"} and action["kind"] == "camera_preview"
            and type(action["duration_seconds"]) is int and 15 <= action["duration_seconds"] <= 90)


def validate_action(raw: Any, entity_id: str, path: str = "action", *, layout_version: int = 2) -> dict[str, Any]:
    action = _keys(raw, {"kind", "service", "data", "control", "property", "initial_duration", "detail", "skip_condition", "stop_actions", "duration_seconds", "parameters"}, path)
    kind = action.get("kind", "default")
    if not isinstance(kind, str):
        raise LayoutError("unsupported_action", "Action kind must be text", path)
    if kind == "camera_preview":
        if layout_version != CONTROL_LAYOUT_VERSION or not is_camera_preview_card({"type": "entity", "entity_id": entity_id, "action": action}):
            raise LayoutError("unsupported_action", "Camera preview requires an explicit v3 camera and duration 15..90 seconds", path)
        return dict(action)
    if "duration_seconds" in action or (entity_id.startswith("camera.") and kind != "none"):
        raise LayoutError("unsupported_action", "Cameras support only passive cards or an explicit preview", path)
    info_panel = action in ({"kind": "control", "control": "panel", "property": "info"}, {"kind": "control", "control": "panel", "property": "agenda"}, {"kind": "control", "control": "panel", "property": "statistics"})
    if entity_id.partition(".")[0] in {"sun", "calendar", "person"} and kind != "none" and not info_panel:
        raise LayoutError("unsupported_action", "This information domain is read-only", path)
    if kind in {"none", "default"}:
        if set(action) - {"kind"}:
            raise LayoutError("invalid_action_data", "This action has no service fields", path)
        return {"kind": kind}
    if kind == "event":
        if layout_version != CONTROL_LAYOUT_VERSION or set(action) != {"kind"} or entity_id:
            raise LayoutError("unsupported_action", "Events require an explicit v3 action with no entity target", path)
        return {"kind": "event"}
    if kind == "fan_oscillation":
        if layout_version != CONTROL_LAYOUT_VERSION or set(action) != {"kind"} or entity_id.partition(".")[0] != "fan":
            raise LayoutError("unsupported_action", "Oscillation requires an explicit v3 fan action", path)
        return {"kind": "fan_oscillation"}
    if kind == "control":
        if "detail" in action:
            if (layout_version != CONTROL_LAYOUT_VERSION or entity_id.partition(".")[0] != "light"
                    or set(action) != {"kind", "control", "detail"} or action["control"] != "light"
                    or type(action["detail"]) is not int or action["detail"] != 1):
                raise LayoutError("unsupported_action", "Light detail requires an explicit v3 profile", path)
            return dict(action)
        if action.get("control") == "panel":
            family = action.get("property")
            if family == "tile_event":
                if (layout_version != CONTROL_LAYOUT_VERSION or entity_id
                        or action != {"kind": "control", "control": "panel", "property": "tile_event"}):
                    raise LayoutError("unsupported_action", "Tile events require an explicit v3 panel without an entity target", path)
                return dict(action)
            if family == "action":
                from .action_panel_domain import saved_action
                from .action_parameters_domain import ACTION as PARAMETERS_ACTION
                parameters = action == PARAMETERS_ACTION and entity_id.startswith("script.")
                if layout_version != CONTROL_LAYOUT_VERSION or not (parameters or saved_action(action, entity_id)):
                    raise LayoutError("unsupported_action", "Action requires an explicit v3 subtype and automation policies", path)
                return dict(action)
            domains = {"timer": {"timer"}, "remote": {"remote"}, "power": {"switch", "input_boolean"}, "climate": {"climate"},
                       "agenda": {"calendar"}, "statistics": {"sensor"}, "info": {"sensor", "binary_sensor", "calendar", "alarm_control_panel", "person", "sun"}, "lock": {"lock"}, "media": {"media_player"}, "datetime": {"input_datetime"}, "text": {"input_text"}}
            expected = {"kind", "control", "property"} | ({"initial_duration"} if "initial_duration" in action else set())
            if (layout_version != CONTROL_LAYOUT_VERSION or set(action) != expected
                    or not isinstance(family, str) or entity_id.partition(".")[0] not in domains.get(family, ())
                    or ("initial_duration" in action and (family != "timer" or type(action["initial_duration"]) is not int
                                                         or not 1 <= action["initial_duration"] <= 86400))):
                raise LayoutError("unsupported_action", "Panels require an explicit supported v3 family", path)
            return dict(action)
        if "initial_duration" in action:
            raise LayoutError("invalid_action_data", "Initial duration belongs to a Timer panel", path)
        if "property" in action:
            valid = ((action == {"kind": "control", "control": "choice", "property": "sound_mode"} and entity_id.partition(".")[0] == "media_player")
                     or (action == {"kind": "control", "control": "choice", "property": "repeat"} and entity_id.partition(".")[0] == "media_player")
                     or (action == {"kind": "control", "control": "choice", "property": "source"} and entity_id.partition(".")[0] == "media_player")
                     or (action == {"kind": "control", "control": "choice", "property": "activity"} and entity_id.partition(".")[0] == "remote")
                     or (action == {"kind": "control", "control": "choice", "property": "direction"} and entity_id.partition(".")[0] == "fan")
                     or (action == {"kind": "control", "control": "number", "property": "position"} and entity_id.partition(".")[0] == "cover")
                     or (action == {"kind": "control", "control": "number", "property": "tilt_position"} and entity_id.partition(".")[0] == "cover")
                     or (action == {"kind": "control", "control": "choice", "property": "fan_speed"} and entity_id.partition(".")[0] == "vacuum")
                     or (action == {"kind": "control", "control": "choice", "property": "percentage"} and entity_id.partition(".")[0] == "fan")
                     or (action == {"kind": "control", "control": "choice", "property": "effect"} and entity_id.partition(".")[0] == "light")
                     or (action == {"kind": "control", "control": "number", "property": "temperature"} and entity_id.partition(".")[0] == "climate")
                     or (action == {"kind": "control", "control": "number", "property": "humidity"} and entity_id.partition(".")[0] in {"humidifier", "climate"})
                     or (action == {"kind": "control", "control": "number", "property": "color_temp_kelvin"} and entity_id.partition(".")[0] == "light")
                     or (action == {"kind": "control", "control": "choice", "property": "hvac_mode"} and entity_id.partition(".")[0] == "climate")
                     or (action == {"kind": "control", "control": "choice", "property": "preset_mode"} and entity_id.partition(".")[0] == "climate")
                     or (action == {"kind": "control", "control": "choice", "property": "fan_mode"} and entity_id.partition(".")[0] == "climate")
                     or (action == {"kind": "control", "control": "choice", "property": "swing_mode"} and entity_id.partition(".")[0] == "climate")
                     or (action == {"kind": "control", "control": "choice", "property": "swing_horizontal_mode"} and entity_id.partition(".")[0] == "climate")
                     or (action == {"kind": "control", "control": "choice", "property": "mode"} and entity_id.partition(".")[0] == "humidifier"))
            if layout_version != CONTROL_LAYOUT_VERSION or not valid:
                raise LayoutError("unsupported_action", "Unsupported explicit v3 control property", path)
            return dict(action)
        if (layout_version != CONTROL_LAYOUT_VERSION or set(action) != {"kind", "control"}
                or (action.get("control"), entity_id.partition(".")[0]) not in (("light", "light"), ("number", "input_number"), ("number", "number"), ("choice", "select"), ("choice", "input_select"), ("choice", "fan"), ("cover", "cover"), ("fan", "fan"), ("humidifier", "humidifier"), ("robot", "vacuum"), ("robot", "lawn_mower"))):
            raise LayoutError("unsupported_action", "Controls require an explicit v3 supported entity action", path)
        return {"kind": "control", "control": action["control"]}
    if any(key in action for key in ("control", "property", "initial_duration", "detail", "skip_condition", "stop_actions", "parameters")):
        raise LayoutError("invalid_action_data", "Control metadata is only valid for a v3 control", path)
    if kind != "service":
        raise LayoutError("unsupported_action", "Unknown action kind", path)
    service = action.get("service")
    if not isinstance(service, str) or not _SERVICE.fullmatch(service):
        raise LayoutError("unsupported_action", "Expected domain.service", path)
    domain, operation = service.split(".", 1)
    entity_domain = entity_id.partition(".")[0]
    if not entity_id or domain not in {entity_domain, "homeassistant"}:
        raise LayoutError("unsupported_action", "Service must target the card entity domain", path)
    if domain == "alarm_control_panel" or (domain == "lock" and operation != "lock"):
        raise LayoutError("unsupported_action", "This action requires a confirmed device control flow", path)
    if domain == "homeassistant" and entity_domain in {"lock", "alarm_control_panel", "cover"}:
        raise LayoutError("unsupported_action", "Generic actions cannot bypass protected controls", path)
    if service not in ACTION_FIELDS and service not in NO_DATA_SERVICES:
        raise LayoutError("unsupported_action", "Service is outside the typed action catalogue", path)
    data = action.get("data", {})
    if not isinstance(data, dict):
        raise LayoutError("invalid_action_data", "Expected an object", path)
    fields = ACTION_FIELDS.get(service, {})
    if unknown := set(data) - set(fields):
        raise LayoutError("invalid_action_data", f"Unsupported fields: {', '.join(sorted(unknown))}", path)
    for name, schema in fields.items():
        if schema.get("required") and name not in data:
            raise LayoutError("invalid_action_data", f"Missing field {name}", path)
    result = {name: validate_field(value, fields[name], f"{path}.{name}") for name, value in data.items()}
    if service == "timer.start" and "duration" in result and int(result["duration"]) != result["duration"]:
        raise LayoutError("invalid_action_data", "Timer duration requires whole seconds", f"{path}.duration")
    if service == "climate.set_temperature":
        if set(result) not in ({"temperature"}, {"target_temp_low", "target_temp_high"}):
            raise LayoutError("invalid_action_data", "Set one temperature or a complete low/high range", path)
        if "target_temp_low" in result and result["target_temp_low"] >= result["target_temp_high"]:
            raise LayoutError("invalid_action_data", "Low temperature must be below high temperature", path)
    if service == "light.turn_on" and sum(name in result for name in ("color_temp_kelvin", "rgb_color")) > 1:
        raise LayoutError("invalid_action_data", "Choose one light colour representation", path)
    return {"kind": "service", "service": service, "data": result}


def validate_home_order(value: Any) -> list[str]:
    if (
        not isinstance(value, list)
        or not 2 <= len(value) <= len(HOME_ORDER)
        or value[0] != HOME_ORDER[0]
        or HOME_ORDER[2] not in value
        or any(not isinstance(item, str) or item not in HOME_ORDER for item in value)
        or len(set(value)) != len(value)
    ):
        raise LayoutError("invalid_carousel", "Choose unique pages and keep Home first and Apps visible", "home_order")
    return value.copy()


def validate_layout(raw: Any) -> dict[str, Any]:
    """Validate atomically; no unknown metadata or credentials are persisted."""
    _bounded_json(raw)
    layout = _keys(raw, {"version", "profile", "revision", "cards", "home_order"}, "layout")
    version = layout.get("version")
    if type(version) is not int or version not in SUPPORTED_LAYOUT_VERSIONS:
        raise LayoutError("unsupported_version", "Expected layout version 2 or 3")
    if layout.get("profile") != PROFILE_ID:
        raise LayoutError("incompatible_profile", f"Expected profile {PROFILE_ID}")
    revision = _integer(layout.get("revision", 0), 0, MAX_REVISION, "revision")
    cards = layout.get("cards")
    order = validate_home_order(layout["home_order"]) if "home_order" in layout else None
    slots_limit = CAROUSEL_SLOT_COUNT if order is not None else SLOT_COUNT
    if not isinstance(cards, list) or len(cards) > slots_limit:
        raise LayoutError("invalid_layout", f"Expected at most {slots_limit} cards", "cards")
    result, ids, slots = [], set(), set()
    for index, raw_card in enumerate(cards):
        path = f"cards[{index}]"
        card = _keys(raw_card, {
            "id", "slot", "type", "entity_id", "title", "icon", "palette", "visible", "action", "state_color", "display_precision", "state_labels"
        }, path)
        card_id = card.get("id")
        if not isinstance(card_id, str) or not _ID.fullmatch(card_id):
            raise LayoutError("invalid_layout", "Expected a stable card ID of 1..64 characters", path)
        if card_id in ids:
            raise LayoutError("duplicate_card_id", "Card ID is already used", path)
        slot = _integer(card.get("slot"), 0, slots_limit - 1, f"{path}.slot")
        if slot in slots:
            raise LayoutError("duplicate_slot", "Slot is already occupied", path)
        card_type = card.get("type", "entity")
        if card_type not in CARD_TYPES:
            raise LayoutError("invalid_layout", "Unsupported card type", path)
        entity_id = card.get("entity_id", "")
        if not isinstance(entity_id, str) or len(entity_id) > 128 or (
            entity_id and (not _ENTITY.fullmatch(entity_id) or entity_id.split(".", 1)[0] not in SUPPORTED_DOMAINS)
        ):
            raise LayoutError("invalid_layout", "Unsupported entity ID", path)
        for field, choices, default in (("icon", ICON_NAMES, "action"), ("palette", PALETTE_NAMES, "surface")):
            if not isinstance(card.get(field, default), str) or card.get(field, default) not in choices:
                raise LayoutError("invalid_layout", f"Unknown {field}", path)
        if card.get("icon") == "auto" and not (card_type == "sensor" and entity_id.startswith("binary_sensor.")):
            raise LayoutError("unsupported_auto_icon", "Automatic icons require a binary information card", path)
        visible = card.get("visible", True)
        if type(visible) is not bool:
            raise LayoutError("invalid_layout", "Expected a boolean", f"{path}.visible")
        if slot < 2 and visible:
            raise LayoutError("reserved_slot", "This slot is reserved and always hidden", path)
        title = card.get("title", "")
        if not isinstance(title, str) or len(title) > 160:
            raise LayoutError("invalid_layout", "Title is too long or not text", path)
        explicit_info = version == CONTROL_LAYOUT_VERSION and card.get("action") in ({"kind": "control", "control": "panel", "property": "info"}, {"kind": "control", "control": "panel", "property": "agenda"}, {"kind": "control", "control": "panel", "property": "statistics"})
        if entity_id.partition(".")[0] == "sun":
            if card_type != "sensor" and not (explicit_info and card_type == "entity"):
                raise LayoutError("unsupported_action", "Sun requires an information card", path)
            if slot not in SUN_TEXT_SLOTS and not explicit_info:
                raise LayoutError("unsupported_domain_slot", "Sun captions require a text tile", path)
        if entity_id.partition(".")[0] == "input_datetime":
            explicit_datetime = version == CONTROL_LAYOUT_VERSION and card.get("action") == {"kind": "control", "control": "panel", "property": "datetime"}
            if card_type != "sensor" and not (explicit_datetime and card_type == "entity"):
                raise LayoutError("unsupported_action", "Date/time helpers require an information card or explicit editor", path)
            if slot not in DATETIME_TEXT_SLOTS and not explicit_datetime:
                raise LayoutError("unsupported_domain_slot", "Date/time helpers require a text tile", path)
        if entity_id.partition(".")[0] == "calendar":
            explicit_info = version == CONTROL_LAYOUT_VERSION and card.get("action") in ({"kind": "control", "control": "panel", "property": "info"}, {"kind": "control", "control": "panel", "property": "agenda"}, {"kind": "control", "control": "panel", "property": "statistics"})
            if card_type != "sensor" and not (explicit_info and card_type == "entity"):
                raise LayoutError("unsupported_action", "Calendar requires an information card", path)
            if slot not in CALENDAR_TEXT_SLOTS and not explicit_info:
                raise LayoutError("unsupported_domain_slot", "Calendar event captions require the wide text tile", path)
        if entity_id.partition(".")[0] == "person":
            if card_type != "sensor" and not (explicit_info and card_type == "entity"):
                raise LayoutError("unsupported_action", "Person requires an information card", path)
            if slot not in PERSON_TEXT_SLOTS and not explicit_info:
                raise LayoutError("unsupported_domain_slot", "Person zone captions require the wide text tile", path)
        action = validate_action(card.get("action", {"kind": "default"}), entity_id, f"{path}.action", layout_version=version)
        if action["kind"] == "camera_preview" and (slot < 2 or card_type != "entity"):
            raise LayoutError("unsupported_action", "Camera previews require an editable entity card", path)
        info_panel = action in ({"kind": "control", "control": "panel", "property": "info"}, {"kind": "control", "control": "panel", "property": "agenda"}, {"kind": "control", "control": "panel", "property": "statistics"})
        action_panel = action.get("kind") == "control" and action.get("control") == "panel" and action.get("property") in {"action", "tile_event"}
        if action_panel and action.get("property") == "tile_event" and card_type != "action":
            raise LayoutError("unsupported_action", "Tile event panels require an action card", path)
        if action["kind"] == "control" and (slot < 2 or card_type not in ({"entity", "sensor"} if info_panel else {"entity", "action"} if action_panel else {"entity"})):
            raise LayoutError("unsupported_action", "Controls require an editable entity card", path)
        if action["kind"] == "event" and (slot < 2 or card_type != "action"):
            raise LayoutError("unsupported_action", "Events require an editable Action card", path)
        if card_type == "sensor" and action["kind"] != "none" and not info_panel:
            raise LayoutError("unsupported_action", "Sensor cards are read-only", path)
        if "state_color" in card:
            if type(card["state_color"]) is not bool:
                raise LayoutError("invalid_layout", "Expected a boolean", f"{path}.state_color")
            if card["state_color"] and not supports_state_color(card_type, entity_id):
                raise LayoutError("unsupported_state_color", "State color requires a supported entity or binary information card", path)
        if "display_precision" in card:
            _integer(card["display_precision"], 0, MAX_PRECISION, f"{path}.display_precision")
            if card_type != "sensor" or entity_id.partition(".")[0] not in PRECISION_DOMAINS:
                raise LayoutError("unsupported_precision", "Precision requires a numeric information card", path)
        ids.add(card_id)
        slots.add(slot)
        result.append({
            "id": card_id, "slot": slot, "type": card_type, "entity_id": entity_id,
            "title": plain_text(title, 40), "icon": card.get("icon", "action"),
            "palette": card.get("palette", "surface"), "visible": visible, "action": action,
        })
        if "state_color" in card:
            result[-1]["state_color"] = card["state_color"]
        if "display_precision" in card:
            result[-1]["display_precision"] = card["display_precision"]
        if "state_labels" in card:
            if not state_labels_eligible(result[-1]):
                raise LayoutError("unsupported_state_labels", "State labels require an editable information card", path)
            try:
                labels = validate_labels(card["state_labels"])
            except (ValueError, UnicodeError) as error:
                raise LayoutError("invalid_state_labels", str(error), f"{path}.state_labels") from error
            if labels:
                result[-1]["state_labels"] = labels
    return {"version": version, "profile": PROFILE_ID, "revision": revision,
            "cards": sorted(result, key=lambda card: card["slot"]),
            **({"home_order": order} if order is not None else {})}


def migrate_v2_to_v3(raw: Any) -> dict[str, Any]:
    """Explicit deterministic upgrade; preserve every ID/slot/action/revision.

    Existing entry reads and v2 saves remain v2. Opt-in editor/import work calls
    this before adding a control and committing its normal revision increment.
    """
    result = validate_layout(raw)
    result["version"] = CONTROL_LAYOUT_VERSION
    return validate_layout(result)


def migrate_legacy(cards: list[dict[str, Any]], revision: int = 0) -> dict[str, Any]:
    """Assign deterministic identities once without changing physical slots."""
    migrated = []
    for card in cards:
        if type(card.get("slot")) is not int or not 0 <= card["slot"] < SLOT_COUNT:
            continue
        item = {key: card[key] for key in ("slot", "entity_id", "title", "icon", "palette", "visible") if key in card}
        item.update(id=card.get("id") or f"legacy-{card['slot']:02d}", type=card.get("type", "entity"))
        item["visible"] = bool(item.get("visible", True)) and item["slot"] >= 2
        action = card.get("action")
        if action is None:
            action = ({"kind": "service", "service": card["service"], "data": {}}
                      if card.get("service") else {"kind": "default"})
        try:
            item["action"] = validate_action(action, item.get("entity_id", ""))
        except LayoutError:
            # An old unsafe/custom-parameter action must not gain authority.
            item["action"] = {"kind": "none"}
        migrated.append(item)
    return validate_layout({"version": LAYOUT_VERSION, "profile": PROFILE_ID,
                            "revision": revision, "cards": migrated})


def export_layout(layout: dict[str, Any]) -> dict[str, Any]:
    canonical = validate_layout(layout)
    canonical.pop("revision")
    return {"format": "atmosfera-layout", "version": 1, "layout": canonical}


def import_layout(backup: Any, revision: int) -> dict[str, Any]:
    _bounded_json(backup)
    envelope = _keys(backup, {"format", "version", "layout"}, "backup")
    if envelope.get("format") != "atmosfera-layout" or type(envelope.get("version")) is not int or envelope.get("version") != 1:
        raise LayoutError("invalid_backup", "Unsupported backup format/version")
    document = deepcopy(envelope.get("layout"))
    if not isinstance(document, dict) or "revision" in document:
        raise LayoutError("invalid_backup", "Backup layout must not contain a device revision")
    document["revision"] = revision
    return validate_layout(document)


def next_revision(current: int, expected: Any) -> int:
    _integer(expected, 0, MAX_REVISION, "expected_revision")
    if expected != current:
        raise LayoutError("revision_conflict", f"Layout changed; current revision is {current}")
    return _integer(current + 1, 1, MAX_REVISION, "revision")
