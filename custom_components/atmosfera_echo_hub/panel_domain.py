"""Bounded Timer/Remote/Power metadata and observations; no service dispatch."""

from dataclasses import dataclass
from datetime import datetime, timezone
import re
import time

from .choice_domain import ChoiceDomain, ChoiceDomainError, choice_domain

PANEL_TYPES = ("timer", "remote", "power")
DOMAINS = {"timer": {"timer"}, "remote": {"remote"}, "power": {"switch", "input_boolean"}}
MAX_SECONDS = 2**31 - 1
MIN_UTC, MAX_UTC = 946684800, 4102444799
TIMER_BITS = {"start": 1, "resume": 2, "pause": 4, "cancel": 8, "set_duration": 16}
OPERATIONS = frozenset(TIMER_BITS) | {"power", "activity"}


class PanelDomainError(ValueError):
    """Malformed or unsupported bounded panel."""


def integer(value, low, high):
    return type(value) is int and low <= value <= high


def panel_type(entity_id):
    domain = entity_id.partition(".")[0]
    return next((family for family, domains in DOMAINS.items() if domain in domains), None)


def duration_seconds(value):
    if not isinstance(value, str) or len(value) > 18 or not re.fullmatch(r"[0-9]+:[0-5][0-9]:[0-5][0-9]", value):
        return None
    hours, minutes, seconds = map(int, value.split(":"))
    result = hours * 3600 + minutes * 60 + seconds
    return result if result <= MAX_SECONDS else None


def utc_seconds(value):
    if not isinstance(value, str) or len(value) > 40:
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if stamp.tzinfo is None or stamp.utcoffset() is None or stamp.microsecond:
            return None
        result = int(stamp.astimezone(timezone.utc).timestamp())
        return result if MIN_UTC <= result <= MAX_UTC else None
    except (ValueError, OverflowError, OSError):
        return None


@dataclass(frozen=True)
class PanelDomain:
    family: str
    turn_on: bool = False
    turn_off: bool = False
    activities: tuple[str, ...] = ()
    device_class: str = "unknown"
    start: bool = False
    pause: bool = False
    cancel: bool = False
    initial_duration: int | None = None

    def __post_init__(self):
        if (self.family not in PANEL_TYPES or any(type(v) is not bool for v in
                (self.turn_on, self.turn_off, self.start, self.pause, self.cancel))
                or type(self.activities) is not tuple
                or not isinstance(self.device_class, str) or self.device_class not in {"unknown", "switch", "outlet"}
                or (self.initial_duration is not None and not integer(self.initial_duration, 1, 86400))):
            raise PanelDomainError("capabilities")
        if self.activities:
            try:
                ChoiceDomain(self.activities)
            except ChoiceDomainError as error:
                raise PanelDomainError("activities") from error
        if (self.family == "timer" and (self.turn_on or self.turn_off or self.activities or self.device_class != "unknown")
                or self.family != "timer" and (self.start or self.pause or self.cancel or self.initial_duration is not None)
                or self.family != "power" and self.device_class != "unknown"
                or self.family != "remote" and self.activities
                or self.activities and not self.turn_on
                or not any((self.turn_on, self.turn_off, self.start, self.pause, self.cancel))):
            raise PanelDomainError("capabilities")

    @classmethod
    def from_ha(cls, hass, state, initial_duration=None):
        family = panel_type(state.entity_id)
        domain = state.entity_id.partition(".")[0]
        supported = lambda name: hass.services.has_service(domain, name)
        if family == "timer":
            return cls(family, start=supported("start"), pause=supported("pause"),
                       cancel=supported("cancel"), initial_duration=initial_duration)
        activities = ()
        if family == "remote" and supported("turn_on"):
            try:
                activities = choice_domain(state.entity_id, state.attributes, "activity").options
            except ChoiceDomainError:
                pass
        device_class = state.attributes.get("device_class") if domain == "switch" else None
        return cls(family, turn_on=supported("turn_on"), turn_off=supported("turn_off"),
                   activities=activities, device_class=device_class if isinstance(device_class, str) and device_class in {"switch", "outlet"} else "unknown")

    def descriptor(self):
        if self.family == "timer":
            return {"start": self.start, "pause": self.pause, "cancel": self.cancel,
                    "initial_duration": self.initial_duration}
        result = {"turn_on": self.turn_on, "turn_off": self.turn_off}
        result.update({"activities": list(self.activities)} if self.family == "remote" else {"device_class": self.device_class})
        return result

    @classmethod
    def from_descriptor(cls, family, caps):
        expected = ({"start", "pause", "cancel", "initial_duration"} if family == "timer" else
                    {"turn_on", "turn_off", "activities" if family == "remote" else "device_class"})
        if type(caps) is not dict or set(caps) != expected:
            raise PanelDomainError("fields")
        kwargs = dict(caps)
        if family == "remote":
            if type(kwargs["activities"]) is not list:
                raise PanelDomainError("activities")
            kwargs["activities"] = tuple(kwargs["activities"])
        return cls(family, **kwargs)

    def service_action(self, entity_id, operation, target=None):
        domain = entity_id.partition(".")[0]
        if domain not in DOMAINS[self.family]:
            raise PanelDomainError("entity")
        if self.family == "timer":
            if operation not in TIMER_BITS:
                raise PanelDomainError("operation")
            service = "start" if operation in {"start", "resume", "set_duration"} else operation
            if not getattr(self, service) or (operation != "set_duration" and target is not None):
                raise PanelDomainError("operation")
            if operation == "set_duration":
                if not integer(target, 1, 86400):
                    raise PanelDomainError("duration")
                return domain, service, {"duration": target}
            return domain, service, {}
        if operation == "power" and integer(target, 0, 1) and (self.turn_on if target else self.turn_off):
            return domain, "turn_on" if target else "turn_off", {}
        if operation == "activity" and self.family == "remote" and integer(target, 0, len(self.activities) - 1):
            return domain, "turn_on", {"activity": self.activities[target]}
        raise PanelDomainError("operation")


@dataclass(frozen=True)
class PanelObservation:
    family: str
    power: str = "unknown"
    activity_index: int | None = None
    phase: str = "unknown"
    duration: int | None = None
    remaining: int | None = None
    finishes_at: int | None = None
    sampled_at: int = MIN_UTC

    @property
    def available(self):
        return self.phase != "unknown" if self.family == "timer" else self.power != "unknown"

    @property
    def command_state(self):
        return ((self.phase, self.duration, self.finishes_at, self.remaining if self.phase == "paused" else None)
                if self.family == "timer" else (self.power, self.activity_index))

    def eligible(self, domain):
        if not self.available:
            return 0
        if self.family == "timer":
            return ((1 if domain.start and self.phase == "idle" else 0)
                    | (2 if domain.start and self.phase == "paused" else 0)
                    | (4 if domain.pause and self.phase == "active" else 0)
                    | (8 if domain.cancel and self.phase in {"active", "paused"} else 0)
                    | (16 if domain.start else 0))
        return ((1 if domain.turn_on and self.power == "off" else 0)
                | (2 if domain.turn_off and self.power == "on" else 0)
                | (4 if domain.activities and (self.power == "off" or self.activity_index is not None) else 0))

    def can_command(self, domain, operation, target):
        if not self.available:
            return False
        if self.family == "timer":
            return bool(self.eligible(domain) & TIMER_BITS.get(operation, 0))
        if operation == "power":
            return integer(target, 0, 1) and (domain.turn_on if target else domain.turn_off)
        return operation == "activity" and bool(self.eligible(domain) & 4)

    def matches(self, operation, target):
        if not self.available:
            return False
        if self.family == "timer":
            expected = {"start": "active", "resume": "active", "pause": "paused", "cancel": "idle"}.get(operation)
            return expected is not None and self.phase == expected
        if operation == "power":
            return self.power == ("on" if target else "off")
        return operation == "activity" and self.power == "on" and self.activity_index == target

    def descriptor(self):
        if self.family == "timer":
            return {"phase": self.phase, "duration_seconds": self.duration, "remaining_seconds": self.remaining,
                    "finishes_at_utc_s": self.finishes_at, "sampled_at_utc_s": self.sampled_at}
        return {"power": self.power, **({"activity_index": self.activity_index} if self.family == "remote" else {})}

    @classmethod
    def from_ha(cls, state, domain, *, now=None):
        if domain.family != "timer":
            power = state.state if state.state in {"on", "off"} else "unknown"
            value = state.attributes.get("current_activity")
            index = domain.activities.index(value) if power == "on" and value in domain.activities else None
            return cls(domain.family, power=power, activity_index=index)
        sampled = int(time.time() if now is None else now)
        if not MIN_UTC <= sampled <= MAX_UTC:
            raise PanelDomainError("clock")
        phase = state.state if state.state in {"idle", "active", "paused"} else "unknown"
        if phase == "unknown":
            return cls("timer", sampled_at=sampled)
        duration = duration_seconds(state.attributes.get("duration"))
        deadline = utc_seconds(state.attributes.get("finishes_at")) if phase == "active" else None
        remaining = (max(0, deadline - sampled) if deadline is not None else
                     duration_seconds(state.attributes.get("remaining")) if phase == "paused" else None)
        if remaining is not None and remaining > MAX_SECONDS:
            deadline, remaining = None, None
        return cls("timer", phase=phase, duration=duration, remaining=remaining, finishes_at=deadline, sampled_at=sampled)

    @classmethod
    def from_descriptor(cls, domain, state):
        if type(state) is not dict:
            raise PanelDomainError("state")
        if domain.family == "timer":
            if (set(state) != {"phase", "duration_seconds", "remaining_seconds", "finishes_at_utc_s", "sampled_at_utc_s"}
                    or state["phase"] not in {"idle", "active", "paused", "unknown"}
                    or not integer(state["sampled_at_utc_s"], MIN_UTC, MAX_UTC)
                    or any(value is not None and not integer(value, 0, MAX_SECONDS) for value in
                           (state["duration_seconds"], state["remaining_seconds"]))
                    or (state["finishes_at_utc_s"] is not None and not integer(state["finishes_at_utc_s"], MIN_UTC, MAX_UTC))):
                raise PanelDomainError("state")
            value = cls("timer", phase=state["phase"], duration=state["duration_seconds"], remaining=state["remaining_seconds"],
                        finishes_at=state["finishes_at_utc_s"], sampled_at=state["sampled_at_utc_s"])
            if ((value.phase != "active" and value.finishes_at is not None)
                    or value.phase == "idle" and value.remaining is not None
                    or value.phase == "unknown" and any(v is not None for v in (value.duration, value.remaining, value.finishes_at))
                    or value.phase == "active" and value.remaining != (max(0, value.finishes_at - value.sampled_at) if value.finishes_at is not None else None)):
                raise PanelDomainError("state")
            return value
        expected = {"power", "activity_index"} if domain.family == "remote" else {"power"}
        if set(state) != expected or state["power"] not in {"on", "off", "unknown"}:
            raise PanelDomainError("state")
        index = state.get("activity_index")
        if index is not None and (state["power"] != "on" or not integer(index, 0, len(domain.activities) - 1)):
            raise PanelDomainError("activity")
        return cls(domain.family, power=state["power"], activity_index=index)
