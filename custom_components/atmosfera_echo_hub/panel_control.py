"""Three panel policies using the existing sole session and service fence."""

from .cards import validate_live_action
from .control_session import CLOSE_REASONS, MAX_SEQUENCE, TERMINAL, ProtocolError
from .panel_domain import DOMAINS, PanelDomain, PanelDomainError, PanelObservation
from .panel_features import valid_types
from .layout import LayoutError, validate_action
from .text import plain_text


class PanelControlPolicy:
    _terminal_statuses = TERMINAL | {"service_completed"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._opening_panel = None
        self._panel_channel = None
        self._panel_types = ()

    def set_mode(self, mode):
        super().set_mode(mode)
        self._panel_channel, self._panel_types = None, ()

    def prepare_bind(self, *args, **kwargs):
        self._panel_channel, self._panel_types = None, ()
        return super().prepare_bind(*args, **kwargs)

    @property
    def panel_types(self):
        return self._panel_types if (self.mode == "entity" and self.channel_ready
                                    and self._panel_channel == self.channel and "panel" in self.control_kinds) else ()

    def accept_panel_features(self, channel, families):
        if (self.mode != "entity" or not self.channel_ready or channel != self.channel
                or "panel" not in self.control_kinds or self._selection is not None or self._opening is not None
                or not valid_types(families)):
            raise ProtocolError("unsupported")
        self._panel_channel, self._panel_types = channel, tuple(families)

    @staticmethod
    def _panel(card):
        action = card.get("action", {})
        return isinstance(action, dict) and action.get("kind") == "control" and action.get("control") == "panel"

    def _panel_domain(self, state, card):
        action = card["action"]
        try:
            domain = PanelDomain.from_ha(self.hass, state, action.get("initial_duration"))
            if domain.family != action.get("property") or domain.family not in self.panel_types:
                raise PanelDomainError("family")
            return domain
        except PanelDomainError:
            raise ProtocolError("unsupported") from None

    def _entity_binding(self, card):
        if not self._panel(card):
            return super()._entity_binding(card)
        entity = card.get("entity_id")
        family = card["action"].get("property")
        if (family not in self.panel_types or card.get("type") != "entity"
                or not isinstance(entity, str) or entity.partition(".")[0] not in DOMAINS.get(family, ())):
            raise ProtocolError("unsupported")
        try:
            validate_action(card["action"], entity, layout_version=3)
        except LayoutError:
            raise ProtocolError("unsupported") from None
        state = self.hass.states.get(entity)
        if state is None:
            raise ProtocolError("entity_unavailable")
        return state, {"panel_domain": self._panel_domain(state, card)}

    def _capture_open(self, message, state, card, caps):
        if not self._panel(card):
            return super()._capture_open(message, state, card, caps)
        self._opening_panel = (self._open_generation, self._resolved_target(state, card, caps).entity_id, caps["panel_domain"], card)
        return self._opening_panel

    def _revalidate_open(self, captured, state, card, caps):
        if not self._panel(card):
            return super()._revalidate_open(captured, state, card, caps)
        if captured is not self._opening_panel or caps["panel_domain"] != captured[2]:
            raise ProtocolError("capabilities_changed")

    def _finish_open(self, captured):
        if captured is not None and captured is self._opening_panel:
            self._opening_panel = None
        return super()._finish_open(captured)

    def _observe_panel(self, selected, state, domain):
        observed = PanelObservation.from_ha(state, domain)
        previous = selected.domain_state
        if previous is None:
            selected.domain_state = (domain, observed, 1)
        elif previous[0] != domain:
            raise ProtocolError("capabilities_changed")
        elif previous[1].command_state != observed.command_state:
            if previous[2] >= MAX_SEQUENCE:
                raise ProtocolError("expired")
            selected.domain_state = (domain, observed, previous[2] + 1)
        else:
            selected.domain_state = (domain, observed, previous[2])
        return selected.domain_state

    def observe_state_event(self, event=None):
        data = getattr(event, "data", {})
        entity, state = data.get("entity_id"), data.get("new_state")
        selected, opening = self._selection, self._opening_panel
        relevant = selected is not None and selected.identity.get("control_kind") == "panel" and entity == selected.entity_id
        if not (relevant or opening and entity == opening[1]):
            return super().observe_state_event(event)
        try:
            if state is None:
                raise ProtocolError("entity_unavailable")
            card = self._valid_selection(selected)[1] if relevant else opening[3]
            domain = self._panel_domain(state, card)
            if opening and entity == opening[1] and domain != opening[2]:
                raise ProtocolError("capabilities_changed")
            if relevant:
                self._observe_panel(selected, state, domain)
        except (ProtocolError, PanelDomainError) as error:
            self._opening_panel = None
            return self.revoke_now(str(error) if str(error) in CLOSE_REASONS else "capabilities_changed")
        return None

    def _selection_snapshot_fields(self, selected, state, card, caps):
        if selected.identity.get("control_kind") != "panel":
            return super()._selection_snapshot_fields(selected, state, card, caps)
        domain, observed, generation = self._observe_panel(selected, state, caps["panel_domain"])
        title = plain_text(card.get("title") or state.attributes.get("friendly_name") or domain.family.title(), 40)
        title = "".join(c for c in title if c.isprintable() and not 0xD800 <= ord(c) <= 0xDFFF)
        while len(title.encode()) > 160:
            title = title[:-1]
        return {"title": title, "panel_type": domain.family, "panel_caps": domain.descriptor(),
                "panel_state": observed.descriptor(), "available": observed.available,
                "eligible_actions": observed.eligible(domain), "state_generation": generation}

    def _prepare_command(self, selected, message):
        if selected.identity.get("control_kind") != "panel":
            return super()._prepare_command(selected, message)
        state, _, caps = self._valid_selection(selected)
        domain, observed, generation = self._observe_panel(selected, state, caps["panel_domain"])
        operation = message["op"]
        target = message.get("duration_seconds") if operation == "set_duration" else message.get("target_index")
        if message["expected_state_generation"] != generation or not observed.can_command(domain, operation, target):
            raise ProtocolError("stale_state")
        try:
            domain.service_action(selected.entity_id, operation, target)
        except PanelDomainError:
            raise ProtocolError("unsupported") from None
        return domain, observed, generation, operation, target

    def _validate_prepared(self, selected, record, state, caps):
        if selected.identity.get("control_kind") != "panel":
            return super()._validate_prepared(selected, record, state, caps)
        current = self._observe_panel(selected, state, caps["panel_domain"])
        if (record.prepared is None or current[0] != record.prepared[0]
                or current[1].command_state != record.prepared[1].command_state or current[2] != record.prepared[2]):
            raise ProtocolError("stale_state")

    def _command_service_action(self, state, caps, record):
        if record.payload.get("control_kind") != "panel":
            return super()._command_service_action(state, caps, record)
        domain, _, _, operation, target = record.prepared
        if caps["panel_domain"] != domain:
            raise ProtocolError("capabilities_changed")
        try:
            service_domain, service, data = domain.service_action(state.entity_id, operation, target)
            validate_live_action(self.hass, state, {"service": service_domain + "." + service, "data": data})
        except ValueError:
            raise ProtocolError("unsupported") from None
        return service_domain, service, data

    def _completed_service_status(self, selected, record):
        if selected.identity.get("control_kind") == "panel" and record.prepared[3] == "set_duration":
            return "service_completed"
        return super()._completed_service_status(selected, record)

    def _command_matches(self, selected, record):
        if selected.identity.get("control_kind") != "panel":
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        domain, observed, generation = self._observe_panel(selected, state, caps["panel_domain"])
        expected, _, prepared_generation, operation, target = record.prepared
        if domain != expected or not observed.matches(operation, target):
            return False
        # A source phase change, not elapsed display time or a repeated active
        # snapshot, proves a Timer transition. Repeatable restart never matches.
        return domain.family != "timer" or (record.service_started and generation > prepared_generation)

    async def _send(self, value):
        selected = self._selection
        if (value.get("kind") == "result" and value.get("status") in self._terminal_statuses
                and value.get("control_kind") == "panel" and selected is not None
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
