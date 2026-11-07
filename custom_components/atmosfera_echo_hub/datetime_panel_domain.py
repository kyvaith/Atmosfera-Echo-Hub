"""Closed wall-date/time tuples; HA remains the authority for observed values."""

from dataclasses import dataclass, field
from datetime import date
import hashlib
import json
import re

from .extra_panel_domain import ha_zone, text_valid
from .info_context_domain import date_text, valid_date

ACTION = {"kind": "control", "control": "panel", "property": "datetime"}
FIELDS = ("year", "month", "day", "hour", "minute", "second")
MODES = {"date": (True, True, True, False, False, False),
         "time": (False, False, False, True, True, True), "datetime": (True,) * 6}
DATE = r"([0-9]{1,4})-([0-9]{2})-([0-9]{2})"
TIME = r"([0-9]{2}):([0-9]{2}):([0-9]{2})"
RAW = {"date": re.compile(DATE), "time": re.compile(TIME), "datetime": re.compile(DATE + " " + TIME)}


class DatetimePanelError(ValueError):
    """An unsupported capability or malformed exact tuple."""


def valid_tuple(value, mode=None):
    if type(value) is not dict or set(value) != set(FIELDS):
        return False
    mask = tuple(value[key] is not None for key in FIELDS)
    if mode is None:
        mode = next((name for name, candidate in MODES.items() if candidate == mask), None)
    if not isinstance(mode, str) or mode not in MODES or mask != MODES[mode]:
        return False
    if any(type(value[key]) is not int for key in FIELDS if value[key] is not None):
        return False
    try:
        if mode != "time":
            date(value["year"], value["month"], value["day"])
        if mode != "date" and not (0 <= value["hour"] <= 23 and 0 <= value["minute"] <= 59 and 0 <= value["second"] <= 59):
            return False
    except (ValueError, OverflowError):
        return False
    return True


@dataclass(frozen=True)
class DatetimeDomain:
    mode: str
    can_set: bool
    zone_text: str = field(default="", compare=False)
    family = "datetime"

    @classmethod
    def from_descriptor(cls, value):
        if (type(value) is not dict or set(value) != {"mode", "can_set", "zone_text"}
                or not isinstance(value["mode"], str) or value["mode"] not in MODES or type(value["can_set"]) is not bool
                or not text_valid(value["zone_text"], 48)
                or value["mode"] != "datetime" and value["zone_text"]):
            raise DatetimePanelError("caps")
        return cls(**value)

    @classmethod
    def from_ha(cls, hass, state):
        if state.entity_id.partition(".")[0] != "input_datetime":
            raise DatetimePanelError("domain")
        has_date, has_time = (state.attributes.get(name) for name in ("has_date", "has_time"))
        if type(has_date) is not bool or type(has_time) is not bool or not (has_date or has_time):
            raise DatetimePanelError("mode")
        mode = "datetime" if has_date and has_time else "date" if has_date else "time"
        zone = ha_zone(hass)
        text = zone.key if mode == "datetime" and zone else ""
        return cls.from_descriptor({"mode": mode, "can_set": hass.services.has_service("input_datetime", "set_datetime"),
                                    "zone_text": text if text_valid(text, 48) else ""})

    def descriptor(self):
        return {"mode": self.mode, "can_set": self.can_set, "zone_text": self.zone_text}

    @property
    def fingerprint(self):
        value = [self.family, {"mode": self.mode, "can_set": self.can_set}]
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def service_action(self, entity_id, operation, target):
        if (not self.can_set or operation != "set_datetime" or not valid_tuple(target, self.mode)
                or not entity_id.startswith("input_datetime.")):
            raise DatetimePanelError("target")
        data = {}
        if self.mode != "time":
            data["date"] = f'{target["year"]:04d}-{target["month"]:02d}-{target["day"]:02d}'
        if self.mode != "date":
            data["time"] = f'{target["hour"]:02d}:{target["minute"]:02d}:{target["second"]:02d}'
        return "input_datetime", "set_datetime", data


@dataclass(frozen=True)
class DatetimeObservation:
    source: str
    values: tuple
    updated_text: str = ""

    @property
    def available(self):
        return self.source == "known"

    @property
    def command_state(self):
        return self.source, self.values

    def target(self):
        return dict(zip(FIELDS, self.values))

    def descriptor(self):
        return {"source": self.source, **self.target(), "updated_text": self.updated_text}

    @classmethod
    def from_descriptor(cls, domain, value):
        if (type(value) is not dict or set(value) != {"source", "updated_text", *FIELDS}
                or value["source"] not in ("known", "unknown", "unavailable")
                or not isinstance(value["updated_text"], str)
                or value["updated_text"] and not valid_date(value["updated_text"])):
            raise DatetimePanelError("state")
        target = {key: value[key] for key in FIELDS}
        if ((value["source"] == "known" and not valid_tuple(target, domain.mode))
                or value["source"] != "known" and any(item is not None for item in target.values())):
            raise DatetimePanelError("state_tuple")
        return cls(value["source"], tuple(target.values()), value["updated_text"])

    @classmethod
    def from_ha(cls, hass, state, domain):
        _, updated = date_text(getattr(state, "last_updated", None), ha_zone(hass))
        source, values = "unknown", (None,) * 6
        raw = state.state
        if raw == "unavailable":
            source = "unavailable"
        elif isinstance(raw, str) and len(raw) <= 19:
            match = RAW[domain.mode].fullmatch(raw)
            if match:
                groups = iter(int(item) for item in match.groups())
                target = {key: next(groups) if present else None for key, present in zip(FIELDS, MODES[domain.mode])}
                if (valid_tuple(target, domain.mode) and all(type(state.attributes.get(key)) is int
                        and state.attributes[key] == value for key, value in target.items() if value is not None)):
                    source, values = "known", tuple(target.values())
        return cls(source, values, updated)

    def eligible(self, domain):
        return int(self.available and domain.can_set)

    def can_command(self, domain, operation, target):
        return bool(self.eligible(domain) and operation == "set_datetime" and valid_tuple(target, domain.mode))

    def matches(self, operation, target):
        return self.available and operation == "set_datetime" and self.target() == target


def datetime_metadata(hass, state, language=None):
    try:
        domain = DatetimeDomain.from_ha(hass, state)
        observed = DatetimeObservation.from_ha(hass, state, domain)
    except DatetimePanelError:
        return {}
    return {"datetime_panel": {"version": 1, "panel_type": "datetime", "caps": domain.descriptor(),
            "fingerprint": domain.fingerprint, "state": observed.descriptor(), "available": observed.available,
            "eligible_actions": observed.eligible(domain)}}
