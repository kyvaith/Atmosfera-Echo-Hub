"""Home Assistant support for Atmosfera Echo Hub product settings."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTR_NODE_NAME,
    ATTR_SLOT,
    ATTR_CARD_ID,
    ATTR_REVISION,
    ATTR_SOURCE,
    ATTR_PAYLOAD,
    CONF_CAMERAS,
    CONF_DEVICE_ID,
    DOMAIN,
    PLATFORMS,
    SERVICE_DOORBELL_PREVIEW,
    SERVICE_REPORT_CAMERA_SOURCE,
    SERVICE_REPORT_TILE_PRESS,
    SERVICE_REPORT_TILE_CONTEXT_PRESS,
    SERVICE_REPORT_LIGHT_CONTROL,
    SERVICE_REPORT_ENTITY_CONTROL,
)
from .camera_proxy import AtmosferaCameraStreamView
from .controller import CameraBridge
from .panel import async_setup_panel
from .layout import CAROUSEL_SLOT_COUNT, LayoutError, MAX_REVISION, parse_report_integer
from .light_control import ProtocolError, decode as decode_light_control
from .light_control_transport import async_route_report, async_route_entity_report
from .entity_control_codec import decode_report as decode_entity_control
from .notification_transport import async_route_notification

_LOGGER = logging.getLogger(__name__)


def _report_number(minimum: int, maximum: int, name: str):
    def validate(value):
        try:
            return parse_report_integer(value, minimum, maximum, name)
        except LayoutError as err:
            raise vol.Invalid(str(err)) from err
    return validate

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): cv.string,
                vol.Optional(CONF_CAMERAS, default=[]): vol.All(
                    cv.ensure_list, [cv.entity_id]
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the device-to-HA source synchronization action."""

    hass.http.register_view(AtmosferaCameraStreamView(hass))
    await async_setup_panel(hass)

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

    async def async_doorbell_preview(call: ServiceCall) -> dict[str, str]:
        matches = [
            entry.runtime_data
            for entry in hass.config_entries.async_loaded_entries(DOMAIN)
            if entry.runtime_data.device_id == call.data[CONF_DEVICE_ID]
        ]
        if len(matches) != 1:
            raise HomeAssistantError("Select a configured Atmosfera display")
        return await matches[0].async_doorbell_preview(
            call.data["camera_entity_id"],
            call.data["duration_seconds"],
            call.data.get("event_id"),
            call.context,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DOORBELL_PREVIEW,
        async_doorbell_preview,
        schema=vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): cv.string,
                vol.Required("camera_entity_id"): cv.entity_id,
                vol.Optional("duration_seconds", default=35): vol.All(
                    vol.Coerce(int), vol.Range(min=15, max=90)
                ),
                vol.Optional("event_id"): vol.All(cv.string, vol.Length(min=1, max=64)),
            }
        ),
        supports_response=SupportsResponse.OPTIONAL,
    )

    async def async_report_tile_press(call: ServiceCall) -> None:
        node_name: str = call.data[ATTR_NODE_NAME]
        slot: int = call.data[ATTR_SLOT]
        for entry in hass.config_entries.async_loaded_entries(DOMAIN):
            bridge: CameraBridge = entry.runtime_data
            if bridge.node_name == node_name:
                await bridge.async_press_tile(slot, context=call.context)
                return
        _LOGGER.debug("Ignored tile press from unknown node %s", node_name)

    hass.services.async_register(
        DOMAIN,
        SERVICE_REPORT_TILE_PRESS,
        async_report_tile_press,
        schema=vol.Schema(
            {
                vol.Required(ATTR_NODE_NAME): cv.string,
                vol.Required(ATTR_SLOT): vol.All(vol.Coerce(int), vol.Range(min=0, max=CAROUSEL_SLOT_COUNT - 1)),
            }
        ),
    )
    async def async_report_tile_context_press(call: ServiceCall) -> None:
        for entry in hass.config_entries.async_loaded_entries(DOMAIN):
            bridge: CameraBridge = entry.runtime_data
            if bridge.node_name == call.data[ATTR_NODE_NAME]:
                await bridge.async_press_tile(
                    call.data[ATTR_SLOT], card_id=call.data[ATTR_CARD_ID],
                    revision=call.data[ATTR_REVISION], context=call.context,
                )
                return

    hass.services.async_register(
        DOMAIN, SERVICE_REPORT_TILE_CONTEXT_PRESS, async_report_tile_context_press,
        schema=vol.Schema({
            vol.Required(ATTR_NODE_NAME): cv.string,
            vol.Required(ATTR_SLOT): _report_number(0, CAROUSEL_SLOT_COUNT - 1, ATTR_SLOT),
            vol.Required(ATTR_CARD_ID): vol.All(cv.string, vol.Match(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")),
            vol.Required(ATTR_REVISION): _report_number(0, MAX_REVISION, ATTR_REVISION),
        }),
    )
    def light_payload(value):
        if not isinstance(value, str):
            raise vol.Invalid("Expected bounded JSON text")
        try:
            message = decode_light_control(value)
            if message["kind"] not in {"open", "command", "close", "cancel_open"}:
                raise ProtocolError("direction")
        except ProtocolError as err:
            raise vol.Invalid(str(err)) from err
        return value

    async def async_report_light_control(call: ServiceCall) -> None:
        try:
            await async_route_report(hass, call.data[ATTR_NODE_NAME], call.data[ATTR_PAYLOAD], call.context)
        except ProtocolError:
            _LOGGER.debug("Rejected light control report")

    hass.services.async_register(
        DOMAIN, SERVICE_REPORT_LIGHT_CONTROL, async_report_light_control,
        schema=vol.Schema({
            vol.Required(ATTR_NODE_NAME): vol.All(cv.string, vol.Length(min=1, max=128)),
            vol.Required(ATTR_PAYLOAD): light_payload,
        }, extra=vol.PREVENT_EXTRA),
    )
    def entity_payload(value):
        if not isinstance(value, str):
            raise vol.Invalid("Expected bounded JSON text")
        try:
            decode_entity_control(value)
        except ProtocolError as error:
            raise vol.Invalid(str(error)) from error
        return value

    async def async_report_entity_control(call: ServiceCall) -> None:
        try:
            await async_route_entity_report(hass, call.data[ATTR_NODE_NAME], call.data[ATTR_PAYLOAD], call.context)
        except ProtocolError:
            _LOGGER.debug("Rejected entity control report")

    hass.services.async_register(
        DOMAIN, SERVICE_REPORT_ENTITY_CONTROL, async_report_entity_control,
        schema=vol.Schema({
            vol.Required(ATTR_NODE_NAME): vol.All(cv.string, vol.Length(min=1, max=128)),
            vol.Required(ATTR_PAYLOAD): entity_payload,
        }, extra=vol.PREVENT_EXTRA),
    )
    async def async_report_notification(call: ServiceCall) -> None:
        await async_route_notification(hass, call.data[ATTR_NODE_NAME], call.data[ATTR_PAYLOAD], call.context)

    hass.services.async_register(
        DOMAIN, "report_notification", async_report_notification,
        schema=vol.Schema({
            vol.Required(ATTR_NODE_NAME): vol.All(cv.string, vol.Length(min=1, max=128)),
            vol.Required(ATTR_PAYLOAD): vol.All(cv.string, vol.Length(max=512)),
        }, extra=vol.PREVENT_EXTRA),
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
    """Apply card changes without restarting camera transport or its listeners."""
    bridge: CameraBridge | None = entry.runtime_data
    if bridge is not None and bridge.async_apply_tile_options():
        return
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the camera bridge."""
    bridge: CameraBridge = entry.runtime_data
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await bridge.async_shutdown()
    return unloaded
