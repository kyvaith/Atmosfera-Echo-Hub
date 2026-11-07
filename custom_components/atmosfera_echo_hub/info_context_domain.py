"""Passive Person/Sun observations; HA owns time conversion and presence policy."""

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import re

from .extra_panel_domain import ExtraPanelError, complete_text, ha_zone, text_valid

TYPES = frozenset(("person", "sun"))
INPUT_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?(?:Z|[+-][0-9]{2}:[0-9]{2})")
WIRE_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{2}:[0-9]{2}")
NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")
PERSON_PHASES = frozenset(("home", "away", "zone", "unknown"))
SUN_PHASES = frozenset(("above_horizon", "below_horizon", "unknown"))
DATE_STATUS = frozenset(("value", "unknown", "invalid", "too_long"))
TEXT_STATUS = DATE_STATUS | {"empty"}


def _utcnow():
    return datetime.now(timezone.utc)


def _offset_valid(value):
    return value.endswith("Z") or int(value[-5:-3]) < 24 and int(value[-2:]) < 60


def valid_date(value):
    if not isinstance(value, str) or WIRE_DATE.fullmatch(value) is None or not _offset_valid(value):
        return False
    try:
        stamp = datetime.fromisoformat(value)
        return stamp.utcoffset() is not None
    except (ValueError, OverflowError):
        return False


def date_text(raw, zone, *, future=False, now=None):
    if raw is None:
        return "unknown", ""
    if isinstance(raw, str):
        if len(raw) > 40:
            return "too_long", ""
        if INPUT_DATE.fullmatch(raw) is None or not _offset_valid(raw):
            return "invalid", ""
        try:
            raw = datetime.fromisoformat(raw)
        except ValueError:
            return "invalid", ""
    if not isinstance(raw, datetime) or raw.tzinfo is None or zone is None:
        return "invalid", ""
    try:
        if raw.utcoffset() is None:
            return "invalid", ""
        # Compare the full source instant before choosing presentation precision.
        if future and raw.astimezone(timezone.utc) <= (now or _utcnow()).astimezone(timezone.utc):
            return "stale", ""
        text = raw.astimezone(zone).isoformat(timespec="seconds")
        return ("value", text) if valid_date(text) else ("invalid", "")
    except (ValueError, OverflowError, TypeError):
        return "invalid", ""


def angle_text(raw, minimum, maximum):
    if raw is None:
        return "unknown", ""
    if type(raw) not in (str, int, float, Decimal):
        return "invalid", ""
    text = str(raw)
    if len(text) > 128:
        return "too_long", ""
    if NUMBER.fullmatch(text) is None:
        return "invalid", ""
    try:
        value = Decimal(text)
        if not value.is_finite() or not Decimal(minimum) <= value <= Decimal(maximum):
            return "invalid", ""
    except InvalidOperation:
        return "invalid", ""
    return ("value", text) if text_valid(text, 24) else ("too_long", "")


def context_fields(hass, state, info_type, language=None):
    raw = state.state
    source = raw if raw in ("unknown", "unavailable") else "known"
    zone = ha_zone(hass)
    _, updated = date_text(getattr(state, "last_updated", None), zone)
    fields = {"source": source, "updated_text": updated, "phase": "unknown", "zone_text": ""}
    if info_type == "person":
        fields.update(text_status="unknown", state_text="", changed_status="unknown", changed_text="")
    else:
        for prefix in ("next_rising", "next_setting", "elevation", "azimuth"):
            fields[prefix+"_status"], fields[prefix+"_text"] = "unknown", ""
    if source != "known":
        return fields
    fields["zone_text"] = zone.key if zone else ""
    if info_type == "person":
        if raw in ("home", "not_home"):
            from .cards import _translate_state_for_locale
            from .formatting import person_state_text
            fields["phase"] = "home" if raw == "home" else "away"
            text = _translate_state_for_locale(hass, state, language,
                semantic_fallback=person_state_text(raw, language))
        else:
            text = raw
            if isinstance(raw, str) and raw.strip():
                fields["phase"] = "zone"
        fields["text_status"], fields["state_text"] = complete_text(text, 96)
        fields["changed_status"], fields["changed_text"] = date_text(getattr(state, "last_changed", None), zone)
    else:
        if isinstance(raw, str) and raw in SUN_PHASES - {"unknown"}:
            fields["phase"] = raw
        now = _utcnow()
        for prefix in ("next_rising", "next_setting"):
            fields[prefix+"_status"], fields[prefix+"_text"] = date_text(state.attributes.get(prefix), zone, future=True, now=now)
        for prefix, minimum, maximum in (("elevation", -90, 90), ("azimuth", 0, 360)):
            fields[prefix+"_status"], fields[prefix+"_text"] = angle_text(state.attributes.get(prefix), minimum, maximum)
    return fields


def validate_context(info_type, fields):
    known = fields["source"] == "known"
    required = {"source", "updated_text", "phase", "zone_text"}
    if fields["updated_text"] and not valid_date(fields["updated_text"]):
        raise ExtraPanelError("updated_date")
    if not text_valid(fields.get("zone_text"), 48) or not known and fields["zone_text"]:
        raise ExtraPanelError("zone")
    phases = PERSON_PHASES if info_type == "person" else SUN_PHASES
    if fields.get("phase") not in phases or not known and fields["phase"] != "unknown":
        raise ExtraPanelError("phase")
    pairs = [("text", "state_text", TEXT_STATUS, 96), ("changed", "changed_text", DATE_STATUS, 40)] if info_type == "person" else [
        ("next_rising", "next_rising_text", DATE_STATUS | {"stale"}, 40),
        ("next_setting", "next_setting_text", DATE_STATUS | {"stale"}, 40),
        ("elevation", "elevation_text", DATE_STATUS, 24), ("azimuth", "azimuth_text", DATE_STATUS, 24)]
    for prefix, text_key, statuses, limit in pairs:
        status_key = prefix+"_status"; required |= {status_key, text_key}
        status, text = fields.get(status_key), fields.get(text_key)
        if (status not in statuses or not text_valid(text, limit) or (status == "value") != bool(text)
                or not known and status != "unknown"):
            raise ExtraPanelError("context_value")
        if status == "value":
            if prefix in {"changed", "next_rising", "next_setting"} and (not valid_date(text) or not fields["zone_text"]):
                raise ExtraPanelError("context_date")
            if prefix in {"elevation", "azimuth"}:
                minimum, maximum = (-90, 90) if prefix == "elevation" else (0, 360)
                if angle_text(text, minimum, maximum) != ("value", text):
                    raise ExtraPanelError("context_angle")
    if info_type == "person" and known and (fields["text_status"] == "unknown"
            or fields["phase"] == "unknown" and fields["text_status"] not in {"invalid", "empty"}):
        raise ExtraPanelError("person_phase")
    if set(fields) != required:
        raise ExtraPanelError("context_fields")
