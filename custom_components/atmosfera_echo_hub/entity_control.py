"""Opt-in generic Light/Number policy over one shared session and service fence."""

from __future__ import annotations

from typing import Any

from . import entity_control_codec as codec
from .control_session import CLOSE_REASONS, MAX_SEQUENCE, OPEN, SELECTION, TERMINAL, ProtocolError
from .light_control import LightControlOwner, decode as light_decode, encode as light_encode, envelope as light_envelope
from .numeric_domain import NumericDomain, NumericDomainError
from .text import plain_text


class EntityControlOwner(LightControlOwner):
    """A mode switch changes codec/policy, never allocates another owner or fence."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = "legacy"
        self._opening_domain = None

    def set_mode(self, mode: str) -> None:
        if mode not in {"legacy", "entity"}:
            raise ProtocolError("unsupported")
        if self._selection is not None or self.channel_ready:
            raise ProtocolError("selection_changed")
        self.mode = mode
        self._open_fields = codec.OPEN if mode == "entity" else OPEN
        self._selection_fields = codec.SELECTION if mode == "entity" else SELECTION
        self._result_reasons = codec.RESULT_REASONS

    def _decode(self, payload):
        return codec.decode(payload) if self.mode == "entity" else light_decode(payload)

    def _encode(self, value):
        return codec.encode(value) if self.mode == "entity" else light_encode(value)

    def _envelope(self, kind, **fields):
        return codec.envelope(kind, **fields) if self.mode == "entity" else light_envelope(kind, **fields)

    @staticmethod
    def _number(card):
        return card.get("action") == {"kind": "control", "control": "number"}

    def _entity_binding(self, card):
        if not self._number(card):
            return super()._entity_binding(card)
        entity_id = card.get("entity_id")
        if self.mode != "entity" or not isinstance(entity_id, str) or not entity_id.startswith("input_number."):
            raise ProtocolError("unsupported")
        state = self.hass.states.get(entity_id)
        if state is None:
            raise ProtocolError("entity_unavailable")
        if not self.hass.services.has_service("input_number", "set_value"):
            raise ProtocolError("unsupported")
        try:
            domain = NumericDomain.from_ha(state.attributes)
        except NumericDomainError:
            raise ProtocolError("unsupported") from None
        return state, {"domain": domain}

    def _binding(self, identity):
        state, card, caps = super()._binding(identity)
        if self.mode == "entity" and identity["control_kind"] != ("number" if self._number(card) else "light"):
            raise ProtocolError("selection_changed")
        return state, card, caps

    def _capture_open(self, message, state, card, caps):
        self._opening_domain = ((self._open_generation, card["entity_id"], caps["domain"])
                                if self._number(card) else None)
        return self._opening_domain

    def _revalidate_open(self, captured, state, card, caps):
        if captured is not None and (captured is not self._opening_domain or caps.get("domain") != captured[2]):
            raise ProtocolError("capabilities_changed")

    def _finish_open(self, captured):
        # This call owns only the guard it captured. An older authorization's
        # late finally must never clear a superseding open's metadata guard.
        if captured is self._opening_domain:
            self._opening_domain = None

    @staticmethod
    def _observed(domain: NumericDomain, state: Any):
        index = domain.observed_index(state.state)
        return index, index is not None

    def _observe_number(self, selected, state, domain):
        index, available = self._observed(domain, state)
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
        """Observe the one selected entity synchronously, before transport coalescing.

        Only the current selection/opening owns this bounded observation. Values
        A-B-A advance twice; metadata A-B-A detaches at B and cannot revive a token.
        """
        if event is None:
            return None
        data = getattr(event, "data", {})
        entity_id, state = data.get("entity_id"), data.get("new_state")
        selected = self._selection
        opening = self._opening_domain
        selected_number = selected is not None and selected.identity.get("control_kind") == "number"
        relevant = (selected_number and entity_id == selected.entity_id) or (opening and entity_id == opening[1])
        if not relevant:
            return None
        try:
            if state is None:
                raise ProtocolError("entity_unavailable")
            domain = NumericDomain.from_ha(state.attributes)
            if opening and entity_id == opening[1] and domain != opening[2]:
                raise ProtocolError("capabilities_changed")
            if selected_number and entity_id == selected.entity_id:
                if domain != selected.caps["domain"]:
                    raise ProtocolError("capabilities_changed")
                self._observe_number(selected, state, domain)
        except (NumericDomainError, ProtocolError) as error:
            reason = str(error) if isinstance(error, ProtocolError) else "capabilities_changed"
            self._opening_domain = None
            return self.revoke_now(reason)
        return None

    def _selection_snapshot_fields(self, selected, state, card, caps):
        if selected.identity.get("control_kind") != "number":
            return super()._selection_snapshot_fields(selected, state, card, caps)
        domain, index, available, generation = self._observe_number(selected, state, caps["domain"])
        title = plain_text(card.get("title") or state.attributes.get("friendly_name") or "Number", 40)
        title = "".join(c for c in title if c.isprintable() and not 0xD800 <= ord(c) <= 0xDFFF)
        while len(title.encode()) > 160:
            title = title[:-1]
        return {"title": title, "domain": domain.descriptor(), "index": index,
                "available": available, "value_text": str(domain.value_at(index)) if available else "--",
                "state_generation": generation}

    def _prepare_command(self, selected, message):
        if selected.identity.get("control_kind") != "number":
            return super()._prepare_command(selected, message)
        state, _, caps = self._valid_selection(selected)
        domain, index, available, generation = self._observe_number(selected, state, caps["domain"])
        if not available or message["expected_index"] != index or message["expected_state_generation"] != generation:
            raise ProtocolError("stale_state")
        target = domain.adjacent_index(index, message["direction"])
        if target == index:
            raise ProtocolError("unsupported")
        # Convert now and again after authorization, before the sole absolute call.
        try:
            domain.service_value(target, current=domain)
        except NumericDomainError:
            raise ProtocolError("unsupported") from None
        return (domain, index, generation, target)

    def _validate_prepared(self, selected, record, state, caps):
        if selected.identity.get("control_kind") != "number":
            return super()._validate_prepared(selected, record, state, caps)
        domain, index, available, generation = self._observe_number(selected, state, caps["domain"])
        captured = record.prepared
        if captured is None or (domain, index, generation) != captured[:3] or not available:
            raise ProtocolError("stale_state")

    def _command_service_action(self, state, caps, record):
        if record.prepared is None:
            return super()._command_service_action(state, caps, record)
        domain, _, _, target = record.prepared
        if not self.hass.services.has_service("input_number", "set_value"):
            raise ProtocolError("unsupported")
        try:
            value = domain.service_value(target, current=caps["domain"])
        except NumericDomainError:
            raise ProtocolError("unsupported") from None
        return "input_number", "set_value", {"value": value}

    def _command_matches(self, selected, record):
        if record.prepared is None:
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        # After dispatch compare the captured target; our own state change must
        # not be rejected by the earlier expected-index/generation predicate.
        domain, _, _, target = record.prepared
        return domain == caps["domain"] and domain.observed_index(state.state) == target

    async def _send(self, value):
        selected = self._selection
        if (value.get("kind") == "result" and value.get("status") in TERMINAL
                and value.get("control_kind") == "number" and selected is not None
                and all(value.get(key) == selected.identity[key] for key in self._selection_fields)):
            try:
                state, card, _ = self._valid_selection(selected)
            except ProtocolError as error:
                # An expired/revoked selection needs its close, never a new
                # snapshot or a terminal result that could revive stale input.
                reason = str(error) if str(error) in CLOSE_REASONS else "capabilities_changed"
                await self.async_close(reason)
                return value
            await self._snapshot(selected, "state", state, card)
            if selected is not self._selection:
                raise ProtocolError("selection_changed")
            value["state_seq"] = selected.state_seq
        return await super()._send(value)
