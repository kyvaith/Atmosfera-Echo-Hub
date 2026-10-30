"""Offline W04 prototype: exact bounded number lattice, without HA/session I/O."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

MAX_PLACES = 6
SCALE = 10**MAX_PLACES
MAX_ABSOLUTE = 10**12
MAX_MICRO = MAX_ABSOLUTE * SCALE
MAX_STEPS = 1_000_000
MAX_NUMERIC_TEXT = 64
MAX_UNIT_BYTES = 32
SCHEMA = "numeric_steps_v1"
_NUMBER = re.compile(r"[+-]?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]{1,3})?\Z", re.ASCII)
_FIELDS = frozenset(("schema", "min", "max", "step", "unit", "max_index"))


class NumericDomainError(ValueError):
    """Invalid value/domain; no implicit clamp, retry or device action."""


def _micro(raw: Any) -> int:
    """Parse Decimal exactly, then use bounded integer arithmetic exclusively."""
    if type(raw) not in (str, int, float, Decimal):
        raise NumericDomainError("numeric_type")
    if type(raw) is int and not -MAX_ABSOLUTE <= raw <= MAX_ABSOLUTE:
        raise NumericDomainError("numeric_magnitude")
    if type(raw) is Decimal:
        if not raw.is_finite() or raw.copy_abs() > MAX_ABSOLUTE:
            raise NumericDomainError("numeric_magnitude")
        parts = raw.as_tuple()
        if len(parts.digits) > MAX_NUMERIC_TEXT or abs(parts.exponent) > 999:
            raise NumericDomainError("numeric_size")
    text = str(raw)  # Decimal(str(float)), never Decimal(float).
    if len(text) > MAX_NUMERIC_TEXT or _NUMBER.fullmatch(text) is None:
        raise NumericDomainError("numeric_text")
    value = Decimal(text)
    if not value.is_finite() or value.copy_abs() > MAX_ABSOLUTE:
        raise NumericDomainError("numeric_magnitude")
    sign, digits, exponent = value.as_tuple()
    if not any(digits):
        return 0  # Canonical zero, including -0 and exponent/trailing-zero forms.
    digits = list(digits)
    while digits[-1] == 0:
        digits.pop()
        exponent += 1
    if exponent < -MAX_PLACES:
        raise NumericDomainError("numeric_precision")
    coefficient = 0
    for digit in digits:
        coefficient = coefficient * 10 + digit
    result = coefficient * 10 ** (exponent + MAX_PLACES)
    return -result if sign else result


def _text(micro: int) -> str:
    whole, fraction = divmod(abs(micro), SCALE)
    result = str(whole)
    if fraction:
        result += "." + str(fraction).zfill(MAX_PLACES).rstrip("0")
    return "-" + result if micro < 0 else result


def _unit(value: Any) -> str:
    if type(value) is not str:
        raise NumericDomainError("unit_type")
    try:
        size = len(value.encode("utf-8"))
    except UnicodeError as error:
        raise NumericDomainError("unit_text") from error
    if size > MAX_UNIT_BYTES or (value and not value.isprintable()):
        raise NumericDomainError("unit_text")
    return value


@dataclass(frozen=True, slots=True)
class NumericDomain:
    """Immutable min-anchored lattice; integer fields are millionths of a unit."""

    minimum_micro: int
    maximum_micro: int
    step_micro: int
    unit: str = ""

    def __post_init__(self) -> None:
        if any(type(value) is not int for value in (self.minimum_micro, self.maximum_micro, self.step_micro)):
            raise NumericDomainError("domain_integer_type")
        if (not -MAX_MICRO <= self.minimum_micro <= self.maximum_micro <= MAX_MICRO
                or not 0 < self.step_micro <= MAX_MICRO):
            raise NumericDomainError("domain_bounds")
        if self.max_index > MAX_STEPS:
            raise NumericDomainError("domain_step_limit")
        _unit(self.unit)

    @classmethod
    def from_ha(cls, attributes: Mapping[str, Any]) -> NumericDomain:
        """Require actual min/max/step; do not invent missing provider metadata."""
        if not isinstance(attributes, Mapping) or not {"min", "max", "step"} <= attributes.keys():
            raise NumericDomainError("domain_attributes")
        return cls(_micro(attributes["min"]), _micro(attributes["max"]),
                   _micro(attributes["step"]), _unit(attributes.get("unit_of_measurement", "")))

    @property
    def max_index(self) -> int:
        """Number of complete intervals; a fractional max tail is not a new step."""
        return (self.maximum_micro - self.minimum_micro) // self.step_micro

    def descriptor(self) -> dict[str, Any]:
        """Proposed canonical wire domain; never native float/percent brightness."""
        return {"schema": SCHEMA, "min": _text(self.minimum_micro),
                "max": _text(self.maximum_micro), "step": _text(self.step_micro),
                "unit": self.unit, "max_index": self.max_index}

    @classmethod
    def from_descriptor(cls, value: Any) -> NumericDomain:
        """Reject extra fields, bool indices and noncanonical numeric wire text."""
        if type(value) is not dict or set(value) != _FIELDS or value["schema"] != SCHEMA:
            raise NumericDomainError("descriptor_fields")
        if any(type(value[key]) is not str for key in ("min", "max", "step")):
            raise NumericDomainError("descriptor_numeric_text")
        domain = cls.from_ha({"min": value["min"], "max": value["max"], "step": value["step"],
                              "unit_of_measurement": value["unit"]})
        if type(value["max_index"]) is not int or value != domain.descriptor():
            raise NumericDomainError("descriptor_noncanonical")
        return domain

    def value_at(self, index: Any) -> Decimal:
        """Resolve one strict step index. Index0 means minimum; value0 is numeric."""
        if type(index) is not int or not 0 <= index <= self.max_index:
            raise NumericDomainError("index")
        return Decimal(_text(self.minimum_micro + index * self.step_micro))

    def exact_index(self, value: Any) -> int:
        """Authoritative values stay exact; an off-grid state is not fabricated."""
        micro = _micro(value)
        if not self.minimum_micro <= micro <= self.maximum_micro:
            raise NumericDomainError("value_range")
        index, remainder = divmod(micro - self.minimum_micro, self.step_micro)
        if remainder:
            raise NumericDomainError("value_off_grid")
        return index

    def observed_index(self, value: Any) -> int | None:
        """Unknown/unavailable/invalid/off-grid remain null, including float noise."""
        try:
            return self.exact_index(value)
        except NumericDomainError:
            return None

    def nearest_index(self, value: Any) -> int:
        """Explicit quantization only: midpoint chooses the greater numeric value."""
        micro = _micro(value)
        if not self.minimum_micro <= micro <= self.maximum_micro:
            raise NumericDomainError("value_range")
        index, remainder = divmod(micro - self.minimum_micro, self.step_micro)
        return min(self.max_index, index + int(remainder * 2 >= self.step_micro))

    def adjacent_index(self, index: Any, direction: Any) -> int:
        """One stepper intent; endpoint no-op. Unknown has no invented start."""
        self.value_at(index)
        if type(direction) is not int or direction not in (-1, 1):
            raise NumericDomainError("direction")
        return max(0, min(self.max_index, index + direction))

    def command_value(self, index: Any, *, current: NumericDomain) -> Decimal:
        """Revalidate live domain before conversion; session/auth are caller-owned."""
        if type(current) is not NumericDomain or current != self:
            raise NumericDomainError("domain_changed")
        return self.value_at(index)


    def service_value(self, index: Any, *, current: NumericDomain) -> int | float:
        """Pure HA numeric boundary: refuse decimal intent lost by float conversion."""
        value = self.command_value(index, current=current)
        micro = self.minimum_micro + index * self.step_micro
        if micro % SCALE == 0:
            return micro // SCALE
        result = float(value)
        try:
            recovered = _micro(result)
        except NumericDomainError as error:
            raise NumericDomainError("service_precision") from error
        if recovered != micro:
            raise NumericDomainError("service_precision")
        return result
