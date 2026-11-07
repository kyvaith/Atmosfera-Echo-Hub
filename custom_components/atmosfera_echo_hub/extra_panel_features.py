"""Independent extensible profile handshake; old Panel/Detail remain exact."""

import json
import re

from .control_session import ProtocolError
from .light_control import _pairs

TYPE = "entity_panel_extra_v1"
PROFILES = ({"name": "action", "version": 2}, {"name": "datetime", "version": 1}, {"name": "info", "version": 1}, {"name": "info_context", "version": 1}, {"name": "lock", "version": 1}, {"name": "media", "version": 1}, {"name": "text", "version": 1}, {"name": "tile_event", "version": 1})


def valid_channel(value):
    return type(value) is str and re.fullmatch("[0-9a-f]{32}", value) is not None


def valid_profiles(profiles, *, empty=True):
    if type(profiles) is not list or not (0 if empty else 1) <= len(profiles) <= 8:
        return False
    names = []
    for item in profiles:
        if (type(item) is not dict or set(item) != {"name", "version"} or type(item["name"]) is not str
                or not re.fullmatch("[a-z][a-z0-9_]{0,23}", item["name"])
                or type(item["version"]) is not int or not 1 <= item["version"] <= 255):
            return False
        names.append(item["name"])
    return (names == sorted(set(names)) and (
        {"name": "info_context", "version": 1} not in profiles
        or {"name": "info", "version": 1} in profiles) and (
        {"name": "tile_event", "version": 1} not in profiles
        or {"name": "action", "version": 2} in profiles))


def payload(channel, profiles):
    if not valid_channel(channel) or not valid_profiles(profiles):
        raise ProtocolError("extra_features")
    result = json.dumps({"v": 1, "type": TYPE, "channel": channel, "profiles": profiles}, separators=(",", ":"))
    if len(result.encode()) > 512:
        raise ProtocolError("extra_features")
    return result


def decode_response(response, *, channel, offered, bind=False):
    raw = getattr(response, "response_data", None)
    if (getattr(response, "success", None) is not True or type(raw) is not bytes or len(raw) > 512
            or not valid_channel(channel) or not valid_profiles(offered, empty=not bind)):
        raise ProtocolError("extra_features")
    try:
        value = json.loads(raw.decode("utf8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError("nonfinite")))
        required = {"v", "type", "channel", "profiles"} | ({"accepted"} if bind else set())
        if (type(value) is not dict or set(value) != required or type(value["v"]) is not int or value["v"] != 1
                or value["type"] != TYPE or value["channel"] != channel or not valid_profiles(value["profiles"])
                or any(profile not in offered for profile in value["profiles"])
                or bind and (type(value["accepted"]) is not bool
                    or value["accepted"] and value["profiles"] != offered
                    or not value["accepted"] and value["profiles"] != [])):
            raise ProtocolError("extra_features")
        return value
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        raise ProtocolError("extra_features") from error
