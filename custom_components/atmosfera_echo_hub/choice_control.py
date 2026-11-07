"""Choice policy hooks over the existing single control session and service fence."""

from .choice_domain import ChoiceDomainError, choice_domain, choice_is_empty, choice_service, choice_state
from .control_session import CLOSE_REASONS, MAX_SEQUENCE, TERMINAL, ProtocolError
from .cards import choice_control_labels, validate_live_action
from .text import plain_text


class ChoiceControlPolicy:
    """Domain policy only; no second session, queue, timer or task owner."""

    def __init__(self, *args, choice_language=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._opening_choice = None
        self._choice_language = choice_language or (lambda: self.hass.config.language)

    @staticmethod
    def _choice(card):
        return card.get("action") in ({"kind": "control", "control": "choice"},
                                      {"kind": "control", "control": "choice", "property": "activity"},
                                      {"kind": "control", "control": "choice", "property": "source"},
                                      {"kind": "control", "control": "choice", "property": "sound_mode"},
                                      {"kind": "control", "control": "choice", "property": "repeat"},
                                      {"kind": "control", "control": "choice", "property": "fan_speed"},
                                      {"kind": "control", "control": "choice", "property": "percentage"},
                                      {"kind": "control", "control": "choice", "property": "effect"},
                                      {"kind": "control", "control": "choice", "property": "direction"},
                                      {"kind": "control", "control": "choice", "property": "hvac_mode"},
                                      {"kind": "control", "control": "choice", "property": "preset_mode"},
                                      {"kind": "control", "control": "choice", "property": "fan_mode"},
                                      {"kind": "control", "control": "choice", "property": "swing_mode"},
                                      {"kind": "control", "control": "choice", "property": "swing_horizontal_mode"},
                                      {"kind": "control", "control": "choice", "property": "mode"})

    def _entity_binding(self, card):
        if not self._choice(card):
            return super()._entity_binding(card)
        entity = card.get("entity_id")
        if (
            self.mode != "entity"
            or "choice" not in self.control_kinds
            or card.get("type") != "entity"
            or not isinstance(entity, str)
            or entity.partition(".")[0] not in {"select", "input_select", "fan", "climate", "humidifier", "light", "vacuum", "remote", "media_player"}
        ):
            raise ProtocolError("unsupported")
        state = self.hass.states.get(entity)
        if state is None or (entity.startswith("media_player.") and state.state not in {"on", "idle", "playing", "paused", "buffering"}) or (entity.startswith("remote.") and state.state not in {"on", "off"}):
            raise ProtocolError("entity_unavailable")
        try:
            property = card["action"].get("property")
            service, _ = choice_service(entity, property)
            if not self.hass.services.has_service(entity.partition(".")[0], service):
                raise ProtocolError("unsupported")
            domain = choice_domain(entity, state.attributes, property, hass=self.hass)
        except ChoiceDomainError:
            raise ProtocolError("unsupported") from None
        caps = {"choice_domain": domain}
        if property is not None:
            caps.update(choice_property=property, choice_labels=choice_control_labels(self.hass, state, domain, property, self._choice_language()))
        return state, caps

    def _capture_open(self, message, state, card, caps):
        if not self._choice(card):
            return super()._capture_open(message, state, card, caps)
        self._opening_choice = (
            self._open_generation,
            card["entity_id"],
            caps,
        )
        return self._opening_choice

    def _revalidate_open(self, captured, state, card, caps):
        if not self._choice(card):
            return super()._revalidate_open(captured, state, card, caps)
        if captured is not self._opening_choice or caps != captured[2]:
            raise ProtocolError("capabilities_changed")

    def _finish_open(self, captured):
        if captured is not None and captured is self._opening_choice:
            self._opening_choice = None
        return super()._finish_open(captured)

    def _observe_choice(self, selected, state, domain):
        property = selected.caps.get("choice_property")
        index = domain.observed_index(choice_state(state.entity_id, state.state, state.attributes, property))
        available = index is not None or bool(self.empty_choice_version and choice_is_empty(
            state.entity_id, state.state, state.attributes, property))
        previous = selected.domain_state
        if previous is None:
            selected.domain_state = (domain, index, available, 1)
        elif previous[0] != domain:
            raise ProtocolError("capabilities_changed")
        elif previous[1:3] != (index, available):
            if previous[3] >= MAX_SEQUENCE:
                raise ProtocolError("expired")
            selected.domain_state = (domain, index, available, previous[3] + 1)
        return selected.domain_state

    def observe_state_event(self, event=None):
        if event is None:
            return None
        data = getattr(event, "data", {})
        entity, state = data.get("entity_id"), data.get("new_state")
        selected, opening = self._selection, self._opening_choice
        selected_choice = (
            selected is not None and selected.identity.get("control_kind") == "choice"
        )
        if not (
            (selected_choice and entity == selected.entity_id)
            or (opening and entity == opening[1])
        ):
            return None
        try:
            if state is None:
                raise ProtocolError("entity_unavailable")
            caps = selected.caps if selected_choice and entity == selected.entity_id else opening[2]
            domain = choice_domain(state.entity_id, state.attributes, caps.get("choice_property"), hass=self.hass)
            if opening and entity == opening[1] and domain != opening[2]["choice_domain"]:
                raise ProtocolError("capabilities_changed")
            if selected_choice and entity == selected.entity_id:
                self._observe_choice(selected, state, domain)
        except (ChoiceDomainError, ProtocolError) as error:
            self._opening_choice = None
            return self.revoke_now(
                str(error)
                if isinstance(error, ProtocolError)
                else "capabilities_changed"
            )
        return None

    def _selection_snapshot_fields(self, selected, state, card, caps):
        if selected.identity.get("control_kind") != "choice":
            return super()._selection_snapshot_fields(selected, state, card, caps)
        domain, index, available, generation = self._observe_choice(
            selected, state, caps["choice_domain"]
        )
        title = plain_text(
            card.get("title") or state.attributes.get("friendly_name") or "Select", 40
        )
        title = "".join(
            c for c in title if c.isprintable() and not 0xD800 <= ord(c) <= 0xDFFF
        )
        while len(title.encode()) > 160:
            title = title[:-1]
        return {
            "title": title,
            "options": list(caps.get("choice_labels", domain.options)),
            "index": index,
            "available": available,
            "state_generation": generation,
        }

    def _prepare_command(self, selected, message):
        if selected.identity.get("control_kind") != "choice":
            return super()._prepare_command(selected, message)
        state, _, caps = self._valid_selection(selected)
        domain, index, available, generation = self._observe_choice(
            selected, state, caps["choice_domain"]
        )
        if (
            not available
            or message["expected_index"] != index
            or message["expected_state_generation"] != generation
        ):
            raise ProtocolError("stale_state")
        try:
            domain.value_at(message["target_index"])
        except ChoiceDomainError:
            raise ProtocolError("unsupported") from None
        return domain, index, generation, message["target_index"]

    def _validate_prepared(self, selected, record, state, caps):
        if selected.identity.get("control_kind") != "choice":
            return super()._validate_prepared(selected, record, state, caps)
        domain, index, available, generation = self._observe_choice(
            selected, state, caps["choice_domain"]
        )
        if (
            not available
            or record.prepared is None
            or (domain, index, generation) != record.prepared[:3]
        ):
            raise ProtocolError("stale_state")

    def _command_service_action(self, state, caps, record):
        if record.payload.get("control_kind") != "choice":
            return super()._command_service_action(state, caps, record)
        domain, _, _, target = record.prepared
        try:
            option = domain.service_value(target, current=caps["choice_domain"])
        except ChoiceDomainError:
            raise ProtocolError("capabilities_changed") from None
        entity_domain = state.entity_id.partition(".")[0]
        service, field = choice_service(state.entity_id, caps.get("choice_property"))
        action = {
            "service": entity_domain + "." + service,
            "data": {field: int(option) if caps.get("choice_property") == "percentage" else option},
        }
        try:
            validate_live_action(self.hass, state, action)
        except ValueError:
            raise ProtocolError("unsupported") from None
        return entity_domain, service, action["data"]

    def _command_matches(self, selected, record):
        if selected.identity.get("control_kind") != "choice":
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        domain, _, _, target = record.prepared
        return (
            domain == caps["choice_domain"]
            and domain.observed_index(choice_state(state.entity_id, state.state, state.attributes, caps.get("choice_property"))) == target
        )

    async def _send(self, value):
        selected = self._selection
        if (
            value.get("kind") == "result"
            and value.get("status") in TERMINAL
            and value.get("control_kind") == "choice"
            and selected is not None
            and all(
                value.get(key) == selected.identity[key]
                for key in self._selection_fields
            )
        ):
            try:
                state, card, _ = self._valid_selection(selected)
            except ProtocolError as error:
                await self.async_close(
                    str(error)
                    if str(error) in CLOSE_REASONS
                    else "capabilities_changed"
                )
                return value
            await self._snapshot(selected, "state", state, card)
            if selected is not self._selection:
                raise ProtocolError("selection_changed")
            value["state_seq"] = selected.state_seq
        return await super()._send(value)
