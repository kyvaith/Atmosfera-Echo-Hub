"""Dynamic camera source select for Atmosfera Echo Hub."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .controller import CameraBridge


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the runtime camera source selector."""
    async_add_entities([CameraSourceSelect(entry.runtime_data)])


class CameraSourceSelect(SelectEntity):
    """Choose which configured HA camera is displayed."""

    _attr_has_entity_name = True
    _attr_name = "Camera source"
    _attr_should_poll = False

    def __init__(self, bridge: CameraBridge) -> None:
        self._bridge = bridge
        self._attr_unique_id = f"{bridge.device_id}_camera_source"
        # Link the helper entity to the existing ESPHome device without adding
        # this helper config entry to that device.
        self.device_entry = bridge.device_entry

    @property
    def available(self) -> bool:
        return self._bridge.available and bool(self._bridge.options)

    @property
    def options(self) -> list[str]:
        return self._bridge.options

    @property
    def current_option(self) -> str | None:
        return self._bridge.current_option

    async def async_select_option(self, option: str) -> None:
        await self._bridge.async_select_source(option)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(self._bridge.add_listener(self._handle_bridge_update))

    @callback
    def _handle_bridge_update(self) -> None:
        self.async_write_ha_state()
