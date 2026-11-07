"""Typed timer presets remain optional and never turn a resume into a reset."""
from copy import deepcopy
import math
import unittest

import test_ha_layout as base
import test_input_button_availability as availability
from test_input_button_availability import timer_environment


class TimerPresetTests(unittest.TestCase):
    def action(self, duration):
        return {"kind": "service", "service": "timer.start", "data": {"duration": duration}}

    def test_schema_and_live_resolver_accept_only_bounded_whole_seconds(self):
        for value in (1, 59, 60, 90, 3600, 86400, 90.0):
            with self.subTest(value=value):
                action = self.action(value)
                original = deepcopy(action)
                self.assertEqual(base.layout.validate_action(action, "timer.example"), action)
                hass, card = timer_environment("paused", action=action)
                result = base.cards.resolve_action(hass, card)
                self.assertEqual(result.data, {"entity_id": "timer.example", "duration": value})
                self.assertEqual(action, original)
                self.assertEqual(hass.services.calls, [])

    def test_bad_values_fail_static_and_live_without_dispatch(self):
        for value in (0, -1, 86401, 1.5, 1.0000001, True, "90", None, [], {}, math.nan, math.inf, 10**400):
            with self.subTest(value=str(value)):
                with self.assertRaises(base.layout.LayoutError):
                    base.layout.validate_action(self.action(value), "timer.example")
                hass, card = timer_environment("paused", action=self.action(value))
                self.assertIsNone(base.cards.resolve_action(hass, card))
                self.assertFalse(base.cards.presentation_payload(hass, [card], press_enabled_supported=True)["cards"][2]["press_enabled"])
                self.assertEqual(hass.services.calls, [])

    def test_missing_duration_preserves_existing_default_and_explicit_resume(self):
        for action in ({"kind": "default"}, {"kind": "service", "service": "timer.start", "data": {}}):
            hass, card = timer_environment("paused", action=action)
            result = base.cards.resolve_action(hass, card)
            self.assertEqual((result.service, result.data), ("start", {"entity_id": "timer.example"}))

    def test_capabilities_publish_optional_unit_step_without_mutation(self):
        hass, _ = timer_environment()
        before = deepcopy(base.layout.ACTION_FIELDS)
        actions = {item["service"]: item for item in base.cards.entity_actions(hass, hass.states.get("timer.example"))}
        field = actions["timer.start"]["fields"]["duration"]
        self.assertEqual(field, {"type": "number", "min": 1, "max": 86400, "required": False, "step": 1})
        field["max"] = 999
        self.assertEqual(base.layout.ACTION_FIELDS, before)
        self.assertEqual(actions["timer.cancel"]["fields"], {})

    def test_labels_describe_preset_and_cancel_without_claiming_success(self):
        for seconds, text in ((1, "0:01"), (90, "1:30"), (3600, "1:00:00"), (86400, "24:00:00")):
            for locale, verb in (("en", "Start"), ("pl-PL", "Uruchom")):
                hass, card = timer_environment("paused", action=self.action(seconds))
                wire = base.cards.presentation_payload(hass, [card], language=locale)["cards"][2]
                self.assertEqual(wire["subtitle"], f"{verb} {text}")
                self.assertLessEqual(len(wire["subtitle"]), 40)
        for locale, label in (("en", "Cancel"), ("pl", "Anuluj")):
            hass, card = timer_environment("active", action={"kind": "service", "service": "timer.cancel", "data": {}})
            self.assertEqual(base.cards.presentation_payload(hass, [card], language=locale)["cards"][2]["subtitle"], label)

    def test_unavailable_missing_service_and_readonly_never_gain_preset(self):
        for updates in ({"state": "unavailable"}, {"state": "unknown"}, {"present": False}, {"services": ()}, {"type": "sensor"}, {"visible": False}):
            hass, card = timer_environment(action=self.action(90), **updates)
            self.assertIsNone(base.cards.resolve_action(hass, card))
            self.assertEqual(hass.services.calls, [])

    def test_duration_is_not_allowed_on_pause_cancel_or_other_domains(self):
        for entity, service in (("timer.example", "timer.pause"), ("timer.example", "timer.cancel"), ("switch.example", "switch.turn_on")):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action({"kind": "service", "service": service, "data": {"duration": 90}}, entity)


class TimerPresetDispatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_contextual_press_dispatches_one_preset_and_rejects_old_revision(self):
        fixture = availability.TimerDefaultDispatchTests()
        bridge = fixture.bridge("paused")
        bridge.tile_cards[0]["action"] = {"kind": "service", "service": "timer.start", "data": {"duration": 90}}
        bridge._native_context_required, bridge._context_press_version = True, 1
        bridge.sent_revision = bridge.saved_revision = 0
        context = object()
        try:
            await bridge.async_press_tile(2, card_id="card-2", revision=0, context=context)
            self.assertEqual(len(bridge.hass.services.calls), 1)
            args, kwargs = bridge.hass.services.calls[0]
            self.assertEqual(args, ("timer", "start", {"entity_id": "timer.example", "duration": 90}))
            self.assertIs(kwargs["context"], context)
            bridge.saved_revision = 1
            await bridge.async_press_tile(2, card_id="card-2", revision=0, context=context)
            self.assertEqual(len(bridge.hass.services.calls), 1)
        finally:
            await fixture.retire(bridge)


if __name__ == "__main__":
    unittest.main()
