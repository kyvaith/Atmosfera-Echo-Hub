"""Config flow for Atmosfera Echo Hub."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr, selector

from .const import (
    CONF_CAMERAS,
    CONF_DEVICE_ID,
    CONF_STREAM_FPS,
    CONF_STREAM_HEIGHT,
    CONF_STREAM_WIDTH,
    DEFAULT_STREAM_FPS,
    DEFAULT_STREAM_HEIGHT,
    DEFAULT_STREAM_WIDTH,
    DOMAIN,
    MAX_STREAM_FPS,
    MIN_STREAM_FPS,
)


def _schema(
    *,
    device_id: str | None = None,
    cameras: list[str] | None = None,
    stream_width: int = DEFAULT_STREAM_WIDTH,
    stream_height: int = DEFAULT_STREAM_HEIGHT,
    stream_fps: int = DEFAULT_STREAM_FPS,
):
    fields: dict[Any, Any] = {}
    if device_id is None:
        fields[vol.Required(CONF_DEVICE_ID)] = selector.DeviceSelector(
            selector.DeviceSelectorConfig(integration="esphome")
        )
    fields[vol.Required(CONF_CAMERAS, default=cameras or [])] = selector.EntitySelector(
        selector.EntitySelectorConfig(domain="camera", multiple=True, reorder=True)
    )
    fields[vol.Required(CONF_STREAM_WIDTH, default=stream_width)] = (
        selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=160,
                max=1920,
                step=8,
                mode=selector.NumberSelectorMode.BOX,
            )
        )
    )
    fields[vol.Required(CONF_STREAM_HEIGHT, default=stream_height)] = (
        selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=160,
                max=1920,
                step=8,
                mode=selector.NumberSelectorMode.BOX,
            )
        )
    )
    fields[vol.Required(CONF_STREAM_FPS, default=stream_fps)] = selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=MIN_STREAM_FPS,
            max=MAX_STREAM_FPS,
            step=1,
            mode=selector.NumberSelectorMode.SLIDER,
        )
    )
    return vol.Schema(fields)


class AtmosferaEchoHubConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure cameras exposed to one Atmosfera Echo Hub."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Select an ESPHome device and its available cameras."""
        errors: dict[str, str] = {}
        if user_input is not None:
            device = dr.async_get(self.hass).async_get(user_input[CONF_DEVICE_ID])
            if device is None or not any(
                (entry := self.hass.config_entries.async_get_entry(entry_id))
                is not None
                and entry.domain == "esphome"
                for entry_id in device.config_entries
            ):
                errors[CONF_DEVICE_ID] = "not_esphome"
            elif not user_input[CONF_CAMERAS]:
                errors[CONF_CAMERAS] = "no_cameras"
            else:
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"{device.name or 'Atmosfera Echo Hub'} cameras",
                    data={
                        CONF_DEVICE_ID: user_input[CONF_DEVICE_ID],
                        CONF_CAMERAS: list(user_input[CONF_CAMERAS]),
                        CONF_STREAM_WIDTH: int(user_input[CONF_STREAM_WIDTH]),
                        CONF_STREAM_HEIGHT: int(user_input[CONF_STREAM_HEIGHT]),
                        CONF_STREAM_FPS: int(user_input[CONF_STREAM_FPS]),
                    },
                )

        return self.async_show_form(
            step_id="user", data_schema=_schema(), errors=errors
        )

    async def async_step_import(self, import_config):
        """Create the same config entry from a one-time YAML bootstrap."""
        return await self.async_step_user(import_config)

    @staticmethod
    @callback
    def async_get_options_flow(_config_entry):
        """Return the camera selection options flow."""
        return AtmosferaEchoHubOptionsFlow()


class AtmosferaEchoHubOptionsFlow(config_entries.OptionsFlow):
    """Update cameras exposed to the display."""

    async def async_step_init(self, user_input=None):
        """Edit the camera list."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not user_input[CONF_CAMERAS]:
                errors[CONF_CAMERAS] = "no_cameras"
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_CAMERAS: list(user_input[CONF_CAMERAS]),
                        CONF_STREAM_WIDTH: int(user_input[CONF_STREAM_WIDTH]),
                        CONF_STREAM_HEIGHT: int(user_input[CONF_STREAM_HEIGHT]),
                        CONF_STREAM_FPS: int(user_input[CONF_STREAM_FPS]),
                    },
                )

        cameras = list(
            self.config_entry.options.get(
                CONF_CAMERAS, self.config_entry.data[CONF_CAMERAS]
            )
        )
        stream_width = int(
            self.config_entry.options.get(
                CONF_STREAM_WIDTH,
                self.config_entry.data.get(CONF_STREAM_WIDTH, DEFAULT_STREAM_WIDTH),
            )
        )
        stream_height = int(
            self.config_entry.options.get(
                CONF_STREAM_HEIGHT,
                self.config_entry.data.get(CONF_STREAM_HEIGHT, DEFAULT_STREAM_HEIGHT),
            )
        )
        stream_fps = int(
            self.config_entry.options.get(
                CONF_STREAM_FPS,
                self.config_entry.data.get(CONF_STREAM_FPS, DEFAULT_STREAM_FPS),
            )
        )
        return self.async_show_form(
            step_id="init",
            data_schema=_schema(
                device_id=self.config_entry.data[CONF_DEVICE_ID],
                cameras=cameras,
                stream_width=stream_width,
                stream_height=stream_height,
                stream_fps=stream_fps,
            ),
            errors=errors,
        )
