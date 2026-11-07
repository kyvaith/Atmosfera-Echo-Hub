"""Optional detail handshake; old Panel-v1 family contract stays exact."""

import json

from .control_session import ProtocolError
from .light_control import _pairs

TYPE = "entity_detail_features_v1"
FIELDS = {"v", "type", "detail_version", "light_detail_version", "climate_panel_version"}


def decode_features(response, *, bind=False):
    raw = getattr(response, "response_data", None)
    if getattr(response, "success", None) is not True or type(raw) is not bytes or len(raw) > 512:
        raise ProtocolError("detail_features")
    try:
        value = json.loads(raw.decode("utf8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError("nonfinite")))
        if (type(value) is not dict or set(value) != FIELDS | ({"channel", "accepted"} if bind else set())
                or type(value["v"]) is not int or value["v"] != 1 or value["type"] != TYPE
                or any(type(value[key]) is not int or value[key] not in (0, 1)
                       for key in ("detail_version", "light_detail_version", "climate_panel_version"))
                or value["detail_version"] != int(bool(value["light_detail_version"] or value["climate_panel_version"]))):
            raise ProtocolError("detail_features")
        if bind and (type(value["accepted"]) is not bool or type(value["channel"]) is not str
                or (value["accepted"] and (value["detail_version"] != 1 or len(value["channel"]) != 32
                    or any(c not in "0123456789abcdef" for c in value["channel"])))
                or (not value["accepted"] and (value["detail_version"] != 0 or value["channel"] != ""))):
            raise ProtocolError("detail_features")
        return value
    except (ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        raise ProtocolError("detail_features") from error


def bind_payload(channel, light, climate):
    value = {"v": 1, "type": TYPE, "detail_version": 1, "light_detail_version": light,
             "climate_panel_version": climate, "channel": channel}
    raw = json.dumps(value | {"accepted": True}, separators=(",", ":")).encode()
    from types import SimpleNamespace
    decode_features(SimpleNamespace(success=True, response_data=raw), bind=True)
    return json.dumps(value, separators=(",", ":"))
