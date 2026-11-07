"""Explicit robot commands, observed feedback and existing power stay separate."""

import importlib
import unittest
from enum import IntFlag
from types import SimpleNamespace
from unittest.mock import patch

import test_ha_layout as base

model = importlib.import_module("_atmosfera_test.vacuum_actions")
SERVICES = ["vacuum." + operation for operation in model.FEATURES]
ALL = sum(model.FEATURES.values())


def card(operation="start"):
    return base.card(entity="vacuum.qa", action={"kind": "service", "service": "vacuum." + operation, "data": {}})


class VacuumActionsTests(unittest.TestCase):
    def test_product_activity_matrix_distinguishes_motion_stop_and_non_motion_locate(self):
        expected = {
            "docked": {"start", "locate", "clean_spot"},
            "idle": {"start", "return_to_base", "locate", "clean_spot"},
            "paused": {"start", "stop", "return_to_base", "locate", "clean_spot"},
            "cleaning": {"pause", "stop", "return_to_base", "locate"},
            "returning": {"pause", "stop", "locate"},
            "error": {"locate"},
        }
        for state, allowed in expected.items():
            self.assertEqual({op for op in model.FEATURES if model.command_allowed(state, {"supported_features": ALL}, op)}, allowed)
        for state in ("unknown", "unavailable", "on", "off", None, 0):
            self.assertFalse(any(model.command_allowed(state, {"supported_features": ALL}, op) for op in model.FEATURES))

    def test_real_core_intflag_supported_but_legacy_turn_on_and_malformed_flags_are_not_start(self):
        class Feature(IntFlag):
            START = 8192
            PAUSE = 4
        self.assertEqual(model.supported_operations({"supported_features": Feature.START | Feature.PAUSE}), ("start", "pause"))
        for flags in (None, True, "8192", 8192.0, -1, 2**53, 1, 2, 3):
            self.assertEqual(model.supported_operations({"supported_features": flags}), ())
        self.assertEqual(model.supported_operations(None), ())

    def test_one_exact_command_target_rechecked_without_predicting_robot_state(self):
        state = base.State("vacuum.qa", "paused", {"supported_features": ALL})
        hass, _ = base.environment(states=[state], services=SERVICES)
        for operation in ("start", "stop", "return_to_base", "locate", "clean_spot"):
            result = base.cards.resolve_action(hass, card(operation))
            self.assertEqual((result.domain, result.service, result.data), ("vacuum", operation, {"entity_id": "vacuum.qa"}))
            self.assertEqual(state.state, "paused")
        self.assertIsNone(base.cards.resolve_action(hass, card("pause")))
        self.assertEqual(hass.services.calls, [])

    def test_absent_service_and_lost_capability_deny_execution_and_catalog(self):
        state = base.State("vacuum.qa", "docked", {"supported_features": ALL})
        hass, _ = base.environment(states=[state], services=[])
        self.assertIsNone(base.cards.resolve_action(hass, card()))
        self.assertEqual(base.cards._vacuum_actions_metadata(hass, state), {})
        hass, _ = base.environment(states=[state], services=SERVICES)
        state.attributes["supported_features"] = ALL - 8192
        self.assertIsNone(base.cards.resolve_action(hass, card()))
        self.assertNotIn("start", base.cards._vacuum_actions_metadata(hass, state)["vacuum_actions"]["supported"])
        for flags in (-1, True, 2**53 + ALL):
            state.attributes["supported_features"] = flags
            self.assertEqual(base.cards.entity_actions(hass, state), [])

    def test_catalog_supported_operations_are_distinct_from_current_eligibility(self):
        state = base.State("vacuum.qa", "docked", {"supported_features": ALL})
        hass, _ = base.environment(states=[state], services=SERVICES)
        meta = base.cards._vacuum_actions_metadata(hass, state)["vacuum_actions"]
        self.assertEqual(set(meta["supported"]), set(model.FEATURES))
        self.assertEqual(set(meta["eligible"]), {"start", "locate", "clean_spot"})
        self.assertEqual({item["service"] for item in base.cards.entity_actions(hass, state)}, set(SERVICES))
        state.state = "unknown"
        self.assertEqual(base.cards._vacuum_actions_metadata(hass, state), {})

    def test_negotiated_press_tracks_activity_and_legacy_peer_omits_field(self):
        state = base.State("vacuum.qa", "docked", {"supported_features": ALL})
        hass, _ = base.environment(states=[state], services=SERVICES)
        for activity in (*model.ACTIVITIES, "unknown", "unavailable"):
            state.state = activity
            projection = base.cards.presentation_payload(hass, [card("pause")], press_enabled_supported=True)["cards"][2]
            self.assertEqual(projection["press_enabled"], activity in {"cleaning", "returning"})
            self.assertNotIn("control_kind", projection)
        self.assertNotIn("press_enabled", base.cards.presentation_payload(hass, [card()], press_enabled_supported=False)["cards"][2])

    def test_passive_hidden_and_default_cards_never_infer_a_motion(self):
        state = base.State("vacuum.qa", "docked", {"supported_features": ALL})
        hass, _ = base.environment(states=[state], services=SERVICES)
        for change in ({"action": {"kind": "default"}}, {"action": {"kind": "none"}}, {"type": "sensor"}, {"visible": False}):
            self.assertIsNone(base.cards.resolve_action(hass, card() | change))
        for operation in ("turn_on", "turn_off", "start_pause", "send_command", "clean_area"):
            self.assertIsNone(base.cards.resolve_action(hass, card(operation)))

    def test_existing_fan_power_control_keeps_its_own_capability_and_service(self):
        state = base.State("vacuum.qa", "cleaning", {"supported_features": 32, "fan_speed_list": ["quiet", "turbo"], "fan_speed": "quiet"})
        hass, _ = base.environment(states=[state], services=["vacuum.set_fan_speed"])
        item = base.card(entity="vacuum.qa", action={"kind": "service", "service": "vacuum.set_fan_speed", "data": {"fan_speed": "turbo"}})
        result = base.cards.resolve_action(hass, item)
        self.assertEqual(result.data, {"entity_id": "vacuum.qa", "fan_speed": "turbo"})
        item["action"] = {"kind": "control", "control": "choice", "property": "fan_speed"}
        self.assertFalse(base.cards.ordinary_action_availability(item))
        self.assertIsNone(base.cards.resolve_action(hass, item))

    def test_actual_ha_labels_win_with_polish_error_fallback_and_no_new_native_contract(self):
        state = base.State("vacuum.qa", "error", {"supported_features": ALL})
        hass, _ = base.environment(states=[state], services=SERVICES)
        hass.config.language = "pl"
        with patch.object(base.cards, "async_get_cached_translations", return_value={"component.vacuum.entity_component._.state.error": "Error"}):
            with patch.object(base.cards, "async_translate_state", return_value="Error") as fast:
                self.assertEqual(base.cards._state_subtitle(hass, state, "pl"), "Błąd")
                fast.assert_not_called()
        state.state = "cleaning"
        with patch.object(base.cards, "async_get_cached_translations", return_value={"component.vacuum.entity_component._.state.cleaning": "HA sprzątanie"}):
            self.assertEqual(base.cards._state_subtitle(hass, state, "en"), "HA sprzątanie")
        self.assertTrue(base.layout.device_profile()["schema_vacuum_actions"])

    def test_stock_returning_label_fits_real_136px_caption_without_overriding_specific_translation(self):
        metrics = importlib.import_module("_atmosfera_test.caption_width")
        state = base.State("vacuum.qa", "returning", {"supported_features": ALL})
        hass, _ = base.environment(states=[state], services=SERVICES)
        hass.config.language = "pl"
        labels = {"component.vacuum.entity_component._.state.returning": "wraca do stacji dokującej"}
        with patch.object(base.cards, "async_get_cached_translations", return_value=labels):
            caption = base.cards._state_subtitle(hass, state, "pl")
            self.assertEqual(caption, "Powrót do bazy")
            self.assertLessEqual(metrics.caption_width(caption), 134)
        hass.entity_registry.entries[state.entity_id] = SimpleNamespace(platform="qa", translation_key="specific")
        labels["component.qa.entity.vacuum.specific.state.returning"] = "Moja stacja"
        with patch.object(base.cards, "async_get_cached_translations", return_value=labels):
            self.assertEqual(base.cards._state_subtitle(hass, state, "pl"), "Moja stacja")
