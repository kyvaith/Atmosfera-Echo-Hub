"""Closed Range1 active-facet grammar, using the shared numeric lattice."""

from .control_session import MAX_SEQUENCE, ProtocolError
from .choice_domain import HVAC_MODES
from .number_domain import THERMOSTAT_ACTIVITIES
from .numeric_domain import NumericDomain, NumericDomainError, SCALE, _micro, _text
from .climate_range_domain import REASONS

FIELDS = {"facet", "view_seq", "domain", "low_index", "high_index", "mode", "activity",
          "current_text", "editable", "reason"}


def validate_state(value, available):
    try:
        if (type(value) is not dict or set(value) != FIELDS or value["facet"] != "range"
                or type(value["view_seq"]) is not int or not 1 <= value["view_seq"] <= MAX_SEQUENCE
                or type(available) is not bool or type(value["mode"]) is not str
                or value["mode"] not in HVAC_MODES | {"unknown"}
                or available != (value["mode"] != "unknown")
                or type(value["activity"]) is not str or value["activity"] not in THERMOSTAT_ACTIVITIES
                or type(value["reason"]) is not str or value["reason"] not in REASONS
                or type(value["editable"]) is not bool or value["editable"] != (value["reason"] == "none")):
            raise ValueError
        domain = NumericDomain.from_descriptor(value["domain"])
        if domain.unit not in {"°C", "°F"} or not -100*SCALE <= domain.minimum_micro < domain.maximum_micro <= 300*SCALE:
            raise ValueError
        low, high = value["low_index"], value["high_index"]
        known = low is not None or high is not None
        if known:
            domain.value_at(low)
            domain.value_at(high)
            if low > high:
                raise ValueError
        text = value["current_text"]
        if type(text) is not str or len(text) > 12:
            raise ValueError
        if text:
            micro = _micro(text)
            if _text(micro) != text or not -100*SCALE <= micro <= 300*SCALE:
                raise ValueError
        reason, mode = value["reason"], value["mode"]
        if (reason == "none" and (mode != "heat_cool" or not known)
                or reason == "invalid_range" and (mode != "heat_cool" or known)
                or reason == "inactive_mode" and mode in {"heat_cool", "unknown"}
                or reason == "source_unavailable" and (mode != "unknown" or known or text or value["activity"] != "unknown")):
            raise ValueError
    except (ValueError, KeyError, TypeError, NumericDomainError):
        raise ProtocolError("range_fields") from None
