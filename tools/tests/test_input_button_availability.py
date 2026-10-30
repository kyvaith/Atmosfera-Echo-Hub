"""Negotiated ordinary input_button availability through the actual HA adapter."""

from __future__ import annotations

import asyncio
from copy import deepcopy
import json
import types
import unittest

import test_ha_layout as base

MISSING = object()


def button_card(**updates):
    return base.card(entity="input_button.example", **{"type": "action", **updates})


def environment(state="unknown", *, service=True, **updates):
    states = [] if state is None else [base.State("input_button.example", state)]
    hass, _ = base.environment(states=states, services=["input_button.press"] if service else [])
    return hass, button_card(**updates)


def status(version=MISSING, *, configured=1):
    result = {"profile": base.layout.PROFILE_ID, "context_press_version": 1,
              "configured_context_version": configured, "revision": 0,
              "snapshot_ready": True, "pending_slots": 0}
    if version is not MISSING:
        result["press_enabled_version"] = version
    return result


class InputButtonProjectionTests(unittest.TestCase):
    def project(self, hass, card, supported=True):
        return base.cards.presentation_payload(hass, [card], press_enabled_supported=supported)["cards"][card["slot"]]

    def test_legacy_projection_is_unchanged_without_negotiation(self):
        hass, card = environment()
        before = base.cards.presentation_payload(hass, [card])
        for supported in (False, 0, 1, "1", None):
            with self.subTest(supported=supported):
                self.assertEqual(base.cards.presentation_payload(hass, [card], press_enabled_supported=supported), before)
        self.assertNotIn("press_enabled", before["cards"][2])

    def test_never_pressed_unknown_and_valid_timestamp_are_enabled(self):
        for state in ("unknown", "2026-10-25T17:00:00+00:00"):
            hass, card = environment(state)
            original = deepcopy(card)
            self.assertIs(self.project(hass, card)["press_enabled"], True)
            self.assertEqual(card, original)
            self.assertEqual(hass.services.calls, [])

    def test_unavailable_missing_or_removed_service_are_disabled(self):
        for state, service in (("unavailable", True), (None, True), ("unknown", False)):
            with self.subTest(state=state, service=service):
                hass, card = environment(state, service=service)
                self.assertIs(self.project(hass, card)["press_enabled"], False)
                self.assertEqual(hass.services.calls, [])

    def test_none_sensor_hidden_and_reserved_are_disabled(self):
        for updates in ({"action": {"kind": "none"}},
                        {"type": "sensor", "action": {"kind": "none"}},
                        {"visible": False}, {"slot": 0}):
            with self.subTest(updates=updates):
                hass, card = environment(**updates)
                self.assertIs(self.project(hass, card)["press_enabled"], False)

    def test_other_domains_and_both_control_kinds_have_identical_projection(self):
        for domain, control in (("automation", None), ("light", "light"),
                                ("input_number", "number")):
            with self.subTest(domain=domain):
                entity = domain + ".example"
                attributes = {"min": -1, "max": 1, "step": 0.25}
                hass, _ = base.environment(states=[base.State(entity, "on", attributes)], services=[domain + ".press"])
                card = base.card(entity=entity)
                if control:
                    card["action"] = {"kind": "control", "control": control}
                kwargs = {"light_control_supported": True, "number_control_supported": True}
                before = base.cards.presentation_payload(hass, [card], **kwargs)
                after = base.cards.presentation_payload(hass, [card], press_enabled_supported=True, **kwargs)
                self.assertEqual(after, before)
                self.assertNotIn("press_enabled", after["cards"][2])

    def test_control_marker_never_gets_ordinary_availability_even_for_invalid_domain(self):
        hass, card = environment(action={"kind": "control", "control": "number"})
        self.assertNotIn("press_enabled", self.project(hass, card))


class InputButtonNegotiationTests(unittest.IsolatedAsyncioTestCase):
    def bridge(self, version=MISSING, *, state="unknown", configured=1):
        bridge = base.BridgeTests.bridge(None)
        bridge._press_enabled_version = 0
        hass, card = environment(state)
        bridge.hass.states, bridge.hass.services = hass.states, hass.services
        bridge.tile_cards, bridge.tile_entity_ids = [card], [card["entity_id"]]
        bridge.events = []
        bridge.response_version, bridge.response_configured = version, configured
        bridge.status_action = types.SimpleNamespace(supports_response=base.controller.SupportsResponseType.ONLY)
        bridge.set_action = object()
        bridge._find_api_action = lambda name: bridge.status_action if name == "home_tiles_get_status" else bridge.set_action

        async def execute(action, data, **_kwargs):
            if action is bridge.status_action:
                bridge.events.append(("status", None))
                return types.SimpleNamespace(success=True, response_data=json.dumps(
                    status(bridge.response_version, configured=bridge.response_configured)).encode())
            bridge.events.append(("set", json.loads(data["payload"])))
            return None

        bridge.esphome_entry.runtime_data.client.execute_service = execute
        return bridge

    async def test_capability_is_negotiated_before_first_supported_payload(self):
        bridge = self.bridge(1, state="unavailable", configured=0)
        self.assertTrue(await bridge.async_push_tiles())
        self.assertEqual(bridge.events[0][0], "status")
        payloads = [value for name, value in bridge.events if name == "set"]
        self.assertEqual(len(payloads), 1)
        self.assertIs(payloads[0]["cards"][2]["press_enabled"], False)
        self.assertEqual(bridge._press_enabled_version, 1)
        self.assertEqual(bridge.sent_revision, 0)
        self.assertIsNone(bridge.accepted_revision)
        self.assertEqual(bridge.hass.services.calls, [])
        bridge._cancel_native_status_requery()
        await asyncio.gather(*bridge._background_tasks, return_exceptions=True)

    async def test_old_status_omits_field_and_wire_stays_legacy(self):
        for version in (MISSING, 0):
            with self.subTest(version=version):
                bridge = self.bridge(version)
                self.assertTrue(await bridge.async_push_tiles())
                payload = next(value for name, value in bridge.events if name == "set")
                self.assertNotIn("press_enabled", payload["cards"][2])
                self.assertEqual(bridge._press_enabled_version, 0)

    async def test_unsupported_status_api_keeps_exact_legacy_payload(self):
        bridge = self.bridge(1)
        bridge._find_api_action = lambda _name: bridge.set_action
        self.assertTrue(await bridge.async_push_tiles())
        self.assertEqual([name for name, _value in bridge.events], ["set"])
        self.assertNotIn("press_enabled", bridge.events[0][1]["cards"][2])

    async def test_malformed_optional_versions_revoke_stale_positive_and_reject_status(self):
        for version in (True, False, "1", 2, -1, None):
            with self.subTest(version=version):
                bridge = self.bridge(version)
                bridge._press_enabled_version = 1
                await bridge._async_refresh_native_status(force=True)
                self.assertEqual(bridge._press_enabled_version, 0)
                self.assertEqual(bridge._native_status_epoch, -1)
                self.assertIsNone(bridge.accepted_revision)

    async def test_failed_or_absent_status_probe_drops_stale_positive(self):
        for mode in ("missing", "timeout", "failure", "bad_json"):
            with self.subTest(mode=mode):
                bridge = self.bridge(1)
                bridge._press_enabled_version = 1
                if mode == "missing":
                    bridge._find_api_action = lambda _name: None
                else:
                    async def execute(*_args, mode=mode, **_kwargs):
                        if mode == "timeout":
                            raise TimeoutError
                        return types.SimpleNamespace(success=mode != "failure", response_data=b"not JSON")
                    bridge.esphome_entry.runtime_data.client.execute_service = execute
                await bridge._async_refresh_native_status(force=True)
                self.assertEqual(bridge._press_enabled_version, 0)

    async def test_missing_optional_version_clears_previous_positive(self):
        bridge = self.bridge()
        bridge._press_enabled_version = 1
        await bridge._async_refresh_native_status(force=True)
        self.assertEqual(bridge._press_enabled_version, 0)
        self.assertEqual(bridge._native_status_epoch, 0)

    async def test_old_epoch_status_cannot_enable_or_send_new_connection_payload(self):
        bridge = self.bridge(1)
        async def replace(*_args, **_kwargs):
            bridge._connection_epoch += 1
            bridge._press_enabled_version = 0
            bridge.esphome_entry.runtime_data = types.SimpleNamespace(available=False)
            return types.SimpleNamespace(success=True, response_data=json.dumps(status(1)).encode())
        bridge.esphome_entry.runtime_data.client.execute_service = replace
        self.assertFalse(await bridge.async_push_tiles())
        self.assertEqual(bridge._press_enabled_version, 0)
        self.assertIsNone(bridge.sent_revision)
        self.assertEqual(bridge.events, [])

    async def test_reconnect_and_shutdown_revoke_negotiated_capability(self):
        bridge = self.bridge(1)
        bridge._press_enabled_version = 1
        bridge.async_schedule_push = bridge.async_schedule_tile_push = lambda **_kwargs: None
        bridge._esphome_device_updated()
        self.assertEqual(bridge._press_enabled_version, 0)
        await asyncio.gather(*bridge._background_tasks, return_exceptions=True)
        bridge._press_enabled_version = 1
        await bridge.async_shutdown()
        self.assertEqual(bridge._press_enabled_version, 0)
        self.assertTrue(bridge._closed)


def one_shot(
    domain, state=None, *, present=True, service=True, attributes=None, **updates
):
    state = ("off" if domain == "script" else "unknown") if state is None else state
    entity = domain + ".example"
    operation = "press" if domain in ("button", "input_button") else "turn_on"
    hass, _ = base.environment(
        states=[base.State(entity, state, attributes)] if present else [],
        services=[domain + "." + operation] if service else [],
    )
    return hass, base.card(entity=entity, **{"type": "action", **updates})


class OneShotAvailabilityTests(unittest.IsolatedAsyncioTestCase):
    domains = ("input_button", "button", "scene", "script")

    def project(self, hass, card, **kwargs):
        return base.cards.presentation_payload(
            hass, [card], press_enabled_supported=True, **kwargs
        )["cards"][card["slot"]]

    def bridge(self, domain, version=1, **kwargs):
        bridge = InputButtonNegotiationTests.bridge(None, version, configured=0)
        hass, card = one_shot(domain, **kwargs)
        bridge.hass.states, bridge.hass.services = hass.states, hass.services
        bridge.tile_cards, bridge.tile_entity_ids = [card], [card["entity_id"]]
        return bridge

    async def retire(self, bridge):
        bridge._cancel_native_status_requery()
        await asyncio.gather(*bridge._background_tasks, return_exceptions=True)

    def test_public_domain_predicate_and_original_state_script_mode_policy(self):
        for domain in self.domains:
            for state in ("unknown", "2026-10-25T17:00:00+00:00", "on", "off"):
                with self.subTest(domain=domain, state=state):
                    hass, card = one_shot(domain, state)
                    original = deepcopy(card)
                    self.assertTrue(base.cards.ordinary_action_availability(card))
                    self.assertIs(
                        self.project(hass, card)["press_enabled"],
                        not (domain == "script" and state == "unknown"),
                    )
                    self.assertEqual(card, original)
                    self.assertEqual(hass.services.calls, [])
        for mode in ("single", "restart", "queued", "parallel"):
            for current in (0, 2):
                hass, card = one_shot(
                    "script", "on", attributes={"mode": mode, "current": current}
                )
                self.assertIs(self.project(hass, card)["press_enabled"], True)
        for domain in (
            "automation",
            "light",
            "input_number",
            "buttonish",
            "xbutton",
            "",
        ):
            self.assertFalse(
                base.cards.ordinary_action_availability(
                    base.card(entity=domain + ".example")
                )
            )
        for domain in self.domains:
            card = one_shot(domain)[1]
            card["action"] = {"kind": "control", "control": "number"}
            self.assertFalse(base.cards.ordinary_action_availability(card))

    def test_live_resolver_missing_unavailable_service_and_nonaction_matrix(self):
        for domain in self.domains:
            for options in (
                {"state": "unavailable"},
                {"present": False},
                {"service": False},
                {"action": {"kind": "none"}},
                {"type": "sensor", "action": {"kind": "none"}},
                {"visible": False},
                {"slot": 0},
                {"action": {"kind": "service", "service": "light.turn_on", "data": {}}},
            ):
                with self.subTest(domain=domain, options=options):
                    hass, card = one_shot(domain, **options)
                    self.assertIs(self.project(hass, card)["press_enabled"], False)
                    self.assertEqual(hass.services.calls, [])
        hass, card = one_shot(
            "script",
            "on",
            action={"kind": "service", "service": "script.turn_off", "data": {}},
        )
        hass.services.names.add("script.turn_off")
        self.assertIs(self.project(hass, card)["press_enabled"], True)
        self.assertEqual(base.cards.resolve_action(hass, card).service, "turn_off")

    def test_legacy_capability_other_domains_and_generic_controls_keep_wire(self):
        for domain in self.domains:
            hass, card = one_shot(domain)
            before = base.cards.presentation_payload(hass, [card])
            for supported in (False, 0, 1, "1", None):
                self.assertEqual(
                    base.cards.presentation_payload(
                        hass, [card], press_enabled_supported=supported
                    ),
                    before,
                )
        for domain, control in (
            ("automation", None),
            ("switch", None),
            ("light", "light"),
            ("input_number", "number"),
        ):
            hass, card = one_shot(
                domain, "on", attributes={"min": -1, "max": 1, "step": 0.25}
            )
            if control:
                card["action"] = {"kind": "control", "control": control}
            options = {
                "light_control_supported": True,
                "number_control_supported": True,
            }
            before = base.cards.presentation_payload(hass, [card], **options)
            self.assertEqual(
                base.cards.presentation_payload(
                    hass, [card], press_enabled_supported=True, **options
                ),
                before,
            )
            self.assertNotIn("press_enabled", before["cards"][2])

    async def test_each_domain_negotiates_before_first_set_and_epoch_change_refuses(
        self,
    ):
        for domain in self.domains:
            bridge = self.bridge(domain)
            self.assertTrue(await bridge.async_push_tiles())
            self.assertEqual(bridge.events[0][0], "status")
            payload = next(value for name, value in bridge.events if name == "set")
            self.assertIs(payload["cards"][2]["press_enabled"], True)
            self.assertEqual(bridge.hass.services.calls, [])
            await self.retire(bridge)
            bridge = self.bridge(domain)

            async def replace(*_args, **_kwargs):
                bridge._connection_epoch += 1
                bridge._press_enabled_version = 0
                bridge.esphome_entry.runtime_data = types.SimpleNamespace(
                    available=False
                )
                return types.SimpleNamespace(
                    success=True, response_data=json.dumps(status(1)).encode()
                )

            bridge.esphome_entry.runtime_data.client.execute_service = replace
            self.assertFalse(await bridge.async_push_tiles())
            self.assertEqual(bridge.events, [])
            self.assertIsNone(bridge.sent_revision)
            await self.retire(bridge)

    async def test_each_domain_failed_missing_malformed_capability_omits_field(self):
        for domain in self.domains:
            for version in (MISSING, 0, True, "1", 2):
                bridge = self.bridge(domain, version)
                bridge._press_enabled_version = 1
                self.assertTrue(await bridge.async_push_tiles())
                payload = next(value for name, value in bridge.events if name == "set")
                self.assertNotIn("press_enabled", payload["cards"][2])
                self.assertEqual(bridge._press_enabled_version, 0)
                await self.retire(bridge)
            bridge = self.bridge(domain)
            bridge._press_enabled_version = 1
            original = bridge.esphome_entry.runtime_data.client.execute_service

            async def timeout(action, data, **kwargs):
                if action is bridge.status_action:
                    raise TimeoutError
                return await original(action, data, **kwargs)

            bridge.esphome_entry.runtime_data.client.execute_service = timeout
            self.assertTrue(await bridge.async_push_tiles())
            payload = next(value for name, value in bridge.events if name == "set")
            self.assertNotIn("press_enabled", payload["cards"][2])
            self.assertEqual(bridge._press_enabled_version, 0)
            await self.retire(bridge)

    async def test_dispatch_reresolves_removed_service_and_one_scene_keeps_context(
        self,
    ):
        for domain in self.domains:
            bridge = self.bridge(domain)
            self.assertIs(
                self.project(bridge.hass, bridge.tile_cards[0])["press_enabled"], True
            )
            bridge._native_context_required, bridge._context_press_version = True, 1
            bridge.sent_revision = bridge.saved_revision = 0
            bridge.hass.services.names.clear()
            await bridge.async_press_tile(
                2, card_id="card-2", revision=0, context=object()
            )
            self.assertEqual(bridge.hass.services.calls, [])
        bridge = self.bridge("scene")
        bridge._native_context_required, bridge._context_press_version = True, 1
        bridge.sent_revision = bridge.saved_revision = 0
        context = types.SimpleNamespace(user_id="allowed")
        await bridge.async_press_tile(2, card_id="card-2", revision=0, context=context)
        self.assertEqual(len(bridge.hass.services.calls), 1)
        args, kwargs = bridge.hass.services.calls[0]
        self.assertEqual(args, ("scene", "turn_on", {"entity_id": "scene.example"}))
        self.assertIs(kwargs["context"], context)

    def test_full16_utf8_payload_bound_exact_delta_and_no_input_mutation(self):
        cards, states, services = [], [], []
        for slot in range(16):
            domain = self.domains[slot % 4]
            entity = domain + ".example_" + str(slot)
            states.append(
                base.State(entity, "off" if domain == "script" else "unknown")
            )
            services.append(
                domain
                + (".press" if domain in ("button", "input_button") else ".turn_on")
            )
            cards.append(
                base.card(slot=slot, entity=entity, title="Ł" * 40, type="action")
            )
        hass, _ = base.environment(states=states, services=services)
        original = deepcopy(cards)
        before = base.cards.presentation_payload(hass, cards)
        after = base.cards.presentation_payload(
            hass, cards, press_enabled_supported=True
        )

        def encode(body):
            return json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode(
                "utf-8"
            )

        self.assertLess(len(encode(after)), 32768)
        expected = sum(
            len(',"press_enabled":' + str(c["press_enabled"]).lower())
            for c in after["cards"]
        )
        self.assertEqual(len(encode(after)) - len(encode(before)), expected)
        self.assertLessEqual(expected, 352)
        self.assertEqual(cards, original)
        self.assertEqual(hass.services.calls, [])

    async def test_nonparticipating_and_control_only_do_not_add_first_probe(self):
        for domain, action in (
            ("automation", {"kind": "none"}),
            ("light", {"kind": "control", "control": "light"}),
            ("input_number", {"kind": "control", "control": "number"}),
        ):
            bridge = self.bridge(domain, action=action)
            self.assertTrue(await bridge.async_push_tiles())
            self.assertEqual(bridge.events[0][0], "set")
            self.assertNotIn("press_enabled", bridge.events[0][1]["cards"][2])
            await self.retire(bridge)



def timer_environment(state="idle", *, present=True, services=("start", "pause", "cancel"), **updates):
    entity = "timer.example"
    hass, _ = base.environment(
        states=[base.State(entity, state, {"duration": "1:00:00", "remaining": "0:02:03"})] if present else [],
        services=["timer." + name for name in services],
    )
    return hass, base.card(entity=entity, title="My timer", icon="clock", **updates)


class TimerDefaultActionTests(unittest.TestCase):
    def test_live_default_state_selects_exact_service_and_never_supplies_duration(self):
        for state, operation in (("idle", "start"), ("active", "pause"), ("paused", "start")):
            hass, card = timer_environment(state)
            before = deepcopy(hass.states.get(card["entity_id"]).attributes)
            action = base.cards.resolve_action(hass, card)
            self.assertEqual((action.domain, action.service, action.data), ("timer", operation, {"entity_id": "timer.example"}))
            self.assertEqual(hass.states.get(card["entity_id"]).attributes, before)
            self.assertEqual(hass.services.calls, [])

    def test_unknown_unavailable_missing_and_unrecognized_states_are_not_guessed(self):
        for state in ("unknown", "unavailable", "finished", "on", "", None, True):
            hass, card = timer_environment(state)
            self.assertIsNone(base.cards.resolve_action(hass, card))
            self.assertIs(base.cards.presentation_payload(hass, [card], press_enabled_supported=True)["cards"][2]["press_enabled"], False)
        hass, card = timer_environment(present=False)
        self.assertIsNone(base.cards.resolve_action(hass, card))

    def test_only_the_current_service_is_required_and_removal_blocks(self):
        for state, operation in (("idle", "start"), ("active", "pause"), ("paused", "start")):
            hass, card = timer_environment(state, services=(operation,))
            self.assertEqual(base.cards.resolve_action(hass, card).service, operation)
            hass.services.names = {"homeassistant.turn_on", "timer.cancel"}
            self.assertIsNone(base.cards.resolve_action(hass, card))

    def test_explicit_services_and_read_only_information_keep_existing_behavior(self):
        for operation in ("start", "pause", "cancel"):
            hass, card = timer_environment("paused", action={"kind": "service", "service": "timer." + operation, "data": {}})
            self.assertEqual(base.cards.resolve_action(hass, card).service, operation)
            self.assertEqual(base.cards.presentation_payload(hass, [card])["cards"][2]["subtitle"], "Paused")
        hass, card = timer_environment("idle", type="sensor", action={"kind": "none"})
        self.assertIsNone(base.cards.resolve_action(hass, card))
        self.assertEqual(base.cards.presentation_payload(hass, [card])["cards"][2]["subtitle"], "Idle")

    def test_default_action_prompts_are_localized_bounded_and_not_execution_results(self):
        for state, english, polish in (("idle", "Start", "Uruchom"), ("active", "Pause", "Wstrzymaj"), ("paused", "Resume", "Wznów")):
            hass, card = timer_environment(state)
            original = deepcopy(card)
            for locale, label in (("en", english), ("pl-PL", polish)):
                wire = base.cards.presentation_payload(hass, [card], language=locale)["cards"][2]
                self.assertEqual(wire["subtitle"], label)
                self.assertEqual((wire["id"], wire["title"]), (original["id"], original["title"]))
                self.assertLessEqual(len(wire["subtitle"]), 40)
            hass.services.names.clear()
            self.assertEqual(base.cards.presentation_payload(hass, [card])["cards"][2]["subtitle"], state.title())
            self.assertEqual(card, original)
            self.assertEqual(hass.services.calls, [])

    def test_none_hidden_reserved_and_controls_do_not_gain_execution(self):
        for updates in ({"action": {"kind": "none"}}, {"visible": False}, {"slot": 0}):
            hass, card = timer_environment(**updates)
            self.assertIsNone(base.cards.resolve_action(hass, card))
            wire = base.cards.presentation_payload(hass, [card], press_enabled_supported=True)["cards"][card["slot"]]
            self.assertIs(wire["press_enabled"], False)
        hass, card = timer_environment(action={"kind": "control", "control": "number"})
        self.assertFalse(base.cards.ordinary_action_availability(card))
        self.assertNotIn("press_enabled", base.cards.presentation_payload(hass, [card], press_enabled_supported=True)["cards"][2])

    def test_optional_flag_requires_exact_negotiation_and_payload_stays_bounded(self):
        cards, states = [], []
        for slot in range(16):
            entity = "timer.example_" + str(slot)
            cards.append(base.card(slot=slot, entity=entity, title="Ł" * 40, icon="clock"))
            states.append(base.State(entity, "paused"))
        hass, _ = base.environment(states=states, services=["timer.start"])
        original = deepcopy(cards)
        for supported in (False, 0, 1, "1", None):
            wire = base.cards.presentation_payload(hass, cards, press_enabled_supported=supported)
            self.assertTrue(all("press_enabled" not in c for c in wire["cards"]))
        wire = base.cards.presentation_payload(hass, cards, press_enabled_supported=True)
        self.assertLess(len(json.dumps(wire, ensure_ascii=False, separators=(",", ":")).encode()), 32768)
        self.assertTrue(all(type(c["press_enabled"]) is bool for c in wire["cards"]))
        self.assertTrue(all("action" not in c and "duration" not in c for c in wire["cards"]))
        self.assertEqual(cards, original)


class TimerDefaultDispatchTests(unittest.IsolatedAsyncioTestCase):
    def bridge(self, state="idle", version=1):
        bridge = InputButtonNegotiationTests.bridge(None, version, configured=0)
        hass, card = timer_environment(state)
        bridge.hass.states, bridge.hass.services = hass.states, hass.services
        bridge.tile_cards, bridge.tile_entity_ids = [card], [card["entity_id"]]
        return bridge

    async def retire(self, bridge):
        bridge._cancel_native_status_requery()
        await asyncio.gather(*bridge._background_tasks, return_exceptions=True)

    async def test_one_current_contextual_report_dispatches_one_exact_service(self):
        for state, operation in (("idle", "start"), ("active", "pause"), ("paused", "start")):
            bridge = self.bridge(state)
            bridge._native_context_required, bridge._context_press_version = True, 1
            bridge.sent_revision = bridge.saved_revision = 0
            context = types.SimpleNamespace(user_id="caller")
            await bridge.async_press_tile(2, card_id="card-2", revision=0, context=context)
            self.assertEqual(len(bridge.hass.services.calls), 1)
            args, kwargs = bridge.hass.services.calls[0]
            self.assertEqual(args, ("timer", operation, {"entity_id": "timer.example"}))
            self.assertIs(kwargs["context"], context)
            await self.retire(bridge)

    async def test_dispatch_rechecks_state_after_projection_without_replaying_old_action(self):
        bridge = self.bridge("idle")
        self.assertEqual(base.cards.presentation_payload(bridge.hass, bridge.tile_cards)["cards"][2]["subtitle"], "Start")
        bridge.hass.states.items["timer.example"] = base.State("timer.example", "active")
        bridge._native_context_required, bridge._context_press_version = True, 1
        bridge.sent_revision = bridge.saved_revision = 0
        await bridge.async_press_tile(2, card_id="card-2", revision=0, context=object())
        self.assertEqual(bridge.hass.services.calls[0][0], ("timer", "pause", {"entity_id": "timer.example"}))
        bridge.hass.states.items["timer.example"] = base.State("timer.example", "unavailable")
        await bridge.async_press_tile(2, card_id="card-2", revision=0, context=object())
        self.assertEqual(len(bridge.hass.services.calls), 1)
        await self.retire(bridge)

    async def test_wrong_identity_revision_or_removed_service_never_dispatches(self):
        for mode in ("identity", "revision", "disconnected", "service", "legacy"):
            bridge = self.bridge()
            bridge._native_context_required, bridge._context_press_version = True, 1
            bridge.sent_revision = bridge.saved_revision = 0
            data = {"card_id": "card-2", "revision": 0}
            if mode == "identity":
                data["card_id"] = "old-card"
            elif mode == "revision":
                data["revision"] = False
            elif mode == "disconnected":
                bridge.esphome_entry.runtime_data.available = False
            elif mode == "service":
                bridge.hass.services.names.clear()
            else:
                data = {}
            await bridge.async_press_tile(2, **data)
            self.assertEqual(bridge.hass.services.calls, [])
            await self.retire(bridge)

    async def test_timer_first_payload_negotiates_and_old_or_replaced_epoch_is_safe(self):
        for version, enabled in ((1, True), (0, False), (True, False), ("1", False)):
            bridge = self.bridge(version=version)
            self.assertTrue(await bridge.async_push_tiles())
            self.assertEqual(bridge.events[0][0], "status")
            wire = next(value for name, value in bridge.events if name == "set")
            if enabled:
                self.assertIs(wire["cards"][2]["press_enabled"], True)
            else:
                self.assertNotIn("press_enabled", wire["cards"][2])
            self.assertEqual(bridge.hass.services.calls, [])
            await self.retire(bridge)
        bridge = self.bridge()

        async def replace(*_args, **_kwargs):
            bridge._connection_epoch += 1
            bridge._press_enabled_version = 0
            bridge.esphome_entry.runtime_data = types.SimpleNamespace(available=False)
            return types.SimpleNamespace(success=True, response_data=json.dumps(status(1)).encode())

        bridge.esphome_entry.runtime_data.client.execute_service = replace
        self.assertFalse(await bridge.async_push_tiles())
        self.assertEqual(bridge.events, [])
        self.assertIsNone(bridge.sent_revision)
        await self.retire(bridge)


if __name__ == "__main__":
    unittest.main()
