"""Fan presets reuse the bounded choice lease; fan power is never an index."""

import asyncio
from enum import IntFlag
import importlib
from types import SimpleNamespace as NS
import unittest

import test_ha_layout as base
import test_choice_control as shared

choice = importlib.import_module("_atmosfera_test.choice_domain")


class FanPresetModelTests(unittest.TestCase):
    def test_capability_service_and_exact_preset_metadata(self):
        class Features(IntFlag):
            PRESET_MODE = 8

        state = base.State("fan.test", "on", {"supported_features": Features.PRESET_MODE,
                           "preset_modes": [" Eco ", "Żółty"], "preset_mode": " Eco "})
        hass, _ = base.environment(states=[state], services=["fan.set_preset_mode"])
        self.assertEqual(base.cards._choice_control_metadata(hass, state),
                         {"choice_control": {"options": [" Eco ", "Żółty"], "index": 0}})
        for value in (0, 32, True, -1, "8", None):
            state.attributes["supported_features"] = value
            self.assertEqual(base.cards._choice_control_metadata(hass, state), {})
        state.attributes["supported_features"] = 8
        for value in ([], ["Eco", "Eco"], ["ą" * 17], list(map(str, range(9)))):
            state.attributes["preset_modes"] = value
            self.assertEqual(base.cards._choice_control_metadata(hass, state), {})
        state.attributes["preset_modes"] = ["Eco"]
        hass.services.names.clear()
        self.assertEqual(base.cards._choice_control_metadata(hass, state), {})

    def test_unknown_power_or_preset_is_never_option_zero(self):
        attrs = {"supported_features": 8, "preset_modes": ["Eco", "Boost"], "preset_mode": "Eco"}
        for power in ("unknown", "unavailable", "missing", None):
            self.assertIsNone(choice.choice_state("fan.test", power, attrs))
        for power in ("on", "off"):
            self.assertEqual(choice.choice_state("fan.test", power, attrs), "Eco")
        attrs["preset_mode"] = None
        self.assertIsNone(choice.choice_domain("fan.test", attrs).observed_index(
            choice.choice_state("fan.test", "on", attrs)))

    def test_explicit_control_layout_and_preset_caption_leave_default_toggle_intact(self):
        item = base.card(entity="fan.test", action={"kind": "control", "control": "choice"})
        doc = base.document([item]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        with self.assertRaises(base.layout.LayoutError):
            base.layout.validate_layout(doc | {"version": 2})
        state = base.State("fan.test", "on", {"supported_features": 8 | 16 | 32,
                           "preset_modes": ["Eco", "Boost"], "preset_mode": "Boost"})
        hass, _ = base.environment(states=[state], services=["fan.set_preset_mode", "fan.toggle"])
        self.assertEqual(base.cards.presentation_payload(hass, [item], choice_control_supported=True)["cards"][2]["subtitle"], "Boost")
        self.assertIsNone(base.cards.resolve_action(hass, item))
        self.assertEqual(base.cards.resolve_action(hass, base.card(entity="fan.test")).service, "toggle")
        state.attributes["preset_mode"] = "absent"
        self.assertEqual(base.cards.presentation_payload(hass, [item], language="pl", choice_control_supported=True)["cards"][2]["subtitle"], "Nieznany")


class FanPresetOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.ChoiceOwnerTests()
        await self.f.asyncSetUp()
        f = self.f
        f.state = base.State("fan.test", "on", {"supported_features": 8,
                            "preset_modes": ["Eco", "Komfort", " Żółty "], "preset_mode": "Eco"})
        f.hass.states.items = {f.state.entity_id: f.state}
        f.card["entity_id"] = f.state.entity_id
        f.hass.services.names = {"fan.set_preset_mode"}

        def change(value, **attrs):
            f.state.attributes.update(preset_mode=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))

        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            f.service_entered.set()
            if f.service_gate:
                await f.service_gate.wait()
            if f.apply:
                change(args[2]["preset_mode"])

        f.change = change
        f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_apply_exact_preset_and_dedupe_preserve_the_shared_context(self):
        f = self.f
        await f.open()
        self.assertEqual(f.owner._selection.domain_state[1], 0)
        command = f.command(2)
        await f.send(command)
        await f.send(command)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args[:3], ("fan", "set_preset_mode", {"entity_id": "fan.test", "preset_mode": " Żółty "}))
        self.assertEqual(kwargs["context"], f.user)
        self.assertEqual(f.results()[-1]["status"], "state_matches")
        f.assert_terminal_order()

    async def test_preset_ABA_while_authorizing_rejects_stale_apply(self):
        f = self.f
        await f.open()
        f.auth_gate = asyncio.Event()
        f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command()), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change("Komfort")
        f.change("Eco")
        f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_list_change_or_lost_preset_feature_revokes_the_token(self):
        f = self.f
        await f.open()
        old = f.command()
        close = f.change("Eco", preset_modes=["Eco", "Other"])
        self.assertEqual(close["reason"], "capabilities_changed")
        self.assertIsNone(f.owner._selection)
        with self.assertRaises(shared.codec.ProtocolError):
            await f.send(old)
        await f.open(seq=2)
        close = f.change("Eco", supported_features=0)
        self.assertEqual(close["reason"], "capabilities_changed")
        self.assertEqual(f.hass.services.calls, [])

    async def test_service_acceptance_without_preset_feedback_is_not_success(self):
        f = self.f
        await f.open()
        f.apply = False
        await f.send(f.command())
        self.assertEqual(len(f.hass.services.calls), 1)
        self.assertNotEqual(f.results()[-1]["status"], "state_matches")
        self.assertEqual(f.state.state, "on")
        self.assertEqual(f.state.attributes["preset_mode"], "Eco")

    async def test_unavailable_power_hides_retained_preset_and_blocks_apply(self):
        f = self.f
        await f.open()
        old = f.command()
        f.state.state = "unavailable"
        f.change("Eco")
        self.assertIsNone(f.owner._selection.domain_state[1])
        await f.send(old)
        self.assertEqual(f.hass.services.calls, [])

