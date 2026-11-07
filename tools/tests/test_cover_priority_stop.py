"""One negotiated successor Stop; no real HA service or physical motor."""
import asyncio
import unittest

import test_cover_control as cover
import test_entity_control as shared


class CoverPriorityStopTests(cover.CoverOwnerTests):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.owner.accept_cover_features(self.owner.channel, 1)
        self.assertEqual(self.owner.cover_stop_version, 1)

    async def wait_for(self, predicate):
        async with asyncio.timeout(.3):
            while not predicate():
                await asyncio.sleep(.001)

    async def start_movement(self):
        await self.open()
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        return self.owner._selection.command

    async def stop(self, seq=2, **change):
        result = await self.owner.async_handle(shared.wire(self.command(seq, "stop", **change)), self.user)
        return result, self.owner._selection.command

    async def test_started_service_finishes_before_one_stop_and_never_replays_movement(self):
        self.service_gate = asyncio.Event()
        movement = await self.start_movement()
        await asyncio.wait_for(self.service_entered.wait(), .2)
        response, stop = await self.stop()
        self.assertEqual(response["status"], "pending")
        self.assertTrue(stop.priority)
        self.assertTrue(stop.predecessor_started)
        await asyncio.sleep(.005)
        self.assertEqual(len(self.hass.services.calls), 1)
        self.service_gate.set()
        await asyncio.wait_for(stop.task, .3)
        self.assertEqual([args[1] for args, _ in self.hass.services.calls], ["open_cover", "stop_cover"])
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assertEqual(self.results()[-1]["command_seq"], 2)
        self.assertEqual(movement.result["status"], "rejected")
        await self.owner.async_handle(shared.wire(self.command(2, "stop", expected_state_generation=1)), self.user)
        self.assertEqual(len(self.hass.services.calls), 2)

    async def test_pending_observation_does_not_delay_stop_or_claim_earlier_feedback(self):
        self.apply = False
        self.owner.state_timeout = .5
        movement = await self.start_movement()
        await self.wait_for(lambda: movement.result["status"] == "ha_accepted")
        self.assertTrue(movement.service_started)
        response, stop = await self.stop()
        await self.wait_for(lambda: len(self.hass.services.calls) == 2)
        self.assertTrue(stop.predecessor_started)
        self.assertEqual([args[1] for args, _ in self.hass.services.calls], ["open_cover", "stop_cover"])
        # Stationary state from before Stop dispatch cannot confirm it.
        self.assertNotIn(stop.result["status"], {"state_matches", "already_matched"})
        self.change("open", current_position=40)
        await self.owner.async_state_changed()
        await asyncio.wait_for(stop.task, .3)
        self.assertEqual(stop.result["status"], "state_matches")

    async def test_unsent_motion_is_canceled_without_any_actuator_service(self):
        movement = await self.start_movement()
        response, stop = await self.stop()
        await asyncio.wait_for(stop.task, .3)
        self.assertFalse(movement.service_started)
        self.assertEqual(stop.result["status"], "already_matched")
        self.assertEqual(self.hass.services.calls, [])

    async def test_another_stop_is_busy_and_does_not_replace_the_only_successor(self):
        self.service_gate = asyncio.Event()
        await self.start_movement()
        await asyncio.wait_for(self.service_entered.wait(), .2)
        _, stop = await self.stop()
        response, current = await self.stop(3)
        self.assertEqual((response["status"], response["reason"]), ("rejected", "busy"))
        self.assertIs(current, stop)
        self.service_gate.set()
        await asyncio.wait_for(stop.task, .3)
        self.assertEqual(len(self.hass.services.calls), 2)

    async def test_stale_stop_does_not_cancel_the_admitted_movement(self):
        self.service_gate = asyncio.Event()
        movement = await self.start_movement()
        await asyncio.wait_for(self.service_entered.wait(), .2)
        response, current = await self.stop(expected_state_generation=99)
        self.assertEqual((response["status"], response["reason"]), ("rejected", "stale_state"))
        self.assertIs(current, movement)
        self.assertFalse(movement.task.done())

    async def test_slow_predecessor_timeout_keeps_fence_and_has_no_late_stop(self):
        self.service_gate = asyncio.Event()
        await self.start_movement()
        await asyncio.wait_for(self.service_entered.wait(), .2)
        _, stop = await self.stop()
        await asyncio.wait_for(stop.task, .3)
        self.assertEqual((stop.result["status"], stop.result["reason"]), ("not_confirmed", "service_timeout"))
        self.assertEqual(len(self.hass.services.calls), 1)
        self.service_gate.set()
        await asyncio.sleep(.01)
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_close_during_predecessor_wait_never_dispatches_stop_into_later_view(self):
        self.service_gate = asyncio.Event()
        await self.start_movement()
        await asyncio.wait_for(self.service_entered.wait(), .2)
        await self.stop()
        await self.owner.async_close()
        self.service_gate.set()
        await asyncio.sleep(.01)
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_features_are_scoped_to_a_current_bound_channel_and_reset_on_rebind(self):
        channel = self.owner.channel
        for other, version in (("f" * 32, 1), (channel, True), (channel, 0), (channel, 2)):
            with self.assertRaises(cover.codec.ProtocolError):
                self.owner.accept_cover_features(other, version)
        await self.owner.async_disconnect()
        self.assertEqual(self.owner.cover_stop_version, 0)
        self.bind()
        # This fixture binds features explicitly; a raw v1-only rebind does not.
        await self.owner.async_disconnect()
        capability = cover.codec.envelope("capability", enabled=True, max_payload_bytes=2048,
                                         control_kinds=["light", "number", "cover"])
        value = self.owner.prepare_bind(shared.wire(capability), epoch=1, runtime=self.runtime)
        self.owner.accept_bind(shared.wire(value), epoch=1, runtime=self.runtime)
        self.assertEqual(self.owner.cover_stop_version, 0)
        with self.assertRaisesRegex(cover.codec.ProtocolError, "unsupported"):
            await self.open()

    async def test_cancellation_resistant_authorization_never_dispatches_old_movement(self):
        await self.open()
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()

        async def stubborn(*_):
            self.auth_entered.set()
            while not self.auth_gate.is_set():
                try:
                    await self.auth_gate.wait()
                except asyncio.CancelledError:
                    continue
            return True

        self.owner.authorize = stubborn
        await self.owner.async_handle(shared.wire(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), .2)
        _, stop = await self.stop()
        await asyncio.wait_for(stop.task, .3)
        self.assertEqual((stop.result["status"], stop.result["reason"]), ("rejected", "busy"))
        self.auth_gate.set()
        await asyncio.sleep(.01)
        self.assertEqual(self.hass.services.calls, [])

    async def test_permission_loss_after_predecessor_completes_does_not_dispatch_stop(self):
        self.service_gate = asyncio.Event()
        await self.start_movement()
        await asyncio.wait_for(self.service_entered.wait(), .2)
        _, stop = await self.stop()
        self.allowed = False
        self.service_gate.set()
        await asyncio.wait_for(stop.task, .3)
        self.assertEqual(stop.result["reason"], "unauthorized")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_stop_intent_survives_position_changes_but_future_generation_is_invalid(self):
        self.apply = False
        self.owner.state_timeout = .5
        movement = await self.start_movement()
        await self.wait_for(lambda: movement.result["status"] == "ha_accepted")
        self.change("opening", current_position=30)
        self.change("opening", current_position=40)
        _, stop = await self.stop(expected_state_generation=1)
        await self.wait_for(lambda: len(self.hass.services.calls) == 2)
        self.assertEqual(stop.prepared[2], self.owner._selection.domain_state[2])
        self.change("open", current_position=40)
        await self.owner.async_state_changed()
        await asyncio.wait_for(stop.task, .3)
        self.assertEqual(stop.result["status"], "state_matches")


if __name__ == "__main__":
    unittest.main()
