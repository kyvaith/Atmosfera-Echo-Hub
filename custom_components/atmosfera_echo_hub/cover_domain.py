"""Bounded Cover action policy; no session, transport, task or display state."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

OPERATIONS = frozenset(("open", "stop", "close"))
KNOWN_STATES = frozenset(("open", "opening", "closed", "closing"))
FEATURES = {"open": 1, "close": 2, "stop": 8}


class CoverDomainError(ValueError):
    """Unsupported metadata/state; never infer an actuator command."""


@dataclass(frozen=True)
class CoverObservation:
    state: str
    position: int | None

    @classmethod
    def from_ha(cls, state: Any, attributes: Mapping[str, Any]):
        if not isinstance(state, str) or state not in KNOWN_STATES:
            return cls("unknown", None)
        raw = attributes.get("current_position")
        position = int(raw) if type(raw) in (int, float) and 0 <= raw <= 100 and int(raw) == raw else None
        return cls(state, position)

    @property
    def available(self):
        return self.state in KNOWN_STATES

    @property
    def moving(self):
        return self.state in {"opening", "closing"}

    def already_matches(self, operation):
        if operation not in OPERATIONS:
            raise CoverDomainError("operation")
        if not self.available:
            return False
        if operation == "open":
            return self.state == "opening" or (self.state == "open" and self.position == 100)
        if operation == "close":
            return self.state in {"closed", "closing"}
        if operation == "stop":
            return not self.moving
        raise CoverDomainError("operation")

    def permits(self, operation):
        if operation not in OPERATIONS:
            raise CoverDomainError("operation")
        if not self.available or self.already_matches(operation):
            return False
        return not ((operation == "open" and self.state == "opening")
                    or (operation == "close" and self.state == "closing"))


@dataclass(frozen=True)
class CoverDomain:
    open: bool
    stop: bool
    close: bool

    def __post_init__(self):
        if any(type(value) is not bool for value in (self.open, self.stop, self.close)):
            raise CoverDomainError("capability_type")
        if not (self.open or self.stop or self.close):
            raise CoverDomainError("unsupported")

    @classmethod
    def from_descriptor(cls, value):
        if not isinstance(value, dict) or set(value) != OPERATIONS:
            raise CoverDomainError("capability_fields")
        return cls(**value)

    @classmethod
    def from_ha(cls, attributes: Mapping[str, Any], services: Mapping[str, bool]):
        if not isinstance(attributes, Mapping) or not isinstance(services, Mapping):
            raise CoverDomainError("metadata")
        features = attributes.get("supported_features")
        # HA entity attributes retain CoverEntityFeature (IntFlag) in memory;
        # the REST/WS JSON representation alone looks like a plain integer.
        if not isinstance(features, int) or isinstance(features, bool) or not 0 <= features <= 2**31 - 1:
            raise CoverDomainError("features")
        result = cls(**{op: bool(features & bit) and services.get(op + "_cover") is True
                       for op, bit in FEATURES.items()})
        if not any(result.descriptor().values()):
            raise CoverDomainError("unsupported")
        return result

    def descriptor(self):
        return {"open": self.open, "stop": self.stop, "close": self.close}

    def supports(self, operation):
        if operation not in OPERATIONS:
            raise CoverDomainError("operation")
        return self.descriptor()[operation]

    def allows(self, operation, observed: CoverObservation):
        return self.supports(operation) and observed.permits(operation)
