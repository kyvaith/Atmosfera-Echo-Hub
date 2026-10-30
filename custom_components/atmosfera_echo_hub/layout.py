"""Bounded Home Assistant layout model; no Home Assistant runtime dependency."""

from __future__ import annotations

from copy import deepcopy
import json
import math
import re
from typing import Any

from .text import plain_text

LAYOUT_VERSION = 2
CONTROL_LAYOUT_VERSION = 3
SUPPORTED_LAYOUT_VERSIONS = (LAYOUT_VERSION, CONTROL_LAYOUT_VERSION)
PROFILE_ID = "echo-hub-m3-v1"
SLOT_COUNT = 16
MAX_DOCUMENT_BYTES = 32768
MAX_REVISION = 2**53 - 1
CARD_TYPES = ("entity", "sensor", "action")
ICON_NAMES = frozenset(
    ("action", "alarm", "climate", "cover", "fan", "light", "lock", "scene",
     "speed", "switch", "sensor", "door", "presence", "clock", "webhook")
)
PALETTE_NAMES = frozenset(
    ("primary", "primary_container", "secondary", "surface", "tertiary")
)
SUPPORTED_DOMAINS = frozenset(
    ("alarm_control_panel", "automation", "binary_sensor", "button", "climate",
     "cover", "fan", "input_boolean", "input_button", "input_number",
     "input_select", "light", "lock", "media_player", "number", "scene",
     "script", "select", "sensor", "sun", "switch", "timer", "vacuum", "lawn_mower")
)
# Product-owned text geometry: large-value Roboto34 places cannot fit Sun captions.
SUN_TEXT_SLOTS = tuple(slot for slot in range(2, SLOT_COUNT) if slot not in (13, 14))
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_ENTITY = re.compile(r"^[a-z_][a-z0-9_]*\.[a-z0-9_]+$")
_SERVICE = re.compile(r"^[a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*$")
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


def device_profile() -> dict[str, Any]:
    """Return independent metadata for the product's precompiled widget pool."""
    slots = []
    for slot, (page, x, y, width, height) in _SLOT_GEOMETRY.items():
        slots.append({
            "slot": slot, "page_id": page, "x": x, "y": y,
            "width": width, "height": height,
            "radius": 72 if slot == 3 else 62 if slot == 7 else min(width, height) // 2,
            "editable": slot >= 2, "hidden": slot < 2, "types": list(CARD_TYPES),
        })
    return {
        "id": PROFILE_ID, "version": 1, "wire_version": 1,
        "layout_versions": list(SUPPORTED_LAYOUT_VERSIONS),
        "schema_control_types": ["light", "number"],
        "sun_text_slots": list(SUN_TEXT_SLOTS),
        "width": 800, "height": 800, "max_cards": SLOT_COUNT,
        "max_document_bytes": MAX_DOCUMENT_BYTES,
        "pages": [
            {"id": "home-1", "title": "Home", "order": 0, "editable": False},
            {"id": "home-2", "title": "Security", "order": 1, "editable": True},
            {"id": "home-3", "title": "Apps", "order": 2, "editable": False},
            {"id": "home-4", "title": "Controls", "order": 3, "editable": True},
        ],
        "slots": slots,
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
        "brightness_pct": _number(0, 100, required=False),
        "color_temp_kelvin": _number(1000, 20000, required=False),
        "rgb_color": {"type": "rgb", "required": False},
    },
    "fan.set_percentage": {"percentage": _number(0, 100)},
    "fan.oscillate": {"oscillating": {"type": "boolean", "required": True}},
    "fan.set_direction": {"direction": {"type": "select", "options": ["forward", "reverse"], "required": True}},
    "fan.set_preset_mode": {"preset_mode": {"type": "text", "required": True}},
    "cover.set_cover_position": {"position": _number(0, 100)},
    "cover.set_cover_tilt_position": {"tilt_position": _number(0, 100)},
    "climate.set_temperature": {
        "temperature": _number(-100, 200, required=False),
        "target_temp_low": _number(-100, 200, required=False),
        "target_temp_high": _number(-100, 200, required=False),
    },
    "climate.set_hvac_mode": {"hvac_mode": {"type": "text", "required": True}},
    "climate.set_preset_mode": {"preset_mode": {"type": "text", "required": True}},
    "climate.set_fan_mode": {"fan_mode": {"type": "text", "required": True}},
    "climate.set_swing_mode": {"swing_mode": {"type": "text", "required": True}},
    "number.set_value": {"value": _number(-1e12, 1e12)},
    "input_number.set_value": {"value": _number(-1e12, 1e12)},
    "select.select_option": {"option": {"type": "text", "required": True}},
    "input_select.select_option": {"option": {"type": "text", "required": True}},
}
NO_DATA_SERVICES = frozenset(
    ("homeassistant.toggle", "homeassistant.turn_on", "homeassistant.turn_off",
     "light.toggle", "light.turn_off", "switch.toggle", "switch.turn_on", "switch.turn_off",
     "input_boolean.toggle", "input_boolean.turn_on", "input_boolean.turn_off",
     "fan.toggle", "fan.turn_on", "fan.turn_off", "button.press", "input_button.press",
     "scene.turn_on", "script.turn_on", "script.turn_off", "automation.trigger",
     "automation.turn_on", "automation.turn_off", "cover.open_cover",
     "cover.close_cover", "cover.stop_cover", "cover.open_cover_tilt",
     "cover.close_cover_tilt", "cover.stop_cover_tilt", "lock.lock",
     "media_player.media_play_pause", "media_player.media_play", "media_player.media_pause",
     "media_player.media_next_track", "media_player.media_previous_track",
     "media_player.turn_on", "media_player.turn_off", "timer.start",
     "timer.pause", "timer.cancel", "vacuum.start", "vacuum.pause",
     "vacuum.stop", "vacuum.return_to_base", "vacuum.locate", "vacuum.clean_spot",
     "lawn_mower.start_mowing", "lawn_mower.pause", "lawn_mower.dock")
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


def validate_action(raw: Any, entity_id: str, path: str = "action", *, layout_version: int = 2) -> dict[str, Any]:
    action = _keys(raw, {"kind", "service", "data", "control"}, path)
    kind = action.get("kind", "default")
    if not isinstance(kind, str):
        raise LayoutError("unsupported_action", "Action kind must be text", path)
    if entity_id.partition(".")[0] == "sun" and kind != "none":
        raise LayoutError("unsupported_action", "Sun cards are read-only", path)
    if kind in {"none", "default"}:
        if set(action) - {"kind"}:
            raise LayoutError("invalid_action_data", "This action has no service fields", path)
        return {"kind": kind}
    if kind == "control":
        if (layout_version != CONTROL_LAYOUT_VERSION or set(action) != {"kind", "control"}
                or (action.get("control"), entity_id.partition(".")[0]) not in (("light", "light"), ("number", "input_number"))):
            raise LayoutError("unsupported_action", "Controls require explicit v3 light or input_number action", path)
        return {"kind": "control", "control": action["control"]}
    if "control" in action:
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
    if service == "climate.set_temperature":
        if set(result) not in ({"temperature"}, {"target_temp_low", "target_temp_high"}):
            raise LayoutError("invalid_action_data", "Set one temperature or a complete low/high range", path)
        if "target_temp_low" in result and result["target_temp_low"] >= result["target_temp_high"]:
            raise LayoutError("invalid_action_data", "Low temperature must be below high temperature", path)
    if service == "light.turn_on" and sum(name in result for name in ("color_temp_kelvin", "rgb_color")) > 1:
        raise LayoutError("invalid_action_data", "Choose one light colour representation", path)
    return {"kind": "service", "service": service, "data": result}


def validate_layout(raw: Any) -> dict[str, Any]:
    """Validate atomically; no unknown metadata or credentials are persisted."""
    _bounded_json(raw)
    layout = _keys(raw, {"version", "profile", "revision", "cards"}, "layout")
    version = layout.get("version")
    if type(version) is not int or version not in SUPPORTED_LAYOUT_VERSIONS:
        raise LayoutError("unsupported_version", "Expected layout version 2 or 3")
    if layout.get("profile") != PROFILE_ID:
        raise LayoutError("incompatible_profile", f"Expected profile {PROFILE_ID}")
    revision = _integer(layout.get("revision", 0), 0, MAX_REVISION, "revision")
    cards = layout.get("cards")
    if not isinstance(cards, list) or len(cards) > SLOT_COUNT:
        raise LayoutError("invalid_layout", f"Expected at most {SLOT_COUNT} cards", "cards")
    result, ids, slots = [], set(), set()
    for index, raw_card in enumerate(cards):
        path = f"cards[{index}]"
        card = _keys(raw_card, {
            "id", "slot", "type", "entity_id", "title", "icon", "palette", "visible", "action"
        }, path)
        card_id = card.get("id")
        if not isinstance(card_id, str) or not _ID.fullmatch(card_id):
            raise LayoutError("invalid_layout", "Expected a stable card ID of 1..64 characters", path)
        if card_id in ids:
            raise LayoutError("duplicate_card_id", "Card ID is already used", path)
        slot = _integer(card.get("slot"), 0, SLOT_COUNT - 1, f"{path}.slot")
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
        visible = card.get("visible", True)
        if type(visible) is not bool:
            raise LayoutError("invalid_layout", "Expected a boolean", f"{path}.visible")
        if slot < 2 and visible:
            raise LayoutError("reserved_slot", "This slot is reserved and always hidden", path)
        title = card.get("title", "")
        if not isinstance(title, str) or len(title) > 160:
            raise LayoutError("invalid_layout", "Title is too long or not text", path)
        if entity_id.partition(".")[0] == "sun":
            if card_type != "sensor":
                raise LayoutError("unsupported_action", "Sun requires an information card", path)
            if slot not in SUN_TEXT_SLOTS:
                raise LayoutError("unsupported_domain_slot", "Sun captions require a text tile", path)
        action = validate_action(card.get("action", {"kind": "default"}), entity_id, f"{path}.action", layout_version=version)
        if action["kind"] == "control" and (slot < 2 or card_type != "entity"):
            raise LayoutError("unsupported_action", "Controls require an editable entity card", path)
        if card_type == "sensor" and action["kind"] != "none":
            raise LayoutError("unsupported_action", "Sensor cards are read-only", path)
        ids.add(card_id)
        slots.add(slot)
        result.append({
            "id": card_id, "slot": slot, "type": card_type, "entity_id": entity_id,
            "title": plain_text(title, 40), "icon": card.get("icon", "action"),
            "palette": card.get("palette", "surface"), "visible": visible, "action": action,
        })
    return {"version": version, "profile": PROFILE_ID, "revision": revision,
            "cards": sorted(result, key=lambda card: card["slot"])}


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
