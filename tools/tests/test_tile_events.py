"""Stateless event declarations and the existing bridge's dispatch fence."""

import asyncio
from copy import deepcopy
import importlib
from types import SimpleNamespace as NS
import unittest

import test_ha_layout as base
import test_light_integration as permissions

events = importlib.import_module("_atmosfera_test.tile_events")


def event_card(slot=2):
    return base.card(slot=slot, entity="", type="action", title="Good evening", action={"kind": "event"})


def document():
    return base.document([event_card()]) | {"version": 3}


class EventModelTests(unittest.TestCase):
    def test_explicit_v3_roundtrip_normalization_and_no_entity_subscription(self):
        source = document()
        self.assertEqual(base.layout.validate_layout(source), source)
        self.assertEqual(base.layout.import_layout(base.layout.export_layout(source), 7), source | {"revision": 7})
        normalized = base.cards.normalize_cards(source["cards"])
        self.assertTrue(events.is_event_card(normalized[0]))
        self.assertEqual(base.cards.card_entity_ids(normalized), [])
        self.assertTrue(base.cards.ordinary_action_availability(normalized[0]))
        hidden = event_card() | {"visible": False}
        self.assertFalse(events.is_event_card(hidden))
        self.assertTrue(events.is_event_card(hidden, visible_only=False))
        self.assertEqual(base.layout.validate_layout(source | {"cards": [hidden]})["cards"], [hidden])

    def test_no_entity_service_payload_or_protected_type_can_be_smuggled(self):
        invalid = [
            document() | {"version": 2},
            document() | {"cards": [event_card() | {"entity_id": "light.kitchen"}]},
            document() | {"cards": [event_card() | {"type": "entity"}]},
            document() | {"cards": [event_card() | {"type": "sensor"}]},
            document() | {"cards": [event_card(0) | {"visible": False}]},
        ]
        for extra in ({"service": "light.turn_on"}, {"data": {}}, {"control": "light"}, {"event_type": "custom"}):
            invalid.append(document() | {"cards": [event_card() | {"action": {"kind": "event", **extra}}]})
        for source in invalid:
            with self.subTest(source=source), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(source)

    def test_projection_requires_negotiated_contract_and_registered_entity(self):
        hass, _ = base.environment()
        card = event_card()
        self.assertIsNone(base.cards.resolve_action(hass, card))
        for supported, registered in ((False, False), (False, True), (True, False), (True, True)):
            wire = base.cards.presentation_payload(hass, [card], press_enabled_supported=True,
                event_press_supported=supported, event_card_ids={card["id"]} if registered else set())["cards"][2]
            self.assertIs(wire["press_enabled"], supported and registered)
            self.assertNotIn("control_kind", wire)
            self.assertEqual(wire["subtitle"], "Automation" if supported and registered else "Button unavailable")
        wire = base.cards.presentation_payload(hass, [card], "AEE2FF", "pl-PL", press_enabled_supported=True,
            event_press_supported=True, event_card_ids={card["id"]})["cards"][2]
        self.assertEqual(wire["subtitle"], "Automatyzacja")
        self.assertNotIn("press_enabled", base.cards.presentation_payload(hass, [card])["cards"][2])


class EventDispatchTests(unittest.IsolatedAsyncioTestCase):
    def bridge(self):
        bridge = base.BridgeTests().bridge()
        bridge.device_id = "display-device"
        bridge.entry.options["home_layout"] = document()
        bridge.layout = document()
        bridge.tile_cards = base.cards.normalize_cards(bridge.layout["cards"])
        bridge.sent_revision = bridge.saved_revision = 0
        bridge._context_press_version = bridge._press_enabled_version = 1
        bridge._tile_event_entities = {}
        bridge._event_dispatch_busy = False
        bridge.async_schedule_tile_push = lambda **_: None
        self.bus = []
        bridge.hass.bus = NS(async_fire=lambda name, data, **kw: self.bus.append((name, deepcopy(data), kw["context"])))
        self.entity = "event.display_good_evening"
        bridge.hass.entity_registry.entries[self.entity] = NS(platform="atmosfera_echo_hub", device_id=bridge.device_id,
            unique_id=events.event_unique_id(bridge.device_id, "card-2"), disabled_by=None)
        self.remove = bridge.register_tile_event("card-2", self.entity, lambda *_: True)
        self.assertTrue(callable(self.remove))
        return bridge

    async def press(self, bridge, context=None, **changes):
        values = {"slot": 2, "card_id": "card-2", "revision": 0, "context": context}
        values.update(changes)
        await bridge.async_press_tile(**values)

    async def test_one_event_no_service_and_exact_real_system_context(self):
        bridge = self.bridge()
        context = permissions.Context()
        await self.press(bridge, context)
        self.assertEqual(len(self.bus), 1)
        self.assertIs(self.bus[0][2], context)
        self.assertEqual(self.bus[0][1], {"entry_id": "test-entry", "device_id": "display-device",
            "card_id": "card-2", "slot": 2, "revision": 0, "type": "press"})
        self.assertEqual(bridge.hass.services.calls, [])

    async def test_retiring_entity_callback_cannot_publish_a_public_event(self):
        bridge = self.bridge()
        bridge.register_tile_event("card-2", self.entity, lambda *_: False)
        await self.press(bridge, permissions.Context())
        self.assertEqual(self.bus, [])

    async def test_none_forged_context_and_legacy_or_stale_reports_are_denied(self):
        bridge = self.bridge()
        for context in (None, NS(user_id=None), {"user_id": None}):
            await self.press(bridge, context)
        context = permissions.Context()
        for values in ({"card_id": None, "revision": None}, {"card_id": "old"}, {"revision": 1},
                       {"revision": True}, {"slot": 2.0}):
            await self.press(bridge, context, **values)
        self.assertEqual(self.bus, [])

    async def test_real_user_policy_targets_event_entity_and_denies_inactive_user(self):
        bridge = self.bridge()
        checked = []
        user = NS(is_active=True, permissions=NS(check_entity=lambda entity, policy: checked.append((entity, policy)) or False))
        async def get_user(_):
            return user
        bridge.hass.auth = NS(async_get_user=get_user)
        await self.press(bridge, permissions.Context("limited"))
        self.assertEqual(checked, [(self.entity, "control")])
        self.assertEqual(self.bus, [])
        user.is_active = False
        user.permissions.check_entity = lambda *_: True
        await self.press(bridge, permissions.Context("inactive"))
        self.assertEqual(self.bus, [])

    async def test_configuration_listener_gap_and_disabled_registry_are_denied(self):
        for kind in ("revision", "hidden", "disabled", "old-native", "disconnected"):
            bridge = self.bridge()
            if kind == "revision":
                bridge.entry.options["home_layout"]["revision"] = 1
            elif kind == "hidden":
                bridge.entry.options["home_layout"]["cards"][0]["visible"] = False
            elif kind == "disabled":
                bridge.hass.entity_registry.entries[self.entity].disabled_by = "user"
            elif kind == "old-native":
                bridge._press_enabled_version = 0
            else:
                bridge.esphome_entry.runtime_data.available = False
            await self.press(bridge, permissions.Context())
            self.assertEqual(self.bus, [], kind)

    async def test_authorization_is_single_flight_and_rechecks_connection_or_binding(self):
        for kind in ("same", "revision", "client", "binding-aba", "shutdown"):
            bridge = self.bridge()
            entered, resume = asyncio.Event(), asyncio.Event()
            async def get_user(_):
                entered.set()
                await resume.wait()
                return NS(is_active=True, permissions=NS(check_entity=lambda *_: True))
            bridge.hass.auth = NS(async_get_user=get_user)
            task = asyncio.create_task(self.press(bridge, permissions.Context("allowed")))
            await entered.wait()
            await self.press(bridge, permissions.Context())
            self.assertEqual(self.bus, [])
            if kind == "revision":
                bridge.entry.options["home_layout"]["revision"] = 1
            elif kind == "client":
                bridge.esphome_entry.runtime_data.client = object()
            elif kind == "binding-aba":
                old = self.remove
                bridge.register_tile_event("card-2", self.entity, lambda *_: True)
                old()
                self.assertIn("card-2", bridge._tile_event_entities)
            elif kind == "shutdown":
                bridge._closed = True
            resume.set()
            await task
            self.assertEqual(len(self.bus), int(kind == "same"), kind)
            self.assertFalse(bridge._event_dispatch_busy)
