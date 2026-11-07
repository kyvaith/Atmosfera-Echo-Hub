"""Bounded optional feature handshake; existing entity_control_v1 stays exact."""
import json

from .control_session import ProtocolError
from .light_control import _pairs

TYPE = "entity_control_features_v1"
MAX_BYTES = 512


def decode_features(response, *, bind=False, empty_choice=False, cover_panel=False):
    feature = "cover_panel_version" if cover_panel else "empty_choice_version" if empty_choice else "cover_stop_version"
    protocol = "entity_cover_features_v1" if cover_panel else "entity_choice_features_v1" if empty_choice else TYPE
    raw = getattr(response, "response_data", None)
    if getattr(response, "success", None) is not True or not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise ProtocolError("native_features")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError("nonfinite")))
    except (UnicodeError, ValueError, TypeError) as error:
        raise ProtocolError("native_features") from error
    fields = {"v", "type", feature} | ({"channel", "accepted"} if bind else set())
    if (type(value) is not dict or set(value) != fields or type(value.get("v")) is not int or value["v"] != 1
            or value.get("type") != protocol or type(value.get(feature)) is not int
            or value[feature] not in (0, 1)):
        raise ProtocolError("native_features")
    if bind:
        channel = value["channel"]
        if (type(value["accepted"]) is not bool or type(channel) is not str
                or (value["accepted"] and (value[feature] != 1 or len(channel) != 32
                                          or any(c not in "0123456789abcdef" for c in channel)))
                or (not value["accepted"] and (channel != "" or value[feature] != 0))):
            raise ProtocolError("native_features")
    return value
