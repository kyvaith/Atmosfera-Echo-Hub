"""Exercise the actual integration's registered service schema, without HA I/O."""

import importlib.util
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

import voluptuous as vol

import test_detail_control as detail
import test_entity_control as shared
import test_ha_layout as base


def load_integration():
    """Only unrelated HA setup adapters are fake; execute the real __init__.py."""
    validation = types.ModuleType("homeassistant.helpers.config_validation")
    validation.string = vol.All(str)
    validation.entity_id = vol.All(str)
    validation.ensure_list = lambda value: value if isinstance(value, list) else [value]
    typing = types.ModuleType("homeassistant.helpers.typing")
    typing.ConfigType = dict
    camera = types.ModuleType("_atmosfera_test.camera_proxy")
    camera.AtmosferaCameraStreamView = lambda hass: object()
    spec = importlib.util.spec_from_file_location(
        "_atmosfera_test._registered_integration", base.COMPONENT / "__init__.py")
    spec.submodule_search_locations = None
    integration = importlib.util.module_from_spec(spec)
    # A package initializer normally makes relative imports point into its own
    # namespace. Use the same component package as the existing offline tests.
    integration.__package__ = "_atmosfera_test"
    with patch.dict(sys.modules, {
        validation.__name__: validation, typing.__name__: typing,
        camera.__name__: camera,
    }), patch.object(sys.modules["homeassistant.core"], "ServiceCall", object, create=True), \
            patch.object(sys.modules["homeassistant.core"], "SupportsResponse",
                         types.SimpleNamespace(OPTIONAL="optional"), create=True):
        spec.loader.exec_module(integration)
    return integration


class RegisteredEntityReportTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.integration = load_integration()
        registered = {}

        def register(domain, name, handler, **options):
            self.assertEqual(domain, "atmosfera_echo_hub")
            self.assertNotIn(name, registered)
            registered[name] = (handler, options["schema"])

        hass = types.SimpleNamespace(
            http=types.SimpleNamespace(register_view=lambda _view: None),
            services=types.SimpleNamespace(async_register=register))
        with patch.object(self.integration, "async_setup_panel", new=AsyncMock()):
            self.assertTrue(await self.integration.async_setup(hass, {}))
        self.hass = hass
        self.handler, self.schema = registered["report_entity_control"]

    def report(self, value):
        return {"node_name": "offline-test-node", "payload": shared.wire(value)}

    async def test_facet_reaches_registered_handler_and_router_without_becoming_a_command(self):
        value = shared.codec.envelope("facet", **(shared.CodecTests().identity() | {"control_kind": "light"}),
                                      facet="color_temp_kelvin", view_seq=1)
        data = self.report(value)
        self.assertEqual(shared.codec.decode_report(data["payload"]), value)
        self.assertEqual(self.schema(data), data)
        context = object()
        route = AsyncMock()
        with patch.object(self.integration, "async_route_entity_report", route):
            await self.handler(types.SimpleNamespace(data=self.schema(data), context=context))
        route.assert_awaited_once_with(self.hass, data["node_name"], data["payload"], context)

    async def test_old_outbound_kinds_still_pass_actual_registered_schema(self):
        codec = shared.codec
        identity = shared.CodecTests().identity()
        opening = {key: value for key, value in identity.items() if key != "token"}
        messages = [codec.envelope("open", **opening),
                    codec.envelope("cancel_open", **opening, reason="user"),
                    codec.envelope("close", **identity, reason="navigation"),
                    codec.envelope("command", **identity, command_seq=1, op="step", direction=1,
                                   expected_index=4, expected_state_generation=1)]
        for value in messages:
            with self.subTest(kind=value["kind"]):
                data = self.report(value)
                self.assertEqual(self.schema(data), data)

    async def test_valid_inbound_messages_rejected_at_registered_schema(self):
        codec = shared.codec
        identity = shared.CodecTests().identity() | {"control_kind": "light"}
        state = detail.DetailCodecTests().snapshot("light")
        messages = [state, state | {"kind": "grant"},
                    codec.envelope("result", **identity, command_seq=1, state_seq=1,
                                   status="rejected", reason="stale_state"),
                    codec.envelope("facet_result", **identity, view_seq=1,
                                   facet="color_temp_kelvin", state_seq=1, status="ready", reason="none")]
        for value in messages:
            with self.subTest(kind=value["kind"]):
                # Prove the message is otherwise valid, not rejected as malformed.
                self.assertEqual(codec.decode(codec.encode(value, light_detail=True), light_detail=True), value)
                with self.assertRaises(vol.Invalid):
                    self.schema(self.report(value))

    async def test_malformed_or_oversize_reports_still_rejected(self):
        for raw in ({}, " " * 2049, '{"v":1,"v":1}', '{"v":NaN}', "{}"):
            with self.subTest(raw=repr(raw)[:40]), self.assertRaises(vol.Invalid):
                self.schema({"node_name": "offline-test-node", "payload": raw})


class RegisteredIngressOwnerNegotiationTests(unittest.IsolatedAsyncioTestCase):
    async def test_structural_facet_admission_does_not_grant_detail_negotiation(self):
        case = detail.DetailOwnerTests()
        await case.asyncSetUp()
        try:
            case.configure("light")
            case.owner._detail_light = case.owner._detail_climate = False
            with self.assertRaises(shared.codec.ProtocolError):
                await case.open()
            self.assertIsNone(case.owner._selection)
            value = shared.codec.envelope("facet", **(shared.CodecTests().identity() | {
                "channel": case.owner.channel, "control_kind": "light"}),
                facet="color_temp_kelvin", view_seq=1)
            self.assertEqual(shared.codec.decode_report(shared.wire(value)), value)
            with self.assertRaises(shared.codec.ProtocolError):
                await case.owner.async_handle(shared.wire(value), case.user)
            self.assertEqual(case.hass.services.calls, [])
        finally:
            await case.asyncTearDown()
