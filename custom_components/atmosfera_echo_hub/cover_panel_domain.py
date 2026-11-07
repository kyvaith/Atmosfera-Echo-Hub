"""Negotiated cover detail metadata; the existing Cover owner remains in charge."""

from collections.abc import Mapping
from dataclasses import dataclass

from .cover_domain import CoverDomain, CoverDomainError, CoverObservation, OPERATIONS

PANEL_FEATURES = {"set_position": 4, "open_tilt": 16, "close_tilt": 32,
                  "stop_tilt": 64, "set_tilt_position": 128}
PANEL_OPERATIONS = frozenset(PANEL_FEATURES) | OPERATIONS
NUMERIC_OPERATIONS = frozenset(("set_position", "set_tilt_position"))
STOP_OPERATIONS = frozenset(("stop", "stop_tilt"))
MOTION_FAMILIES = {"stop": frozenset(("open", "close", "set_position")),
                   "stop_tilt": frozenset(("open_tilt", "close_tilt", "set_tilt_position"))}
DEVICE_CLASSES = frozenset(("unknown", "awning", "blind", "curtain", "damper", "door",
                            "garage", "gate", "shade", "shutter", "window"))
SERVICES = {"open": "open_cover", "close": "close_cover", "stop": "stop_cover",
            "set_position": "set_cover_position", "open_tilt": "open_cover_tilt",
            "close_tilt": "close_cover_tilt", "stop_tilt": "stop_cover_tilt",
            "set_tilt_position": "set_cover_tilt_position"}


@dataclass(frozen=True)
class CoverPanelDomain(CoverDomain):
    set_position: bool = False
    open_tilt: bool = False
    close_tilt: bool = False
    stop_tilt: bool = False
    set_tilt_position: bool = False
    device_class: str = "unknown"

    def __post_init__(self):
        values = [getattr(self, name) for name in PANEL_OPERATIONS]
        if any(type(value) is not bool for value in values) or not any(values):
            raise CoverDomainError("panel_capabilities")
        if type(self.device_class) is not str or self.device_class not in DEVICE_CLASSES:
            raise CoverDomainError("device_class")

    @classmethod
    def from_ha(cls, attributes, services):
        if not isinstance(attributes, Mapping) or not isinstance(services, Mapping):
            raise CoverDomainError("metadata")
        features = attributes.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or not 0 <= features <= 2**31 - 1:
            raise CoverDomainError("features")
        device_class = attributes.get("device_class")
        if not isinstance(device_class, str) or device_class not in DEVICE_CLASSES:
            device_class = "unknown"
        bits = {"open": 1, "close": 2, "stop": 8, **PANEL_FEATURES}
        return cls(**{op: bool(features & bit) and services.get(SERVICES[op]) is True for op, bit in bits.items()},
                   device_class=str(device_class))

    @classmethod
    def from_panel_descriptor(cls, primary, panel):
        if (type(primary) is not dict or set(primary) != OPERATIONS
                or type(panel) is not dict or set(panel) != {"version", "device_class", "tilt_position", "caps"}
                or type(panel["version"]) is not int or panel["version"] != 1
                or type(panel["caps"]) is not dict or set(panel["caps"]) != set(PANEL_FEATURES)):
            raise CoverDomainError("panel_fields")
        tilt = panel["tilt_position"]
        if tilt is not None and (type(tilt) is not int or not 0 <= tilt <= 100):
            raise CoverDomainError("tilt_position")
        return cls(**primary, **panel["caps"], device_class=panel["device_class"])

    def panel_descriptor(self, tilt_position):
        return {"version": 1, "device_class": self.device_class, "tilt_position": tilt_position,
                "caps": {name: getattr(self, name) for name in PANEL_FEATURES}}

    def supports(self, operation):
        if operation not in PANEL_OPERATIONS:
            raise CoverDomainError("operation")
        return getattr(self, operation)

    def service_action(self, operation, target=None):
        if not self.supports(operation):
            raise CoverDomainError("unsupported")
        if operation in NUMERIC_OPERATIONS:
            if type(target) is not int or not 0 <= target <= 100:
                raise CoverDomainError("target_index")
            return SERVICES[operation], {"position" if operation == "set_position" else "tilt_position": target}
        if target is not None:
            raise CoverDomainError("unexpected_target")
        return SERVICES[operation], {}


@dataclass(frozen=True)
class CoverPanelObservation(CoverObservation):
    tilt_position: int | None = None

    @classmethod
    def from_ha(cls, state, attributes):
        primary = CoverObservation.from_ha(state, attributes)
        raw = attributes.get("current_tilt_position")
        tilt = (int(raw) if primary.available and type(raw) in (int, float)
                and 0 <= raw <= 100 and int(raw) == raw else None)
        return cls(primary.state, primary.position, tilt)

    def numeric_known(self, operation):
        return self.available and (self.position if operation == "set_position" else self.tilt_position) is not None

    def target_matches(self, operation, target=None):
        if not self.available:
            return False
        if operation == "set_position":
            return self.position == target
        if operation == "set_tilt_position":
            return self.tilt_position == target
        if operation == "open_tilt":
            return self.tilt_position == 100
        if operation == "close_tilt":
            return self.tilt_position == 0
        # Standard HA has no independent tilt motion/stopped observation.
        # A stationary primary state or unchanged tilt never proves StopTilt.
        return False
