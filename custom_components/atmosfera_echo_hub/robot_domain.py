"""Bounded robot metadata and existing product admission; no services or I/O."""

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json

from homeassistant.helpers.area_registry import async_get as async_get_area_registry
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .choice_domain import ChoiceDomain, ChoiceDomainError, choice_domain
from . import mower_actions, vacuum_actions
from .vacuum_areas import area_command_allowed, has_area_capability, mapped_area_ids

ROBOT_ACTION = {"kind": "control", "control": "robot"}
BITS = {"start": 1, "pause": 2, "stop": 4, "dock": 8, "locate": 16, "spot": 32}
OPERATIONS = frozenset(BITS) | {"speed", "area"}
INDEXED_OPERATIONS = frozenset(("speed", "area"))
COMPLETED_OPERATIONS = frozenset(("locate", "area"))
SERVICES = {
    "vacuum": {"start": "start", "pause": "pause", "stop": "stop", "dock": "return_to_base",
               "locate": "locate", "spot": "clean_spot", "speed": "set_fan_speed", "area": "clean_area"},
    "lawn_mower": {"start": "start_mowing", "pause": "pause", "dock": "dock"},
}
ACTIVITIES = {"vacuum": vacuum_actions.ACTIVITIES, "lawn_mower": mower_actions.ACTIVITIES}
INTERRUPTS = {"vacuum": {"pause", "stop"}, "lawn_mower": {"pause"}}
MOTION_FAMILIES = {"vacuum": frozenset(("start", "spot", "dock", "area")),
                   "lawn_mower": frozenset(("start", "dock"))}


class RobotDomainError(ValueError):
    """Unsupported or malformed bounded robot metadata."""


def _options(values):
    if not values:
        return ()
    return ChoiceDomain.from_options(values).options


@dataclass(frozen=True)
class RobotDomain:
    robot_type: str
    actions: int
    speeds: tuple[str, ...] = ()
    areas: tuple[str, ...] = ()
    area_targets: tuple[str, ...] = ()
    area_mapping: tuple = ()
    area_reason: str | None = "unsupported"

    def __post_init__(self):
        if (self.robot_type not in SERVICES or type(self.actions) is not int
                or not 0 <= self.actions <= 63
                or (self.robot_type == "lawn_mower" and (self.actions & ~11 or self.speeds or self.areas))
                or not (self.actions or self.speeds or self.areas)):
            raise RobotDomainError("capabilities")
        try:
            if _options(list(self.speeds)) != self.speeds or _options(list(self.areas)) != self.areas:
                raise RobotDomainError("catalogue")
        except ChoiceDomainError as error:
            raise RobotDomainError("catalogue") from error

    @classmethod
    def from_descriptor(cls, robot_type, caps):
        if (type(caps) is not dict or set(caps) != {"actions", "speeds", "areas"}
                or type(caps["speeds"]) is not list or type(caps["areas"]) is not list):
            raise RobotDomainError("fields")
        return cls(robot_type, caps["actions"], tuple(caps["speeds"]), tuple(caps["areas"]))

    @classmethod
    def from_ha(cls, hass, state):
        robot_type = state.entity_id.partition(".")[0]
        if robot_type not in SERVICES or not isinstance(state.attributes, Mapping):
            raise RobotDomainError("entity")
        policy = vacuum_actions if robot_type == "vacuum" else mower_actions
        supported = policy.supported_operations(state.attributes)
        actions = sum(bit for op, bit in BITS.items() if SERVICES[robot_type].get(op) in supported
                      and hass.services.has_service(robot_type, SERVICES[robot_type][op]))
        speeds, areas, targets, mapping, reason = (), (), (), (), "unsupported"
        if robot_type == "vacuum":
            if hass.services.has_service("vacuum", "set_fan_speed"):
                try:
                    speeds = choice_domain(state.entity_id, state.attributes, "fan_speed", hass=hass).options
                except ChoiceDomainError:
                    pass
            if has_area_capability(state.attributes) and hass.services.has_service("vacuum", "clean_area"):
                entry = async_get_entity_registry(hass).async_get(state.entity_id)
                options = getattr(entry, "options", None)
                ids = mapped_area_ids(options)
                reason = "no_mapped_areas"
                if ids:
                    registry = async_get_area_registry(hass)
                    rows = [(area_id, registry.async_get_area(area_id)) for area_id in ids]
                    # The complete real mapping is selection metadata, even when
                    # its display facet cannot fit the bounded native catalogue.
                    raw = options["vacuum"]["area_mapping"]
                    mapping = tuple((area_id, tuple(raw[area_id]), getattr(area, "name", None)) for area_id, area in rows)
                    if len(rows) > 8:
                        reason = "too_many_areas"
                    elif any(area is None for _, area in rows):
                        reason = "no_mapped_areas"
                    else:
                        try:
                            areas = ChoiceDomain.from_options([area.name for _, area in rows]).options
                            targets = tuple(area_id for area_id, _ in rows)
                            reason = None
                        except ChoiceDomainError:
                            reason = "area_labels_unsupported"
        return cls(robot_type, actions, speeds, areas, targets, mapping, reason)

    def descriptor(self):
        return {"actions": self.actions, "speeds": list(self.speeds), "areas": list(self.areas)}

    @property
    def fingerprint(self):
        source = (self.robot_type, self.actions, self.speeds, self.areas, self.area_targets, self.area_mapping)
        return hashlib.sha256(json.dumps(source, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()

    def service_action(self, operation, target=None):
        if operation in BITS:
            if target is not None or not self.actions & BITS[operation]:
                raise RobotDomainError("unsupported")
            return self.robot_type, SERVICES[self.robot_type][operation], {}
        options = self.speeds if operation == "speed" else self.area_targets if operation == "area" else ()
        if type(target) is not int or not 0 <= target < len(options):
            raise RobotDomainError("target_index")
        return self.robot_type, SERVICES[self.robot_type][operation], {
            "fan_speed" if operation == "speed" else "cleaning_area_id": options[target]
        }


@dataclass(frozen=True)
class RobotObservation:
    activity: str
    speed_index: int | None
    battery_percent: int | None
    eligible_actions: int
    area_enabled: bool

    @property
    def available(self):
        return self.activity != "unknown"

    @property
    def command_state(self):
        return self.activity, self.speed_index, self.eligible_actions, self.area_enabled

    @classmethod
    def from_ha(cls, state, domain):
        activity = str(state.state) if state.state in ACTIVITIES[domain.robot_type] else "unknown"
        if activity == "unknown":
            return cls(activity, None, None, 0, False)
        policy = vacuum_actions if domain.robot_type == "vacuum" else mower_actions
        eligible = sum(bit for op, bit in BITS.items() if domain.actions & bit
                       and policy.command_allowed(state.state, state.attributes, SERVICES[domain.robot_type][op]))
        value = state.attributes.get("fan_speed")
        index = domain.speeds.index(value) if isinstance(value, str) and value in domain.speeds else None
        battery = state.attributes.get("battery_level")
        battery = battery if type(battery) is int and 0 <= battery <= 100 else None
        return cls(activity, index, battery, eligible,
                   bool(domain.areas) and area_command_allowed(state.state, state.attributes))

    def descriptor(self):
        return {"activity": self.activity, "available": self.available, "speed_index": self.speed_index,
                "battery_percent": self.battery_percent, "eligible_actions": self.eligible_actions,
                "area_enabled": self.area_enabled}

    def can_command(self, operation):
        if not self.available:
            return False
        if operation in BITS:
            return bool(self.eligible_actions & BITS[operation])
        return self.speed_index is not None if operation == "speed" else self.area_enabled if operation == "area" else False

    def matches(self, domain, operation, target=None):
        if not self.available or operation in COMPLETED_OPERATIONS:
            return False
        if operation == "speed":
            return self.speed_index is not None and self.speed_index == target
        expected = {"start": {"cleaning" if domain.robot_type == "vacuum" else "mowing"},
                    "spot": {"cleaning"}, "pause": {"paused"}, "stop": {"idle"}, "dock": {"returning", "docked"}}
        return self.activity in expected.get(operation, ())
