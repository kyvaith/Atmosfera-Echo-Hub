"""Negotiated known-empty choice is distinct from missing or unavailable."""
import asyncio
import unittest

import test_fan_preset_control as fan


class EmptyChoiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.fixture = fan.FanPresetOwnerTests()
        await self.fixture.asyncSetUp()
        self.f = self.fixture.f
        self.f.state.attributes["preset_mode"] = None

    async def asyncTearDown(self):
        await self.fixture.asyncTearDown()

    async def send(self, command):
        f = self.f
        result = await f.owner.async_handle(f.owner._encode(command), f.user)
        if f.owner._selection and f.owner._selection.command:
            await asyncio.wait_for(f.owner._selection.command.task, .5)
        return result

    def negotiate(self):
        self.f.owner.accept_empty_choice_features(self.f.owner.channel, 1)

    async def test_legacy_codec_stays_strict_and_old_peer_stays_unavailable(self):
        grant = await self.f.open()
        self.assertIsNone(grant["index"])
        self.assertIs(grant["available"], False)
        self.assertEqual(self.f.owner.empty_choice_version, 0)

    async def test_manual_apply_has_null_expected_index_and_exact_preset_service(self):
        self.negotiate()
        grant = await self.f.open()
        self.assertIsNone(grant["index"])
        self.assertIs(grant["available"], True)
        command = self.f.command(2)
        with self.assertRaises(fan.shared.codec.ProtocolError):
            fan.shared.codec.encode(command)
        self.assertIsNone(command["expected_index"])
        await self.send(command)
        self.assertEqual(len(self.f.hass.services.calls), 1)
        self.assertEqual(self.f.hass.services.calls[0][0],
                         ("fan", "set_preset_mode", {"entity_id": "fan.test", "preset_mode": " Żółty "}))
        self.assertEqual(self.f.results()[-1]["status"], "state_matches")

    async def test_public_service_ingress_is_structural_but_owner_remains_strict(self):
        self.negotiate()
        await self.f.open()
        command = self.f.command(2)
        payload = self.f.owner._encode(command)
        self.assertEqual(fan.shared.codec.decode_report(payload), command)
        # Service shape validation alone never grants the extension to a peer.
        with self.assertRaises(fan.shared.codec.ProtocolError):
            fan.shared.codec.decode(payload)
        for message in (self.f.outputs[0], fan.shared.codec.envelope("capability", enabled=True,
                        max_payload_bytes=2048, control_kinds=["light", "number", "choice"])):
            with self.assertRaises(fan.shared.codec.ProtocolError):
                fan.shared.codec.decode_report(self.f.owner._encode(message))

    async def test_missing_off_list_and_unavailable_never_become_manual(self):
        self.negotiate()
        for value, missing, power in ((None, True, "on"), ("absent", False, "on"),
                                      (None, False, "unavailable"), (None, False, "unknown")):
            self.f.state.state = power
            self.f.state.attributes["preset_mode"] = value
            if missing:
                self.f.state.attributes.pop("preset_mode")
            grant = await self.f.open(seq=1 if missing else 2 if value else 3 if power == "unavailable" else 4)
            self.assertIs(grant["available"], False)
            await self.f.owner.async_close("selection_changed")
        self.assertEqual(self.f.hass.services.calls, [])

    async def test_manual_ABA_while_authorizing_is_stale(self):
        self.negotiate()
        await self.f.open()
        self.f.auth_gate = asyncio.Event()
        self.f.auth_entered.clear()
        await self.f.owner.async_handle(self.f.owner._encode(self.f.command()), self.f.user)
        await asyncio.wait_for(self.f.auth_entered.wait(), .2)
        self.f.change("Eco")
        self.f.change(None)
        self.f.auth_gate.set()
        await asyncio.wait_for(self.f.owner._selection.command.task, .3)
        self.assertEqual(self.f.hass.services.calls, [])
        self.assertEqual(self.f.results()[-1]["reason"], "stale_state")

    async def test_new_channel_cannot_inherit_empty_selection_acceptance(self):
        self.negotiate()
        self.assertEqual(self.f.owner.empty_choice_version, 1)
        old = self.f.owner.channel
        self.f.owner.revoke_now("connection_lost", disconnect=True)
        self.f.bind()
        self.assertNotEqual(self.f.owner.channel, old)
        self.assertEqual(self.f.owner.empty_choice_version, 0)
        with self.assertRaises(fan.shared.codec.ProtocolError):
            self.f.owner.accept_empty_choice_features(old, 1)
