"""Runtime bridge between Home Assistant cameras and an ESPHome display."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
import logging
from urllib.parse import quote, urlencode

from aioesphomeapi import APIConnectionError, UserService

from homeassistant.components.camera.helper import get_camera_from_entity_id
from homeassistant.components.network import async_get_source_ip
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_FRIENDLY_NAME, CONF_HOST
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.network import NoURLAvailableError, get_url

from .const import (
    API_ACTION_SELECT_SOURCE,
    API_ACTION_SET_SOURCES,
    CONF_CAMERAS,
    CONF_DEVICE_ID,
    CONF_STREAM_FPS,
    CONF_STREAM_HEIGHT,
    CONF_STREAM_WIDTH,
    DEFAULT_STREAM_FPS,
    DEFAULT_STREAM_HEIGHT,
    DEFAULT_STREAM_WIDTH,
    RETRY_INTERVAL_SECONDS,
    TOKEN_REFRESH_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CameraSource:
    """One camera exposed to the display."""

    entity_id: str
    name: str
    url: str


class CameraBridge:
    """Publish selected HA cameras through the existing ESPHome API session."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the bridge."""
        self.hass = hass
        self.entry = entry
        self.device_id: str = entry.data[CONF_DEVICE_ID]
        self.camera_entity_ids: list[str] = list(
            entry.options.get(CONF_CAMERAS, entry.data[CONF_CAMERAS])
        )
        self.stream_width = int(
            entry.options.get(
                CONF_STREAM_WIDTH,
                entry.data.get(CONF_STREAM_WIDTH, DEFAULT_STREAM_WIDTH),
            )
        )
        self.stream_height = int(
            entry.options.get(
                CONF_STREAM_HEIGHT,
                entry.data.get(CONF_STREAM_HEIGHT, DEFAULT_STREAM_HEIGHT),
            )
        )
        self.stream_fps = int(
            entry.options.get(
                CONF_STREAM_FPS,
                entry.data.get(CONF_STREAM_FPS, DEFAULT_STREAM_FPS),
            )
        )

        device = dr.async_get(hass).async_get(self.device_id)
        if device is None:
            raise HomeAssistantError(f"Device {self.device_id} no longer exists")
        self.device_entry = device

        self.esphome_entry = self._find_esphome_entry()
        if self.esphome_entry is None:
            raise HomeAssistantError("The selected device is not managed by ESPHome")

        self.sources: list[CameraSource] = []
        self.current_option: str | None = None
        self.available = False
        self._listeners: set[Callable[[], None]] = set()
        self._remove_debounce: CALLBACK_TYPE | None = None
        self._unsubscribers: list[CALLBACK_TYPE] = []
        self._push_lock = asyncio.Lock()

    @property
    def options(self) -> list[str]:
        """Return names suitable for a dynamic HA select entity."""
        return [source.name for source in self.sources]

    @property
    def node_name(self) -> str:
        """Return the native ESPHome node name."""
        runtime_data = self.esphome_entry.runtime_data
        return (
            runtime_data.name if runtime_data is not None else self.esphome_entry.title
        )

    def _find_esphome_entry(self) -> ConfigEntry | None:
        for entry_id in self.device_entry.config_entries:
            candidate = self.hass.config_entries.async_get_entry(entry_id)
            if candidate is not None and candidate.domain == "esphome":
                return candidate
        return None

    async def async_setup(self) -> None:
        """Start state tracking and publish the first catalog."""
        self._unsubscribers.append(
            async_track_state_change_event(
                self.hass, self.camera_entity_ids, self._camera_state_changed
            )
        )
        self._unsubscribers.append(
            async_track_time_interval(
                self.hass, self._periodic_refresh, TOKEN_REFRESH_INTERVAL
            )
        )
        self.async_schedule_push(delay=0)

    async def async_shutdown(self) -> None:
        """Stop tracking runtime state."""
        if self._remove_debounce is not None:
            self._remove_debounce()
            self._remove_debounce = None
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers.clear()

    @callback
    def add_listener(self, listener: Callable[[], None]) -> CALLBACK_TYPE:
        """Register an entity state listener."""
        self._listeners.add(listener)
        return lambda: self._listeners.discard(listener)

    @callback
    def _notify_listeners(self) -> None:
        for listener in tuple(self._listeners):
            listener()

    @callback
    def _camera_state_changed(self, event: Event) -> None:
        self.async_schedule_push(delay=1)

    async def _periodic_refresh(self, _now) -> None:
        await self.async_push_sources()

    @callback
    def async_schedule_push(self, delay: float = 1) -> None:
        """Debounce camera state changes and token rotations."""
        if self._remove_debounce is not None:
            self._remove_debounce()
        self._remove_debounce = async_call_later(
            self.hass, delay, self._async_delayed_push
        )

    async def _async_delayed_push(self, _now) -> None:
        self._remove_debounce = None
        if not await self.async_push_sources():
            self.async_schedule_push(delay=RETRY_INTERVAL_SECONDS)

    async def _async_camera_base_url(self) -> str:
        """Return the HA Core URL reachable from the selected ESPHome device."""
        target_host = self.esphome_entry.data.get(CONF_HOST)
        source_ip: str | None = None
        if isinstance(target_host, str):
            try:
                source_ip = await async_get_source_ip(self.hass, target_host)
            except HomeAssistantError:
                pass

        # A plain HTTP HA Core listener is safe to address by the local source
        # IP selected for this ESPHome node. A TLS listener normally uses a
        # certificate for a hostname, so preserve the configured URL instead
        # of introducing an IP/certificate mismatch.
        if (
            source_ip is not None
            and self.hass.http is not None
            and not self.hass.http.ssl_certificate
        ):
            return f"http://{source_ip}:{self.hass.http.server_port}"

        try:
            return get_url(
                self.hass,
                prefer_external=False,
                allow_cloud=False,
                allow_ip=True,
            ).rstrip("/")
        except NoURLAvailableError:
            raise HomeAssistantError(
                "No Home Assistant URL is reachable from the display"
            ) from None

    async def _async_build_sources(self) -> list[CameraSource]:
        """Build signed camera proxy sources for the configured entities."""
        try:
            base_url = await self._async_camera_base_url()
        except HomeAssistantError as err:
            _LOGGER.warning("Unable to build the camera catalog: %s", err)
            return []

        names_seen: dict[str, int] = {}
        sources: list[CameraSource] = []
        for entity_id in self.camera_entity_ids:
            state = self.hass.states.get(entity_id)
            try:
                camera = get_camera_from_entity_id(self.hass, entity_id)
            except HomeAssistantError:
                continue
            if not camera.access_tokens:
                continue
            token = camera.access_tokens[-1]

            name = str(
                state.attributes.get(ATTR_FRIENDLY_NAME, entity_id)
                if state is not None
                else camera.name or entity_id
            )
            name = " ".join(name.replace("\n", " ").split())[:64] or entity_id
            duplicate = names_seen.get(name, 0)
            names_seen[name] = duplicate + 1
            if duplicate:
                name = f"{name} ({duplicate + 1})"

            path = (
                "/api/atmosfera_echo_hub/camera_stream/"
                f"{quote(entity_id, safe='.:_')}"
            )
            query = urlencode(
                {
                    "token": str(token),
                    "width": self.stream_width,
                    "height": self.stream_height,
                    "fps": self.stream_fps,
                }
            )
            sources.append(CameraSource(entity_id, name, f"{base_url}{path}?{query}"))
        return sources

    @callback
    def async_prefer_source(self, option: str) -> None:
        """Remember a restored HA selection before the catalog is republished."""
        self.current_option = option

    def _find_api_action(self, action_name: str) -> UserService | None:
        runtime_data = self.esphome_entry.runtime_data
        if runtime_data is None:
            return None
        return next(
            (
                service
                for service in runtime_data.services.values()
                if service.name == action_name
            ),
            None,
        )

    async def async_push_sources(self) -> bool:
        """Push names and short-lived signed camera URLs to the display."""
        async with self._push_lock:
            runtime_data = self.esphome_entry.runtime_data
            action = self._find_api_action(API_ACTION_SET_SOURCES)
            select_action = self._find_api_action(API_ACTION_SELECT_SOURCE)
            sources = await self._async_build_sources()
            if (
                runtime_data is None
                or not runtime_data.available
                or action is None
                or not sources
            ):
                self.available = False
                self._notify_listeners()
                return False

            try:
                await runtime_data.client.execute_service(
                    action,
                    {
                        "names": [source.name for source in sources],
                        "urls": [source.url for source in sources],
                    },
                )
            except (APIConnectionError, TimeoutError) as err:
                self.available = False
                self._notify_listeners()
                _LOGGER.debug("Unable to update camera catalog: %s", err)
                return False

            self.sources = sources
            if self.current_option not in self.options:
                self.current_option = self.options[0]
            if select_action is not None and self.current_option is not None:
                try:
                    await runtime_data.client.execute_service(
                        select_action,
                        {"index": self.options.index(self.current_option)},
                    )
                except (APIConnectionError, TimeoutError) as err:
                    self.available = False
                    self._notify_listeners()
                    _LOGGER.debug("Unable to restore camera selection: %s", err)
                    return False
            self.available = True
            self._notify_listeners()
            return True

    async def async_select_source(self, option: str) -> None:
        """Select one camera through the existing ESPHome API connection."""
        if option not in self.options:
            raise HomeAssistantError(f"Unknown camera source: {option}")
        runtime_data = self.esphome_entry.runtime_data
        action = self._find_api_action(API_ACTION_SELECT_SOURCE)
        if runtime_data is None or not runtime_data.available or action is None:
            raise HomeAssistantError("Atmosfera Echo Hub is not available")
        try:
            await runtime_data.client.execute_service(
                action, {"index": self.options.index(option)}
            )
        except (APIConnectionError, TimeoutError) as err:
            raise HomeAssistantError(
                "Unable to select the camera on Atmosfera Echo Hub"
            ) from err
        self.async_report_source(option)

    @callback
    def async_report_source(self, source: str) -> None:
        """Accept source changes made on the display."""
        if source not in self.options or self.current_option == source:
            return
        self.current_option = source
        self._notify_listeners()
