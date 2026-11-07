"""Choice admission is explicit and cannot be inferred from a product profile."""

from copy import deepcopy
import json
from types import SimpleNamespace as NS
import unittest

import test_ha_layout as base
import test_entity_control as generic


class ChoiceModelTests(unittest.TestCase):
    def test_invalid_live_list_is_passive_even_with_extended_native(self):
        card = base.card(entity="input_select.test", action={"kind": "control", "control": "choice"})
        for options in ([], ["x"] * 9, ["a", "a"], ["unknown"], ["x" * 33]):
            hass, _ = base.environment(states=[base.State(card["entity_id"], "a", {"options": options})],
                                       services=["input_select.select_option"])
            wire = base.cards.presentation_payload(hass, [card], choice_control_supported=True,
                                                  press_enabled_supported=True)["cards"][2]
            self.assertNotIn("control_kind", wire)
            self.assertIs(wire["press_enabled"], False)
            self.assertEqual(wire["subtitle"], "Options unavailable")
        hass, _ = base.environment(states=[base.State(card["entity_id"], "unknown", {"options": ["Eco", "Boost"]})],
                                   services=["input_select.select_option"])
        wire = base.cards.presentation_payload(hass, [card], choice_control_supported=True,
                                              press_enabled_supported=True)["cards"][2]
        self.assertEqual(wire["control_kind"], "choice")
        self.assertNotIn("press_enabled", wire)

    def test_both_domains_roundtrip_v3_and_old_native_stays_passive(self):
        for domain in ("select", "input_select"):
            card = base.card(
                entity=domain + ".test", action={"kind": "control", "control": "choice"}
            )
            doc = base.document([card]) | {"version": 3}
            self.assertEqual(base.layout.validate_layout(doc), doc)
            self.assertEqual(
                base.layout.import_layout(base.layout.export_layout(doc), 5),
                doc | {"revision": 5},
            )
            hass, _ = base.environment(
                states=[
                    base.State(card["entity_id"], "Eco", {"options": ["Eco", "Boost"]})
                ],
                services=[domain + ".select_option"],
            )
            self.assertIsNone(base.cards.resolve_action(hass, card))
            wire = base.cards.presentation_payload(hass, [card])["cards"][2]
            self.assertNotIn("control_kind", wire)
            self.assertNotIn("press_enabled", wire)
            self.assertEqual(wire["subtitle"], "Unsupported device")
            wire = base.cards.presentation_payload(
                hass, [card], choice_control_supported=True
            )["cards"][2]
            self.assertEqual(wire["control_kind"], "choice")
            for entity in ("number.test", "light.test", "sensor.test"):
                with self.assertRaises(base.layout.LayoutError):
                    base.layout.validate_layout(
                        doc | {"cards": [card | {"entity_id": entity}]}
                    )
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(doc | {"version": 2})

    def test_metadata_rejects_whole_bad_lists_and_preserves_exact_values(self):
        state = base.State(
            "input_select.test", " Eco ", {"options": [" Eco ", "Żółty"]}
        )
        hass, _ = base.environment(
            states=[state], services=["input_select.select_option"]
        )
        original = deepcopy(state.attributes)
        self.assertEqual(
            base.cards._choice_control_metadata(hass, state),
            {"choice_control": {"options": original["options"], "index": 0}},
        )
        self.assertEqual(state.attributes, original)
        for options in ([], ["Eco", "Eco"], ["a"] * 9, ["ą" * 17], None):
            state.attributes["options"] = options
            self.assertEqual(base.cards._choice_control_metadata(hass, state), {})
        state.attributes = original
        state.state = "unknown"
        self.assertIsNone(
            base.cards._choice_control_metadata(hass, state)["choice_control"]["index"]
        )
        hass.services.names.clear()
        self.assertEqual(base.cards._choice_control_metadata(hass, state), {})


class ChoiceTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_only_actual_extended_capability_admits_choice(self):
        fixture = generic.NumberModelTransportTests()
        for extended in (False, True):
            bridge = fixture.generic_bridge()
            original = bridge.runtime.client.execute_service

            async def execute(action, data, **kwargs):
                result = await original(action, data, **kwargs)
                if extended and action.name == "entity_control_get_status":
                    value = json.loads(result.response_data)
                    value["control_kinds"].append("choice")
                    return NS(
                        success=True, response_data=generic.codec.encode(value).encode()
                    )
                return result

            bridge.runtime.client.execute_service = execute
            try:
                self.assertTrue(await bridge._light_control.async_negotiate())
                self.assertIs(bridge._light_control.choice_supported, extended)
                self.assertEqual(
                    bridge._light_control.status()["control_kinds"],
                    ["light", "number"] + (["choice"] if extended else []),
                )
                bridge._light_control.invalidate_connection()
                self.assertIs(bridge._light_control.choice_supported, False)
            finally:
                await bridge._light_control.async_shutdown()
