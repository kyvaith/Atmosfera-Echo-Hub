"""External-media policy on the existing selected owner and single service fence."""

from .cards import validate_live_action
from .control_session import CLOSE_REASONS, MAX_SEQUENCE, TERMINAL, ControlSessionOwner, ProtocolError
from .detail_control import DetailSelection
from .media_panel_domain import MEDIA_ACTION, MediaDomain, MediaPanelError
from .text import plain_text


class MediaPanelPolicy:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._opening_media = None

    def prepare_bind(self, *args, **kwargs):
        self._opening_media = None
        return super().prepare_bind(*args, **kwargs)

    def _media_domain(self, state):
        try:
            return MediaDomain.from_ha(self.hass, state, self._choice_language())
        except ValueError:
            raise ProtocolError("unsupported") from None

    def _entity_binding(self, card):
        if card.get("action") != MEDIA_ACTION:
            return super()._entity_binding(card)
        if (card.get("type") != "entity" or not isinstance(card.get("entity_id"), str)
                or not card["entity_id"].startswith("media_player.")
                or {"name": "media", "version": 1} not in self.panel_extra_profiles):
            raise ProtocolError("unsupported")
        state = self.hass.states.get(card["entity_id"])
        if state is None:
            raise ProtocolError("entity_unavailable")
        return state, {"media_domain": self._media_domain(state)}

    def _capture_open(self, message, state, card, caps):
        if "media_domain" not in caps:
            return super()._capture_open(message, state, card, caps)
        self._opening_media = (self._open_generation, card["entity_id"], caps["media_domain"])
        return self._opening_media

    def _revalidate_open(self, captured, state, card, caps):
        if "media_domain" not in caps:
            return super()._revalidate_open(captured, state, card, caps)
        if captured is not self._opening_media or captured[2] != caps["media_domain"]:
            raise ProtocolError("capabilities_changed")

    def _finish_open(self, captured):
        if captured is not None and captured is self._opening_media:
            self._opening_media = None
        return super()._finish_open(captured)

    def _observe_media(self, selected, state, domain):
        observation = domain.command_state(state)
        current = selected.domain_state
        if current is None:
            current = selected.domain_state = DetailSelection(domain, observation)
        elif not isinstance(current, DetailSelection) or current.domain != domain:
            raise ProtocolError("capabilities_changed")
        elif current.observation != observation:
            if current.generation >= MAX_SEQUENCE:
                raise ProtocolError("expired")
            current.observation, current.generation = observation, current.generation + 1
        return current

    def observe_state_event(self, event=None):
        data = getattr(event, "data", {})
        entity, state = data.get("entity_id"), data.get("new_state")
        selected, opening = self._selection, self._opening_media
        relevant = selected is not None and "media_domain" in selected.caps and entity == selected.entity_id
        if not (relevant or opening and entity == opening[1]):
            return super().observe_state_event(event)
        try:
            if state is None:
                raise ProtocolError("entity_unavailable")
            domain = self._media_domain(state)
            if opening and entity == opening[1] and domain != opening[2]:
                raise ProtocolError("capabilities_changed")
            if relevant:
                self._observe_media(selected, state, domain)
        except ProtocolError as error:
            self._opening_media = None
            return self.revoke_now(str(error) if str(error) in CLOSE_REASONS else "capabilities_changed")
        return None

    def _selection_snapshot_fields(self, selected, state, card, caps):
        if "media_domain" not in caps:
            return super()._selection_snapshot_fields(selected, state, card, caps)
        domain = caps["media_domain"]
        current = self._observe_media(selected, state, domain)
        title = plain_text(card.get("title") or state.attributes.get("friendly_name") or "Media", 40)
        title = "".join(c for c in title if c.isprintable() and not 0xD800 <= ord(c) <= 0xDFFF)
        while len(title.encode()) > 160:
            title = title[:-1]
        body = domain.view(state, current.facet, current.view_seq)
        eligible = body["eligible"] if current.facet == "main" else (
            (1 if current.facet == "volume" else 2) if body["editable"] else 0)
        return {"title": title, "panel_type": "media", "available": domain.source(state) == "known",
                "panel_caps": domain.descriptor(), "panel_state": body,
                "eligible_actions": eligible, "state_generation": current.generation}

    async def async_handle(self, payload, context=None):
        message = self._decode(payload)
        if message["kind"] != "facet" or message.get("media_version") != 1:
            return await super().async_handle(payload, context)
        selected = self._selection
        if not self._connection_current() or not self.channel_ready or message["channel"] != self.channel:
            raise ProtocolError("connection_lost")
        if selected is None or any(message[key] != selected.identity[key] for key in self._selection_fields):
            raise ProtocolError("selection_changed")
        if self._principal(context) != selected.principal:
            raise ProtocolError("unauthorized")
        state, card, caps = self._valid_selection(selected)
        if "media_domain" not in caps:
            raise ProtocolError("unsupported")
        current = self._observe_media(selected, state, caps["media_domain"])
        sequence, facet = message["view_seq"], message["facet"]

        async def receipt(status, reason="none", retain=True):
            value = self._envelope("facet_result", **selected.identity, media_version=1, view_seq=sequence,
                                   facet=facet, state_seq=selected.state_seq, status=status, reason=reason)
            if retain and sequence == current.highest_view:
                current.last_view = value
            return await self._send(value)

        if current.last_view and sequence == current.last_view["view_seq"]:
            if facet != current.last_view["facet"]:
                return await receipt("rejected", "sequence_conflict", False)
            return await self._send(current.last_view)
        if sequence <= current.highest_view:
            return await receipt("rejected", "stale_sequence", False)
        current.highest_view = sequence
        if (current.pending is not None or selected.command is not None
                or self._service_task is not None and not self._service_task.done()
                or self._authorization_task is not None and not self._authorization_task.done()):
            return await receipt("rejected", "busy")
        if not current.domain.allowed_facet(facet):
            return await receipt("rejected", "unsupported")
        current.pending = sequence
        try:
            allowed = await self._authorized(context, selected.entity_id)
            if selected is not self._selection:
                return None
            if not allowed:
                return await receipt("rejected", "unauthorized")
            state, card, caps = self._valid_selection(selected)
            self._observe_media(selected, state, caps["media_domain"])
            current.facet, current.view_seq = facet, sequence
            await self._snapshot(selected, "state", state, card)
            if selected is self._selection:
                return await receipt("ready")
        except ProtocolError as error:
            if selected is self._selection:
                if str(error) in CLOSE_REASONS:
                    await self.async_close(str(error))
                else:
                    return await receipt("rejected", str(error) if str(error) in self._result_reasons else "unsupported")
        finally:
            if current.pending == sequence:
                current.pending = None
        return None

    def _prepare_command(self, selected, message):
        if "media_domain" not in selected.caps:
            if "media_version" in message:
                raise ProtocolError("unsupported")
            return super()._prepare_command(selected, message)
        state, _, caps = self._valid_selection(selected)
        current = self._observe_media(selected, state, caps["media_domain"])
        if current.pending is not None:
            raise ProtocolError("busy")
        if (message.get("media_version") != 1 or message.get("facet") != current.facet
                or message.get("view_seq") != current.view_seq
                or message.get("expected_state_generation") != current.generation):
            raise ProtocolError("stale_state")
        domain, operation, facet = current.domain, message["op"], current.facet
        target = None
        if operation == "volume":
            observed = domain.volume(state)
            if observed is None or message.get("expected_raw") != observed.raw:
                raise ProtocolError("stale_state")
            target = message["target_percent"]
        elif operation == "choice":
            index = domain.choice(state, facet)
            if index is None or message.get("expected_index") != index:
                raise ProtocolError("stale_state")
            target = message["target_index"]
        elif operation in {"mute", "shuffle"}:
            target = message["target"]
        try:
            domain.service(self.hass, state, facet, operation, target)
        except ValueError:
            raise ProtocolError("unsupported") from None
        return (domain, current.observation, current.generation, facet, current.view_seq, operation, target)

    def _validate_prepared(self, selected, record, state, caps):
        if "media_domain" not in caps:
            return super()._validate_prepared(selected, record, state, caps)
        current = self._observe_media(selected, state, caps["media_domain"])
        if record.prepared[:5] != (current.domain, current.observation, current.generation, current.facet, current.view_seq):
            raise ProtocolError("stale_state")

    def _command_service_action(self, state, caps, record):
        if "media_domain" not in caps:
            return super()._command_service_action(state, caps, record)
        domain, _, _, facet, _, operation, target = record.prepared
        try:
            return domain.service(self.hass, state, facet, operation, target)
        except ValueError:
            raise ProtocolError("unsupported") from None

    def _command_matches(self, selected, record):
        if "media_domain" not in selected.caps:
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        current = self._observe_media(selected, state, caps["media_domain"])
        domain, _, generation, facet, _, operation, target = record.prepared
        return (current.domain == domain and record.service_started and current.generation > generation
                and domain.matches(state, facet, operation, target))

    def _completed_service_status(self, selected, record):
        if "media_domain" not in selected.caps:
            return super()._completed_service_status(selected, record)
        return "service_completed" if record.prepared[5] in {"previous", "next", "volume_up", "volume_down"} else None

    async def _send(self, value):
        selected = self._selection
        if (value.get("kind") == "result" and value.get("status") in TERMINAL and selected is not None
                and "media_domain" in selected.caps
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
            return await ControlSessionOwner._send(self, value)
        return await super()._send(value)
