"""Dedicated robot policy over the existing single entity-control session."""

from .cards import validate_live_action
from .control_session import CLOSE_REASONS, MAX_SEQUENCE, TERMINAL, ProtocolError
from .robot_domain import (ROBOT_ACTION, RobotDomain, RobotDomainError, RobotObservation,
                           COMPLETED_OPERATIONS, INTERRUPTS, MOTION_FAMILIES)
from .text import plain_text


class RobotControlPolicy:
    """One robot selection shares the existing authorization and service fence."""

    _terminal_statuses = TERMINAL | {"service_completed"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._opening_robot = None

    @staticmethod
    def _robot(card):
        return card.get("action") == ROBOT_ACTION

    def _robot_domain(self, state):
        try:
            return RobotDomain.from_ha(self.hass, state)
        except RobotDomainError:
            raise ProtocolError("unsupported") from None

    def _entity_binding(self, card):
        if not self._robot(card):
            return super()._entity_binding(card)
        entity = card.get("entity_id")
        if (self.mode != "entity" or "robot" not in self.control_kinds or card.get("type") != "entity"
                or not isinstance(entity, str) or entity.partition(".")[0] not in {"vacuum", "lawn_mower"}):
            raise ProtocolError("unsupported")
        state = self.hass.states.get(entity)
        if state is None:
            raise ProtocolError("entity_unavailable")
        return state, {"robot_domain": self._robot_domain(state)}

    def _capture_open(self, message, state, card, caps):
        if not self._robot(card):
            return super()._capture_open(message, state, card, caps)
        self._opening_robot = (self._open_generation, card["entity_id"], caps["robot_domain"])
        return self._opening_robot

    def _revalidate_open(self, captured, state, card, caps):
        if not self._robot(card):
            return super()._revalidate_open(captured, state, card, caps)
        if captured is not self._opening_robot or caps["robot_domain"] != captured[2]:
            raise ProtocolError("capabilities_changed")

    def _finish_open(self, captured):
        if captured is not None and captured is self._opening_robot:
            self._opening_robot = None
        return super()._finish_open(captured)

    def _observe_robot(self, selected, state, domain):
        observation = RobotObservation.from_ha(state, domain)
        previous = selected.domain_state
        if previous is None:
            selected.domain_state = (domain, observation, 1)
        elif previous[0] != domain:
            raise ProtocolError("capabilities_changed")
        elif previous[1].command_state != observation.command_state:
            if previous[2] >= MAX_SEQUENCE:
                raise ProtocolError("expired")
            selected.domain_state = (domain, observation, previous[2] + 1)
        else:
            selected.domain_state = (domain, observation, previous[2])
        return selected.domain_state

    def observe_state_event(self, event=None):
        data = getattr(event, "data", {})
        entity, state = data.get("entity_id"), data.get("new_state")
        selected, opening = self._selection, self._opening_robot
        selected_robot = selected is not None and selected.identity.get("control_kind") == "robot"
        if not ((selected_robot and entity == selected.entity_id) or (opening and entity == opening[1])):
            return super().observe_state_event(event)
        try:
            if state is None:
                raise ProtocolError("entity_unavailable")
            domain = self._robot_domain(state)
            if opening and entity == opening[1] and domain != opening[2]:
                raise ProtocolError("capabilities_changed")
            if selected_robot and entity == selected.entity_id:
                self._observe_robot(selected, state, domain)
        except ProtocolError as error:
            self._opening_robot = None
            return self.revoke_now("capabilities_changed" if str(error) == "unsupported" else str(error))
        return None

    def observe_robot_registry_event(self, event):
        """Observe private area metadata now, including A-B-A during an await."""
        selected, opening = self._selection, self._opening_robot
        entity = selected.entity_id if selected is not None and selected.identity.get("control_kind") == "robot" else opening[1] if opening else None
        if entity is None:
            return None
        changed = getattr(event, "data", {}).get("entity_id")
        if changed is not None and changed != entity:
            return None
        area_id = getattr(event, "data", {}).get("area_id")
        previous = selected.domain_state[0] if selected is not None and selected.domain_state else opening[2] if opening else None
        if area_id is not None and previous is not None and area_id not in {item[0] for item in previous.area_mapping}:
            return None
        from types import SimpleNamespace
        return self.observe_state_event(SimpleNamespace(data={"entity_id": entity, "new_state": self.hass.states.get(entity)}))

    def _selection_snapshot_fields(self, selected, state, card, caps):
        if selected.identity.get("control_kind") != "robot":
            return super()._selection_snapshot_fields(selected, state, card, caps)
        domain, observed, generation = self._observe_robot(selected, state, caps["robot_domain"])
        title = plain_text(card.get("title") or state.attributes.get("friendly_name") or "Robot", 40)
        title = "".join(c for c in title if c.isprintable() and not 0xD800 <= ord(c) <= 0xDFFF)
        while len(title.encode()) > 160:
            title = title[:-1]
        return {"title": title, **observed.descriptor(), "robot_caps": domain.descriptor(),
                "robot_type": domain.robot_type,
                "state_generation": generation}

    def _prepare_command(self, selected, message):
        if selected.identity.get("control_kind") != "robot":
            return super()._prepare_command(selected, message)
        state, _, caps = self._valid_selection(selected)
        domain, observed, generation = self._observe_robot(selected, state, caps["robot_domain"])
        interrupt = message["op"] in INTERRUPTS[domain.robot_type]
        expected = message["expected_state_generation"]
        if ((expected > generation if interrupt else expected != generation)
                or not observed.can_command(message["op"])):
            raise ProtocolError("stale_state")
        try:
            domain.service_action(message["op"], message.get("target_index"))
        except RobotDomainError:
            raise ProtocolError("unsupported") from None
        return domain, observed, generation, message["op"], message.get("target_index")

    def _validate_prepared(self, selected, record, state, caps):
        if selected.identity.get("control_kind") != "robot":
            return super()._validate_prepared(selected, record, state, caps)
        current = self._observe_robot(selected, state, caps["robot_domain"])
        if record.prepared is not None and record.prepared[3] in INTERRUPTS[current[0].robot_type]:
            if current[0] != record.prepared[0] or not current[1].can_command(record.prepared[3]):
                raise ProtocolError("stale_state")
            record.prepared = (*current, *record.prepared[3:])
            return
        if (record.prepared is None or current[0] != record.prepared[0]
                or current[1].command_state != record.prepared[1].command_state or current[2] != record.prepared[2]):
            raise ProtocolError("stale_state")

    def _is_priority_successor(self, selected, message):
        if selected.identity.get("control_kind") != "robot":
            return super()._is_priority_successor(selected, message)
        previous = selected.command
        domain = selected.domain_state[0]
        return (message.get("op") in INTERRUPTS[domain.robot_type] and previous is not None
                and not previous.priority and previous.payload.get("control_kind") == "robot"
                and previous.payload.get("op") in MOTION_FAMILIES[domain.robot_type])

    def _command_service_action(self, state, caps, record):
        if record.payload.get("control_kind") != "robot":
            return super()._command_service_action(state, caps, record)
        domain, _, _, operation, target = record.prepared
        if caps["robot_domain"] != domain:
            raise ProtocolError("capabilities_changed")
        try:
            service_domain, service, data = domain.service_action(operation, target)
            validate_live_action(self.hass, state, {"service": service_domain + "." + service, "data": data})
        except ValueError:
            raise ProtocolError("unsupported") from None
        return service_domain, service, data

    def _completed_service_status(self, selected, record):
        if selected.identity.get("control_kind") == "robot" and record.prepared[3] in COMPLETED_OPERATIONS:
            return "service_completed"
        return super()._completed_service_status(selected, record)

    def _command_matches(self, selected, record):
        if selected.identity.get("control_kind") != "robot":
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        domain, _, _, operation, target = record.prepared
        if record.result["status"] == "pending" and record.priority and record.predecessor_started:
            return False
        return domain == caps["robot_domain"] and RobotObservation.from_ha(state, domain).matches(domain, operation, target)

    async def _send(self, value):
        selected = self._selection
        if (value.get("kind") == "result" and value.get("status") in self._terminal_statuses
                and value.get("control_kind") == "robot" and selected is not None
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
