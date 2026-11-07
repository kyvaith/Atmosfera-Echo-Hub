"""Closed, opt-in form for one required Boolean field of a real HA script."""

from collections.abc import Mapping
from dataclasses import dataclass, field
import re

from .action_panel_domain import (ACTION as BASE_ACTION, CAP_KEYS, ActionDomain,
    ActionObservation, ActionPanelError)
from .extra_panel_domain import text_valid

ACTION = dict(BASE_ACTION, parameters="boolean_v1")
PARAM_KEYS = {"parameters_version", "parameter_status", "parameter_label", "parameter_default"}
STATUSES = {"ready", "unsupported", "metadata_unavailable"}
FIELD_KEYS = {"name", "description", "required", "default", "selector", "advanced", "example"}


@dataclass(frozen=True, eq=False)
class ScriptBinding:
    """HA-only incarnation identity; the actual handler is never put on the wire."""

    registry_id: str
    unique_id: str
    service: object = field(repr=False)

    def __eq__(self, other):
        return (isinstance(other, ScriptBinding) and self.registry_id == other.registry_id
                and self.unique_id == other.unique_id and self.service is other.service)


def script_binding(hass, entity_id):
    from homeassistant.helpers.entity_registry import async_get

    entry = async_get(hass).async_get(entity_id)
    unique_id = getattr(entry, "unique_id", None)
    registry_id = getattr(entry, "id", None)
    if (getattr(entry, "platform", None) != "script" or type(unique_id) is not str
            or re.fullmatch(r"[a-z0-9_]{1,128}", unique_id) is None
            or type(registry_id) is not str or not registry_id):
        return None
    # Public shallow copy: retain a reference, not id(service), to detect ABA.
    service = hass.services.async_services_for_domain("script").get(unique_id)
    return ScriptBinding(registry_id, unique_id, service) if service is not None else None


def parameter_fields(descriptor):
    """Do not infer required/default values or truncate unsupported forms."""
    if not isinstance(descriptor, Mapping) or not isinstance(descriptor.get("fields"), Mapping):
        return "metadata_unavailable", "", None, ""
    fields = descriptor["fields"]
    if len(fields) != 1:
        return "unsupported", "", None, ""
    key, value = next(iter(fields.items()))
    if (not isinstance(key, str) or not text_valid(str(key), 128) or not key
            or not isinstance(value, Mapping) or set(value) - FIELD_KEYS
            or value.get("required") is not True or value.get("advanced", False) is not False
            or "default" in value and type(value["default"]) is not bool):
        return "unsupported", "", None, ""
    selector = value.get("selector")
    if not isinstance(selector, Mapping) or set(selector) != {"boolean"}:
        return "unsupported", "", None, ""
    config = selector["boolean"]
    if config is not None and (not isinstance(config, Mapping) or set(config) - {"read_only"}
                               or config.get("read_only", False) is not False):
        return "unsupported", "", None, ""
    label = value.get("name", key)
    if not isinstance(label, str) or not label.strip() or not text_valid(str(label), 96):
        return "unsupported", "", None, ""
    # Description/example are editor-only. They cannot select variables or services.
    if ("description" in value and not isinstance(value["description"], str)
            or "example" in value and not isinstance(value["example"], str) and type(value["example"]) is not bool):
        return "unsupported", "", None, ""
    return "ready", str(label), value.get("default"), str(key)


@dataclass(frozen=True)
class ActionParametersDomain(ActionDomain):
    parameters_version: int = 1
    parameter_status: str = "metadata_unavailable"
    parameter_label: str = ""
    parameter_default: bool | None = None
    field_key: str = field(default="", repr=False)
    binding: ScriptBinding | None = field(default=None, repr=False)

    def __post_init__(self):
        super().__post_init__()
        if (self.action_type != "script" or type(self.parameters_version) is not int
                or self.parameters_version != 1 or type(self.parameter_status) is not str or self.parameter_status not in STATUSES
                or not text_valid(self.parameter_label, 96)
                or self.parameter_default is not None and type(self.parameter_default) is not bool):
            raise ActionPanelError("parameters_caps")
        ready = self.parameter_status == "ready"
        expected = ("service_unavailable" if not self.operations & 4 else
                    {"ready": "none", "unsupported": "needs_parameters",
                     "metadata_unavailable": "metadata_unavailable"}[self.parameter_status])
        if (ready != bool(self.parameter_label.strip()) or not ready and (self.parameter_label != "" or self.parameter_default is not None)
                or self.run_blocked != expected):
            raise ActionPanelError("parameters_caps")

    def descriptor(self):
        return super().descriptor() | {name: getattr(self, name) for name in PARAM_KEYS}

    @classmethod
    def from_descriptor(cls, caps):
        if type(caps) is not dict or set(caps) != CAP_KEYS | PARAM_KEYS:
            raise ActionPanelError("parameters_caps")
        return cls(**caps)

    @classmethod
    def from_ha(cls, hass, state, action=None):
        from homeassistant.helpers.service import async_get_cached_service_description

        if not state.entity_id.startswith("script.") or action is not None and action != ACTION:
            raise ActionPanelError("parameters_action")
        binding = script_binding(hass, state.entity_id)
        status, label, default, key = ("metadata_unavailable", "", None, "")
        if binding is not None:
            status, label, default, key = parameter_fields(
                async_get_cached_service_description(hass, "script", binding.unique_id))
        operations = (4 if binding is not None else 0) | (8 if hass.services.has_service("script", "turn_off") else 0)
        blocked = ("service_unavailable" if not operations & 4 else
                   {"ready": "none", "unsupported": "needs_parameters", "metadata_unavailable": "metadata_unavailable"}[status])
        return cls("script", operations, run_blocked=blocked, parameter_status=status,
                   parameter_label=label, parameter_default=default, field_key=key, binding=binding)

    def service_action(self, entity_id, operation, target=None):
        if operation == "run":
            if (not entity_id.startswith("script.") or type(target) is not bool
                    or self.parameter_status != "ready" or self.binding is None or not self.field_key
                    or not self.operations & 4):
                raise ActionPanelError("parameters_operation")
            return "script", self.binding.unique_id, {self.field_key: target}
        return super().service_action(entity_id, operation, target)


class ActionParametersObservation(ActionObservation):
    def can_command(self, domain, operation, target=None):
        if operation == "run":
            return type(target) is bool and super().can_command(domain, operation, None)
        return operation == "stop" and super().can_command(domain, operation, target)


def action_parameters_metadata(hass, state, language=None):
    if not state.entity_id.startswith("script."):
        return {}
    try:
        domain = ActionParametersDomain.from_ha(hass, state)
        observed = ActionParametersObservation.from_ha(hass, state, domain)
        return {"action_parameters": {"version": 1, "panel_type": "action", "caps": domain.descriptor(),
            "fingerprint": domain.fingerprint, "state": observed.descriptor(), "available": observed.available,
            "eligible_actions": observed.eligible(domain)}}
    except (ActionPanelError, AttributeError):
        return {}
