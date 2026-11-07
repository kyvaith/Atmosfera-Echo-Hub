"""Connection fencing, replay rejection, authorization and persistence order."""

import asyncio
import importlib
import json
import types
import unittest
from unittest.mock import AsyncMock, patch

import test_ha_layout as fixture

transport = importlib.import_module("_atmosfera_test.notification_transport")


class NotificationTransportTests(unittest.IsolatedAsyncioTestCase):
    def owner(self, modern=False, actions=False):
        self.sent = []
        self.saved = []

        async def send(_action, data):
            self.sent.append(json.loads(data["payload"]))

        bridge = types.SimpleNamespace(
            hass=types.SimpleNamespace(
                config=types.SimpleNamespace(language="pl"),
                entity_registry=types.SimpleNamespace(
                    async_get_entity_id=lambda *_: "notify.atmosfera"
                ),
            ),
            entry=types.SimpleNamespace(entry_id="test"),
            _connection_epoch=1,
            device_id="device",
            device_locale=None,
            tile_device_available=True,
            esphome_entry=types.SimpleNamespace(
                runtime_data=types.SimpleNamespace(
                    client=types.SimpleNamespace(execute_service=send)
                )
            ),
            _find_api_action=lambda name: (
                object()
                if name == "notification_sync"
                or (modern and name == "notification_sync_v2")
                or (actions and name == "notification_sync_v3")
                else None
            ),
        )
        owner = transport.NotificationTransport(bridge)

        async def save(data):
            self.saved.append(data)

        owner.store = types.SimpleNamespace(async_save=save)
        return owner

    def request(self, owner, seq=1, op="page", **extra):
        return {
            "v": 1,
            "channel": owner.channel,
            "seq": seq,
            "op": op,
            "offset": 0,
            **extra,
        }

    async def test_persist_before_delivery_and_page_bound(self):
        owner = self.owner()
        await owner.add("A", "B")
        self.assertEqual(len(self.saved[0]), 1)
        self.assertEqual(self.saved[0][0]["id"], self.sent[0]["rows"][0]["id"])
        self.assertEqual(self.sent[0]["seq"], 0)
        self.assertEqual(len(owner.channel), 32)

    async def test_delivery_capability_keeps_legacy_and_modern_windows_separate(self):
        old = self.owner()
        await old.add("Old", "Body")
        self.assertEqual(self.sent[-1]["v"], 1)
        self.assertNotIn("created", self.sent[-1]["rows"][0])
        modern = self.owner(modern=True)
        for index in range(20):
            modern.history.add(str(index), "Body")
        await modern.push()
        request = self.request(modern, v=2, offset=5)
        with patch.object(
            transport, "authorize_ha_context", AsyncMock(return_value=True)
        ):
            await modern.report(request, object())
        self.assertEqual(self.sent[-1]["v"], 2)
        self.assertEqual(self.sent[-1]["offset"], 5)
        self.assertIn("created", self.sent[-1]["rows"][0])

    async def test_permissions_checked_before_mutation_or_reply(self):
        owner = self.owner()
        await owner.add("A", "B")
        data = self.request(owner, op="dismiss", id=owner.history.records[0].id)
        with patch.object(
            transport, "authorize_ha_context", AsyncMock(return_value=False)
        ) as authorize:
            await owner.report(data, object())
        self.assertEqual(len(self.sent), 1)
        self.assertEqual(len(owner.history.records), 1)
        self.assertEqual(authorize.await_args.args[-1], "notify.atmosfera")

    async def test_duplicate_old_channel_and_disconnect_cannot_delete(self):
        owner = self.owner()
        await owner.add("A", "B")
        old = self.request(owner, op="dismiss", id=owner.history.records[0].id)
        with patch.object(
            transport, "authorize_ha_context", AsyncMock(return_value=True)
        ):
            owner.bridge._connection_epoch += 1
            await owner.report(old, object())
            self.assertEqual(len(owner.history.records), 1)
            await owner.push()
            self.assertNotEqual(old["channel"], owner.channel)
            await owner.report(old, object())
            current = self.request(owner, op="dismiss", id=owner.history.records[0].id)
            await owner.report(current, object())
            replies = len(self.sent)
            await owner.report(current, object())
        self.assertEqual(len(owner.history.records), 0)
        self.assertEqual(len(self.sent), replies)

    async def test_detail_reads_full_text_without_changing_archive(self):
        owner = self.owner()
        await owner.add("Tytuł", "Zażółć " * 50)
        original = owner.history.dump()
        with patch.object(
            transport, "authorize_ha_context", AsyncMock(return_value=True)
        ):
            await owner.report(
                self.request(owner, op="open", id=original[0]["id"]), object()
            )
        self.assertEqual(self.sent[-1]["detail"]["message"], original[0]["message"])
        self.assertEqual(owner.history.dump(), original)

    async def test_failure_during_delivery_keeps_durable_notice(self):
        owner = self.owner()
        owner.bridge.esphome_entry.runtime_data.client.execute_service = AsyncMock(
            side_effect=TimeoutError
        )
        await owner.add("A", "B")
        self.assertEqual(len(self.saved[-1]), 1)
        self.assertEqual(len(owner.history.records), 1)

    async def test_doorbell_detail_action_expiry_permission_and_replay(self):
        owner = self.owner(actions=True)
        camera, event = "camera.front", "f" * 32
        owner.bridge.camera_entity_ids = [camera]
        open_camera = owner.bridge.async_request_camera_preview = AsyncMock(
            return_value="opened"
        )
        authorize = AsyncMock(return_value=True)
        with patch.object(transport, "monotonic", return_value=500) as clock:
            self.assertEqual(
                await owner.add_doorbell(camera, 35, event), "notification_saved"
            )
            self.assertEqual(await owner.add_doorbell(camera, 35, event), "duplicate")
            record_id = self.saved[0][0]["id"]
            self.assertNotIn("action", self.saved[0][0])
            self.assertNotIn(camera, json.dumps(self.sent[0]))
            data = self.request(owner, v=3, op="open", id=record_id)
            with patch.object(transport, "authorize_ha_context", authorize):
                await owner.report(data, object())
                self.assertEqual(
                    self.sent[-1]["detail"]["action"],
                    {"type": "camera_preview", "remaining": 180},
                )
                activate = dict(data, seq=2, op="activate")
                authorize.side_effect = [True, False]
                await owner.report(activate, object())
                open_camera.assert_not_awaited()
                authorize.side_effect = None
                await owner.report(dict(activate, seq=3), object())
                open_camera.assert_awaited_once_with(camera, 35, event, expires=680)
                await owner.report(dict(activate, seq=3), object())
                await owner.report(dict(activate, seq=4), object())
                open_camera.assert_awaited_once()
                await owner.add_doorbell(camera, 35, "a" * 32)
                expired_id = owner.history.records[0].id
                clock.return_value = 681
                await owner.report(dict(activate, seq=5, id=expired_id), object())
                open_camera.assert_awaited_once()
                await owner.report(dict(data, seq=6, id=expired_id), object())
                self.assertNotIn("action", self.sent[-1]["detail"])
                self.assertEqual(len(owner.history.records), 2)


if __name__ == "__main__":
    unittest.main()
