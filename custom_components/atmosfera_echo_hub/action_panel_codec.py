"""Closed Action:1 extension; common identity stays in the existing codec."""

from .action_panel_domain import ActionDomain, ActionObservation, ActionPanelError, BITS
from .action_parameters_domain import PARAM_KEYS, ActionParametersDomain, ActionParametersObservation
from .control_session import MAX_SEQUENCE, ProtocolError
from .light_control import _integer

PANEL = {"panel_type", "panel_caps", "panel_state", "available", "eligible_actions", "state_generation"}


def translate(value, *, enabled=False, tile_event=False, parameters=False):
    kind = value.get("kind")
    snapshot = kind in {"grant", "state"} and value.get("panel_type") == "action"
    marked = "action_version" in value
    params_command = "action_parameters_version" in value or "parameter_value" in value
    if params_command and (not parameters or not marked or value.get("op") != "run"
            or type(value.get("action_parameters_version")) is not int or value["action_parameters_version"] != 1
            or type(value.get("parameter_value")) is not bool):
        raise ProtocolError("action_fields")
    if not snapshot and not marked:
        return None
    if not enabled or value.get("control_kind") != "panel":
        raise ProtocolError("action_fields")
    result = dict(value)
    if snapshot:
        if marked or not PANEL <= value.keys() or not _integer(value["state_generation"], 1, MAX_SEQUENCE):
            raise ProtocolError("action_fields")
        try:
            params = type(value["panel_caps"]) is dict and bool(PARAM_KEYS & value["panel_caps"].keys())
            if params and not parameters:
                raise ActionPanelError("parameters_profile")
            domain = (ActionParametersDomain if params else ActionDomain).from_descriptor(value["panel_caps"])
            if domain.action_type == "tile_event" and not tile_event:
                raise ActionPanelError("tile_event_profile")
            observed = (ActionParametersObservation if params else ActionObservation).from_descriptor(domain, value["panel_state"])
        except ActionPanelError:
            raise ProtocolError("action_fields") from None
        if (type(value["available"]) is not bool or value["available"] != observed.available
                or not _integer(value["eligible_actions"], 0, 127) or value["eligible_actions"] != observed.eligible(domain)):
            raise ProtocolError("action_fields")
        for key in PANEL:
            result.pop(key)
        result.update(control_kind="light", on=False, brightness_pct=None,
                      caps={"brightness": False, "turn_on": False, "turn_off": False})
    else:
        if (kind != "command" or type(value["action_version"]) is not int or value["action_version"] != 1
                or value.get("op") not in BITS or not _integer(value.get("expected_state_generation"), 1, MAX_SEQUENCE)):
            raise ProtocolError("action_fields")
        if params_command:
            result.pop("action_parameters_version")
            result.pop("parameter_value")
        result.pop("action_version")
        result.pop("expected_state_generation")
        result.update(control_kind="light", op="turn_on")
    return result
