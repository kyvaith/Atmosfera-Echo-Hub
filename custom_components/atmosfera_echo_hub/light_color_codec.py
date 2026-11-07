"""Exact Color1 state grammar; only the active Color facet carries values."""

from .control_session import ProtocolError
from .light_color_domain import MODES, REASONS, triple, target, ColorDomainError

FIELDS = {"version", "write_mode", "source_mode", "rgb", "hue_milli", "saturation_milli", "editable", "reason"}


def validate_state(value):
    if (type(value) is not dict or set(value) != FIELDS or type(value["version"]) is not int or value["version"] != 1
            or type(value["write_mode"]) is not str or value["write_mode"] not in {"rgb", "hs", "xy"}
            or type(value["source_mode"]) is not str or value["source_mode"] not in MODES | {"other", "unknown"}
            or type(value["reason"]) is not str or value["reason"] not in REASONS
            or type(value["editable"]) is not bool or value["editable"] != (value["reason"] == "none")):
        raise ProtocolError("color_fields")
    reason, mode = value["reason"], value["source_mode"]
    known = reason in {"none", "invalid_brightness"}
    if known:
        if mode not in MODES or type(value["rgb"]) is not list or triple(value["rgb"]) is None:
            raise ProtocolError("color_fields")
        try:
            target(value["hue_milli"], value["saturation_milli"])
        except ColorDomainError:
            raise ProtocolError("color_fields") from None
    elif any(value[key] is not None for key in ("rgb", "hue_milli", "saturation_milli")):
        raise ProtocolError("color_fields")
    if (reason in {"off", "source_unavailable"} and mode != "unknown"
            or reason == "unsupported_mode" and mode not in {"other", "unknown"}
            or reason == "invalid_color" and mode not in MODES):
        raise ProtocolError("color_fields")
