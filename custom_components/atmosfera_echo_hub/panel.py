"""Authenticated Home Assistant layout editor and bounded configuration API."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import voluptuous as vol
from homeassistant.components import panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .cards import (
    ICONS,
    PALETTES,
    SUPPORTED_DOMAINS,
    entity_catalogue,
    entry_layout,
    normalize_accent,
    normalize_cards,
    validate_live_action,
)
from .const import (
    CONF_ACCENT_COLOR,
    CONF_CAMERAS,
    CONF_DEVICE_ID,
    CONF_LAYOUT,
    CONF_TILES,
    DEFAULT_ACCENT_COLOR,
    DOMAIN,
    PANEL_URL_PATH,
    PANEL_WEBCOMPONENT,
)
from .layout import (
    CARD_TYPES,
    LayoutError,
    device_profile,
    export_layout,
    import_layout,
    migrate_legacy,
    next_revision,
    validate_layout,
)
from .text import plain_text
from .tile_palette import derive_tile_palette, observed_accent

PANEL_ASSET_VERSION = "0.4.0.dev131"
STATIC_URL = "/atmosfera_echo_hub_static"


async def async_setup_panel(hass: HomeAssistant) -> None:
    """Register the editor and admin-only WebSocket commands."""
    await hass.http.async_register_static_paths([
        StaticPathConfig(STATIC_URL, str(Path(__file__).parent / "www"), False)
    ])
    await panel_custom.async_register_panel(
        hass, webcomponent_name=PANEL_WEBCOMPONENT, frontend_url_path=PANEL_URL_PATH,
        module_url=f"{STATIC_URL}/tile-editor.js?v={PANEL_ASSET_VERSION}",
        sidebar_title="Atmosfera", sidebar_icon="mdi:view-dashboard-edit", require_admin=True,
    )
    for command in (
        websocket_get_tiles, websocket_save_tiles, websocket_get_layout,
        websocket_save_layout, websocket_validate_layout, websocket_export_layout,
        websocket_import_layout, websocket_get_catalogue,
    ):
        websocket_api.async_register_command(hass, command)


def _entry(hass: HomeAssistant, entry_id: str):
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.domain != DOMAIN:
        raise LayoutError("entry_not_found", "Unknown Atmosfera device")
    return entry


def _layout(entry) -> dict[str, Any]:
    return entry_layout(entry.options, entry.data)


def _device_identity(hass: HomeAssistant, entry) -> dict[str, Any]:
    """Project bounded retained registry facts, never a live firmware probe."""
    device_id = entry.data.get(CONF_DEVICE_ID)
    device = (dr.async_get(hass).async_get(device_id)
              if type(device_id) is str and 0 < len(device_id) <= 256 else None)

    def text(value) -> str | None:
        if not isinstance(value, str):
            return None
        clean = "".join(character for character in plain_text(value[:320], 80)
                        if character.isprintable()).strip()
        return clean or None

    return {
        "source": "home_assistant_device_registry",
        "registry_entry_present": device is not None,
        "name": (text(getattr(device, "name_by_user", None))
                 or text(getattr(device, "name", None))),
        "manufacturer": text(getattr(device, "manufacturer", None)),
        "model": text(getattr(device, "model", None)),
        "software_version": text(getattr(device, "sw_version", None)),
    }


def _preview_accent(entry) -> int:
    """Prefer the connection-scoped device preference; options are a fallback."""
    mirrored = observed_accent(getattr(entry.runtime_data, "observed_accent_color", None))
    return normalize_accent(mirrored if mirrored is not None else entry.options.get(
        CONF_ACCENT_COLOR, entry.data.get(CONF_ACCENT_COLOR, DEFAULT_ACCENT_COLOR)
    ))


def _status(entry, layout: dict[str, Any] | None = None) -> dict[str, Any]:
    current = layout if layout is not None else _layout(entry)
    bridge = entry.runtime_data
    sent = getattr(bridge, "sent_revision", None)
    available = bool(bridge is not None and getattr(bridge, "tile_device_available", False))
    return {
        "saved_revision": current["revision"], "sent_revision": sent,
        "applied_revision": None, "device_available": available,
        "pending": sent != current["revision"],
        "accepted_revision": getattr(bridge, "accepted_revision", None),
        "snapshot_ready": getattr(bridge, "snapshot_ready", None),
        "pending_slots": getattr(bridge, "pending_slots", None),
        "context_press_version": getattr(bridge, "context_press_version", 0),
        "press_enabled_version": getattr(bridge, "press_enabled_version", 0),
        "event_press_supported": bool(getattr(bridge, "event_press_supported", False)),
        "camera_preview_supported": bool(getattr(bridge, "camera_preview_supported", False)),
        "camera_preview_entities": list(getattr(bridge, "camera_preview_entities", ())),
        "camera_catalog_generation": getattr(bridge, "_camera_catalog_generation", 0),
        **(bridge.light_control_status() if bridge is not None and hasattr(bridge, "light_control_status") else
           {"native_control_types": [], "light_control_status": "unsupported"}),
    }


def _error(connection, msg: dict[str, Any], err: LayoutError) -> None:
    connection.send_error(msg["id"], err.code, str(err))


def _legacy_cards(layout: dict[str, Any]) -> list[dict[str, Any]]:
    """Keep old readers working while preserving IDs and typed action metadata."""
    cards = normalize_cards(layout["cards"])
    for card in cards:
        if card.get("action", {}).get("kind") in ("control", "event", "camera_preview"):
            # A pre-layout reader may infer toggle from the entity domain.
            # Keep this compatibility view passive; the v3 document owns it.
            card.update(entity_id="", service="", action={"kind": "none"})
    return cards


def _save(hass: HomeAssistant, entry, expected: int, raw: Any) -> dict[str, Any]:
    current = _layout(entry)
    revision = next_revision(current["revision"], expected)
    canonical = validate_layout(raw)
    if "home_order" in canonical and "home_order" not in current and not getattr(entry.runtime_data, "carousel_supported", False):
        raise LayoutError("unsupported_carousel", "The display must be connected with carousel firmware")
    if "home_order" in current and "home_order" not in canonical:
        raise LayoutError("invalid_carousel", "The saved carousel order is required")
    _validate_actions(hass, canonical, entry)
    if canonical["revision"] != expected:
        raise LayoutError("revision_conflict", f"Draft revision differs; current revision is {current['revision']}")
    # A reserved slot is not editable, including its ID, presentation or action.
    def reserved(doc):
        return [card for card in doc["cards"] if card["slot"] < 2]
    if reserved(canonical) != reserved(current):
        raise LayoutError("reserved_slot", "Reserved hidden cards cannot be changed")
    canonical["revision"] = revision
    options = dict(entry.options)
    options[CONF_LAYOUT] = canonical
    options[CONF_TILES] = _legacy_cards(canonical)
    # No await between revision comparison and update: HA's event loop commits
    # layout + legacy mirror as one configuration entry update.
    hass.config_entries.async_update_entry(entry, options=options)
    return canonical


def _validate_actions(hass, document: dict[str, Any], entry=None) -> None:
    """Check available live capabilities without operating any entity."""
    for card in document["cards"]:
        action = card["action"]
        state = hass.states.get(card["entity_id"]) if card["entity_id"] else None
        cameras = entry.options.get(CONF_CAMERAS, entry.data.get(CONF_CAMERAS, ())) if entry is not None else ()
        if action["kind"] == "camera_preview" and (state is None or card["entity_id"] not in cameras):
            raise LayoutError("unsupported_camera", "Choose an existing camera from this display's allow-list")
        if action == {"kind": "control", "control": "panel", "property": "action", "parameters": "boolean_v1"}:
            from .action_parameters_domain import ActionParametersDomain, ActionPanelError
            # Existing saved forms stay editable/passive after their script changes.
            previous = _layout(entry)["cards"] if entry is not None else ()
            retained = any(old.get("id") == card.get("id") and old.get("entity_id") == card["entity_id"]
                           and old.get("action") == action for old in previous)
            if not retained:
                try:
                    if state is None or ActionParametersDomain.from_ha(hass, state, action).parameter_status != "ready":
                        raise ActionPanelError("parameters_unsupported")
                except (ActionPanelError, AttributeError):
                    raise LayoutError("unsupported_action", "Choose a script with one required Boolean field") from None
        if action["kind"] == "service" and state is not None:
            validate_live_action(hass, state, action)


@websocket_api.websocket_command({vol.Required("type"): "atmosfera_echo_hub/tiles/get"})
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_get_tiles(hass, connection, msg) -> None:
    """Compatibility API for the old fixed-slot editor."""
    try:
        entries = [{
            "entry_id": entry.entry_id, "title": entry.title,
            "cards": _legacy_cards(_layout(entry)),
        } for entry in hass.config_entries.async_loaded_entries(DOMAIN)]
        connection.send_result(msg["id"], {
            "version": 1, "entries": entries, "icons": sorted(ICONS),
            "palettes": sorted(PALETTES), "domains": sorted(SUPPORTED_DOMAINS),
        })
    except LayoutError as err:
        _error(connection, msg, err)


@websocket_api.websocket_command({
    vol.Required("type"): "atmosfera_echo_hub/tiles/save",
    vol.Required("entry_id"): str, vol.Required("cards"): list,
})
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_save_tiles(hass, connection, msg) -> None:
    """Legacy saves advance the shared revision without dropping other options."""
    try:
        entry = _entry(hass, msg["entry_id"])
        current = _layout(entry)
        if current["version"] >= 3:
            raise LayoutError("incompatible_editor", "Legacy tile saves cannot edit v3 layouts; use the versioned layout editor")
        cards = normalize_cards(msg["cards"])
        old_ids = {card["slot"]: card["id"] for card in current["cards"]}
        for card in cards:
            card["id"] = old_ids.get(card["slot"], f"legacy-{card['slot']:02d}")
        converted = migrate_legacy(cards, current["revision"])
        # Old clients expose reserved rows. Preserve their current definitions.
        converted["cards"] = [card for card in converted["cards"] if card["slot"] >= 2]
        converted["cards"] += [card for card in current["cards"] if card["slot"] < 2]
        saved = _save(hass, entry, current["revision"], converted)
        connection.send_result(msg["id"], {"cards": _legacy_cards(saved)})
    except LayoutError as err:
        _error(connection, msg, err)


@websocket_api.websocket_command({
    vol.Required("type"): "atmosfera_echo_hub/layout/get",
    vol.Optional("entry_id"): str,
})
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_get_layout(hass, connection, msg) -> None:
    """Read versioned layouts, fixed device capabilities and honest send status."""
    try:
        entries = ([_entry(hass, msg["entry_id"])] if msg.get("entry_id")
                   else hass.config_entries.async_loaded_entries(DOMAIN))
        result = []
        for entry in entries:
            layout = _layout(entry)
            accent = _preview_accent(entry)
            result.append({
                "entry_id": entry.entry_id, "title": entry.title,
                "layout": layout, "profile": device_profile(
                    carousel="home_order" in layout or getattr(entry.runtime_data, "carousel_supported", False)
                ), "status": _status(entry, layout),
                "device_identity": _device_identity(hass, entry),
                "accent_color": f"{accent:06X}",
                "colors": {name: {"background": colors[0], "foreground": colors[1]}
                           for name, colors in derive_tile_palette(accent).items()},
            })
        connection.send_result(msg["id"], {
            "version": 2, "entries": result, "icons": sorted(ICONS),
            "palettes": sorted(PALETTES), "types": list(CARD_TYPES),
        })
    except LayoutError as err:
        _error(connection, msg, err)


@websocket_api.websocket_command({
    vol.Required("type"): "atmosfera_echo_hub/layout/save",
    vol.Required("entry_id"): str, vol.Required("expected_revision"): int,
    vol.Required("layout"): dict,
})
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_save_layout(hass, connection, msg) -> None:
    try:
        entry = _entry(hass, msg["entry_id"])
        saved = _save(hass, entry, msg["expected_revision"], msg["layout"])
        connection.send_result(msg["id"], {"layout": saved, "status": _status(entry, saved)})
    except LayoutError as err:
        _error(connection, msg, err)


@websocket_api.websocket_command({
    vol.Required("type"): "atmosfera_echo_hub/layout/validate",
    vol.Required("entry_id"): str, vol.Required("layout"): dict,
})
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_validate_layout(hass, connection, msg) -> None:
    try:
        entry = _entry(hass, msg["entry_id"])
        document = validate_layout(msg["layout"])
        _validate_actions(hass, document, entry)
        connection.send_result(msg["id"], {"layout": document})
    except LayoutError as err:
        _error(connection, msg, err)


@websocket_api.websocket_command({
    vol.Required("type"): "atmosfera_echo_hub/layout/export",
    vol.Required("entry_id"): str,
})
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_export_layout(hass, connection, msg) -> None:
    try:
        entry = _entry(hass, msg["entry_id"])
        connection.send_result(msg["id"], {"backup": export_layout(_layout(entry))})
    except LayoutError as err:
        _error(connection, msg, err)


@websocket_api.websocket_command({
    vol.Required("type"): "atmosfera_echo_hub/layout/import",
    vol.Required("entry_id"): str, vol.Required("expected_revision"): int,
    vol.Required("backup"): dict, vol.Optional("dry_run", default=True): bool,
})
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_import_layout(hass, connection, msg) -> None:
    try:
        entry = _entry(hass, msg["entry_id"])
        current = _layout(entry)
        next_revision(current["revision"], msg["expected_revision"])
        draft = import_layout(msg["backup"], current["revision"])
        # Reserved bindings belong to the destination and are not portable.
        draft["cards"] = [card for card in draft["cards"] if card["slot"] >= 2]
        draft["cards"] += [card for card in current["cards"] if card["slot"] < 2]
        draft = validate_layout(draft)
        _validate_actions(hass, draft, entry)
        saved = draft if msg["dry_run"] else _save(hass, entry, msg["expected_revision"], draft)
        connection.send_result(msg["id"], {
            "layout": saved, "status": _status(entry),
            "dry_run": msg["dry_run"], "warnings": [],
        })
    except LayoutError as err:
        _error(connection, msg, err)


@websocket_api.websocket_command({
    vol.Required("type"): "atmosfera_echo_hub/catalogue/get",
    vol.Required("entry_id"): str, vol.Optional("query", default=""): vol.All(str, vol.Length(max=128)),
    vol.Optional("domains"): [str],
    vol.Optional("area_id"): vol.All(str, vol.Length(max=256)),
    vol.Optional("limit", default=200): vol.All(int, vol.Range(min=1, max=500)),
})
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_get_catalogue(hass, connection, msg) -> None:
    try:
        entry = _entry(hass, msg["entry_id"])
        connection.send_result(msg["id"], entity_catalogue(
            hass, msg["query"], msg.get("domains"), msg["limit"], msg.get("area_id"),
            camera_entity_ids=entry.options.get(CONF_CAMERAS, entry.data.get(CONF_CAMERAS, ()))
        ))
    except LayoutError as err:
        _error(connection, msg, err)
