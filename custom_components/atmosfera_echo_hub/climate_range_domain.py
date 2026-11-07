"""One exact Climate range on the existing Detail owner; no service I/O."""

from dataclasses import dataclass
import math

from homeassistant.components.climate import DATA_COMPONENT

from .choice_domain import HVAC_MODES
from .number_domain import THERMOSTAT_ACTIVITIES
from .numeric_domain import NumericDomain, NumericDomainError, SCALE, _micro, _text

RANGE_BIT = 128
REASONS = frozenset(("none", "inactive_mode", "invalid_range", "source_unavailable"))


class RangeDomainError(ValueError):
    """Missing or incompatible provider metadata must never invent a range."""


def raw_attribute(attrs, key):
    """Immutable source signature, preserving missing/null and invalid changes."""
    if key not in attrs:
        return (False,)
    value = attrs[key]
    return (True, type(value).__name__, repr(value))


def measured_text(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        return ""
    try:
        micro = _micro(value)
    except NumericDomainError:
        return ""
    text = _text(micro)
    return text if -100 * SCALE <= micro <= 300 * SCALE and len(text) <= 12 else ""


@dataclass(frozen=True)
class RangeDomain:
    domain: NumericDomain

    @classmethod
    def from_ha(cls, hass, state):
        attrs = state.attributes
        features = attrs.get("supported_features")
        if (not state.entity_id.startswith("climate.") or not isinstance(features, int)
                or isinstance(features, bool) or features < 0 or not features & 2
                or not hass.services.has_service("climate", "set_temperature")):
            raise RangeDomainError("unsupported")
        unit = getattr(getattr(hass.config, "units", None), "temperature_unit", None)
        component = getattr(hass, "data", {}).get(DATA_COMPONENT)
        lookup = getattr(component, "get_entity", None)
        entity = lookup(state.entity_id) if callable(lookup) else None
        # Core11 converts the published bounds/targets, but leaves the step raw.
        if (unit not in {"°C", "°F"} or getattr(entity, "native_temperature_unit", None) != unit
                or attrs.get("temperature_unit") != unit):
            raise RangeDomainError("unit_unknown_or_mismatch")
        try:
            domain = NumericDomain.from_ha({"min": attrs["min_temp"], "max": attrs["max_temp"],
                "step": attrs["target_temp_step"], "unit_of_measurement": str(unit)})
        except (KeyError, NumericDomainError):
            raise RangeDomainError("invalid_domain") from None
        if not -100 * SCALE <= domain.minimum_micro < domain.maximum_micro <= 300 * SCALE:
            raise RangeDomainError("invalid_domain")
        return cls(domain)

    def indices(self, state):
        values = (state.attributes.get("target_temp_low"), state.attributes.get("target_temp_high"))
        if any(type(value) not in (int, float) for value in values):
            return None
        low, high = (self.domain.observed_index(value) for value in values)
        return (low, high) if low is not None and high is not None and low <= high else None

    def source(self, state):
        known = state.state in HVAC_MODES
        mode = state.state if known else "unknown"
        pair = self.indices(state) if known else None
        reason = ("source_unavailable" if not known else "inactive_mode" if mode != "heat_cool"
                  else "invalid_range" if pair is None else "none")
        activity = state.attributes.get("hvac_action") if known else None
        if activity not in THERMOSTAT_ACTIVITIES:
            activity = "off" if mode == "off" else "unknown"
        return {"domain": self.domain.descriptor(), "low_index": pair[0] if pair is not None else None,
                "high_index": pair[1] if pair is not None else None, "mode": mode, "activity": activity,
                "current_text": measured_text(state.attributes.get("current_temperature")) if known else "",
                "editable": reason == "none", "reason": reason}

    @staticmethod
    def context(state):
        return state.state, raw_attribute(state.attributes, "preset_mode")

    def observation(self, state):
        return self.context(state) + tuple(raw_attribute(state.attributes, key)
                                          for key in ("target_temp_low", "target_temp_high"))

    def target(self, low, high):
        try:
            self.domain.value_at(low)
            self.domain.value_at(high)
        except NumericDomainError:
            raise RangeDomainError("invalid_target") from None
        if low > high:
            raise RangeDomainError("invalid_target")
        return low, high

    def service(self, state, low, high):
        self.target(low, high)
        if not self.source(state)["editable"]:
            raise RangeDomainError("unavailable")
        return {"target_temp_low": self.domain.service_value(low, current=self.domain),
                "target_temp_high": self.domain.service_value(high, current=self.domain)}

    def matches(self, state, low, high, context):
        return (self.context(state) == context and self.source(state)["editable"]
                and self.indices(state) == self.target(low, high))

