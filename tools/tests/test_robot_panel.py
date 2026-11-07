"""Robot panel contracts over the existing owner; all services are host fakes."""

import asyncio
from copy import deepcopy
import importlib
import json
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import test_entity_control as shared
import test_ha_layout as base

codec = shared.codec
robot = importlib.import_module("_atmosfera_test.robot_domain")
ACTION = robot.ROBOT_ACTION
KINDS = ["light", "number", "choice", "cover", "fan", "humidifier", "robot"]


def environment(kind="vacuum"):
    attributes = ({"supported_features": 32700, "fan_speed_list": [" Eco ", "Żółty"], "fan_speed": " Eco "}
                  if kind == "vacuum" else {"supported_features": 7})
    state = base.State(kind + ".test", "docked", attributes)
    hass, _ = base.environment(states=[state], services=[kind + "." + name for name in robot.SERVICES[kind].values()])
    if kind == "vacuum":
        hass.entity_registry.entries[state.entity_id] = NS(platform=None, translation_key=None,
            options={"vacuum": {"area_mapping": {"living": ["vendor42"], "kitchen": ["vendor3"]}}})
        hass.area_registry.entries.update(living=NS(name="Salon"), kitchen=NS(name="Kuchnia"))
    return hass, state


class RobotModelTests(unittest.TestCase):
    def test_all_masks_services_and_activities_reuse_existing_admission(self):
        for kind in robot.SERVICES:
            policy = robot.vacuum_actions if kind == "vacuum" else robot.mower_actions
            operations = list(policy.FEATURES)
            for mask in range(1 << len(operations)):
                features = sum(policy.FEATURES[op] for index, op in enumerate(operations) if mask & (1 << index))
                for missing in (None, *operations):
                    hass, state = environment(kind)
                    state.attributes["supported_features"] = features
                    if missing:
                        hass.services.names.remove(kind + "." + missing)
                    expected = sum(bit for op, bit in robot.BITS.items() if robot.SERVICES[kind].get(op) in operations
                                   and features & policy.FEATURES[robot.SERVICES[kind][op]]
                                   and robot.SERVICES[kind][op] != missing)
                    with self.subTest(kind=kind, mask=mask, missing=missing):
                        if not expected:
                            with self.assertRaises(robot.RobotDomainError):
                                robot.RobotDomain.from_ha(hass, state)
                            continue
                        domain = robot.RobotDomain.from_ha(hass, state)
                        self.assertEqual(domain.actions, expected)
                        for activity in (*robot.ACTIVITIES[kind], "unknown", "unavailable", "on"):
                            state.state = activity
                            observed = robot.RobotObservation.from_ha(state, domain)
                            allowed = sum(bit for op, bit in robot.BITS.items() if expected & bit
                                          and activity in policy.ALLOWED[robot.SERVICES[kind][op]])
                            self.assertEqual(observed.eligible_actions, allowed)
                            self.assertEqual(observed.available, activity in robot.ACTIVITIES[kind])

    def test_actual_catalogues_map_exact_values_without_vendor_ids_on_wire(self):
        hass, state = environment()
        domain = robot.RobotDomain.from_ha(hass, state)
        self.assertEqual(domain.actions, 63)
        self.assertEqual(domain.speeds, (" Eco ", "Żółty"))
        self.assertEqual(domain.areas, ("Salon", "Kuchnia"))
        self.assertEqual(domain.service_action("speed", 0), ("vacuum", "set_fan_speed", {"fan_speed": " Eco "}))
        self.assertEqual(domain.service_action("area", 1), ("vacuum", "clean_area", {"cleaning_area_id": "kitchen"}))
        self.assertNotIn("vendor", repr(domain.descriptor()))
        for target in (True, -1, 2, "1", 1.0):
            with self.assertRaises(robot.RobotDomainError):
                domain.service_action("area", target)
        before = domain.fingerprint
        hass.entity_registry.entries[state.entity_id].options["vacuum"]["area_mapping"]["living"] = ["changed_target"]
        self.assertNotEqual(robot.RobotDomain.from_ha(hass, state).fingerprint, before)

    def test_room_catalogue_is_complete_or_disabled_without_hiding_other_facets(self):
        hass, state = environment()
        entry = hass.entity_registry.entries[state.entity_id]
        entry.options["vacuum"]["area_mapping"] = {str(i): [str(i)] for i in range(8)}
        hass.area_registry.entries = {str(i): NS(name=str(i) + "ą" * 15) for i in range(8)}
        self.assertEqual(len(robot.RobotDomain.from_ha(hass, state).areas), 8)
        entry.options["vacuum"]["area_mapping"]["8"] = ["8"]
        hass.area_registry.entries["8"] = NS(name="Room9")
        domain = robot.RobotDomain.from_ha(hass, state)
        self.assertEqual((domain.areas, domain.area_reason), ((), "too_many_areas"))
        self.assertEqual(domain.actions, 63)
        del entry.options["vacuum"]["area_mapping"]["8"]
        for invalid in ("x" * 33, "bad\nname", "0" + "ą" * 15):
            hass.area_registry.entries["1"].name = invalid
            domain = robot.RobotDomain.from_ha(hass, state)
            self.assertEqual((domain.areas, domain.area_reason), ((), "area_labels_unsupported"))
            self.assertEqual(domain.speeds, (" Eco ", "Żółty"))
        del hass.area_registry.entries["0"]
        self.assertEqual(robot.RobotDomain.from_ha(hass, state).area_reason, "no_mapped_areas")

    def test_unknown_and_partial_suction_do_not_invent_current_or_battery(self):
        hass, state = environment()
        domain = robot.RobotDomain.from_ha(hass, state)
        original = robot.RobotObservation.from_ha(state, domain)
        self.assertIsNone(original.battery_percent)
        for value, expected in ((0, 0), (100, 100), (51, 51), (51.5, None), (True, None), ("50", None), (-1, None), (101, None)):
            state.attributes["battery_level"] = value
            observed = robot.RobotObservation.from_ha(state, domain)
            self.assertEqual(observed.battery_percent, expected)
            self.assertEqual(observed.command_state, original.command_state)
        state.attributes["fan_speed"] = "not in catalogue"
        observed = robot.RobotObservation.from_ha(state, domain)
        self.assertIsNone(observed.speed_index)
        self.assertFalse(observed.can_command("speed"))
        self.assertTrue(observed.can_command("start"))
        state.state = "unavailable"
        self.assertEqual(robot.RobotObservation.from_ha(state, domain), robot.RobotObservation("unknown", None, None, 0, False))
        state.attributes["fan_speed_list"] = [str(i) for i in range(9)]
        self.assertEqual(robot.RobotDomain.from_ha(hass, state).speeds, ())

    def test_launcher_metadata_and_projection_are_explicit_and_passive(self):
        for kind in robot.SERVICES:
            hass, state = environment(kind)
            card = base.card(entity=state.entity_id, action=ACTION)
            self.assertEqual(base.layout.validate_layout(base.document([card]) | {"version": 3})["cards"][0], card)
            self.assertIsNone(base.cards.resolve_action(hass, card))
            meta = base.cards._robot_control_metadata(hass, state)["robot_control"]
            self.assertEqual(meta["robot_type"], kind)
            self.assertRegex(meta["catalogue_fingerprint"], r"^[a-f0-9]{64}$")
            self.assertEqual(meta["caps"]["actions"], 63 if kind == "vacuum" else 11)
            for enabled in (True, False):
                row = base.cards.presentation_payload(hass, [card], robot_control_supported=enabled,
                                                       press_enabled_supported=True)["cards"][2]
                self.assertEqual(row.get("control_kind"), "robot" if enabled else None)
        for entity, action, version in (("fan.test", ACTION, 3), ("vacuum.test", ACTION, 2),
                                        ("vacuum.test", ACTION | {"property": "area"}, 3)):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_action(action, entity, layout_version=version)

    def test_registry_listeners_are_filtered_and_share_existing_subscription_lifetime(self):
        bridge = base.BridgeTests().bridge()
        bridge.hass, state = environment()
        card = base.card(entity=state.entity_id, action=ACTION)
        bridge.tile_cards, bridge.tile_entity_ids = [card], (state.entity_id,)
        events, removed, pushes, notifications = [], [], [], []
        bridge.hass.bus = NS(async_listen=lambda kind, callback: (events.append(kind) or (lambda: removed.append(kind))))
        bridge.async_schedule_tile_push = lambda **kwargs: pushes.append(kwargs)
        bridge._light_control = NS(robot_registry_changed=lambda event: notifications.append(event.data))
        with patch.object(base.controller, "async_track_state_change_event", return_value=lambda: None):
            bridge._replace_tile_subscription()
            self.assertEqual(events, ["entity_registry_updated", "area_registry_updated"])
            for data in ({"entity_id": "vacuum.other"}, {"area_id": "other"}):
                bridge._tile_area_registry_changed(NS(data=data))
            self.assertEqual(pushes, [])
            for data in ({"entity_id": state.entity_id}, {"area_id": "living"}):
                bridge._tile_area_registry_changed(NS(data=data))
            self.assertEqual(len(notifications), 2)
            self.assertEqual(pushes, [{"delay": 0}, {"delay": 0}])
            card["visible"] = False
            bridge._tile_area_registry_changed(NS(data={"area_id": "living"}))
            self.assertEqual(len(pushes), 2)
            bridge._closed = True
            bridge._replace_tile_subscription()
        self.assertEqual(removed, events)
        self.assertEqual(bridge._tile_registry_unsubscribers, [])


class RobotCodecTests(unittest.TestCase):
    def state(self):
        hass, state = environment()
        domain = robot.RobotDomain.from_ha(hass, state)
        return codec.envelope("grant", channel="a" * 32, token="b" * 32, open_seq=1, slot=31,
            card_id="robot31", revision=10, control_kind="robot", state_seq=1, ttl_ms=30000,
            title="Robot", state_generation=1, robot_type="vacuum", robot_caps=domain.descriptor(),
            **robot.RobotObservation.from_ha(state, domain).descriptor())

    def test_exact_snapshot_commands_maximum_envelope_and_new_terminal_is_robot_only(self):
        value = self.state()
        self.assertEqual(codec.decode(codec.encode(value)), value)
        maximum = value | {"title": "ą" * 80, "card_id": "a" * 64, "revision": 2**53 - 1,
                           "open_seq": 2**31-1, "state_seq": 2**31-1, "state_generation": 2**31-1,
                           "robot_caps": {"actions": 63, "speeds": [str(i) + '"' * 31 for i in range(8)],
                                          "areas": [str(i) + "\\" * 31 for i in range(8)]}}
        self.assertLessEqual(len(codec.encode(maximum).encode()), 2048)
        identity = {key: value[key] for key in codec.SELECTION}
        for op in robot.OPERATIONS:
            command = codec.envelope("command", **identity, command_seq=1, op=op,
                                     expected_state_generation=1, **({"target_index": 1} if op in robot.INDEXED_OPERATIONS else {}))
            self.assertEqual(codec.decode_report(codec.encode(command)), command)
        result = codec.envelope("result", **identity, command_seq=1, state_seq=1, status="service_completed", reason="none")
        self.assertEqual(codec.decode(codec.encode(result)), result)
        for control in ("light", "number", "choice", "cover", "fan", "humidifier"):
            with self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(result | {"control_kind": control}))
        with self.assertRaises(codec.ProtocolError):
            shared.light.decode(shared.wire({k: v for k, v in result.items() if k != "control_kind"} | {"type": shared.light.TYPE}))

    def test_strict_capabilities_observations_and_commands(self):
        value = self.state()
        for change in ({"activity": "mowing"}, {"available": 1}, {"available": False},
                       {"eligible_actions": 63}, {"eligible_actions": True}, {"speed_index": 2},
                       {"battery_percent": 51.5}, {"battery_percent": True}, {"area_enabled": 1},
                       {"robot_type": "lawn_mower"}, {"robot_caps": {"actions": 0, "speeds": [], "areas": []}},
                       {"robot_caps": value["robot_caps"] | {"actions": True}}, {"extra": 0}):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(value | change))
        unknown = value | {"activity": "unknown", "available": False, "speed_index": None,
                           "battery_percent": None, "eligible_actions": 0, "area_enabled": False}
        self.assertEqual(codec.decode(codec.encode(unknown)), unknown)
        for change in ({"speed_index": 0}, {"battery_percent": 0}, {"eligible_actions": 1}, {"area_enabled": True}):
            with self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(unknown | change))
        identity = {key: value[key] for key in codec.SELECTION}
        command = codec.envelope("command", **identity, command_seq=1, op="speed", target_index=1, expected_state_generation=1)
        for change in ({"target_index": 8}, {"target_index": True}, {"op": "start"}, {"target": 1}, {"expected_state_generation": True}):
            with self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(command | change))


class RobotOwnerTests(unittest.IsolatedAsyncioTestCase):
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown

    def bind(self):
        cap = codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=KINDS)
        value = self.owner.prepare_bind(shared.wire(cap), epoch=1, runtime=self.runtime)
        self.owner.accept_bind(shared.wire(value), epoch=1, runtime=self.runtime)

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.hass, self.state = environment()
        self.owner.hass = self.hass
        self.card.update(entity_id=self.state.entity_id, action=deepcopy(ACTION))
        self.fail_service = False

        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate:
                await self.service_gate.wait()
            if self.fail_service:
                raise RuntimeError("provider failed")
            if not self.apply:
                return
            operation, data = args[1:3]
            if operation == "set_fan_speed":
                self.change(self.state.state, fan_speed=data["fan_speed"])
            elif operation not in {"locate", "clean_area"}:
                self.change({"start": "cleaning", "start_mowing": "mowing", "pause": "paused", "stop": "idle",
                             "return_to_base": "returning", "dock": "docked", "clean_spot": "cleaning"}[operation])
        self.hass.services.async_call = service

    async def open(self, seq=1):
        return await shared.NumberOwnerTests.open(self, seq, "robot")

    def command(self, seq=1, op="start", target=None, **changes):
        selected = self.owner._selection
        return codec.envelope("command", **selected.identity, command_seq=seq, op=op,
            expected_state_generation=selected.domain_state[2], **({"target_index": target} if op in robot.INDEXED_OPERATIONS else {})) | changes

    def registry_event(self, **data):
        return self.owner.observe_robot_registry_event(NS(data=data))

    async def test_passive_open_exact_actions_suction_and_rooms_send_once_with_context(self):
        grant = await self.open()
        self.assertEqual(grant["robot_caps"]["areas"], ["Salon", "Kuchnia"])
        self.assertEqual(self.hass.services.calls, [])
        for seq, op, target in ((1, "speed", 1), (2, "area", 1), (3, "locate", None),
                                (4, "start", None), (5, "pause", None), (6, "stop", None),
                                (7, "spot", None), (8, "dock", None)):
            command = self.command(seq, op, target)
            await self.send(command)
            await self.send(command)
            self.assertEqual(self.results()[-1]["status"], "service_completed" if op in robot.COMPLETED_OPERATIONS else "state_matches")
        self.assertEqual(len(self.hass.services.calls), 8)
        self.assertEqual(self.hass.services.calls[0][0], ("vacuum", "set_fan_speed", {"entity_id":"vacuum.test", "fan_speed":"Żółty"}))
        self.assertEqual(self.hass.services.calls[1][0], ("vacuum", "clean_area", {"entity_id":"vacuum.test", "cleaning_area_id":"kitchen"}))
        self.assertTrue(all(kwargs["context"] is self.user for _, kwargs in self.hass.services.calls))
        for i, value in enumerate(self.outputs):
            if value["kind"] == "result" and value["status"] in self.owner._terminal_statuses:
                self.assertEqual((self.outputs[i-1]["kind"], self.outputs[i-1]["state_seq"]), ("state", value["state_seq"]))
        await self.owner.async_close()
        self.assertEqual(len(self.hass.services.calls), 8)

    async def test_service_completed_waits_for_callback_and_never_fakes_activity(self):
        await self.open()
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command(op="locate")), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        record = self.owner._selection.command
        self.assertEqual(record.result["status"], "pending")
        self.service_gate.set()
        await asyncio.wait_for(record.task, .4)
        self.assertEqual(record.result["status"], "service_completed")
        self.assertEqual(self.state.state, "docked")
        self.assertIsNone(self.owner._selection.command)
        self.assertFalse(any(v["status"] in {"state_matches", "already_matched"} for v in self.results()))

    async def test_unobservable_service_exception_and_timeout_are_not_completed(self):
        await self.open()
        self.fail_service = True
        await self.send(self.command(op="area", target=0))
        self.assertEqual((self.results()[-1]["status"], self.results()[-1]["reason"]), ("rejected", "service_error"))
        self.fail_service = False
        self.service_gate = asyncio.Event()
        await self.send(self.command(2, "locate"))
        self.assertEqual((self.results()[-1]["status"], self.results()[-1]["reason"]), ("not_confirmed", "service_timeout"))
        self.service_gate.set()
        await asyncio.sleep(.01)
        self.assertFalse(any(v["status"] == "service_completed" for v in self.results()))

    async def test_battery_update_preserves_held_command_but_activity_ABA_cancels(self):
        await self.open()
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        await self.owner.async_handle(shared.wire(self.command(op="speed", target=1)), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        record = self.owner._selection.command
        self.change("docked", battery_level=43)
        self.assertEqual(self.owner._selection.domain_state[2], 1)
        self.auth_gate.set()
        await asyncio.wait_for(record.task, .4)
        self.assertEqual(record.result["status"], "state_matches")
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        await self.owner.async_handle(shared.wire(self.command(2)), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        record = self.owner._selection.command
        self.change("cleaning")
        self.change("docked")
        self.auth_gate.set()
        await asyncio.wait_for(record.task, .4)
        self.assertEqual(record.result["reason"], "stale_state")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_room_mapping_ABA_during_authorization_revokes_exact_target(self):
        await self.open()
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        await self.owner.async_handle(shared.wire(self.command(op="area", target=0)), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        mapping = self.hass.entity_registry.entries[self.state.entity_id].options["vacuum"]["area_mapping"]
        mapping["living"] = ["different_segment"]
        close = self.registry_event(entity_id=self.state.entity_id)
        self.assertEqual(close["reason"], "capabilities_changed")
        mapping["living"] = ["vendor42"]
        self.registry_event(entity_id=self.state.entity_id)
        self.auth_gate.set()
        await asyncio.sleep(.01)
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_area_rename_ABA_while_opening_cannot_grant_and_unrelated_area_does_not_revoke(self):
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        job = asyncio.create_task(self.open())
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.hass.area_registry.entries["living"].name = "Changed"
        self.registry_event(area_id="living")
        self.hass.area_registry.entries["living"].name = "Salon"
        self.registry_event(area_id="living")
        self.auth_gate.set()
        self.assertIsNone(await asyncio.wait_for(job, .4))
        await self.open(2)
        self.registry_event(area_id="unrelated")
        self.assertIsNotNone(self.owner._selection)

    async def test_priority_stop_waits_for_start_callback_without_parallel_or_second_successor(self):
        await self.open()
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        self.change("cleaning")
        await self.owner.async_handle(shared.wire(self.command(2, "stop", expected_state_generation=1)), self.user)
        successor = self.owner._selection.command
        self.assertTrue(successor.priority)
        await self.owner.async_handle(shared.wire(self.command(3, "pause")), self.user)
        self.assertEqual(len(self.hass.services.calls), 1)
        self.service_gate.set()
        await asyncio.wait_for(successor.task, .4)
        self.assertEqual([args[1] for args, _ in self.hass.services.calls], ["start", "stop"])
        self.assertEqual(successor.result["status"], "state_matches")

    async def test_unknown_and_capability_loss_disable_without_dispatch(self):
        await self.open()
        self.change("unavailable")
        await self.send(self.command(op="locate"))
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assertEqual(self.hass.services.calls, [])
        self.change("docked")
        close = self.change("docked", supported_features=32700 & ~512)
        self.assertEqual(close["reason"], "capabilities_changed")
        self.assertIsNone(self.owner._selection)

    async def test_mower_reuses_three_actual_services_without_fabricated_stop(self):
        self.hass, self.state = environment("lawn_mower")
        previous = self.owner.hass.services.async_call
        self.owner.hass = self.hass
        self.hass.services.async_call = previous
        self.card["entity_id"] = self.state.entity_id
        grant = await self.open()
        self.assertEqual(grant["robot_caps"], {"actions": 11, "speeds": [], "areas": []})
        for seq, op in ((1, "start"), (2, "pause"), (3, "dock")):
            await self.send(self.command(seq, op))
            self.assertEqual(self.results()[-1]["status"], "state_matches")
        await self.send(self.command(4, "stop"))
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assertEqual([args[1] for args, _ in self.hass.services.calls], ["start_mowing", "pause", "dock"])

    async def test_permission_loss_and_service_loss_recheck_before_dispatch(self):
        await self.open()
        self.allowed = False
        await self.send(self.command(op="locate"))
        self.assertEqual(self.results()[-1]["reason"], "unauthorized")
        self.assertEqual(self.hass.services.calls, [])
        self.allowed = True
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        await self.owner.async_handle(shared.wire(self.command(2)), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        record = self.owner._selection.command
        self.hass.services.names.remove("vacuum.start")
        self.auth_gate.set()
        await asyncio.wait_for(record.task, .4)
        self.assertEqual(self.hass.services.calls, [])
        self.assertIsNone(self.owner._selection)

    async def test_close_before_service_callback_finishes_never_publishes_old_completion(self):
        await self.open()
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command(op="area", target=0)), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        await self.owner.async_close()
        self.service_gate.set()
        await asyncio.sleep(.02)
        self.assertEqual(len(self.hass.services.calls), 1)
        self.assertFalse(any(value["status"] == "service_completed" for value in self.results()))

    async def test_close_while_interrupt_waits_never_executes_late_pause(self):
        await self.open()
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        self.change("cleaning")
        await self.owner.async_handle(shared.wire(self.command(2, "pause")), self.user)
        await self.owner.async_close()
        self.service_gate.set()
        await asyncio.sleep(.02)
        self.assertEqual([args[1] for args, _ in self.hass.services.calls], ["start"])


class RobotTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_editor_support_requires_negotiated_live_robot_kind(self):
        for enabled in (False, True):
            bridge = shared.NumberModelTransportTests().generic_bridge()
            original = bridge.runtime.client.execute_service

            async def execute(action, data, **kwargs):
                reply = await original(action, data, **kwargs)
                if enabled and action.name == "entity_control_get_status":
                    value = json.loads(reply.response_data)
                    value["control_kinds"].append("robot")
                    reply.response_data = shared.wire(value).encode()
                return reply

            bridge.runtime.client.execute_service = execute
            transport = bridge._light_control
            try:
                self.assertTrue(await transport.async_negotiate())
                self.assertEqual(transport.robot_supported, enabled)
                self.assertEqual(transport.status().get("robot_control_supported", False), enabled)
                transport.invalidate_connection()
                self.assertFalse(transport.robot_supported)
                self.assertFalse(transport.status().get("robot_control_supported", False))
            finally:
                await transport.async_shutdown()
