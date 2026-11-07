"""Bounded shared control-session ownership; adapters supply wire/domain policy.

One instance owns one channel, selection, authorization slot and service fence.
No domain adapter creates another task queue or bypasses this lifecycle.
"""

from __future__ import annotations

import asyncio
from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
import secrets
import time
from typing import Any, Awaitable, Callable

from .layout import LayoutError

MAX_SEQUENCE = 2**31 - 1
TTL_MS = 30000
OPEN = {"channel", "open_seq", "slot", "card_id", "revision"}
SELECTION = OPEN | {"token"}
CLOSE_REASONS = frozenset((
    "user", "navigation", "sleep", "voice", "selection_changed",
    "connection_lost", "entity_unavailable", "capabilities_changed", "expired", "unload",
))
RESULT_REASONS = frozenset((
    "none", "service_error", "service_timeout", "state_timeout", "selection_changed",
    "connection_lost", "entity_unavailable", "unsupported", "expired",
    "sequence_conflict", "stale_sequence", "busy", "unauthorized",
))
TERMINAL = frozenset(("state_matches", "already_matched", "not_confirmed", "rejected"))


class ProtocolError(ValueError):
    """Malformed or inadmissible message; no service is dispatched."""


@dataclass(frozen=True)
class ControlTarget:
    """Resolved authorization target and optional private registration identity."""
    entity_id: str
    registration: object | None = None


@dataclass(frozen=True)
class ServiceDispatch:
    domain: str
    operation: str
    data: dict[str, Any]


@dataclass(frozen=True)
class CallbackDispatch:
    """Trusted local callback only; never parsed from a native payload."""
    invoke: Callable[[Any], bool]


@dataclass
class _Command:
    seq: int
    digest: str
    payload: dict[str, Any]
    result: dict[str, Any]
    task: asyncio.Task | None = None
    prepared: Any = None
    changed: asyncio.Event = field(default_factory=asyncio.Event)
    priority: bool = False
    predecessor: asyncio.Task | None = None
    predecessor_started: bool = False
    service_started: bool = False


@dataclass
class _Selection:
    identity: dict[str, Any]
    entity_id: str
    context: Any
    principal: Any
    caps: dict[str, Any]
    deadline: float
    state_seq: int = 0
    highest_command: int = 0
    command: _Command | None = None
    last: _Command | None = None
    renewal: asyncio.Task | None = None
    domain_state: Any = None


class ControlSessionOwner:
    """One channel/selection/service fence, with no implicit service permission.

    ``authorize(context, entity_id)`` is REQUIRED and must enforce HA control
    permission for an authenticated caller or trusted native transport policy.
    ``emit`` sends presentation envelopes only, in order, over that bound runtime.
    A command retains the actual HA caller Context through async_call.
    """

    _open_fields = OPEN
    _selection_fields = SELECTION
    _result_reasons = RESULT_REASONS
    _terminal_statuses = TERMINAL

    def __init__(self, hass: Any, read_context: Callable[[], Any],
                 emit: Callable[[dict[str, Any], int, object], Awaitable[None]],
                 authorize: Callable[[Any, str], Awaitable[bool]], *,
                 clock: Callable[[], float] = time.monotonic,
                 token_factory: Callable[[], str] = lambda: secrets.token_hex(16),
                 service_timeout: float = 5, state_timeout: float = 8,
                 renewal_interval: float = 10, authorization_timeout: float = 2):
        self.hass, self.read_context, self.emit, self.authorize = hass, read_context, emit, authorize
        self.clock, self.token_factory = clock, token_factory
        self.service_timeout, self.state_timeout = service_timeout, state_timeout
        self.renewal_interval = renewal_interval
        self.authorization_timeout = authorization_timeout
        self.channel: str | None = None
        self._epoch: int | None = None
        self._runtime: object | None = None
        self._bound = False
        self._closed = False
        self._open_seq = 0
        self._open_generation = 0
        self._opening: tuple[dict[str, Any], Any] | None = None
        self._selection: _Selection | None = None
        self._service_task: asyncio.Task | None = None
        self._authorization_task: asyncio.Task | None = None

    def prepare_bind(self, capability: str | bytes, *, epoch: int, runtime: object) -> dict[str, Any]:
        """Call only after closing the old connection; no profile-based inference."""
        message = self._decode(capability)
        if message["kind"] != "capability" or not message["enabled"] or self._closed or self._selection is not None:
            raise ProtocolError("capability_or_lifecycle")
        context = self.read_context()
        if not context.available or context.epoch != epoch or context.runtime is not runtime:
            raise ProtocolError("connection_lost")
        channel = self.token_factory()
        result = self._envelope("bind", channel=channel)
        self._encode(result)
        self.channel, self._epoch, self._runtime = channel, context.epoch, context.runtime
        self._bound, self._open_seq = False, 0
        self._open_generation += 1
        self._opening = None
        self._cancel_authorization()
        return result

    def accept_bind(self, response: str | bytes, *, epoch: int, runtime: object) -> None:
        """Exact source acceptance echo; not visual/physical application."""
        value = self._decode(response)
        if (value != self._envelope("bind", channel=self.channel) or not self._connection_current()
                or epoch != self._epoch or runtime is not self._runtime):
            raise ProtocolError("bind")
        self._bound = True

    def _connection_current(self) -> bool:
        current = self.read_context()
        return not self._closed and current.available and current.epoch == self._epoch and current.runtime is self._runtime

    @property
    def channel_ready(self) -> bool:
        return self._bound and self._connection_current()

    @staticmethod
    def _principal(context: Any) -> Any:
        return getattr(context, "user_id", None)

    def _authorization_policy(self, card):
        return self.authorize

    async def _authorized(self, context: Any, entity_id: str, *, authorizer=None) -> bool:
        # One lookup, with no waiter queue. A cancellation-resistant hook retains
        # this sole slot and blocks later lookup/dispatch instead of spawning jobs.
        if self._authorization_task is not None and not self._authorization_task.done():
            raise ProtocolError("busy")
        caller = asyncio.current_task()
        job = asyncio.create_task((authorizer or self.authorize)(context, entity_id), name=caller.get_name() if caller else None)
        self._authorization_task = job
        job.add_done_callback(self._authorization_done)
        try:
            done, _ = await asyncio.wait({job}, timeout=self.authorization_timeout)
            if not done:
                job.cancel()
                return False
            if job.cancelled():
                raise ProtocolError("busy")
            return job.result() is True
        except ProtocolError:
            raise
        except asyncio.CancelledError:
            job.cancel()
            raise
        except Exception:
            # Permission lookup failure must never turn into implicit system access.
            return False

    def _cancel_authorization(self) -> None:
        if self._authorization_task is not None:
            self._authorization_task.cancel()

    def _authorization_done(self, task: asyncio.Task) -> None:
        if not task.cancelled():
            task.exception()
        if self._authorization_task is task:
            self._authorization_task = None

    def _binding(self, identity: dict[str, Any]) -> tuple[Any, dict[str, Any], dict[str, bool]]:
        current = self.read_context()
        if not self._bound or not self._connection_current() or identity["channel"] != self.channel:
            raise ProtocolError("connection_lost")
        if (current.layout_version != 3 or current.revision != identity["revision"]
                or current.sent_revision != current.revision or identity["slot"] not in current.editable_slots):
            raise ProtocolError("selection_changed")
        matches = [card for card in current.cards if card.get("slot") == identity["slot"]]
        if len(matches) != 1:
            raise ProtocolError("selection_changed")
        card = matches[0]
        if card.get("id") != identity["card_id"] or card.get("visible") is not True:
            raise ProtocolError("selection_changed")
        state, caps = self._entity_binding(card)
        return state, card, caps
    def _valid_selection(self, selected: _Selection) -> tuple[Any, dict[str, Any], dict[str, bool]]:
        if selected is not self._selection:
            raise ProtocolError("selection_changed")
        if self.clock() >= selected.deadline:
            raise ProtocolError("expired")
        state, card, caps = self._binding(selected.identity)
        if self._resolved_target(state, card, caps).entity_id != selected.entity_id:
            raise ProtocolError("selection_changed")
        if caps != selected.caps:
            raise ProtocolError("capabilities_changed")
        return state, card, caps

    async def _send(self, value: dict[str, Any]) -> dict[str, Any]:
        self._encode(value)
        epoch, runtime, channel = self._epoch, self._runtime, self.channel
        generation = self._open_generation
        try:
            if epoch is None or runtime is None or value.get("channel") != channel:
                raise ProtocolError("connection_lost")
            await self.emit(deepcopy(value), epoch, runtime)
        except Exception as err:
            # A failed old-runtime await must never revoke a rebound channel.
            if (epoch == self._epoch and runtime is self._runtime and channel == self.channel
                    and generation == self._open_generation):
                self._bound = False
                self._open_generation += 1
                self._opening = None
                self._cancel_authorization()
                await self._close_selection("connection_lost", notify=False)
            raise ProtocolError("connection_lost") from err
        return value

    async def async_handle(self, payload: str | bytes, context: Any = None) -> dict[str, Any] | None:
        message = self._decode(payload)
        if message["kind"] not in ("open", "command", "close", "cancel_open"):
            raise ProtocolError("direction")
        if not self._connection_current() or not self._bound or message["channel"] != self.channel:
            raise ProtocolError("connection_lost")
        if message["kind"] == "open":
            return await self._open(message, context)
        if message["kind"] == "cancel_open":
            # A cancel can precede a delayed open/grant and consumes the sequence.
            if message["open_seq"] < self._open_seq:
                return None
            selected = self._selection
            target = selected.identity if selected and selected.identity["open_seq"] == message["open_seq"] else None
            principal = selected.principal if target else None
            if self._opening and self._opening[0]["open_seq"] == message["open_seq"]:
                target, principal = self._opening
            if target is not None and any(message[key] != target[key] for key in self._open_fields):
                raise ProtocolError("selection_changed")
            if target is not None and self._principal(context) != principal:
                raise ProtocolError("unauthorized")
            self._open_seq = message["open_seq"]
            self._open_generation += 1
            self._opening = None
            self._cancel_authorization()
            if selected is not None and all(message[key] == selected.identity[key] for key in self._open_fields):
                await self.async_close(message["reason"])
            return None
        selected = self._selection
        if selected is None or any(message[key] != selected.identity[key] for key in self._selection_fields):
            raise ProtocolError("selection_changed")
        if self._principal(context) != selected.principal:
            raise ProtocolError("unauthorized")
        if message["kind"] == "close":
            await self.async_close(message["reason"])
            return None
        try:
            return await self._command(selected, message, context)
        except ProtocolError as err:
            if str(err) in CLOSE_REASONS and selected is self._selection:
                await self.async_close(str(err))
            raise

    async def _open(self, message: dict[str, Any], context: Any) -> dict[str, Any] | None:
        if message["open_seq"] <= self._open_seq:
            raise ProtocolError("stale_sequence")
        self._open_seq = message["open_seq"]
        self._open_generation += 1
        generation = self._open_generation
        self._opening = (message, self._principal(context))
        self._cancel_authorization()
        await self._close_selection("selection_changed")
        # Give the old cooperative lookup one cancellation turn. If it ignores
        # cancellation the sole slot stays occupied; a new open is denied busy.
        await asyncio.sleep(0)
        if generation != self._open_generation:
            return None
        captured_open = None
        try:
            state, card, caps = self._binding(message)
            authorized_target = self._resolved_target(state, card, caps)
            captured_open = self._capture_open(message, state, card, caps)
            allowed = await self._authorized(context, authorized_target.entity_id, authorizer=self._authorization_policy(card))
            # Authorization awaits: recheck every identity/capability before granting.
            if generation != self._open_generation:
                return None
            if not allowed:
                raise ProtocolError("unauthorized")
            state, card, caps = self._binding(message)
            if self._resolved_target(state, card, caps) != authorized_target:
                raise ProtocolError("selection_changed")
            self._revalidate_open(captured_open, state, card, caps)
            token = self.token_factory()
            identity = {key: message[key] for key in self._open_fields} | {"token": token}
            selected = _Selection(identity, authorized_target.entity_id, context, self._principal(context), caps,
                                  self.clock() + TTL_MS / 1000)
            self._selection = selected
            self._opening = None
            value = await self._snapshot(selected, "grant", state, card)
            if selected is self._selection:
                selected.renewal = asyncio.create_task(self._renew(selected))
            return value
        except ProtocolError as err:
            if generation != self._open_generation:
                return None
            if generation == self._open_generation:
                self._opening = None
                # Roll back only this attempted grant, never a newer selection.
                if self._selection is not None and self._selection.identity.get("open_seq") == message["open_seq"]:
                    await self._close_selection("selection_changed", notify=False)
                reason = str(err) if str(err) in CLOSE_REASONS else "selection_changed"
                await self._send(self._envelope("cancel_open", **{key: message[key] for key in self._open_fields}, reason=reason))
            raise
        finally:
            self._finish_open(captured_open)


    async def _snapshot(self, selected: _Selection, kind: str, state: Any, card: dict[str, Any]) -> dict[str, Any]:
        if selected.state_seq >= MAX_SEQUENCE:
            await self.async_close("expired")
            raise ProtocolError("expired")
        selected.state_seq += 1
        fields = self._selection_snapshot_fields(selected, state, card, selected.caps)
        value = self._envelope(kind, **selected.identity, state_seq=selected.state_seq, ttl_ms=TTL_MS, **fields)
        selected.deadline = self.clock() + TTL_MS / 1000
        return await self._send(value)

    async def _renew(self, selected: _Selection) -> None:
        try:
            while selected is self._selection:
                await asyncio.sleep(self.renewal_interval)
                await self.async_state_changed(selected)
        except (asyncio.CancelledError, ProtocolError):
            pass

    async def async_state_changed(self, expected: _Selection | None = None) -> None:
        """Bridge calls for the one selected entity; also used by one renewal task."""
        selected = expected or self._selection
        if selected is None or selected is not self._selection:
            return
        try:
            state, card, _ = self._valid_selection(selected)
        except ProtocolError as err:
            reason = str(err) if str(err) in CLOSE_REASONS else "capabilities_changed"
            await self.async_close(reason)
            return
        # Renewal is allowed only while actual permission is still valid.
        try:
            allowed = await self._authorized(selected.context, selected.entity_id, authorizer=self._authorization_policy(card))
        except ProtocolError:
            return  # Another bounded lookup owns admission; coalesce this refresh.
        if selected is not self._selection:
            return
        if not allowed:
            await self.async_close("selection_changed")
            return
        try:
            state, card, _ = self._valid_selection(selected)
        except ProtocolError:
            if selected is self._selection:
                await self.async_close("selection_changed")
            return
        await self._snapshot(selected, "state", state, card)
        if selected.command is not None:
            selected.command.changed.set()

    def _result(self, selected: _Selection, seq: int, status: str, reason: str = "none") -> dict[str, Any]:
        return self._envelope("result", **selected.identity, command_seq=seq,
                        state_seq=selected.state_seq, status=status, reason=reason)

    async def _command(self, selected: _Selection, message: dict[str, Any], context: Any) -> dict[str, Any]:
        self._valid_selection(selected)
        digest = hashlib.sha256(json.dumps(message, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        seq = message["command_seq"]
        for record in (selected.command, selected.last):
            if record is not None and seq == record.seq:
                if digest != record.digest:
                    return await self._send(self._result(selected, seq, "rejected", "sequence_conflict"))
                return await self._send(record.result)
        if seq <= selected.highest_command:
            return await self._send(self._result(selected, seq, "rejected", "stale_sequence"))
        selected.highest_command = seq
        predecessor = selected.command
        priority = self._is_priority_successor(selected, message)
        if (predecessor is not None or (self._service_task is not None and not self._service_task.done())) and not priority:
            record = _Command(seq, digest, message, self._result(selected, seq, "rejected", "busy"))
            selected.last = record
            return await self._send(record.result)
        record = _Command(seq, digest, message, self._result(selected, seq, "pending"))
        record.priority = priority
        if not priority:
            selected.command = record
        try:
            record.prepared = self._prepare_command(selected, message)
        except ProtocolError as error:
            reason = str(error) if str(error) in self._result_reasons else "unsupported"
            if priority:
                # A malformed/stale successor must not cancel the admitted job.
                record.result = self._result(selected, seq, "rejected", reason)
                selected.last = record
                return await self._send(record.result)
            await self._publish(selected, record, "rejected", reason)
            return deepcopy(record.result)
        if priority:
            if selected is not self._selection or predecessor is None or selected.command is not predecessor:
                raise ProtocolError("selection_changed")
            record.predecessor = self._service_task
            record.predecessor_started = predecessor.service_started
            # No await: cancellation and replacement happen before the old
            # authorization/observer gets another dispatch opportunity.
            if predecessor.task is not None:
                predecessor.task.cancel()
            predecessor.result = self._result(selected, predecessor.seq, "rejected", "stale_sequence")
            selected.last, selected.command = predecessor, record
        await self._send(record.result)
        if self._record_current(selected, record):
            record.task = asyncio.create_task(self._execute(selected, record, context))
        return deepcopy(record.result)

    async def _publish(self, selected: _Selection, record: _Command, status: str, reason: str = "none") -> None:
        if selected is not self._selection or selected.command is not record or record.result["status"] in self._terminal_statuses:
            return
        record.result = self._result(selected, record.seq, status, reason)
        if status in self._terminal_statuses:
            selected.last, selected.command = record, None
        await self._send(record.result)

    def _matches(self, selected: _Selection, command: dict[str, Any]) -> bool:
        state, _, _ = self._valid_selection(selected)
        return self._state_matches(state, selected.caps, command)

    def _record_current(self, selected: _Selection, record: _Command) -> bool:
        return (selected is self._selection and selected.command is record
                and record.result["status"] not in self._terminal_statuses)

    def _is_priority_successor(self, selected: _Selection, message: dict[str, Any]) -> bool:
        """Policy opt-in only; ordinary controls never preempt an admitted job."""
        return False

    def _completed_service_status(self, selected: _Selection, record: _Command) -> str | None:
        """Policy opt-in terminal after successful callback, never physical proof."""
        return None

    def _service_call_blocking(self, selected: _Selection, record: _Command) -> bool:
        """Default to callback completion; only negotiated policy may dispatch asynchronously."""
        return True

    def _resolved_target(self, state, card, caps) -> ControlTarget:
        return ControlTarget(card["entity_id"])

    def _command_dispatch(self, selected, record, state, caps) -> ServiceDispatch | CallbackDispatch:
        return ServiceDispatch(*self._command_service_action(state, caps, record))

    async def _run_dispatch(self, selected, record, dispatch, context):
        if isinstance(dispatch, ServiceDispatch):
            return await self.hass.services.async_call(
                dispatch.domain, dispatch.operation, {"entity_id": selected.entity_id, **dispatch.data},
                blocking=self._service_call_blocking(selected, record), context=context)
        if not isinstance(dispatch, CallbackDispatch) or not self._record_current(selected, record):
            raise ProtocolError("selection_changed")
        # create_task schedules another turn. Recheck the entire capture in that
        # turn, then fire synchronously: no await gap can admit a retired binding.
        state, _, caps = self._valid_selection(selected)
        self._validate_prepared(selected, record, state, caps)
        if dispatch.invoke(context) is not True:
            raise ProtocolError("service_error")

    async def _execute(self, selected: _Selection, record: _Command, context: Any) -> None:
        try:
            self._cancel_authorization()
            await asyncio.sleep(0)
            if record.predecessor is not None:
                try:
                    # Do not cancel a service already dispatched to HA. The
                    # successor retains its order but never waits indefinitely.
                    await asyncio.wait_for(asyncio.shield(record.predecessor), self.service_timeout)
                except TimeoutError:
                    await self._publish(selected, record, "not_confirmed", "service_timeout")
                    return
                except Exception:
                    pass  # Ambiguous old failure still permits explicit Stop.
            if not self._record_current(selected, record):
                return
            if not await self._authorized(context, selected.entity_id):
                await self._publish(selected, record, "rejected", "unauthorized")
                return
            if not self._record_current(selected, record):
                return
            state, _, caps = self._valid_selection(selected)
            self._validate_prepared(selected, record, state, caps)
            dispatch = self._command_dispatch(selected, record, state, caps)
            if self._command_matches(selected, record):
                await self._publish(selected, record, "already_matched")
                return
            if self._service_task is not None and not self._service_task.done():
                await self._publish(selected, record, "rejected", "busy")
                return
            # No await between the final live validation and creating exactly one call.
            record.service_started = True
            job = asyncio.create_task(self._run_dispatch(selected, record, dispatch, context))
            self._service_task = job
            job.add_done_callback(self._service_done)
            try:
                await asyncio.wait_for(asyncio.shield(job), self.service_timeout)
            except TimeoutError:
                await self._publish(selected, record, "not_confirmed", "service_timeout")
                return
            except Exception:
                await self._publish(selected, record, "rejected", "service_error")
                return
            self._valid_selection(selected)
            completed = self._completed_service_status(selected, record)
            if completed is not None:
                await self._publish(selected, record, completed)
                return
            await self._publish(selected, record, "ha_accepted")
            deadline = self.clock() + self.state_timeout
            while selected is self._selection:
                record.changed.clear()
                if self._command_matches(selected, record):
                    await self._publish(selected, record, "state_matches")
                    return
                remaining = deadline - self.clock()
                if remaining <= 0:
                    break
                try:
                    await asyncio.wait_for(record.changed.wait(), remaining)
                except TimeoutError:
                    break
            await self._publish(selected, record, "not_confirmed", "state_timeout")
        except (ProtocolError, LayoutError) as err:
            reason = str(err) if str(err) in self._result_reasons else "unsupported"
            await self._publish(selected, record, "rejected", reason)
            if str(err) in CLOSE_REASONS and selected is self._selection:
                await self.async_close(str(err))
        except asyncio.CancelledError:
            # Closing a view does not undo/cancel a service already sent to HA.
            pass

    def _service_done(self, task: asyncio.Task) -> None:
        # Consume late exceptions; never report an old job into a new selection.
        if not task.cancelled():
            task.exception()
        if self._service_task is task:
            self._service_task = None

    async def async_close(self, reason: str = "user") -> None:
        if reason not in CLOSE_REASONS:
            raise ProtocolError("reason")
        self._open_generation += 1
        self._opening = None
        self._cancel_authorization()
        await self._close_selection(reason)

    def revoke_now(self, reason: str, *, disconnect: bool = False) -> dict[str, Any] | None:
        """Synchronously stop admission from HA connection/options callbacks.

        Return an optional old-selection close presentation. No task, transport
        call or inverse action is created here; caller owns bounded notification.
        """
        if reason not in CLOSE_REASONS:
            raise ProtocolError("reason")
        self._open_generation += 1
        self._opening = None
        self._cancel_authorization()
        value = self._detach_selection(reason)
        if disconnect:
            self._bound = False
            self.channel, self._runtime, self._epoch = None, None, None
        return value

    def _detach_selection(self, reason: str) -> dict[str, Any] | None:
        selected, self._selection = self._selection, None
        if selected is None:
            return None
        current = asyncio.current_task()
        for task in (selected.renewal, selected.command.task if selected.command else None):
            if task is not None and task is not current:
                task.cancel()
        return self._envelope("close", **selected.identity, reason=reason)

    async def _close_selection(self, reason: str, *, notify: bool = True) -> None:
        value = self._detach_selection(reason)
        if value is not None and notify:
            await self._send(value)

    async def async_disconnect(self) -> None:
        self._bound = False
        self._open_generation += 1
        self._opening = None
        self._cancel_authorization()
        await self._close_selection("connection_lost", notify=False)
        self.channel, self._runtime, self._epoch = None, None, None

    async def async_unload(self) -> None:
        self._closed, self._bound = True, False
        self._open_generation += 1
        try:
            await self.async_close("unload")
        finally:
            # Cancel our local service coroutine on unload. This cannot undo an
            # HA service already dispatched and must never cause a retry.
            if self._service_task is not None:
                self._service_task.cancel()
            self.channel, self._runtime, self._epoch = None, None, None

    def _capture_open(self, message, state, card, caps):
        return None

    def _revalidate_open(self, captured, state, card, caps):
        pass

    def _finish_open(self, captured):
        pass

    def _selection_snapshot_fields(self, selected, state, card, caps):
        return self._snapshot_fields(state, card, caps)

    def _prepare_command(self, selected, message):
        return None

    def _validate_prepared(self, selected, record, state, caps):
        pass

    def _command_service_action(self, state, caps, record):
        return self._service_action(state, caps, record.payload)

    def _command_matches(self, selected, record):
        return self._matches(selected, record.payload)

    @staticmethod
    def _decode(payload: str | bytes) -> dict[str, Any]:
        raise NotImplementedError("A control wire adapter is required")

    @staticmethod
    def _encode(value: dict[str, Any]) -> str:
        raise NotImplementedError("A control wire adapter is required")

    @staticmethod
    def _envelope(kind: str, **fields: Any) -> dict[str, Any]:
        raise NotImplementedError("A control wire adapter is required")

    def _entity_binding(self, card: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
        raise NotImplementedError("A control domain adapter is required")

    def _snapshot_fields(self, state: Any, card: dict[str, Any], caps: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("A control domain adapter is required")

    def _state_matches(self, state: Any, caps: dict[str, Any], command: dict[str, Any]) -> bool:
        raise NotImplementedError("A control domain adapter is required")

    def _service_action(self, state: Any, caps: dict[str, Any], message: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
        raise NotImplementedError("A control domain adapter is required")
