"""An explicit mower command remains separate from live movement feedback."""

import importlib
import unittest
from enum import IntFlag
from types import SimpleNamespace
from unittest.mock import patch

import test_ha_layout as base

model = importlib.import_module("_atmosfera_test.mower_actions")
SERVICES = ["lawn_mower." + operation for operation in ("start_mowing", "pause", "dock")]


def card(operation="start_mowing"):
    return base.card(entity="lawn_mower.qa", action={"kind": "service", "service": "lawn_mower." + operation, "data": {}})


class MowerActionsTests(unittest.TestCase):
    def test_actual_core_intflag_capabilities_are_valid_without_accepting_bool(self):
        class Feature(IntFlag):
            START_MOWING = 1
            PAUSE = 2
            DOCK = 4
        flags = Feature.START_MOWING | Feature.PAUSE | Feature.DOCK
        self.assertEqual(model.supported_operations({"supported_features": flags}), ("start_mowing", "pause", "dock"))
        state = base.State("lawn_mower.qa", "docked", {"supported_features": flags})
        hass, _ = base.environment(states=[state], services=SERVICES)
        self.assertIsNotNone(base.cards.resolve_action(hass, card()))
        self.assertEqual(model.supported_operations({"supported_features": True}), ())

    def test_explicit_activity_matrix_and_capabilities_never_infer_replacement_command(self):
        allowed = {"docked": {"start_mowing"}, "paused": {"start_mowing", "dock"}, "mowing": {"pause", "dock"}, "returning": {"pause"}, "error": set()}
        for state, expected in allowed.items():
            self.assertEqual({op for op in model.FEATURES if model.command_allowed(state, {"supported_features": 7}, op)}, expected)
        for state in ("unknown", "unavailable", "idle", "on", "off", None, 0):
            self.assertFalse(any(model.command_allowed(state, {"supported_features": 7}, op) for op in model.FEATURES))

    def test_unknown_missing_malformed_feature_flags_and_absent_service_are_not_authority(self):
        for features in (None, True, "7", 7.0, -1, 2**53):
            self.assertEqual(model.supported_operations({"supported_features": features}), ())
        self.assertEqual(model.supported_operations(None), ())
        state = base.State("lawn_mower.qa", "docked", {"supported_features": 1})
        hass, _ = base.environment(states=[state], services=[])
        self.assertIsNone(base.cards.resolve_action(hass, card()))
        self.assertEqual(base.cards._mower_actions_metadata(hass, state), {})

    def test_resolver_returns_one_exact_no_data_command_and_cannot_claim_observed_motion(self):
        state = base.State("lawn_mower.qa", "paused", {"supported_features": 7})
        hass, _ = base.environment(states=[state], services=SERVICES)
        for op in ("start_mowing", "dock"):
            action = base.cards.resolve_action(hass, card(op))
            self.assertEqual((action.domain, action.service, action.data), ("lawn_mower", op, {"entity_id": state.entity_id}))
            self.assertEqual(state.state, "paused")
        self.assertIsNone(base.cards.resolve_action(hass, card("pause")))
        self.assertEqual(hass.services.calls, [])

    def test_metadata_describes_configuration_capabilities_separately_from_current_eligibility(self):
        state = base.State("lawn_mower.qa", "docked", {"supported_features": 7})
        hass, _ = base.environment(states=[state], services=SERVICES)
        meta = base.cards._mower_actions_metadata(hass, state)["mower_actions"]
        self.assertEqual(meta, {"state": "docked", "features": 7, "supported": ["start_mowing", "pause", "dock"], "eligible": ["start_mowing"]})
        self.assertEqual({item["service"] for item in base.cards.entity_actions(hass, state)}, set(SERVICES))
        state.state = "error"
        self.assertEqual(base.cards._mower_actions_metadata(hass, state)["mower_actions"]["eligible"], [])
        state.state = "unknown"
        self.assertEqual(base.cards._mower_actions_metadata(hass, state), {})

    def test_negotiated_native_press_availability_changes_without_optimistic_state_or_new_control(self):
        state = base.State("lawn_mower.qa", "docked", {"supported_features": 7})
        hass, _ = base.environment(states=[state], services=SERVICES)
        item = card("pause")
        for activity in ("docked", "paused", "mowing", "returning", "error", "unknown", "unavailable"):
            state.state = activity
            projected = base.cards.presentation_payload(hass, [item], press_enabled_supported=True)["cards"][2]
            self.assertEqual(projected["press_enabled"], activity in {"mowing", "returning"})
            self.assertNotIn("control_kind", projected)
        projected = base.cards.presentation_payload(hass, [item], press_enabled_supported=False)["cards"][2]
        self.assertNotIn("press_enabled", projected)

    def test_no_default_start_no_sensor_action_and_no_unknown_or_stale_capability(self):
        state = base.State("lawn_mower.qa", "docked", {"supported_features": 7})
        hass, _ = base.environment(states=[state], services=SERVICES)
        for change in ({"action": {"kind": "default"}}, {"action": {"kind": "none"}}, {"type": "sensor"}, {"visible": False}):
            self.assertIsNone(base.cards.resolve_action(hass, card() | change))
        for raw in (0, 2, 4):
            state.attributes["supported_features"] = raw
            self.assertIsNone(base.cards.resolve_action(hass, card()))
        state.attributes["supported_features"] = 7
        for activity in ("mowing", "returning", "error", "unknown", "unavailable", "idle"):
            state.state = activity
            self.assertIsNone(base.cards.resolve_action(hass, card()))

    def test_ha_labels_win_and_missing_polish_and_english_activity_names_are_bounded(self):
        state = base.State("lawn_mower.qa", "mowing", {"supported_features": 7})
        hass, _ = base.environment(states=[state], services=SERVICES)
        self.assertEqual(base.cards._state_subtitle(hass, state, "pl"), "Koszenie")
        self.assertEqual(base.cards._state_subtitle(hass, state, "en"), "Mowing")
        with patch.object(base.cards, "async_get_cached_translations", return_value={"component.lawn_mower.entity_component._.state.mowing": "Etykieta HA"}):
            self.assertEqual(base.cards._state_subtitle(hass, state, "pl"), "Etykieta HA")
        self.assertTrue(base.layout.device_profile()["schema_mower_actions"])

    def test_partial_stock_polish_resources_use_fallback_but_specific_translation_wins(self):
        state = base.State("lawn_mower.qa", "returning", {"supported_features": 7})
        hass, _ = base.environment(states=[state], services=SERVICES)
        labels = {"component.lawn_mower.entity_component._.state.returning": "Returning"}
        with patch.object(base.cards, "async_get_cached_translations", return_value=labels):
            self.assertEqual(base.cards._state_subtitle(hass, state, "pl"), "Powrót")
            self.assertEqual(base.cards._state_subtitle(hass, state, "en"), "Returning")
        hass.entity_registry.entries[state.entity_id] = SimpleNamespace(platform="qa", translation_key="specific")
        labels["component.qa.entity.lawn_mower.specific.state.returning"] = "Returning"
        with patch.object(base.cards, "async_get_cached_translations", return_value=labels):
            self.assertEqual(base.cards._state_subtitle(hass, state, "pl"), "Returning")

    def test_matching_server_polish_locale_cannot_bypass_stock_fallback_through_fast_translation(self):
        state = base.State("lawn_mower.qa", "error", {"supported_features": 7})
        hass, _ = base.environment(states=[state], services=SERVICES)
        hass.config.language = "pl"
        labels = {"component.lawn_mower.entity_component._.state.error": "Error"}
        with patch.object(base.cards, "async_translate_state", return_value="Error") as fast:
            with patch.object(base.cards, "async_get_cached_translations", return_value=labels):
                self.assertEqual(base.cards._state_subtitle(hass, state, "pl"), "Błąd")
                fast.assert_not_called()
