"""Bounded public input_text values; hidden values never enter a descriptor."""

from dataclasses import dataclass, field
import hashlib
import json

ACTION = {"kind": "control", "control": "panel", "property": "text"}
MAX_CODEPOINTS = 255
MAX_UTF8_BYTES = 1020
# Product policy, independently supplied to the reusable native editor.
REPERTOIRE = frozenset(chr(value) for value in range(0x20, 0x7F)) | frozenset("ĄąĆćĘęŁłŃńÓóŚśŹźŻż")
SOURCES = ("known", "unknown", "unavailable", "unsupported")
REASONS = ("none", "password", "mode", "pattern", "bounds", "length", "encoding", "characters")
RESERVED = frozenset(("unknown", "unavailable"))


class TextPanelError(ValueError):
    """Malformed Text descriptor or inadmissible exact target."""


def valid_bounds(minimum, maximum):
    return (type(minimum) is int and type(maximum) is int
            and 0 <= minimum <= maximum <= MAX_CODEPOINTS and maximum >= 1)


def value_reason(value, minimum=0, maximum=MAX_CODEPOINTS):
    if type(value) is not str:
        return "encoding"
    try:
        size = len(value.encode("utf8"))
    except UnicodeError:
        return "encoding"
    if not minimum <= len(value) <= maximum or len(value) > MAX_CODEPOINTS or size > MAX_UTF8_BYTES:
        return "length"
    if any(char not in REPERTOIRE for char in value):
        return "characters"
    return "none"


def valid_target(value, minimum=0, maximum=MAX_CODEPOINTS):
    return value_reason(value, minimum, maximum) == "none" and value not in RESERVED


def _semantic(value):
    """Keep exact typed configuration locally; never send raw patterns."""
    return type(value).__name__, json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)


@dataclass(frozen=True)
class TextDomain:
    minimum: int | None
    maximum: int | None
    can_set: bool
    blocked_reason: str = field(default="none", repr=False)
    policy: tuple = field(default=(), repr=False)
    family = "text"

    @classmethod
    def from_descriptor(cls, value):
        if (type(value) is not dict or set(value) != {"min", "max", "can_set"}
                or type(value["can_set"]) is not bool):
            raise TextPanelError("caps")
        minimum, maximum = value["min"], value["max"]
        if not valid_bounds(minimum, maximum) and not (minimum is maximum is None and not value["can_set"]):
            raise TextPanelError("bounds")
        return cls(minimum, maximum, value["can_set"])

    @classmethod
    def from_ha(cls, hass, state):
        if state.entity_id.partition(".")[0] != "input_text":
            raise TextPanelError("domain")
        attrs = state.attributes
        mode, pattern = attrs.get("mode"), attrs.get("pattern")
        minimum, maximum = attrs.get("min"), attrs.get("max")
        bounds = valid_bounds(minimum, maximum)
        # Determine privacy before anyone reads state.state.
        reason = ("password" if mode == "password" else "mode" if mode != "text" else
                  "pattern" if pattern is not None else "bounds" if not bounds else "none")
        policy = tuple(_semantic(item) for item in (mode, pattern, minimum, maximum))
        return cls(minimum if bounds else None, maximum if bounds else None,
                   reason == "none" and hass.services.has_service("input_text", "set_value"), reason, policy)

    def descriptor(self):
        return {"min": self.minimum, "max": self.maximum, "can_set": self.can_set}

    @property
    def fingerprint(self):
        value = [self.family, self.descriptor(), self.blocked_reason, self.policy, sorted(REPERTOIRE)]
        return hashlib.sha256(json.dumps(value, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()

    def service_action(self, entity_id, operation, target):
        if (not self.can_set or operation != "set_value" or not entity_id.startswith("input_text.")
                or not valid_target(target, self.minimum, self.maximum)):
            raise TextPanelError("target")
        return "input_text", "set_value", {"value": target}


@dataclass(frozen=True)
class TextObservation:
    source: str
    value: str | None
    reason: str = "none"

    @property
    def available(self):
        return self.source == "known"

    @property
    def command_state(self):
        return self.source, self.value, self.reason

    def descriptor(self):
        return {"source": self.source, "value": self.value, "reason": self.reason}

    @classmethod
    def from_descriptor(cls, domain, value):
        if (type(value) is not dict or set(value) != {"source", "value", "reason"}
                or type(value["source"]) is not str or value["source"] not in SOURCES
                or type(value["reason"]) is not str or value["reason"] not in REASONS):
            raise TextPanelError("state")
        source, text, reason = value["source"], value["value"], value["reason"]
        bounds = valid_bounds(domain.minimum, domain.maximum)
        if source != "unsupported":
            if reason != "none" or not bounds:
                raise TextPanelError("state")
            if source == "known":
                if not valid_target(text, domain.minimum, domain.maximum):
                    raise TextPanelError("value")
            elif text is not None:
                raise TextPanelError("hidden_value")
        elif (reason == "none" or text is not None
              or reason in {"password", "mode", "pattern", "bounds"} and domain.can_set
              or reason == "bounds" and bounds
              or reason in {"length", "encoding", "characters"} and not bounds):
            raise TextPanelError("unsupported_state")
        return cls(source, text, reason)

    @classmethod
    def from_ha(cls, hass, state, domain):
        if domain.blocked_reason != "none":
            return cls("unsupported", None, domain.blocked_reason)
        raw = state.state
        if type(raw) is str and raw in RESERVED:
            return cls(raw, None)
        reason = value_reason(raw, domain.minimum, domain.maximum)
        return cls("known", raw) if reason == "none" else cls("unsupported", None, reason)

    def eligible(self, domain):
        return int(self.available and domain.can_set)

    def can_command(self, domain, operation, target):
        return bool(self.eligible(domain) and operation == "set_value"
                    and valid_target(target, domain.minimum, domain.maximum))

    def matches(self, operation, target):
        return self.available and operation == "set_value" and self.value == target


def text_metadata(hass, state, language=None):
    try:
        domain = TextDomain.from_ha(hass, state)
        observed = TextObservation.from_ha(hass, state, domain)
    except TextPanelError:
        return {}
    return {"text_panel": {"version": 1, "panel_type": "text", "caps": domain.descriptor(),
            "fingerprint": domain.fingerprint, "state": observed.descriptor(), "available": observed.available,
            "eligible_actions": observed.eligible(domain)}}
