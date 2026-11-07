"""Closed optional external-media bodies over unchanged session identity."""

from types import SimpleNamespace

from .choice_domain import ChoiceDomain
from .control_session import MAX_SEQUENCE, RESULT_REASONS, CLOSE_REASONS, ProtocolError
from .light_control import _integer
from .media_panel_domain import FACET_BITS, KNOWN_PHASES, MEDIA_ACTIVE_STATES, OP_BITS, MediaDomain, volume_observation

FACETS = {"main", *FACET_BITS}
CAPS = {"device_type", "operations", "facets"}
MAIN = {"source", "phase", "eligible", "volume_raw", "volume_percent", "volume_rail", "muted", "shuffle",
        "title_status", "media_title", "artist_status", "media_artist"}
PANEL = {"panel_type", "panel_caps", "panel_state", "available", "eligible_actions", "state_generation"}


def fail():
    raise ProtocolError("media_fields")


def description(status, value, maximum):
    if (type(status) is not str or status not in {"value", "empty", "invalid", "excerpt"}
            or type(value) is not str or len(value.encode("utf8")) > maximum
            or value and not value.isprintable()
            or (status in {"empty", "invalid"}) != (value == "")
            or status == "excerpt" and not value.endswith("…")):
        fail()


def volume(raw, percent, rail):
    if raw is None:
        if percent != "" or rail is not None:
            fail()
        return None
    if type(raw) is not str or not 1 <= len(raw) <= 24:
        fail()
    observed = volume_observation(float(raw))
    if (observed is None or observed.raw != raw or observed.percent != percent
            or not _integer(rail, 0, 10000) or observed.rail != rail):
        fail()
    return observed


def view(body, caps, available):
    if (type(body) is not dict or type(caps) is not dict or set(caps) != CAPS
            or caps["device_type"] not in {"generic", "speaker", "tv", "receiver"}
            or not _integer(caps["operations"], 0, sum(OP_BITS.values()))
            or not _integer(caps["facets"], 0, sum(FACET_BITS.values()))
            or bool(caps["facets"] & FACET_BITS["volume"]) != bool(caps["operations"] & OP_BITS["volume"])):
        fail()
    facet, sequence, source = body.get("facet"), body.get("view_seq"), body.get("source")
    if (facet not in FACETS or not _integer(sequence, 0, MAX_SEQUENCE)
            or facet != "main" and (not sequence or not caps["facets"] & FACET_BITS[facet])
            or source not in {"known", "unknown", "unavailable"} or type(available) is not bool
            or available != (source == "known")):
        fail()
    common = {"facet", "view_seq"}
    if facet == "main":
        if set(body) != common | MAIN or body["phase"] not in KNOWN_PHASES | {"unknown"}:
            fail()
        if available != (body["phase"] != "unknown"):
            fail()
        observation = volume(body["volume_raw"], body["volume_percent"], body["volume_rail"])
        operations = tuple(name for name, bit in OP_BITS.items() if caps["operations"] & bit)
        domain = MediaDomain(caps["device_type"], operations, (), ())
        state = SimpleNamespace(state=body["phase"], attributes={
            "volume_level": float(observation.raw) if observation else None,
            "is_volume_muted": body["muted"], "shuffle": body["shuffle"]})
        for key, operation in (("muted", "mute"), ("shuffle", "shuffle")):
            if body[key] is not None and (type(body[key]) is not bool or domain.boolean(state, operation) is None):
                fail()
        if observation is not None and domain.volume(state) is None:
            fail()
        eligible = sum(OP_BITS[name] for name in operations if domain.eligible(state, name))
        if type(body["eligible"]) is not int or body["eligible"] != eligible:
            fail()
        description(body["title_status"], body["media_title"], 128)
        description(body["artist_status"], body["media_artist"], 96)
        if body["phase"] not in MEDIA_ACTIVE_STATES and (body["media_title"] or body["media_artist"]):
            fail()
        return eligible
    if facet == "volume":
        if (set(body) != common | {"source", "editable", "ui_step_percent", "observed_raw", "percent_text", "rail"}
                or type(body["ui_step_percent"]) is not int or body["ui_step_percent"] != 1):
            fail()
        observation = volume(body["observed_raw"], body["percent_text"], body["rail"])
        if (type(body["editable"]) is not bool or body["editable"] != (observation is not None)
                or not available and observation is not None):
            fail()
        return int(body["editable"])
    if set(body) != common | {"source", "options", "index", "editable"}:
        fail()
    domain = ChoiceDomain.from_options(body["options"])
    index = body["index"]
    if (index is not None and not _integer(index, 0, len(domain.options) - 1)
            or type(body["editable"]) is not bool or body["editable"] != (index is not None)
            or not available and index is not None):
        fail()
    return 2 if body["editable"] else 0


def translate(value, *, enabled=False):
    """Media discriminator is consumed before the Light/Climate facet parser."""
    kind = value.get("kind")
    snapshot = kind in {"grant", "state"} and value.get("panel_type") == "media"
    marked = "media_version" in value
    if not snapshot and not marked:
        return None
    if not enabled or value.get("control_kind") != "panel":
        fail()
    result = dict(value)
    if snapshot:
        if marked or not PANEL <= value.keys() or not _integer(value["state_generation"], 1, MAX_SEQUENCE):
            fail()
        eligible = view(value["panel_state"], value["panel_caps"], value["available"])
        if (type(value["eligible_actions"]) is not int or value["eligible_actions"] != eligible
                or kind == "grant" and (value["panel_state"]["facet"] != "main" or value["panel_state"]["view_seq"] != 0)):
            fail()
        for key in PANEL:
            result.pop(key)
        result.update(control_kind="light", on=False, brightness_pct=None,
                      caps={"brightness": False, "turn_on": False, "turn_off": False})
        return result
    if type(value["media_version"]) is not int or value["media_version"] != 1 or kind not in {"command", "facet", "facet_result"}:
        fail()
    result.pop("media_version")
    facet = value.get("facet")
    if facet not in FACETS or not _integer(value.get("view_seq"), 0 if kind == "command" else 1, MAX_SEQUENCE):
        fail()
    result.pop("facet")
    if kind in {"facet", "facet_result"}:
        result["command_seq"] = result.pop("view_seq")
        if kind == "facet":
            result.update(kind="command", op="turn_on", control_kind="light")
        else:
            if (value.get("status") not in {"ready", "rejected"} or value.get("reason") not in RESULT_REASONS | CLOSE_REASONS
                    or value["status"] == "ready" and value["reason"] != "none"
                    or value["status"] == "rejected" and value["reason"] in {"none", "service_timeout", "state_timeout"}):
                fail()
            result.update(kind="result", control_kind="light", status="ha_accepted" if value["status"] == "ready" else "rejected")
            if value["reason"] in CLOSE_REASONS:
                result["reason"] = "selection_changed"
        return result
    if not _integer(value.get("expected_state_generation"), 1, MAX_SEQUENCE):
        fail()
    result.pop("expected_state_generation")
    result.pop("view_seq")
    operation = value.get("op")
    if operation == "volume":
        if (facet != "volume" or not _integer(value.get("target_percent"), 0, 100)
                or type(value.get("expected_raw")) is not str):
            fail()
        raw = value["expected_raw"]
        observed = volume_observation(float(raw)) if len(raw) <= 24 else None
        if observed is None or raw != observed.raw:
            fail()
        result.pop("target_percent")
        result.pop("expected_raw")
    elif operation == "choice":
        if (facet not in {"source", "sound_mode", "repeat"}
                or not _integer(value.get("expected_index"), 0, 7) or not _integer(value.get("target_index"), 0, 7)):
            fail()
        result.pop("target_index")
        result.pop("expected_index")
    elif operation in {"mute", "shuffle"}:
        if facet != "main" or type(value.get("target")) is not bool:
            fail()
        result.pop("target")
    elif facet != "main" or operation not in OP_BITS:
        fail()
    result.update(control_kind="light", op="turn_on")
    return result
