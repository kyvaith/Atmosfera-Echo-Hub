"""Opt-in test devices for the Atmosfera dashboard."""

from .entities import DEMO_PLATFORMS

PLATFORMS = tuple(DEMO_PLATFORMS) + ("lawn_mower", "remote")


async def async_setup_entry(hass, entry):
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
