"""Bounded humidifier observations and exact HA numeric domain, without I/O."""

from collections.abc import Mapping
from dataclasses import dataclass

from .choice_domain import ChoiceDomain, ChoiceDomainError
from .number_domain import humidity_domain
from .numeric_domain import NumericDomain, NumericDomainError, SCALE, _micro, _text

OPERATIONS = frozenset(("power", "humidity", "mode"))
DEVICE_CLASSES = ("unknown", "humidifier", "dehumidifier")
HUMIDIFIER_ACTION = {"kind": "control", "control": "humidifier"}


class HumidifierDomainError(ValueError):
    """Invalid advertised domain or requested operation."""


def measurement_text(value):
    """Unknown remains empty; retain exact measured fractions up to six places."""
    try:
        micro = _micro(value)
    except NumericDomainError:
        return ""
    return _text(micro) if 0 <= micro <= 100 * SCALE else ""


@dataclass(frozen=True)
class HumidifierDomain:
    turn_on: bool
    turn_off: bool
    humidity: NumericDomain | None = None
    modes: tuple[str, ...] = ()
    device_class: str = "unknown"

    @classmethod
    def from_descriptor(cls, caps, numeric, device_class):
        if (type(caps) is not dict or set(caps) != {"turn_on", "turn_off", "modes"}
                or any(type(caps[key]) is not bool for key in ("turn_on", "turn_off"))
                or type(caps["modes"]) is not list or device_class not in DEVICE_CLASSES):
            raise HumidifierDomainError("humidifier_caps")
        try:
            modes = ChoiceDomain.from_options(caps["modes"]).options if caps["modes"] else ()
            domain = NumericDomain.from_descriptor(numeric) if numeric is not None else None
            if domain is not None and (domain.unit != "%" or not 0 <= domain.minimum_micro <= domain.maximum_micro <= 100 * SCALE
                    or any(value % SCALE for value in (domain.minimum_micro, domain.maximum_micro, domain.step_micro))):
                raise HumidifierDomainError("humidity_domain")
        except (ChoiceDomainError, NumericDomainError) as error:
            raise HumidifierDomainError("humidifier_domain") from error
        result = cls(caps["turn_on"], caps["turn_off"], domain, modes, device_class)
        if not any((result.turn_on, result.turn_off, result.humidity, result.modes)):
            raise HumidifierDomainError("humidifier_unsupported")
        return result

    @classmethod
    def from_ha(cls, hass, state):
        if not state.entity_id.startswith("humidifier.") or not isinstance(state.attributes, Mapping):
            raise HumidifierDomainError("humidifier_entity")
        attrs = state.attributes
        features = attrs.get("supported_features")
        if not isinstance(features, int) or isinstance(features, bool) or not 0 <= features <= 2**53 - 1:
            raise HumidifierDomainError("humidifier_features")
        available = lambda service: hass.services.has_service("humidifier", service)
        numeric, modes = None, []
        if available("set_humidity"):
            try:
                numeric = humidity_domain(attrs).descriptor()
            except NumericDomainError:
                pass  # Bad optional limits must not remove power or mode.
        if features & 1 and available("set_mode"):
            try:
                modes = list(ChoiceDomain.from_options(attrs.get("available_modes")).options)
            except ChoiceDomainError:
                pass
        device_class = attrs.get("device_class")
        if device_class not in DEVICE_CLASSES:
            device_class = "unknown"
        return cls.from_descriptor({"turn_on": available("turn_on"), "turn_off": available("turn_off"),
                                    "modes": modes}, numeric, str(device_class))

    def descriptor(self):
        return {"turn_on": self.turn_on, "turn_off": self.turn_off, "modes": list(self.modes)}

    def numeric_descriptor(self):
        return self.humidity.descriptor() if self.humidity is not None else None

    def service_action(self, operation, target):
        if type(target) is not int:
            raise HumidifierDomainError("humidifier_target")
        if operation == "power" and target in (0, 1) and (self.turn_on if target else self.turn_off):
            return ("turn_on" if target else "turn_off"), {}
        if operation == "humidity" and self.humidity is not None:
            try:
                return "set_humidity", {"humidity": self.humidity.service_value(target, current=self.humidity)}
            except NumericDomainError as error:
                raise HumidifierDomainError("humidity_target") from error
        if operation == "mode" and 0 <= target < len(self.modes):
            return "set_mode", {"mode": self.modes[target]}
        raise HumidifierDomainError("humidifier_operation")


@dataclass(frozen=True)
class HumidifierObservation:
    state: str = "unknown"
    humidity_index: int | None = None
    humidity_text: str = "--"
    current_humidity: str = ""
    mode_index: int | None = None

    @property
    def available(self):
        return self.state in ("on", "off")

    @property
    def command_state(self):
        # Measurement-only changes must not cancel a target being dragged.
        return self.state, self.humidity_index, self.humidity_text, self.mode_index

    @classmethod
    def from_ha(cls, state, domain):
        if state.state not in ("on", "off"):
            return cls()
        attrs = state.attributes
        target = attrs.get("humidity")
        index = domain.humidity.observed_index(target) if domain.humidity and type(target) in (int, float) else None
        text = str(domain.humidity.value_at(index)) if index is not None else "--"
        mode = attrs.get("mode")
        mode_index = domain.modes.index(mode) if type(mode) is str and mode in domain.modes else None
        current = attrs.get("current_humidity")
        return cls(str(state.state), index, text, measurement_text(current) if type(current) in (int, float) else "", mode_index)

    def descriptor(self):
        return {"humidifier_state": self.state, "available": self.available,
                "humidity_index": self.humidity_index, "humidity_text": self.humidity_text,
                "current_humidity": self.current_humidity, "mode_index": self.mode_index}

    def can_command(self, domain, operation):
        return self.available and {"power": True, "humidity": self.humidity_index is not None,
                                   "mode": self.mode_index is not None}.get(operation, False)

    def matches(self, domain, operation, target):
        if not self.can_command(domain, operation):
            return False
        if operation == "power":
            return (self.state == "on") == bool(target)
        return {"humidity": self.humidity_index, "mode": self.mode_index}.get(operation) == target
