"""Bounded passive observations and lock-only policy; no service dispatch."""

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .text import plain_text

CONTEXT_INFO_TYPES = frozenset(("person", "sun"))
INFO_DOMAINS = frozenset(("sensor", "binary_sensor", "calendar", "alarm_control_panel")) | CONTEXT_INFO_TYPES
EXTRA_DOMAINS = {"info": INFO_DOMAINS, "lock": frozenset(("lock",))}
INFO_ACTION = {"kind": "control", "control": "panel", "property": "info"}
LOCK_ACTION = {"kind": "control", "control": "panel", "property": "lock"}
SOURCES = frozenset(("known", "unknown", "unavailable"))
TEXT_STATUS = frozenset(("value", "empty", "invalid", "too_long", "unknown"))
ALARM_PHASES = frozenset(("disarmed", "armed_home", "armed_away", "armed_night", "armed_vacation",
    "armed_custom_bypass", "pending", "arming", "disarming", "triggered", "unknown"))
LOCK_PHASES = frozenset(("locked", "unlocked", "locking", "unlocking", "open", "opening", "jammed", "unknown"))


class ExtraPanelError(ValueError):
    """Unsupported metadata or malformed closed observation."""


def text_valid(value, limit):
    return (type(value) is str and all(c.isprintable() and not 0xD800 <= ord(c) <= 0xDFFF for c in value)
            and len(value.encode("utf8")) <= limit)


def complete_text(raw, limit):
    """Never return a prefix as a complete value; status remains explicit."""
    if not isinstance(raw, str) or any(0xD800 <= ord(c) <= 0xDFFF for c in raw):
        return "invalid", ""
    if len(raw) > 16384:
        return "too_long", ""
    value = plain_text(raw, len(raw) * 2 + 1)
    if not all(c.isprintable() for c in value):
        return "invalid", ""
    if len(value.encode("utf8")) > limit:
        return "too_long", ""
    return ("value" if value else "empty"), value


def excerpt(raw, limit):
    if raw is None:
        return "", False
    status, value = complete_text(raw, 65536)
    if status not in {"value", "empty"}:
        raise ExtraPanelError("calendar_text")
    if len(value.encode("utf8")) <= limit:
        return value, False
    return value.encode("utf8")[:limit - 3].decode("utf8", errors="ignore") + "…", True


def ha_zone(hass):
    name = getattr(getattr(hass, "config", None), "time_zone", None)
    if not text_valid(name, 48):
        return None
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        return None


def updated_text(hass, state):
    stamp, zone = getattr(state, "last_updated", None), ha_zone(hass)
    if not isinstance(stamp, datetime) or stamp.tzinfo is None or zone is None:
        return ""
    value = stamp.astimezone(zone).isoformat(timespec="seconds")
    return value if text_valid(value, 48) else ""


@dataclass(frozen=True)
class ExtraDomain:
    family: str
    info_type: str | None = None
    device_class: str | None = None
    lock: bool = False

    def __post_init__(self):
        if (self.family not in EXTRA_DOMAINS or type(self.lock) is not bool
                or self.family == "lock" and (self.info_type is not None or self.device_class is not None)
                or self.family == "info" and (self.lock or self.info_type not in {"sensor", "binary_sensor", "calendar", "alarm", "person", "sun"})
                or self.device_class is not None and (type(self.device_class) is not str
                    or re.fullmatch(r"[a-z][a-z0-9_]{0,31}", self.device_class) is None)
                or self.info_type in {"calendar", "alarm", "person", "sun"} and self.device_class is not None):
            raise ExtraPanelError("caps")

    @classmethod
    def from_ha(cls, hass, state):
        domain = state.entity_id.partition(".")[0]
        if domain == "lock":
            return cls("lock", lock=hass.services.has_service("lock", "lock"))
        if domain not in INFO_DOMAINS:
            raise ExtraPanelError("entity")
        device_class = state.attributes.get("device_class") if domain in {"sensor", "binary_sensor"} else None
        if device_class is not None:
            if not isinstance(device_class, str) or re.fullmatch(r"[a-z][a-z0-9_]{0,31}", device_class) is None:
                device_class = None
            else:
                device_class = str(device_class)
        return cls("info", "alarm" if domain == "alarm_control_panel" else domain, device_class)

    def descriptor(self):
        return {"lock": self.lock} if self.family == "lock" else {"info_type": self.info_type, "device_class": self.device_class}

    @classmethod
    def from_descriptor(cls, family, caps):
        expected = {"lock"} if family == "lock" else {"info_type", "device_class"}
        if type(caps) is not dict or set(caps) != expected:
            raise ExtraPanelError("caps")
        return cls(family, **caps)

    @property
    def fingerprint(self):
        return hashlib.sha256(json.dumps([self.family, self.descriptor()], sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def service_action(self, entity_id, operation, target=None):
        if self.family != "lock" or not self.lock or entity_id.partition(".")[0] != "lock" or operation != "lock" or target is not None:
            raise ExtraPanelError("operation")
        return "lock", "lock", {}


def calendar_fields(hass, state, source):
    blank = dict(event="unknown", active=None, summary="", start_text="", end_text="", zone_text="",
                 all_day=None, location="", description="", truncated_fields=0)
    if source != "known":
        return blank
    attrs = state.attributes
    required = {"message", "all_day", "start_time", "end_time"}
    if state.state == "off" and not required.intersection(attrs):
        return blank | {"event": "none"}
    try:
        zone = ha_zone(hass)
        if (state.state not in {"on", "off"} or not required <= attrs.keys() or zone is None
                or type(attrs["all_day"]) is not bool or not isinstance(attrs["message"], str)):
            raise ExtraPanelError("calendar")
        stamps = []
        for key in ("start_time", "end_time"):
            value = attrs[key]
            if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}", value):
                raise ExtraPanelError("calendar_date")
            stamps.append(datetime.fromisoformat(value))
        start, end = stamps
        if attrs["all_day"]:
            if start.time() != datetime.min.time() or end.time() != datetime.min.time() or end.date() <= start.date():
                raise ExtraPanelError("calendar_date")
            first, last = start.date().isoformat(), (end.date() - timedelta(days=1)).isoformat()
        else:
            # These are Core's already-local wall fields. Keep both complete;
            # do not reinterpret them as UTC or infer elapsed time across folds.
            if end.date() < start.date():
                raise ExtraPanelError("calendar_date")
            first, last = start.isoformat(sep=" "), end.isoformat(sep=" ")
        result = blank | dict(event="present", active=state.state == "on", all_day=attrs["all_day"],
                              start_text=first, end_text=last, zone_text=zone.key)
        for bit, output, key, limit in ((1, "summary", "message", 128), (2, "location", "location", 96), (4, "description", "description", 64)):
            result[output], shortened = excerpt(attrs.get(key), limit)
            if shortened:
                result["truncated_fields"] |= bit
        return result
    except (ValueError, OverflowError, TypeError):
        return blank | {"event": "invalid"}


@dataclass(frozen=True)
class ExtraObservation:
    family: str
    fields: dict

    @property
    def available(self):
        return self.fields["source"] == "known"

    @property
    def command_state(self):
        return (self.fields["source"], self.fields["phase"]) if self.family == "lock" else (self.fields["source"],)

    def descriptor(self):
        return deepcopy(self.fields)

    def eligible(self, domain):
        return int(domain.family == "lock" and domain.lock and self.available and self.fields["phase"] in {"unlocked", "open", "jammed"})

    def can_command(self, domain, operation, target):
        return operation == "lock" and target is None and bool(self.eligible(domain))

    def matches(self, operation, target):
        return self.family == "lock" and operation == "lock" and target is None and self.available and self.fields["phase"] == "locked"

    @classmethod
    def from_ha(cls, hass, state, domain, language=None):
        if domain.info_type in CONTEXT_INFO_TYPES:
            from .info_context_domain import context_fields
            return cls.from_descriptor(domain, context_fields(hass, state, domain.info_type, language))
        source = state.state if state.state in {"unknown", "unavailable"} else "known"
        fields = {"source": source, "updated_text": updated_text(hass, state)}
        if domain.family == "lock":
            fields["phase"] = state.state if source == "known" and state.state in LOCK_PHASES else "unknown"
        elif domain.info_type == "calendar":
            fields.update(calendar_fields(hass, state, source))
        elif domain.info_type == "sensor":
            status, value = complete_text(state.state, 96) if source == "known" else ("unknown", "")
            unit_status, unit = complete_text(state.attributes.get("unit_of_measurement") or "", 24)
            numeric = bool(unit or state.attributes.get("state_class")) and domain.device_class not in {"enum", "date", "timestamp"}
            if source == "known" and status == "value" and numeric:
                try:
                    if not Decimal(value).is_finite():
                        raise InvalidOperation
                except InvalidOperation:
                    status, value = "invalid", ""
            if unit_status not in {"value", "empty"}:
                status, value, unit = (unit_status if source == "known" else "unknown"), "", ""
            fields.update(value_status=status, value_text=value, unit_text=unit)
        else:
            raw = state.state
            recognized = raw in ({"on", "off"} if domain.info_type == "binary_sensor" else ALARM_PHASES - {"unknown"})
            status, text = ("unknown", "") if source != "known" else ("invalid", "")
            if source == "known" and recognized:
                # Reuse cached HA translations without the tile caption truncation.
                from .cards import _translate_state_for_locale
                from .formatting import binary_fallback, display_language
                fallback = binary_fallback(raw, domain.device_class, language) if domain.info_type == "binary_sensor" else None
                if domain.info_type == "binary_sensor" and domain.device_class == "moisture":
                    labels = ("Mokro", "Sucho") if display_language(language) == "pl" else ("Wet", "Dry")
                    fallback = labels[0 if raw == "on" else 1]
                translated = _translate_state_for_locale(hass, state, language, semantic_fallback=fallback)
                status, text = complete_text(translated, 96)
            fields.update(text_status=status, state_text=text)
            fields.update({"active": raw == "on" if recognized and source == "known" else None}
                          if domain.info_type == "binary_sensor" else {"phase": raw if recognized and source == "known" else "unknown"})
        return cls.from_descriptor(domain, fields)

    @classmethod
    def from_descriptor(cls, domain, fields):
        if type(fields) is not dict or fields.get("source") not in SOURCES or not text_valid(fields.get("updated_text"), 48):
            raise ExtraPanelError("state")
        if domain.info_type in CONTEXT_INFO_TYPES:
            from .info_context_domain import validate_context
            validate_context(domain.info_type, fields)
            return cls(domain.family, deepcopy(fields))
        required = {"source", "updated_text"}
        known = fields["source"] == "known"
        if domain.family == "lock":
            required |= {"phase"}
            if fields.get("phase") not in LOCK_PHASES or not known and fields["phase"] != "unknown":
                raise ExtraPanelError("phase")
        elif domain.info_type == "calendar":
            required |= {"event", "active", "summary", "start_text", "end_text", "zone_text", "all_day", "location", "description", "truncated_fields"}
            if (fields.get("event") not in {"present", "none", "invalid", "unknown"}
                    or type(fields.get("truncated_fields")) is not int or not 0 <= fields["truncated_fields"] <= 7
                    or any(not text_valid(fields.get(key), limit) for key, limit in
                           (("summary", 128), ("start_text", 40), ("end_text", 40), ("zone_text", 48), ("location", 96), ("description", 64)))):
                raise ExtraPanelError("calendar")
            if fields["event"] == "present":
                if (not known or type(fields.get("active")) is not bool or type(fields.get("all_day")) is not bool
                        or not all(fields[k] for k in ("start_text", "end_text", "zone_text"))):
                    raise ExtraPanelError("calendar")
            elif (fields.get("active") is not None or fields.get("all_day") is not None or fields["truncated_fields"] != 0
                    or any(fields[k] for k in ("summary", "start_text", "end_text", "zone_text", "location", "description"))
                    or (not known and fields["event"] != "unknown") or (known and fields["event"] == "unknown")):
                raise ExtraPanelError("calendar")
        else:
            sensor = domain.info_type == "sensor"
            status_key, text_key = ("value_status", "value_text") if sensor else ("text_status", "state_text")
            required |= {status_key, text_key, "unit_text" if sensor else "active" if domain.info_type == "binary_sensor" else "phase"}
            status, text = fields.get(status_key), fields.get(text_key)
            if (status not in TEXT_STATUS or not text_valid(text, 96)
                    or (status == "value") != bool(text) or not known and status != "unknown"
                    or known and status == "unknown" or sensor and not text_valid(fields.get("unit_text"), 24)):
                raise ExtraPanelError("text")
            if not sensor:
                if domain.info_type == "binary_sensor":
                    active = fields.get("active")
                    if (active is not None and type(active) is not bool or not known and active is not None
                            or known and active is None and status != "invalid"):
                        raise ExtraPanelError("active")
                elif (fields.get("phase") not in ALARM_PHASES or not known and fields["phase"] != "unknown"
                      or known and fields["phase"] == "unknown" and status != "invalid"):
                    raise ExtraPanelError("phase")
        if set(fields) != required:
            raise ExtraPanelError("fields")
        return cls(domain.family, deepcopy(fields))


def extra_metadata(hass, state, language=None):
    if state.entity_id.partition(".")[0] not in INFO_DOMAINS | {"lock"}:
        return {}
    domain = ExtraDomain.from_ha(hass, state)
    observed = ExtraObservation.from_ha(hass, state, domain, language)
    return {"extra_panel": {"version": 1, "panel_type": domain.family, "caps": domain.descriptor(),
            "fingerprint": domain.fingerprint, "state": observed.descriptor(),
            "available": observed.available, "eligible_actions": observed.eligible(domain)}}
