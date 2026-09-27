"""Notification entity for the Atmosfera display overlay."""

from __future__ import annotations

from homeassistant.components.notify import NotifyEntity, NotifyEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .controller import CameraBridge
from .text import plain_text


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Create one notification target for the selected ESPHome device."""
    async_add_entities([AtmosferaNotifyEntity(entry.runtime_data)])


class AtmosferaNotifyEntity(NotifyEntity):
    """Send a bounded text notification to the display."""

    _attr_has_entity_name = True
    _attr_name = "Display notifications"
    _attr_should_poll = False
    _attr_supported_features = NotifyEntityFeature.TITLE

    def __init__(self, bridge: CameraBridge) -> None:
        self._bridge = bridge
        self._attr_unique_id = f"{bridge.device_id}_display_notifications"
        self.device_entry = bridge.device_entry

    @property
    def available(self) -> bool:
        runtime_data = self._bridge.esphome_entry.runtime_data
        return bool(runtime_data is not None and runtime_data.available)

    async def async_send_message(
        self,
        message: str,
        title: str | None = None,
    ) -> None:
        """Show a Material bottom-sheet notification."""
        await self._bridge.async_show_notification(
            plain_text(title or "Home Assistant", 64),
            plain_text(message, 384),
            "\ue7f4",
            6000,
        )
