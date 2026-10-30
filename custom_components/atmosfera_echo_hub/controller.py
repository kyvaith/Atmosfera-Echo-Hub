"""Runtime bridge between Home Assistant cameras and an ESPHome display."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
import json
import logging
from urllib.parse import quote, urlencode

from aioesphomeapi import APIConnectionError, EntityState, UserService
from aioesphomeapi.model import SupportsResponseType

from homeassistant.components.camera.helper import get_camera_from_entity_id
from homeassistant.components.network import async_get_source_ip
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_FRIENDLY_NAME, CONF_HOST, EVENT_CORE_CONFIG_UPDATE
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
    entry_layout,
    normalize_cards,
    ordinary_action_availability,
    presentation_payload,
    resolve_action,
)
from .const import (
    API_ACTION_SELECT_SOURCE,
    API_ACTION_DISMISS_NOTIFICATION,
    API_ACTION_SHOW_NOTIFICATION,
    API_ACTION_SET_SOURCES,
    API_ACTION_SET_TILES,
    API_ACTION_GET_TILE_STATUS,
    CONF_CAMERAS,
    CONF_DEVICE_ID,
    CONF_STREAM_FPS,
    CONF_STREAM_HEIGHT,
    CONF_STREAM_WIDTH,
    CONF_ACCENT_COLOR,
    DEFAULT_ACCENT_COLOR,
    DEFAULT_STREAM_FPS,
    DEFAULT_STREAM_HEIGHT,
    DEFAULT_STREAM_WIDTH,
    RETRY_INTERVAL_SECONDS,
    TOKEN_REFRESH_INTERVAL,
)
from .text import plain_text
from .tile_palette import observed_accent
from .layout import PROFILE_ID
from .light_control_transport import LightControlTransport

_LOGGER = logging.getLogger(__name__)
_NATIVE_STATUS_REQUERY_DELAYS = (0.3, 0.8, 1.5)


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
        self.layout = entry_layout(entry.options, entry.data)
        self.tile_cards = normalize_cards(self.layout["cards"])
        self.saved_revision = self.layout["revision"]
        self.sent_revision: int | None = None
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
        self._preference_lock = asyncio.Lock()
        self._last_tile_payload = ""
        self._missing_camera_entity_ids: tuple[str, ...] = ()
        self.device_locale: str | None = None
        self._device_preference_client = None
        self._device_preference_keys: dict[int, str] = {}
        self._observed_accent_color: str | None = None
        self._device_preference_generation = 0
        self._tile_unsubscribe: CALLBACK_TYPE | None = None
        self._closed = False
        self._connection_epoch = 0
        self._native_status_lock = asyncio.Lock()
        self._native_status_epoch = -1
        self._context_press_version = 0
        self._press_enabled_version = 0
        self._native_context_required = False
        self.accepted_revision: int | None = None
        self.snapshot_ready: bool | None = None
        self.pending_slots: int | None = None
        self._native_status_requery_task: asyncio.Task | None = None
        self._native_status_requery_key: tuple[int, int] | None = None
        self._background_tasks: set[asyncio.Task] = set()
        self._active_push_tasks: set[asyncio.Task] = set()
        self._light_control = LightControlTransport(self)

    @property
    def tile_device_available(self) -> bool:
        runtime_data = self.esphome_entry.runtime_data
        return not self._closed and runtime_data is not None and runtime_data.available

    def _spawn_background(self, coroutine) -> asyncio.Task:
        task = self.hass.async_create_task(coroutine)
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        return task

    def _cancel_native_status_requery(self) -> None:
        if self._native_status_requery_task is not None:
            self._native_status_requery_task.cancel()
        self._native_status_requery_task = None
        self._native_status_requery_key = None

    def _schedule_native_status_requery(self, revision: int, epoch: int) -> None:
        """Bound source-ready telemetry; never render or poll hidden pages."""
        if (self._closed or not self.tile_device_available or not self._native_context_required
                or self.saved_revision != revision or self.sent_revision != revision
                or self._connection_epoch != epoch
                or (self.accepted_revision == revision and self.snapshot_ready is True)):
            return
        key = (epoch, revision)
        if self._native_status_requery_key == key:
            return
        self._cancel_native_status_requery()
        self._native_status_requery_key = key
        self._native_status_requery_task = self._spawn_background(
            self._async_requery_native_status(revision, epoch)
        )

    async def _async_requery_native_status(self, revision: int, epoch: int) -> None:
        try:
            for delay in _NATIVE_STATUS_REQUERY_DELAYS:
                await asyncio.sleep(delay)
                if (self._closed or not self.tile_device_available
                        or self.saved_revision != revision or self.sent_revision != revision
                        or self._connection_epoch != epoch):
                    return
                await self._async_refresh_native_status(force=True)
                if self.accepted_revision == revision and self.snapshot_ready is True:
                    return
        finally:
            if self._native_status_requery_task is asyncio.current_task():
                self._native_status_requery_task = None
                self._native_status_requery_key = None

    def _replace_tile_subscription(self) -> None:
        """Replace exactly the card listener, preserving camera subscriptions."""
        if self._tile_unsubscribe is not None:
            self._tile_unsubscribe()
            self._tile_unsubscribe = None
        if self.tile_entity_ids and not self._closed:
            self._tile_unsubscribe = async_track_state_change_event(
                self.hass, self.tile_entity_ids, self._tile_state_changed
            )

    @callback
    def async_apply_tile_options(self) -> bool:
        """Hot-apply card/accent options; return false for camera configuration."""
        options, data = self.entry.options, self.entry.data
        camera_settings = (
            (CONF_CAMERAS, self.camera_entity_ids),
            (CONF_STREAM_WIDTH, self.stream_width),
            (CONF_STREAM_HEIGHT, self.stream_height),
            (CONF_STREAM_FPS, self.stream_fps),
        )
        if any(options.get(key, data.get(key, current)) != current
               for key, current in camera_settings):
            return False
        previous = (self.saved_revision, self.layout["version"])
        self.layout = entry_layout(options, data)
        if self.saved_revision != self.layout["revision"]:
            self._cancel_native_status_requery()
            self.snapshot_ready = None
            self.pending_slots = None
        self.tile_cards = normalize_cards(self.layout["cards"])
        self.saved_revision = self.layout["revision"]
        if previous != (self.saved_revision, self.layout["version"]) and (light := getattr(self, "_light_control", None)):
            light.invalidate_selection()
        self.tile_entity_ids = card_entity_ids(self.tile_cards)
        self.accent_color = options.get(
            CONF_ACCENT_COLOR, data.get(CONF_ACCENT_COLOR, DEFAULT_ACCENT_COLOR)
        )
        self._replace_tile_subscription()
        self._last_tile_payload = ""
        self.async_schedule_tile_push(delay=0)
        return True

    @property
    def observed_accent_color(self) -> str | None:
        """Last valid accent observed on this preference connection, never an option write."""
        runtime = self.esphome_entry.runtime_data
        if (self._closed or runtime is None or not runtime.available
                or runtime.client is not getattr(self, "_device_preference_client", None)):
            return None
        return getattr(self, "_observed_accent_color", None)

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
        self._replace_tile_subscription()
        self._unsubscribers.append(
            self.hass.bus.async_listen(EVENT_CORE_CONFIG_UPDATE, self._core_config_updated)
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
        if self._closed:
            return
        self._connection_epoch += 1
        if light := getattr(self, "_light_control", None):
            light.invalidate_connection()
        self._cancel_native_status_requery()
        self._last_tile_payload = ""
        self.sent_revision = None
        self._native_status_epoch = -1
        self._context_press_version = 0
        self._press_enabled_version = 0
        self._native_context_required = False
        self.accepted_revision = None
        self.snapshot_ready = None
        self.pending_slots = None
        runtime_data = self.esphome_entry.runtime_data
        if runtime_data is None or not runtime_data.available:
            self._device_preference_client = None
            self._device_preference_keys.clear()
            self.available = False
            self._notify_listeners()
            return

        self._spawn_background(self._async_subscribe_device_preferences())

        # ESPHome announces availability immediately before replacing its
        # retained user-service catalog. Delay the first attempt slightly;
        # async_push_sources() retains the normal retry when setup takes longer.
        self.async_schedule_push(delay=0.25)
        self.async_schedule_tile_push(delay=0.5)

    async def async_shutdown(self) -> None:
        """Stop tracking runtime state."""
        self._closed = True
        self._observed_accent_color = None
        self._press_enabled_version = 0
        if light := getattr(self, "_light_control", None):
            await light.async_shutdown()
        self._cancel_native_status_requery()
        if self._remove_debounce is not None:
            self._remove_debounce()
            self._remove_debounce = None
        if self._remove_tile_debounce is not None:
            self._remove_tile_debounce()
            self._remove_tile_debounce = None
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers.clear()
        self._replace_tile_subscription()
        self._device_preference_keys.clear()
        current = asyncio.current_task()
        tasks = (self._background_tasks | self._active_push_tasks) - {current}
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._background_tasks.clear()
        self._active_push_tasks.clear()

    async def _async_subscribe_device_preferences(self) -> None:
        """Serialize subscription setup across source and tile refresh tasks."""
        async with self._preference_lock:
            await self._async_subscribe_device_preferences_locked()

    async def _async_subscribe_device_preferences_locked(self) -> None:
        """Mirror the device's locale and accent before publishing card state."""
        runtime_data = self.esphome_entry.runtime_data
        if self._closed or runtime_data is None or not runtime_data.available:
            return
        client = runtime_data.client
        epoch = self._connection_epoch
        if client is self._device_preference_client:
            return
        try:
            entities, _services = await client.list_entities_services()
        except (APIConnectionError, TimeoutError):
            return
        if self._closed or epoch != self._connection_epoch or runtime_data is not self.esphome_entry.runtime_data:
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
        # This preview cache belongs to this existing subscription only.
        # Keep the legacy wire/locale handler and its dispatch behavior intact.
        self._device_preference_generation = getattr(self, "_device_preference_generation", 0) + 1
        generation = self._device_preference_generation
        self._observed_accent_color = None

        @callback
        def state_changed(state):
            self._device_preference_state_changed(state)
            runtime = self.esphome_entry.runtime_data
            if (not self._closed and generation == self._device_preference_generation
                    and runtime is not None and runtime.available
                    and runtime.client is client and self._device_preference_client is client
                    and keys.get(state.key) == "accent"):
                normalized = observed_accent(getattr(state, "state", None))
                if normalized is not None:
                    self._observed_accent_color = normalized

        client.subscribe_states(state_changed)

    @callback
    def _device_preference_state_changed(self, state: EntityState) -> None:
        """Accept user changes made on the device before the next HA refresh."""
        if self._closed:
            return
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
                self._spawn_background(self._async_load_device_locale(locale))
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
        if light := getattr(self, "_light_control", None):
            light.state_changed(event)
        self.async_schedule_tile_push(delay=0.18)

    @callback
    def _core_config_updated(self, event: Event) -> None:
        """Reproject Sun local captions when UTC source attributes stay unchanged."""
        if (self._closed or "time_zone" not in event.data
                or not any(card["visible"] and card["entity_id"].startswith("sun.") for card in self.tile_cards)):
            return
        self.async_schedule_tile_push(delay=0)

    async def _periodic_refresh(self, _now) -> None:
        await self.async_push_sources()
        await self.async_push_tiles(force=True)

    @callback
    def async_schedule_push(self, delay: float = 1) -> None:
        """Debounce camera state changes and token rotations."""
        if self._closed:
            return
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
        if self._closed:
            return
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
        """Own source push work until the existing camera request completes."""
        if self._closed:
            return False
        task = asyncio.current_task()
        self._active_push_tasks.add(task)
        try:
            return await self._async_push_sources()
        finally:
            self._active_push_tasks.discard(task)

    async def _async_push_sources(self) -> bool:
        """Push names and short-lived signed camera URLs to the display."""
        async with self._push_lock:
            if self._closed:
                return False
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
        """Own in-flight tile work so unloading cannot resurrect its retries."""
        if self._closed:
            return False
        task = asyncio.current_task()
        self._active_push_tasks.add(task)
        try:
            return await self._async_push_tiles(force=force)
        finally:
            self._active_push_tasks.discard(task)

    async def _async_push_tiles(self, *, force: bool = False) -> bool:
        """Push changed card presentation without rebuilding the LVGL tree."""
        async with self._tile_push_lock:
            await self._async_subscribe_device_preferences()
            if self._closed:
                return False
            # The preference request may await through a reconnect. Bind the
            # actual send and its result to the current connection afterwards.
            runtime_data = self.esphome_entry.runtime_data
            epoch = self._connection_epoch
            light = getattr(self, "_light_control", None)
            if light is not None:
                await light.async_negotiate()
                if self._closed or epoch != self._connection_epoch or runtime_data is not self.esphome_entry.runtime_data:
                    return False
            # Negotiate optional ordinary-action availability before its first
            # payload. Context acceptance still needs the normal post-send read.
            if (self._native_status_epoch != epoch and any(
                    ordinary_action_availability(card)
                    for card in self.tile_cards)):
                await self._async_refresh_native_status()
                if self._closed or epoch != self._connection_epoch or runtime_data is not self.esphome_entry.runtime_data:
                    return False
            revision = self.saved_revision
            action = self._find_api_action(API_ACTION_SET_TILES)
            wire = presentation_payload(
                self.hass, self.tile_cards, self.accent_color, self.device_locale,
                light_control_supported=light.supported if light is not None else False,
                number_control_supported=light.number_supported if light is not None else False,
                press_enabled_supported=getattr(self, "_press_enabled_version", 0) == 1,
            )
            # Older v1 renderers ignore this optional metadata. It provides a
            # correlation point for a future native acknowledgement; successful
            # API dispatch alone remains sent, never applied.
            wire["revision"] = revision
            wire["profile"] = PROFILE_ID
            payload = json.dumps(
                wire,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            if not force and payload == self._last_tile_payload and self.sent_revision == revision:
                if self._native_context_required and self._context_press_version != 1:
                    await self._async_refresh_native_status()
                return True
            if runtime_data is None or not runtime_data.available or action is None:
                return False
            try:
                await runtime_data.client.execute_service(action, {"payload": payload})
            except (APIConnectionError, TimeoutError) as err:
                _LOGGER.debug("Unable to update home cards: %s", err)
                return False
            if self._closed or epoch != self._connection_epoch or runtime_data is not self.esphome_entry.runtime_data:
                return False
            self._last_tile_payload = payload
            self.sent_revision = revision
            # The native renderer has no context contract until its first
            # ID/revision-bearing payload. Query after sending, not before.
            await self._async_refresh_native_status(
                force=self.accepted_revision != revision or self.snapshot_ready is not True
            )
            self._schedule_native_status_requery(revision, epoch)
            return True

    async def _async_refresh_native_status(self, *, force: bool = False) -> None:
        """Negotiate only an explicitly response-capable native status action."""
        async with self._native_status_lock:
            if self._closed or not self.tile_device_available:
                return
            epoch = self._connection_epoch
            if (not force and self._native_status_epoch == epoch
                    and self._context_press_version == 1
                    and self.accepted_revision == self.saved_revision
                    and self.snapshot_ready is True):
                return
            # A missing, failed or malformed fresh probe must not retain an
            # earlier positive optional capability in this connection epoch.
            self._press_enabled_version = 0
            action = self._find_api_action(API_ACTION_GET_TILE_STATUS)
            if action is None or getattr(action, "supports_response", None) not in (
                SupportsResponseType.OPTIONAL, SupportsResponseType.ONLY,
            ):
                return
            self._native_context_required = True
            runtime_data = self.esphome_entry.runtime_data
            try:
                response = await runtime_data.client.execute_service(
                    action, {}, return_response=True, timeout=5.0
                )
                if response is None or not response.success or not isinstance(response.response_data, bytes):
                    return
                if len(response.response_data) > 2048:
                    return
                status = json.loads(response.response_data)
            except (APIConnectionError, TimeoutError, ValueError, UnicodeError):
                return
            if self._closed or epoch != self._connection_epoch or runtime_data is not self.esphome_entry.runtime_data:
                return
            if not isinstance(status, dict) or status.get("profile") != PROFILE_ID:
                return
            if type(status.get("context_press_version")) is not int or status["context_press_version"] not in (0, 1):
                return
            press_enabled_version = status.get("press_enabled_version", 0)
            if type(press_enabled_version) is not int or press_enabled_version not in (0, 1):
                return
            accepted = status.get("revision")
            ready = status.get("snapshot_ready")
            if type(accepted) is not int or not 0 <= accepted <= 2**53 - 1 or type(ready) is not bool:
                return
            configured = status.get("configured_context_version")
            if type(configured) is not int or configured not in (0, 1):
                return
            pending = status.get("pending_slots")
            if pending is not None and (
                type(pending) is not int or not 0 <= pending < 2**16
                or ready != (pending == 0)
            ):
                return
            self._context_press_version = status["context_press_version"]
            self._press_enabled_version = press_enabled_version
            self._native_status_epoch = epoch
            self.accepted_revision = accepted if configured == 1 else None
            self.snapshot_ready = ready if configured == 1 else None
            self.pending_slots = pending if configured == 1 else None

    @property
    def context_press_version(self) -> int:
        return self._context_press_version

    def light_control_status(self) -> dict:
        light = getattr(self, "_light_control", None)
        return light.status() if light is not None else {"native_control_types": [], "light_control_status": "unsupported"}

    async def async_report_light_control(self, payload: str, context) -> None:
        light = getattr(self, "_light_control", None)
        if light is not None:
            await light.async_report(payload, context)

    async def async_press_tile(self, slot: int, *, card_id=None, revision=None, context=None) -> None:
        """Execute the conservative action assigned to one card slot."""
        # The legacy report has no configuration revision. Suppress its
        # obvious pending/disconnected window without claiming this is a
        # native application acknowledgement or complete stale-tap protection.
        if not self.tile_device_available or self.sent_revision != self.saved_revision:
            return
        card = next((card for card in self.tile_cards if card["slot"] == slot), None)
        if self._closed or card is None:
            return
        if card_id is None and revision is None:
            if self._native_context_required or self._context_press_version:
                return
        elif (
            self._context_press_version != 1 or not card_id
            or card_id != card.get("id") or type(revision) is not int
            or revision != self.saved_revision
        ):
            return
        action = resolve_action(self.hass, card)
        if action is None:
            _LOGGER.debug("Tile %u has no executable action", slot)
            return
        try:
            await self.hass.services.async_call(
                action.domain, action.service, action.data, blocking=False,
                context=context,
            )
        except HomeAssistantError:
            _LOGGER.warning("Configured card action could not be dispatched for slot %u", slot)

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
