"""Automation taps distinguish enabling triggers from running actions."""

import unittest

import test_ha_layout as base
import test_input_button_availability as availability


SERVICES = ("automation.turn_on", "automation.turn_off", "automation.trigger")


def automation(**updates):
    return base.card(**{"entity": "automation.example", "type": "action", **updates})


class AutomationCardTests(unittest.TestCase):
    def test_default_enables_or_disables_without_triggering_or_stopping_a_run(self):
        for state, service, data in (
            ("off", "turn_on", {}),
            ("on", "turn_off", {"stop_actions": False}),
        ):
            hass, _ = base.environment(
                states=[base.State("automation.example", state)], services=SERVICES
            )
            action = base.cards.resolve_action(hass, automation())
            self.assertEqual(action.domain, "automation")
            self.assertEqual(action.service, service)
            self.assertEqual(action.data, {"entity_id": "automation.example", **data})
            self.assertFalse(hass.services.calls)
            hass.services.names.remove("automation." + service)
            self.assertIsNone(base.cards.resolve_action(hass, automation()))

    def test_explicit_run_and_stop_parameters_preserve_strict_booleans(self):
        for service, field in (
            ("automation.trigger", "skip_condition"),
            ("automation.turn_off", "stop_actions"),
        ):
            for value in (False, True):
                card = automation(
                    action={
                        "kind": "service",
                        "service": service,
                        "data": {field: value},
                    }
                )
                document = base.document([card])
                self.assertEqual(base.layout.validate_layout(document), document)
                hass, _ = base.environment(
                    states=[base.State("automation.example", "off")], services=SERVICES
                )
                self.assertIs(base.cards.resolve_action(hass, card).data[field], value)
            for value in (0, 1, "false", None, []):
                with (
                    self.subTest(value=value),
                    self.assertRaises(base.layout.LayoutError),
                ):
                    base.layout.validate_action(
                        {"kind": "service", "service": service, "data": {field: value}},
                        "automation.example",
                    )
            old = {"kind": "service", "service": service, "data": {}}
            self.assertEqual(
                base.layout.validate_action(old, "automation.example"), old
            )

    def test_unavailable_unknown_missing_and_information_never_resolve(self):
        for state in (None, "unknown", "unavailable", "pending", "ON"):
            states = [] if state is None else [base.State("automation.example", state)]
            hass, _ = base.environment(states=states, services=SERVICES)
            for action in (
                {"kind": "default"},
                {"kind": "service", "service": "automation.trigger", "data": {}},
            ):
                card = automation(action=action)
                self.assertTrue(base.cards.ordinary_action_availability(card))
                self.assertIsNone(base.cards.resolve_action(hass, card))
                wire = base.cards.presentation_payload(
                    hass,
                    base.cards.normalize_cards([card]),
                    press_enabled_supported=True,
                )["cards"][2]
                self.assertIs(wire["press_enabled"], False)
        hass, _ = base.environment(
            states=[base.State("automation.example", "on")], services=SERVICES
        )
        self.assertIsNone(
            base.cards.resolve_action(
                hass, automation(type="sensor", action={"kind": "none"})
            )
        )

    def test_prompts_palette_and_negotiated_availability_follow_authoritative_state(
        self,
    ):
        for state, prompt in (("off", "Włącz"), ("on", "Wyłącz")):
            card = automation(state_color=True)
            doc = base.document([card])
            self.assertEqual(base.layout.validate_layout(doc), doc)
            hass, _ = base.environment(
                states=[base.State("automation.example", state)], services=SERVICES
            )
            wire = base.cards.presentation_payload(
                hass,
                base.cards.normalize_cards([card]),
                language="pl",
                press_enabled_supported=True,
            )["cards"][2]
            self.assertEqual(wire["subtitle"], prompt)
            self.assertEqual(wire["palette"], "primary" if state == "on" else "surface")
            self.assertIs(wire["press_enabled"], True)
            card["action"] = {
                "kind": "service",
                "service": "automation.trigger",
                "data": {"skip_condition": False},
            }
            for language, label in (("pl", "Uruchom"), ("en", "Run")):
                wire = base.cards.presentation_payload(
                    hass, base.cards.normalize_cards([card]), language=language
                )["cards"][2]
                self.assertEqual(wire["subtitle"], label)


class AutomationDispatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_live_state_revision_and_caller_context_guard_default_and_explicit_run(
        self,
    ):
        fixture = availability.OneShotAvailabilityTests()
        bridge = fixture.bridge("automation", state="off")
        bridge.hass.services.names.update(SERVICES)
        bridge._native_context_required, bridge._context_press_version = True, 1
        bridge.sent_revision = bridge.saved_revision = 0
        context = object()
        try:
            await bridge.async_press_tile(
                2, card_id="card-2", revision=0, context=context
            )
            self.assertEqual(
                bridge.hass.services.calls[0][0],
                ("automation", "turn_on", {"entity_id": "automation.example"}),
            )
            bridge.hass.states.items["automation.example"] = base.State(
                "automation.example", "on"
            )
            await bridge.async_press_tile(
                2, card_id="card-2", revision=0, context=context
            )
            self.assertEqual(
                bridge.hass.services.calls[1][0],
                (
                    "automation",
                    "turn_off",
                    {"entity_id": "automation.example", "stop_actions": False},
                ),
            )
            bridge.tile_cards[0]["action"] = {
                "kind": "service",
                "service": "automation.trigger",
                "data": {"skip_condition": False},
            }
            await bridge.async_press_tile(
                2, card_id="card-2", revision=0, context=context
            )
            self.assertEqual(
                bridge.hass.services.calls[2][0],
                (
                    "automation",
                    "trigger",
                    {"entity_id": "automation.example", "skip_condition": False},
                ),
            )
            self.assertTrue(
                all(
                    kwargs["context"] is context
                    for _, kwargs in bridge.hass.services.calls
                )
            )
            bridge.saved_revision = 1
            await bridge.async_press_tile(
                2, card_id="card-2", revision=0, context=context
            )
            self.assertEqual(len(bridge.hass.services.calls), 3)
            bridge.saved_revision = 0
            bridge.hass.states.items["automation.example"] = base.State(
                "automation.example", "unknown"
            )
            await bridge.async_press_tile(
                2, card_id="card-2", revision=0, context=context
            )
            self.assertEqual(len(bridge.hass.services.calls), 3)
        finally:
            await fixture.retire(bridge)


if __name__ == "__main__":
    unittest.main()
