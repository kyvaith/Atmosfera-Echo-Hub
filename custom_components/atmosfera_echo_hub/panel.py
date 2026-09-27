"""Authenticated Home Assistant panel for editing display cards."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.components import panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .cards import ICONS, PALETTES, SUPPORTED_DOMAINS, normalize_cards
from .const import CONF_TILES, DOMAIN, PANEL_URL_PATH, PANEL_WEBCOMPONENT

PANEL_ASSET_VERSION = "0.3.3"

STATIC_URL = "/atmosfera_echo_hub_static"


async def async_setup_panel(hass: HomeAssistant) -> None:
    """Register the static editor and its authenticated WebSocket commands."""
    static_path = Path(__file__).parent / "www"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL, str(static_path), False)]
    )
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_WEBCOMPONENT,
        frontend_url_path=PANEL_URL_PATH,
        module_url=f"{STATIC_URL}/tile-editor.js?v={PANEL_ASSET_VERSION}",
        sidebar_title="Atmosfera",
        sidebar_icon="mdi:view-dashboard-edit",
        require_admin=True,
    )
    websocket_api.async_register_command(hass, websocket_get_tiles)
    websocket_api.async_register_command(hass, websocket_save_tiles)


def _entry_payload(hass: HomeAssistant) -> list[dict[str, Any]]:
    return [
        {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "cards": normalize_cards(
                entry.options.get(CONF_TILES, entry.data.get(CONF_TILES))
            ),
        }
        for entry in hass.config_entries.async_loaded_entries(DOMAIN)
    ]


@websocket_api.websocket_command(
    {vol.Required("type"): "atmosfera_echo_hub/tiles/get"}
)
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_get_tiles(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return device configs and editor choices."""
    connection.send_result(
        msg["id"],
        {
            "version": 1,
            "entries": _entry_payload(hass),
            "icons": sorted(ICONS),
            "palettes": sorted(PALETTES),
            "domains": sorted(SUPPORTED_DOMAINS),
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "atmosfera_echo_hub/tiles/save",
        vol.Required("entry_id"): str,
        vol.Required("cards"): list,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_save_tiles(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Validate and persist one card layout."""
    entry = hass.config_entries.async_get_entry(msg["entry_id"])
    if entry is None or entry.domain != DOMAIN:
        connection.send_error(msg["id"], "entry_not_found", "Unknown Atmosfera device")
        return
    cards = normalize_cards(msg["cards"])
    options = dict(entry.options)
    options[CONF_TILES] = cards
    hass.config_entries.async_update_entry(entry, options=options)
    connection.send_result(msg["id"], {"cards": cards})
