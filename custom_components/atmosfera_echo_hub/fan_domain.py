"""Bounded, explicit fan capabilities and observations; no service dispatch."""

from collections.abc import Mapping
from dataclasses import dataclass

from .choice_domain import ChoiceDomain, ChoiceDomainError, fan_speed_options

OPERATIONS = frozenset(("power", "speed", "preset", "oscillation", "direction"))
DIRECTIONS = ("forward", "reverse")
FAN_ACTION = {"kind": "control", "control": "fan"}


class FanDomainError(ValueError):
    """The advertised fan domain or requested operation is invalid."""


@dataclass(frozen=True)
class FanDomain:
    turn_on: bool
    turn_off: bool
    oscillate: bool
    direction: bool
    speeds: tuple[int, ...] = ()
    presets: tuple[str, ...] = ()

    @classmethod
    def from_descriptor(cls, value):
        if type(value) is not dict or set(value) != {"turn_on", "turn_off", "oscillate", "direction", "speeds", "presets"}:
            raise FanDomainError("fan_caps")
        if any(type(value[key]) is not bool for key in ("turn_on", "turn_off", "oscillate", "direction")):
            raise FanDomainError("fan_caps")
        speeds, presets = value["speeds"], value["presets"]
        if (type(speeds) is not list or type(presets) is not list
                or (speeds and (not 2 <= len(speeds) <= 8 or speeds[0] != 0 or speeds[-1] != 100
                    or any(type(item) is not int or not 0 <= item <= 100 for item in speeds)
                    or any(left >= right for left, right in zip(speeds, speeds[1:]))))):
            raise FanDomainError("fan_speeds")
        try:
            options = ChoiceDomain.from_options(presets).options if presets else ()
        except ChoiceDomainError as error:
            raise FanDomainError("fan_presets") from error
        result = cls(value["turn_on"], value["turn_off"], value["oscillate"], value["direction"], tuple(speeds), options)
        if not any((result.turn_on, result.turn_off, result.oscillate, result.direction, result.speeds, result.presets)):
            raise FanDomainError("fan_unsupported")
        return result

    @classmethod
    def from_ha(cls, hass, state):
        if not state.entity_id.startswith("fan.") or not isinstance(state.attributes, Mapping):
            raise FanDomainError("fan_entity")
        attrs = state.attributes
        features = attrs.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or not 0 <= features <= 2**53 - 1:
            raise FanDomainError("fan_features")
        def supported(bit, service):
            return bool(features & bit and hass.services.has_service("fan", service))
        speeds, presets = [], []
        if supported(1, "set_percentage"):
            try:
                speeds = [int(value) for value in fan_speed_options(hass, state.entity_id, attrs)]
            except ChoiceDomainError:
                pass  # An unsupported speed catalogue does not disable power.
        # Core accepts either SET_SPEED or PRESET_MODE for this service.
        if supported(1 | 8, "set_preset_mode"):
            try:
                presets = list(ChoiceDomain.from_options(attrs.get("preset_modes")).options)
            except ChoiceDomainError:
                pass
        return cls.from_descriptor({
            "turn_on": supported(32, "turn_on"), "turn_off": supported(16, "turn_off"),
            "oscillate": supported(2, "oscillate"), "direction": supported(4, "set_direction"),
            "speeds": speeds, "presets": presets,
        })

    def descriptor(self):
        return {"turn_on": self.turn_on, "turn_off": self.turn_off, "oscillate": self.oscillate,
                "direction": self.direction, "speeds": list(self.speeds), "presets": list(self.presets)}

    def service_action(self, operation, target):
        if type(target) is not int:
            raise FanDomainError("fan_target")
        if operation == "power" and target in (0, 1) and (self.turn_on if target else self.turn_off):
            return ("turn_on" if target else "turn_off"), {}
        if operation == "speed" and 0 <= target < len(self.speeds):
            return "set_percentage", {"percentage": self.speeds[target]}
        if operation == "preset" and 0 <= target < len(self.presets):
            return "set_preset_mode", {"preset_mode": self.presets[target]}
        if operation == "oscillation" and self.oscillate and target in (0, 1):
            return "oscillate", {"oscillating": bool(target)}
        if operation == "direction" and self.direction and target in (0, 1):
            return "set_direction", {"direction": DIRECTIONS[target]}
        raise FanDomainError("fan_operation")


@dataclass(frozen=True)
class FanObservation:
    state: str = "unknown"
    percentage: int | None = None
    preset_index: int | None = None
    preset_known: bool = False
    oscillating: bool | None = None
    direction: str | None = None

    @property
    def available(self):
        return self.state in ("on", "off")

    @classmethod
    def from_ha(cls, state, domain):
        if state.state not in ("on", "off"):
            return cls()
        attrs = state.attributes
        percentage = attrs.get("percentage")
        if type(percentage) is not int or not 0 <= percentage <= 100:
            percentage = None
        preset = attrs.get("preset_mode")
        preset_known = bool(domain.presets and "preset_mode" in attrs
                            and (preset is None or type(preset) is str and preset in domain.presets))
        preset_index = domain.presets.index(preset) if preset_known and preset is not None else None
        oscillating = attrs.get("oscillating") if domain.oscillate else None
        if type(oscillating) is not bool:
            oscillating = None
        direction = attrs.get("direction") if domain.direction else None
        if type(direction) is not str or direction not in DIRECTIONS:
            direction = None
        return cls(str(state.state), percentage, preset_index, preset_known, oscillating, direction)

    def descriptor(self):
        return {"fan_state": self.state, "available": self.available, "percentage": self.percentage,
                "preset_index": self.preset_index, "preset_known": self.preset_known,
                "oscillating": self.oscillating, "direction": self.direction}

    def can_command(self, domain, operation):
        if not self.available:
            return False
        # An active named preset legitimately has no percentage. The caller
        # still supplies an absolute catalogue target, never a relative step
        # or an inferred current speed. Unknown/manual-without-speed stays off.
        speed_source = self.percentage is not None or (self.preset_known and self.preset_index is not None)
        return {"power": True, "speed": bool(domain.speeds) and speed_source,
                "preset": self.preset_known, "oscillation": self.oscillating is not None,
                "direction": self.direction is not None}.get(operation, False)

    def matches(self, domain, operation, target):
        if not self.can_command(domain, operation):
            return False
        if operation == "power":
            return (self.state == "on") == bool(target)
        if operation == "speed":
            return self.percentage == domain.speeds[target]
        if operation == "preset":
            return self.preset_index == target
        if operation == "oscillation":
            return self.oscillating is bool(target)
        if operation == "direction":
            return self.direction == DIRECTIONS[target]
        return False
