"""Bounded display formatting; independent of Home Assistant and layout schemas."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from collections.abc import Mapping
from decimal import (
    ROUND_HALF_EVEN,
    Context,
    Decimal,
    DivisionByZero,
    InvalidOperation,
    Overflow,
    localcontext,
)
from typing import Any

from .text import plain_text

MAX_PRECISION = 6
MAX_NUMBER = Decimal("1e15")
MAX_DURATION_SECONDS = Decimal(10 * 366 * 86400)
# Never inherit a caller's rounding, exponent limits, flags or signal traps.
# localcontext copies this template for parsing and every arithmetic operation.
_DECIMAL_CONTEXT = Context(
    prec=32, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
    capitals=1, clamp=0, flags=[], traps=[InvalidOperation, DivisionByZero, Overflow],
)
_NUMBER = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?$")
_NON_FINITE = frozenset(("nan", "+nan", "-nan", "snan", "inf", "+inf", "-inf",
                         "infinity", "+infinity", "-infinity"))
_TEXT_CLASSES = frozenset(("enum", "date", "timestamp", "uptime"))
_SECONDS = {"μs": Decimal("0.000001"), "ms": Decimal("0.001"), "s": Decimal(1),
            "min": Decimal(60), "h": Decimal(3600), "d": Decimal(86400),
            "w": Decimal(604800)}
_STATE_LABELS = {
    "en": {"unknown": "Unknown", "unavailable": "Unavailable", "out_of_range": "Out of range"},
    "pl": {"unknown": "Nieznany", "unavailable": "Niedostępny", "out_of_range": "Poza zakresem"},
}


def display_language(language: Any) -> str:
    """Select the product's supported display language without global locale state."""
    if isinstance(language, str) and language.replace("_", "-").split("-", 1)[0].lower() == "pl":
        return "pl"
    return "en"


def state_label(state: str, language: Any = None) -> str:
    """Localize exceptional states; they must never imply a safe binary state."""
    return _STATE_LABELS[display_language(language)][state]


def binary_fallback(state: str, device_class: Any, language: Any = None) -> str | None:
    """Fallback semantics only for real on/off values and known binary classes."""
    if state not in ("on", "off") or not isinstance(device_class, str):
        return None
    polish = display_language(language) == "pl"
    if device_class in {"door", "window", "opening", "garage_door"}:
        labels = ("Otwarte", "Zamknięte") if polish else ("Open", "Closed")
    elif device_class in {"motion", "occupancy"}:
        labels = ("Wykryto", "Nie wykryto") if polish else ("Detected", "Clear")
    elif device_class == "presence":
        labels = ("Obecność", "Brak obecności") if polish else ("Present", "Away")
    else:
        return None
    return labels[0 if state == "on" else 1]


def _parse_number(state: str) -> Decimal | None:
    if len(state) > 128 or not _NUMBER.fullmatch(state):
        return None
    try:
        with localcontext(_DECIMAL_CONTEXT):
            value = Decimal(state)
        return value if value.is_finite() else None
    except InvalidOperation:
        return None


def sensor_precision(state: str, registry_options: Any = None) -> int:
    """Read public sensor registry options, then infer bounded state precision.

    HA 2026.7.1 stores both options in RegistryEntry.options['sensor']; its
    public async_rounded_state uses display_precision before the suggestion.
    suggested_display_precision is not a guaranteed state attribute.
    """
    options = registry_options.get("sensor") if isinstance(registry_options, Mapping) else None
    if isinstance(options, Mapping):
        for key in ("display_precision", "suggested_display_precision"):
            value = options.get(key)
            if type(value) is int:
                return max(0, min(MAX_PRECISION, value))
    if (value := _parse_number(state)) is not None:
        return max(0, min(MAX_PRECISION, -value.as_tuple().exponent))
    return 0


def _decimal_text(value: Decimal, precision: int, language: Any) -> str:
    with localcontext(_DECIMAL_CONTEXT):
        # Decimal formatting rounds without losing the raw state's decimal
        # precision through float conversion. z removes negative zero.
        text = format(value, f"z.{precision}f")
    return text.replace(".", ",") if display_language(language) == "pl" else text


def _duration(value: Decimal, unit: str, precision: int, language: Any) -> str:
    with localcontext(_DECIMAL_CONTEXT):
        return _duration_parts(value, unit, precision, language)


def _duration_parts(value: Decimal, unit: str, precision: int, language: Any) -> str:
    # First honor precision in HA's current display unit. Months/years have no
    # fixed conversion here; their units stay on the ordinary numeric path.
    rounded = Decimal(_decimal_text(value, precision, "en"))
    seconds = rounded * _SECONDS[unit]
    if seconds.copy_abs() > MAX_DURATION_SECONDS:
        return state_label("out_of_range", language)
    if seconds.copy_abs() < 1 and seconds != 0:
        # HA uses Greek mu (U+03BC), absent from the product's GF_Latin_Core
        # font subset. The ASCII unit alias avoids silently losing that glyph.
        displayed_unit = "us" if unit == "μs" else unit
        return plain_text(f"{_decimal_text(value, precision, language)} {displayed_unit}", 40)
    sign = "-" if seconds < 0 else ""
    remaining = seconds.copy_abs()
    parts = []
    for amount, suffix in ((86400, "d"), (3600, "h"), (60, "min")):
        count = int(remaining // amount)
        remaining %= amount
        if count:
            parts.append(f"{count} {suffix}")
        if len(parts) == 2:
            break
    else:
        if remaining or not parts:
            places = max(0, min(MAX_PRECISION, -remaining.as_tuple().exponent))
            parts.append(f"{_decimal_text(remaining, places, language)} s")
    return plain_text(sign + " ".join(parts), 40)


def sensor_text(
    state: Any,
    unit: Any = "",
    device_class: Any = None,
    language: Any = None,
    registry_options: Any = None,
) -> str | None:
    """Format numeric readings, or return None for translated custom text states.

    Units come from the runtime state, already converted by HA. This formatter
    never changes units for general measurements, writes options, or mutates a
    source state. Numeric output and compact duration output stay within 40 chars.
    """
    if not isinstance(state, str):
        return state_label("unknown", language)
    raw = state.strip()
    if raw in ("unknown", "unavailable"):
        return state_label(raw, language)
    if isinstance(device_class, str) and device_class in _TEXT_CLASSES:
        return None
    unit = plain_text(unit, 20) if isinstance(unit, str) else ""
    value = _parse_number(raw)
    if value is None:
        # A syntactically finite numeric value outside the input/Decimal
        # representation budget is different from missing or malformed data.
        if _NUMBER.fullmatch(raw):
            return state_label("out_of_range", language)
        numeric_looking = bool(raw) and (raw[0] in "+-.0123456789")
        if not raw or raw.lower() in _NON_FINITE or unit or numeric_looking:
            return state_label("unknown", language)
        return None
    if value.copy_abs() > MAX_NUMBER:
        return state_label("out_of_range", language)
    precision = sensor_precision(raw, registry_options)
    if device_class == "duration" and unit in _SECONDS:
        return _duration(value, unit, precision, language)
    return plain_text(f"{_decimal_text(value, precision, language)} {unit}", 40)


def sun_event_text(
    state: Any,
    attributes: Any,
    time_zone: Any,
    language: Any = None,
    *,
    now: datetime | None = None,
) -> str:
    """Project HA's next events; never calculate astronomy or guess a timezone.

    Both aware event instants are required to identify the next event honestly.
    Dates are explicit DD.MM; no relative day label can become stale at midnight.
    Fixed 24-hour output is independent of the host's process locale and timezone.
    """
    if state in ("unknown", "unavailable"):
        return state_label(state, language)
    if (state not in ("above_horizon", "below_horizon")
            or not isinstance(attributes, Mapping)
            or type(time_zone) is not str or not 0 < len(time_zone) <= 128):
        return state_label("unknown", language)
    try:
        zone = ZoneInfo(time_zone)
        reference = now if now is not None else datetime.now(UTC)
        if not isinstance(reference, datetime) or reference.utcoffset() is None:
            return state_label("unknown", language)
        reference = reference.astimezone(UTC)
        events = []
        for name in ("next_rising", "next_setting"):
            raw = attributes.get(name)
            if type(raw) is not str or not 0 < len(raw) <= 128:
                return state_label("unknown", language)
            instant = datetime.fromisoformat(raw)
            if instant.utcoffset() is None:
                return state_label("unknown", language)
            instant = instant.astimezone(UTC)
            if instant <= reference:
                return state_label("unknown", language)
            events.append((instant, name))
        if events[0][0] == events[1][0]:
            return state_label("unknown", language)
        instant, name = min(events)
        local = instant.astimezone(zone)
    except (ValueError, TypeError, OverflowError, ZoneInfoNotFoundError):
        return state_label("unknown", language)
    labels = {"next_rising": ("Rise", "Wsch."), "next_setting": ("Set", "Zach.")}
    label = labels[name][display_language(language) == "pl"]
    return plain_text(f"{label} {local:%d.%m %H:%M}", 40)
