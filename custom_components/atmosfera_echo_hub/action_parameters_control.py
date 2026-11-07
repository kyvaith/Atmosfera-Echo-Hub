"""One required Boolean draft over the existing Action owner and service fence."""

from .action_parameters_domain import ACTION, ActionParametersDomain, ActionParametersObservation
from .action_panel_domain import ActionPanelError
from .control_session import MAX_SEQUENCE, ProtocolError, ServiceDispatch
from .layout import LayoutError, validate_action


class ActionParametersPolicy:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._action_parameters_channel = None

    def prepare_bind(self, *args, **kwargs):
        self._action_parameters_channel = None
        return super().prepare_bind(*args, **kwargs)

    @property
    def action_parameters_version(self):
        return int(self.mode == "entity" and self.channel_ready
                   and self._action_parameters_channel == self.channel
                   and {"name": "action", "version": 2} in self.panel_extra_profiles)

    def accept_action_parameters_features(self, channel):
        if (channel != self.channel or not self.channel_ready or self.mode != "entity"
                or {"name": "action", "version": 2} not in self.panel_extra_profiles
                or self._selection is not None or self._opening is not None
                or self._service_task is not None and not self._service_task.done()
                or self._authorization_task is not None and not self._authorization_task.done()):
            raise ProtocolError("unsupported")
        self._action_parameters_channel = channel

    def accept_extra_features(self, *args, **kwargs):
        result = super().accept_extra_features(*args, **kwargs)
        self._action_parameters_channel = None
        return result

    def _panel_domain(self, state, card):
        if card.get("action") != ACTION:
            return super()._panel_domain(state, card)
        if self.action_parameters_version != 1:
            raise ProtocolError("unsupported")
        try:
            return ActionParametersDomain.from_ha(self.hass, state, card["action"])
        except (ActionPanelError, AttributeError):
            raise ProtocolError("unsupported") from None

    def _entity_binding(self, card):
        if card.get("action") != ACTION:
            return super()._entity_binding(card)
        if card.get("type") not in {"entity", "action"}:
            raise ProtocolError("unsupported")
        try:
            validate_action(card["action"], card.get("entity_id", ""), layout_version=3)
        except LayoutError:
            raise ProtocolError("unsupported") from None
        state = self.hass.states.get(card["entity_id"])
        if state is None:
            raise ProtocolError("entity_unavailable")
        return state, {"panel_domain": self._panel_domain(state, card)}

    def _observe_panel(self, selected, state, domain):
        if not isinstance(domain, ActionParametersDomain):
            return super()._observe_panel(selected, state, domain)
        observed = ActionParametersObservation.from_ha(self.hass, state, domain)
        previous = selected.domain_state
        generation = previous[2] if previous else 1
        if previous and previous[0] != domain:
            raise ProtocolError("capabilities_changed")
        if previous and previous[1].command_state != observed.command_state:
            if generation >= MAX_SEQUENCE:
                raise ProtocolError("expired")
            generation += 1
        selected.domain_state = domain, observed, generation
        return selected.domain_state

    def _prepare_command(self, selected, message):
        domain = selected.caps.get("panel_domain")
        marked = "action_parameters_version" in message or "parameter_value" in message
        if not isinstance(domain, ActionParametersDomain):
            if marked:
                raise ProtocolError("unsupported")
            return super()._prepare_command(selected, message)
        state, _, caps = self._valid_selection(selected)
        domain, observed, generation = self._observe_panel(selected, state, caps["panel_domain"])
        operation = message.get("op")
        if (type(message.get("action_version")) is not int or message["action_version"] != 1
                or operation not in {"run", "stop"}
                or operation == "run" and (not marked or type(message.get("action_parameters_version")) is not int
                    or message["action_parameters_version"] != 1 or type(message.get("parameter_value")) is not bool)
                or operation == "stop" and marked):
            raise ProtocolError("unsupported")
        target = message["parameter_value"] if operation == "run" else None
        if message["expected_state_generation"] != generation or not observed.can_command(domain, operation, target):
            raise ProtocolError("stale_state")
        try:
            domain.service_action(selected.entity_id, operation, target)
        except ActionPanelError:
            raise ProtocolError("unsupported") from None
        return domain, observed, generation, operation, target

    @staticmethod
    def _parameters_run(selected, record):
        return (isinstance(selected.caps.get("panel_domain"), ActionParametersDomain)
                and record.prepared is not None and record.prepared[3] == "run")

    def _command_dispatch(self, selected, record, state, caps):
        if not self._parameters_run(selected, record):
            return super()._command_dispatch(selected, record, state, caps)
        domain, _, _, operation, target = record.prepared
        return ServiceDispatch(*domain.service_action(selected.entity_id, operation, target))

    async def _run_dispatch(self, selected, record, dispatch, context):
        if not self._parameters_run(selected, record):
            return await super()._run_dispatch(selected, record, dispatch, context)
        # create_task has yielded since the outer check. Repeat the actual
        # incarnation and semantic fence in this job, then hand off without await.
        if not self._record_current(selected, record):
            raise ProtocolError("selection_changed")
        if self._principal(context) != selected.principal:
            raise ProtocolError("unauthorized")
        state, _, caps = self._valid_selection(selected)
        self._validate_prepared(selected, record, state, caps)
        expected = self._command_dispatch(selected, record, state, caps)
        if not isinstance(dispatch, ServiceDispatch) or dispatch != expected:
            raise ProtocolError("capabilities_changed")
        # No generic entity_id injection: here every data key is a script variable.
        return await self.hass.services.async_call(dispatch.domain, dispatch.operation,
            dispatch.data, blocking=False, context=context)

    def _service_call_blocking(self, selected, record):
        return False if self._parameters_run(selected, record) else super()._service_call_blocking(selected, record)

    def observe_action_parameters_lifecycle(self, event):
        data = getattr(event, "data", {})
        selected, opening = self._selection, self._opening_panel
        domain = selected.caps.get("panel_domain") if selected is not None else opening[2] if opening else None
        if not isinstance(domain, ActionParametersDomain):
            return None
        entity = selected.entity_id if selected is not None else opening[1]
        kind = getattr(event, "event_type", "")
        binding = domain.binding
        if kind in {"service_registered", "service_removed"}:
            relevant = (data.get("domain") == "script" and
                (data.get("service") == "turn_off" or binding is not None and data.get("service") == binding.unique_id))
        elif kind == "entity_registry_updated":
            changes = data.get("changes", {})
            relevant = data.get("entity_id") == entity or isinstance(changes, dict) and changes.get("entity_id") == entity
        else:
            return None
        if relevant:
            self._opening_panel = None
            return self.revoke_now("capabilities_changed")
        return None
