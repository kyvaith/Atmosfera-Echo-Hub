"""Isolated W03 bridge adapter; only existing ESPHome and HA service transports."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from typing import Any

from aioesphomeapi.model import SupportsResponseType, UserServiceArgType

from .const import API_ACTION_BIND_LIGHT, API_ACTION_GET_LIGHT_STATUS, API_ACTION_UPDATE_LIGHT, DOMAIN
from .const import API_ACTION_BIND_ENTITY, API_ACTION_GET_ENTITY_STATUS, API_ACTION_UPDATE_ENTITY
from .entity_control import EntityControlOwner
from . import entity_control_codec
from .layout import device_profile
from .light_control import LightContext, ProtocolError, TYPE, decode


def _real_context(context: Any) -> bool:
    # Lazy imports keep this optional adapter independent of auth setup at import.
    from homeassistant.core import Context

    return isinstance(context, Context)


async def authorize_ha_context(hass: Any, context: Any, entity_id: str) -> bool:
    """Use HA caller policy, never a device-provided identity or default allow.

    A real internal/system HA Context follows HA entity-service semantics. The
    owner separately requires this connection's bound explicit card/revision.
    None/non-Context are denied; this function never manufactures a Context.
    """
    from homeassistant.auth.permissions.const import POLICY_CONTROL

    if not _real_context(context):
        return False
    user_id = context.user_id
    if user_id is None:
        return True  # Explicit HA trusted internal/system-caller policy.
    if not isinstance(user_id, str) or not user_id:
        return False
    user = await hass.auth.async_get_user(user_id)
    return bool(user is not None and user.is_active
                and user.permissions.check_entity(entity_id, POLICY_CONTROL))


def _action_contract(action: Any, *, payload: bool, response: bool) -> bool:
    if action is None:
        return False
    expected = [("payload", UserServiceArgType.STRING)] if payload else []
    args = getattr(action, "args", None)
    if not isinstance(args, (list, tuple)) or [(getattr(arg, "name", None), getattr(arg, "type", None)) for arg in args] != expected:
        return False
    support = getattr(action, "supports_response", None)
    return (support == SupportsResponseType.ONLY if response else
            support in (SupportsResponseType.NONE, SupportsResponseType.OPTIONAL))


class LightControlTransport:
    """One owner, epoch, channel and bounded/coalesced adapter work per bridge."""

    def __init__(self, bridge: Any) -> None:
        self.bridge = bridge
        self._closed = False
        self._generation = 0
        self._enabled = False
        self._probe_key = None
        self._bound_epoch = None
        self._bound_runtime = None
        self._bound_channel = None
        self._negotiation_task: asyncio.Task | None = None
        self._state_task: asyncio.Task | None = None
        self._state_dirty = False
        self._close_task: asyncio.Task | None = None
        self._report_task: asyncio.Task | None = None
        self._control_report_task: asyncio.Task | None = None
        self._output_lock = asyncio.Lock()
        self.state = "unconfirmed"
        self._actions = (API_ACTION_GET_LIGHT_STATUS, API_ACTION_BIND_LIGHT, API_ACTION_UPDATE_LIGHT)
        self._editable = frozenset(slot["slot"] for slot in device_profile()["slots"] if slot["editable"])
        self.owner = EntityControlOwner(bridge.hass, self._read_context, self._emit, self._authorize)

    def _read_context(self) -> LightContext:
        return LightContext(
            self.bridge._connection_epoch, self.bridge.esphome_entry.runtime_data,
            self.bridge.tile_device_available and not self._closed,
            self.bridge.layout["version"], self.bridge.saved_revision, self.bridge.sent_revision,
            tuple(deepcopy(self.bridge.tile_cards)), self._editable,
        )

    async def _authorize(self, context: Any, entity_id: str) -> bool:
        return await authorize_ha_context(self.bridge.hass, context, entity_id)

    def _current(self, epoch: int, runtime: Any, generation: int | None = None) -> bool:
        return (not self._closed and self.bridge.tile_device_available
                and epoch == self.bridge._connection_epoch
                and runtime is self.bridge.esphome_entry.runtime_data
                and (generation is None or generation == self._generation))

    @property
    def supported(self) -> bool:
        return bool(self._enabled and self.owner.channel_ready
                    and self._current(self._bound_epoch, self._bound_runtime))

    def _cancel(self, task: asyncio.Task | None) -> None:
        if task is not None and task is not asyncio.current_task():
            task.cancel()

    def invalidate_connection(self) -> None:
        """HA callback: revoke immediately before any scheduled reconnect work."""
        self._generation += 1
        self._enabled = False
        self._probe_key = None
        self.state = "unconfirmed" if self.bridge.tile_device_available else "offline"
        self.owner.revoke_now("connection_lost", disconnect=True)
        self._state_dirty = False
        self._bound_runtime = self._bound_epoch = self._bound_channel = None
        for task in (self._negotiation_task, self._state_task, self._close_task,
                     self._report_task, self._control_report_task):
            self._cancel(task)

    def invalidate_selection(self) -> None:
        """Options callback: revoke first, send at most one old-token close later."""
        value = self.owner.revoke_now("selection_changed")
        self._state_dirty = False
        self._cancel(self._state_task)
        if value is not None and self.supported:
            self._cancel(self._close_task)
            epoch, runtime = self._bound_epoch, self._bound_runtime
            self._close_task = self.bridge._spawn_background(self._notify_close(value, epoch, runtime))

    async def _notify_close(self, value: dict[str, Any], epoch: int, runtime: Any) -> None:
        try:
            await self._emit(value, epoch, runtime)
        except (ProtocolError, TimeoutError, asyncio.CancelledError):
            pass

    def _response(self, response: Any) -> bytes:
        if (response is None or response.success is not True
                or not isinstance(response.response_data, bytes) or len(response.response_data) > 2048):
            raise ProtocolError("native_response")
        self.owner._decode(response.response_data)
        return response.response_data

    async def async_negotiate(self) -> bool:
        """No polling task. Existing serialized tile pushes call this once/epoch."""
        if self._closed or not self.bridge.tile_device_available:
            self.state = "offline"
            return False
        current = asyncio.current_task()
        if self._negotiation_task is not None and not self._negotiation_task.done():
            return False
        runtime, epoch, generation = (self.bridge.esphome_entry.runtime_data,
                                      self.bridge._connection_epoch, self._generation)
        generic_names = (API_ACTION_GET_ENTITY_STATUS, API_ACTION_BIND_ENTITY, API_ACTION_UPDATE_ENTITY)
        generic = tuple(self.bridge._find_api_action(name) for name in generic_names)
        use_generic = (_action_contract(generic[0], payload=False, response=True)
                       and _action_contract(generic[1], payload=True, response=True)
                       and _action_contract(generic[2], payload=True, response=False))
        names = generic_names if use_generic else (API_ACTION_GET_LIGHT_STATUS, API_ACTION_BIND_LIGHT, API_ACTION_UPDATE_LIGHT)
        actions = generic if use_generic else tuple(self.bridge._find_api_action(name) for name in names)
        signature = (names, tuple((id(action), getattr(action, "key", None)) for action in actions))
        key = (epoch, id(runtime), signature)
        if key == self._probe_key:
            return self.supported
        self._probe_key = key
        self._enabled = False
        self.owner.revoke_now("connection_lost", disconnect=True)
        self.owner.set_mode("entity" if use_generic else "legacy")
        self._actions = names
        self._bound_runtime = self._bound_epoch = self._bound_channel = None
        if not (_action_contract(actions[0], payload=False, response=True)
                and _action_contract(actions[1], payload=True, response=True)
                and _action_contract(actions[2], payload=True, response=False)):
            self.state = "unsupported"
            return False
        self._negotiation_task = current
        self.state = "negotiating"
        self.owner.revoke_now("connection_lost", disconnect=True)
        try:
            response = await runtime.client.execute_service(actions[0], {}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation):
                return False
            capability = self._response(response)
            bind = self.owner.prepare_bind(capability, epoch=epoch, runtime=runtime)
            response = await runtime.client.execute_service(
                actions[1], {"payload": self.owner._encode(bind)}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation):
                return False
            self.owner.accept_bind(self._response(response), epoch=epoch, runtime=runtime)
            self._enabled = True
            self._bound_epoch, self._bound_runtime, self._bound_channel = epoch, runtime, self.owner.channel
            self.state = "ready"
            return True
        except asyncio.CancelledError:
            raise
        except Exception:
            if self._current(epoch, runtime, generation):
                self._enabled = False
                self.owner.revoke_now("connection_lost", disconnect=True)
                self.state = "unconfirmed"
            return False
        finally:
            if self._negotiation_task is current:
                self._negotiation_task = None

    async def _emit(self, value: dict[str, Any], epoch: int, runtime: Any) -> None:
        """Ordered presentation send; deadline includes waiting for the one lock."""
        payload = self.owner._encode(value)

        def valid():
            # A final close may be attempted during shutdown, never admission.
            closing = value["kind"] == "close"
            return (value["channel"] == self._bound_channel and epoch == self._bound_epoch
                    and runtime is self._bound_runtime and epoch == self.bridge._connection_epoch
                    and runtime is self.bridge.esphome_entry.runtime_data and runtime.available
                    and (closing or self.supported))

        if not valid():
            raise ProtocolError("connection_lost")
        try:
            async with asyncio.timeout(3.0):
                async with self._output_lock:
                    if not valid():
                        raise ProtocolError("connection_lost")
                    action = self.bridge._find_api_action(self._actions[2])
                    if not _action_contract(action, payload=True, response=False):
                        raise ProtocolError("unsupported")
                    await runtime.client.execute_service(action, {"payload": payload})
                    if not valid():
                        raise ProtocolError("connection_lost")
        except Exception as err:
            raise ProtocolError("connection_lost") from err

    async def async_report(self, payload: str, context: Any) -> None:
        """Called only with actual ServiceCall.context; never construct/fake it."""
        message = self.owner._decode(payload)
        if not _real_context(context):
            raise ProtocolError("unauthorized")
        if not self.supported or message.get("channel") != self.owner.channel:
            raise ProtocolError("connection_lost")
        field = "_control_report_task" if message["kind"] in {"close", "cancel_open"} else "_report_task"
        previous = getattr(self, field)
        if previous is not None and not previous.done():
            raise ProtocolError("busy")
        current = asyncio.current_task()
        setattr(self, field, current)
        try:
            await self.owner.async_handle(payload, context)
        finally:
            if getattr(self, field) is current:
                setattr(self, field, None)

    def state_changed(self, event=None) -> None:
        """Reuse existing tile listener; coalesce events, no new subscription."""
        if self._closed or not self.supported:
            return
        close = self.owner.observe_state_event(event)
        if close is not None:
            self._cancel(self._close_task)
            self._close_task = self.bridge._spawn_background(self._notify_close(close, self._bound_epoch, self._bound_runtime))
        self._state_dirty = True
        if self._state_task is not None and not self._state_task.done():
            return
        self._state_task = self.bridge._spawn_background(self._refresh_state())

    async def _refresh_state(self) -> None:
        current, generation = asyncio.current_task(), self._generation
        try:
            while self._state_dirty and self.supported and not self._closed and generation == self._generation:
                self._state_dirty = False
                await self.owner.async_state_changed()
        except (ProtocolError, asyncio.CancelledError):
            pass
        finally:
            if self._state_task is current:
                self._state_task = None

    async def async_shutdown(self) -> None:
        self._closed = True
        self._state_dirty = False
        tasks = {task for task in (self._negotiation_task, self._state_task, self._close_task,
                                  self._report_task, self._control_report_task)
                 if task is not None and task is not asyncio.current_task()}
        for task in tasks:
            task.cancel()
        try:
            await self.owner.async_unload()
        except ProtocolError:
            pass
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._enabled = False
        self._bound_runtime = self._bound_epoch = self._bound_channel = None
        self.state = "offline"

    def status(self) -> dict[str, Any]:
        supported = self.supported
        state = "ready" if supported else self.state
        if self._closed or not self.bridge.tile_device_available:
            state = "offline"
        elif not supported and state == "ready":
            state = "unconfirmed"
        types = [entity_control_codec.TYPE] if self.owner.mode == "entity" else [TYPE]
        result = {"native_control_types": types if supported else [], "light_control_status": state}
        if self.owner.mode == "entity":
            result["entity_control_status"] = state
            result["control_kinds"] = ["light", "number"] if supported else []
        return result

    @property
    def number_supported(self):
        return self.supported and self.owner.mode == "entity"

    async def async_report_generic(self, payload, context):
        if self.owner.mode != "entity":
            raise ProtocolError("unsupported")
        await self.async_report(payload, context)


async def async_route_report(hass: Any, node_name: str, payload: str, context: Any) -> bool:
    """Unique loaded-bridge correlation only; the mandatory owner checks policy."""
    message = decode(payload)
    bridges = [entry.runtime_data for entry in hass.config_entries.async_loaded_entries(DOMAIN)
               if entry.runtime_data is not None and entry.runtime_data.node_name == node_name
               and getattr(entry.runtime_data, "_light_control", None) is not None
               and entry.runtime_data._light_control.owner.channel == message.get("channel")]
    if len(bridges) != 1:
        return False
    await bridges[0].async_report_light_control(payload, context)
    return True


async def async_route_entity_report(hass, node_name, payload, context):
    message = entity_control_codec.decode(payload)
    bridges = [entry.runtime_data for entry in hass.config_entries.async_loaded_entries(DOMAIN)
               if entry.runtime_data is not None and entry.runtime_data.node_name == node_name
               and getattr(entry.runtime_data, "_light_control", None) is not None
               and entry.runtime_data._light_control.owner.mode == "entity"
               and entry.runtime_data._light_control.owner.channel == message.get("channel")]
    if len(bridges) != 1:
        return False
    await bridges[0]._light_control.async_report_generic(payload, context)
    return True
