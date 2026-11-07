"""Closed Action:1 semantics; no service dispatch, polling, variables or handoff."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re

from .extra_panel_domain import ha_zone, text_valid

ACTION = {"kind": "control", "control": "panel", "property": "action"}
BITS = {"press": 1, "activate": 2, "run": 4, "stop": 8, "enable": 16, "disable": 32, "trigger": 64}
MASKS = {"button": 1, "input_button": 1, "scene": 2, "script": 12, "automation": 112}
CAP_MASKS = MASKS | {"tile_event": 1}
SERVICES = {"button": {"press": "press"}, "input_button": {"press": "press"},
    "scene": {"activate": "turn_on"}, "script": {"run": "turn_on", "stop": "turn_off"},
    "automation": {"enable": "turn_on", "disable": "turn_off", "trigger": "trigger"}}
PHASES = {"button": {"stateless"}, "input_button": {"stateless"}, "scene": {"stateless"}, "tile_event": {"stateless"},
    "script": {"idle", "running"}, "automation": {"enabled", "disabled"}}
RUN_BLOCKS = {"none", "needs_parameters", "metadata_unavailable", "service_unavailable"}
CAP_KEYS = {"action_type", "operations", "skip_condition", "stop_actions", "run_blocked"}
STATE_KEYS = {"source", "phase", "last_used_status", "last_used_text", "current"}
TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})")


class ActionPanelError(ValueError):
    """Malformed/unsupported Action semantics, not an inferred service ability."""


def saved_action(action, entity_id):
    domain = entity_id.partition(".")[0] if isinstance(entity_id, str) else ""
    if type(action) is not dict or domain not in MASKS:
        return False
    keys = set(ACTION) | ({"skip_condition", "stop_actions"} if domain == "automation" else set())
    return (set(action) == keys and all(action.get(key) == value for key, value in ACTION.items())
            and (domain != "automation" or all(type(action[key]) is bool for key in ("skip_condition", "stop_actions"))))


def script_descriptor_gate(descriptor):
    """No v1 variables/default inference. Oversized metadata is explicitly unavailable."""
    if not isinstance(descriptor, Mapping) or not isinstance(fields := descriptor.get("fields"), Mapping) or len(fields) > 128:
        return "metadata_unavailable"
    required = False
    for name, field in fields.items():
        if (not text_valid(name, 128) or not name or not isinstance(field, Mapping)
                or "required" in field and type(field["required"]) is not bool
                or "fields" in field):
            return "metadata_unavailable"
        required |= field.get("required", False)
    return "needs_parameters" if required else "none"


def script_gate(hass, entity_id):
    """Public HA metadata cache keyed by the real script service identity.

    Core registers script descriptions under registry unique_id, which can differ
    from a renamed entity suffix. Missing/unregistered metadata fails closed; no
    global description loading, private source config or guessed fields are used.
    """
    from homeassistant.helpers.entity_registry import async_get
    from homeassistant.helpers.service import async_get_cached_service_description

    entry = async_get(hass).async_get(entity_id)
    service = getattr(entry, "unique_id", None)
    if (getattr(entry, "platform", None) != "script" or type(service) is not str
            or re.fullmatch(r"[a-z0-9_]{1,128}", service) is None
            or not hass.services.has_service("script", service)):
        return "metadata_unavailable"
    return script_descriptor_gate(async_get_cached_service_description(hass, "script", service))


@dataclass(frozen=True)
class ActionDomain:
    action_type: str
    operations: int
    skip_condition: bool | None = None
    stop_actions: bool | None = None
    run_blocked: str = "none"

    @property
    def family(self):
        return "action"

    def __post_init__(self):
        if (type(self.action_type) is not str or self.action_type not in CAP_MASKS
                or type(self.operations) is not int or not 0 <= self.operations <= 127
                or self.operations & ~CAP_MASKS[self.action_type]
                or type(self.run_blocked) is not str or self.run_blocked not in RUN_BLOCKS):
            raise ActionPanelError("caps")
        if self.action_type == "automation":
            if type(self.skip_condition) is not bool or type(self.stop_actions) is not bool:
                raise ActionPanelError("policy")
        elif self.skip_condition is not None or self.stop_actions is not None:
            raise ActionPanelError("policy")
        if self.action_type == "script":
            if bool(self.operations & BITS["run"]) == (self.run_blocked == "service_unavailable"):
                raise ActionPanelError("run_capability")
        elif self.run_blocked != "none":
            raise ActionPanelError("run_scope")

    @classmethod
    def from_ha(cls, hass, state, action=None):
        subtype = state.entity_id.partition(".")[0]
        if subtype not in MASKS:
            raise ActionPanelError("entity")
        if action is None:
            action = dict(ACTION, **({"skip_condition": False, "stop_actions": False} if subtype == "automation" else {}))
        if not saved_action(action, state.entity_id):
            raise ActionPanelError("saved_action")
        operations = sum(BITS[op] for op, service in SERVICES[subtype].items() if hass.services.has_service(subtype, service))
        blocked = "none"
        if subtype == "script":
            blocked = script_gate(hass, state.entity_id) if operations & BITS["run"] else "service_unavailable"
        return cls(subtype, operations, action.get("skip_condition"), action.get("stop_actions"), blocked)

    def descriptor(self):
        return {key: getattr(self, key) for key in CAP_KEYS}

    @classmethod
    def from_descriptor(cls, caps):
        if type(caps) is not dict or set(caps) != CAP_KEYS:
            raise ActionPanelError("caps")
        return cls(**caps)

    @property
    def fingerprint(self):
        return hashlib.sha256(json.dumps([self.family, self.descriptor()], sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def service_action(self, entity_id, operation, target=None):
        if (self.action_type not in SERVICES or entity_id.partition(".")[0] != self.action_type or operation not in SERVICES[self.action_type]
                or not self.operations & BITS[operation] or target is not None):
            raise ActionPanelError("operation")
        data = {"skip_condition": self.skip_condition} if operation == "trigger" else (
            {"stop_actions": self.stop_actions} if operation == "disable" else {})
        return self.action_type, SERVICES[self.action_type][operation], data

    def service_only(self, operation):
        return operation in {"press", "activate", "run", "trigger"} or operation == "disable" and self.stop_actions is True


def last_used(raw, zone):
    if raw is None or raw in ("", "unknown", "unavailable"):
        return "unknown", ""
    if isinstance(raw, datetime):
        stamp = raw
    elif type(raw) is str:
        if not text_valid(raw, 48):
            if any(0xD800 <= ord(c) <= 0xDFFF for c in raw):
                return "invalid", ""
            return ("too_long" if len(raw.encode("utf8")) > 48 else "invalid"), ""
        # HA timestamps have at most microsecond precision. Reject rather than
        # silently rounding an extended fraction through datetime.fromisoformat.
        if TIMESTAMP.fullmatch(raw) is None:
            return "invalid", ""
        try:
            stamp = datetime.fromisoformat(raw)
        except ValueError:
            return "invalid", ""
    else:
        return "invalid", ""
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        return "invalid", ""
    try:
        value = (stamp.astimezone(zone) if zone is not None else stamp).isoformat()
    except (ValueError, OverflowError):
        return "invalid", ""
    if not text_valid(value, 48):
        return "too_long", ""
    return ("value", value) if TIMESTAMP.fullmatch(value) else ("invalid", "")


@dataclass(frozen=True)
class ActionObservation:
    source: str
    phase: str
    last_used_status: str = "unknown"
    last_used_text: str = ""
    current: int | None = None

    @property
    def available(self):
        return self.source == "known"

    @property
    def command_state(self):
        return self.source, self.phase

    def descriptor(self):
        return {key: getattr(self, key) for key in STATE_KEYS}

    @classmethod
    def from_ha(cls, hass, state, domain):
        raw = state.state
        if raw == "unavailable":
            return cls("unavailable", "unknown")
        momentary = domain.action_type in {"button", "input_button", "scene", "tile_event"}
        if type(raw) is not str or not momentary and raw not in {"on", "off"}:
            return cls("unknown", "unknown")
        phase = "stateless" if momentary else ({"on": "running", "off": "idle"} if domain.action_type == "script"
                                                else {"on": "enabled", "off": "disabled"})[raw]
        status, text = last_used(raw if momentary else state.attributes.get("last_triggered"), ha_zone(hass))
        current = state.attributes.get("current") if not momentary else None
        if type(current) is not int or not 0 <= current <= 65535:
            current = None
        return cls("known", phase, status, text, current)

    @classmethod
    def from_descriptor(cls, domain, fields):
        if type(fields) is not dict or set(fields) != STATE_KEYS:
            raise ActionPanelError("state")
        source, phase, status, text, current = (fields[k] for k in ("source", "phase", "last_used_status", "last_used_text", "current"))
        if (type(source) is not str or source not in {"known", "unknown", "unavailable"}
                or type(phase) is not str or phase not in (PHASES[domain.action_type] if source == "known" else {"unknown"})
                or type(status) is not str or status not in {"value", "unknown", "invalid", "too_long"}
                or not text_valid(text, 48) or (status == "value") != bool(text)
                or current is not None and (type(current) is not int or not 0 <= current <= 65535)
                or domain.action_type in {"button", "input_button", "scene", "tile_event"} and current is not None
                or source != "known" and (status != "unknown" or text or current is not None)):
            raise ActionPanelError("state")
        if status == "value" and last_used(text, None) != ("value", text):
            raise ActionPanelError("timestamp")
        return cls(**fields)

    def eligible(self, domain):
        if not self.available:
            return 0
        if domain.action_type in {"button", "input_button", "scene", "tile_event"}:
            return domain.operations
        if domain.action_type == "script":
            desired = BITS["stop"] if self.phase == "running" else BITS["run"] if domain.run_blocked == "none" else 0
        else:
            desired = BITS["trigger"] | (BITS["enable"] if self.phase == "disabled" else 0)
            if self.phase == "enabled" or domain.stop_actions:
                desired |= BITS["disable"]
        return desired & domain.operations

    def can_command(self, domain, operation, target=None):
        return target is None and operation in BITS and bool(self.eligible(domain) & BITS[operation])

    def matches(self, operation, target=None):
        return self.available and target is None and self.phase == {"stop": "idle", "enable": "enabled", "disable": "disabled"}.get(operation)


def action_metadata(hass, state, language=None):
    if state.entity_id.partition(".")[0] not in MASKS:
        return {}
    try:
        domain = ActionDomain.from_ha(hass, state)
        observed = ActionObservation.from_ha(hass, state, domain)
        return {"action_panel": {"version": 1, "panel_type": "action", "caps": domain.descriptor(),
            "fingerprint": domain.fingerprint, "state": observed.descriptor(), "available": observed.available,
            "eligible_actions": observed.eligible(domain)}}
    except ActionPanelError:
        return {}
