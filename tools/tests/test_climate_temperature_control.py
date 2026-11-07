"""One climate target uses exact provider units and the existing numeric lease."""

import asyncio
from copy import deepcopy
from enum import IntFlag, StrEnum
import importlib
from types import SimpleNamespace as NS
import unittest

import test_ha_layout as base
import test_entity_control as shared
from homeassistant.components.climate import DATA_COMPONENT

number = importlib.import_module("_atmosfera_test.number_domain")
ACTION = number.TEMPERATURE_ACTION


def climate(unit="°C"):
    attrs = {"supported_features": 1, "min_temp": 16, "max_temp": 30,
             "target_temp_step": .5, "temperature": 21.5, "current_temperature": 99}
    if unit == "°F":
        attrs.update(min_temp=50, max_temp=86, target_temp_step=1, temperature=70)
    state = base.State("climate.test", "off", attrs)
    hass, _ = base.environment(states=[state], services=["climate.set_temperature"])
    hass.config.units = NS(temperature_unit=unit)
    native = NS(temperature_unit=unit)
    hass.data = {DATA_COMPONENT: NS(get_entity=lambda entity: native if entity == state.entity_id else None)}
    return hass, state, native


class TemperatureModelTests(unittest.TestCase):
    def test_explicit_v3_climate_only_does_not_repurpose_other_numeric_controls(self):
        item = base.card(entity="climate.test", action=deepcopy(ACTION))
        doc = base.document([item]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(doc), doc)
        self.assertTrue(base.layout.device_profile()["schema_climate_temperature"])
        for entity, action, version in (("climate.test", ACTION, 2), ("number.test", ACTION, 3),
                                       ("climate.test", ACTION | {"property": "current_humidity"}, 3),
                                       ("climate.test", ACTION | {"data": {}}, 3)):
            with self.subTest(entity=entity, action=action), self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)
        self.assertEqual(number.number_service("number.test"), ("number", "set_value", "value"))

    def test_celsius_fahrenheit_target_metadata_and_caption_do_not_use_current_temperature(self):
        for unit, index, text in (("°C", 11, "Cel 21,5 °C"), ("°F", 20, "Cel 70 °F")):
            hass, state, _ = climate(unit)
            meta = base.cards._number_control_metadata(hass, state, "temperature")["climate_temperature"]
            self.assertEqual((meta["domain"]["unit"], meta["index"]), (unit, index))
            item = base.card(entity=state.entity_id, action=ACTION)
            self.assertEqual(base.cards.presentation_payload(hass, [item], language="pl-PL",
                             number_control_supported=True)["cards"][2]["subtitle"], text)

    def test_unknown_off_grid_modes_units_capabilities_and_missing_step_fail_closed(self):
        hass, state, native = climate()
        for value in (None, True, "unknown", 21.3, 99):
            state.attributes["temperature"] = value
            d = number.number_domain(hass, state, "temperature")
            self.assertIsNone(d.observed_index(number.number_state(state, "temperature")))
        state.attributes["temperature"] = 21.5
        for mode in ("auto", "heat_cool", "unknown", "unavailable", "bad"):
            state.state = mode
            self.assertIsNone(number.number_state(state, "temperature"))
        state.state = "off"
        for features in (0, 2, 3, True, -1, "1"):
            state.attributes["supported_features"] = features
            self.assertEqual(base.cards._number_control_metadata(hass, state, "temperature"), {})
        class Features(IntFlag):
            TARGET = 1
        state.attributes["supported_features"] = Features.TARGET
        self.assertTrue(base.cards._number_control_metadata(hass, state, "temperature"))
        native.temperature_unit = "°F"
        self.assertEqual(base.cards._number_control_metadata(hass, state, "temperature"), {})
        native.temperature_unit = "°C"
        del state.attributes["target_temp_step"]
        self.assertEqual(base.cards._number_control_metadata(hass, state, "temperature"), {})

    def test_missing_loaded_core_component_never_invents_a_native_unit(self):
        hass, state, _ = climate()
        self.assertTrue(base.cards._number_control_metadata(hass, state, "temperature"))
        del hass.data[DATA_COMPONENT]
        self.assertEqual(base.cards._number_control_metadata(hass, state, "temperature"), {})

    def test_core_temperature_enum_is_normalized_only_after_verified_unit_equality(self):
        class UnitOfTemperature(StrEnum):
            CELSIUS = "°C"
            FAHRENHEIT = "°F"
        for unit in UnitOfTemperature:
            hass, state, native = climate(str(unit))
            hass.config.units.temperature_unit = unit
            native.temperature_unit = unit
            domain = number.number_domain(hass, state, "temperature")
            self.assertIs(type(domain.unit), str)
            self.assertEqual(domain.unit, str(unit))
        native.temperature_unit = UnitOfTemperature.CELSIUS
        self.assertEqual(base.cards._number_control_metadata(hass, state, "temperature"), {})


class TemperatureOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.f = shared.NumberOwnerTests()
        await self.f.asyncSetUp()
        f = self.f
        f.hass, f.state, self.native = climate()
        # The existing owner retains its original context, fence and authorization.
        f.owner.hass = f.hass
        f.card.update(entity_id=f.state.entity_id, action=deepcopy(ACTION))

        def change(value, **attrs):
            f.state.attributes.update(temperature=value, **attrs)
            return f.owner.observe_state_event(NS(data={"entity_id": f.state.entity_id, "new_state": f.state}))

        async def service(*args, **kwargs):
            f.hass.services.calls.append((args, kwargs))
            if f.apply:
                change(args[2]["temperature"])

        f.change = change
        f.hass.services.async_call = service

    async def asyncTearDown(self):
        await self.f.asyncTearDown()

    async def test_exact_half_step_absolute_service_context_and_no_hvac_side_effect(self):
        f = self.f
        grant = await f.open()
        self.assertEqual((grant["value_text"], grant["domain"]["unit"], grant["index"]), ("21.5", "°C", 11))
        value = f.command()
        await f.send(value)
        await f.send(value)
        self.assertEqual(len(f.hass.services.calls), 1)
        args, kwargs = f.hass.services.calls[0]
        self.assertEqual(args, ("climate", "set_temperature", {"entity_id": "climate.test", "temperature": 22}))
        self.assertIs(kwargs["context"], f.user)
        self.assertEqual(f.state.state, "off")
        self.assertEqual(f.results()[-1]["status"], "state_matches")
        f.assert_terminal_order()

    async def test_negotiated_thermostat_keeps_measured_temperature_and_activity_read_only_without_step(self):
        f = self.f
        f.owner.accept_thermostat_features(f.owner.channel)
        del f.state.attributes["target_temp_step"]
        f.state.state = "heat"
        f.state.attributes.update(current_temperature=19.25, hvac_action="heating")
        item = f.card
        without = base.cards.presentation_payload(f.hass, [item], number_control_supported=True)["cards"][item["slot"]]
        with_view = base.cards.presentation_payload(
            f.hass, [item], number_control_supported=True, thermostat_supported=True
        )["cards"][item["slot"]]
        self.assertNotIn("control_kind", without)
        self.assertEqual(with_view["control_kind"], "number")
        grant = await f.open()
        self.assertEqual((grant["domain"], grant["index"], grant["available"]), (None, None, False))
        self.assertEqual(grant["thermostat"], {"unit": "°C", "target": "21.5", "current": "19.25",
                                             "min": "16", "max": "30", "level": 39, "activity": "heating"})
        with self.assertRaises(shared.codec.ProtocolError):
            shared.codec.encode(grant)
        self.assertEqual(shared.codec.decode(shared.codec.encode(grant, thermostat=True), thermostat=True), grant)
        f.state.attributes.update(current_temperature=21, hvac_action="idle")
        await f.owner.async_state_changed()
        self.assertEqual(f.hass.services.calls, [])

    async def test_temperature_ABA_while_authorizing_never_dispatches_a_stale_step(self):
        f = self.f
        await f.open()
        f.auth_gate = asyncio.Event()
        f.auth_entered.clear()
        await f.owner.async_handle(shared.codec.encode(f.command()), f.user)
        await asyncio.wait_for(f.auth_entered.wait(), .2)
        f.change(22)
        f.change(21.5)
        f.auth_gate.set()
        await asyncio.wait_for(f.owner._selection.command.task, .3)
        self.assertEqual(f.hass.services.calls, [])
        self.assertEqual(f.results()[-1]["reason"], "stale_state")

    async def test_dial_dispatches_one_absolute_target_and_rejects_out_of_range(self):
        f = self.f
        f.owner.accept_thermostat_features(f.owner.channel, dial=True)
        grant = await f.open()
        self.assertTrue(grant["thermostat"]["dial"])
        value = f.command()
        value.pop("direction")
        value.update(op="set_target", target_index=20)
        payload = shared.codec.encode(value, thermostat_dial=True)
        with self.assertRaises(shared.codec.ProtocolError):
            shared.codec.decode(payload)
        await f.owner.async_handle(payload, f.user)
        await f.owner._selection.command.task
        await f.owner.async_handle(payload, f.user)
        self.assertEqual(len(f.hass.services.calls), 1)
        self.assertEqual(f.hass.services.calls[0][0][2]["temperature"], 26)
        invalid = f.command(seq=2)
        invalid.pop("direction")
        invalid.update(op="set_target", target_index=29)
        await f.owner.async_handle(shared.codec.encode(invalid, thermostat_dial=True), f.user)
        self.assertEqual(len(f.hass.services.calls), 1)
        self.assertEqual(f.results()[-1]["status"], "rejected")

    async def test_step_ABA_and_unit_change_revoke_existing_selection(self):
        f = self.f
        await f.open()
        close = f.change(21.5, target_temp_step=.25)
        self.assertEqual(close["reason"], "capabilities_changed")
        f.change(21.5, target_temp_step=.5)
        self.assertIsNone(f.owner._selection)
        await f.open(seq=2)
        f.hass.config.units.temperature_unit = "°F"
        await f.owner.async_state_changed()
        self.assertIsNone(f.owner._selection)
        self.assertEqual(f.hass.services.calls, [])

    async def test_unknown_target_disables_both_steps_and_service_loss_blocks_dispatch(self):
        f = self.f
        f.state.attributes["temperature"] = None
        grant = await f.open()
        self.assertEqual((grant["index"], grant["available"], grant["value_text"]), (None, False, "--"))
        f.change(21.5)
        await f.owner.async_state_changed()
        command = f.command()
        f.hass.services.names.clear()
        with self.assertRaises(shared.codec.ProtocolError):
            await f.send(command)
        self.assertEqual(f.hass.services.calls, [])
