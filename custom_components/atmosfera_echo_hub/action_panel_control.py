"""Optional Action policy on the existing Panel session and service fence."""

from .action_panel_domain import ActionDomain, ActionObservation, ActionPanelError, MASKS, saved_action
from .control_session import CallbackDispatch, ControlTarget, MAX_SEQUENCE, ProtocolError, TERMINAL
from .layout import LayoutError, validate_action
from .tile_events import is_event_panel


class ActionPanelPolicy:
    # Dispatched is terminal only for the explicitly negotiated Action2 policy.
    _terminal_statuses = TERMINAL | {"service_completed", "service_dispatched"}

    def __init__(self, *args, tile_event_resolver=None, tile_event_dispatch=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._tile_event_resolver = tile_event_resolver
        self._tile_event_dispatch = tile_event_dispatch

    @property
    def tile_event_supported(self):
        return ({"name": "action", "version": 2} in self.panel_extra_profiles
                and {"name": "tile_event", "version": 1} in self.panel_extra_profiles
                and callable(self._tile_event_resolver) and callable(self._tile_event_dispatch))

    def _tile_binding(self, card):
        if not self.tile_event_supported or not is_event_panel(card):
            raise ProtocolError("unsupported")
        binding = self._tile_event_resolver(card["slot"], card["id"], self.read_context().revision)
        if binding is None:
            raise ProtocolError("capabilities_changed")
        return binding

    def _resolved_target(self, state, card, caps):
        if not is_event_panel(card):
            return super()._resolved_target(state, card, caps)
        binding = caps["tile_event_binding"]
        return ControlTarget(binding[0], binding[1])

    def observe_tile_event_binding(self, card_id):
        selected, opening = self._selection, self._opening_panel
        if ((selected is not None and selected.identity["card_id"] == card_id
             and "tile_event_binding" in selected.caps)
                or opening is not None and opening[3]["id"] == card_id and is_event_panel(opening[3])):
            return self.revoke_now("capabilities_changed")
        return None
    @staticmethod
    def _action_panel(card):
        action = card.get("action", {})
        return isinstance(action, dict) and action.get("kind") == "control" and action.get("control") == "panel" and action.get("property") == "action"

    def _panel_domain(self, state, card):
        if is_event_panel(card):
            self._tile_binding(card)
            return ActionDomain("tile_event", 1)
        if not self._action_panel(card):
            return super()._panel_domain(state, card)
        try:
            if {"name": "action", "version": 2} not in self.panel_extra_profiles:
                raise ActionPanelError("profile")
            return ActionDomain.from_ha(self.hass, state, card["action"])
        except ActionPanelError:
            raise ProtocolError("unsupported") from None

    def _entity_binding(self, card):
        if is_event_panel(card):
            binding = self._tile_binding(card)
            state = self.hass.states.get(binding[0])
            if state is None:
                raise ProtocolError("entity_unavailable")
            return state, {"panel_domain": ActionDomain("tile_event", 1), "tile_event_binding": binding}
        if not self._action_panel(card):
            return super()._entity_binding(card)
        entity = card.get("entity_id")
        if (not isinstance(entity, str) or entity.partition(".")[0] not in MASKS
                or card.get("type") not in {"entity", "action"} or not saved_action(card["action"], entity)):
            raise ProtocolError("unsupported")
        try:
            validate_action(card["action"], entity, layout_version=3)
        except LayoutError:
            raise ProtocolError("unsupported") from None
        state = self.hass.states.get(entity)
        if state is None:
            raise ProtocolError("entity_unavailable")
        return state, {"panel_domain": self._panel_domain(state, card)}

    def _observe_panel(self, selected, state, domain):
        if not isinstance(domain, ActionDomain):
            return super()._observe_panel(selected, state, domain)
        observed = ActionObservation.from_ha(self.hass, state, domain)
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
        action = selected.identity.get("control_kind") == "panel" and isinstance(selected.caps.get("panel_domain"), ActionDomain)
        if action != (type(message.get("action_version")) is int and message["action_version"] == 1):
            raise ProtocolError("unsupported")
        if action and selected.caps["panel_domain"].action_type == "tile_event":
            state, _, caps = self._valid_selection(selected)
            domain, observed, generation = self._observe_panel(selected, state, caps["panel_domain"])
            if (message["expected_state_generation"] != generation
                    or not observed.can_command(domain, message["op"])):
                raise ProtocolError("stale_state")
            return domain, observed, generation, message["op"], None
        return super()._prepare_command(selected, message)

    def _command_dispatch(self, selected, record, state, caps):
        domain = caps.get("panel_domain")
        if not isinstance(domain, ActionDomain) or domain.action_type != "tile_event":
            return super()._command_dispatch(selected, record, state, caps)
        identity, binding = selected.identity, caps["tile_event_binding"]
        return CallbackDispatch(lambda context: self._tile_event_dispatch(
            identity["slot"], identity["card_id"], identity["revision"], binding, context))

    def _service_call_blocking(self, selected, record):
        domain = selected.caps.get("panel_domain")
        # Core automation.trigger awaits its entire sequence in blocking mode.
        # Action2 promises only successful public HA dispatch, never completion.
        if (isinstance(domain, ActionDomain) and domain.action_type == "automation"
                and record.prepared[3] == "trigger"):
            return False
        return super()._service_call_blocking(selected, record)

    def _completed_service_status(self, selected, record):
        domain = selected.caps.get("panel_domain")
        if isinstance(domain, ActionDomain) and domain.action_type == "tile_event":
            return "service_dispatched"
        if not self._service_call_blocking(selected, record):
            return "service_dispatched"
        domain = selected.caps.get("panel_domain")
        if isinstance(domain, ActionDomain) and domain.service_only(record.prepared[3]):
            return "service_completed"
        return super()._completed_service_status(selected, record)

    def _command_matches(self, selected, record):
        domain = selected.caps.get("panel_domain")
        if not isinstance(domain, ActionDomain):
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        current, observed, generation = self._observe_panel(selected, state, caps["panel_domain"])
        expected, _, prepared_generation, operation, target = record.prepared
        return (current == expected and not domain.service_only(operation) and record.service_started
                and generation > prepared_generation and observed.matches(operation, target))
