"""One bounded Recorder read on the existing Info selection and refresh path."""

from dataclasses import dataclass
from datetime import datetime, timezone

from .control_session import MAX_SEQUENCE, ProtocolError
from .layout import LayoutError, validate_action
from .statistics_domain import (ACTION, ERRORS, UNSUPPORTED, StatisticsDomain,
    StatisticsError, StatisticsObservation, current_status, fields_for, window_end)
from .statistics_recorder import ready_recorder, read_dataset


@dataclass
class StatisticsSelection:
    domain: StatisticsDomain
    end_hour: int
    fields: dict
    started: float
    generation: int = 1
    digest: str = ""
    submitted: bool = False
    completed: object = None
    invalid: bool = False


class StatisticsControlPolicy:
    def __init__(self, *args, statistics_changed=None, statistics_now=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._statistics_channel = None
        self._statistics_changed = statistics_changed or (lambda: None)
        self._statistics_now = statistics_now or (lambda: datetime.now(timezone.utc))
        # This is the ORIGINAL executor future, never an await/timeout wrapper.
        # It outlives a closed selection and is never cancelled by this policy.
        self._statistics_job = None

    def prepare_bind(self, *args, **kwargs):
        self._statistics_channel = None
        return super().prepare_bind(*args, **kwargs)

    @property
    def info_statistics_version(self):
        return int(self.mode == "entity" and self.channel_ready and self._statistics_channel == self.channel
                   and {"name": "info", "version": 1} in self.panel_extra_profiles)

    def accept_statistics_features(self, channel):
        if (channel != self.channel or not self.channel_ready or self.mode != "entity"
                or {"name": "info", "version": 1} not in self.panel_extra_profiles
                or self._selection is not None or self._opening is not None
                or self._service_task is not None and not self._service_task.done()
                or self._authorization_task is not None and not self._authorization_task.done()):
            raise ProtocolError("unsupported")
        self._statistics_channel = channel

    def _authorization_policy(self, card):
        return self.authorize_read if card.get("action") == ACTION else super()._authorization_policy(card)

    def _panel_domain(self, state, card):
        if card.get("action") != ACTION:
            return super()._panel_domain(state, card)
        if self.info_statistics_version != 1:
            raise ProtocolError("unsupported")
        try:
            return StatisticsDomain.from_ha(self.hass, state)
        except StatisticsError:
            raise ProtocolError("entity_unavailable") from None

    def _entity_binding(self, card):
        if card.get("action") != ACTION:
            return super()._entity_binding(card)
        entity_id = card.get("entity_id")
        if (card.get("type") not in ("sensor", "entity") or not isinstance(entity_id, str)
                or not entity_id.startswith("sensor.")):
            raise ProtocolError("unsupported")
        try:
            validate_action(card["action"], entity_id, layout_version=3)
        except LayoutError:
            raise ProtocolError("unsupported") from None
        state = self.hass.states.get(entity_id)
        if state is None:
            raise ProtocolError("entity_unavailable")
        return state, {"panel_domain": self._panel_domain(state, card)}

    def _valid_selection(self, selected):
        state, card, caps = super()._valid_selection(selected)
        if isinstance(selected.domain_state, StatisticsSelection):
            self._observe_panel(selected, state, caps["panel_domain"])
        return state, card, caps

    def _statistics_replace(self, current, fields, digest=None):
        new_digest = current.digest if digest is None else digest
        if fields != current.fields or new_digest != current.digest:
            if current.generation >= MAX_SEQUENCE:
                current.invalid = True
                raise ProtocolError("expired")
            current.generation += 1
            current.fields, current.digest = fields, new_digest

    def _statistics_error(self, current, reason):
        if reason not in UNSUPPORTED | ERRORS:
            reason = "read_failed"
        fields = fields_for(current.domain, current.end_hour, current.fields["current_status"],
                            status="unsupported" if reason in UNSUPPORTED else "error", reason=reason)
        self._statistics_replace(current, fields)

    def _observe_panel(self, selected, state, domain):
        if not isinstance(domain, StatisticsDomain):
            return super()._observe_panel(selected, state, domain)
        current = selected.domain_state
        source = current_status(state)
        if current is None:
            end_hour = window_end(self._statistics_now())
            fields = fields_for(domain, end_hour, source,
                status="loading" if domain.arithmetic else "unsupported",
                reason="none" if domain.arithmetic else "not_arithmetic")
            current = selected.domain_state = StatisticsSelection(domain, end_hour, fields, self.clock())
        elif not isinstance(current, StatisticsSelection) or current.domain != domain:
            raise ProtocolError("capabilities_changed")
        elif current.invalid:
            raise ProtocolError("expired")
        else:
            self._statistics_replace(current, current.fields | {"current_status": source})
            if current.fields["status"] == "loading" and current.submitted and self.clock() - current.started >= 10 and current.completed is None:
                self._statistics_error(current, "read_timeout")
        return domain, StatisticsObservation(current.fields), current.generation

    def _submit_statistics(self, selected, current):
        current.submitted = True
        if self._statistics_job is not None:
            self._statistics_error(current, "busy")
            self._statistics_changed()
            return
        try:
            instance = ready_recorder(self.hass)
            current.started = self.clock()
            future = instance.async_add_executor_job(read_dataset, instance, selected.entity_id, current.end_hour, current.domain.unit)
        except StatisticsError as error:
            self._statistics_error(current, str(error))
            self._statistics_changed()
            return
        except Exception:
            self._statistics_error(current, "read_failed")
            self._statistics_changed()
            return
        self._statistics_job = future

        def completed(job):
            # Retrieve every outcome, even after close/unload. Do not cancel this
            # future: cancellation would not stop an already-running DB worker.
            try:
                outcome = (None, "read_failed") if job.cancelled() else (job.result(), None)
            except StatisticsError as error:
                outcome = None, str(error)
            except Exception:
                outcome = None, "read_failed"
            if self._statistics_job is job:
                self._statistics_job = None
            if selected is not self._selection or selected.domain_state is not current:
                return
            if self.clock() - current.started >= 10 or current.fields["status"] != "loading":
                current.completed = None, "read_timeout"
            else:
                current.completed = outcome
            # Existing coalesced refresh reauthorizes before consuming/publishing.
            self._statistics_changed()

        future.add_done_callback(completed)

    async def _snapshot(self, selected, kind, state, card):
        current = selected.domain_state
        if selected is self._selection and isinstance(current, StatisticsSelection) and current.completed is not None:
            self._valid_selection(selected)  # Caller has freshly reauthorized.
            dataset, reason = current.completed
            current.completed = None
            if reason:
                self._statistics_error(current, reason)
            else:
                fields = fields_for(current.domain, current.end_hour, current_status(state))
                fields.update(dataset.fields)
                self._statistics_replace(current, fields, dataset.digest)
        result = await super()._snapshot(selected, kind, state, card)
        current = selected.domain_state
        if (kind == "grant" and selected is self._selection and isinstance(current, StatisticsSelection)
                and current.fields["status"] == "loading" and not current.submitted):
            # The grant send itself awaited. Reauthorize and capture the same
            # source before the first and only database submission.
            allowed = await self._authorized(selected.context, selected.entity_id, authorizer=self.authorize_read)
            if selected is not self._selection:
                return result
            if not allowed:
                await self.async_close("selection_changed")
                return result
            self._valid_selection(selected)
            self._submit_statistics(selected, current)
        return result

    def _detach_selection(self, reason):
        selected = self._selection
        current = selected.domain_state if selected is not None else None
        if isinstance(current, StatisticsSelection):
            current.completed = None
            current.fields.clear()
            current.digest = ""
        return super()._detach_selection(reason)

    def _prepare_command(self, selected, message):
        if isinstance(selected.caps.get("panel_domain"), StatisticsDomain):
            raise ProtocolError("unsupported")
        return super()._prepare_command(selected, message)

    def observe_robot_registry_event(self, event):
        selected, opening = self._selection, self._opening_panel
        if (selected is not None and isinstance(selected.caps.get("panel_domain"), StatisticsDomain)
                or opening is not None and isinstance(opening[2], StatisticsDomain)):
            data = getattr(event, "data", {})
            changes = data.get("changes") or {}
            entity_id = selected.entity_id if selected is not None else opening[1]
            if entity_id in {data.get("entity_id"), changes.get("entity_id")} and (data.get("action") in {"create", "remove"}
                    or {"disabled_by", "entity_id", "device_id", "unique_id", "platform", "config_entry_id"}.intersection(changes)):
                return self.revoke_now("capabilities_changed")
        return super().observe_robot_registry_event(event)

    def observe_statistics_zone_event(self, event):
        selected, opening = self._selection, self._opening_panel
        if (selected is not None and isinstance(selected.caps.get("panel_domain"), StatisticsDomain)
                or opening is not None and isinstance(opening[2], StatisticsDomain)):
            if "time_zone" in getattr(event, "data", {}):
                return self.revoke_now("capabilities_changed")
        return None
