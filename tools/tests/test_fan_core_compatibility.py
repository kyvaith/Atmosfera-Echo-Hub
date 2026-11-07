"""Core11 fan preset capability and explicit preset-to-manual control contracts.

No HA connection or device. The two fixture setters reproduce Core demo's
mutually exclusive percentage/preset observations instead of retaining both.
"""
import asyncio
from copy import deepcopy
from enum import IntFlag
import unittest

import test_fan_panel as panel
import test_fan_preset_control as presets
import test_ha_layout as base


class FanCoreCapabilityTests(unittest.TestCase):
    def setUp(self):
        fixture = panel.speed_fixture.core_math_fixture()
        fixture.start()
        self.addCleanup(fixture.stop)
        self.hass, self.state, _ = panel.environment()
        self.state.attributes["preset_mode"] = " Eco "

    def test_either_core_feature_reaches_panel_choice_and_live_service_gate(self):
        class Feature(IntFlag):
            SET_SPEED = 1
            PRESET_MODE = 8

        for mask in (1, 8, 9, 55, 56, 63, Feature.SET_SPEED, Feature.PRESET_MODE):
            with self.subTest(mask=mask):
                self.state.attributes["supported_features"] = mask
                domain = panel.fan.FanDomain.from_ha(self.hass, self.state)
                self.assertEqual(domain.presets, (" Eco ", "Żółty"))
                self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state),
                                 {"choice_control": {"options": [" Eco ", "Żółty"], "index": 0}})
                self.assertIn("fan.set_preset_mode", {r["service"] for r in base.cards.entity_actions(self.hass, self.state)})
                base.cards.validate_live_action(self.hass, self.state,
                    {"service": "fan.set_preset_mode", "data": {"preset_mode": "Żółty"}})
                self.assertEqual(domain.service_action("preset", 0),
                                 ("set_preset_mode", {"preset_mode": " Eco "}))

    def test_unrelated_bits_and_malformed_features_do_not_create_preset_controls(self):
        for mask in (0, 2, 4, 16, 32, 48):
            with self.subTest(mask=mask):
                self.state.attributes["supported_features"] = mask
                try:
                    domain = panel.fan.FanDomain.from_ha(self.hass, self.state)
                except panel.fan.FanDomainError:
                    pass
                else:
                    self.assertEqual(domain.presets, ())
                self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state), {})
                with self.assertRaises(base.layout.LayoutError):
                    base.cards.validate_live_action(self.hass, self.state,
                        {"service": "fan.set_preset_mode", "data": {"preset_mode": " Eco "}})
        for mask in (True, -1, "8", None):
            self.state.attributes["supported_features"] = mask
            with self.subTest(mask=mask), self.assertRaises(panel.fan.FanDomainError):
                panel.fan.FanDomain.from_ha(self.hass, self.state)
            self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state), {})

    def test_service_and_complete_bounded_catalogue_remain_required(self):
        self.state.attributes["supported_features"] = 55
        for options in (None, [], ["a", "a"], [str(i) for i in range(9)], ["ą" * 17], ["a\nb"]):
            with self.subTest(options=options):
                self.state.attributes["preset_modes"] = options
                domain = panel.fan.FanDomain.from_ha(self.hass, self.state)
                self.assertEqual(domain.presets, ())
                self.assertEqual(domain.speeds, (0, 33, 66, 100))
                self.assertTrue(domain.turn_on and domain.turn_off and domain.oscillate and domain.direction)
                self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state), {})
        self.state.attributes["preset_modes"] = [" Eco ", "Żółty"]
        self.hass.services.names.remove("fan.set_preset_mode")
        self.assertEqual(panel.fan.FanDomain.from_ha(self.hass, self.state).presets, ())
        self.assertEqual(base.cards._choice_control_metadata(self.hass, self.state), {})
        with self.assertRaises(base.layout.LayoutError):
            base.cards.validate_live_action(self.hass, self.state,
                {"service": "fan.set_preset_mode", "data": {"preset_mode": " Eco "}})

    def test_only_known_active_preset_bridges_unknown_percentage_to_absolute_speed(self):
        self.state.attributes.update(supported_features=55, percentage=None, preset_mode="Żółty")
        domain = panel.fan.FanDomain.from_ha(self.hass, self.state)
        observed = panel.fan.FanObservation.from_ha(self.state, domain)
        self.assertIsNone(observed.percentage)
        self.assertTrue(observed.can_command(domain, "speed"))
        for value in (None, "missing", "", True):
            self.state.attributes["preset_mode"] = value
            with self.subTest(preset=value):
                self.assertFalse(panel.fan.FanObservation.from_ha(self.state, domain).can_command(domain, "speed"))
        self.state.attributes.pop("preset_mode")
        self.assertFalse(panel.fan.FanObservation.from_ha(self.state, domain).can_command(domain, "speed"))
        self.state.attributes["preset_mode"] = "Żółty"
        for value in ("unknown", "unavailable"):
            self.state.state = value
            self.assertFalse(panel.fan.FanObservation.from_ha(self.state, domain).can_command(domain, "speed"))
        self.state.state = "on"
        for mask in (8, 56):
            self.state.attributes["supported_features"] = mask
            preset_only = panel.fan.FanDomain.from_ha(self.hass, self.state)
            observed = panel.fan.FanObservation.from_ha(self.state, preset_only)
            self.assertTrue(observed.can_command(preset_only, "preset"))
            self.assertFalse(observed.can_command(preset_only, "speed"))
        self.state.attributes["supported_features"] = 55
        self.hass.services.names.remove("fan.set_percentage")
        readonly_speed = panel.fan.FanDomain.from_ha(self.hass, self.state)
        self.assertFalse(panel.fan.FanObservation.from_ha(self.state, readonly_speed).can_command(readonly_speed, "speed"))

    def test_direction_and_climate_preset_bits_remain_separate(self):
        for mask in (1, 8, 9):
            with self.assertRaises(presets.choice.ChoiceDomainError):
                presets.choice.choice_domain("fan.test", {"supported_features": mask}, "direction")
            with self.assertRaises(presets.choice.ChoiceDomainError):
                presets.choice.choice_domain("climate.test", {"supported_features": mask, "preset_modes": ["Eco"]}, "preset_mode")
        self.assertEqual(presets.choice.choice_domain("fan.test", {"supported_features": 4}, "direction").options,
                         ("forward", "reverse"))


class FullFanCoreOwnerTests(panel.FanPanelOwnerTests):
    """Repeat shared fan fences for real Core full-fan mask55, plus transitions."""
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.state.attributes["supported_features"] = 55
        original_service = self.hass.services.async_call

        async def service(*args, **kwargs):
            operation, data = args[1:3]
            if operation not in ("set_percentage", "set_preset_mode"):
                return await original_service(*args, **kwargs)
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate:
                await self.service_gate.wait()
            if self.apply:
                changes = {"percentage": data["percentage"], "preset_mode": None} if operation == "set_percentage" else {
                    "preset_mode": data["preset_mode"], "percentage": None}
                self.change("on" if changes["preset_mode"] is not None or changes["percentage"] else "off", **changes)
        self.hass.services.async_call = service

    async def test_manual_preset_manual_sends_exactly_two_absolute_commands_with_observed_feedback(self):
        grant = await self.open()
        self.assertEqual((grant["percentage"], grant["preset_index"]), (33, None))
        self.assertEqual(grant["fan_caps"]["presets"], [" Eco ", "Żółty"])
        first = self.command(op="preset", target=1)
        await self.send(first)
        await self.send(first)
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertIsNone(self.state.attributes["percentage"])
        self.assertEqual(self.state.attributes["preset_mode"], "Żółty")
        self.assertIsNone(self.owner._selection.domain_state[1].percentage)
        second = self.command(2, "speed", 2)
        await self.send(second)
        await self.send(second)
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual(self.state.attributes["percentage"], 66)
        self.assertIsNone(self.state.attributes["preset_mode"])
        self.assertEqual([args for args, _ in self.hass.services.calls], [
            ("fan", "set_preset_mode", {"entity_id": "fan.test", "preset_mode": "Żółty"}),
            ("fan", "set_percentage", {"entity_id": "fan.test", "percentage": 66})])
        self.assertTrue(all(kwargs["context"] is self.user for _, kwargs in self.hass.services.calls))
        self.assert_terminal_order()

    async def test_preset_to_manual_without_feedback_is_not_success_and_does_not_guess_speed(self):
        self.state.attributes.update(percentage=None, preset_mode="Żółty")
        await self.open()
        self.apply = False
        await self.send(self.command(op="speed", target=1))
        self.assertEqual(len(self.hass.services.calls), 1)
        self.assertEqual(self.results()[-1]["status"], "not_confirmed")
        self.assertIsNone(self.state.attributes["percentage"])
        self.assertEqual(self.state.attributes["preset_mode"], "Żółty")

    async def test_active_preset_ABA_rejects_held_absolute_speed_after_authorization(self):
        self.state.attributes.update(percentage=None, preset_mode="Żółty")
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(panel.shared.wire(self.command(op="speed", target=2)), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("on", preset_mode=" Eco ")
        self.change("on", preset_mode="Żółty")
        self.auth_gate.set()
        await asyncio.wait_for(self.owner._selection.command.task, .4)
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["reason"], "stale_state")

    async def test_preset_to_manual_keeps_permission_and_live_service_fences(self):
        self.state.attributes.update(percentage=None, preset_mode="Żółty")
        await self.open()
        self.allowed = False
        await self.send(self.command(op="speed", target=1))
        self.assertEqual(self.results()[-1]["reason"], "unauthorized")
        self.assertEqual(self.hass.services.calls, [])
        self.allowed = True
        self.hass.services.names.remove("fan.set_percentage")
        with self.assertRaisesRegex(panel.codec.ProtocolError, "capabilities_changed"):
            await self.send(self.command(2, "speed", 1))
        self.assertEqual(self.hass.services.calls, [])
        self.assertIsNone(self.owner._selection)

    async def test_unknown_or_manual_without_percentage_never_sends_a_speed_command(self):
        await self.open()
        original = deepcopy(self.state.attributes)
        cases = [("on", {}), ("on", {"preset_mode": None}), ("on", {"preset_mode": "absent"}),
                 ("unknown", {"preset_mode": "Żółty"}), ("unavailable", {"preset_mode": "Żółty"})]
        for seq, (power, attributes) in enumerate(cases, 1):
            self.state.attributes = original | {"percentage": None}
            self.state.attributes.pop("preset_mode")
            self.change(power, **attributes)
            await self.send(self.command(seq, "speed", 2))
            self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assertEqual(self.hass.services.calls, [])
