"""Optional Range1 handshake; the established Detail1 contract is unchanged."""

import json
import re

from .control_session import ProtocolError
from .light_control import _pairs

TYPE = "entity_detail_range_v1"
QUERY = "entity_detail_range_query"
BIND = "entity_detail_range_bind"


def channel_valid(value):
    return type(value) is str and re.fullmatch("[0-9a-f]{32}", value) is not None


def decode_features(response, *, bind=False):
    raw = getattr(response, "response_data", None)
    if getattr(response, "success", None) is not True or type(raw) is not bytes or len(raw) > 512:
        raise ProtocolError("range_features")
    try:
        value = json.loads(raw.decode("utf8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        fields = {"v", "type", "range_version"} | ({"channel", "accepted"} if bind else set())
        if (type(value) is not dict or set(value) != fields or type(value["v"]) is not int or value["v"] != 1
                or value["type"] != TYPE or type(value["range_version"]) is not int or value["range_version"] not in (0, 1)):
            raise ValueError
        if bind and (type(value["accepted"]) is not bool or type(value["channel"]) is not str
                     or value["accepted"] and (value["range_version"] != 1 or not channel_valid(value["channel"]))
                     or not value["accepted"] and (value["range_version"] != 0 or value["channel"] != "")):
            raise ValueError
        return value
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        raise ProtocolError("range_features") from error


def bind_payload(channel):
    if not channel_valid(channel):
        raise ProtocolError("range_features")
    return json.dumps({"v": 1, "type": TYPE, "channel": channel, "range_version": 1}, separators=(",", ":"))
