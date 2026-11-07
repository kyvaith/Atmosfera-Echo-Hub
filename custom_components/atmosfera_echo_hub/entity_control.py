"""Opt-in generic Light/Number policy over one shared session and service fence."""

from __future__ import annotations

from typing import Any

from . import entity_control_codec as codec
from .control_session import CLOSE_REASONS, MAX_SEQUENCE, OPEN, SELECTION, TERMINAL, ProtocolError
from .light_control import LightControlOwner, decode as light_decode, encode as light_encode, envelope as light_envelope
from .numeric_domain import NumericDomain, NumericDomainError
from .number_domain import COLOR_TEMPERATURE_ACTION, COVER_POSITION_ACTION, COVER_TILT_ACTION, HUMIDITY_ACTION, TEMPERATURE_ACTION, number_domain, number_service, number_state, thermostat_snapshot
from .choice_control import ChoiceControlPolicy
from .cover_control import CoverControlPolicy
from .fan_control import FanControlPolicy
from .humidifier_control import HumidifierControlPolicy
from .robot_control import RobotControlPolicy
from .panel_control import PanelControlPolicy
from .detail_control import DetailControlPolicy
from .extra_panel_control import ExtraPanelPolicy
from .media_panel_control import MediaPanelPolicy
from .action_panel_control import ActionPanelPolicy
from .action_parameters_control import ActionParametersPolicy
from .datetime_panel_control import DatetimePanelPolicy
from .text_panel_control import TextPanelPolicy
from .agenda_control import AgendaControlPolicy
from .statistics_control import StatisticsControlPolicy
from .text import plain_text


class EntityControlOwner(StatisticsControlPolicy, AgendaControlPolicy, TextPanelPolicy, DatetimePanelPolicy, ActionParametersPolicy, ActionPanelPolicy, MediaPanelPolicy, ExtraPanelPolicy, DetailControlPolicy, PanelControlPolicy, RobotControlPolicy, HumidifierControlPolicy, FanControlPolicy, CoverControlPolicy, ChoiceControlPolicy, LightControlOwner):
    """A mode switch changes codec/policy, never allocates another owner or fence."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = "legacy"
        self._opening_domain = None
        self.control_kinds = ()
        self._cover_stop_channel = None
        self._cover_panel_channel = None
        self._empty_choice_channel = None
        self._thermostat_channel = None
        self._thermostat_dial = False

    def set_mode(self, mode: str) -> None:
        if mode not in {"legacy", "entity"}:
            raise ProtocolError("unsupported")
        if self._selection is not None or self.channel_ready:
            raise ProtocolError("selection_changed")
        self.mode = mode
        self._extra_channel, self._extra_profiles = None, ()
        self._panel_channel, self._panel_types = None, ()
        self._detail_channel = None
        self._detail_light = self._detail_climate = False
        self._color_channel = None
        self._agenda_channel = None
        self._statistics_channel = None
        self._action_parameters_channel = None
        self.control_kinds = ()
        self._cover_stop_channel = None
        self._cover_panel_channel = None
        self._empty_choice_channel = None
        self._thermostat_channel = None
        self._thermostat_dial = False
        self._open_fields = codec.OPEN if mode == "entity" else OPEN
        self._selection_fields = codec.SELECTION if mode == "entity" else SELECTION
        self._result_reasons = codec.RESULT_REASONS

    def prepare_bind(self, capability, *, epoch, runtime):
        self._cover_stop_channel = None
        self._cover_panel_channel = None
        self._empty_choice_channel = None
        self._thermostat_channel = None
        self._thermostat_dial = False
        message = self._decode(capability)
        result = super().prepare_bind(capability, epoch=epoch, runtime=runtime)
        self.control_kinds = tuple(message.get("control_kinds", ("light",)))
        return result

    @property
    def cover_stop_version(self):
        return int(self.mode == "entity" and self.channel_ready and "cover" in self.control_kinds
                   and self._cover_stop_channel == self.channel)

    def accept_cover_features(self, channel, version):
        if (type(version) is not int or version != 1 or self.mode != "entity" or not self.channel_ready
                or channel != self.channel or "cover" not in self.control_kinds
                or self._selection is not None or self._opening is not None):
            raise ProtocolError("unsupported")
        self._cover_stop_channel = channel

    @property
    def cover_panel_version(self):
        return int(self.cover_stop_version == 1 and self._cover_panel_channel == self.channel)

    def accept_cover_panel_features(self, channel, version):
        if (type(version) is not int or version != 1 or self.cover_stop_version != 1
                or channel != self.channel or self._selection is not None or self._opening is not None):
            raise ProtocolError("unsupported")
        self._cover_panel_channel = channel

    @property
    def empty_choice_version(self):
        return int(self.mode == "entity" and self.channel_ready and "choice" in self.control_kinds
                   and self._empty_choice_channel == self.channel)

    def accept_empty_choice_features(self, channel, version):
        if (type(version) is not int or version != 1 or self.mode != "entity" or not self.channel_ready
                or channel != self.channel or "choice" not in self.control_kinds
                or self._selection is not None or self._opening is not None):
            raise ProtocolError("unsupported")
        self._empty_choice_channel = channel

    def _decode(self, payload):
        return codec.decode(payload, empty_choice=bool(self.empty_choice_version),
                            extra_profiles=tuple(item["name"] for item in self.panel_extra_profiles),
                            action_dispatched={"name": "action", "version": 2} in self.panel_extra_profiles,
                            action_parameters=bool(self.action_parameters_version),
                            cover_panel=bool(self.cover_panel_version),
                            light_detail=bool(self.light_detail_version), climate_panel=bool(self.climate_panel_version), light_color=bool(self.light_color_version), climate_range=bool(self.climate_range_version), info_agenda=bool(self.info_agenda_version), info_statistics=bool(self.info_statistics_version),
                            thermostat_dial=self.thermostat_dial) if self.mode == "entity" else light_decode(payload)

    def _encode(self, value):
        return codec.encode(value, empty_choice=bool(self.empty_choice_version),
                            extra_profiles=tuple(item["name"] for item in self.panel_extra_profiles),
                            action_dispatched={"name": "action", "version": 2} in self.panel_extra_profiles,
                            action_parameters=bool(self.action_parameters_version),
                            cover_panel=bool(self.cover_panel_version),
                            light_detail=bool(self.light_detail_version), climate_panel=bool(self.climate_panel_version), light_color=bool(self.light_color_version), climate_range=bool(self.climate_range_version), info_agenda=bool(self.info_agenda_version), info_statistics=bool(self.info_statistics_version),
                            thermostat=self.thermostat_supported,
                            thermostat_dial=self.thermostat_dial) if self.mode == "entity" else light_encode(value)

    @property
    def thermostat_supported(self):
        return self.channel_ready and self._thermostat_channel == self.channel

    @property
    def thermostat_dial(self):
        return self.thermostat_supported and self._thermostat_dial

    def accept_thermostat_features(self, channel, *, dial=False):
        if self.mode == "entity" and self.channel_ready and channel == self.channel and "number" in self.control_kinds:
            self._thermostat_channel = channel
            self._thermostat_dial = dial

    def _envelope(self, kind, **fields):
        return codec.envelope(kind, **fields) if self.mode == "entity" else light_envelope(kind, **fields)

    @staticmethod
    def _number(card):
        return card.get("action") in ({"kind": "control", "control": "number"}, TEMPERATURE_ACTION, HUMIDITY_ACTION, COLOR_TEMPERATURE_ACTION, COVER_POSITION_ACTION, COVER_TILT_ACTION)

    def _entity_binding(self, card):
        if not self._number(card):
            return super()._entity_binding(card)
        entity_id = card.get("entity_id")
        if self.mode != "entity" or not isinstance(entity_id, str):
            raise ProtocolError("unsupported")
        state = self.hass.states.get(entity_id)
        if state is None:
            raise ProtocolError("entity_unavailable")
        property = card["action"].get("property")
        thermostat = self.thermostat_supported and card["action"] == TEMPERATURE_ACTION
        try:
            domain = self._numeric_binding(state, property, thermostat)
        except NumericDomainError:
            raise ProtocolError("unsupported") from None
        return state, {"domain": domain, **({"number_property": property} if property else {}),
                       **({"thermostat": True} if thermostat else {})}

    def _numeric_binding(self, state, property, thermostat):
        if thermostat and thermostat_snapshot(self.hass, state) is None:
            raise NumericDomainError("thermostat_unsupported")
        try:
            domain, service, _ = number_service(state.entity_id, property)
            if not self.hass.services.has_service(domain, service):
                raise NumericDomainError("service_unsupported")
            return number_domain(self.hass, state, property)
        except NumericDomainError:
            if not thermostat:
                raise
            return None

    def _binding(self, identity):
        state, card, caps = super()._binding(identity)
        expected = "panel" if self._panel(card) else "robot" if self._robot(card) else "humidifier" if self._humidifier(card) else "fan" if self._fan(card) else "number" if self._number(card) else "choice" if self._choice(card) else "cover" if self._cover(card) else "light"
        if self.mode == "entity" and identity["control_kind"] != expected:
            raise ProtocolError("selection_changed")
        return state, card, caps

    def _capture_open(self, message, state, card, caps):
        self._opening_domain = ((self._open_generation, card["entity_id"], caps)
                                if self._number(card) else None)
        return self._opening_domain if self._number(card) else super()._capture_open(message, state, card, caps)

    def _revalidate_open(self, captured, state, card, caps):
        if not self._number(card):
            return super()._revalidate_open(captured, state, card, caps)
        if captured is not None and (captured is not self._opening_domain or caps != captured[2]):
            raise ProtocolError("capabilities_changed")

    def _finish_open(self, captured):
        # This call owns only the guard it captured. An older authorization's
        # late finally must never clear a superseding open's metadata guard.
        if captured is self._opening_domain:
            self._opening_domain = None
        else:
            super()._finish_open(captured)

    @staticmethod
    def _observed(domain: NumericDomain | None, state: Any, property=None):
        index = domain.observed_index(number_state(state, property)) if domain is not None else None
        return index, index is not None

    def _observe_number(self, selected, state, domain):
        index, available = self._observed(domain, state, selected.caps.get("number_property"))
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
            return super().observe_state_event(event)
        try:
            if state is None:
                raise ProtocolError("entity_unavailable")
            caps = selected.caps if selected_number and entity_id == selected.entity_id else opening[2]
            domain = self._numeric_binding(state, caps.get("number_property"), caps.get("thermostat", False))
            if opening and entity_id == opening[1] and domain != opening[2]["domain"]:
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
        view = thermostat_snapshot(self.hass, state) if caps.get("thermostat") else None
        if view is not None and self.thermostat_dial:
            view["dial"] = True
        return {"title": title, "domain": domain.descriptor() if domain is not None else None, "index": index,
                "available": available, "value_text": str(domain.value_at(index)) if available else "--",
                "state_generation": generation,
                **({"thermostat": view} if view is not None else {})}

    def _prepare_command(self, selected, message):
        if selected.identity.get("control_kind") != "number":
            return super()._prepare_command(selected, message)
        state, _, caps = self._valid_selection(selected)
        domain, index, available, generation = self._observe_number(selected, state, caps["domain"])
        if not available or message["expected_index"] != index or message["expected_state_generation"] != generation:
            raise ProtocolError("stale_state")
        if message["op"] == "set_target":
            if not self.thermostat_dial or not caps.get("thermostat"):
                raise ProtocolError("unsupported")
            target = message["target_index"]
        else:
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
        if record.payload.get("control_kind") != "number" or record.prepared is None:
            return super()._command_service_action(state, caps, record)
        domain, _, _, target = record.prepared
        try:
            service_domain, service, field = number_service(state.entity_id, caps.get("number_property"))
            if not self.hass.services.has_service(service_domain, service):
                raise ProtocolError("unsupported")
            value = domain.service_value(target, current=caps["domain"])
        except NumericDomainError:
            raise ProtocolError("unsupported") from None
        return service_domain, service, {field: value}

    def _command_matches(self, selected, record):
        if selected.identity.get("control_kind") != "number" or record.prepared is None:
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        # After dispatch compare the captured target; our own state change must
        # not be rejected by the earlier expected-index/generation predicate.
        domain, _, _, target = record.prepared
        return domain == caps["domain"] and domain.observed_index(number_state(state, caps.get("number_property"))) == target

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
