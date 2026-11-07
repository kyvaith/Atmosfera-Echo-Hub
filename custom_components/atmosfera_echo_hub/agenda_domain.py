"""Bounded Calendar observations; no calendar writes or retained provider list."""

from bisect import bisect_left
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
from zoneinfo import ZoneInfo

from .text import plain_text

ACTION = {"kind": "control", "control": "panel", "property": "agenda"}
CAPS = {"info_type": "agenda", "agenda_version": 1}
LIMITS = {"summary": 96, "start_text": 40, "end_text": 40, "zone_text": 48,
          "location": 64, "description": 32}


class AgendaError(ValueError):
    """Unsupported source or unrepresentable event, without private values."""


def resolve_calendar(hass, entity_id):
    from homeassistant.components.calendar import CalendarEntity, DATA_COMPONENT
    component = getattr(hass, "data", {}).get(DATA_COMPONENT)
    getter = getattr(component, "get_entity", None)
    entity = getter(entity_id) if callable(getter) else None
    if not isinstance(entity, CalendarEntity):
        raise AgendaError("source")
    return entity


@dataclass(frozen=True, eq=False)
class AgendaDomain:
    # Private source identity is never part of descriptor, deepcopy or wire.
    entity: object
    zone: str
    registry: tuple | None
    family = "info"

    def __eq__(self, other):
        return (isinstance(other, AgendaDomain) and self.entity is other.entity
                and self.zone == other.zone and self.registry == other.registry)

    @classmethod
    def from_ha(cls, hass, state):
        from homeassistant.helpers import entity_registry as er
        if not state.entity_id.startswith("calendar."):
            raise AgendaError("source")
        entity = resolve_calendar(hass, state.entity_id)
        registry = er.async_get(hass).async_get(state.entity_id)
        if registry is not None and getattr(registry, "disabled_by", None) is not None:
            raise AgendaError("disabled")
        signature = None if registry is None else tuple(getattr(registry, key, None) for key in
            ("id", "entity_id", "unique_id", "platform", "config_entry_id", "device_id"))
        zone = getattr(hass.config, "time_zone", None)
        if not text_valid(zone, 48) or not zone:
            raise AgendaError("zone")
        try:
            ZoneInfo(zone)
        except (ValueError, KeyError):
            raise AgendaError("zone") from None
        return cls(entity, zone, signature)

    def descriptor(self):
        return dict(CAPS)


def text_valid(value, maximum):
    try:
        return type(value) is str and len(value.encode("utf8")) <= maximum and all(c.isprintable() for c in value)
    except UnicodeError:
        return False


def integer(value, low, high):
    return type(value) is int and low <= value <= high


def empty_fields(source="known", status="loading", request_seq=0):
    return dict(source=source, status=status, request_seq=request_seq, index=None, count=0, has_more=False,
                all_day=None, truncated_fields=0, **{key: "" for key in LIMITS})


def validate_fields(fields):
    if type(fields) is not dict or set(fields) != set(empty_fields()):
        raise AgendaError("fields")
    if (fields["source"] not in ("known", "unknown", "unavailable")
            or fields["status"] not in ("loading", "ready", "error", "unknown")
            or not integer(fields["request_seq"], 0, 2147483647)
            or not integer(fields["count"], 0, 16) or type(fields["has_more"]) is not bool
            or not integer(fields["truncated_fields"], 0, 7)
            or any(not text_valid(fields[key], limit) for key, limit in LIMITS.items())):
        raise AgendaError("fields")
    if (fields["source"] == "known") == (fields["status"] == "unknown"):
        raise AgendaError("source")
    present = fields["source"] == "known" and fields["status"] == "ready" and fields["count"] > 0
    if present:
        if (not integer(fields["index"], 0, fields["count"] - 1) or type(fields["all_day"]) is not bool
                or any(not fields[key] for key in ("start_text", "end_text", "zone_text"))
                or fields["has_more"] and fields["count"] != 16):
            raise AgendaError("event")
    elif (fields["index"] is not None or fields["count"] != 0 or fields["has_more"]
          or fields["all_day"] is not None or fields["truncated_fields"] != 0
          or any(fields[key] for key in LIMITS)):
        raise AgendaError("empty")


def window(now, zone):
    local = now.astimezone(ZoneInfo(zone))
    return local, datetime.combine(local.date() + timedelta(days=7), time(), ZoneInfo(zone))


def _event_date(value, all_day, zone):
    if type(value) is not str:
        raise AgendaError("date")
    try:
        if all_day:
            parsed = date.fromisoformat(value)
            return parsed, datetime.combine(parsed, time(), zone)
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError
        local = parsed.astimezone(zone)
        return local, local
    except (ValueError, OverflowError):
        raise AgendaError("date") from None


def _excerpt(value, limit):
    if value is None:
        value = ""
    if type(value) is not str:
        raise AgendaError("text")
    # Normalize one provider string at a time; only its excerpt and digest survive.
    value.encode("utf8")
    text = plain_text(value, len(value))
    text = "".join(c for c in text if c.isprintable())
    encoded = text.encode("utf8")
    if len(encoded) <= limit:
        return text, False
    return encoded[:limit - 3].decode("utf8", errors="ignore") + "…", True


@dataclass(frozen=True)
class AgendaEvent:
    order: tuple
    digest: str
    fields: dict


def bounded_events(events, start, end, zone_name):
    """Select the first 16 without sorting/copying or mutating Core's list."""
    if type(events) is not list:
        raise AgendaError("events")
    zone = ZoneInfo(zone_name)
    rows, more = [], False
    begin_utc, end_utc = start.astimezone(timezone.utc), end.astimezone(timezone.utc)
    for position, event in enumerate(events):
        if type(event) is not dict or type(event.get("all_day")) is not bool:
            raise AgendaError("event")
        if event.get("status") == "cancelled":
            continue
        all_day = event["all_day"]
        first, first_time = _event_date(event.get("start"), all_day, zone)
        last, last_time = _event_date(event.get("end"), all_day, zone)
        first_utc, last_utc = first_time.astimezone(timezone.utc), last_time.astimezone(timezone.utc)
        if last_utc < first_utc or all_day and last_utc == first_utc:
            raise AgendaError("duration")
        if last_utc <= begin_utc or first_utc >= end_utc:
            continue
        order = first_utc, last_utc, position
        # No normalized copy of an event beyond the retained boundary.
        if len(rows) == 16 and order >= rows[-1].order:
            more = True
            continue
        fields = {"start_text": first.isoformat(),
                  "end_text": (last - timedelta(days=1)).isoformat() if all_day else last.isoformat(),
                  "zone_text": zone_name, "all_day": all_day, "truncated_fields": 0}
        for key, bit in (("summary", 1), ("location", 2), ("description", 4)):
            fields[key], shortened = _excerpt(event.get(key), LIMITS[key])
            if shortened:
                fields["truncated_fields"] |= bit
        if any(not text_valid(fields[key], LIMITS[key]) for key in ("start_text", "end_text", "zone_text")):
            raise AgendaError("date_size")
        # Include full text beyond excerpts and occurrence identity; no raw values retained.
        semantic = [event.get(key) for key in ("start", "end", "all_day", "summary", "location",
                                              "description", "uid", "recurrence_id", "rrule", "status")]
        digest = hashlib.sha256(json.dumps(semantic, ensure_ascii=False, separators=(",", ":"),
                                            allow_nan=False).encode("utf8")).hexdigest()
        row = AgendaEvent(order, digest, fields)
        index = bisect_left([item.order for item in rows], order)
        if len(rows) == 16:
            rows.pop()
            more = True
        rows.insert(index, row)
    return rows, more


@dataclass(frozen=True)
class AgendaObservation:
    fields: dict

    @property
    def available(self):
        return self.fields["source"] == "known"

    def descriptor(self):
        return dict(self.fields)

    def eligible(self, domain):
        return 0


def agenda_metadata(hass, state):
    try:
        AgendaDomain.from_ha(hass, state)
    except (AgendaError, ImportError):
        return {}
    return {"agenda": {"version": 1, "read_only": True}}
