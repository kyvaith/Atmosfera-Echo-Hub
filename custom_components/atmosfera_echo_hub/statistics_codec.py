"""Statistics1 snapshots through the existing strict identity codec."""

from .control_session import MAX_SEQUENCE, ProtocolError
from .statistics_domain import CAPS, StatisticsError, integer, validate_fields

PANEL = {"panel_type", "panel_caps", "panel_state", "available", "eligible_actions", "state_generation"}


def translate(value, *, enabled=False):
    if (value.get("kind") not in ("grant", "state") or not isinstance(value.get("panel_caps"), dict)
            or value["panel_caps"].get("info_type") != "statistics"):
        return None
    if (not enabled or value.get("control_kind") != "panel" or not PANEL <= value.keys()
            or value["panel_type"] != "info" or value["panel_caps"] != CAPS
            or type(value["panel_caps"].get("statistics_version")) is not int
            or not integer(value["state_generation"], 1, MAX_SEQUENCE)):
        raise ProtocolError("statistics_fields")
    try:
        validate_fields(value["panel_state"])
    except StatisticsError:
        raise ProtocolError("statistics_fields") from None
    if (type(value["available"]) is not bool or value["available"] != (value["panel_state"]["source"] == "known")
            or type(value["eligible_actions"]) is not int or value["eligible_actions"] != 0):
        raise ProtocolError("statistics_fields")
    result = {key: item for key, item in value.items() if key not in PANEL}
    result.update(control_kind="light", on=False, brightness_pct=None,
                  caps={"brightness": False, "turn_on": False, "turn_off": False})
    return result
