"""Choice policy uses one shared lease, authorization slot and service fence."""

import asyncio
from copy import deepcopy
import importlib
from types import SimpleNamespace as NS
import unittest

import test_ha_layout as base

policy = importlib.import_module("_atmosfera_test.entity_control")
codec = importlib.import_module("_atmosfera_test.entity_control_codec")
light = importlib.import_module("_atmosfera_test.light_control")


class ChoiceOwnerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.state = base.State(
            "input_select.test", "Eco", {"options": ["Eco", "Komfort", " Boost "]}
        )
        self.hass, _ = base.environment(
            states=[self.state],
            services=["input_select.select_option", "select.select_option"],
        )
        self.card = base.card(
            entity=self.state.entity_id, action={"kind": "control", "control": "choice"}
        )
        self.runtime, self.user = object(), NS(user_id="caller")
        self.context = light.LightContext(1, self.runtime, True, 3, 4, 4, (self.card,))
        self.outputs, self.serial = [], 0
        self.allowed, self.apply = True, True
        self.auth_gate = self.service_gate = None
        self.auth_entered, self.service_entered = asyncio.Event(), asyncio.Event()

        async def emit(value, *_):
            self.outputs.append(deepcopy(value))

        async def authorize(*_):
            self.auth_entered.set()
            if self.auth_gate:
                await self.auth_gate.wait()
            return self.allowed

        async def service(*args, **kwargs):
            self.hass.services.calls.append((args, kwargs))
            self.service_entered.set()
            if self.service_gate:
                await self.service_gate.wait()
            if self.apply:
                self.change(args[2]["option"])

        def token():
            self.serial += 1
            return f"{self.serial:032x}"

        self.hass.services.async_call = service
        self.owner = policy.EntityControlOwner(
            self.hass,
            lambda: self.context,
            emit,
            authorize,
            token_factory=token,
            service_timeout=0.03,
            state_timeout=0.03,
            renewal_interval=100,
            authorization_timeout=0.2,
        )
        self.owner.set_mode("entity")
        self.bind()

    def bind(self, kinds=None):
        cap = codec.envelope(
            "capability",
            enabled=True,
            max_payload_bytes=2048,
            control_kinds=kinds or ["light", "number", "choice"],
        )
        value = self.owner.prepare_bind(
            codec.encode(cap), epoch=1, runtime=self.runtime
        )
        self.owner.accept_bind(codec.encode(value), epoch=1, runtime=self.runtime)

    async def asyncTearDown(self):
        if self.auth_gate:
            self.auth_gate.set()
        if self.service_gate:
            self.service_gate.set()
        await self.owner.async_unload()
        await asyncio.sleep(0.001)

    async def open(self, seq=1):
        value = codec.envelope(
            "open",
            channel=self.owner.channel,
            open_seq=seq,
            slot=2,
            card_id="card-2",
            revision=4,
            control_kind="choice",
        )
        return await self.owner.async_handle(codec.encode(value), self.user)

    def command(self, target=1, **updates):
        selected = self.owner._selection
        return (
            codec.envelope(
                "command",
                **selected.identity,
                command_seq=1,
                op="choose",
                target_index=target,
                expected_index=selected.domain_state[1],
                expected_state_generation=selected.domain_state[3],
            )
            | updates
        )

    async def send(self, value):
        result = await self.owner.async_handle(codec.encode(value), self.user)
        selected = self.owner._selection
        task = selected.command.task if selected and selected.command else None
        if task:
            await asyncio.wait_for(task, 0.5)
        return result

    def change(self, value, **attributes):
        self.state.state = value
        self.state.attributes.update(attributes)
        return self.owner.observe_state_event(
            NS(data={"entity_id": self.state.entity_id, "new_state": self.state})
        )

    def results(self):
        return [value for value in self.outputs if value["kind"] == "result"]

    def assert_terminal_order(self):
        for index, value in enumerate(self.outputs):
            if value["kind"] == "result" and value["status"] in {
                "rejected",
                "not_confirmed",
                "state_matches",
                "already_matched",
            }:
                previous = self.outputs[index - 1]
                self.assertEqual(
                    (previous["kind"], previous["token"], previous["state_seq"]),
                    ("state", value["token"], value["state_seq"]),
                )

    async def test_grant_and_one_exact_absolute_command_preserve_context_and_result_order(
        self,
    ):
        grant = await self.open()
        self.assertEqual(
            (grant["options"], grant["index"], grant["state_generation"]),
            (["Eco", "Komfort", " Boost "], 0, 1),
        )
        await self.send(self.command(2))
        self.assertEqual(len(self.hass.services.calls), 1)
        args, kwargs = self.hass.services.calls[0]
        self.assertEqual(
            args,
            (
                "input_select",
                "select_option",
                {"entity_id": self.state.entity_id, "option": " Boost "},
            ),
        )
        self.assertIs(kwargs["context"], self.user)
        self.assertEqual(self.state.state, " Boost ")
        self.assertEqual(self.results()[-1]["status"], "state_matches")
        self.assert_terminal_order()

    async def test_select_domain_uses_its_own_service_and_exact_unicode(self):
        del self.hass.states.items[self.state.entity_id]
        self.state.entity_id = self.card["entity_id"] = "select.test"
        self.hass.states.items[self.state.entity_id] = self.state
        self.state.attributes["options"] = ["Eco", "Żółty"]
        await self.open()
        await self.send(self.command())
        self.assertEqual(
            self.hass.services.calls[0][0],
            (
                "select",
                "select_option",
                {"entity_id": "select.test", "option": "Żółty"},
            ),
        )

    async def test_noop_and_duplicate_do_not_create_a_second_service(self):
        await self.open()
        await self.send(self.command(0))
        self.assertEqual(self.results()[-1]["status"], "already_matched")
        self.assertEqual(self.hass.services.calls, [])
        value = self.command(1, command_seq=2)
        await self.send(value)
        await self.send(value)
        self.assertEqual(len(self.hass.services.calls), 1)
        await self.send(value | {"target_index": 2})
        self.assertEqual(self.results()[-1]["reason"], "sequence_conflict")

    async def test_old_generic_capability_cannot_grant_choice(self):
        self.owner.revoke_now("connection_lost", disconnect=True)
        self.owner.set_mode("entity")
        self.bind(["light", "number"])
        with self.assertRaisesRegex(codec.ProtocolError, "unsupported"):
            await self.open()
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.hass.services.calls, [])

    async def test_unknown_state_is_nullable_and_cannot_apply_a_fabricated_zero(self):
        self.change("unknown")
        grant = await self.open()
        self.assertIsNone(grant["index"])
        self.assertIs(grant["available"], False)
        await self.send(self.command(expected_index=0))
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assertEqual(self.hass.services.calls, [])

    async def test_state_ABA_during_authorization_rejects_captured_generation(self):
        await self.open()
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        value = self.command()
        await self.owner.async_handle(codec.encode(value), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), 0.2)
        self.change("Komfort")
        self.change("Eco")
        self.auth_gate.set()
        task = self.owner._selection.command.task
        await asyncio.wait_for(task, 0.3)
        self.assertEqual(self.owner._selection.domain_state[3], 3)
        self.assertEqual(self.results()[-1]["reason"], "stale_state")
        self.assertEqual(self.hass.services.calls, [])
        self.assert_terminal_order()

    async def test_option_list_ABA_revokes_opening_before_authorization_returns(self):
        self.auth_gate = asyncio.Event()
        task = asyncio.create_task(self.open())
        await asyncio.wait_for(self.auth_entered.wait(), 0.2)
        self.change("Eco", options=["Eco", "Other"])
        self.change("Eco", options=["Eco", "Komfort", " Boost "])
        self.auth_gate.set()
        await task
        self.assertIsNone(self.owner._selection)
        self.assertFalse(any(v["kind"] == "grant" for v in self.outputs))
        self.assertEqual(self.hass.services.calls, [])

    async def test_option_list_change_and_entity_removal_revoke_selected_token(self):
        await self.open()
        value = self.command()
        close = self.change("Eco", options=["Komfort", "Eco"])
        self.assertEqual(close["reason"], "capabilities_changed")
        self.assertIsNone(self.owner._selection)
        with self.assertRaises(codec.ProtocolError):
            await self.send(value)
        await self.open(seq=2)
        close = self.owner.observe_state_event(
            NS(data={"entity_id": self.state.entity_id, "new_state": None})
        )
        self.assertEqual(close["reason"], "entity_unavailable")
        self.assertEqual(self.hass.services.calls, [])

    async def test_live_service_removal_or_permission_denial_never_dispatches(self):
        await self.open()
        self.allowed = False
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["reason"], "unauthorized")
        self.assertEqual(self.hass.services.calls, [])
        self.hass.services.names.clear()
        with self.assertRaises(codec.ProtocolError):
            await self.send(self.command(command_seq=2))
        self.assertEqual(self.hass.services.calls, [])

    async def test_service_timeout_keeps_the_existing_single_service_fence(self):
        await self.open()
        self.service_gate = asyncio.Event()
        await self.send(self.command())
        self.assertEqual(self.results()[-1]["reason"], "service_timeout")
        await self.send(self.command(2, command_seq=2))
        self.assertEqual(self.results()[-1]["reason"], "busy")
        self.assertEqual(len(self.hass.services.calls), 1)

    async def test_changed_metadata_after_authorization_cannot_reinterpret_target(self):
        await self.open()
        self.auth_gate = asyncio.Event()
        self.auth_entered.clear()
        await self.owner.async_handle(codec.encode(self.command()), self.user)
        await asyncio.wait_for(self.auth_entered.wait(), 0.2)
        self.state.attributes["options"] = ["Eco", "Changed"]
        self.auth_gate.set()
        await asyncio.sleep(0.03)
        self.assertEqual(self.hass.services.calls, [])
        self.assertIsNone(self.owner._selection)
        self.assertEqual(self.outputs[-1]["reason"], "capabilities_changed")


if __name__ == "__main__":
    unittest.main()
