"""Info read admission and lock-only actions over the one existing Panel owner."""

from .control_session import MAX_SEQUENCE, ProtocolError
from .extra_panel_domain import CONTEXT_INFO_TYPES, EXTRA_DOMAINS, INFO_ACTION, LOCK_ACTION, ExtraDomain, ExtraObservation, ExtraPanelError
from .extra_panel_features import PROFILES, valid_profiles
from .layout import LayoutError, validate_action


async def _deny_read(context, entity_id):
    return False


class ExtraPanelPolicy:
    def __init__(self, *args, authorize_read=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.authorize_read = authorize_read or _deny_read
        self._extra_channel, self._extra_profiles = None, ()

    def prepare_bind(self, *args, **kwargs):
        self._extra_channel, self._extra_profiles = None, ()
        return super().prepare_bind(*args, **kwargs)

    @property
    def panel_extra_profiles(self):
        return [dict(profile) for profile in self._extra_profiles] if (
            self.mode == "entity" and self.channel_ready and self._extra_channel == self.channel
            and "panel" in self.control_kinds) else []

    def accept_extra_features(self, channel, profiles):
        if (self.mode != "entity" or not self.channel_ready or channel != self.channel
                or "panel" not in self.control_kinds or self._selection is not None or self._opening is not None
                or self._service_task is not None and not self._service_task.done()
                or not valid_profiles(profiles, empty=False) or any(item not in PROFILES for item in profiles)):
            raise ProtocolError("unsupported")
        self._extra_channel, self._extra_profiles = channel, tuple(dict(profile) for profile in profiles)

    @staticmethod
    def _extra(card):
        return card.get("action") in (INFO_ACTION, LOCK_ACTION)

    def _authorization_policy(self, card):
        return self.authorize_read if card.get("action") == INFO_ACTION else super()._authorization_policy(card)

    def _panel_domain(self, state, card):
        if not self._extra(card):
            return super()._panel_domain(state, card)
        try:
            domain = ExtraDomain.from_ha(self.hass, state)
            if domain.family != card["action"]["property"] or {"name": domain.family, "version": 1} not in self.panel_extra_profiles:
                raise ExtraPanelError("family")
            if domain.info_type in CONTEXT_INFO_TYPES and {"name": "info_context", "version": 1} not in self.panel_extra_profiles:
                raise ExtraPanelError("info_context")
            return domain
        except ExtraPanelError:
            raise ProtocolError("unsupported") from None

    def _entity_binding(self, card):
        if not self._extra(card):
            return super()._entity_binding(card)
        entity = card.get("entity_id")
        family = card["action"]["property"]
        if (not isinstance(entity, str) or entity.partition(".")[0] not in EXTRA_DOMAINS[family]
                or card.get("type") not in ({"sensor", "entity"} if family == "info" else {"entity"})):
            raise ProtocolError("unsupported")
        try:
            validate_action(card["action"], entity, layout_version=3)
        except LayoutError:
            raise ProtocolError("unsupported") from None
        state = self.hass.states.get(entity)
        if state is None:
            raise ProtocolError("entity_unavailable")
        return state, {"panel_domain": self._panel_domain(state, card)}

    def _observe_panel(self, selected, state, domain):
        if not isinstance(domain, ExtraDomain):
            return super()._observe_panel(selected, state, domain)
        observed = ExtraObservation.from_ha(self.hass, state, domain, self._choice_language())
        previous = selected.domain_state
        generation = previous[2] if previous else 1
        if previous and previous[0] != domain:
            raise ProtocolError("capabilities_changed")
        if previous and previous[1].command_state != observed.command_state:
            if generation >= MAX_SEQUENCE:
                raise ProtocolError("expired")
            generation += 1
        selected.domain_state = (domain, observed, generation)
        return selected.domain_state

    def _prepare_command(self, selected, message):
        if (selected.identity.get("control_kind") == "panel" and isinstance(selected.caps.get("panel_domain"), ExtraDomain)
                and selected.caps["panel_domain"].family == "info"):
            raise ProtocolError("unsupported")
        return super()._prepare_command(selected, message)

    def _command_matches(self, selected, record):
        domain = selected.caps.get("panel_domain")
        if not isinstance(domain, ExtraDomain):
            return super()._command_matches(selected, record)
        state, _, caps = self._valid_selection(selected)
        current, observed, generation = self._observe_panel(selected, state, caps["panel_domain"])
        expected, _, prepared_generation, operation, target = record.prepared
        return (domain.family == "lock" and current == expected and record.service_started
                and generation > prepared_generation and observed.matches(operation, target))
