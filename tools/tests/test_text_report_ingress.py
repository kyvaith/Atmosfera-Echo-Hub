"""Exercise the actual registered report schema, router and negotiated Text owner."""
from __future__ import annotations

import ast
import asyncio
import logging
from types import SimpleNamespace as NS
import unittest

import voluptuous as vol

import test_text_panels as text


def report_registration(hass):
    """Compile the real nested validator/handler/registration, not a copied schema."""
    source = text.base.COMPONENT / "__init__.py"
    tree = ast.parse(source.read_text(encoding="utf8"))
    setup = next(node for node in tree.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_setup")
    nodes = [node for node in setup.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
             and node.name in {"entity_payload", "async_report_entity_control"}]
    register = [node for node in setup.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and len(node.value.args) >= 2 and isinstance(node.value.args[1], ast.Name)
                and node.value.args[1].id == "SERVICE_REPORT_ENTITY_CONTROL"]
    assert len(nodes) == 2 and len(register) == 1
    transport = text.base.COMPONENT / "light_control_transport.py"
    route = next(node for node in ast.parse(transport.read_text(encoding="utf8")).body
                 if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_route_entity_report")
    registered = {}
    hass.services.async_register = lambda domain, name, handler, *, schema: registered.update(
        domain=domain, name=name, handler=handler, schema=schema)
    def string(value):
        if not isinstance(value, str):
            raise vol.Invalid("Expected string")
        return value
    namespace = dict(hass=hass, vol=vol, cv=NS(string=string),
        DOMAIN="atmosfera_echo_hub", SERVICE_REPORT_ENTITY_CONTROL="report_entity_control",
        ATTR_NODE_NAME="node_name", ATTR_PAYLOAD="payload", ServiceCall=object,
        ProtocolError=text.codec.ProtocolError, decode_entity_control=text.codec.decode_report,
        entity_control_codec=text.codec, _LOGGER=logging.getLogger(__name__))
    module = ast.Module(body=[route, *nodes, *register], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(source), "exec"), namespace)
    return registered


class TextReportIngressTests(unittest.IsolatedAsyncioTestCase):
    asyncSetUp = text.TextOwnerTests.asyncSetUp
    asyncTearDown = text.TextOwnerTests.asyncTearDown
    configure = text.TextOwnerTests.configure
    bind = text.TextOwnerTests.bind
    change = text.TextOwnerTests.change
    open = text.TextOwnerTests.open
    command = text.TextOwnerTests.command
    results = text.TextOwnerTests.results

    def registered(self):
        self.routed = []
        async def report(payload, context):
            self.routed.append((payload, context))
            return await self.owner.async_handle(payload, context)
        bridge = NS(node_name="test-node", _light_control=NS(owner=self.owner, async_report_generic=report))
        self.hass.config_entries = NS(async_loaded_entries=lambda _domain: [NS(runtime_data=bridge)])
        return report_registration(self.hass)

    async def dispatch(self, registered, payload):
        validated = registered["schema"]({"node_name": "test-node", "payload": payload})
        await registered["handler"](NS(data=validated, context=self.user))
        selection = self.owner._selection
        if selection and selection.command and selection.command.task:
            await asyncio.wait_for(selection.command.task, .4)

    async def test_actual_schema_router_owner_preserves_unicode_empty_context_and_one_command(self):
        await self.open()
        registered = self.registered()
        for sequence, value in enumerate(("Zażółć \"test\"", "", "Ż" * 255), 1):
            payload = text.shared.wire(self.command(sequence, value))
            self.assertEqual(text.codec.decode_report(payload)["value"], value)
            await self.dispatch(registered, payload)
            self.assertEqual(len(self.hass.services.calls), sequence)
            args, kwargs = self.hass.services.calls[-1]
            self.assertEqual(args, ("input_text", "set_value", {"entity_id": self.state.entity_id, "value": value}))
            self.assertIs(kwargs["context"], self.user)
            self.assertEqual(self.results()[-1]["status"], "state_matches")
            self.assertIs(self.routed[-1][1], self.user)
            await self.dispatch(registered, payload)
            self.assertEqual(len(self.hass.services.calls), sequence)

    async def test_structural_ingress_does_not_enable_unnegotiated_text_owner(self):
        await self.open()
        registered = self.registered()
        payload = text.shared.wire(self.command())
        self.assertEqual(registered["schema"]({"node_name": "test-node", "payload": payload})["payload"], payload)
        with self.assertRaises(text.codec.ProtocolError):
            text.codec.decode(payload)
        self.owner._extra_profiles = ()
        await self.dispatch(registered, payload)
        self.assertEqual(len(self.routed), 1)
        self.assertEqual(self.hass.services.calls, [])
        self.assertIsNone(self.owner._selection.command)

    async def test_real_service_schema_rejects_malformed_and_reverse_direction_before_route(self):
        await self.open()
        registered = self.registered()
        command = self.command()
        raw = text.shared.wire(command)
        cases = [raw.replace('"value":', '"value":"duplicate","value":'),
                 text.shared.wire(command | {"extra": True}),
                 text.shared.wire(command | {"value": "x" * 256}),
                 text.shared.wire(command | {"value": None}),
                 text.shared.wire(text.TextCodecTests().snapshot()),
                 "x" * 2049, command]
        for payload in cases:
            with self.subTest(payload_type=type(payload).__name__):
                with self.assertRaises(vol.Invalid):
                    await self.dispatch(registered, payload)
        self.assertEqual(self.routed, [])
        self.assertEqual(self.hass.services.calls, [])


if __name__ == "__main__":
    unittest.main()
