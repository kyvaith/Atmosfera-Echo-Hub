"""Mapped-room commands use Core areas and never guessed vendor segments."""

import importlib
import unittest
from enum import IntFlag
from types import SimpleNamespace
from unittest.mock import patch

import test_ha_layout as base

model = importlib.import_module("_atmosfera_test.vacuum_areas")


def fixture():
    state = base.State("vacuum.qa", "docked", {"supported_features": 16384})
    hass, _ = base.environment(states=[state], services=["vacuum.clean_area"])
    hass.entity_registry.entries[state.entity_id] = SimpleNamespace(platform="mqtt", translation_key=None, options={"vacuum": {"area_mapping": {"living": ["17", "18"], "office": ["01"], "removed": ["9"]}}})
    hass.area_registry.entries.update(living=SimpleNamespace(name="Salon"), office=SimpleNamespace(name="Biuro"))
    card = base.card(entity=state.entity_id, action={"kind": "service", "service": "vacuum.clean_area", "data": {"cleaning_area_id": "living"}})
    return hass, state, card


class VacuumAreaTests(unittest.TestCase):
    def test_catalog_uses_actual_registered_areas_and_leaves_segments_private_to_core(self):
        hass, state, _ = fixture()
        metadata = base.cards._vacuum_area_metadata(hass, state)["vacuum_area"]
        self.assertEqual(metadata["areas"], [{"id": "living", "name": "Salon"}, {"id": "office", "name": "Biuro"}])
        descriptor = base.cards.entity_actions(hass, state)[0]
        self.assertEqual(descriptor["service"], "vacuum.clean_area")
        self.assertEqual(descriptor["fields"]["cleaning_area_id"], {"type": "select", "required": True, "options": ["living", "office"], "option_labels": ["Salon", "Biuro"]})
        self.assertNotIn("17", str(metadata))

    def test_exact_area_target_not_vendor_id_is_resolved_and_activity_remains_observed(self):
        hass, state, card = fixture()
        result = base.cards.resolve_action(hass, card)
        self.assertEqual(result.data, {"entity_id": "vacuum.qa", "cleaning_area_id": "living"})
        self.assertEqual(state.state, "docked")
        self.assertEqual(hass.services.calls, [])

    def test_capabilities_are_real_intflags_not_legacy_power_or_bool(self):
        class Feature(IntFlag):
            CLEAN_AREA = 16384
        self.assertTrue(model.has_area_capability({"supported_features": Feature.CLEAN_AREA}))
        for value in (True, None, -1, 1, 2, 8192, "16384", 16384.0, 2**53):
            self.assertFalse(model.has_area_capability({"supported_features": value}))

    def test_empty_missing_malformed_or_unbounded_mapping_never_generates_a_room(self):
        for mapping in ({}, None, [], {"living": []}, {"living": [17]}, {"living": ["1", "1"]}, {"living": ["x\n"]}, {"living": ["x" * 129]}, {str(i): [str(i)] for i in range(33)}):
            self.assertEqual(model.mapped_area_ids({"vacuum": {"area_mapping": mapping}}), ())
        self.assertEqual(model.mapped_area_ids(None), ())

    def test_mapping_or_area_removed_without_state_change_revokes_old_action(self):
        hass, state, card = fixture()
        original_state = state.state
        hass.entity_registry.entries[state.entity_id].options["vacuum"]["area_mapping"].pop("living")
        self.assertIsNone(base.cards.resolve_action(hass, card))
        hass, state, card = fixture()
        hass.area_registry.entries.pop("living")
        self.assertIsNone(base.cards.resolve_action(hass, card))
        self.assertEqual(state.state, original_state)

    def test_missing_service_or_unsupported_provider_never_exposes_a_room(self):
        hass, state, card = fixture()
        hass.services = base.Services([])
        self.assertEqual(base.cards._vacuum_area_metadata(hass, state), {})
        self.assertIsNone(base.cards.resolve_action(hass, card))
        hass, state, card = fixture()
        state.attributes["supported_features"] = 8192
        self.assertEqual(base.cards.entity_actions(hass, state), [])
        self.assertIsNone(base.cards.resolve_action(hass, card))

    def test_busy_error_unknown_and_unavailable_are_not_room_cleaning_admission(self):
        hass, state, card = fixture()
        for activity in ("cleaning", "returning", "error", "unknown", "unavailable"):
            state.state = activity
            self.assertIsNone(base.cards.resolve_action(hass, card))
            projected = base.cards.presentation_payload(hass, [card], press_enabled_supported=True)["cards"][2]
            self.assertFalse(projected["press_enabled"])
        for activity in ("docked", "idle", "paused"):
            state.state = activity
            self.assertIsNotNone(base.cards.resolve_action(hass, card))

    def test_no_default_no_guess_no_multiple_or_raw_segments_in_static_layout(self):
        hass, _, card = fixture()
        for value in ("17", "Bedroom", "removed"):
            card["action"]["data"]["cleaning_area_id"] = value
            self.assertIsNone(base.cards.resolve_action(hass, card))
        for data in ({}, {"cleaning_area_id": ["living"]}, {"segment_ids": ["17"]}):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action({"kind": "service", "service": "vacuum.clean_area", "data": data}, "vacuum.qa")

    def test_registry_events_only_refresh_owned_visible_area_cards_without_camera_work(self):
        bridge = base.BridgeTests().bridge()
        hass, _, card = fixture()
        bridge.tile_cards = [card]
        scheduled = []
        bridge.async_schedule_tile_push = lambda **kw: scheduled.append(kw)
        for data in ({"entity_id": "vacuum.other"}, {"area_id": "other"}):
            bridge._tile_area_registry_changed(SimpleNamespace(data=data))
        self.assertEqual(scheduled, [])
        for data in ({"entity_id": "vacuum.qa"}, {"area_id": "living"}):
            bridge._tile_area_registry_changed(SimpleNamespace(data=data))
        self.assertEqual(scheduled, [{"delay": 0}, {"delay": 0}])
        card["visible"] = False
        bridge._tile_area_registry_changed(SimpleNamespace(data={"entity_id": "vacuum.qa"}))
        self.assertEqual(len(scheduled), 2)

    def test_mapping_listeners_are_owned_replaced_and_removed_on_unload(self):
        bridge = base.BridgeTests().bridge()
        _, _, card = fixture()
        bridge.tile_cards = [card]
        bridge.tile_entity_ids = ("vacuum.qa",)
        events, removed = [], []
        bridge.hass.bus = SimpleNamespace(async_listen=lambda event, callback: (events.append(event) or (lambda: removed.append(event))))
        with patch.object(base.controller, "async_track_state_change_event", return_value=lambda: None):
            bridge._replace_tile_subscription()
            self.assertEqual(events, ["entity_registry_updated", "area_registry_updated"])
            self.assertEqual(len(bridge._tile_registry_unsubscribers), 2)
            bridge._closed = True
            bridge._replace_tile_subscription()
        self.assertEqual(removed, events)
        self.assertEqual(bridge._tile_registry_unsubscribers, [])
