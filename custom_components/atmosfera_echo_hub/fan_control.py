"""Dedicated fan policy over the existing single entity-control session."""

from .cards import validate_live_action
from .control_session import CLOSE_REASONS, MAX_SEQUENCE, TERMINAL, ProtocolError
from .fan_domain import FAN_ACTION, FanDomain, FanDomainError, FanObservation
from .text import plain_text


class FanControlPolicy:
    """One fan selection shares the existing authorization and service fence."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._opening_fan = None

    @staticmethod
    def _fan(card):
        return card.get("action") == FAN_ACTION

    def _fan_domain(self, state):
        try:
            return FanDomain.from_ha(self.hass, state)
        except FanDomainError:
            raise ProtocolError("unsupported") from None

    def _entity_binding(self, card):
        if not self._fan(card):
            return super()._entity_binding(card)
        entity = card.get("entity_id")
        if (self.mode != "entity" or "fan" not in self.control_kinds or card.get("type") != "entity"
                or not isinstance(entity, str) or not entity.startswith("fan.")):
            raise ProtocolError("unsupported")
        state = self.hass.states.get(entity)
        if state is None:
            raise ProtocolError("entity_unavailable")
        return state, {"fan_domain": self._fan_domain(state)}

    def _capture_open(self, message, state, card, caps):
        if not self._fan(card):
            return super()._capture_open(message, state, card, caps)
        self._opening_fan = (self._open_generation, card["entity_id"], caps["fan_domain"])
        return self._opening_fan

    def _revalidate_open(self, captured, state, card, caps):
        if not self._fan(card):
            return super()._revalidate_open(captured, state, card, caps)
        if captured is not self._opening_fan or caps["fan_domain"] != captured[2]:
            raise ProtocolError("capabilities_changed")

    def _finish_open(self, captured):
        if captured is not None and captured is self._opening_fan:
            self._opening_fan = None
        return super()._finish_open(captured)

    def _observe_fan(self, selected, state, domain):
        observation = FanObservation.from_ha(state, domain)
        previous = selected.domain_state
        if previous is None:
            selected.domain_state = (domain, observation, 1)
        elif previous[0] != domain:
            raise ProtocolError("capabilities_changed")
        elif previous[1] != observation:
            if previous[2] >= MAX_SEQUENCE:
                raise ProtocolError("expired")
            selected.domain_state = (domain, observation, previous[2] + 1)
        return selected.domain_state

    def observe_state_event(self, event=None):
        data = getattr(event, "data", {})
        entity, state = data.get("entity_id"), data.get("new_state")
        selected, opening = self._selection, self._opening_fan
        selected_fan = selected is not None and selected.identity.get("control_kind") == "fan"
        if not ((selected_fan and entity == selected.entity_id) or (opening and entity == opening[1])):
            return super().observe_state_event(event)
        try:
            if state is None:
                raise ProtocolError("entity_unavailable")
            domain = self._fan_domain(state)
            if opening and entity == opening[1] and domain != opening[2]:
                raise ProtocolError("capabilities_changed")
            if selected_fan and entity == selected.entity_id:
                self._observe_fan(selected, state, domain)
        except ProtocolError as error:
            self._opening_fan = None
            return self.revoke_now("capabilities_changed" if str(error) == "unsupported" else str(error))
        return None

    def _selection_snapshot_fields(self, selected, state, card, caps):
        if selected.identity.get("control_kind") != "fan":
            return super()._selection_snapshot_fields(selected, state, card, caps)
        domain, observed, generation = self._observe_fan(selected, state, caps["fan_domain"])
        title = plain_text(card.get("title") or state.attributes.get("friendly_name") or "Fan", 40)
        title = "".join(c for c in title if c.isprintable() and not 0xD800 <= ord(c) <= 0xDFFF)
        while len(title.encode()) > 160:
            title = title[:-1]
        return {"title": title, **observed.descriptor(), "fan_caps": domain.descriptor(),
                "state_generation": generation}

    def _prepare_command(self, selected, message):
        if selected.identity.get("control_kind") != "fan":
            return super()._prepare_command(selected, message)
        state, _, caps = self._valid_selection(selected)
        domain, observed, generation = self._observe_fan(selected, state, caps["fan_domain"])
        if (message["expected_state_generation"] != generation
                or not observed.can_command(domain, message["op"])):
            raise ProtocolError("stale_state")
        try:
            domain.service_action(message["op"], message["target_index"])
        except FanDomainError:
            raise ProtocolError("unsupported") from None
        return domain, observed, generation, message["op"], message["target_index"]

    def _validate_prepared(self, selected, record, state, caps):
        if selected.identity.get("control_kind") != "fan":
            return super()._validate_prepared(selected, record, state, caps)
        current = self._observe_fan(selected, state, caps["fan_domain"])
        if record.prepared is None or current != record.prepared[:3]:
            raise ProtocolError("stale_state")

    def _command_service_action(self, state, caps, record):
        if record.payload.get("control_kind") != "fan":
            return super()._command_service_action(state, caps, record)
        domain, _, _, operation, target = record.prepared
        if caps["fan_domain"] != domain:
            raise ProtocolError("capabilities_changed")
        try:
            service, data = domain.service_action(operation, target)
            validate_live_action(self.hass, state, {"service": "fan." + service, "data": data})
        except ValueError:
            raise ProtocolError("unsupported") from None
        return "fan", service, data

    def _command_matches(self, selected, record):
        if selected.identity.get("control_kind") != "fan":
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        domain, _, _, operation, target = record.prepared
        return domain == caps["fan_domain"] and FanObservation.from_ha(state, domain).matches(domain, operation, target)

    async def _send(self, value):
        selected = self._selection
        if (value.get("kind") == "result" and value.get("status") in TERMINAL
                and value.get("control_kind") == "fan" and selected is not None
                and all(value.get(key) == selected.identity[key] for key in self._selection_fields)):
            try:
                state, card, _ = self._valid_selection(selected)
                await self._snapshot(selected, "state", state, card)
            except ProtocolError as error:
                if selected is self._selection:
                    await self.async_close(str(error) if str(error) in CLOSE_REASONS else "capabilities_changed")
                return value
            if selected is not self._selection:
                raise ProtocolError("selection_changed")
            value["state_seq"] = selected.state_seq
        return await super()._send(value)
