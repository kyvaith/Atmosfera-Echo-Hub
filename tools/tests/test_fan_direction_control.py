"""Direction labels never become service values or fan power commands."""

import asyncio
from copy import deepcopy
import importlib
from types import SimpleNamespace as NS
import unittest

import test_ha_layout as base
import test_choice_control as shared

choice = importlib.import_module("_atmosfera_test.choice_domain")
ACTION = {"kind": "control", "control": "choice", "property": "direction"}


class FanDirectionModelTests(unittest.TestCase):
    def test_schema_is_explicit_and_does_not_repurpose_presets(self):
        item = base.card(entity="fan.test", action=ACTION)
        doc = base.document([item]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_fan_direction"])
        for entity, action, version in (("fan.test", ACTION, 2), ("select.test", ACTION, 3),
                                       ("fan.test", ACTION | {"property": "preset"}, 3),
                                       ("fan.test", ACTION | {"data": {}}, 3),
                                       ("fan.test", {"kind": "default", "property": "direction"}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        self.assertEqual(choice.choice_service("fan.test"), ("set_preset_mode", "preset_mode"))

    def test_live_metadata_strict_capabilities_caption_and_no_manual_inference(self):
        state = base.State("fan.test", "off", {"supported_features": 4, "direction": "reverse", "preset_mode": None})
        hass, _ = base.environment(states=[state], services=["fan.set_direction"])
        self.assertEqual(base.cards._choice_control_metadata(hass, state, "direction"),
                         {"fan_direction": {"options": ["forward", "reverse"], "index": 1}})
        item = base.card(entity=state.entity_id, action=ACTION)
        for language, caption in (("pl-PL", "Wstecz"), ("en", "Reverse")):
            self.assertEqual(base.cards.presentation_payload(hass, [item], language=language,
                             choice_control_supported=True)["cards"][2]["subtitle"], caption)
        for value in (None, True, 0, "FORWARD", "missing"):
            state.attributes["direction"] = value
            self.assertIsNone(choice.choice_domain(state.entity_id, state.attributes, "direction").observed_index(
                choice.choice_state(state.entity_id, state.state, state.attributes, "direction")))
            self.assertFalse(choice.choice_is_empty(state.entity_id, state.state, state.attributes, "direction"))
        for value in (0, 8, True, -1, "4"):
            state.attributes["supported_features"] = value
            self.assertEqual(base.cards._choice_control_metadata(hass, state, "direction"), {})
        state.attributes.update(supported_features=4, direction="forward")
        hass.services.names.clear()
        self.assertEqual(base.cards._choice_control_metadata(hass, state, "direction"), {})


class FanDirectionOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.ChoiceOwnerTests()
        await self.f.asyncSetUp()
        f = self.f
        f.state = base.State("fan.test", "off", {"supported_features": 4, "direction": "forward"})
        f.hass.states.items = {f.state.entity_id: f.state}
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        f.hass.services.names = {"fan.set_direction"}
        self.language = "pl-PL"
        f.owner._choice_language = lambda: self.language

        def change(value, **attrs):
            f.state.attributes.update(direction=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))

        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            f.service_entered.set()
            if f.apply:
                change(args[2]["direction"])

        f.change = change
        f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_localized_grant_canonical_dispatch_dedupe_and_context(self):
        f = self.f
        grant = await f.open()
        self.assertEqual(grant["options"], ["Do przodu", "Wstecz"])
        command = f.command(1)
        await f.send(command)
        await f.send(command)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args[:3], ("fan", "set_direction", {"entity_id": "fan.test", "direction": "reverse"}))
        self.assertEqual(kwargs["context"], f.user)
        self.assertEqual(f.results()[-1]["status"], "state_matches")
        self.assertEqual(f.state.state, "off")
        f.assert_terminal_order()

    async def test_direction_ABA_during_authorization_cannot_revive_apply(self):
        f = self.f
        await f.open()
        f.auth_gate = asyncio.Event()
        f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command()), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change("reverse")
        f.change("forward")
        f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_language_change_revokes_selection_and_next_grant_is_english(self):
        f = self.f
        await f.open()
        self.language = "en-US"
        await f.owner.async_state_changed()
        self.assertIsNone(f.owner._selection)
        grant = await f.open(seq=2)
        self.assertEqual(grant["options"], ["Forward", "Reverse"])
        self.assertEqual(f.hass.services.calls, [])

    async def test_capability_loss_unavailable_and_service_loss_block_commands(self):
        f = self.f
        await f.open()
        close = f.change("forward", supported_features=8)
        self.assertEqual(close["reason"], "capabilities_changed")
        f.state.attributes["supported_features"] = 4
        await f.open(seq=2)
        command = f.command()
        f.state.state = "unavailable"
        f.change("forward")
        await f.send(command)
        self.assertEqual(f.hass.services.calls, [])
        f.state.state = "off"
        await f.owner.async_close()
        await f.open(seq=3)
        command = f.command()
        f.hass.services.names.clear()
        with self.assertRaises(shared.codec.ProtocolError):
            await f.send(command)
        self.assertEqual(f.hass.services.calls, [])
