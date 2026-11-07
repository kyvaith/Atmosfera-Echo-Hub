"""Optional text:1 envelopes sharing the strict selection identity codec."""

from .control_session import MAX_SEQUENCE, ProtocolError
from .text_panel_domain import TextDomain, TextObservation, TextPanelError, valid_target
from .light_control import _integer

PANEL = {"panel_type", "panel_caps", "panel_state", "available", "eligible_actions", "state_generation"}


def translate(value, *, enabled=False):
    snapshot = value.get("kind") in ("grant", "state") and value.get("panel_type") == "text"
    marked = "text_version" in value
    if not snapshot and not marked:
        return None
    if not enabled or value.get("control_kind") != "panel":
        raise ProtocolError("text_fields")
    result = dict(value)
    if snapshot:
        if marked or not PANEL <= value.keys() or not _integer(value["state_generation"], 1, MAX_SEQUENCE):
            raise ProtocolError("text_fields")
        try:
            domain = TextDomain.from_descriptor(value["panel_caps"])
            observed = TextObservation.from_descriptor(domain, value["panel_state"])
        except TextPanelError:
            raise ProtocolError("text_fields") from None
        if (type(value["available"]) is not bool or value["available"] != observed.available
                or not _integer(value["eligible_actions"], 0, 1) or value["eligible_actions"] != observed.eligible(domain)):
            raise ProtocolError("text_fields")
        for key in PANEL:
            result.pop(key)
        result.update(control_kind="light", on=False, brightness_pct=None,
                      caps={"brightness": False, "turn_on": False, "turn_off": False})
    else:
        if (value.get("kind") != "command" or type(value["text_version"]) is not int or value["text_version"] != 1
                or value.get("op") != "set_value" or not valid_target(value.get("value"))
                or not _integer(value.get("expected_state_generation"), 1, MAX_SEQUENCE)):
            raise ProtocolError("text_fields")
        for key in ("text_version", "value", "expected_state_generation"):
            result.pop(key)
        result.update(control_kind="light", op="turn_on")
    return result
