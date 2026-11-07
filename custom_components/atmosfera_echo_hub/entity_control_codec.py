"""Strict entity_control_v1 boundary; legacy Light codec remains byte independent."""

from __future__ import annotations

import json
from .cover_domain import CoverDomain, CoverDomainError, KNOWN_STATES, OPERATIONS as COVER_OPERATIONS
from .cover_panel_domain import CoverPanelDomain, NUMERIC_OPERATIONS as COVER_NUMERIC_OPERATIONS, PANEL_OPERATIONS as COVER_PANEL_OPERATIONS
from . import statistics_codec, agenda_codec, action_panel_codec, datetime_panel_codec, detail_codec, media_panel_codec, text_panel_codec

from .panel_domain import PanelDomain, PanelDomainError, PanelObservation, OPERATIONS as PANEL_OPERATIONS
from .extra_panel_domain import CONTEXT_INFO_TYPES, ExtraDomain, ExtraObservation, ExtraPanelError
from .control_session import MAX_SEQUENCE, OPEN as LEGACY_OPEN, RESULT_REASONS as LEGACY_REASONS, SELECTION as LEGACY_SELECTION, ProtocolError
from .light_control import TYPE as LIGHT_TYPE, _integer, _pairs, decode as light_decode
from .numeric_domain import MAX_STEPS, SCALE, NumericDomain, NumericDomainError, _micro, _text as decimal_text
from .number_domain import THERMOSTAT_ACTIVITIES
from .choice_domain import MAX_OPTIONS, ChoiceDomain, ChoiceDomainError
from .fan_domain import DIRECTIONS, OPERATIONS as FAN_OPERATIONS, FanDomain, FanDomainError
from .humidifier_domain import OPERATIONS as HUMIDIFIER_OPERATIONS, HumidifierDomain, HumidifierDomainError, measurement_text
from .robot_domain import (RobotDomain, RobotDomainError, ACTIVITIES as ROBOT_ACTIVITIES, BITS as ROBOT_BITS,
                           SERVICES as ROBOT_SERVICES, OPERATIONS as ROBOT_OPERATIONS, INDEXED_OPERATIONS,
                           vacuum_actions, mower_actions)

TYPE = "entity_control_v1"
MAX_BYTES = 2048
OPEN = LEGACY_OPEN | {"control_kind"}
SELECTION = LEGACY_SELECTION | {"control_kind"}
RESULT_REASONS = LEGACY_REASONS | {"stale_state"}
_NUMBER_STATE = {"domain", "index", "available", "value_text", "state_generation"}
_NUMBER_COMMAND = {"direction", "expected_index", "expected_state_generation"}
_CHOICE_STATE = {"options", "index", "available", "state_generation"}
_CHOICE_COMMAND = {"target_index", "expected_index", "expected_state_generation"}
_COVER_STATE = {"cover_state", "position", "available", "cover_caps", "state_generation"}
_COVER_COMMAND = {"expected_state_generation"}
_FAN_STATE = {"fan_state", "available", "percentage", "preset_index", "preset_known", "oscillating",
              "direction", "fan_caps", "state_generation"}
_FAN_COMMAND = {"target_index", "expected_state_generation"}
_HUMIDIFIER_STATE = {"humidifier_state", "available", "humidity_domain", "humidity_index", "humidity_text",
                     "current_humidity", "mode_index", "device_class", "humidifier_caps", "state_generation"}
_PANEL_STATE = {"panel_type", "panel_caps", "panel_state", "available", "eligible_actions", "state_generation"}
_ROBOT_STATE = {"robot_type", "activity", "available", "speed_index", "battery_percent", "robot_caps",
                "eligible_actions", "area_enabled", "state_generation"}
_CONTROL_KINDS = (["light", "number"], ["light", "number", "choice"],
                  ["light", "number", "cover"], ["light", "number", "choice", "cover"])


def _text(value, maximum):
    return type(value) is str and len(value.encode("utf-8")) <= maximum and all(c.isprintable() for c in value)


def _valid_thermostat(value, dial):
    fields = {"unit", "target", "current", "min", "max", "level", "activity"}
    if dial and isinstance(value, dict) and value.get("dial") is True:
        fields.add("dial")
    if (type(value) is not dict or set(value) != fields
            or value["unit"] not in ("°C", "°F") or value["activity"] not in THERMOSTAT_ACTIVITIES
            or (value["level"] is not None and not _integer(value["level"], 0, 100))):
        return False
    for key in ("target", "current", "min", "max"):
        text = value[key]
        if type(text) is not str or len(text) > 12:
            return False
        if text:
            micro = _micro(text)
            if not -100 * SCALE <= micro <= 300 * SCALE or decimal_text(micro) != text:
                return False
    return True


def decode(payload, *, empty_choice=False, thermostat=False, thermostat_dial=False, cover_panel=False, light_detail=False, climate_panel=False, light_color=False, climate_range=False, info_agenda=False, info_statistics=False, extra_profiles=(), action_dispatched=False, action_parameters=False):
    """Require exact fields and strict scalar types, including nested duplicates."""
    try:
        raw = payload.encode("utf-8") if isinstance(payload, str) else payload
        if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
            raise ProtocolError("payload_size")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError("nonfinite")))
        if type(value) is not dict or type(value.get("v")) is not int or value["v"] != 1 or value.get("type") != TYPE:
            raise ProtocolError("version")
        normalized = statistics_codec.translate(value, enabled=info_statistics and "info" in extra_profiles)
        if normalized is None:
            normalized = agenda_codec.translate(value, enabled=info_agenda and "info" in extra_profiles)
        if normalized is None:
            normalized = text_panel_codec.translate(value, enabled="text" in extra_profiles)
        if normalized is None:
            normalized = datetime_panel_codec.translate(value, enabled="datetime" in extra_profiles)
        if normalized is None:
            normalized = action_panel_codec.translate(value, enabled="action" in extra_profiles,
                                                       tile_event="tile_event" in extra_profiles and action_dispatched,
                                                       parameters=action_parameters and action_dispatched)
        if normalized is None:
            normalized = media_panel_codec.translate(value, enabled="media" in extra_profiles)
        if normalized is None:
            normalized = detail_codec.translate(value, light=light_detail, climate=climate_panel, color=light_color, range_enabled=climate_range)
        if normalized is not None:
            decode(json.dumps(normalized, ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                   empty_choice=empty_choice, thermostat=thermostat, thermostat_dial=thermostat_dial, cover_panel=cover_panel)
            return value
        kind = value.get("kind")
        translated = dict(value, type=LIGHT_TYPE)
        if kind == "capability":
            if value.get("control_kinds") not in tuple(kinds + extra + robot + panel for kinds in _CONTROL_KINDS
                    for extra in ([], ["fan"], ["humidifier"], ["fan", "humidifier"]) for robot in ([], ["robot"]) for panel in ([], ["panel"])):
                raise ProtocolError("control_kinds")
            translated.pop("control_kinds")
        elif kind != "bind":
            control = value.get("control_kind")
            if control not in ("light", "number", "choice", "cover", "fan", "humidifier", "robot", "panel"):
                raise ProtocolError("control_kind")
            translated.pop("control_kind")
            if control == "panel" and kind in ("grant", "state"):
                if set(value) != {"v", "type", "kind"} | SELECTION | {"state_seq", "ttl_ms", "title"} | _PANEL_STATE:
                    raise ProtocolError("panel_snapshot")
                if value["panel_type"] in {"info", "lock"}:
                    if value["panel_type"] not in extra_profiles:
                        raise ProtocolError("unsupported")
                    domain = ExtraDomain.from_descriptor(value["panel_type"], value["panel_caps"])
                    if domain.info_type in CONTEXT_INFO_TYPES and "info_context" not in extra_profiles:
                        raise ProtocolError("unsupported")
                    observed = ExtraObservation.from_descriptor(domain, value["panel_state"])
                else:
                    domain = PanelDomain.from_descriptor(value["panel_type"], value["panel_caps"])
                    observed = PanelObservation.from_descriptor(domain, value["panel_state"])
                if (type(value["available"]) is not bool or value["available"] != observed.available
                        or not _integer(value["eligible_actions"], 0, 31) or value["eligible_actions"] != observed.eligible(domain)
                        or not _integer(value["state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("panel_snapshot")
                for key in _PANEL_STATE:
                    translated.pop(key)
                translated.update(on=False, brightness_pct=None,
                                  caps={"brightness": False, "turn_on": False, "turn_off": False})
            elif control == "panel" and kind == "command":
                operation = value.get("op")
                fields = {"expected_state_generation"}
                if operation in {"power", "activity"}:
                    fields.add("target_index")
                    valid_target = _integer(value.get("target_index"), 0, 1 if operation == "power" else 7)
                elif operation == "set_duration":
                    fields.add("duration_seconds")
                    valid_target = _integer(value.get("duration_seconds"), 1, 86400)
                else:
                    valid_target = operation in PANEL_OPERATIONS or operation == "lock" and "lock" in extra_profiles
                if (not fields <= value.keys() or not valid_target
                        or not _integer(value["expected_state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("panel_command")
                for key in fields:
                    translated.pop(key)
                translated["op"] = "turn_on"
            elif control == "robot" and kind in ("grant", "state"):
                if set(value) != {"v", "type", "kind"} | SELECTION | {"state_seq", "ttl_ms", "title"} | _ROBOT_STATE:
                    raise ProtocolError("robot_snapshot")
                domain = RobotDomain.from_descriptor(value["robot_type"], value["robot_caps"])
                activity, available = value["activity"], value["available"]
                index, battery, eligible = value["speed_index"], value["battery_percent"], value["eligible_actions"]
                policy = vacuum_actions if domain.robot_type == "vacuum" else mower_actions
                maximum = sum(bit for op, bit in ROBOT_BITS.items() if domain.actions & bit
                              and activity in policy.ALLOWED[ROBOT_SERVICES[domain.robot_type][op]])
                if (activity not in ROBOT_ACTIVITIES[domain.robot_type] | {"unknown"}
                        or type(available) is not bool or available != (activity != "unknown")
                        or not _integer(eligible, 0, 63) or eligible & ~maximum
                        or (index is not None and not _integer(index, 0, len(domain.speeds) - 1))
                        or (battery is not None and not _integer(battery, 0, 100))
                        or type(value["area_enabled"]) is not bool
                        or (value["area_enabled"] and (not domain.areas or activity not in {"docked", "idle", "paused"}))
                        or (not available and (index is not None or battery is not None or eligible or value["area_enabled"]))
                        or not _integer(value["state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("robot_snapshot")
                for key in _ROBOT_STATE:
                    translated.pop(key)
                translated.update(on=False, brightness_pct=None,
                                  caps={"brightness": False, "turn_on": False, "turn_off": False})
            elif control == "robot" and kind == "command":
                operation = value.get("op")
                fields = {"expected_state_generation"} | ({"target_index"} if operation in INDEXED_OPERATIONS else set())
                if (not fields <= value.keys() or operation not in ROBOT_OPERATIONS
                        or ("target_index" in fields and not _integer(value["target_index"], 0, 7))
                        or not _integer(value["expected_state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("robot_command")
                for key in fields:
                    translated.pop(key)
                translated["op"] = "turn_on"
            elif control == "humidifier" and kind in ("grant", "state"):
                if set(value) != {"v", "type", "kind"} | SELECTION | {"state_seq", "ttl_ms", "title"} | _HUMIDIFIER_STATE:
                    raise ProtocolError("humidifier_snapshot")
                domain = HumidifierDomain.from_descriptor(value["humidifier_caps"], value["humidity_domain"], value["device_class"])
                power, available, index = value["humidifier_state"], value["available"], value["humidity_index"]
                text, current, mode = value["humidity_text"], value["current_humidity"], value["mode_index"]
                if (power not in ("on", "off", "unknown") or type(available) is not bool
                        or available != (power in ("on", "off"))
                        or (index is not None and (domain.humidity is None or not _integer(index, 0, domain.humidity.max_index)))
                        or text != (str(domain.humidity.value_at(index)) if index is not None else "--")
                        or type(current) is not str or len(current) > 12 or current != measurement_text(current)
                        or (mode is not None and not _integer(mode, 0, len(domain.modes) - 1))
                        or (not available and (index is not None or mode is not None or current))
                        or not _integer(value["state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("humidifier_snapshot")
                for key in _HUMIDIFIER_STATE:
                    translated.pop(key)
                translated.update(on=False, brightness_pct=None,
                                  caps={"brightness": False, "turn_on": False, "turn_off": False})
            elif control == "humidifier" and kind == "command":
                operation = value.get("op")
                maximum = {"power": 1, "humidity": 100, "mode": 7}.get(operation, -1)
                if (not _FAN_COMMAND <= value.keys() or operation not in HUMIDIFIER_OPERATIONS
                        or not _integer(value["target_index"], 0, maximum)
                        or not _integer(value["expected_state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("humidifier_command")
                for key in _FAN_COMMAND:
                    translated.pop(key)
                translated["op"] = "turn_on"
            elif control == "fan" and kind in ("grant", "state"):
                if set(value) != {"v", "type", "kind"} | SELECTION | {"state_seq", "ttl_ms", "title"} | _FAN_STATE:
                    raise ProtocolError("fan_snapshot")
                domain = FanDomain.from_descriptor(value["fan_caps"])
                power, available, percentage = value["fan_state"], value["available"], value["percentage"]
                index, known, oscillating, direction = (value["preset_index"], value["preset_known"],
                                                       value["oscillating"], value["direction"])
                if (power not in ("on", "off", "unknown") or type(available) is not bool
                        or available != (power in ("on", "off")) or type(known) is not bool
                        or (percentage is not None and not _integer(percentage, 0, 100))
                        or (index is not None and (not known or not _integer(index, 0, len(domain.presets) - 1)))
                        or (known and not domain.presets)
                        or (oscillating is not None and (not domain.oscillate or type(oscillating) is not bool))
                        or (direction is not None and (not domain.direction or direction not in DIRECTIONS))
                        or (not available and (known or any(item is not None for item in (percentage, index, oscillating, direction))))
                        or not _integer(value["state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("fan_snapshot")
                for key in _FAN_STATE:
                    translated.pop(key)
                translated.update(on=False, brightness_pct=None,
                                  caps={"brightness": False, "turn_on": False, "turn_off": False})
            elif control == "fan" and kind == "command":
                operation = value.get("op")
                maximum = 7 if operation in ("speed", "preset") else 1
                if (not _FAN_COMMAND <= value.keys() or operation not in FAN_OPERATIONS
                        or not _integer(value["target_index"], 0, maximum)
                        or not _integer(value["expected_state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("fan_command")
                for key in _FAN_COMMAND:
                    translated.pop(key)
                translated["op"] = "turn_on"
            elif control == "cover" and kind in ("grant", "state"):
                state_fields = _COVER_STATE | ({"cover_panel"} if cover_panel else set())
                if set(value) != {"v", "type", "kind"} | SELECTION | {"state_seq", "ttl_ms", "title"} | state_fields:
                    raise ProtocolError("cover_snapshot")
                if cover_panel:
                    CoverPanelDomain.from_panel_descriptor(value["cover_caps"], value["cover_panel"])
                    if not value["available"] and value["cover_panel"]["tilt_position"] is not None:
                        raise ProtocolError("cover_snapshot")
                else:
                    CoverDomain.from_descriptor(value["cover_caps"])
                state, position, available = value["cover_state"], value["position"], value["available"]
                if (state not in KNOWN_STATES | {"unknown"} or type(available) is not bool
                        or available != (state in KNOWN_STATES)
                        or (position is not None and (not available or not _integer(position, 0, 100)))
                        or not _integer(value["state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("cover_snapshot")
                for key in state_fields:
                    translated.pop(key)
                translated.update(on=False, brightness_pct=None,
                                  caps={"brightness": False, "turn_on": False, "turn_off": False})
            elif control == "cover" and kind == "command":
                operation = value.get("op")
                fields = _COVER_COMMAND | ({"target_index"} if cover_panel and operation in COVER_NUMERIC_OPERATIONS else set())
                if (not fields <= value.keys() or operation not in (COVER_PANEL_OPERATIONS if cover_panel else COVER_OPERATIONS)
                        or ("target_index" in fields and not _integer(value["target_index"], 0, 100))
                        or not _integer(value["expected_state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("cover_command")
                for key in fields:
                    translated.pop(key)
                translated["op"] = "turn_on"
            elif control == "choice" and kind in ("grant", "state"):
                if set(value) != {"v", "type", "kind"} | SELECTION | {"state_seq", "ttl_ms", "title"} | _CHOICE_STATE:
                    raise ProtocolError("choice_snapshot")
                domain = ChoiceDomain.from_options(value["options"])
                index = value["index"]
                if (index is not None and not _integer(index, 0, len(domain.options) - 1)
                        or type(value["available"]) is not bool
                        or (value["available"] != (index is not None)
                            and not (empty_choice and value["available"] and index is None))
                        or not _integer(value["state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("choice_snapshot")
                for key in _CHOICE_STATE:
                    translated.pop(key)
                translated.update(on=False, brightness_pct=None,
                                  caps={"brightness": False, "turn_on": False, "turn_off": False})
            elif control == "choice" and kind == "command":
                if (not _CHOICE_COMMAND <= value.keys() or value.get("op") != "choose"
                        or not _integer(value["target_index"], 0, MAX_OPTIONS - 1)
                        or (not _integer(value["expected_index"], 0, MAX_OPTIONS - 1)
                            and not (empty_choice and value["expected_index"] is None))
                        or not _integer(value["expected_state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("choice_command")
                for key in _CHOICE_COMMAND:
                    translated.pop(key)
                translated["op"] = "turn_on"
            elif control == "number" and kind in ("grant", "state"):
                state_fields = _NUMBER_STATE
                if thermostat and "thermostat" in value:
                    if not _valid_thermostat(value["thermostat"], thermostat_dial):
                        raise ProtocolError("thermostat_snapshot")
                    state_fields = _NUMBER_STATE | {"thermostat"}
                if set(value) != {"v", "type", "kind"} | SELECTION | {"state_seq", "ttl_ms", "title"} | state_fields:
                    raise ProtocolError("number_snapshot")
                domain = (None if "thermostat" in state_fields and value["domain"] is None
                          else NumericDomain.from_descriptor(value["domain"]))
                index = value["index"]
                if (index is not None and (domain is None or not _integer(index, 0, domain.max_index))
                        or type(value["available"]) is not bool
                        or value["available"] != (index is not None)
                        or not _integer(value["state_generation"], 1, MAX_SEQUENCE)
                        or not _text(value["value_text"], 64)
                        or value["value_text"] != (str(domain.value_at(index)) if index is not None else "--")):
                    raise ProtocolError("number_snapshot")
                for key in state_fields:
                    translated.pop(key)
                translated.update(on=False, brightness_pct=None,
                                  caps={"brightness": False, "turn_on": False, "turn_off": False})
            elif control == "number" and kind == "command":
                fields = _NUMBER_COMMAND
                if value.get("op") == "set_target" and thermostat_dial:
                    fields = (_NUMBER_COMMAND - {"direction"}) | {"target_index"}
                    valid_target = _integer(value.get("target_index"), 0, MAX_STEPS)
                else:
                    valid_target = value.get("op") == "step" and type(value.get("direction")) is int and value["direction"] in (-1, 1)
                if (not fields <= value.keys() or not valid_target
                        or not _integer(value["expected_index"], 0, MAX_STEPS)
                        or not _integer(value["expected_state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("number_command")
                for key in fields:
                    translated.pop(key)
                translated["op"] = "turn_on"
            if kind == "result" and value.get("reason") == "stale_state":
                if value.get("status") != "rejected":
                    raise ProtocolError("result_reason")
                translated["reason"] = "unsupported"
            if kind == "result" and value.get("status") == "service_dispatched":
                if action_dispatched is not True or "action" not in extra_profiles or control != "panel" or value.get("reason") != "none":
                    raise ProtocolError("result_reason")
                translated["status"] = "ha_accepted"
            if kind == "result" and value.get("status") == "service_completed":
                if control not in {"robot", "panel"} or value.get("reason") != "none":
                    raise ProtocolError("result_reason")
                # Validate unchanged common fields with a legacy-compatible
                # status, without changing the returned Robot terminal value.
                translated["status"] = "ha_accepted"
        # This validates the unchanged common identity, kind direction, fields,
        # Light body and status/reason combinations through the legacy boundary.
        light_decode(json.dumps(translated, ensure_ascii=False, separators=(",", ":"), allow_nan=False))
        return value
    except (UnicodeError, ValueError, TypeError, KeyError, RecursionError, OverflowError) as error:
        if isinstance(error, ProtocolError):
            raise
        if isinstance(error, NumericDomainError):
            raise ProtocolError("numeric_domain") from error
        if isinstance(error, ChoiceDomainError):
            raise ProtocolError("choice_domain") from error
        if isinstance(error, CoverDomainError):
            raise ProtocolError("cover_domain") from error
        if isinstance(error, FanDomainError):
            raise ProtocolError("fan_domain") from error
        if isinstance(error, HumidifierDomainError):
            raise ProtocolError("humidifier_domain") from error
        if isinstance(error, PanelDomainError):
            raise ProtocolError("panel_domain") from error
        if isinstance(error, RobotDomainError):
            raise ProtocolError("robot_domain") from error
        raise ProtocolError("json") from error


def decode_report(payload):
    """Structural service ingress; the matched owner validates negotiation next."""
    message = decode(payload, empty_choice=True, thermostat_dial=True, cover_panel=True, light_detail=True, climate_panel=True, light_color=True, climate_range=True, info_agenda=True, info_statistics=True, extra_profiles=("action", "datetime", "info", "info_context", "lock", "media", "text", "tile_event"), action_dispatched=True, action_parameters=True)
    if message["kind"] not in {"open", "command", "close", "cancel_open", "facet", "page"}:
        raise ProtocolError("direction")
    return message


def encode(value, *, empty_choice=False, thermostat=False, thermostat_dial=False, cover_panel=False, light_detail=False, climate_panel=False, light_color=False, climate_range=False, info_agenda=False, info_statistics=False, extra_profiles=(), action_dispatched=False, action_parameters=False):
    result = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    decode(result, empty_choice=empty_choice, thermostat=thermostat, thermostat_dial=thermostat_dial, cover_panel=cover_panel,
           light_detail=light_detail, climate_panel=climate_panel, light_color=light_color, climate_range=climate_range, info_agenda=info_agenda, info_statistics=info_statistics, extra_profiles=extra_profiles, action_dispatched=action_dispatched, action_parameters=action_parameters)
    return result


def envelope(kind, **fields):
    return {"v": 1, "type": TYPE, "kind": kind, **fields}
