"""Runtime bridge between Home Assistant cameras and an ESPHome display."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
import json
import logging
from urllib.parse import quote, urlencode

from aioesphomeapi import APIConnectionError, EntityState, UserService

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
from homeassistant.helpers.translation import async_get_translations

from .cards import (
    card_entity_ids,
    normalize_cards,
    presentation_payload,
    resolve_action,
)
from .const import (
    API_ACTION_SELECT_SOURCE,
    API_ACTION_DISMISS_NOTIFICATION,
    API_ACTION_SHOW_NOTIFICATION,
    API_ACTION_SET_SOURCES,
    API_ACTION_SET_TILES,
    CONF_CAMERAS,
    CONF_DEVICE_ID,
    CONF_STREAM_FPS,
    CONF_STREAM_HEIGHT,
    CONF_STREAM_WIDTH,
    CONF_TILES,
    CONF_ACCENT_COLOR,
    DEFAULT_ACCENT_COLOR,
    DEFAULT_STREAM_FPS,
    DEFAULT_STREAM_HEIGHT,
    DEFAULT_STREAM_WIDTH,
    RETRY_INTERVAL_SECONDS,
    TOKEN_REFRESH_INTERVAL,
)
from .text import plain_text

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
        self.tile_cards = normalize_cards(
            entry.options.get(CONF_TILES, entry.data.get(CONF_TILES))
        )
        self.accent_color = entry.options.get(
            CONF_ACCENT_COLOR, entry.data.get(CONF_ACCENT_COLOR, DEFAULT_ACCENT_COLOR)
        )
        self.tile_entity_ids = card_entity_ids(self.tile_cards)

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
        self._remove_tile_debounce: CALLBACK_TYPE | None = None
        self._unsubscribers: list[CALLBACK_TYPE] = []
        self._push_lock = asyncio.Lock()
        self._tile_push_lock = asyncio.Lock()
        self._last_tile_payload = ""
        self._missing_camera_entity_ids: tuple[str, ...] = ()
        self.device_locale: str | None = None
        self._device_preference_client = None
        self._device_preference_keys: dict[int, str] = {}

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
        runtime_data = self.esphome_entry.runtime_data
        if runtime_data is not None:
            self._unsubscribers.append(
                runtime_data.async_subscribe_device_updated(
                    self._esphome_device_updated
                )
            )
        if self.camera_entity_ids:
            self._unsubscribers.append(
                async_track_state_change_event(
                    self.hass, self.camera_entity_ids, self._camera_state_changed
                )
            )
        if self.tile_entity_ids:
            self._unsubscribers.append(
                async_track_state_change_event(
                    self.hass, self.tile_entity_ids, self._tile_state_changed
                )
            )
        self._unsubscribers.append(
            async_track_time_interval(
                self.hass, self._periodic_refresh, TOKEN_REFRESH_INTERVAL
            )
        )
        await self._async_subscribe_device_preferences()
        self.async_schedule_push(delay=0)
        self.async_schedule_tile_push(delay=0.5)

    @callback
    def _esphome_device_updated(self) -> None:
        """Republish runtime configuration after an ESPHome reconnect."""
        runtime_data = self.esphome_entry.runtime_data
        if runtime_data is None or not runtime_data.available:
            self.available = False
            self._notify_listeners()
            return

        self.hass.async_create_task(self._async_subscribe_device_preferences())

        # ESPHome announces availability immediately before replacing its
        # retained user-service catalog. Delay the first attempt slightly;
        # async_push_sources() retains the normal retry when setup takes longer.
        self.async_schedule_push(delay=0.25)
        self.async_schedule_tile_push(delay=0.5)

    async def async_shutdown(self) -> None:
        """Stop tracking runtime state."""
        if self._remove_debounce is not None:
            self._remove_debounce()
            self._remove_debounce = None
        if self._remove_tile_debounce is not None:
            self._remove_tile_debounce()
            self._remove_tile_debounce = None
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers.clear()

    async def _async_subscribe_device_preferences(self) -> None:
        """Mirror the device's locale and accent before publishing card state."""
        runtime_data = self.esphome_entry.runtime_data
        if runtime_data is None or not runtime_data.available:
            return
        client = runtime_data.client
        if client is self._device_preference_client:
            return
        try:
            entities, _services = await client.list_entities_services()
        except (APIConnectionError, TimeoutError):
            return
        keys: dict[int, str] = {}
        for entity in entities:
            object_id = str(getattr(entity, "object_id", "")).lower()
            name = str(getattr(entity, "name", "")).lower().replace(" ", "_")
            candidate = f"{object_id} {name}"
            if "accent_color" in candidate:
                keys[entity.key] = "accent"
            elif "interface_language" in candidate or "ui_language" in candidate:
                keys[entity.key] = "locale"
        self._device_preference_keys = keys
        self._device_preference_client = client
        client.subscribe_states(self._device_preference_state_changed)

    @callback
    def _device_preference_state_changed(self, state: EntityState) -> None:
        """Accept user changes made on the device before the next HA refresh."""
        kind = self._device_preference_keys.get(state.key)
        if kind == "accent":
            value = str(state.state).strip().lstrip("#")
            try:
                parsed = int(value, 16) if len(value) == 6 else -1
            except ValueError:
                parsed = -1
            if 0 <= parsed <= 0xFFFFFF:
                normalized = f"{parsed:06X}"
                if normalized != str(self.accent_color).strip().lstrip("#").upper():
                    self.accent_color = normalized
                    self._last_tile_payload = ""
                    self.async_schedule_tile_push(delay=0.1)
        elif kind == "locale":
            locale = str(state.state).strip()
            if locale and locale != self.device_locale:
                self.device_locale = locale
                self._last_tile_payload = ""
                self.hass.async_create_task(self._async_load_device_locale(locale))
                self.async_schedule_tile_push(delay=0.1)

    async def _async_load_device_locale(self, locale: str) -> None:
        """Warm HA's translation cache for a locale selected on the display."""
        language = locale.replace("_", "-").split("-", 1)[0].lower()
        try:
            await async_get_translations(self.hass, language, "entity")
            await async_get_translations(self.hass, language, "entity_component")
            self._last_tile_payload = ""
            self.async_schedule_tile_push(delay=0)
        except (HomeAssistantError, ValueError):
            _LOGGER.debug("Unable to load Home Assistant translations for %s", locale)

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

    @callback
    def _tile_state_changed(self, event: Event) -> None:
        self.async_schedule_tile_push(delay=0.18)

    async def _periodic_refresh(self, _now) -> None:
        await self.async_push_sources()
        await self.async_push_tiles(force=True)

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

    @callback
    def async_schedule_tile_push(self, delay: float = 0.18) -> None:
        """Coalesce HA state bursts into one compact device update."""
        if self._remove_tile_debounce is not None:
            self._remove_tile_debounce()
        self._remove_tile_debounce = async_call_later(
            self.hass, delay, self._async_delayed_tile_push
        )

    async def _async_delayed_tile_push(self, _now) -> None:
        self._remove_tile_debounce = None
        if not await self.async_push_tiles():
            self.async_schedule_tile_push(delay=RETRY_INTERVAL_SECONDS)

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
        missing_entity_ids: list[str] = []
        for entity_id in self.camera_entity_ids:
            state = self.hass.states.get(entity_id)
            if state is None:
                missing_entity_ids.append(entity_id)
                continue
            try:
                camera = get_camera_from_entity_id(self.hass, entity_id)
            except HomeAssistantError:
                missing_entity_ids.append(entity_id)
                continue
            if not camera.access_tokens:
                continue
            token = camera.access_tokens[-1]

            name = plain_text(
                state.attributes.get(ATTR_FRIENDLY_NAME, entity_id)
                if state is not None
                else camera.name or entity_id,
                64,
            )
            name = name or entity_id
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
        missing = tuple(missing_entity_ids)
        if missing != self._missing_camera_entity_ids:
            self._missing_camera_entity_ids = missing
            if missing:
                _LOGGER.warning(
                    "Ignoring unavailable configured camera entities: %s",
                    ", ".join(missing),
                )
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
            if not self.camera_entity_ids:
                self.sources.clear()
                self.current_option = None
                self.available = False
                self._notify_listeners()
                return True

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

    async def async_push_tiles(self, *, force: bool = False) -> bool:
        """Push changed card presentation without rebuilding the LVGL tree."""
        async with self._tile_push_lock:
            runtime_data = self.esphome_entry.runtime_data
            await self._async_subscribe_device_preferences()
            action = self._find_api_action(API_ACTION_SET_TILES)
            payload = json.dumps(
                presentation_payload(
                    self.hass,
                    self.tile_cards,
                    self.accent_color,
                    self.device_locale,
                ),
                ensure_ascii=False,
                separators=(",", ":"),
            )
            if not force and payload == self._last_tile_payload:
                return True
            if runtime_data is None or not runtime_data.available or action is None:
                return False
            try:
                await runtime_data.client.execute_service(action, {"payload": payload})
            except (APIConnectionError, TimeoutError) as err:
                _LOGGER.debug("Unable to update home cards: %s", err)
                return False
            self._last_tile_payload = payload
            return True

    async def async_press_tile(self, slot: int) -> None:
        """Execute the conservative action assigned to one card slot."""
        card = next((card for card in self.tile_cards if card["slot"] == slot), None)
        if card is None:
            return
        action = resolve_action(self.hass, card)
        if action is None:
            _LOGGER.debug("Tile %u has no executable action", slot)
            return
        await self.hass.services.async_call(
            action.domain, action.service, action.data, blocking=False
        )

    async def async_show_notification(
        self, title: str, message: str, icon: str, duration_ms: int
    ) -> None:
        """Present a notification through the native ESPHome API session."""
        runtime_data = self.esphome_entry.runtime_data
        action = self._find_api_action(API_ACTION_SHOW_NOTIFICATION)
        if runtime_data is None or not runtime_data.available or action is None:
            raise HomeAssistantError("Atmosfera Echo Hub is not available")
        try:
            await runtime_data.client.execute_service(
                action,
                {
                    "title": title,
                    "message": message,
                    "icon": icon,
                    "duration_ms": duration_ms,
                },
            )
        except (APIConnectionError, TimeoutError) as err:
            raise HomeAssistantError(
                "Unable to show a notification on Atmosfera Echo Hub"
            ) from err

    async def async_dismiss_notification(self) -> None:
        """Dismiss the active device notification."""
        runtime_data = self.esphome_entry.runtime_data
        action = self._find_api_action(API_ACTION_DISMISS_NOTIFICATION)
        if runtime_data is None or not runtime_data.available or action is None:
            return
        try:
            await runtime_data.client.execute_service(action, {})
        except (APIConnectionError, TimeoutError):
            return

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
