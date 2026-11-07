"""Simulation-only button platform."""

from uuid import uuid4

from homeassistant.components.button import ButtonEntity
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry

from .entities import demo_platform


async def async_setup_entry(hass, entry, add):
    await demo_platform("button")(hass, entry, add)
    add([DemoAttention("notice", "Test powiadomienia"), DemoAttention("doorbell", "Test dzwonka")])


class DemoAttention(ButtonEntity):
    _attr_should_poll = False

    def __init__(self, kind, title):
        self.kind = kind
        self.entity_id = f"button.atmosfera_demo_{kind}"
        self._attr_unique_id = self.entity_id
        self._attr_name = title

    async def async_press(self):
        entries = self.hass.config_entries.async_loaded_entries("atmosfera_echo_hub")
        if len(entries) != 1:
            raise HomeAssistantError("Choose one configured Atmosfera display for the demo")
        bridge = entries[0].runtime_data
        if self.kind == "doorbell":
            source = next((source for source in bridge.sources
                           if source.entity_id == "camera.atmosfera_demo_camera"), None)
            if source is None:
                raise HomeAssistantError("Add the Atmosfera demo camera to the display's camera list")
            await self.hass.services.async_call(
                "atmosfera_echo_hub", "doorbell_preview",
                {"device_id": bridge.device_id, "camera_entity_id": source.entity_id,
                 "event_id": uuid4().hex, "duration_seconds": 25},
                blocking=True, return_response=True,
            )
            return
        entity = entity_registry.async_get(self.hass).async_get_entity_id(
            "notify", "atmosfera_echo_hub", f"{bridge.device_id}_display_notifications"
        )
        if entity is None:
            raise HomeAssistantError("Atmosfera display notifications are unavailable")
        await self.hass.services.async_call(
            "notify", "send_message", {"entity_id": entity, "title": "Atmosfera Demo",
                                       "message": "Przykładowe powiadomienie z Home Assistanta."},
            blocking=True,
        )
