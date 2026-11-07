"""Entity lifecycle adapter checks; the live HA Event base is a separate gate."""

import asyncio
from copy import deepcopy
import importlib
from types import SimpleNamespace as NS
import unittest

import test_ha_layout as base
import test_tile_events as policy


class FakeEventEntity:
    registry_entry = None

    def async_on_remove(self, callback):
        if not hasattr(self, "_remove_callbacks"):
            self._remove_callbacks = []
        self._remove_callbacks.append(callback)

    async def async_added_to_hass(self):
        return None

    def async_write_ha_state(self):
        self.writes = getattr(self, "writes", 0) + 1

    def _trigger_event(self, event_type, attributes):
        self.triggers = [*getattr(self, "triggers", []), (event_type, deepcopy(attributes), self._context)]

    async def async_remove(self):
        self.remove_calls = getattr(self, "remove_calls", 0) + 1
        for callback in reversed(self._remove_callbacks):
            callback()


base.module("homeassistant.components.event", EventDeviceClass=NS(BUTTON="button"), EventEntity=FakeEventEntity)
platform = importlib.import_module("_atmosfera_test.event")


class EventEntityTests(unittest.IsolatedAsyncioTestCase):
    def manager(self):
        bridge = policy.EventDispatchTests().bridge()
        bridge._tile_event_entities.clear()
        bridge.device_entry = NS(id=bridge.device_id)
        bridge.entry.runtime_data = bridge
        bridge.hass.loop = asyncio.get_running_loop()
        added = []
        manager = platform.TileEventEntities(bridge.hass, bridge.entry, lambda rows: added.extend(rows))
        return manager, bridge, added

    async def finish(self, entity):
        entity.entity_id = "event.test_" + entity.card_id.replace("-", "_")
        entity.hass = entity._manager.hass
        await entity.async_added_to_hass()
        await asyncio.sleep(0)
        await entity.added_done

    async def test_added_unknown_no_restore_or_synthetic_press_then_exact_callback(self):
        manager, bridge, added = self.manager()
        await manager.async_sync()
        self.assertEqual(len(added), 1)
        entity = added[0]
        self.assertEqual(bridge._tile_event_entities, {})
        await self.finish(entity)
        self.assertIsNone(await entity.async_get_last_event_data())
        self.assertEqual(getattr(entity, "triggers", []), [])
        self.assertEqual(entity._attr_event_types, ["press"])
        self.assertEqual(entity._attr_unique_id, policy.events.event_unique_id(bridge.device_id, "card-2"))
        context = object()
        payload = {"card_id": "card-2", "slot": 2, "revision": 0, "type": "press"}
        self.assertIs(entity._accept_press(payload, context), True)
        self.assertIs(entity.triggers[0][2], context)
        self.assertEqual(entity.triggers[0][:2], ("press", {"card_id": "card-2", "slot": 2, "revision": 0}))
        self.assertIs(entity._accept_press(payload | {"card_id": "wrong"}, context), False)
        manager.close()
        self.assertIs(entity._accept_press(payload, context), False)
        await entity.async_remove()
        self.assertEqual(bridge._tile_event_entities, {})

    async def test_move_reuses_entity_and_hidden_or_removed_card_retires_registration(self):
        manager, bridge, added = self.manager()
        await manager.async_sync();entity = added[0];await self.finish(entity)
        original = entity._attr_unique_id
        doc = bridge.entry.options["home_layout"]
        doc["revision"] = 1;doc["cards"][0]["slot"] = 3
        await manager.async_sync()
        self.assertEqual(len(added), 1)
        self.assertIs(manager.entities["card-2"], entity)
        self.assertEqual(entity._attr_unique_id, original)
        self.assertEqual(getattr(entity, "triggers", []), [])
        doc["revision"] = 2;doc["cards"][0]["visible"] = False
        await manager.async_sync()
        self.assertEqual(entity.remove_calls, 1)
        self.assertEqual(manager.entities, {})
        self.assertEqual(bridge._tile_event_entities, {})
        self.assertFalse(entity._accept_press({"card_id": "card-2", "type": "press"}, object()))

    async def test_explicit_direct_to_panel_migration_preserves_entity_and_registration_without_event(self):
        manager, bridge, added = self.manager()
        await manager.async_sync(); entity = added[0]; await self.finish(entity)
        binding = bridge._tile_event_entities['card-2']
        doc = bridge.entry.options['home_layout']
        doc['revision'] += 1
        doc['cards'][0]['action'] = dict(policy.events.PANEL_ACTION)
        await manager.async_sync()
        self.assertEqual(len(added), 1)
        self.assertIs(manager.entities['card-2'], entity)
        self.assertIs(bridge._tile_event_entities['card-2'], binding)
        self.assertEqual(getattr(entity, 'triggers', []), [])
        doc['revision'] += 1
        doc['cards'][0]['action'] = {'kind': 'event'}
        await manager.async_sync()
        self.assertIs(bridge._tile_event_entities['card-2'], binding)
        await entity.async_remove()

    async def test_remove_before_add_waits_for_core_abort_without_registration(self):
        manager, bridge, added = self.manager()
        await manager.async_sync();entity = added[0]
        bridge.entry.options["home_layout"]["cards"] = []
        task = asyncio.create_task(manager.async_sync())
        await asyncio.sleep(0)
        self.assertFalse(task.done())
        entity._removed()  # Public Core add-abort runs registered remove hooks.
        await task
        self.assertEqual(manager.entities, {})
        self.assertEqual(bridge._tile_event_entities, {})
        self.assertEqual(getattr(entity, "remove_calls", 0), 0)

    async def test_bounded_active_set_and_rename_never_emits_event(self):
        manager, bridge, added = self.manager()
        doc = bridge.entry.options["home_layout"]
        doc["cards"] = [policy.event_card(slot) for slot in range(2, 16)]
        await manager.async_sync()
        self.assertEqual(len(added), 14)
        for entity in added:
            await self.finish(entity)
        self.assertEqual(len(bridge._tile_event_entities), 14)
        entity = added[0]
        doc["cards"][0]["title"] = "New title"
        await manager.async_sync()
        self.assertEqual(entity._attr_name, "New title")
        self.assertEqual(getattr(entity, "triggers", []), [])
        for entity in list(added):
            await entity.async_remove()
        self.assertEqual(manager.entities, {})
        self.assertEqual(bridge._tile_event_entities, {})
