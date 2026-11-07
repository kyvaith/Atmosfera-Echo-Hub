"""Set up one isolated set of Atmosfera demonstration entities."""

from homeassistant.config_entries import ConfigFlow


class AtmosferaDemoConfigFlow(ConfigFlow, domain="atmosfera_demo"):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")
        return self.async_create_entry(title="Atmosfera Demo", data={})
