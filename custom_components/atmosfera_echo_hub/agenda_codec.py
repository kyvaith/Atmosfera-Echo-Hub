"""Agenda1 fields, reduced to the existing strict identity boundary."""

from .agenda_domain import CAPS, AgendaError, integer, validate_fields
from .control_session import MAX_SEQUENCE, ProtocolError

PANEL = {"panel_type", "panel_caps", "panel_state", "available", "eligible_actions", "state_generation"}
REASONS = {"unsupported", "busy", "unauthorized", "stale_state", "stale_sequence", "sequence_conflict",
           "selection_changed", "connection_lost", "entity_unavailable", "expired"}


def translate(value, *, enabled=False):
    kind = value.get("kind")
    snapshot = kind in ("grant", "state") and isinstance(value.get("panel_caps"), dict) and value["panel_caps"].get("info_type") == "agenda"
    if not snapshot and kind not in ("page", "page_result"):
        return None
    if not enabled or value.get("control_kind") != "panel":
        raise ProtocolError("agenda_fields")
    result = dict(value)
    if snapshot:
        if (not PANEL <= value.keys() or value["panel_type"] != "info" or value["panel_caps"] != CAPS
                or type(value["panel_caps"].get("agenda_version")) is not int
                or not integer(value["state_generation"], 1, MAX_SEQUENCE)):
            raise ProtocolError("agenda_fields")
        try:
            validate_fields(value["panel_state"])
        except AgendaError:
            raise ProtocolError("agenda_fields") from None
        if (type(value["available"]) is not bool or value["available"] != (value["panel_state"]["source"] == "known")
                or type(value["eligible_actions"]) is not int or value["eligible_actions"] != 0):
            raise ProtocolError("agenda_fields")
        for key in PANEL:
            result.pop(key)
        result.update(control_kind="light", on=False, brightness_pct=None,
                      caps={"brightness": False, "turn_on": False, "turn_off": False})
    else:
        if not integer(value.get("request_seq"), 1, MAX_SEQUENCE) or not integer(value.get("target_index"), 0, 15):
            raise ProtocolError("agenda_fields")
        if any(key in value for key in ("command_seq", "op")):
            raise ProtocolError("agenda_fields")
        result.update(control_kind="light", command_seq=result.pop("request_seq"))
        result.pop("target_index")
        if kind == "page":
            if not integer(value.get("expected_state_generation"), 1, MAX_SEQUENCE):
                raise ProtocolError("agenda_fields")
            result.pop("expected_state_generation")
            result.update(kind="command", op="turn_on")
        else:
            if (value.get("status") not in {"ready", "rejected"}
                    or value.get("reason") not in ({"none"} if value.get("status") == "ready" else REASONS)):
                raise ProtocolError("agenda_fields")
            result.update(kind="result", status="state_matches" if value["status"] == "ready" else "rejected")
    return result
