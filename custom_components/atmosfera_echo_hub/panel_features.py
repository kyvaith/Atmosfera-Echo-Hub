"""Strict optional family handshake; old entity capability shape is unchanged."""

import json

from .control_session import ProtocolError
from .light_control import _pairs
from .panel_domain import PANEL_TYPES

TYPE = "entity_panel_features_v1"


def valid_types(value):
    return (type(value) is list and bool(value) and all(type(item) is str for item in value)
            and value == [family for family in PANEL_TYPES if family in value])


def decode_features(response, *, bind=False):
    raw = getattr(response, "response_data", None)
    if getattr(response, "success", None) is not True or type(raw) is not bytes or len(raw) > 512:
        raise ProtocolError("panel_features")
    try:
        value = json.loads(raw.decode("utf8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError("nonfinite")))
        fields = {"v", "type", "panel_version", "panel_types"} | ({"channel", "accepted"} if bind else set())
        if (type(value) is not dict or set(value) != fields or type(value["v"]) is not int or value["v"] != 1
                or value["type"] != TYPE or type(value["panel_version"]) is not int or value["panel_version"] not in (0, 1)
                or (not valid_types(value["panel_types"]) if value["panel_version"] else value["panel_types"] != [])):
            raise ProtocolError("panel_features")
        if bind:
            channel = value["channel"]
            if (type(value["accepted"]) is not bool or type(channel) is not str
                    or (value["accepted"] and (value["panel_version"] != 1 or len(channel) != 32 or any(c not in "0123456789abcdef" for c in channel)))
                    or (not value["accepted"] and (value["panel_version"] != 0 or channel != ""))):
                raise ProtocolError("panel_features")
        return value
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        raise ProtocolError("panel_features") from error


def bind_payload(channel, families):
    if (not valid_types(families) or type(channel) is not str or len(channel) != 32
            or any(c not in "0123456789abcdef" for c in channel)):
        raise ProtocolError("panel_features")
    return json.dumps({"v": 1, "type": TYPE, "panel_version": 1, "channel": channel,
                       "panel_types": families}, separators=(",", ":"))
