"""Cover host policy races; service fakes do not operate an actual actuator."""

import asyncio
from copy import deepcopy
import unittest

import test_entity_control as shared
import test_ha_layout as base

codec = shared.codec


class CoverCodecTests(unittest.TestCase):
    def identity(self):
        return dict(channel="a" * 32, open_seq=1, slot=2, card_id="card-2", revision=4,
                    control_kind="cover", token="b" * 32)

    def state(self):
        return codec.envelope("state", **self.identity(), state_seq=1, ttl_ms=30000,
                              title="Roleta", cover_state="closed", position=0, available=True,
                              cover_caps={"open": True, "stop": True, "close": True}, state_generation=1)

    def test_strict_roundtrip_and_old_capability_sets_remain_accepted(self):
        state = self.state()
        opening = {k: v for k, v in self.identity().items() if k != "token"}
        for value in [state, state | {"kind": "grant"},
                      codec.envelope("open", **opening),
                      codec.envelope("command", **self.identity(), command_seq=1, op="open", expected_state_generation=1),
                      codec.envelope("result", **self.identity(), command_seq=1, state_seq=1, status="state_matches", reason="none"),
                      state | {"cover_state": "unknown", "position": None, "available": False}]:
            self.assertEqual(codec.decode(codec.encode(value)), value)
        for kinds in (["light", "number"], ["light", "number", "choice"],
                      ["light", "number", "cover"], ["light", "number", "choice", "cover"]):
            value = codec.envelope("capability", enabled=True, max_payload_bytes=2048, control_kinds=kinds)
            self.assertEqual(codec.decode(codec.encode(value)), value)

    def test_snapshot_rejects_bad_caps_availability_position_and_mixed_kind_fields(self):
        state = self.state()
        for change in ({"position": True}, {"position": -1}, {"position": 101}, {"position": 1.5},
                       {"cover_state": "stopped"}, {"available": False}, {"available": 1},
                       {"cover_caps": {"open": 1, "stop": True, "close": True}},
                       {"cover_caps": {"open": False, "stop": False, "close": False}},
                       {"cover_caps": {"open": True, "stop": True, "close": True, "tilt": True}},
                       {"state_generation": True}, {"index": 0}, {"options": ["Open"]}):
            with self.subTest(change=change), self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(state | change))
        command = codec.envelope("command", **self.identity(), command_seq=1, op="open", expected_state_generation=1)
        for change in ({"op": "toggle"}, {"op": "set_position"}, {"expected_index": 0},
                       {"expected_state_generation": 0}, {"expected_state_generation": True}, {"target": 100}):
            with self.assertRaises(codec.ProtocolError):
                codec.decode(shared.wire(command | change))


class CoverOwnerTests(unittest.IsolatedAsyncioTestCase):
    send = shared.NumberOwnerTests.send
    change = shared.NumberOwnerTests.change
    results = shared.NumberOwnerTests.results
    assert_terminal_order = shared.NumberOwnerTests.assert_terminal_order
    asyncTearDown = shared.NumberOwnerTests.asyncTearDown

    def bind(self):
        capability = codec.envelope("capability", enabled=True, max_payload_bytes=2048,
                                    control_kinds=["light", "number", "choice", "cover"])
        value = self.owner.prepare_bind(shared.wire(capability), epoch=1, runtime=self.runtime)
        self.owner.accept_bind(shared.wire(value), epoch=1, runtime=self.runtime)
        self.owner.accept_cover_features(self.owner.channel, 1)

    async def asyncSetUp(self):
        await shared.NumberOwnerTests.asyncSetUp(self)
        self.hass.states.items.pop(self.state.entity_id)
        self.state.entity_id = "cover.test"
        self.state.state = "closed"
        self.state.attributes = {"supported_features": 11, "current_position": 0}
        self.hass.states.items[self.state.entity_id] = self.state
        self.card.update(entity_id=self.state.entity_id, action={"kind": "control", "control": "cover"})
        self.hass.services.names.update({"cover.open_cover", "cover.stop_cover", "cover.close_cover"})
        original = self.hass.services.async_call

        async def service(*args, **kwargs):
            await original(*args, **kwargs)
            if self.apply and args[0] == "cover":
                state, position = {"open_cover": ("opening", 0), "close_cover": ("closing", 100),
                                   "stop_cover": ("open", 40)}[args[1]]
                self.change(state, current_position=position)

        self.hass.services.async_call = service

    async def open(self, seq=1, control="cover"):
        return await shared.NumberOwnerTests.open(self, seq, control)

    def command(self, seq=1, operation="open", **changes):
        selected = self.owner._selection
        return codec.envelope("command", **selected.identity, command_seq=seq, op=operation,
                              expected_state_generation=selected.domain_state[2]) | changes

    async def test_open_reverse_close_stop_have_one_exact_service_and_source_before_terminal(self):
        grant = await self.open()
        self.assertEqual((grant["cover_state"], grant["position"], grant["available"]), ("closed", 0, True))
        command = self.command()
        await self.send(command)
        await self.send(command)
        self.assertEqual(len(self.hass.services.calls), 1)
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        await self.send(self.command(2, "close"))
        await self.send(self.command(3, "stop"))
        self.assertEqual([args for args, _ in self.hass.services.calls], [
            ("cover", "open_cover", {"entity_id": "cover.test"}),
            ("cover", "close_cover", {"entity_id": "cover.test"}),
            ("cover", "stop_cover", {"entity_id": "cover.test"})])
        self.assertTrue(all(kwargs["context"] is self.user for _, kwargs in self.hass.services.calls))
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assert_terminal_order()

    async def test_partial_open_and_unknown_position_do_not_invent_full_open_noop(self):
        for position in (50, None):
            self.change("open", current_position=position)
            await self.open(1 if position == 50 else 2)
            self.apply = False
            await self.send(self.command())
            self.assertEqual(self.results()[-1]["status"], "not_confirmed")
            await self.owner.async_close()
        self.assertEqual(len(self.hass.services.calls), 2)

    async def test_observed_endpoints_and_current_movement_are_idempotent(self):
        for seq, state, position, operation in [(1, "open", 100, "open"), (2, "closed", 0, "close"),
                                                 (3, "opening", 30, "open"), (4, "closing", 30, "close"),
                                                 (5, "open", 30, "stop")]:
            self.change(state, current_position=position)
            await self.open(seq)
            await self.send(self.command(operation=operation))
            self.assertEqual(self.results()[-1]["status"], "already_matched")
            await self.owner.async_close()
        self.assertEqual(self.hass.services.calls, [])

    async def test_unknown_and_unavailable_have_no_position_and_cannot_dispatch(self):
        for seq, state in enumerate(("unknown", "unavailable"), 1):
            self.change(state, current_position=50)
            grant = await self.open(seq)
            self.assertEqual((grant["cover_state"], grant["available"], grant["position"]), ("unknown", False, None))
            await self.send(self.command())
            self.assertEqual(self.results()[-1]["reason"], "stale_state")
            await self.owner.async_close()
        self.assertEqual(self.hass.services.calls, [])

    async def test_value_ABA_while_permission_pending_rejects_even_same_final_state(self):
        await self.open()
        self.auth_gate, self.auth_entered = asyncio.Event(), asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("open", current_position=30)
        self.change("closed", current_position=0)
        self.assertEqual(self.owner._selection.domain_state[2], 3)
        self.auth_gate.set()
        await asyncio.wait_for(self.owner._selection.command.task, .4)
        self.assertEqual(self.hass.services.calls, [])
        self.assertEqual(self.results()[-1]["reason"], "stale_state")

    async def test_metadata_ABA_during_open_authorization_retires_capture(self):
        self.auth_gate = asyncio.Event()
        task = asyncio.create_task(self.open())
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        self.change("closed", supported_features=3)
        self.change("closed", supported_features=11)
        self.auth_gate.set()
        self.assertIsNone(await task)
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_capability_loss_and_unnegotiated_kind_never_fall_back(self):
        await self.open()
        self.change("closed", supported_features=3)
        self.assertIsNone(self.owner._selection)
        self.owner.control_kinds = ("light", "number", "choice")
        with self.assertRaises(codec.ProtocolError):
            await self.open(2)
        self.assertEqual(self.hass.services.calls, [])

    async def test_shared_service_fence_survives_cover_to_light_handoff(self):
        await self.open()
        self.service_gate = asyncio.Event()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.service_entered.wait(), .2)
        await self.owner.async_close()
        self.card.update(entity_id="light.test", action={"kind": "control", "control": "light"})
        await self.open(2, "light")
        value = codec.envelope("command", **self.owner._selection.identity, command_seq=1, op="turn_on")
        await self.send(value)
        self.assertEqual(len(self.hass.services.calls), 1)
        self.assertEqual(self.results()[-1]["reason"], "busy")

    async def test_service_registry_loss_without_state_event_rejects_before_dispatch(self):
        await self.open()
        value = self.command()
        self.hass.services.names.remove("cover.open_cover")
        with self.assertRaisesRegex(codec.ProtocolError, "capabilities_changed"):
            await self.owner.async_handle(shared.wire(value), self.user)
        self.assertEqual(self.hass.services.calls, [])


class CoverModelTests(unittest.TestCase):
    def test_explicit_shape_roundtrip_and_negotiated_projection_have_no_legacy_fallback(self):
        card = base.card(entity="cover.test", action={"kind": "control", "control": "cover"})
        document = base.document([card]) | {"version": 3}
        self.assertEqual(base.layout.import_layout(base.layout.export_layout(document), 9)["cards"], [card])
        state = base.State("cover.test", "open", {"supported_features": 11, "current_position": 40})
        hass, _ = base.environment(states=[state], services=["cover.open_cover", "cover.close_cover", "cover.stop_cover"])
        passive = base.cards.presentation_payload(hass, [card], press_enabled_supported=True)["cards"][2]
        self.assertNotIn("control_kind", passive)
        self.assertIs(passive["press_enabled"], False)
        active = base.cards.presentation_payload(hass, [card], cover_control_supported=True)["cards"][2]
        self.assertEqual(active["control_kind"], "cover")
        self.assertIsNone(base.cards.resolve_action(hass, card))
        for change in ({"type": "sensor"}, {"entity_id": "light.test"}):
            with self.assertRaises(base.layout.LayoutError):
                base.layout.validate_layout(document | {"cards": [card | change]})
