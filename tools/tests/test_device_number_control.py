"""Device Number policy uses the same exact lattice and session as helpers."""

from copy import deepcopy
import unittest

import test_entity_control as shared
import test_ha_layout as base


class DeviceNumberOwnerTests(unittest.IsolatedAsyncioTestCase):
    bind = shared.NumberOwnerTests.bind
    open = shared.NumberOwnerTests.open
    command = shared.NumberOwnerTests.command
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    assert_terminal_order = shared.NumberOwnerTests.assert_terminal_order
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.hass.states.items.pop(self.state.entity_id)
        self.state.entity_id = "number.provider"
        self.hass.states.items[self.state.entity_id] = self.state
        self.card["entity_id"] = self.state.entity_id
        self.hass.services.names.add("number.set_value")
        service = self.hass.services.async_call

        async def apply(*args, **kwargs):
            await service(*args, **kwargs)
            if self.apply and args[0] == "number":
                self.change(str(args[2]["value"]))

        self.hass.services.async_call = apply

    async def test_exact_step_dispatches_only_number_service_with_original_context(self):
        grant = await self.open()
        self.assertEqual((grant["index"], grant["value_text"]), (4, "0"))
        await self.send(self.command())
        args, kwargs = self.hass.services.calls[0]
        self.assertEqual(args, ("number", "set_value", {"entity_id": "number.provider", "value": .25}))
        self.assertIs(kwargs["context"], self.user)
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assert_terminal_order()

    async def test_helper_service_cannot_substitute_for_missing_provider_service(self):
        self.hass.services.names.remove("number.set_value")
        with self.assertRaises(shared.codec.ProtocolError):
            await self.open()
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(base.cards._number_control_metadata(self.hass, self.state), {})

    async def test_provider_service_removed_during_session_never_dispatches_to_helper(self):
        await self.open()
        value = self.command()
        self.hass.services.names.remove("number.set_value")
        with self.assertRaises(shared.codec.ProtocolError):
            await self.send(value)
        self.assertEqual(self.hass.services.calls, [])

    test_value_ABA_during_authorization = shared.NumberOwnerTests.test_authorization_pending_value_ABA_rejects_captured_generation
    test_metadata_ABA_retires_selection = shared.NumberOwnerTests.test_metadata_ABA_revokes_immediately_even_before_refresh_task
    test_unknown_endpoints_duplicate = shared.NumberOwnerTests.test_stale_unknown_endpoint_and_duplicate_never_extra_dispatch


class DeviceNumberModelTests(unittest.TestCase):
    def test_roundtrip_is_explicit_and_other_domains_cannot_be_substituted(self):
        card = base.card(entity="number.provider", action={"kind": "control", "control": "number"})
        document = base.document([card]) | {"version": 3}
        self.assertEqual(base.layout.validate_layout(document)["cards"][0], card)
        self.assertEqual(base.layout.import_layout(base.layout.export_layout(document), 9)["cards"][0], card)
        for entity in ("sensor.provider", "select.provider", "input_number_bad.provider"):
            bad = deepcopy(document)
            bad["cards"][0]["entity_id"] = entity
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(bad)

    def test_catalogue_has_exact_metadata_only_for_the_correct_registered_service(self):
        state = base.State("number.provider", "0.5", {"min": "-1", "max": "1", "step": "0.25", "unit_of_measurement": "W"})
        hass, _ = base.environment(states=[state], services=["number.set_value"])
        value = base.cards._number_control_metadata(hass, state)["number_control"]
        self.assertEqual(value["index"], 6)
        self.assertEqual(value["domain"]["step"], "0.25")
        self.assertIsNone(base.cards.resolve_action(hass, base.card(entity=state.entity_id)))
        state.attributes["step"] = "0.0000001"
        self.assertEqual(base.cards._number_control_metadata(hass, state), {})
