"""HA-owned numeric facets; no transport, timers or guessed target values."""

import math
from collections.abc import Mapping

from homeassistant.components.climate import DATA_COMPONENT

from .choice_domain import HVAC_MODES
from .numeric_domain import NumericDomain, NumericDomainError

TEMPERATURE_ACTION = {"kind": "control", "control": "number", "property": "temperature"}
HUMIDITY_ACTION = {"kind": "control", "control": "number", "property": "humidity"}
COLOR_TEMPERATURE_ACTION = {"kind": "control", "control": "number", "property": "color_temp_kelvin"}
COVER_POSITION_ACTION = {"kind": "control", "control": "number", "property": "position"}
COVER_TILT_ACTION = {"kind": "control", "control": "number", "property": "tilt_position"}
SINGLE_TARGET_MODES = frozenset(("off", "heat", "cool", "dry", "fan_only"))
THERMOSTAT_ACTIVITIES = ("unknown", "off", "idle", "heating", "cooling", "drying", "fan", "preheating", "defrosting")


def thermostat_snapshot(hass, state):
    """Read the HA display state independently of the writable numeric domain."""
    unit = getattr(getattr(hass.config, "units", None), "temperature_unit", None)
    if unit not in {"°C", "°F"} or not state.entity_id.startswith("climate."):
        return None
    attrs = state.attributes
    features = attrs.get("supported_features")
    if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & 1 or features & 2:
        return None

    def temperature(key):
        value = attrs.get(key) if state.state not in {"unknown", "unavailable"} else None
        return float(value) if type(value) in (int, float) and -100 <= value <= 300 else None

    def text(value):
        return format(round(value, 6) or 0, ".6f").rstrip("0").rstrip(".") if value is not None else ""

    target, current = temperature("temperature"), temperature("current_temperature")
    minimum, maximum = temperature("min_temp"), temperature("max_temp")
    level = None
    if minimum is not None and maximum is not None and minimum < maximum:
        if target is not None and minimum <= target <= maximum:
            level = round(100 * (target - minimum) / (maximum - minimum))
    else:
        minimum = maximum = None
    activity = attrs.get("hvac_action") if state.state not in {"unknown", "unavailable"} else None
    if activity not in THERMOSTAT_ACTIVITIES:
        activity = "off" if state.state == "off" else "unknown"
    return {"unit": str(unit), "target": text(target), "current": text(current),
            "min": text(minimum), "max": text(maximum), "level": level, "activity": activity}


def number_service(entity_id, property=None):
    domain = entity_id.partition(".")[0]
    if property == "position" and domain == "cover":
        return domain, "set_cover_position", "position"
    if property == "tilt_position" and domain == "cover":
        return domain, "set_cover_tilt_position", "tilt_position"
    if property == "temperature" and domain == "climate":
        return domain, "set_temperature", "temperature"
    if property == "humidity" and domain in {"humidifier", "climate"}:
        return domain, "set_humidity", "humidity"
    if property == "color_temp_kelvin" and domain == "light":
        return domain, "turn_on", "color_temp_kelvin"
    if property is None and domain in {"number", "input_number"}:
        return domain, "set_value", "value"
    raise NumericDomainError("unsupported_numeric_property")


def temperature_unit(hass, entity_id):
    """Old Core's raw step is safe only when native and displayed units match."""
    unit = getattr(getattr(hass.config, "units", None), "temperature_unit", None)
    component = getattr(hass, "data", {}).get(DATA_COMPONENT)
    lookup = getattr(component, "get_entity", None)
    entity = lookup(entity_id) if callable(lookup) else None
    native_unit = getattr(entity, "temperature_unit", None)
    if unit not in {"°C", "°F"} or native_unit != unit:
        raise NumericDomainError("temperature_unit_unknown_or_mismatch")
    # Core uses UnitOfTemperature (StrEnum); the numeric wire domain deliberately
    # accepts canonical plain strings only. Normalize after exact unit checks.
    return str(unit)


def humidity_domain(attrs):
    """Use Core's integer service granularity when no device step is reported."""
    if not isinstance(attrs, Mapping) or not {"min_humidity", "max_humidity"} <= attrs.keys():
        raise NumericDomainError("humidity_domain_missing")
    values = (attrs["min_humidity"], attrs["max_humidity"], attrs.get("target_humidity_step", 1))
    try:
        valid = all(type(value) in (int, float) and math.isfinite(value) and int(value) == value for value in values)
    except (ValueError, OverflowError):
        valid = False
    if not valid or not 0 <= values[0] <= values[1] <= 100 or values[2] <= 0:
        raise NumericDomainError("humidity_domain_invalid")
    return NumericDomain.from_ha({"min": values[0], "max": values[1], "step": values[2],
                                  "unit_of_measurement": "%"})


def color_temperature_domain(attrs):
    """Fine adjustment uses Core's integer Kelvin service, never guessed bounds."""
    if not isinstance(attrs, Mapping):
        raise NumericDomainError("color_temperature_attributes")
    modes = attrs.get("supported_color_modes")
    if (not isinstance(modes, (list, tuple, set, frozenset)) or not modes
            or any(not isinstance(mode, str) for mode in modes) or "color_temp" not in modes):
        raise NumericDomainError("color_temperature_unsupported")
    values = (attrs.get("min_color_temp_kelvin"), attrs.get("max_color_temp_kelvin"))
    try:
        valid = all(type(value) in (int, float) and math.isfinite(value) and int(value) == value for value in values)
    except (ValueError, OverflowError):
        valid = False
    if not valid or not 1000 <= values[0] <= values[1] <= 20000:
        raise NumericDomainError("color_temperature_bounds")
    return NumericDomain.from_ha({"min": values[0], "max": values[1], "step": 1,
                                  "unit_of_measurement": "K"})


def number_domain(hass, state, property=None):
    number_service(state.entity_id, property)
    attrs = state.attributes
    if property is None:
        return NumericDomain.from_ha(attrs)
    if property in {"position", "tilt_position"}:
        features = attrs.get("supported_features") if isinstance(attrs, Mapping) else None
        feature = 4 if property == "position" else 128
        if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & feature:
            raise NumericDomainError("cover_position_unsupported")
        return NumericDomain.from_ha({"min": 0, "max": 100, "step": 1, "unit_of_measurement": "%"})
    if property == "humidity":
        if state.entity_id.startswith("climate."):
            features = attrs.get("supported_features") if isinstance(attrs, Mapping) else None
            if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & 4:
                raise NumericDomainError("climate_humidity_unsupported")
        return humidity_domain(attrs)
    if property == "color_temp_kelvin":
        return color_temperature_domain(attrs)
    if not isinstance(attrs, Mapping):
        raise NumericDomainError("domain_attributes")
    features = attrs.get("supported_features")
    if (not isinstance(features, int) or isinstance(features, bool) or features < 0
            or not features & 1 or features & 2):
        raise NumericDomainError("single_target_unsupported")
    if not {"min_temp", "max_temp", "target_temp_step"} <= attrs.keys():
        raise NumericDomainError("temperature_domain_missing")
    return NumericDomain.from_ha({"min": attrs["min_temp"], "max": attrs["max_temp"],
                                  "step": attrs["target_temp_step"],
                                  "unit_of_measurement": temperature_unit(hass, state.entity_id)})


def number_state(state, property=None):
    if property in {"position", "tilt_position"}:
        field = "current_position" if property == "position" else "current_tilt_position"
        value = state.attributes.get(field) if state.state in {"open", "closed", "opening", "closing"} else None
        return value if type(value) in (int, float) else None
    if property == "color_temp_kelvin":
        value = state.attributes.get("color_temp_kelvin") if state.state == "on" and state.attributes.get("color_mode") == "color_temp" else None
        return value if type(value) in (int, float) else None
    if property == "humidity":
        modes = HVAC_MODES if state.entity_id.startswith("climate.") else {"on", "off"}
        value = state.attributes.get("humidity") if state.state in modes else None
        return value if type(value) in (int, float) else None
    if property == "temperature":
        return state.attributes.get("temperature") if state.state in SINGLE_TARGET_MODES else None
    return state.state
