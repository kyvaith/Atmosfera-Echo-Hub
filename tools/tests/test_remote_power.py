"""Explicit Remote transitions and denied stale/unsupported targets."""
import unittest
import test_ha_layout as base


def card(operation="turn_on"):
    return base.card(entity="remote.qa", action={"kind": "service", "service": "remote." + operation, "data": {}})


class RemotePowerTests(unittest.TestCase):
    def test_power_needs_no_activity_feature_and_does_not_predict_feedback(self):
        for attrs in ({}, {"supported_features": 0}, {"supported_features": 7}):
            state = base.State("remote.qa", "off", attrs)
            hass, _ = base.environment(states=[state], services=["remote.turn_on", "remote.turn_off"])
            self.assertEqual({a["service"] for a in base.cards.entity_actions(hass, state)}, {"remote.turn_on", "remote.turn_off"})
            result = base.cards.resolve_action(hass, card())
            self.assertEqual((result.domain, result.service, result.data), ("remote", "turn_on", {"entity_id": "remote.qa"}))
            self.assertEqual(state.state, "off")
            self.assertEqual(hass.services.calls, [])

    def test_observed_transition_matrix_and_negotiated_press(self):
        state = base.State("remote.qa", "off", {})
        hass, _ = base.environment(states=[state], services=["remote.turn_on", "remote.turn_off"])
        for value in ("off", "on", "unknown", "unavailable", "idle", "error", "off"):
            state.state = value
            for operation, required in (("turn_on", "off"), ("turn_off", "on")):
                allowed = value == required
                self.assertEqual(base.cards.resolve_action(hass, card(operation)) is not None, allowed)
                rendered = base.cards.presentation_payload(hass, [card(operation)], press_enabled_supported=True)["cards"][2]
                self.assertIs(rendered["press_enabled"], allowed)
                self.assertNotIn("control_kind", rendered)
            if value not in {"on", "off"}:
                self.assertEqual(base.cards.entity_actions(hass, state), [])
                self.assertEqual(base.cards._remote_power_metadata(hass, state), {})
        self.assertNotIn("press_enabled", base.cards.presentation_payload(hass, [card()], press_enabled_supported=False)["cards"][2])

    def test_no_service_or_passive_default_hidden_and_foreign_action_is_inert(self):
        state = base.State("remote.qa", "off", {})
        hass, _ = base.environment(states=[state], services=[])
        self.assertIsNone(base.cards.resolve_action(hass, card()))
        self.assertEqual(base.cards._remote_power_metadata(hass, state), {})
        hass, _ = base.environment(states=[state], services=["remote.turn_on", "remote.turn_off", "homeassistant.turn_on"])
        for change in ({"type": "sensor"}, {"visible": False}, {"action": {"kind": "none"}}, {"action": {"kind": "default"}},
                       {"action": {"kind": "service", "service": "homeassistant.turn_on", "data": {}}}):
            self.assertIsNone(base.cards.resolve_action(hass, card() | change))
        for operation in ("toggle", "send_command", "learn_command", "delete_command"):
            self.assertIsNone(base.cards.resolve_action(hass, card(operation)))
        self.assertTrue(base.layout.device_profile()["schema_remote_power"])

    def test_activity_command_and_target_fields_are_rejected(self):
        for data in ({"activity": "TV"}, {"command": "play"}, {"entity_id": "remote.other"}, {"device_id": "other"}):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action({"kind": "service", "service": "remote.turn_on", "data": data}, "remote.qa")
