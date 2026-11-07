"""Optional datetime:1 envelopes over the existing identity codec."""

from .control_session import MAX_SEQUENCE, ProtocolError
from .datetime_panel_domain import DatetimeDomain, DatetimeObservation, DatetimePanelError, valid_tuple
from .light_control import _integer

PANEL = {"panel_type", "panel_caps", "panel_state", "available", "eligible_actions", "state_generation"}


def translate(value, *, enabled=False):
    snapshot = value.get("kind") in ("grant", "state") and value.get("panel_type") == "datetime"
    marked = "datetime_version" in value
    if not snapshot and not marked:
        return None
    if not enabled or value.get("control_kind") != "panel":
        raise ProtocolError("datetime_fields")
    result = dict(value)
    if snapshot:
        if marked or not PANEL <= value.keys() or not _integer(value["state_generation"], 1, MAX_SEQUENCE):
            raise ProtocolError("datetime_fields")
        try:
            domain = DatetimeDomain.from_descriptor(value["panel_caps"])
            observed = DatetimeObservation.from_descriptor(domain, value["panel_state"])
        except DatetimePanelError:
            raise ProtocolError("datetime_fields") from None
        if (type(value["available"]) is not bool or value["available"] != observed.available
                or not _integer(value["eligible_actions"], 0, 1) or value["eligible_actions"] != observed.eligible(domain)):
            raise ProtocolError("datetime_fields")
        for key in PANEL:
            result.pop(key)
        result.update(control_kind="light", on=False, brightness_pct=None,
                      caps={"brightness": False, "turn_on": False, "turn_off": False})
    else:
        if (value.get("kind") != "command" or type(value["datetime_version"]) is not int or value["datetime_version"] != 1
                or value.get("op") != "set_datetime" or not valid_tuple(value.get("target"))
                or not _integer(value.get("expected_state_generation"), 1, MAX_SEQUENCE)):
            raise ProtocolError("datetime_fields")
        for key in ("datetime_version", "target", "expected_state_generation"):
            result.pop(key)
        result.update(control_kind="light", op="turn_on")
    return result
