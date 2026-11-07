"""One discoverable HA Event entity per visible configured automation card."""

from __future__ import annotations

import asyncio
from copy import deepcopy

from homeassistant.components.event import EventDeviceClass, EventEntity
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er

from .cards import entry_layout
from .tile_events import EVENT_TYPE_PRESS, MAX_EVENT_CARDS, event_unique_id, is_event_definition


async def async_setup_entry(hass, entry, async_add_entities):
    """Use the existing config-entry lifecycle, with no poller or new timer."""
    manager = TileEventEntities(hass, entry, async_add_entities)
    entry.async_on_unload(entry.add_update_listener(manager.async_options_updated))
    entry.async_on_unload(manager.close)
    await manager.async_sync()


class TileEventEntities:
    """Serialize dynamic add/remove and retain at most the active card set."""

    def __init__(self, hass, entry, add_entities):
        self.hass, self.entry, self.add_entities = hass, entry, add_entities
        self.entities = {}
        self.closed = False
        self._lock = asyncio.Lock()

    @callback
    def close(self):
        self.closed = True
        for entity in self.entities.values():
            entity.deactivate()

    @callback
    def removed(self, entity):
        if self.entities.get(entity.card_id) is entity:
            del self.entities[entity.card_id]

    async def async_options_updated(self, _hass, _entry):
        await self.async_sync()

    async def async_sync(self):
        async with self._lock:
            if self.closed:
                return
            document = entry_layout(self.entry.options, self.entry.data)
            cards = {card["id"]: card for card in document["cards"] if is_event_definition(card)}
            assert len(cards) <= MAX_EVENT_CARDS
            for card_id in set(self.entities) - set(cards):
                entity = self.entities.pop(card_id)
                entity.deactivate()
                # The public add callback schedules addition. Wait for finish or
                # abort before removing, including registry-disabled entities.
                await entity.added_done
                if entity.added:
                    await entity.async_remove()
            additions = []
            for card_id, card in cards.items():
                if card_id in self.entities:
                    self.entities[card_id].update_card(card)
                else:
                    entity = TilePressEvent(self, card)
                    self.entities[card_id] = entity
                    additions.append(entity)
            if additions:
                self.add_entities(additions)


class TilePressEvent(EventEntity):
    """Publish only accepted callbacks; a public bus event cannot forge a press."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_device_class = EventDeviceClass.BUTTON
    _attr_translation_key = "tile_press"

    def __init__(self, manager, card):
        self._manager = manager
        self._bridge = manager.entry.runtime_data
        self._card = deepcopy(card)
        self.card_id = card["id"]
        self._attr_unique_id = event_unique_id(self._bridge.device_id, self.card_id)
        self._attr_name = card["title"] or "Automation button"
        self._attr_event_types = [EVENT_TYPE_PRESS]
        self.device_entry = self._bridge.device_entry
        self.added = False
        self._active = True
        self.added_done = manager.hass.loop.create_future()
        self.async_on_remove(self._removed)

    @callback
    def deactivate(self):
        self._active = False

    @callback
    def _removed(self):
        self._active = self.added = False
        self._manager.removed(self)
        if not self.added_done.done():
            self.added_done.set_result(None)

    @callback
    def update_card(self, card):
        assert card["id"] == self.card_id
        self._card = deepcopy(card)
        name = card["title"] or "Automation button"
        if self._attr_name == name:
            return
        self._attr_name = name
        if self.added:
            registered = self.registry_entry
            if registered is not None and registered.original_name != name:
                er.async_get(self.hass).async_update_entity(self.entity_id, original_name=name)
            self.async_write_ha_state()

    async def async_get_last_event_data(self):
        """Do not replay a historical press after a rebind/reload."""
        return None

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.added = True
        # EntityPlatform marks ADDED and writes its initial state after this
        # hook returns. Only then may a native press publish another state.
        self.hass.loop.call_soon(self._finish_added)

    @callback
    def _finish_added(self):
        if self._active and not self._manager.closed and self._manager.entities.get(self.card_id) is self:
            remove = self._bridge.register_tile_event(self.card_id, self.entity_id, self._accept_press)
            if remove is not None:
                self.async_on_remove(remove)
        if not self.added_done.done():
            self.added_done.set_result(None)

    @callback
    def _accept_press(self, payload, context):
        if (not self._active or not self.added or self._manager.closed
                or self._manager.entities.get(self.card_id) is not self
                or payload.get("card_id") != self.card_id or payload.get("type") != EVENT_TYPE_PRESS):
            return False
        self._context = context
        self._trigger_event(EVENT_TYPE_PRESS, {key: payload[key] for key in ("card_id", "slot", "revision")})
        self.async_write_ha_state()
        return True
