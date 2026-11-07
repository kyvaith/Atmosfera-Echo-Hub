"""HVAC labels, canonical mode codes and the existing single choice lease."""

import asyncio
from copy import deepcopy
from enum import StrEnum
import importlib
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import test_ha_layout as base
import test_choice_control as shared

choice = importlib.import_module("_atmosfera_test.choice_domain")
ACTION = {"kind": "control", "control": "choice", "property": "hvac_mode"}
OPTIONS = ["off", "heat", "cool", "auto"]


class HVACModelTests(unittest.TestCase):
    def test_explicit_climate_schema_and_known_core_enum_catalogue(self):
        class HVACMode(StrEnum):
            OFF = "off"
            HEAT = "heat"
        state = base.State("climate.test", "off", {"hvac_modes": [HVACMode.OFF, HVACMode.HEAT]})
        hass, _ = base.environment(states=[state], services=["climate.set_hvac_mode"])
        meta = base.cards._choice_control_metadata(hass, state, "hvac_mode")
        self.assertEqual(meta, {"climate_hvac_mode": {"options": ["off", "heat"], "index": 0}})
        self.assertTrue(all(type(value) is str for value in meta["climate_hvac_mode"]["options"]))
        doc = base.document([base.card(entity=state.entity_id, action=ACTION)]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_climate_hvac_mode"])
        for entity, action, version in (("climate.test", ACTION, 2), ("fan.test", ACTION, 3),
                                       ("climate.test", ACTION | {"property": "preset"}, 3),
                                       ("climate.test", ACTION | {"service": "climate.set_hvac_mode"}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        for values in ([], ["off", "off"], ["off", "away"], ["off", True], tuple(OPTIONS)):
            state.attributes["hvac_modes"] = values
            self.assertEqual(base.cards._choice_control_metadata(hass, state, "hvac_mode"), {})

    def test_ha_labels_win_but_invalid_or_duplicate_translations_use_bounded_language_pack(self):
        state = base.State("climate.test", "heat", {"hvac_modes": OPTIONS})
        hass, _ = base.environment(states=[state], services=["climate.set_hvac_mode"])
        domain = choice.choice_domain(state.entity_id, state.attributes, "hvac_mode")
        translated = {f"component.climate.entity_component._.state.{value}": "HA " + value for value in OPTIONS}
        with patch.object(base.cards, "async_get_cached_translations", return_value=translated):
            self.assertEqual(base.cards.choice_control_labels(hass, state, domain, "hvac_mode", "pl"), tuple("HA " + value for value in OPTIONS))
            item = base.card(entity=state.entity_id, action=ACTION)
            self.assertEqual(base.cards.presentation_payload(hass, [item], language="pl", choice_control_supported=True)["cards"][2]["subtitle"], "HA heat")
        for bad in ("x" * 33, "\n", "same"):
            values = {key: bad for key in translated}
            with patch.object(base.cards, "async_get_cached_translations", return_value=values):
                self.assertEqual(base.cards.choice_control_labels(hass, state, domain, "hvac_mode", "pl"),
                                 ("Wyłączone", "Ogrzewanie", "Chłodzenie", "Automatyczny"))


class HVACOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.ChoiceOwnerTests()
        await self.f.asyncSetUp()
        f = self.f
        f.state = base.State("climate.test", "off", {"hvac_modes": OPTIONS.copy(), "temperature": 21.5, "supported_features": 0})
        f.hass.states.items = {f.state.entity_id: f.state}
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))
        f.hass.services.names = {"climate.set_hvac_mode"}
        self.language = "pl"
        f.owner._choice_language = lambda: self.language

        def change(value, **attrs):
            f.state.state = value
            f.state.attributes.update(attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))

        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["hvac_mode"])

        f.change = change
        f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_localized_choice_dispatches_canonical_mode_once_with_context_and_no_temperature(self):
        f = self.f
        grant = await f.open()
        self.assertEqual(grant["options"], ["Wyłączone", "Ogrzewanie", "Chłodzenie", "Automatyczny"])
        value = f.command(1)
        await f.send(value)
        await f.send(value)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("climate", "set_hvac_mode", {"entity_id": "climate.test", "hvac_mode": "heat"}))
        self.assertIs(kwargs["context"], f.user)
        self.assertEqual(f.state.attributes["temperature"], 21.5)
        self.assertEqual(f.results()[-1]["status"], "state_matches")
        f.assert_terminal_order()

    async def test_mode_ABA_during_authorization_cannot_revive_apply(self):
        f = self.f
        await f.open()
        f.auth_gate = asyncio.Event()
        f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command(2)), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change("heat")
        f.change("off")
        f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_catalogue_reorder_and_locale_change_revoke_selection(self):
        f = self.f
        await f.open()
        close = f.change("off", hvac_modes=["off", "cool", "heat", "auto"])
        self.assertEqual(close["reason"], "capabilities_changed")
        await f.open(seq=2)
        self.language = "en"
        await f.owner.async_state_changed()
        self.assertIsNone(f.owner._selection)
        grant = await f.open(seq=3)
        self.assertEqual(grant["options"], ["Off", "Cooling", "Heating", "Automatic"])
        self.assertEqual(f.hass.services.calls, [])

    async def test_outage_and_missing_mode_service_never_send_commands(self):
        f = self.f
        await f.open()
        old = f.command()
        f.change("unavailable")
        await f.send(old)
        self.assertEqual(f.hass.services.calls, [])
        f.change("off")
        await f.owner.async_close()
        await f.open(seq=2)
        old = f.command()
        f.hass.services.names.clear()
        with self.assertRaises(shared.codec.ProtocolError):
            await f.send(old)
        self.assertEqual(f.hass.services.calls, [])
