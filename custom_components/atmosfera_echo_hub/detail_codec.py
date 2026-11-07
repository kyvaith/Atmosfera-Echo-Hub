"""Translate opt-in detail envelopes for unchanged shared identity validation."""

from .control_session import MAX_SEQUENCE, RESULT_REASONS, CLOSE_REASONS, SELECTION, ProtocolError
from .detail_domain import FACETS, LIGHT_BITS, CLIMATE_BITS
from .choice_domain import ChoiceDomain, HVAC_MODES
from .number_domain import THERMOSTAT_ACTIVITIES
from .numeric_domain import NumericDomain, MAX_STEPS, SCALE, _micro, _text
from .light_control import _integer
from .light_color_codec import validate_state as validate_color_state
from .climate_range_codec import validate_state as validate_range_state

DETAIL_FIELDS = {"version", "facets", "state_generation", "facet", "view_seq"}
MAIN_FIELDS = {"unit", "mode", "activity", "target", "current", "low", "high", "min", "max", "domain", "index", "editable"}
NUMERIC_FIELDS = {"domain", "index", "value_text", "current_text", "editable"}
CHOICE_FIELDS = {"options", "index", "choice_known", "editable"}


def fail():
    raise ProtocolError("detail_fields")


def text(value, minimum, maximum):
    if type(value) is not str or len(value) > 12:
        fail()
    if value:
        micro = _micro(value)
        if _text(micro) != value or not minimum * SCALE <= micro <= maximum * SCALE:
            fail()


def view(body, family, mask, available, *, color=False, range_enabled=False):
    facet = body.get("facet")
    if facet not in FACETS[family] or not _integer(body.get("view_seq"), 0, MAX_SEQUENCE):
        fail()
    if facet != "main" and body["view_seq"] == 0:
        fail()
    common = {"facet", "view_seq"}
    if facet == "range":
        if family != "climate" or not range_enabled or not mask & 128:
            fail()
        validate_range_state(body, available)
        return 1 if body["editable"] else 0
    if facet == "color":
        if family != "light" or not color or not mask & 4 or set(body) != common:
            fail()
        return 0
    if facet != "main" and not mask & (LIGHT_BITS if family == "light" else CLIMATE_BITS)[facet]:
        fail()
    if facet == "main" and family == "light":
        if set(body) != common:
            fail()
        return 0
    if facet == "main":
        if (set(body) != common | MAIN_FIELDS or body["unit"] not in (None, "°C", "°F")
                or body["mode"] not in HVAC_MODES | {"unknown"} or body["activity"] not in THERMOSTAT_ACTIVITIES
                or available != (body["mode"] != "unknown")):
            fail()
        for field in ("target", "current", "low", "high", "min", "max"):
            text(body[field], -100, 300)
        if not available and (any(body[field] for field in ("target", "current", "low", "high"))
                              or body["activity"] != "unknown"):
            fail()
        if body["unit"] is None and (body["domain"] is not None or any(body[field] for field in ("target", "current", "low", "high", "min", "max"))):
            fail()
        if bool(mask & 1) != (body["domain"] is not None):
            fail()
    elif facet in {"humidity", "color_temp_kelvin"}:
        if set(body) != common | NUMERIC_FIELDS:
            fail()
        text(body["current_text"], 0, 100)
        if facet == "color_temp_kelvin" and body["current_text"]:
            fail()
    else:
        if set(body) != common | CHOICE_FIELDS:
            fail()
        domain = ChoiceDomain.from_options(body["options"])
        index = body["index"]
        if (index is not None and not _integer(index, 0, len(domain.options)-1)
                or type(body["choice_known"]) is not bool or type(body["editable"]) is not bool
                or body["editable"] != body["choice_known"]
                or (index is not None and not body["choice_known"])
                or (body["choice_known"] and index is None and facet not in {"effect", "preset_mode"})
                or (not available and (index is not None or body["choice_known"]))):
            fail()
        return 2 if body["editable"] else 0
    domain = NumericDomain.from_descriptor(body["domain"]) if body["domain"] is not None else None
    unit = body["unit"] if facet == "main" else ("K" if facet == "color_temp_kelvin" else "%")
    index = body["index"]
    if (domain is not None and domain.unit != unit or facet != "main" and domain is None
            or index is not None and (domain is None or not _integer(index, 0, domain.max_index))
            or type(body["editable"]) is not bool or body["editable"] != (index is not None)
            or not available and index is not None):
        fail()
    if facet != "main" and body["value_text"] != (str(domain.value_at(index)) if index is not None else "--"):
        fail()
    return 1 if body["editable"] else 0


def translate(value, *, light=False, climate=False, color=False, range_enabled=False):
    """Return legacy-shaped equivalent only for new, negotiated envelopes."""
    control, kind = value.get("control_kind"), value.get("kind")
    result = dict(value)
    if kind in {"open", "cancel_open"} and "detail_version" in value:
        if control != "light" or not light or type(value["detail_version"]) is not int or value["detail_version"] != 1:
            fail()
        result.pop("detail_version")
        return result
    is_light = control == "light" and "light_detail" in value and kind in {"grant", "state"}
    is_climate = control == "panel" and value.get("panel_type") == "climate" and kind in {"grant", "state"}
    if is_light or is_climate:
        initial = value["light_detail"] if is_light else value.get("panel_state")
        if kind == "grant" and (type(initial) is not dict or initial.get("facet") != "main" or initial.get("view_seq") != 0):
            fail()
        if is_light:
            if not light or type(value["light_detail"]) is not dict:
                fail()
            detail = dict(value["light_detail"])
            if (not DETAIL_FIELDS <= detail.keys() or type(detail["version"]) is not int or detail.pop("version") != 1
                    or not _integer(detail["facets"], 0, 7 if color else 3) or not _integer(detail["state_generation"], 1, MAX_SEQUENCE)):
                fail()
            mask = detail.pop("facets")
            detail.pop("state_generation")
            view(detail, "light", mask, True, color=color)
            if detail["facet"] == "color":
                if kind != "state" or "light_color" not in value:
                    fail()
                validate_color_state(value["light_color"])
                expected_on = value["light_color"]["reason"] not in {"off", "source_unavailable"}
                if value.get("on") is not expected_on:
                    fail()
                result.pop("light_color")
            elif "light_color" in value:
                fail()
            result.pop("light_detail")
        else:
            if (not climate or type(value.get("panel_caps")) is not dict or set(value["panel_caps"]) != {"facets"}
                    or not _integer(value["panel_caps"]["facets"], 0, 255 if range_enabled else 127) or type(value.get("panel_state")) is not dict
                    or type(value.get("available")) is not bool or not _integer(value.get("state_generation"), 1, MAX_SEQUENCE)):
                fail()
            eligible = view(value["panel_state"], "climate", value["panel_caps"]["facets"], value["available"], range_enabled=range_enabled)
            if type(value.get("eligible_actions")) is not int or value["eligible_actions"] != eligible:
                fail()
            for key in ("panel_type", "panel_caps", "panel_state", "available", "eligible_actions", "state_generation"):
                result.pop(key)
            result.update(on=False, brightness_pct=None, caps={"turn_on":False,"turn_off":False,"brightness":False},control_kind="light")
        return result
    if kind in {"facet", "facet_result"}:
        expected = {"v", "type", "kind", "control_kind", "facet", "view_seq"} | SELECTION
        if kind == "facet_result":
            expected |= {"state_seq", "status", "reason"}
        if set(value) != expected:
            fail()
        if not ((control == "light" and light) or (control == "panel" and climate)):
            fail()
        family = "light" if control == "light" else "climate"
        if value.get("facet") == "color" and (not color or family != "light"):
            fail()
        if value.get("facet") == "range" and (not range_enabled or family != "climate"):
            fail()
        if value.get("facet") not in FACETS[family] or not _integer(value.get("view_seq"), 1, MAX_SEQUENCE):
            fail()
        result["control_kind"] = "light"
        result["command_seq"] = result.pop("view_seq")
        result.pop("facet")
        if kind == "facet":
            result.update(kind="command",op="turn_on")
        else:
            if (value.get("status") not in {"ready", "rejected"} or value.get("reason") not in RESULT_REASONS | CLOSE_REASONS
                    or value["status"] == "ready" and value["reason"] != "none"
                    or value["status"] == "rejected" and value["reason"] in {"none", "service_timeout", "state_timeout"}):
                fail()
            result.update(kind="result",status="ha_accepted" if value["status"] == "ready" else "rejected")
            if value["reason"] in CLOSE_REASONS:
                result["reason"] = "selection_changed"
        return result
    if kind == "command" and (value.get("op") in {"facet_number", "facet_choice", "facet_color", "facet_range"} or "view_seq" in value):
        if not ((control == "light" and light) or (control == "panel" and climate)):
            fail()
        if not _integer(value.get("view_seq"), 0, MAX_SEQUENCE) or not _integer(value.get("expected_state_generation"), 1, MAX_SEQUENCE):
            fail()
        for key in ("view_seq", "expected_state_generation"):
            result.pop(key)
        if value["op"] == "facet_range":
            if (not range_enabled or control != "panel" or value.get("facet") != "range" or value["view_seq"] == 0
                    or not _integer(value.get("target_low_index"), 0, MAX_STEPS)
                    or not _integer(value.get("target_high_index"), 0, MAX_STEPS)
                    or value["target_low_index"] > value["target_high_index"]):
                fail()
            for key in ("facet", "target_low_index", "target_high_index"):
                result.pop(key)
            result.update(op="turn_on", control_kind="light")
        elif value["op"] == "facet_color":
            if (not color or control != "light" or value.get("facet") != "color" or value["view_seq"] == 0
                    or not _integer(value.get("target_hue_milli"), 0, 359999)
                    or not _integer(value.get("target_saturation_milli"), 0, 100000)):
                fail()
            for key in ("facet", "target_hue_milli", "target_saturation_milli"):
                result.pop(key)
            result.update(op="turn_on", control_kind="light")
        elif value["op"] in {"facet_number", "facet_choice"}:
            facet = value.get("facet")
            family = "light" if control == "light" else "climate"
            numeric = facet in ({"color_temp_kelvin"} if family == "light" else {"main", "humidity"})
            if (facet not in FACETS[family] or facet in {"color", "range"} or numeric != (value["op"] == "facet_number")
                    or not _integer(value.get("target_index"), 0, MAX_STEPS if numeric else 7)
                    or (not _integer(value.get("expected_index"), 0, MAX_STEPS if numeric else 7)
                        and (numeric or value.get("expected_index") is not None))):
                fail()
            for key in ("facet", "target_index", "expected_index"):
                result.pop(key)
            result.update(op="turn_on",control_kind="light")
        elif control != "light" or value["op"] not in {"brightness", "turn_on", "turn_off"}:
            fail()
        return result
    return None
