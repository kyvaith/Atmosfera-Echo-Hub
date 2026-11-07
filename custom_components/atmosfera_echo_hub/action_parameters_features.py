"""Independent ActionParams1 opt-in; the eight Extra profiles stay unchanged."""

import json
from .control_session import ProtocolError
from .light_control import _pairs
from .extra_panel_features import valid_channel

TYPE = "entity_action_parameters_v1"
QUERY = "entity_action_parameters_query"
BIND = "entity_action_parameters_bind"


def decode_features(response, *, bind=False):
    raw = getattr(response, "response_data", None)
    if getattr(response, "success", None) is not True or type(raw) is not bytes or len(raw) > 512:
        raise ProtocolError("action_parameters_features")
    try:
        value = json.loads(raw.decode("utf8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        fields = {"v", "type", "parameters_version"} | ({"channel", "accepted"} if bind else set())
        if (type(value) is not dict or set(value) != fields or type(value["v"]) is not int or value["v"] != 1
                or value["type"] != TYPE or type(value["parameters_version"]) is not int
                or value["parameters_version"] not in (0, 1)):
            raise ValueError
        if bind and (type(value["accepted"]) is not bool or type(value["channel"]) is not str
                     or value["accepted"] and (value["parameters_version"] != 1 or not valid_channel(value["channel"]))
                     or not value["accepted"] and (value["parameters_version"] != 0 or value["channel"] != "")):
            raise ValueError
        return value
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        raise ProtocolError("action_parameters_features") from error


def bind_payload(channel):
    if not valid_channel(channel):
        raise ProtocolError("action_parameters_features")
    return json.dumps({"v": 1, "type": TYPE, "channel": channel, "parameters_version": 1}, separators=(",", ":"))
