"""Strict entity_control_v1 boundary; legacy Light codec remains byte independent."""

from __future__ import annotations

import json

from .control_session import MAX_SEQUENCE, OPEN as LEGACY_OPEN, RESULT_REASONS as LEGACY_REASONS, SELECTION as LEGACY_SELECTION, ProtocolError
from .light_control import TYPE as LIGHT_TYPE, _integer, _pairs, decode as light_decode
from .numeric_domain import MAX_STEPS, NumericDomain, NumericDomainError

TYPE = "entity_control_v1"
MAX_BYTES = 2048
OPEN = LEGACY_OPEN | {"control_kind"}
SELECTION = LEGACY_SELECTION | {"control_kind"}
RESULT_REASONS = LEGACY_REASONS | {"stale_state"}
_NUMBER_STATE = {"domain", "index", "available", "value_text", "state_generation"}
_NUMBER_COMMAND = {"direction", "expected_index", "expected_state_generation"}


def _text(value, maximum):
    return type(value) is str and len(value.encode("utf-8")) <= maximum and all(c.isprintable() for c in value)


def decode(payload):
    """Require exact fields and strict scalar types, including nested duplicates."""
    try:
        raw = payload.encode("utf-8") if isinstance(payload, str) else payload
        if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
            raise ProtocolError("payload_size")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError("nonfinite")))
        if type(value) is not dict or type(value.get("v")) is not int or value["v"] != 1 or value.get("type") != TYPE:
            raise ProtocolError("version")
        kind = value.get("kind")
        translated = dict(value, type=LIGHT_TYPE)
        if kind == "capability":
            if value.get("control_kinds") != ["light", "number"]:
                raise ProtocolError("control_kinds")
            translated.pop("control_kinds")
        elif kind != "bind":
            control = value.get("control_kind")
            if control not in ("light", "number"):
                raise ProtocolError("control_kind")
            translated.pop("control_kind")
            if control == "number" and kind in ("grant", "state"):
                if set(value) != {"v", "type", "kind"} | SELECTION | {"state_seq", "ttl_ms", "title"} | _NUMBER_STATE:
                    raise ProtocolError("number_snapshot")
                domain = NumericDomain.from_descriptor(value["domain"])
                index = value["index"]
                if (index is not None and not _integer(index, 0, domain.max_index)
                        or type(value["available"]) is not bool
                        or value["available"] != (index is not None)
                        or not _integer(value["state_generation"], 1, MAX_SEQUENCE)
                        or not _text(value["value_text"], 64)
                        or value["value_text"] != (str(domain.value_at(index)) if index is not None else "--")):
                    raise ProtocolError("number_snapshot")
                for key in _NUMBER_STATE:
                    translated.pop(key)
                translated.update(on=False, brightness_pct=None,
                                  caps={"brightness": False, "turn_on": False, "turn_off": False})
            elif control == "number" and kind == "command":
                if (not _NUMBER_COMMAND <= value.keys() or value.get("op") != "step"
                        or type(value["direction"]) is not int or value["direction"] not in (-1, 1)
                        or not _integer(value["expected_index"], 0, MAX_STEPS)
                        or not _integer(value["expected_state_generation"], 1, MAX_SEQUENCE)):
                    raise ProtocolError("number_command")
                for key in _NUMBER_COMMAND:
                    translated.pop(key)
                translated["op"] = "turn_on"
            if kind == "result" and value.get("reason") == "stale_state":
                if value.get("status") != "rejected":
                    raise ProtocolError("result_reason")
                translated["reason"] = "unsupported"
        # This validates the unchanged common identity, kind direction, fields,
        # Light body and status/reason combinations through the legacy boundary.
        light_decode(json.dumps(translated, ensure_ascii=False, separators=(",", ":"), allow_nan=False))
        return value
    except (UnicodeError, ValueError, TypeError, KeyError, RecursionError, OverflowError) as error:
        if isinstance(error, ProtocolError):
            raise
        if isinstance(error, NumericDomainError):
            raise ProtocolError("numeric_domain") from error
        raise ProtocolError("json") from error


def encode(value):
    result = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    decode(result)
    return result


def envelope(kind, **fields):
    return {"v": 1, "type": TYPE, "kind": kind, **fields}
