"""An activity remote with no external command transport."""

from homeassistant.components.remote import ATTR_ACTIVITY, RemoteEntity, RemoteEntityFeature


async def async_setup_entry(hass, entry, add):
    add([DemoActivityRemote()])


class DemoActivityRemote(RemoteEntity):
    entity_id = "remote.atmosfera_demo_remote"
    _attr_name = "Atmosfera Demo Remote"
    _attr_unique_id = "atmosfera_demo_remote"
    _attr_should_poll = False
    _attr_is_on = True
    _attr_current_activity = "Music"
    _attr_activity_list = ["Music", "Cinema", "Radio"]
    _attr_supported_features = RemoteEntityFeature.ACTIVITY

    async def async_turn_on(self, **kwargs):
        activity = kwargs.get(ATTR_ACTIVITY)
        if activity in self._attr_activity_list:
            self._attr_current_activity = activity
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._attr_is_on = False
        self.async_write_ha_state()
