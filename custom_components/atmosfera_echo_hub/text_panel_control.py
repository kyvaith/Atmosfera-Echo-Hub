"""Public text editing uses the existing CONTROL authorization and service fence."""

from .control_session import MAX_SEQUENCE, ProtocolError
from .text_panel_domain import ACTION, TextDomain, TextObservation, TextPanelError


class TextPanelPolicy:
    @staticmethod
    def _text_panel(card):
        return card.get("action") == ACTION

    def _panel_domain(self, state, card):
        if not self._text_panel(card):
            return super()._panel_domain(state, card)
        try:
            if {"name": "text", "version": 1} not in self.panel_extra_profiles:
                raise TextPanelError("profile")
            return TextDomain.from_ha(self.hass, state)
        except TextPanelError:
            raise ProtocolError("unsupported") from None

    def _entity_binding(self, card):
        if not self._text_panel(card):
            return super()._entity_binding(card)
        entity = card.get("entity_id")
        if not isinstance(entity, str) or entity.partition(".")[0] != "input_text" or card.get("type") != "entity":
            raise ProtocolError("unsupported")
        state = self.hass.states.get(entity)
        if state is None:
            raise ProtocolError("entity_unavailable")
        return state, {"panel_domain": self._panel_domain(state, card)}

    def _observe_panel(self, selected, state, domain):
        if not isinstance(domain, TextDomain):
            return super()._observe_panel(selected, state, domain)
        try:
            current = TextDomain.from_ha(self.hass, state)
        except TextPanelError:
            raise ProtocolError("capabilities_changed") from None
        previous = selected.domain_state
        if current != domain or previous and previous[0] != current:
            raise ProtocolError("capabilities_changed")
        observed = TextObservation.from_ha(self.hass, state, current)
        generation = previous[2] if previous else 1
        if previous and previous[1].command_state != observed.command_state:
            if generation >= MAX_SEQUENCE:
                raise ProtocolError("expired")
            generation += 1
        selected.domain_state = current, observed, generation
        return selected.domain_state

    def _prepare_command(self, selected, message):
        domain = selected.caps.get("panel_domain")
        if not isinstance(domain, TextDomain):
            if "text_version" in message:
                raise ProtocolError("unsupported")
            return super()._prepare_command(selected, message)
        if type(message.get("text_version")) is not int or message["text_version"] != 1:
            raise ProtocolError("unsupported")
        state, _, caps = self._valid_selection(selected)
        current, observed, generation = self._observe_panel(selected, state, caps["panel_domain"])
        operation, target = message["op"], message.get("value")
        if message["expected_state_generation"] != generation or not observed.can_command(current, operation, target):
            raise ProtocolError("stale_state")
        return current, observed, generation, operation, target

    def _command_service_action(self, state, caps, record):
        if not isinstance(caps.get("panel_domain"), TextDomain):
            return super()._command_service_action(state, caps, record)
        domain, _, _, operation, target = record.prepared
        if caps["panel_domain"] != domain:
            raise ProtocolError("capabilities_changed")
        try:
            return domain.service_action(state.entity_id, operation, target)
        except TextPanelError:
            raise ProtocolError("unsupported") from None

    def _command_matches(self, selected, record):
        if not isinstance(selected.caps.get("panel_domain"), TextDomain):
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        domain, observed, generation = self._observe_panel(selected, state, caps["panel_domain"])
        expected, _, prepared_generation, operation, target = record.prepared
        return (domain == expected and observed.matches(operation, target)
                and (not record.service_started or generation > prepared_generation))
