"""Offline v3/transport/public-policy adapter tests. Every HA/ESPHome call is fake."""

from __future__ import annotations

import asyncio
from copy import deepcopy
import importlib
import json
import sys
import types
import unittest

import test_ha_layout as base

transport = importlib.import_module("_atmosfera_test.light_control_transport")
light = importlib.import_module("_atmosfera_test.light_control")
layout, cards = base.layout, base.cards


class Context:
    """Shim of the public type/field contract, not real HA authorization proof."""

    def __init__(self, user_id=None):
        self.user_id = user_id


sys.modules["homeassistant.core"].Context = Context
base.module("homeassistant.auth")
base.module("homeassistant.auth.permissions")
base.module("homeassistant.auth.permissions.const", POLICY_CONTROL="control")


def control_doc():
    result = base.document([base.card(entity="light.test", action={"kind": "control", "control": "light"})], revision=4)
    result["version"] = 3
    return result


def wire(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class V3Tests(unittest.TestCase):
    def test_v2_read_and_defaults_remain_v2_and_do_not_gain_controls(self):
        old = base.document()
        result = cards.entry_layout({"home_layout": old}, {})
        self.assertEqual(result["version"], 2)
        self.assertEqual(result["cards"][0]["action"], {"kind": "default"})

    def test_explicit_upgrade_is_deterministic_idempotent_and_preserves_ids_actions_revision(self):
        source = base.document([base.card(action={"kind": "service", "service": "light.turn_on", "data": {"brightness_pct": 70}})], revision=8)
        result = layout.migrate_v2_to_v3(source)
        self.assertEqual(result, layout.migrate_v2_to_v3(source))
        self.assertEqual(result, layout.migrate_v2_to_v3(result))
        self.assertEqual(result["cards"], layout.validate_layout(source)["cards"])
        self.assertEqual(result["revision"], 8)
        self.assertEqual(source["version"], 2)

    def test_only_exact_v3_light_entity_control_is_valid(self):
        self.assertEqual(layout.validate_layout(control_doc())["cards"][0]["action"], {"kind": "control", "control": "light"})
        for change in ({"version": 2}, {"version": True}, {"version": 4}):
            with self.assertRaises(layout.LayoutError):
                layout.validate_layout(control_doc() | change)
        for changes in ({"entity_id": "switch.test"}, {"type": "sensor"}, {"type": "action"}, {"slot": 0, "visible": False},
                        {"action": {"kind": "control", "control": "fan"}},
                        {"action": {"kind": "control", "control": "light", "data": {}}},
                        {"action": {"kind": "service", "service": "light.turn_off", "control": "light"}}):
            doc = control_doc()
            doc["cards"][0].update(changes)
            with self.subTest(changes=changes), self.assertRaises(layout.LayoutError):
                layout.validate_layout(doc)

    def test_hidden_control_remains_configured_but_never_executable(self):
        doc = control_doc()
        doc["cards"][0]["visible"] = False
        card = layout.validate_layout(doc)["cards"][0]
        hass, _ = base.environment(states=[base.State("light.test")], services=["light.toggle"])
        self.assertIsNone(cards.resolve_action(hass, card))
        rendered = cards.presentation_payload(hass, [card], light_control_supported=True)
        self.assertNotIn("control_kind", rendered["cards"][2])

    def test_v3_backup_import_validates_schema_without_tokens_or_entry_metadata(self):
        exported = layout.export_layout(control_doc())
        self.assertNotIn("revision", exported["layout"])
        self.assertEqual(layout.import_layout(exported, 15)["revision"], 15)
        self.assertEqual(layout.import_layout(exported, 15)["version"], 3)
        exported["layout"]["channel"] = "secret"
        with self.assertRaises(layout.LayoutError):
            layout.import_layout(exported, 15)

    def test_control_is_passive_to_taps_and_legacy_compatibility_mirror(self):
        doc = layout.validate_layout(control_doc())
        hass, _ = base.environment(states=[base.State("light.test")], services=["light.toggle"])
        self.assertIsNone(cards.resolve_action(hass, doc["cards"][0]))
        mirror = base.panel._legacy_cards(doc)[0]
        self.assertEqual((mirror["entity_id"], mirror["service"], mirror["action"]), ("", "", {"kind": "none"}))
        self.assertEqual(doc["cards"][0]["entity_id"], "light.test")

    def test_control_marker_requires_actual_negotiation_and_full16_wire_stays_v1(self):
        hass, _ = base.environment(states=[base.State("light.test")])
        card = layout.validate_layout(control_doc())["cards"][0]
        for supported in (False, True):
            payload = cards.presentation_payload(hass, [card], language="pl", light_control_supported=supported)
            self.assertEqual((payload["version"], len(payload["cards"])), (1, 16))
            self.assertEqual(payload["cards"][2].get("control_kind"), "light" if supported else None)
            if not supported:
                self.assertEqual(payload["cards"][2]["subtitle"], "Urządzenie bez obsługi")
        ordinary = cards.presentation_payload(hass, [base.card(entity="light.test")], light_control_supported=True)
        self.assertNotIn("control_kind", ordinary["cards"][2])

    def test_profile_advertises_schema_not_connected_native_support(self):
        profile = layout.device_profile()
        self.assertEqual(profile["layout_versions"], [2, 3])
        self.assertEqual(profile["schema_control_types"], ["light", "number", "choice", "cover", "fan", "humidifier", "robot", "panel"])
        self.assertEqual(profile["schema_panel_types"], ["timer", "remote", "power"])
        self.assertTrue(profile["schema_panel_control"])
        self.assertTrue(profile["schema_robot_control"])
        self.assertFalse(profile["features"]["native_controls"])


class Bridge:
    def __init__(self):
        self.hass, _ = base.environment(states=[base.State("light.test", "off", {
            "supported_color_modes": ["brightness"], "brightness": 0,
        })], services=["light.turn_on", "light.turn_off"])
        self._closed, self._connection_epoch = False, 1
        self.layout = layout.validate_layout(control_doc())
        self.tile_cards = cards.normalize_cards(self.layout["cards"])
        self.saved_revision, self.sent_revision = 4, 4
        self.node_name = "test-node"
        self.tasks, self.calls, self.models, self.tile_payloads = set(), [], [], []
        self.gate_kind, self.response_override, self.fail_updates = None, {}, False
        self.entered, self.release = asyncio.Event(), asyncio.Event()
        self.services = {}
        for index, name in enumerate(("light_control_get_status", "light_control_bind", "light_control_update")):
            args = [] if index == 0 else [types.SimpleNamespace(name="payload", type=transport.UserServiceArgType.STRING)]
            self.services[name] = types.SimpleNamespace(name=name, key=index, args=args,
                supports_response=transport.SupportsResponseType.NONE if index == 2 else transport.SupportsResponseType.ONLY)
        self.runtime = types.SimpleNamespace(available=True, client=types.SimpleNamespace(execute_service=self.execute))
        self.esphome_entry = types.SimpleNamespace(runtime_data=self.runtime)
        self.users, self.auth_calls = {}, []

        async def get_user(user_id):
            self.auth_calls.append(user_id)
            return self.users.get(user_id)

        self.hass.auth = types.SimpleNamespace(async_get_user=get_user)
        self.hass.async_create_task = asyncio.create_task
        self._light_control = transport.LightControlTransport(self)
        self._light_control.owner.service_timeout = .02
        self._light_control.owner.state_timeout = .02

    @property
    def tile_device_available(self):
        runtime = self.esphome_entry.runtime_data
        return not self._closed and runtime is not None and runtime.available

    def _find_api_action(self, name):
        return self.services.get(name)

    def _spawn_background(self, coroutine):
        task = asyncio.create_task(coroutine)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task

    async def execute(self, action, data, **kwargs):
        self.calls.append((action.name, deepcopy(data), kwargs))
        if self.gate_kind == action.name:
            self.entered.set()
            await self.release.wait()
        if action.name in self.response_override:
            return self.response_override[action.name]
        if action.name == "home_tiles_set_config":
            self.tile_payloads.append(json.loads(data["payload"]))
            return None
        if action.name == "light_control_get_status":
            value = light.envelope("capability", enabled=True, max_payload_bytes=2048)
        elif action.name == "light_control_bind":
            value = json.loads(data["payload"])
        else:
            if self.fail_updates:
                raise RuntimeError("synthetic transport failure")
            self.models.append(json.loads(data["payload"]))
            return None
        return types.SimpleNamespace(success=True, response_data=wire(value).encode())

    async def async_report_light_control(self, payload, context):
        await self._light_control.async_report(payload, context)


class TransportTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bridge = Bridge()
        self.t = self.bridge._light_control

    async def asyncTearDown(self):
        self.bridge.release.set()
        await self.t.async_shutdown()
        if self.bridge.tasks:
            await asyncio.gather(*self.bridge.tasks, return_exceptions=True)

    def open_message(self, seq=1):
        return light.envelope("open", channel=self.t.owner.channel, open_seq=seq, slot=2, card_id="card-2", revision=4)

    async def opened(self, context=None):
        self.assertTrue(await self.t.async_negotiate())
        await self.t.async_report(wire(self.open_message()), Context() if context is None else context)
        return self.t.owner._selection

    async def test_negotiate_exact_actions_once_then_bind_echo_source_only(self):
        self.assertTrue(await self.t.async_negotiate())
        self.assertTrue(await self.t.async_negotiate())
        self.assertEqual([call[0] for call in self.bridge.calls], ["light_control_get_status", "light_control_bind"])
        self.assertEqual(self.bridge.calls[0][2], {"return_response": True, "timeout": 3.0})
        self.assertEqual(self.t.status(), {"native_control_types": [light.TYPE], "light_control_status": "ready"})
        self.assertEqual(self.bridge.hass.services.calls, [])

    async def test_missing_or_wrong_argument_response_contract_never_binds(self):
        for name in list(self.bridge.services):
            original = self.bridge.services.pop(name)
            self.assertFalse(await self.t.async_negotiate())
            self.bridge.services[name] = original
        self.assertEqual(self.bridge.calls, [])
        self.bridge.services["light_control_bind"].supports_response = transport.SupportsResponseType.OPTIONAL
        self.assertFalse(await self.t.async_negotiate())
        self.assertFalse(self.t.supported)

    async def test_malformed_oversized_disabled_or_wrong_kind_capability_is_not_support(self):
        for data in (b"{}", b"x" * 2049, wire(light.envelope("capability", enabled=False, max_payload_bytes=2048)).encode(),
                     wire(light.envelope("bind", channel="a" * 32)).encode()):
            self.t.invalidate_connection()
            self.bridge.response_override["light_control_get_status"] = types.SimpleNamespace(success=True, response_data=data)
            self.assertFalse(await self.t.async_negotiate())
            self.assertFalse(self.t.supported)

    async def test_bad_bind_echo_never_enables_and_does_not_call_ha(self):
        self.bridge.response_override["light_control_bind"] = types.SimpleNamespace(success=True,
            response_data=wire(light.envelope("bind", channel="f" * 32)).encode())
        self.assertFalse(await self.t.async_negotiate())
        self.assertEqual(self.t.status()["native_control_types"], [])
        self.assertEqual(self.bridge.hass.services.calls, [])

    async def test_old_capability_response_cannot_bind_replaced_runtime(self):
        self.bridge.gate_kind = "light_control_get_status"
        pending = asyncio.create_task(self.t.async_negotiate())
        await asyncio.wait_for(self.bridge.entered.wait(), .2)
        self.bridge._connection_epoch += 1
        self.bridge.esphome_entry.runtime_data = types.SimpleNamespace(available=True, client=self.bridge.runtime.client)
        self.bridge.release.set()
        self.assertFalse(await pending)
        self.assertIsNone(self.t.owner.channel)

    async def test_connection_invalidation_revokes_synchronously_and_new_epoch_gets_new_channel(self):
        selected = await self.opened()
        first = self.t.owner.channel
        self.bridge._connection_epoch += 1
        self.t.invalidate_connection()
        self.assertIsNone(self.t.owner._selection)
        self.assertFalse(self.t.supported)
        self.assertTrue(selected.renewal.cancelling())
        self.assertTrue(await self.t.async_negotiate())
        self.assertNotEqual(first, self.t.owner.channel)

    async def test_revision_invalidation_revokes_before_close_transport_and_preserves_channel(self):
        selected = await self.opened()
        channel = self.t.owner.channel
        self.bridge.saved_revision = 5
        self.t.invalidate_selection()
        self.assertIsNone(self.t.owner._selection)
        self.assertEqual(self.t.owner.channel, channel)
        if self.t._close_task:
            await self.t._close_task
        self.assertEqual(self.bridge.models[-1]["kind"], "close")
        self.assertEqual(self.bridge.models[-1]["token"], selected.identity["token"])

    async def test_real_system_context_is_explicit_policy_but_none_and_lookalikes_deny(self):
        self.assertTrue(await transport.authorize_ha_context(self.bridge.hass, Context(), "light.test"))
        for value in (None, types.SimpleNamespace(user_id=None), {"user_id": None}):
            self.assertFalse(await transport.authorize_ha_context(self.bridge.hass, value, "light.test"))
        self.assertFalse(await transport.authorize_ha_context(self.bridge.hass, Context(""), "light.test"))

    async def test_actual_active_user_and_control_permission_are_both_required(self):
        checks = []
        user = types.SimpleNamespace(is_active=True, permissions=types.SimpleNamespace(
            check_entity=lambda entity, policy: checks.append((entity, policy)) or True))
        self.bridge.users["allowed"] = user
        self.assertTrue(await transport.authorize_ha_context(self.bridge.hass, Context("allowed"), "light.test"))
        self.assertEqual(checks, [("light.test", "control")])
        user.is_active = False
        self.assertFalse(await transport.authorize_ha_context(self.bridge.hass, Context("allowed"), "light.test"))
        self.assertFalse(await transport.authorize_ha_context(self.bridge.hass, Context("unknown"), "light.test"))

    async def test_authenticated_denial_never_grants_or_dispatches(self):
        self.bridge.users["denied"] = types.SimpleNamespace(is_active=True,
            permissions=types.SimpleNamespace(check_entity=lambda *_: False))
        await self.t.async_negotiate()
        with self.assertRaisesRegex(light.ProtocolError, "unauthorized"):
            await self.t.async_report(wire(self.open_message()), Context("denied"))
        self.assertIsNone(self.t.owner._selection)
        self.assertEqual(self.bridge.hass.services.calls, [])

    async def test_service_dispatch_preserves_actual_context_and_bound_server_entity(self):
        context = Context()
        selected = await self.opened(context)
        command = light.envelope("command", **selected.identity, command_seq=1, op="brightness", value=100)
        await self.t.async_report(wire(command), context)
        await selected.command.task
        args, kwargs = self.bridge.hass.services.calls[0]
        self.assertEqual(args, ("light", "turn_on", {"entity_id": "light.test", "brightness_pct": 100}))
        self.assertIs(kwargs["context"], context)
        self.assertEqual(self.bridge.models[-1]["status"], "not_confirmed")

    async def test_v2_open_is_denied_even_after_successful_native_bind(self):
        self.bridge.layout["version"] = 2
        await self.t.async_negotiate()
        with self.assertRaisesRegex(light.ProtocolError, "selection_changed"):
            await self.t.async_report(wire(self.open_message()), Context())
        self.assertEqual(self.bridge.hass.services.calls, [])

    async def test_reused_tile_listener_events_are_coalesced_to_one_task(self):
        await self.opened()
        for _ in range(100):
            self.t.state_changed()
        self.assertEqual(len(self.bridge.tasks), 1)
        await self.t._state_task
        self.assertEqual(sum(value["kind"] == "state" for value in self.bridge.models), 1)

    async def test_missing_live_state_closes_without_ha_dispatch(self):
        await self.opened()
        self.bridge.hass.states.items.clear()
        self.t.state_changed()
        await self.t._state_task
        self.assertIsNone(self.t.owner._selection)
        self.assertEqual(self.bridge.models[-1]["reason"], "entity_unavailable")
        self.assertEqual(self.bridge.hass.services.calls, [])

    async def test_entity_removal_during_state_send_drains_latest_once_and_closes(self):
        await self.opened()
        self.bridge.gate_kind = "light_control_update"
        self.t.state_changed()
        pending = self.t._state_task
        await asyncio.wait_for(self.bridge.entered.wait(), .2)
        self.bridge.hass.states.items.clear()
        for _ in range(100):
            self.t.state_changed()
        self.assertEqual(len(self.bridge.tasks), 1)
        self.assertIs(self.t._state_task, pending)
        self.bridge.release.set()
        await pending
        self.assertIsNone(self.t.owner._selection)
        self.assertEqual([value["kind"] for value in self.bridge.models], ["grant", "state", "close"])
        self.assertEqual(self.bridge.models[-1]["reason"], "entity_unavailable")
        self.assertEqual(self.bridge.hass.services.calls, [])

    async def test_capability_removal_during_state_send_also_closes_latest_selection(self):
        await self.opened()
        self.bridge.gate_kind = "light_control_update"
        self.t.state_changed()
        pending = self.t._state_task
        await asyncio.wait_for(self.bridge.entered.wait(), .2)
        self.bridge.hass.services.names.remove("light.turn_off")
        self.t.state_changed()
        self.bridge.release.set()
        await pending
        self.assertIsNone(self.t.owner._selection)
        self.assertEqual(self.bridge.models[-1]["reason"], "capabilities_changed")
        self.assertEqual(self.bridge.hass.services.calls, [])

    async def test_transport_failure_cannot_report_ready_or_applied(self):
        await self.opened()
        self.bridge.fail_updates = True
        self.t.state_changed()
        await self.t._state_task
        self.assertFalse(self.t.supported)
        self.assertEqual(self.t.status()["light_control_status"], "unconfirmed")
        self.assertNotIn("applied", self.t.status())

    async def test_removing_native_action_revokes_cached_support(self):
        await self.opened()
        self.bridge.services.pop("light_control_update")
        self.assertFalse(await self.t.async_negotiate())
        self.assertFalse(self.t.supported)
        self.assertIsNone(self.t.owner._selection)

    async def test_shutdown_cancels_probe_and_cannot_reenable_from_late_response(self):
        self.bridge.gate_kind = "light_control_get_status"
        pending = asyncio.create_task(self.t.async_negotiate())
        await asyncio.wait_for(self.bridge.entered.wait(), .2)
        await self.t.async_shutdown()
        self.assertTrue(pending.cancelled())
        self.bridge.release.set()
        self.assertFalse(self.t.supported)
        self.assertFalse(await self.t.async_negotiate())

    async def test_unique_node_and_channel_route_forward_context_ambiguity_rejects(self):
        await self.t.async_negotiate()
        entry = types.SimpleNamespace(runtime_data=self.bridge)
        entries = [entry]
        self.bridge.hass.config_entries.async_loaded_entries = lambda _domain: entries
        context = Context()
        self.assertFalse(await transport.async_route_report(self.bridge.hass, "wrong-node", wire(self.open_message()), context))
        entries.append(entry)
        self.assertFalse(await transport.async_route_report(self.bridge.hass, "test-node", wire(self.open_message()), context))
        entries.pop()
        self.assertTrue(await transport.async_route_report(self.bridge.hass, "test-node", wire(self.open_message()), context))
        self.assertIs(self.t.owner._selection.context, context)

    async def test_legacy_get_then_save_cannot_downgrade_or_erase_current_v3(self):
        hass, entry = base.environment(doc=control_doc())
        original = deepcopy(entry.options)
        read = base.Connection()
        await base.panel.websocket_get_tiles(hass, read, {"id": 1})
        mirror = read.results[0]["entries"][0]["cards"]
        self.assertEqual(mirror[0]["entity_id"], "")
        response = base.Connection()
        await base.panel.websocket_save_tiles(hass, response, {
            "id": 2, "entry_id": entry.entry_id, "cards": mirror,
        })
        self.assertEqual(response.errors[0][0], "incompatible_editor")
        self.assertEqual(response.results, [])
        self.assertEqual(hass.config_entries.updates, [])
        self.assertEqual(entry.options, original)
        self.assertEqual(entry.options["home_layout"]["version"], 3)
        self.assertEqual(entry.options["home_layout"]["cards"][0]["entity_id"], "light.test")

    async def test_legacy_v2_save_still_preserves_its_supported_behavior_and_other_options(self):
        hass, entry = base.environment()
        old_camera_options = {key: deepcopy(entry.options[key]) for key in ("cameras", "stream_fps", "future_setting")}
        response = base.Connection()
        await base.panel.websocket_save_tiles(hass, response, {
            "id": 1, "entry_id": entry.entry_id,
            "cards": base.panel._legacy_cards(entry.options["home_layout"]),
        })
        self.assertEqual(response.errors, [])
        self.assertEqual(entry.options["home_layout"]["version"], 2)
        self.assertEqual(entry.options["home_layout"]["revision"], 1)
        self.assertEqual(entry.options["home_layout"]["cards"][0]["id"], "card-2")
        self.assertEqual({key: entry.options[key] for key in old_camera_options}, old_camera_options)

    def controller_bridge(self):
        bridge = base.BridgeTests("test_send_revision_only_after_successful_api_call").bridge()
        bridge.hass = self.bridge.hass
        bridge.layout = self.bridge.layout
        bridge.tile_cards = self.bridge.tile_cards
        bridge.saved_revision, bridge.sent_revision = 4, None
        bridge.esphome_entry = self.bridge.esphome_entry
        self.bridge.services["home_tiles_set_config"] = types.SimpleNamespace(name="home_tiles_set_config")
        bridge._find_api_action = self.bridge._find_api_action
        bridge._light_control = transport.LightControlTransport(bridge)
        return bridge

    async def test_actual_controller_negotiates_before_optin_marker_and_sent_revision(self):
        bridge = self.controller_bridge()
        try:
            self.assertTrue(await bridge.async_push_tiles())
            self.assertEqual([call[0] for call in self.bridge.calls], [
                "light_control_get_status", "light_control_bind", "home_tiles_set_config"])
            self.assertEqual(self.bridge.tile_payloads[-1]["cards"][2]["control_kind"], "light")
            self.assertEqual(bridge.sent_revision, 4)
            self.assertIsNone(bridge.accepted_revision)
            self.assertNotIn("applied_revision", bridge.light_control_status())
        finally:
            await bridge.async_shutdown()

    async def test_actual_controller_control_card_never_falls_back_to_ordinary_tap(self):
        bridge = self.controller_bridge()
        try:
            bridge.sent_revision = 4
            self.bridge.hass.services.names.add("light.toggle")
            await bridge.async_press_tile(2, context=Context())
            self.assertEqual(self.bridge.hass.services.calls, [])
            bridge.tile_cards[0]["action"] = {"kind": "default"}
            await bridge.async_press_tile(2, context=Context())
            self.assertEqual(len(self.bridge.hass.services.calls), 1)
        finally:
            await bridge.async_shutdown()

    async def test_actual_controller_options_revoke_selected_control_before_resending(self):
        bridge = self.controller_bridge()
        try:
            await bridge.async_push_tiles()
            owner = bridge._light_control.owner
            message = light.envelope("open", channel=owner.channel, open_seq=1, slot=2, card_id="card-2", revision=4)
            await bridge.async_report_light_control(wire(message), Context())
            self.assertIsNotNone(owner._selection)
            changed = control_doc()
            changed["revision"] = 5
            bridge.entry.options["home_layout"] = changed
            bridge.async_schedule_tile_push = lambda **_: None
            self.assertTrue(bridge.async_apply_tile_options())
            self.assertIsNone(owner._selection)
            self.assertEqual(bridge.saved_revision, 5)
            self.assertEqual(self.bridge.hass.services.calls, [])
        finally:
            await bridge.async_shutdown()


if __name__ == "__main__":
    unittest.main()
