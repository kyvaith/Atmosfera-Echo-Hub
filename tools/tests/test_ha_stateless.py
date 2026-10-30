"""Isolated W01 proposal tests; synthetic HA states/services only."""

from __future__ import annotations

import types
import unittest
from copy import deepcopy

import test_ha_layout as base

cards = base.cards
STAMP = "2026-10-24T10:00:00+00:00"


def example(domain, state="unknown", action=None, **updates):
    entity = f"{domain}.example"
    services = [f"{domain}.press"] if domain in ("button", "input_button") else [f"{domain}.turn_on", f"{domain}.turn_off"]
    hass, _ = base.environment(states=[base.State(entity, state)], services=services)
    card = base.card(entity=entity, type="action", **updates)
    if action is not None:
        card["action"] = action
    return hass, card


class StatelessProposalTests(unittest.TestCase):
    def test_never_pressed_buttons_resolve_exact_default_press_without_dispatch(self):
        for domain in ("button", "input_button"):
            with self.subTest(domain=domain):
                hass, card = example(domain)
                result = cards.resolve_action(hass, card)
                self.assertEqual((result.domain, result.service, result.data), (domain, "press", {"entity_id": card["entity_id"]}))
                self.assertEqual(hass.services.calls, [])

    def test_unactivated_scene_unknown_and_activated_timestamp_both_resolve_turn_on(self):
        for state in ("unknown", STAMP):
            hass, card = example("scene", state)
            result = cards.resolve_action(hass, card)
            self.assertEqual((result.domain, result.service), ("scene", "turn_on"))
            self.assertEqual(hass.services.calls, [])

    def test_script_unknown_is_not_inferred_idle_but_real_on_off_states_keep_default_run(self):
        hass, card = example("script")
        self.assertIsNone(cards.resolve_action(hass, card))
        for state in ("on", "off"):
            hass, card = example("script", state)
            self.assertEqual(cards.resolve_action(hass, card).service, "turn_on")

    def test_unavailable_missing_and_service_removed_all_block(self):
        for domain in ("button", "input_button", "scene", "script"):
            with self.subTest(domain=domain):
                hass, card = example(domain, "unavailable")
                self.assertIsNone(cards.resolve_action(hass, card))
                hass.states.items.clear()
                self.assertIsNone(cards.resolve_action(hass, card))
                hass, card = example(domain, "off" if domain == "script" else "unknown")
                hass.services.names.clear()
                self.assertIsNone(cards.resolve_action(hass, card))

    def test_unknown_non_timestamp_domains_do_not_gain_an_action(self):
        for domain in ("light", "switch", "input_boolean", "fan", "sensor", "binary_sensor", "number", "automation", "script"):
            hass, card = example(domain)
            hass.services.names.update({f"{domain}.toggle", f"{domain}.turn_on", "homeassistant.turn_on"})
            self.assertIsNone(cards.resolve_action(hass, card), domain)
            card["action"] = {"kind": "service", "service": f"{domain}.turn_on", "data": {}}
            self.assertIsNone(cards.resolve_action(hass, card), domain)

    def test_explicit_none_read_only_hidden_and_reserved_cards_remain_non_executable(self):
        for updates in ({"action": {"kind": "none"}}, {"type": "sensor", "action": {"kind": "none"}}, {"visible": False}, {"slot": 0}):
            hass, card = example("button")
            card.update(updates)
            self.assertIsNone(cards.resolve_action(hass, card))

    def test_explicit_script_stop_and_same_domain_typed_validation_are_preserved(self):
        stop = {"kind": "service", "service": "script.turn_off", "data": {}}
        hass, card = example("script", "on", stop)
        resolved = cards.resolve_action(hass, card)
        self.assertEqual((resolved.domain, resolved.service), ("script", "turn_off"))
        for action in (
            {"kind": "service", "service": "button.press", "data": {}},
            {"kind": "service", "service": "script.anything", "data": {}},
            {"kind": "service", "service": "script.turn_on", "data": {"entity_id": "script.other"}},
        ):
            card["action"] = action
            self.assertIsNone(cards.resolve_action(hass, card))

    def test_press_run_labels_are_localized_action_prompts_not_timestamps_or_completion(self):
        for domain, state in (("button", "unknown"), ("input_button", STAMP), ("scene", "unknown"), ("scene", STAMP), ("script", "off"), ("script", "on")):
            hass, card = example(domain, state)
            original = deepcopy(card)
            for language in ("en", "pl"):
                wire = cards.presentation_payload(hass, [card], language=language)["cards"][2]
                expected = ("Naciśnij" if language == "pl" else "Press") if domain in ("button", "input_button") else ("Uruchom" if language == "pl" else "Run")
                self.assertEqual(wire["subtitle"], expected)
                self.assertEqual(wire["title"], original["title"])
                self.assertEqual(wire["id"], original["id"])
                self.assertNotIn("action", wire)
                self.assertLessEqual(len(wire["subtitle"]), 40)
            self.assertEqual(card, original)
            self.assertEqual(hass.services.calls, [])

    def test_disabled_or_different_explicit_action_never_gets_a_misleading_run_prompt(self):
        for action in ({"kind": "none"}, {"kind": "service", "service": "script.turn_off", "data": {}}):
            hass, card = example("script", "on", action)
            self.assertEqual(cards.presentation_payload(hass, [card])["cards"][2]["subtitle"], "On")
        hass, card = example("button", STAMP)
        hass.services.names.clear()
        self.assertEqual(cards.presentation_payload(hass, [card])["cards"][2]["subtitle"], STAMP)

    def test_missing_and_unavailable_still_have_localized_exceptional_labels(self):
        hass, card = example("button", "unavailable")
        self.assertEqual(cards.presentation_payload(hass, [card], language="pl")["cards"][2]["subtitle"], "Niedostępny")
        hass.states.items.clear()
        self.assertEqual(cards.presentation_payload(hass, [card], language="pl")["cards"][2]["subtitle"], "Niedostępny")

    def test_read_only_timestamp_card_keeps_original_information(self):
        hass, card = example("scene", STAMP)
        card.update(type="sensor", action={"kind": "none"})
        self.assertEqual(cards.presentation_payload(hass, [card])["cards"][2]["subtitle"], STAMP)

    def test_catalogue_eligibility_distinguishes_never_fired_timestamp_entities(self):
        states = [base.State(f"{domain}.example", "unknown") for domain in ("button", "input_button", "scene", "script", "light", "sensor")]
        hass, _ = base.environment(states=states, services=["button.press", "input_button.press", "scene.turn_on", "script.turn_on"])
        catalogue = {item["domain"]: item for item in cards.entity_catalogue(hass)["entities"]}
        for domain in ("button", "input_button", "scene"):
            self.assertTrue(catalogue[domain]["available"], domain)
            self.assertEqual(len(catalogue[domain]["actions"]), 1)
        for domain in ("script", "light", "sensor"):
            self.assertFalse(catalogue[domain]["available"], domain)
        self.assertEqual(hass.services.calls, [])


def bridge_for(domain="button"):
    bridge = base.BridgeTests.bridge(None)
    hass, card = example(domain)
    bridge.hass = hass
    bridge.tile_cards, bridge.tile_entity_ids = [card], [card["entity_id"]]
    bridge._native_context_required, bridge._context_press_version = True, 1
    bridge.saved_revision = bridge.sent_revision = 0
    return bridge


class StatelessDispatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_one_correlated_report_dispatches_one_service_with_unchanged_context(self):
        for domain in ("button", "input_button", "scene"):
            bridge = bridge_for(domain)
            context = types.SimpleNamespace(user_id="allowed")
            await bridge.async_press_tile(2, card_id="card-2", revision=0, context=context)
            self.assertEqual(len(bridge.hass.services.calls), 1)
            args, kwargs = bridge.hass.services.calls[0]
            expected = "press" if domain in ("button", "input_button") else "turn_on"
            self.assertEqual(args, (domain, expected, {"entity_id": f"{domain}.example"}))
            self.assertIs(kwargs["context"], context)

    async def test_wrong_context_revision_pending_and_disconnected_are_still_rejected(self):
        for mode in ("identity", "revision", "pending", "unavailable", "legacy"):
            bridge = bridge_for()
            kwargs = {"card_id": "card-2", "revision": 0}
            if mode == "identity":
                kwargs["card_id"] = "other"
            elif mode == "revision":
                kwargs["revision"] = 1
            elif mode == "pending":
                bridge.sent_revision = None
            elif mode == "unavailable":
                bridge.esphome_entry.runtime_data.available = False
            else:
                kwargs = {}
            await bridge.async_press_tile(2, **kwargs)
            self.assertEqual(bridge.hass.services.calls, [], mode)

    async def test_restricted_context_is_forwarded_and_denied_before_fake_execution(self):
        bridge = bridge_for()
        context = types.SimpleNamespace(user_id="denied")
        observed = []

        async def permission_checked(*_args, **kwargs):
            observed.append(kwargs["context"])
            raise PermissionError("Denied by synthetic HA permission check")

        bridge.hass.services.async_call = permission_checked
        with self.assertRaises(PermissionError):
            await bridge.async_press_tile(2, card_id="card-2", revision=0, context=context)
        self.assertEqual(observed, [context])
        self.assertEqual(bridge.hass.services.calls, [])


if __name__ == "__main__":
    unittest.main()
