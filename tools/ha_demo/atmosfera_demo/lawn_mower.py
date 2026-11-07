"""A mower that only changes its simulated activity."""

from homeassistant.components.lawn_mower import (
    LawnMowerActivity,
    LawnMowerEntity,
    LawnMowerEntityFeature,
)


async def async_setup_entry(hass, entry, add):
    add([DemoMower()])


class DemoMower(LawnMowerEntity):
    entity_id = "lawn_mower.atmosfera_demo_mower"
    _attr_name = "Atmosfera Demo Mower"
    _attr_unique_id = "atmosfera_demo_mower"
    _attr_should_poll = False
    _attr_activity = LawnMowerActivity.DOCKED
    _attr_supported_features = (
        LawnMowerEntityFeature.START_MOWING | LawnMowerEntityFeature.PAUSE | LawnMowerEntityFeature.DOCK
    )

    async def async_start_mowing(self):
        self._attr_activity = LawnMowerActivity.MOWING
        self.async_write_ha_state()

    async def async_pause(self):
        self._attr_activity = LawnMowerActivity.PAUSED
        self.async_write_ha_state()

    async def async_dock(self):
        self._attr_activity = LawnMowerActivity.DOCKED
        self.async_write_ha_state()
