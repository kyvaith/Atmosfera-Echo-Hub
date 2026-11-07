"""Isolated W03 bridge adapter; only existing ESPHome and HA service transports."""

from __future__ import annotations

import asyncio
import json
from copy import deepcopy
from typing import Any

from aioesphomeapi.model import SupportsResponseType, UserServiceArgType

from .const import API_ACTION_BIND_LIGHT, API_ACTION_GET_LIGHT_STATUS, API_ACTION_UPDATE_LIGHT, DOMAIN
from .const import API_ACTION_BIND_ENTITY, API_ACTION_GET_ENTITY_STATUS, API_ACTION_UPDATE_ENTITY
from .const import API_ACTION_GET_ENTITY_FEATURES, API_ACTION_BIND_ENTITY_FEATURES
from .const import API_ACTION_GET_COVER_FEATURES, API_ACTION_BIND_COVER_FEATURES
from .const import API_ACTION_GET_CHOICE_FEATURES, API_ACTION_BIND_CHOICE_FEATURES
from .entity_control_features import decode_features
from . import panel_features
from . import detail_features
from . import light_color_features, climate_range_features, agenda_features, statistics_features
from . import extra_panel_features, action_parameters_features
from .const import API_ACTION_GET_PANEL_FEATURES, API_ACTION_BIND_PANEL_FEATURES
from .const import API_ACTION_GET_DETAIL_FEATURES, API_ACTION_BIND_DETAIL_FEATURES
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

    return await _authorize_entity_policy(hass, context, entity_id, POLICY_CONTROL)


async def authorize_ha_read_context(hass: Any, context: Any, entity_id: str) -> bool:
    """Read permission is separate and never used by service commands."""
    from homeassistant.auth.permissions.const import POLICY_READ

    return await _authorize_entity_policy(hass, context, entity_id, POLICY_READ)


async def _authorize_entity_policy(hass, context, entity_id, policy):

    if not _real_context(context):
        return False
    user_id = context.user_id
    if user_id is None:
        return True  # Explicit HA trusted internal/system-caller policy.
    if not isinstance(user_id, str) or not user_id:
        return False
    user = await hass.auth.async_get_user(user_id)
    return bool(user is not None and user.is_active
                and user.permissions.check_entity(entity_id, policy))


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
        self._editable = frozenset(slot["slot"] for slot in device_profile(carousel=True)["slots"] if slot["editable"])
        self.owner = EntityControlOwner(bridge.hass, self._read_context, self._emit, self._authorize,
                                       authorize_read=self._authorize_read, agenda_changed=self.state_changed, statistics_changed=self.state_changed,
                                       tile_event_resolver=getattr(bridge, "resolve_tile_event_panel", None),
                                       tile_event_dispatch=getattr(bridge, "dispatch_tile_event_panel", None),
                                       choice_language=lambda: getattr(bridge, "device_locale", None) or bridge.hass.config.language)

    def _read_context(self) -> LightContext:
        return LightContext(
            self.bridge._connection_epoch, self.bridge.esphome_entry.runtime_data,
            self.bridge.tile_device_available and not self._closed,
            self.bridge.layout["version"], self.bridge.saved_revision, self.bridge.sent_revision,
            tuple(deepcopy(self.bridge.tile_cards)), self._editable,
        )

    async def _authorize(self, context: Any, entity_id: str) -> bool:
        return await authorize_ha_context(self.bridge.hass, context, entity_id)

    async def _authorize_read(self, context: Any, entity_id: str) -> bool:
        return await authorize_ha_read_context(self.bridge.hass, context, entity_id)

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

    async def _negotiate_cover_stop(self, epoch, runtime, generation):
        """Optional one-shot extension; never weakens or expands the v1 codec."""
        query = self.bridge._find_api_action(API_ACTION_GET_ENTITY_FEATURES)
        bind = self.bridge._find_api_action(API_ACTION_BIND_ENTITY_FEATURES)
        args = getattr(bind, "args", None)
        expected = [("channel", UserServiceArgType.STRING), ("cover_stop_version", UserServiceArgType.INT)]
        if (not _action_contract(query, payload=False, response=True) or bind is None
                or not isinstance(args, (list, tuple))
                or [(getattr(arg, "name", None), getattr(arg, "type", None)) for arg in args] != expected
                or getattr(bind, "supports_response", None) != SupportsResponseType.ONLY):
            return
        channel = self.owner.channel
        try:
            response = await runtime.client.execute_service(query, {}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or decode_features(response)["cover_stop_version"] != 1:
                return
            response = await runtime.client.execute_service(
                bind, {"channel": channel, "cover_stop_version": 1}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation):
                return
            value = decode_features(response, bind=True)
            if value["accepted"] is True and value["channel"] == channel and value["cover_stop_version"] == 1:
                self.owner.accept_cover_features(channel, 1)
        except asyncio.CancelledError:
            raise
        except Exception:
            # Other negotiated controls remain usable; Cover stays passive.
            return

    async def _negotiate_empty_choice(self, epoch, runtime, generation):
        """Optional one-shot extension; never weakens or expands the v1 codec."""
        query = self.bridge._find_api_action(API_ACTION_GET_CHOICE_FEATURES)
        bind = self.bridge._find_api_action(API_ACTION_BIND_CHOICE_FEATURES)
        args = getattr(bind, "args", None)
        expected = [("channel", UserServiceArgType.STRING), ("empty_choice_version", UserServiceArgType.INT)]
        if (not _action_contract(query, payload=False, response=True) or bind is None
                or not isinstance(args, (list, tuple))
                or [(getattr(arg, "name", None), getattr(arg, "type", None)) for arg in args] != expected
                or getattr(bind, "supports_response", None) != SupportsResponseType.ONLY):
            return

        channel = self.owner.channel
        try:
            response = await runtime.client.execute_service(query, {}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or decode_features(response, empty_choice=True)["empty_choice_version"] != 1:
                return
            response = await runtime.client.execute_service(
                bind, {"channel": channel, "empty_choice_version": 1}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation):
                return
            value = decode_features(response, bind=True, empty_choice=True)
            if value["accepted"] is True and value["channel"] == channel and value["empty_choice_version"] == 1:
                self.owner.accept_empty_choice_features(channel, 1)
        except asyncio.CancelledError:
            raise
        except Exception:
            # Other negotiated controls remain usable; Empty selections stay unavailable.
            return


    async def _negotiate_cover_panel(self, epoch, runtime, generation):
        """Bind the detail extension only after existing priority Stop succeeds."""
        if self.owner.cover_stop_version != 1:
            return
        query = self.bridge._find_api_action(API_ACTION_GET_COVER_FEATURES)
        bind = self.bridge._find_api_action(API_ACTION_BIND_COVER_FEATURES)
        args = getattr(bind, "args", None)
        expected = [("channel", UserServiceArgType.STRING), ("cover_panel_version", UserServiceArgType.INT)]
        if (not _action_contract(query, payload=False, response=True) or bind is None
                or not isinstance(args, (list, tuple))
                or [(getattr(arg, "name", None), getattr(arg, "type", None)) for arg in args] != expected
                or getattr(bind, "supports_response", None) != SupportsResponseType.ONLY):
            return
        channel = self.owner.channel
        try:
            response = await runtime.client.execute_service(query, {}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or decode_features(response, cover_panel=True)["cover_panel_version"] != 1:
                return
            response = await runtime.client.execute_service(
                bind, {"channel": channel, "cover_panel_version": 1}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation):
                return
            value = decode_features(response, bind=True, cover_panel=True)
            if value["accepted"] is True and value["channel"] == channel and value["cover_panel_version"] == 1:
                self.owner.accept_cover_panel_features(channel, 1)
        except asyncio.CancelledError:
            raise
        except Exception:
            return  # Legacy Cover remains available with its existing contract.
    async def _negotiate_panel(self, epoch, runtime, generation):
        query = self.bridge._find_api_action(API_ACTION_GET_PANEL_FEATURES)
        bind = self.bridge._find_api_action(API_ACTION_BIND_PANEL_FEATURES)
        if not (_action_contract(query, payload=False, response=True) and _action_contract(bind, payload=True, response=True)):
            return
        channel = self.owner.channel
        try:
            reply = await runtime.client.execute_service(query, {}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel:
                return
            features = panel_features.decode_features(reply)
            if features["panel_version"] != 1:
                return
            families = features["panel_types"]
            reply = await runtime.client.execute_service(bind, {"payload": panel_features.bind_payload(channel, families)},
                                                         return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel:
                return
            accepted = panel_features.decode_features(reply, bind=True)
            if accepted["accepted"] and accepted["channel"] == channel and accepted["panel_types"] == families:
                self.owner.accept_panel_features(channel, families)
        except asyncio.CancelledError:
            raise
        except Exception:
            return  # Unsupported Panel families never disable existing controls.

    async def _negotiate_extra(self, epoch, runtime, generation):
        query = self.bridge._find_api_action("entity_panel_extra_query")
        bind = self.bridge._find_api_action("entity_panel_extra_bind")
        if not (_action_contract(query, payload=True, response=True) and _action_contract(bind, payload=True, response=True)):
            return
        channel = self.owner.channel
        offered = [dict(profile) for profile in extra_panel_features.PROFILES]
        try:
            reply = await runtime.client.execute_service(query, {"payload": extra_panel_features.payload(channel, offered)},
                                                         return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel:
                return
            profiles = extra_panel_features.decode_response(reply, channel=channel, offered=offered)["profiles"]
            if not profiles:
                return
            reply = await runtime.client.execute_service(bind, {"payload": extra_panel_features.payload(channel, profiles)},
                                                         return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel:
                return
            accepted = extra_panel_features.decode_response(reply, channel=channel, offered=profiles, bind=True)
            if accepted["accepted"]:
                self.owner.accept_extra_features(channel, profiles)
        except asyncio.CancelledError:
            raise
        except Exception:
            return  # Optional Info/Lock never disable Panel-v1 or Detail.

    async def _negotiate_detail(self, epoch, runtime, generation):
        query = self.bridge._find_api_action(API_ACTION_GET_DETAIL_FEATURES)
        bind = self.bridge._find_api_action(API_ACTION_BIND_DETAIL_FEATURES)
        if not (_action_contract(query, payload=False, response=True) and _action_contract(bind, payload=True, response=True)):
            return
        channel = self.owner.channel
        try:
            reply = await runtime.client.execute_service(query, {}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel:
                return
            features = detail_features.decode_features(reply)
            light = features["light_detail_version"] if "light" in self.owner.control_kinds else 0
            climate = features["climate_panel_version"] if "panel" in self.owner.control_kinds else 0
            if not (light or climate):
                return
            reply = await runtime.client.execute_service(bind, {"payload": detail_features.bind_payload(channel, light, climate)},
                                                         return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel:
                return
            accepted = detail_features.decode_features(reply, bind=True)
            if (accepted["accepted"] and accepted["channel"] == channel
                    and accepted["light_detail_version"] == light and accepted["climate_panel_version"] == climate):
                self.owner.accept_detail_features(channel, light, climate)
        except asyncio.CancelledError:
            raise
        except Exception:
            return  # New detail profiles never disable existing controls.

    async def _negotiate_color(self, epoch, runtime, generation):
        if self.owner.light_detail_version != 1:
            return
        query = self.bridge._find_api_action(light_color_features.QUERY)
        bind = self.bridge._find_api_action(light_color_features.BIND)
        if not (_action_contract(query, payload=False, response=True) and _action_contract(bind, payload=True, response=True)):
            return
        channel = self.owner.channel
        client = runtime.client
        try:
            reply = await client.execute_service(query, {}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel or runtime.client is not client:
                return
            if light_color_features.decode_features(reply)["color_version"] != 1:
                return
            reply = await client.execute_service(bind, {"payload": light_color_features.bind_payload(channel)},
                                                         return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel or runtime.client is not client:
                return
            accepted = light_color_features.decode_features(reply, bind=True)
            if accepted["accepted"] and accepted["channel"] == channel:
                self.owner.accept_color_features(channel)
        except asyncio.CancelledError:
            raise
        except Exception:
            return  # Optional Color cannot disable existing Detail/Extra controls.

    async def _negotiate_range(self, epoch, runtime, generation):
        if self.owner.climate_panel_version != 1:
            return
        query = self.bridge._find_api_action(climate_range_features.QUERY)
        bind = self.bridge._find_api_action(climate_range_features.BIND)
        if not (_action_contract(query, payload=False, response=True) and _action_contract(bind, payload=True, response=True)):
            return
        channel = self.owner.channel
        client = runtime.client
        try:
            reply = await client.execute_service(query, {}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel or runtime.client is not client:
                return
            if climate_range_features.decode_features(reply)["range_version"] != 1:
                return
            reply = await client.execute_service(bind, {"payload": climate_range_features.bind_payload(channel)},
                                                         return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel or runtime.client is not client:
                return
            accepted = climate_range_features.decode_features(reply, bind=True)
            if accepted["accepted"] and accepted["channel"] == channel:
                self.owner.accept_range_features(channel)
        except asyncio.CancelledError:
            raise
        except Exception:
            return  # Optional Range cannot disable existing Detail/Extra controls.

    async def _negotiate_agenda(self, epoch, runtime, generation):
        if {"name": "info", "version": 1} not in self.owner.panel_extra_profiles:
            return
        query = self.bridge._find_api_action(agenda_features.QUERY)
        bind = self.bridge._find_api_action(agenda_features.BIND)
        if not (_action_contract(query, payload=False, response=True) and _action_contract(bind, payload=True, response=True)):
            return
        channel = self.owner.channel
        client = runtime.client
        try:
            reply = await client.execute_service(query, {}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel or runtime.client is not client:
                return
            if agenda_features.decode_features(reply)["agenda_version"] != 1:
                return
            reply = await client.execute_service(bind, {"payload": agenda_features.bind_payload(channel)},
                                                         return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel or runtime.client is not client:
                return
            accepted = agenda_features.decode_features(reply, bind=True)
            if accepted["accepted"] and accepted["channel"] == channel:
                self.owner.accept_agenda_features(channel)
        except asyncio.CancelledError:
            raise
        except Exception:
            return  # Optional Agenda cannot disable existing Info/Extra controls.

    async def _negotiate_statistics(self, epoch, runtime, generation):
        if {"name": "info", "version": 1} not in self.owner.panel_extra_profiles:
            return
        query = self.bridge._find_api_action(statistics_features.QUERY)
        bind = self.bridge._find_api_action(statistics_features.BIND)
        if not (_action_contract(query, payload=False, response=True) and _action_contract(bind, payload=True, response=True)):
            return
        channel = self.owner.channel
        client = runtime.client
        try:
            reply = await client.execute_service(query, {}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel or runtime.client is not client:
                return
            if statistics_features.decode_features(reply)["statistics_version"] != 1:
                return
            reply = await client.execute_service(bind, {"payload": statistics_features.bind_payload(channel)},
                                                         return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel or runtime.client is not client:
                return
            accepted = statistics_features.decode_features(reply, bind=True)
            if accepted["accepted"] and accepted["channel"] == channel:
                self.owner.accept_statistics_features(channel)
        except asyncio.CancelledError:
            raise
        except Exception:
            return  # Optional Statistics cannot disable existing Info/Extra controls.

    async def _negotiate_action_parameters(self, epoch, runtime, generation):
        if {"name": "action", "version": 2} not in self.owner.panel_extra_profiles:
            return
        query = self.bridge._find_api_action(action_parameters_features.QUERY)
        bind = self.bridge._find_api_action(action_parameters_features.BIND)
        if not (_action_contract(query, payload=False, response=True) and _action_contract(bind, payload=True, response=True)):
            return
        channel = self.owner.channel
        client = runtime.client
        try:
            reply = await client.execute_service(query, {}, return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel or runtime.client is not client:
                return
            if action_parameters_features.decode_features(reply)["parameters_version"] != 1:
                return
            reply = await client.execute_service(bind, {"payload": action_parameters_features.bind_payload(channel)},
                                                         return_response=True, timeout=3.0)
            if not self._current(epoch, runtime, generation) or self.owner.channel != channel or runtime.client is not client:
                return
            accepted = action_parameters_features.decode_features(reply, bind=True)
            if accepted["accepted"] and accepted["channel"] == channel:
                self.owner.accept_action_parameters_features(channel)
        except asyncio.CancelledError:
            raise
        except Exception:
            return  # Optional parameters cannot disable ordinary Action controls.

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
            if use_generic and "cover" in self.owner.control_kinds:
                await self._negotiate_cover_stop(epoch, runtime, generation)
                if not self._current(epoch, runtime, generation):
                    return False
                await self._negotiate_cover_panel(epoch, runtime, generation)
                if not self._current(epoch, runtime, generation):
                    return False
            if use_generic and "choice" in self.owner.control_kinds:
                await self._negotiate_empty_choice(epoch, runtime, generation)
                if not self._current(epoch, runtime, generation):
                    return False
            if use_generic and "number" in self.owner.control_kinds:
                await self._negotiate_thermostat(epoch, runtime, generation)
                if not self._current(epoch, runtime, generation):
                    return False
            if use_generic and "panel" in self.owner.control_kinds:
                await self._negotiate_panel(epoch, runtime, generation)
                if not self._current(epoch, runtime, generation):
                    return False
            if use_generic:
                await self._negotiate_detail(epoch, runtime, generation)
                if not self._current(epoch, runtime, generation):
                    return False
                await self._negotiate_color(epoch, runtime, generation)
                if not self._current(epoch, runtime, generation):
                    return False
                await self._negotiate_range(epoch, runtime, generation)
                if not self._current(epoch, runtime, generation):
                    return False
            if use_generic and "panel" in self.owner.control_kinds:
                await self._negotiate_extra(epoch, runtime, generation)
                if not self._current(epoch, runtime, generation):
                    return False
                await self._negotiate_agenda(epoch, runtime, generation)
                await self._negotiate_statistics(epoch, runtime, generation)
                await self._negotiate_action_parameters(epoch, runtime, generation)
                if not self._current(epoch, runtime, generation):
                    return False
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

    async def _negotiate_thermostat(self, epoch, runtime, generation):
        channel = self.owner.channel
        for name, version in (("entity_thermostat_get_dial_features", 2), ("entity_thermostat_get_features", 1)):
            query = self.bridge._find_api_action(name)
            if not _action_contract(query, payload=False, response=True):
                continue
            try:
                response = await runtime.client.execute_service(query, {}, return_response=True, timeout=3.0)
                raw = response.response_data
                if not self._current(epoch, runtime, generation):
                    return
                if (response.success is True and isinstance(raw, bytes) and len(raw) <= 128
                        and json.loads(raw) == {"thermostat_version": version, "channel": channel}):
                    self.owner.accept_thermostat_features(channel, dial=version == 2)
                    return
            except Exception:
                if not self._current(epoch, runtime, generation):
                    return

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

    def state_changed(self, event=None, *, registry=False) -> None:
        """Reuse existing tile listener; coalesce events, no new subscription."""
        if self._closed or not self.supported:
            return
        close = self.owner.observe_robot_registry_event(event) if registry else self.owner.observe_state_event(event)
        if close is not None:
            self._cancel(self._close_task)
            self._close_task = self.bridge._spawn_background(self._notify_close(close, self._bound_epoch, self._bound_runtime))
        self._state_dirty = True
        if self._state_task is not None and not self._state_task.done():
            return
        self._state_task = self.bridge._spawn_background(self._refresh_state())

    def action_parameters_lifecycle_changed(self, event) -> None:
        if self._closed or not self.supported:
            return
        close = self.owner.observe_action_parameters_lifecycle(event)
        if close is not None:
            self._cancel(self._close_task)
            self._close_task = self.bridge._spawn_background(self._notify_close(close, self._bound_epoch, self._bound_runtime))

    def statistics_zone_changed(self, event) -> None:
        if self._closed or not self.supported:
            return
        close = self.owner.observe_statistics_zone_event(event)
        if close is not None:
            self._cancel(self._close_task)
            self._close_task = self.bridge._spawn_background(self._notify_close(close, self._bound_epoch, self._bound_runtime))

    def robot_registry_changed(self, event) -> None:
        self.state_changed(event, registry=True)

    def tile_event_binding_changed(self, card_id) -> None:
        if self._closed or not self.supported:
            return
        close = self.owner.observe_tile_event_binding(card_id)
        if close is not None:
            self._cancel(self._close_task)
            self._close_task = self.bridge._spawn_background(self._notify_close(close, self._bound_epoch, self._bound_runtime))

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
            result["control_kinds"] = list(self.owner.control_kinds) if supported else []
            result["detail_version"] = int(self.light_detail_supported or self.climate_panel_supported)
            result["light_detail_version"] = int(self.light_detail_supported)
            result["light_color_version"] = int(supported and self.owner.light_color_version == 1)
            result["climate_range_version"] = int(supported and self.owner.climate_range_version == 1)
            result["info_agenda_version"] = self.info_agenda_version
            result["info_statistics_version"] = self.info_statistics_version
            result["action_parameters_version"] = self.action_parameters_version
            result["climate_panel_version"] = int(self.climate_panel_supported)
            result["panel_extra_profiles"] = self.panel_extra_profiles
            if "panel" in self.owner.control_kinds:
                result["panel_version"] = int(bool(self.panel_types))
                result["panel_types"] = list(self.panel_types)
            if "robot" in self.owner.control_kinds:
                result["robot_control_supported"] = self.robot_supported
            if "cover" in self.owner.control_kinds:
                result["cover_stop_version"] = self.owner.cover_stop_version if supported else 0
                result["cover_panel_version"] = self.owner.cover_panel_version if supported else 0
            if "choice" in self.owner.control_kinds:
                result["empty_choice_version"] = self.owner.empty_choice_version if supported else 0
            if self.thermostat_supported:
                result["thermostat_version"] = 2 if self.owner.thermostat_dial else 1
        return result

    @property
    def number_supported(self):
        return self.supported and self.owner.mode == "entity"

    @property
    def thermostat_supported(self):
        return self.number_supported and self.owner.thermostat_supported

    @property
    def choice_supported(self):
        return self.supported and self.owner.mode == "entity" and "choice" in self.owner.control_kinds

    @property
    def cover_supported(self):
        return self.supported and self.owner.cover_stop_version == 1

    @property
    def cover_panel_supported(self):
        return self.supported and self.owner.cover_panel_version == 1

    @property
    def humidifier_supported(self):
        return self.supported and self.owner.mode == "entity" and "humidifier" in self.owner.control_kinds

    @property
    def light_detail_supported(self):
        return self.supported and self.owner.light_detail_version == 1

    @property
    def climate_panel_supported(self):
        return self.supported and self.owner.climate_panel_version == 1

    @property
    def panel_types(self):
        return self.owner.panel_types if self.supported else ()

    @property
    def panel_extra_profiles(self):
        return self.owner.panel_extra_profiles if self.supported else []

    @property
    def robot_supported(self):
        return self.supported and self.owner.mode == "entity" and "robot" in self.owner.control_kinds

    @property
    def fan_supported(self):
        return self.supported and self.owner.mode == "entity" and "fan" in self.owner.control_kinds

    @property
    def action_parameters_version(self):
        return int(self.supported and self.owner.action_parameters_version == 1)

    @property
    def info_statistics_version(self):
        return int(self.supported and self.owner.info_statistics_version == 1)

    @property
    def info_agenda_version(self):
        return int(self.supported and self.owner.info_agenda_version == 1)

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
    # Structural routing only; the matched owner's negotiated codec validates
    # this again before accepting or authorizing any operation.
    message = entity_control_codec.decode_report(payload)
    bridges = [entry.runtime_data for entry in hass.config_entries.async_loaded_entries(DOMAIN)
               if entry.runtime_data is not None and entry.runtime_data.node_name == node_name
               and getattr(entry.runtime_data, "_light_control", None) is not None
               and entry.runtime_data._light_control.owner.mode == "entity"
               and entry.runtime_data._light_control.owner.channel == message.get("channel")]
    if len(bridges) != 1:
        return False
    await bridges[0]._light_control.async_report_generic(payload, context)
    return True
