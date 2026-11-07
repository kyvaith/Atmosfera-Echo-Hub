"""Bounded completed-hour observations; no live state/Recorder writes."""

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
from zoneinfo import ZoneInfo

ACTION = {"kind": "control", "control": "panel", "property": "statistics"}
CAPS = {"info_type": "statistics", "statistics_version": 1}
LIMITS = {"axis_min_text": 24, "axis_max_text": 24, "unit": 32,
          "start_text": 32, "end_text": 32, "zone_text": 48}
UNSUPPORTED = {"recorder_missing", "no_metadata", "not_arithmetic", "unit_incompatible", "label_unrepresentable"}
ERRORS = {"recorder_unavailable", "invalid_data", "read_failed", "read_timeout", "busy"}


class StatisticsError(ValueError):
    """Only bounded reason codes, never query/source values."""


def integer(value, low, high):
    return type(value) is int and low <= value <= high


def text_valid(value, limit, *, ascii_only=False):
    try:
        return (type(value) is str and len(value.encode("ascii" if ascii_only else "utf8")) <= limit
                and all(c.isprintable() for c in value))
    except UnicodeError:
        return False


def current_status(state):
    return state.state if state.state in ("unknown", "unavailable") else "known"


def _plain_string(value):
    # Core exposes string enums in sensor properties and State attributes.
    # Preserve their text before storing the semantic fence or wire labels.
    return str(value) if isinstance(value, str) else value


@dataclass(frozen=True, eq=False)
class StatisticsDomain:
    # Keep source identity by reference; never copy it into descriptors or JSON.
    entity: object
    registry: tuple | None
    zone: str
    unit: str | None
    qualification: tuple
    arithmetic: bool
    family = "info"

    def __eq__(self, other):
        return (isinstance(other, StatisticsDomain) and self.entity is other.entity
                and (self.registry, self.zone, self.unit, self.qualification, self.arithmetic)
                == (other.registry, other.zone, other.unit, other.qualification, other.arithmetic))

    @classmethod
    def from_ha(cls, hass, state):
        if not state.entity_id.startswith("sensor."):
            raise StatisticsError("source")
        from homeassistant.components.sensor import DATA_COMPONENT, SensorEntity
        from homeassistant.helpers import entity_registry as er
        component = getattr(hass, "data", {}).get(DATA_COMPONENT)
        getter = getattr(component, "get_entity", None)
        entity = getter(state.entity_id) if callable(getter) else None
        if not isinstance(entity, SensorEntity):
            raise StatisticsError("source")
        row = er.async_get(hass).async_get(state.entity_id)
        if row is not None and getattr(row, "disabled_by", None) is not None:
            raise StatisticsError("source")
        registry = None if row is None else tuple(getattr(row, key, None) for key in
            ("id", "entity_id", "unique_id", "platform", "config_entry_id", "device_id"))
        attributes = state.attributes
        # Both event attributes and actual object properties matter: an earlier
        # B event still retires an A->B->A change coalesced before presentation.
        qualification = tuple(_plain_string(attributes.get(key)) for key in ("state_class", "device_class", "unit_of_measurement"))
        native = tuple(_plain_string(getattr(entity, key, None)) for key in ("state_class", "device_class", "unit_of_measurement"))
        unit = qualification[2]
        zone = _plain_string(getattr(hass.config, "time_zone", None))
        if type(zone) is not str or unit is not None and type(unit) is not str:
            raise StatisticsError("source")
        try:
            ZoneInfo(zone)
        except (KeyError, ValueError):
            raise StatisticsError("source") from None
        return cls(entity, registry, zone, unit, qualification + native,
                   qualification[0] == native[0] == "measurement"
                   and qualification[1] not in ("enum", "date", "timestamp"))

    def descriptor(self):
        return dict(CAPS)


def statistics_metadata(hass, state):
    try:
        domain = StatisticsDomain.from_ha(hass, state)
        return {"statistics": {"version": 1, "read_only": True, "hours": 24}} if domain.arithmetic else {}
    except StatisticsError:
        return {}


def window_end(now):
    value = math.floor(now.timestamp() / 3600)
    if not integer(value, 24, 0xFFFFFFFF):
        raise StatisticsError("invalid_data")
    return value


def fields_for(domain, end_hour, current="known", *, status="loading", reason="none"):
    source = "unknown" if status == "unsupported" else "unavailable" if status == "error" else "known"
    result = dict(source=source, status=status, reason=reason, current_status=current,
                  window_end_hour=end_hour, valid_mask=0, packed_q="", flat=False,
                  axis_min_text="", axis_max_text="", unit=domain.unit or "",
                  start_text=datetime.fromtimestamp((end_hour - 24) * 3600, timezone.utc).astimezone(ZoneInfo(domain.zone)).isoformat(timespec="seconds"),
                  end_text=datetime.fromtimestamp(end_hour * 3600, timezone.utc).astimezone(ZoneInfo(domain.zone)).isoformat(timespec="seconds"),
                  zone_text=domain.zone)
    if any(not text_valid(result[key], limit) for key, limit in LIMITS.items()):
        result.update(source="unknown", status="unsupported", reason="label_unrepresentable")
        result.update({key: "" for key in ("unit", "start_text", "end_text", "zone_text")})
    return result


def validate_fields(value):
    keys = {"source", "status", "reason", "current_status", "window_end_hour", "valid_mask", "packed_q", "flat"} | LIMITS.keys()
    if type(value) is not dict or set(value) != keys:
        raise StatisticsError("fields")
    source, status, reason = value["source"], value["status"], value["reason"]
    valid = ((source, status, reason) in (("known", "loading", "none"), ("known", "ready", "none"), ("known", "empty", "no_data"))
             or source == "unknown" and status == "unsupported" and reason in UNSUPPORTED
             or source == "unavailable" and status == "error" and reason in ERRORS)
    if (not valid or value["current_status"] not in ("known", "unknown", "unavailable")
            or not integer(value["window_end_hour"], 24, 0xFFFFFFFF)
            or not integer(value["valid_mask"], 0, 0xFFFFFF) or type(value["flat"]) is not bool
            or any(not text_valid(value[key], limit, ascii_only=key.startswith("axis_")) for key, limit in LIMITS.items())):
        raise StatisticsError("fields")
    context = ("unit", "start_text", "end_text", "zone_text")
    if reason == "label_unrepresentable":
        if any(value[key] for key in context):
            raise StatisticsError("labels")
    elif not all(value[key] for key in context[1:]):
        raise StatisticsError("labels")
    if status != "ready":
        if value["valid_mask"] or value["packed_q"] != "" or value["flat"] or value["axis_min_text"] or value["axis_max_text"]:
            raise StatisticsError("empty")
        return
    packed = value["packed_q"]
    if (not value["valid_mask"] or type(packed) is not str or re.fullmatch("[0-9a-f]{288}", packed) is None
            or not value["axis_min_text"] or not value["axis_max_text"]):
        raise StatisticsError("points")
    for index in range(24):
        a, b, c = (int(packed[index * 12 + offset:index * 12 + offset + 4], 16) for offset in (0, 4, 8))
        if value["valid_mask"] & (1 << index):
            if not 0 <= a <= b <= c <= 1000 or value["flat"] and (a, b, c) != (500, 500, 500):
                raise StatisticsError("points")
        elif (a, b, c) != (0, 0, 0):
            raise StatisticsError("points")


@dataclass(frozen=True)
class StatisticsObservation:
    fields: dict

    @property
    def available(self):
        return self.fields["source"] == "known"

    def descriptor(self):
        return dict(self.fields)

    def eligible(self, _domain):
        return 0


def dataset_digest(metadata, points):
    # Full finite values participate, including changes hidden by quantization.
    return hashlib.sha256(json.dumps((metadata, points), ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
