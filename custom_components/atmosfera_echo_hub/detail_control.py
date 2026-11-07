"""One active detail facet over the existing owner and service fence."""

from dataclasses import dataclass

from .cards import validate_live_action
from .control_session import CLOSE_REASONS, MAX_SEQUENCE, TERMINAL, ProtocolError, ControlSessionOwner
from .detail_domain import CLIMATE_ACTION, LIGHT_ACTION, DetailDomain, DetailDomainError
from .numeric_domain import NumericDomainError
from .choice_domain import ChoiceDomainError
from .text import plain_text
from .light_color_domain import ColorDomainError, target as color_target
from .climate_range_domain import RangeDomainError


@dataclass
class DetailSelection:
    domain: DetailDomain
    observation: tuple
    generation: int = 1
    facet: str = "main"
    view_seq: int = 0
    highest_view: int = 0
    pending: int | None = None
    last_view: dict | None = None


class DetailControlPolicy:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._detail_channel = None
        self._detail_light = self._detail_climate = False
        self._opening_detail = None
        self._color_channel = None
        self._range_channel = None

    def prepare_bind(self, *args, **kwargs):
        self._detail_channel = None
        self._detail_light = self._detail_climate = False
        self._color_channel = None
        self._range_channel = None
        return super().prepare_bind(*args, **kwargs)

    @property
    def light_detail_version(self):
        return int(self.mode == "entity" and self.channel_ready and self.channel == self._detail_channel
                   and "light" in self.control_kinds and self._detail_light)

    @property
    def climate_panel_version(self):
        return int(self.mode == "entity" and self.channel_ready and self.channel == self._detail_channel
                   and "panel" in self.control_kinds and self._detail_climate)

    def accept_detail_features(self, channel, light, climate):
        if (self.mode != "entity" or not self.channel_ready or channel != self.channel
                or self._selection is not None or self._opening is not None
                or type(light) is not int or light not in (0, 1) or type(climate) is not int or climate not in (0, 1)
                or not (light or climate) or light and "light" not in self.control_kinds
                or climate and "panel" not in self.control_kinds):
            raise ProtocolError("unsupported")
        self._color_channel = None
        self._range_channel = None
        self._detail_channel, self._detail_light, self._detail_climate = channel, bool(light), bool(climate)

    @property
    def light_color_version(self):
        return int(self.light_detail_version == 1 and self._color_channel == self.channel)

    def accept_color_features(self, channel):
        if (self.light_detail_version != 1 or channel != self.channel or self._selection is not None
                or self._opening is not None or self._service_task is not None and not self._service_task.done()
                or self._authorization_task is not None and not self._authorization_task.done()):
            raise ProtocolError("unsupported")
        self._color_channel = channel

    @property
    def climate_range_version(self):
        return int(self.climate_panel_version == 1 and self._range_channel == self.channel)

    def accept_range_features(self, channel):
        if (self.climate_panel_version != 1 or channel != self.channel or self._selection is not None
                or self._opening is not None or self._service_task is not None and not self._service_task.done()
                or self._authorization_task is not None and not self._authorization_task.done()):
            raise ProtocolError("unsupported")
        self._range_channel = channel

    @staticmethod
    def _detail(card):
        return card.get("action") in (LIGHT_ACTION, CLIMATE_ACTION)

    def _detail_domain(self, state):
        try:
            return DetailDomain.from_ha(self.hass, state, self._choice_language(), color=bool(self.light_color_version),
                                        range_enabled=bool(self.climate_range_version))
        except (DetailDomainError, NumericDomainError, ChoiceDomainError):
            raise ProtocolError("unsupported") from None

    def _entity_binding(self, card):
        if not self._detail(card):
            return super()._entity_binding(card)
        light = card["action"] == LIGHT_ACTION
        if (card.get("type") != "entity" or not isinstance(card.get("entity_id"), str)
                or card["entity_id"].partition(".")[0] != ("light" if light else "climate")
                or not (self.light_detail_version if light else self.climate_panel_version)):
            raise ProtocolError("unsupported")
        state = self.hass.states.get(card["entity_id"])
        if state is None or light and state.state not in {"on", "off"}:
            raise ProtocolError("entity_unavailable")
        return state, {"detail_domain": self._detail_domain(state)}

    def _binding(self, identity):
        state, card, caps = super()._binding(identity)
        if "token" not in identity and identity.get("control_kind") == "light":
            if (identity.get("detail_version") == 1) != (card["action"] == LIGHT_ACTION):
                raise ProtocolError("selection_changed")
        return state, card, caps

    def _capture_open(self, message, state, card, caps):
        if not self._detail(card):
            return super()._capture_open(message, state, card, caps)
        self._opening_detail = (self._open_generation, card["entity_id"], caps["detail_domain"])
        return self._opening_detail

    def _revalidate_open(self, captured, state, card, caps):
        if not self._detail(card):
            return super()._revalidate_open(captured, state, card, caps)
        if captured is not self._opening_detail or captured[2] != caps["detail_domain"]:
            raise ProtocolError("capabilities_changed")

    def _finish_open(self, captured):
        if captured is not None and captured is self._opening_detail:
            self._opening_detail = None
        return super()._finish_open(captured)

    def _observe_detail(self, selected, state, domain):
        observed = domain.command_state(state)
        current = selected.domain_state
        if current is None:
            current = selected.domain_state = DetailSelection(domain, observed)
        elif not isinstance(current, DetailSelection) or current.domain != domain:
            raise ProtocolError("capabilities_changed")
        elif current.observation != observed:
            if current.generation >= MAX_SEQUENCE:
                raise ProtocolError("expired")
            current.observation, current.generation = observed, current.generation + 1
        return current

    def observe_state_event(self, event=None):
        data = getattr(event, "data", {})
        entity, state = data.get("entity_id"), data.get("new_state")
        selected, opening = self._selection, self._opening_detail
        relevant = selected is not None and "detail_domain" in selected.caps and entity == selected.entity_id
        if not (relevant or opening and entity == opening[1]):
            return super().observe_state_event(event)
        try:
            if state is None or entity.startswith("light.") and state.state not in {"on", "off"}:
                raise ProtocolError("entity_unavailable")
            domain = self._detail_domain(state)
            if opening and entity == opening[1] and domain != opening[2]:
                raise ProtocolError("capabilities_changed")
            if relevant:
                self._observe_detail(selected, state, domain)
        except ProtocolError as error:
            self._opening_detail = None
            return self.revoke_now(str(error) if str(error) in CLOSE_REASONS else "capabilities_changed")
        return None

    def _selection_snapshot_fields(self, selected, state, card, caps):
        if "detail_domain" not in caps:
            return super()._selection_snapshot_fields(selected, state, card, caps)
        domain = caps["detail_domain"]
        current = self._observe_detail(selected, state, domain)
        title = plain_text(card.get("title") or state.attributes.get("friendly_name") or domain.family.title(), 40)
        title = "".join(char for char in title if char.isprintable() and not 0xD800 <= ord(char) <= 0xDFFF)
        while len(title.encode()) > 160:
            title = title[:-1]
        view = domain.view(state, current.facet, current.view_seq)
        if domain.family == "light":
            result = {"title": title, **domain.main(state), "light_detail": {
                "version": 1, "facets": domain.mask, "state_generation": current.generation, **view}}
            if current.facet == "color":
                result["light_color"] = domain.color.source(state)
            return result
        eligible = (1 if current.facet in {"main", "humidity", "range"} else 2) if view["editable"] else 0
        return {"title": title, "panel_type": "climate", "available": domain.known(state),
                "panel_caps": {"facets": domain.mask}, "panel_state": view,
                "eligible_actions": eligible, "state_generation": current.generation}

    async def async_handle(self, payload, context=None):
        message = self._decode(payload)
        if message["kind"] != "facet":
            return await super().async_handle(payload, context)
        selected = self._selection
        if (not self._connection_current() or not self.channel_ready or message["channel"] != self.channel):
            raise ProtocolError("connection_lost")
        if selected is None or any(message[key] != selected.identity[key] for key in self._selection_fields):
            raise ProtocolError("selection_changed")
        if self._principal(context) != selected.principal:
            raise ProtocolError("unauthorized")
        state, card, caps = self._valid_selection(selected)
        if "detail_domain" not in caps:
            raise ProtocolError("unsupported")
        current = self._observe_detail(selected, state, caps["detail_domain"])
        sequence, facet = message["view_seq"], message["facet"]

        async def receipt(status, reason="none", retain=True):
            value = self._envelope("facet_result", **selected.identity, view_seq=sequence, facet=facet,
                                   state_seq=selected.state_seq, status=status, reason=reason)
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
            self._observe_detail(selected, state, caps["detail_domain"])
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
        if "detail_domain" not in selected.caps:
            if "view_seq" in message:
                raise ProtocolError("unsupported")
            return super()._prepare_command(selected, message)
        state, _, caps = self._valid_selection(selected)
        current = self._observe_detail(selected, state, caps["detail_domain"])
        if current.pending is not None:
            raise ProtocolError("busy")
        if message.get("view_seq") != current.view_seq or message.get("expected_state_generation") != current.generation:
            raise ProtocolError("stale_state")
        domain, operation, facet = current.domain, message["op"], current.facet
        if operation == "facet_range":
            if domain.family != "climate" or facet != "range" or domain.range_domain is None or message.get("facet") != facet:
                raise ProtocolError("unsupported")
            try:
                target = domain.range_domain.target(message["target_low_index"], message["target_high_index"])
                domain.range_domain.service(state, *target)
            except (RangeDomainError, NumericDomainError):
                raise ProtocolError("unsupported") from None
            return (domain, current.observation, current.generation, facet, current.view_seq, operation,
                    target, domain.range_domain.context(state))
        if operation == "facet_color":
            if domain.family != "light" or facet != "color" or domain.color is None or message.get("facet") != facet:
                raise ProtocolError("unsupported")
            try:
                target = color_target(message["target_hue_milli"], message["target_saturation_milli"])
                domain.color.service(state, *target)
            except ColorDomainError:
                raise ProtocolError("unsupported") from None
            return (domain, current.observation, current.generation, facet, current.view_seq, operation,
                    target, state.attributes["brightness"])
        if operation in {"brightness", "turn_on", "turn_off"}:
            if domain.family != "light" or facet != "main":
                raise ProtocolError("unsupported")
            self._service_action(state, dict(domain.light_caps), message)
            target, index = message.get("value"), None
        else:
            index, known = domain.observed(state, facet)
            if message.get("facet") != facet or not known or message.get("expected_index") != index:
                raise ProtocolError("stale_state")
            target = message["target_index"]
            try:
                domain.service(state, facet, operation, target)
            except (DetailDomainError, NumericDomainError, ChoiceDomainError):
                raise ProtocolError("unsupported") from None
        return (domain, current.observation, current.generation, facet, current.view_seq, operation, target, index)

    def _validate_prepared(self, selected, record, state, caps):
        if "detail_domain" not in caps:
            return super()._validate_prepared(selected, record, state, caps)
        current = self._observe_detail(selected, state, caps["detail_domain"])
        if record.prepared[:5] != (current.domain, current.observation, current.generation, current.facet, current.view_seq):
            raise ProtocolError("stale_state")

    def _command_service_action(self, state, caps, record):
        if "detail_domain" not in caps:
            return super()._command_service_action(state, caps, record)
        domain, _, _, facet, _, operation, target, _ = record.prepared
        if operation == "facet_range":
            try:
                # Typed paired-target route; ordinary card service schemas stay unchanged.
                return "climate", "set_temperature", domain.range_domain.service(state, *target)
            except (RangeDomainError, NumericDomainError):
                raise ProtocolError("unsupported") from None
        if operation == "facet_color":
            try:
                # This typed path admits only HS plus captured brightness; the
                # ordinary card service-data allow-list remains unchanged.
                return "light", "turn_on", domain.color.service(state, *target)
            except ColorDomainError:
                raise ProtocolError("unsupported") from None
        if operation in {"brightness", "turn_on", "turn_off"}:
            return self._service_action(state, dict(domain.light_caps), record.payload)
        try:
            service_domain, service, values = domain.service(state, facet, operation, target)
            validate_live_action(self.hass, state, {"service": service_domain + "." + service, "data": values})
            return service_domain, service, values
        except ValueError:
            raise ProtocolError("unsupported") from None

    def _command_matches(self, selected, record):
        if "detail_domain" not in selected.caps:
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        domain, _, _, facet, _, operation, target, _ = record.prepared
        if domain != caps["detail_domain"]:
            raise ProtocolError("capabilities_changed")
        if operation == "facet_range":
            current = self._observe_detail(selected, state, domain)
            return ((not record.service_started or current.generation > record.prepared[2])
                    and domain.range_domain.matches(state, *target, record.prepared[7]))
        if operation == "facet_color":
            current = self._observe_detail(selected, state, domain)
            if not record.service_started:
                return domain.color.unchanged(state, *target)
            return (current.generation > record.prepared[2]
                    and domain.color.matches(state, *target, record.prepared[7]))
        if operation in {"brightness", "turn_on", "turn_off"}:
            return self._state_matches(state, dict(domain.light_caps), record.payload)
        index, known = domain.observed(state, facet)
        return known and index == target

    def _completed_service_status(self, selected, record):
        if "detail_domain" in selected.caps:
            return None
        return super()._completed_service_status(selected, record)

    async def _run_dispatch(self, selected, record, dispatch, context):
        if ("detail_domain" in selected.caps and record.prepared is not None
                and record.prepared[5] in {"facet_color", "facet_range"}):
            # create_task is a scheduling boundary. A fresh color/range
            # observation here prevents an external change being overwritten.
            if not self._record_current(selected, record):
                raise ProtocolError("selection_changed")
            state, _, caps = self._valid_selection(selected)
            self._validate_prepared(selected, record, state, caps)
        return await super()._run_dispatch(selected, record, dispatch, context)

    async def _send(self, value):
        selected = self._selection
        if (value.get("kind") == "result" and value.get("status") in TERMINAL and selected is not None
                and "detail_domain" in selected.caps
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
