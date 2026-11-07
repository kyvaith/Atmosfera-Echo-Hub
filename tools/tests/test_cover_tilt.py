"""Precise slat tilt uses actual current_tilt_position and one integer service."""

import asyncio
import importlib
import unittest
from copy import deepcopy
from types import SimpleNamespace as NS

import test_entity_control as shared
import test_ha_layout as base

number = importlib.import_module("_atmosfera_test.number_domain")
ACTION = number.COVER_TILT_ACTION


def cover():
    state = base.State("cover.test", "open", {"supported_features": 128, "current_tilt_position": 45,
        "current_position": 99})
    hass, _ = base.environment(states=[state], services=["cover.set_cover_tilt_position", "cover.stop_cover"])
    return hass, state


class CoverTiltModelTests(unittest.TestCase):
    def test_explicit_v3_cover_only_actual_feature_and_registered_service(self):
        doc = base.document([base.card(entity="cover.test", action=ACTION)]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_cover_tilt"])
        for entity, action, version in (("cover.test", ACTION, 2), ("number.test", ACTION, 3),
            ("cover.test", ACTION | {"data": {}}, 3), ("cover.test", ACTION | {"control": "cover"}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        hass, state = cover()
        self.assertEqual(base.cards._number_control_metadata(hass, state, "tilt_position")["cover_tilt"]["index"], 45)
        self.assertEqual(base.cards.entity_actions(hass, state), [{"service": "cover.set_cover_tilt_position", "fields": {
            "tilt_position": {"type": "number", "min": 0, "max": 100, "step": 1, "required": True}}}])

    def test_actual_tilt_including_endpoints_and_motion_is_not_primary_position_or_inferred_from_state(self):
        hass, state = cover();item = base.card(entity=state.entity_id, action=ACTION)
        for status in ("open", "closed", "opening", "closing"):
            state.state = status
            self.assertEqual(number.number_state(state, "tilt_position"), 45)
            for language, expected in (("pl", "Pochylenie 45 %"), ("en", "Tilt 45 %")):
                rendered = base.cards.presentation_payload(hass, [item], language=language, number_control_supported=True)["cards"][2]
                self.assertEqual(rendered["subtitle"], expected)
        domain = number.number_domain(hass, state, "tilt_position")
        for position in (0, 45, 100):
            state.attributes["current_tilt_position"] = position
            self.assertEqual(domain.observed_index(number.number_state(state, "tilt_position")), position)
        for position in (None, True, False, 45.5, -1, 101, "45"):
            state.attributes["current_tilt_position"] = position
            self.assertIsNone(domain.observed_index(number.number_state(state, "tilt_position")))
        state.attributes.pop("current_tilt_position")
        self.assertIsNone(number.number_state(state, "tilt_position"))

    def test_feature_service_and_unknown_state_fail_closed_and_static_fraction_is_rejected(self):
        for features in (0, 1, 2, 4, True, "4", -1):
            hass, state = cover();state.attributes["supported_features"] = features
            self.assertEqual(base.cards._number_control_metadata(hass, state, "tilt_position"), {})
        hass, state = cover();hass.services.names.clear()
        self.assertEqual(base.cards._number_control_metadata(hass, state, "tilt_position"), {})
        for status in ("unknown", "unavailable", "on", "bad"):
            state.state = status
            self.assertIsNone(number.number_state(state, "tilt_position"))
        for position in (True, 45.5, -1, 101):
            with self.subTest(position=position), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action({"kind": "service", "service": "cover.set_cover_tilt_position", "data": {"tilt_position": position}}, "cover.test", layout_version=3)


class CoverTiltOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.NumberOwnerTests();await self.f.asyncSetUp();f = self.f
        f.hass, f.state = cover();f.owner.hass = f.hass
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        def change(value, **attrs):
            f.state.attributes.update(current_tilt_position=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))
        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["tilt_position"])
        f.change = change;f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_one_integer_tilt_command_retains_primary_position_without_implicit_open_close_stop(self):
        f = self.f;grant = await f.open()
        self.assertEqual((grant["value_text"], grant["domain"]["unit"], grant["index"]), ("45", "%", 45))
        command = f.command();await f.send(command);await f.send(command)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("cover", "set_cover_tilt_position", {"entity_id": "cover.test", "tilt_position": 46}))
        self.assertIs(type(args[2]["tilt_position"]), int);self.assertIs(kwargs["context"], f.user)
        self.assertEqual(f.state.attributes["current_position"], 99)
        self.assertEqual(f.results()[-1]["status"], "state_matches")

    async def test_held_position_ABA_never_revives_an_old_step(self):
        f = self.f;await f.open();f.auth_gate = asyncio.Event();f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command()), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change(46);f.change(45);f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, []);self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_unknown_and_endpoints_disable_steps_and_feature_loss_revokes(self):
        f = self.f;f.state.attributes["current_tilt_position"] = None
        grant = await f.open();self.assertEqual((grant["available"], grant["index"], grant["value_text"]), (False, None, "--"))
        f.change(100);await f.owner.async_state_changed()
        await f.send(f.command())
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.change(45, supported_features=0)["reason"], "capabilities_changed")
