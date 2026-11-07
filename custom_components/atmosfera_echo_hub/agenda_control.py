"""Read-only Agenda policy on the existing selection, auth slot and refresh task."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from .agenda_domain import ACTION, AgendaDomain, AgendaError, AgendaObservation, bounded_events, empty_fields, window
from .control_session import CLOSE_REASONS, MAX_SEQUENCE, ProtocolError
from .layout import LayoutError, validate_action


@dataclass
class AgendaSelection:
    domain: AgendaDomain
    start: datetime
    end: datetime
    started: float
    generation: int = 1
    source: str = "known"
    status: str = "loading"
    rows: list = field(default_factory=list)
    more: bool = False
    digest: tuple = ("known", "loading", False, ())
    index: int | None = None
    request_seq: int = 0
    highest: int = 0
    pending: int | None = None
    last: tuple | None = None
    unsubscribe: object = None
    invalid: bool = False

    def fields(self):
        value = empty_fields(self.source, self.status, self.request_seq)
        if self.source == "known" and self.status == "ready" and self.rows:
            value.update(self.rows[self.index].fields, index=self.index, count=len(self.rows), has_more=self.more)
        return value


class AgendaControlPolicy:
    def __init__(self, *args, agenda_changed=None, agenda_now=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._agenda_channel = None
        self._agenda_changed = agenda_changed or (lambda: None)
        self._agenda_now = agenda_now or (lambda: datetime.now(timezone.utc))

    def prepare_bind(self, *args, **kwargs):
        self._agenda_channel = None
        return super().prepare_bind(*args, **kwargs)

    @property
    def info_agenda_version(self):
        return int(self.mode == "entity" and self.channel_ready and self._agenda_channel == self.channel
                   and {"name": "info", "version": 1} in self.panel_extra_profiles)

    def accept_agenda_features(self, channel):
        if (channel != self.channel or not self.channel_ready or self.mode != "entity"
                or {"name": "info", "version": 1} not in self.panel_extra_profiles
                or self._selection is not None or self._opening is not None
                or self._service_task is not None and not self._service_task.done()
                or self._authorization_task is not None and not self._authorization_task.done()):
            raise ProtocolError("unsupported")
        self._agenda_channel = channel

    def _authorization_policy(self, card):
        return self.authorize_read if card.get("action") == ACTION else super()._authorization_policy(card)

    def _panel_domain(self, state, card):
        if card.get("action") != ACTION:
            return super()._panel_domain(state, card)
        if self.info_agenda_version != 1:
            raise ProtocolError("unsupported")
        try:
            return AgendaDomain.from_ha(self.hass, state)
        except AgendaError:
            raise ProtocolError("entity_unavailable") from None

    def _entity_binding(self, card):
        if card.get("action") != ACTION:
            return super()._entity_binding(card)
        entity_id = card.get("entity_id")
        if (card.get("type") not in {"sensor", "entity"} or not isinstance(entity_id, str)
                or not entity_id.startswith("calendar.")):
            raise ProtocolError("unsupported")
        try:
            validate_action(card["action"], entity_id, layout_version=3)
        except LayoutError:
            raise ProtocolError("unsupported") from None
        state = self.hass.states.get(entity_id)
        if state is None:
            raise ProtocolError("entity_unavailable")
        return state, {"panel_domain": self._panel_domain(state, card)}

    @staticmethod
    def _agenda_source(state):
        return state.state if state.state in {"unknown", "unavailable"} else "known"

    def _valid_selection(self, selected):
        state, card, caps = super()._valid_selection(selected)
        if isinstance(selected.domain_state, AgendaSelection):
            # Validate bounded cache/deadline before the common refresh enters
            # its snapshot path, so generation exhaustion uses its CLOSE path.
            self._observe_panel(selected, state, caps["panel_domain"])
        return state, card, caps

    def _replace_agenda(self, current, source, status, events=None):
        # Discard the old bounded cache before building its replacement. Only the
        # old digest/index survive; Core owns the incoming list, which we never edit.
        old_index = current.index
        current.rows.clear()
        current.more = False
        if events is not None and source == "known":
            try:
                current.rows, current.more = bounded_events(events, current.start, current.end, current.domain.zone)
            except (AgendaError, UnicodeError, TypeError, ValueError, OverflowError):
                status = "error"
        digest = source, status, current.more, tuple(item.digest for item in current.rows)
        current.source, current.status = source, status
        if digest != current.digest:
            if current.generation >= MAX_SEQUENCE:
                current.invalid = True
                raise ProtocolError("expired")
            current.generation += 1
            current.digest = digest
            current.index = 0 if current.rows else None
        else:
            current.index = old_index if current.rows else None

    def _observe_panel(self, selected, state, domain):
        if not isinstance(domain, AgendaDomain):
            return super()._observe_panel(selected, state, domain)
        current = selected.domain_state
        source = self._agenda_source(state)
        if current is None:
            start, end = window(self._agenda_now(), domain.zone)
            current = AgendaSelection(domain, start, end, self.clock())
            current.source = source
            current.status = "loading" if source == "known" else "unknown"
            current.digest = source, current.status, False, ()
            selected.domain_state = current
        elif not isinstance(current, AgendaSelection) or current.domain != domain:
            raise ProtocolError("capabilities_changed")
        elif current.invalid:
            raise ProtocolError("expired")
        elif source != current.source:
            self._replace_agenda(current, source, "loading" if source == "known" else "unknown")
        elif current.status == "loading" and self.clock() - current.started >= 10:
            self._replace_agenda(current, source, "error")
        return domain, AgendaObservation(current.fields()), current.generation

    async def _snapshot(self, selected, kind, state, card):
        result = await super()._snapshot(selected, kind, state, card)
        current = selected.domain_state
        if kind == "grant" and selected is self._selection and isinstance(current, AgendaSelection):
            entity = current.domain.entity

            def changed(events):
                if selected is not self._selection or selected.domain_state is not current:
                    return
                try:
                    state, _, _ = self._valid_selection(selected)
                    source = self._agenda_source(state)
                    self._replace_agenda(current, source,
                        "unknown" if source != "known" else "error" if events is None else "ready", events)
                except ProtocolError:
                    # Existing coalesced refresh retires the now-invalid source.
                    pass
                self._agenda_changed()

            current.unsubscribe = entity.async_subscribe_events(current.start, current.end, changed)
            # Core schedules/owns its fetch; closing never assumes that task stopped.
            entity.async_update_single_event_listener(current.start, current.end, changed)
        return result

    def _detach_selection(self, reason):
        selected = self._selection
        current = selected.domain_state if selected is not None else None
        if isinstance(current, AgendaSelection):
            if current.unsubscribe is not None:
                current.unsubscribe()
                current.unsubscribe = None
            current.rows.clear()
            current.last = current.pending = None
        return super()._detach_selection(reason)

    def _prepare_command(self, selected, message):
        if isinstance(selected.caps.get("panel_domain"), AgendaDomain):
            raise ProtocolError("unsupported")
        return super()._prepare_command(selected, message)

    def observe_robot_registry_event(self, event):
        selected = self._selection
        opening = self._opening_panel
        agenda_opening = opening is not None and isinstance(opening[2], AgendaDomain)
        if agenda_opening or selected is not None and isinstance(selected.caps.get("panel_domain"), AgendaDomain):
            data = getattr(event, "data", {})
            changes = data.get("changes") or {}
            affected = {data.get("entity_id"), changes.get("entity_id")}
            identity_keys = {"disabled_by", "entity_id", "device_id", "unique_id", "platform", "config_entry_id"}
            entity_id = selected.entity_id if selected is not None else opening[1]
            if entity_id in affected and (data.get("action") in {"create", "remove"} or identity_keys.intersection(changes)):
                return self.revoke_now("capabilities_changed")
        return super().observe_robot_registry_event(event)

    async def async_handle(self, payload, context=None):
        message = self._decode(payload)
        if message["kind"] != "page":
            return await super().async_handle(payload, context)
        if not self._connection_current() or not self.channel_ready or message["channel"] != self.channel:
            raise ProtocolError("connection_lost")
        selected = self._selection
        if selected is None or any(message[key] != selected.identity[key] for key in self._selection_fields):
            raise ProtocolError("selection_changed")
        if self._principal(context) != selected.principal:
            raise ProtocolError("unauthorized")
        state, card, caps = self._valid_selection(selected)
        if not isinstance(caps.get("panel_domain"), AgendaDomain):
            raise ProtocolError("unsupported")
        self._observe_panel(selected, state, caps["panel_domain"])
        current = selected.domain_state
        seq, target, expected = (message[key] for key in ("request_seq", "target_index", "expected_state_generation"))
        request = seq, target, expected

        async def receipt(status, reason="none", retain=True):
            value = self._envelope("page_result", **selected.identity, request_seq=seq, target_index=target,
                                   state_seq=selected.state_seq, status=status, reason=reason)
            if retain and seq == current.highest:
                current.last = request, value
            return await self._send(value)

        if current.last and seq == current.last[0][0]:
            if request != current.last[0]:
                return await receipt("rejected", "sequence_conflict", False)
            if current.last[1]["status"] == "ready" and expected != current.generation:
                return await receipt("rejected", "stale_state", False)
            return await self._send(current.last[1])
        if seq <= current.highest:
            return await receipt("rejected", "stale_sequence", False)
        current.highest = seq
        if current.pending is not None or self._authorization_task is not None and not self._authorization_task.done():
            return await receipt("rejected", "busy")

        def admissible():
            return (current.source == "known" and current.status == "ready" and expected == current.generation
                    and target < len(current.rows) and target != current.index)

        if not admissible():
            return await receipt("rejected", "stale_state")
        current.pending = seq
        try:
            allowed = await self._authorized(context, selected.entity_id, authorizer=self.authorize_read)
            if selected is not self._selection:
                return None
            if not allowed:
                return await receipt("rejected", "unauthorized")
            state, card, caps = self._valid_selection(selected)
            self._observe_panel(selected, state, caps["panel_domain"])
            if not admissible():
                return await receipt("rejected", "stale_state")
            current.index, current.request_seq = target, seq
            await self._snapshot(selected, "state", state, card)
            if selected is not self._selection:
                return None
            self._valid_selection(selected)
            if (current.generation, current.index, current.request_seq) != (expected, target, seq):
                return await receipt("rejected", "stale_state")
            return await receipt("ready")
        except ProtocolError as error:
            if selected is self._selection:
                if str(error) in CLOSE_REASONS:
                    await self.async_close(str(error))
                else:
                    return await receipt("rejected", "unsupported")
        finally:
            if current.pending == seq:
                current.pending = None
        return None
