"""Check the keyed catalog and HA authorization for a doorbell preview."""

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

import test_ha_layout as host

controller = host.controller


def bridge():
    bridge = host.BridgeTests().bridge()
    bridge.device_id = "atmosfera-device"
    bridge.hass.states = SimpleNamespace(get=lambda entity: SimpleNamespace(state="idle"))
    bridge.sources = [
        controller.CameraSource("camera.door", "Door", "https://local/door?token=first"),
        controller.CameraSource("camera.other", "Other", "https://local/other"),
    ]
    bridge.camera_entity_ids = ["camera.door", "camera.other"]
    bridge.current_option = "Door"
    bridge.available = True
    bridge._push_lock = asyncio.Lock()
    bridge._notify_listeners = lambda: None
    return bridge


def test_key_survives_reorder_rename_and_signed_url_rotation():
    async def scenario():
        owner = bridge()
        newer = controller.CameraSource("camera.door", "New label", "https://local/door?token=second")
        owner._async_build_sources = AsyncMock(return_value=[owner.sources[1], newer])
        keyed_action, select_action = object(), object()
        owner._find_api_action = {
            controller.API_ACTION_SET_KEYED_SOURCES: keyed_action,
            controller.API_ACTION_SELECT_SOURCE: select_action,
        }.get
        execute = AsyncMock(return_value=SimpleNamespace(success=True, response_data=b'{"accepted":true}'))
        owner.esphome_entry.runtime_data.client.execute_service = execute
        old_key = owner.sources[0].key

        assert await owner._async_push_sources()

        args, kwargs = execute.await_args_list[0]
        assert args[0] is keyed_action and kwargs["return_response"]
        sources = json.loads(args[1]["payload"])["sources"]
        assert [source["key"] for source in sources] == [owner.sources[0].key, old_key]
        assert owner.current_option == newer.name
        assert execute.await_args_list[1].args == (select_action, {"index": 1})

    asyncio.run(scenario())


def test_doorbell_checks_access_and_never_sends_a_camera_url():
    async def scenario():
        owner = bridge()
        owner._notifications = controller.NotificationTransport(owner)
        owner._find_api_action = {
            controller.API_ACTION_DOORBELL_PREVIEW: SimpleNamespace(
                supports_response=controller.SupportsResponseType.ONLY
            )
        }.get
        execute = AsyncMock(return_value=SimpleNamespace(success=True, response_data=b'{"status":"busy"}'))
        owner.esphome_entry.runtime_data.client.execute_service = execute
        registry = SimpleNamespace(async_get_entity_id=lambda *args: "notify.atmosfera")
        with patch.object(controller.er, "async_get", return_value=registry):
            with patch.object(controller, "authorize_ha_context", AsyncMock(side_effect=[True, False])):
                with pytest.raises(controller.HomeAssistantError, match="denied"):
                    await owner.async_doorbell_preview("camera.door", 25, "ring", object())
            with pytest.raises(controller.HomeAssistantError, match="allow-list"):
                await owner.async_doorbell_preview("camera.unlisted", 25, "ring", object())
            execute.assert_not_awaited()
            with patch.object(controller, "authorize_ha_context", AsyncMock(return_value=True)):
                assert await owner.async_doorbell_preview("camera.door", 25, "ring", object()) == {"status": "busy"}

        payload = execute.await_args.args[1]
        assert set(payload) == {"source_key", "event_id", "duration_seconds"}
        assert payload["source_key"] == owner.sources[0].key
        assert payload["duration_seconds"] == 25

    asyncio.run(scenario())
