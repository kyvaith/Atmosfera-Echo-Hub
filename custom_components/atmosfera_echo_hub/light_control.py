"""Isolated W03 proposal: bounded light session, no registered transport or services.

The future bridge must supply authenticated transport admission, caller permission
checks, current context and ordered output. This module registers nothing in HA.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any

from .cards import entity_actions, validate_live_action
from .control_session import (
    CLOSE_REASONS, MAX_SEQUENCE, OPEN, RESULT_REASONS, SELECTION, TERMINAL, TTL_MS,
    ControlSessionOwner, ProtocolError as ProtocolError,
    _Command as _Command, _Selection as _Selection,
)
from .text import plain_text

MAX_BYTES = 2048
MAX_REVISION = 2**53 - 1
TYPE = "light_brightness_v1"
COMMON = {"v", "type", "kind"}
SNAPSHOT = {"state_seq", "ttl_ms", "title", "on", "brightness_pct", "caps"}
STATUSES = TERMINAL | {"pending", "ha_accepted"}
_HEX = re.compile(r"[0-9a-f]{32}\Z", re.ASCII)
_CARD = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z", re.ASCII)


def _integer(value: Any, minimum: int, maximum: int) -> bool:
    return type(value) is int and minimum <= value <= maximum


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProtocolError("duplicate_field")
        result[key] = value
    return result


def decode(payload: str | bytes) -> dict[str, Any]:
    """Validate exact v1 envelopes at the bytes boundary, including output fixtures."""
    try:
        raw = payload.encode("utf-8") if isinstance(payload, str) else payload
        if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
            raise ProtocolError("payload_size")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError("nonfinite")))
        if not isinstance(value, dict) or type(value.get("v")) is not int or value["v"] != 1 or value.get("type") != TYPE:
            raise ProtocolError("version")
        kind = value.get("kind")
        fields = {
            "capability": {"enabled", "max_payload_bytes"}, "bind": {"channel"},
            "open": OPEN, "cancel_open": OPEN | {"reason"},
            "grant": SELECTION | SNAPSHOT, "state": SELECTION | SNAPSHOT,
            "command": SELECTION | {"command_seq", "op"},
            "result": SELECTION | {"command_seq", "state_seq", "status", "reason"},
            "close": SELECTION | {"reason"},
        }.get(kind)
        if fields is None:
            raise ProtocolError("kind")
        if kind == "command" and value.get("op") == "brightness":
            fields = fields | {"value"}
        if set(value) != COMMON | fields:
            raise ProtocolError("fields")
        for key in ("channel", "token"):
            if key in value and (not isinstance(value[key], str) or not _HEX.fullmatch(value[key])):
                raise ProtocolError(key)
        if "card_id" in value and (not isinstance(value["card_id"], str) or not _CARD.fullmatch(value["card_id"])):
            raise ProtocolError("card_id")
        for key in ("open_seq", "command_seq", "state_seq"):
            if key in value and not _integer(value[key], 1, MAX_SEQUENCE):
                raise ProtocolError(key)
        if "revision" in value and not _integer(value["revision"], 0, MAX_REVISION):
            raise ProtocolError("revision")
        if "slot" in value and not _integer(value["slot"], 2, 15):
            raise ProtocolError("slot")
        if kind == "capability" and (type(value["enabled"]) is not bool or type(value["max_payload_bytes"]) is not int or value["max_payload_bytes"] != MAX_BYTES):
            raise ProtocolError("capability")
        if kind in ("grant", "state"):
            if (type(value["ttl_ms"]) is not int or value["ttl_ms"] != TTL_MS
                    or type(value["on"]) is not bool
                    or not isinstance(value["title"], str)
                    or len(value["title"].encode("utf-8")) > 160
                    or any(ord(char) < 32 or ord(char) == 127 for char in value["title"])):
                raise ProtocolError("snapshot")
            if value["brightness_pct"] is not None and not _integer(value["brightness_pct"], 0, 100):
                raise ProtocolError("brightness")
            caps = value["caps"]
            if not isinstance(caps, dict) or set(caps) != {"brightness", "turn_on", "turn_off"} or any(type(item) is not bool for item in caps.values()):
                raise ProtocolError("caps")
            if caps["brightness"] and not (caps["turn_on"] and caps["turn_off"]):
                raise ProtocolError("brightness_requires_power")
            if not caps["brightness"] and value["brightness_pct"] is not None:
                raise ProtocolError("brightness_without_capability")
        if kind == "command":
            if value["op"] not in ("brightness", "turn_on", "turn_off"):
                raise ProtocolError("op")
            if value["op"] == "brightness" and not _integer(value["value"], 0, 100):
                raise ProtocolError("value")
        if kind == "result" and (value["status"] not in STATUSES or value["reason"] not in RESULT_REASONS):
            raise ProtocolError("result")
        if kind == "result":
            status, reason = value["status"], value["reason"]
            if ((status in {"pending", "ha_accepted", "state_matches", "already_matched"} and reason != "none")
                    or (status == "not_confirmed" and reason not in {"service_timeout", "state_timeout"})
                    or (status == "rejected" and reason in {"none", "service_timeout", "state_timeout"})):
                raise ProtocolError("result_reason")
        if kind in ("close", "cancel_open") and value["reason"] not in CLOSE_REASONS:
            raise ProtocolError("reason")
        return value
    except (UnicodeError, ValueError, TypeError, RecursionError, OverflowError) as err:
        if isinstance(err, ProtocolError):
            raise
        raise ProtocolError("json") from err


def encode(value: dict[str, Any]) -> str:
    """Every outgoing envelope crosses the same strict boundary."""
    result = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    decode(result)
    return result


def envelope(kind: str, **fields: Any) -> dict[str, Any]:
    return {"v": 1, "type": TYPE, "kind": kind, **fields}


@dataclass(frozen=True)
class LightContext:
    """Trusted bridge snapshot, proposed adapter; never accepted from device JSON.

    runtime identity is compared with ``is``; epoch changes on reconnect. v3 and
    explicit control action are admission requirements, not a v2 migration here.
    """

    epoch: int
    runtime: object
    available: bool
    layout_version: int
    revision: int
    sent_revision: int | None
    cards: tuple[dict[str, Any], ...]
    editable_slots: frozenset[int] = frozenset(range(2, 16))


class LightControlOwner(ControlSessionOwner):
    """Light policy over the one shared session owner; public v1 wire is unchanged."""

    _decode = staticmethod(decode)
    _encode = staticmethod(encode)
    _envelope = staticmethod(envelope)

    def _entity_binding(self, card: dict[str, Any]) -> tuple[Any, dict[str, bool]]:
        if (card.get("action") != {"kind": "control", "control": "light"}
                or not isinstance(card.get("entity_id"), str) or not card["entity_id"].startswith("light.")):
            raise ProtocolError("selection_changed")
        state = self.hass.states.get(card["entity_id"])
        if state is None or state.state not in ("on", "off"):
            raise ProtocolError("entity_unavailable")
        try:
            descriptors = {item["service"]: item["fields"] for item in entity_actions(self.hass, state)}
        except (TypeError, ValueError, AttributeError):
            raise ProtocolError("unsupported") from None
        caps = {"turn_on": "light.turn_on" in descriptors, "turn_off": "light.turn_off" in descriptors}
        modes = state.attributes.get("supported_color_modes")
        brightness_mode = (isinstance(modes, (list, tuple, set, frozenset))
                           and all(isinstance(mode, str) for mode in modes)
                           and bool(set(modes) & {"brightness", "color_temp", "hs", "xy", "rgb", "rgbw", "rgbww", "white"}))
        caps["brightness"] = (caps["turn_on"] and caps["turn_off"] and brightness_mode
                              and "brightness_pct" in descriptors.get("light.turn_on", {}))
        if not caps["turn_on"] and not caps["turn_off"]:
            raise ProtocolError("unsupported")
        return state, caps

    @staticmethod
    def _brightness(state: Any, caps: dict[str, bool]) -> int | None:
        if not caps["brightness"]:
            return None
        if state.state == "off":
            return 0
        raw = state.attributes.get("brightness")
        return (raw * 100 + 127) // 255 if _integer(raw, 0, 255) else None


    def _snapshot_fields(self, state: Any, card: dict[str, Any], caps: dict[str, bool]) -> dict[str, Any]:
        title = plain_text(card.get("title") or state.attributes.get("friendly_name") or "Light", 40)
        # Local HA/title data is not wire-validated input. Remove non-wire code
        # points here without altering the saved title or shared text helper.
        title = "".join(char for char in title if ord(char) >= 32 and ord(char) != 127
                        and not 0xD800 <= ord(char) <= 0xDFFF)
        # plain_text's character budget does not imply a UTF-8 byte budget.
        while len(title.encode("utf-8")) > 160:
            title = title[:-1]
        return {"title": title, "on": state.state == "on", "brightness_pct": self._brightness(state, caps), "caps": caps}

    def _state_matches(self, state: Any, caps: dict[str, bool], command: dict[str, Any]) -> bool:
        if command["op"] == "turn_on":
            return state.state == "on"
        if command["op"] == "turn_off" or command.get("value") == 0:
            return state.state == "off"
        value = self._brightness(state, caps)
        return state.state == "on" and value is not None and abs(value - command["value"]) <= 1


    def _service_action(self, state: Any, caps: dict[str, bool], message: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        if not caps[message["op"]]:
            raise ProtocolError("unsupported")
        operation = "turn_off" if message["op"] == "turn_off" or message.get("value") == 0 else "turn_on"
        data = {"brightness_pct": message["value"]} if message["op"] == "brightness" and message["value"] else {}
        validate_live_action(self.hass, state, {"service": f"light.{operation}", "data": data})
        return "light", operation, data
