"""Home Assistant support for Atmosfera Echo Hub product settings."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTR_NODE_NAME,
    ATTR_SOURCE,
    CONF_CAMERAS,
    CONF_DEVICE_ID,
    DOMAIN,
    PLATFORMS,
    SERVICE_REPORT_CAMERA_SOURCE,
)
from .camera_proxy import AtmosferaCameraStreamView
from .controller import CameraBridge

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): cv.string,
                vol.Required(CONF_CAMERAS): vol.All(cv.ensure_list, [cv.entity_id]),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the device-to-HA source synchronization action."""

    hass.http.register_view(AtmosferaCameraStreamView(hass))

    async def async_report_camera_source(call: ServiceCall) -> None:
        node_name: str = call.data[ATTR_NODE_NAME]
        source: str = call.data[ATTR_SOURCE]
        for entry in hass.config_entries.async_loaded_entries(DOMAIN):
            bridge: CameraBridge = entry.runtime_data
            if bridge.node_name == node_name:
                bridge.async_report_source(source)
                return
        _LOGGER.debug("Ignored camera source report from unknown node %s", node_name)

    hass.services.async_register(
        DOMAIN,
        SERVICE_REPORT_CAMERA_SOURCE,
        async_report_camera_source,
        schema=vol.Schema(
            {
                vol.Required(ATTR_NODE_NAME): cv.string,
                vol.Required(ATTR_SOURCE): cv.string,
            }
        ),
    )
    if DOMAIN in config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": config_entries.SOURCE_IMPORT},
                data=config[DOMAIN],
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one display camera catalog."""
    bridge = CameraBridge(hass, entry)
    entry.runtime_data = bridge
    await bridge.async_setup()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload after the selected camera list changes."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the camera bridge."""
    bridge: CameraBridge = entry.runtime_data
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await bridge.async_shutdown()
    return unloaded
