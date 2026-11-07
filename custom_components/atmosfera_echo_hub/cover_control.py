"""Cover policy hooks over the existing one owner, lease and service fence."""

from .cards import validate_live_action
from .control_session import CLOSE_REASONS, MAX_SEQUENCE, TERMINAL, ProtocolError
from .cover_domain import CoverDomain, CoverDomainError, CoverObservation
from .cover_panel_domain import CoverPanelDomain, CoverPanelObservation, MOTION_FAMILIES, NUMERIC_OPERATIONS, SERVICES, STOP_OPERATIONS
from .text import plain_text


class CoverControlPolicy:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._opening_cover = None

    @staticmethod
    def _cover(card):
        return card.get("action") == {"kind": "control", "control": "cover"}

    def _cover_domain(self, state):
        try:
            if self.cover_panel_version == 1:
                return CoverPanelDomain.from_ha(state.attributes, {
                    service: self.hass.services.has_service("cover", service) for service in SERVICES.values()
                })
            return CoverDomain.from_ha(state.attributes, {
                operation + "_cover": self.hass.services.has_service("cover", operation + "_cover")
                for operation in ("open", "stop", "close")
            })
        except CoverDomainError:
            raise ProtocolError("unsupported") from None

    def _entity_binding(self, card):
        if not self._cover(card):
            return super()._entity_binding(card)
        entity = card.get("entity_id")
        if (self.mode != "entity" or "cover" not in self.control_kinds or card.get("type") != "entity"
                or self.cover_stop_version != 1
                or not isinstance(entity, str) or entity.partition(".")[0] != "cover"):
            raise ProtocolError("unsupported")
        state = self.hass.states.get(entity)
        if state is None:
            raise ProtocolError("entity_unavailable")
        return state, {"cover_domain": self._cover_domain(state)}

    def _capture_open(self, message, state, card, caps):
        if not self._cover(card):
            return super()._capture_open(message, state, card, caps)
        self._opening_cover = (self._open_generation, card["entity_id"], caps["cover_domain"])
        return self._opening_cover

    def _revalidate_open(self, captured, state, card, caps):
        if not self._cover(card):
            return super()._revalidate_open(captured, state, card, caps)
        if captured is not self._opening_cover or caps["cover_domain"] != captured[2]:
            raise ProtocolError("capabilities_changed")

    def _finish_open(self, captured):
        if captured is not None and captured is self._opening_cover:
            self._opening_cover = None
        return super()._finish_open(captured)

    def _observe_cover(self, selected, state, domain):
        model = CoverPanelObservation if isinstance(domain, CoverPanelDomain) else CoverObservation
        observed = model.from_ha(state.state, state.attributes)
        previous = selected.domain_state
        if previous is None:
            selected.domain_state = (domain, observed, 1)
        elif previous[0] != domain:
            raise ProtocolError("capabilities_changed")
        elif previous[1] != observed:
            if previous[2] >= MAX_SEQUENCE:
                raise ProtocolError("expired")
            selected.domain_state = (domain, observed, previous[2] + 1)
        return selected.domain_state

    def observe_state_event(self, event=None):
        data = getattr(event, "data", {})
        entity, state = data.get("entity_id"), data.get("new_state")
        selected, opening = self._selection, self._opening_cover
        selected_cover = selected is not None and selected.identity.get("control_kind") == "cover"
        if not ((selected_cover and entity == selected.entity_id) or (opening and entity == opening[1])):
            return super().observe_state_event(event)
        try:
            if state is None:
                raise ProtocolError("entity_unavailable")
            domain = self._cover_domain(state)
            if opening and entity == opening[1] and domain != opening[2]:
                raise ProtocolError("capabilities_changed")
            if selected_cover and entity == selected.entity_id:
                self._observe_cover(selected, state, domain)
        except ProtocolError as error:
            self._opening_cover = None
            return self.revoke_now("capabilities_changed" if str(error) == "unsupported" else str(error))
        return None

    def _selection_snapshot_fields(self, selected, state, card, caps):
        if selected.identity.get("control_kind") != "cover":
            return super()._selection_snapshot_fields(selected, state, card, caps)
        domain, observed, generation = self._observe_cover(selected, state, caps["cover_domain"])
        title = plain_text(card.get("title") or state.attributes.get("friendly_name") or "Cover", 40)
        title = "".join(c for c in title if c.isprintable() and not 0xD800 <= ord(c) <= 0xDFFF)
        fields = {"title": title, "cover_state": observed.state, "position": observed.position,
                  "available": observed.available, "cover_caps": domain.descriptor(), "state_generation": generation}
        if isinstance(domain, CoverPanelDomain):
            fields["cover_panel"] = domain.panel_descriptor(observed.tilt_position)
        return fields

    def _prepare_command(self, selected, message):
        if selected.identity.get("control_kind") != "cover":
            return super()._prepare_command(selected, message)
        state, _, caps = self._valid_selection(selected)
        domain, observed, generation = self._observe_cover(selected, state, caps["cover_domain"])
        expected = message["expected_state_generation"]
        operation = message["op"]
        stop_intent = operation in STOP_OPERATIONS and self.cover_stop_version == 1
        if not observed.available or (expected > generation if stop_intent else expected != generation):
            raise ProtocolError("stale_state")
        if not domain.supports(operation):
            raise ProtocolError("unsupported")
        if operation in NUMERIC_OPERATIONS:
            if not isinstance(domain, CoverPanelDomain) or not observed.numeric_known(operation):
                raise ProtocolError("stale_state")
            return domain, observed, generation, operation, message["target_index"]
        return domain, observed, generation, operation

    def _validate_prepared(self, selected, record, state, caps):
        if selected.identity.get("control_kind") != "cover":
            return super()._validate_prepared(selected, record, state, caps)
        current = self._observe_cover(selected, state, caps["cover_domain"])
        if record.priority or (record.prepared is not None and record.prepared[3] in STOP_OPERATIONS
                               and self.cover_stop_version == 1):
            if (self.cover_stop_version != 1 or record.prepared is None or record.prepared[3] not in STOP_OPERATIONS
                    or current[0] != record.prepared[0] or not current[1].available
                    or not current[0].supports(record.prepared[3])):
                raise ProtocolError("capabilities_changed")
            # State updates while the predecessor completes do not invalidate
            # an admitted Stop intent. Only feedback after its own dispatch may
            # confirm it; earlier stationary state must never count as new.
            record.prepared = (*current, record.prepared[3])
            return
        if record.prepared is None or current != record.prepared[:3] or not current[1].available:
            raise ProtocolError("stale_state")

    def _is_priority_successor(self, selected, message):
        previous = selected.command
        stop = message.get("op")
        family = (MOTION_FAMILIES.get(stop, ()) if self.cover_panel_version == 1
                  else {"open", "close"} if stop == "stop" else ())
        return (self.cover_stop_version == 1 and selected.identity.get("control_kind") == "cover"
                and family and previous is not None and not previous.priority
                and previous.payload.get("control_kind") == "cover"
                and previous.payload.get("op") in family)

    def _command_service_action(self, state, caps, record):
        if record.payload.get("control_kind") != "cover":
            return super()._command_service_action(state, caps, record)
        operation = record.prepared[3]
        if not caps["cover_domain"].supports(operation):
            raise ProtocolError("unsupported")
        try:
            if isinstance(caps["cover_domain"], CoverPanelDomain):
                service, data = caps["cover_domain"].service_action(operation, record.prepared[4] if len(record.prepared) == 5 else None)
            else:
                service, data = operation + "_cover", {}
            validate_live_action(self.hass, state, {"service": "cover." + service, "data": data})
        except ValueError:
            raise ProtocolError("unsupported") from None
        return "cover", service, data

    def _command_matches(self, selected, record):
        if selected.identity.get("control_kind") != "cover":
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        _, observed, generation = self._observe_cover(selected, state, caps["cover_domain"])
        operation = record.prepared[3]
        if not observed.available:
            return False
        if isinstance(observed, CoverPanelObservation) and operation not in {"open", "close", "stop"}:
            if record.result["status"] == "pending" and record.priority and record.predecessor_started:
                return False
            return observed.target_matches(operation, record.prepared[4] if len(record.prepared) == 5 else None)
        if record.result["status"] == "pending":
            if record.priority and record.predecessor_started:
                return False
            return observed.already_matches(operation)
        if operation == "open":
            return observed.state == "opening" or (observed.state == "open" and
                    (observed.position == 100 or generation > record.prepared[2]))
        if operation == "close":
            return observed.state in {"closing", "closed"}
        return not observed.moving and generation > record.prepared[2]

    async def _send(self, value):
        selected = self._selection
        if (value.get("kind") == "result" and value.get("status") in TERMINAL
                and value.get("control_kind") == "cover" and selected is not None
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
