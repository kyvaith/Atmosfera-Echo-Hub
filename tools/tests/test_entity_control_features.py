"""Optional typed feature echo never changes or weakens the v1 control codec."""
import importlib
import json
from types import SimpleNamespace as NS
import unittest

import test_entity_control as generic

features = importlib.import_module("_atmosfera_test.entity_control_features")
transport = generic.integration.transport


def response(value):
    return NS(success=True, response_data=json.dumps(value, separators=(",", ":")).encode())


class FeatureCodecTests(unittest.TestCase):
    def test_exact_query_and_echo_and_strict_failure_shapes(self):
        query = {"v": 1, "type": features.TYPE, "cover_stop_version": 1}
        echo = query | {"accepted": True, "channel": "a" * 32}
        self.assertEqual(features.decode_features(response(query)), query)
        self.assertEqual(features.decode_features(response(echo), bind=True), echo)
        rejected = query | {"accepted": False, "channel": "", "cover_stop_version": 0}
        self.assertEqual(features.decode_features(response(rejected), bind=True), rejected)
        for value, bind in [(query | {"v": True}, False), (query | {"cover_stop_version": True}, False),
                            (query | {"cover_stop_version": 2}, False), (query | {"extra": 0}, False),
                            (echo | {"channel": "A" * 32}, True), (echo | {"accepted": 1}, True),
                            (echo | {"cover_stop_version": 0}, True), (rejected | {"channel": "a" * 32}, True),
                            ([], False)]:
            with self.subTest(value=value), self.assertRaises(features.ProtocolError):
                features.decode_features(response(value), bind=bind)
        for raw in (b'{"v":1,"v":1,"type":"entity_control_features_v1","cover_stop_version":1}',
                    b'\xff', b' ' * 513, b'{"v":1,"type":"entity_control_features_v1","cover_stop_version":NaN}'):
            with self.assertRaises(features.ProtocolError):
                features.decode_features(NS(success=True, response_data=raw))


class FeatureTransportTests(unittest.IsolatedAsyncioTestCase):
    def bridge(self, mode="ok"):
        bridge = generic.NumberModelTransportTests().generic_bridge()
        original = bridge.runtime.client.execute_service
        arg = transport.UserServiceArgType
        support = transport.SupportsResponseType.ONLY
        bridge.services["entity_control_get_features"] = NS(name="entity_control_get_features", args=[], supports_response=support)
        bridge.services["entity_control_bind_features"] = NS(name="entity_control_bind_features", args=[
            NS(name="channel", type=arg.STRING), NS(name="cover_stop_version", type=arg.INT)], supports_response=support)
        if mode == "missing":
            del bridge.services["entity_control_get_features"]
        if mode == "wrong_contract":
            bridge.services["entity_control_bind_features"].args = None

        async def execute(action, data, **kwargs):
            if action.name in {"entity_control_get_features", "entity_control_bind_features"}:
                bridge.calls.append((action.name, dict(data), kwargs))
                if mode == "exception":
                    raise RuntimeError("isolated feature service failure")
                value = {"v": 1, "type": features.TYPE, "cover_stop_version": 0 if mode == "off" else 1}
                if action.name.endswith("bind_features"):
                    value.update(accepted=True, channel="f" * 32 if mode == "wrong_channel" else data["channel"])
                    if mode == "epoch_changed":
                        bridge._connection_epoch += 1
                        bridge._light_control.invalidate_connection()
                if mode == "bad_version":
                    value["cover_stop_version"] = True
                return response(value)
            result = await original(action, data, **kwargs)
            if action.name == "entity_control_get_status":
                value = json.loads(result.response_data)
                value["control_kinds"].append("cover")
                return response(value)
            return result

        bridge.runtime.client.execute_service = execute
        return bridge

    async def test_exact_current_channel_echo_is_required_for_cover_readiness(self):
        for mode in ("ok", "missing", "wrong_contract", "exception", "off", "wrong_channel", "bad_version"):
            with self.subTest(mode=mode):
                bridge = self.bridge(mode)
                control = bridge._light_control
                try:
                    self.assertTrue(await control.async_negotiate())
                    self.assertTrue(control.number_supported)
                    self.assertIs(control.cover_supported, mode == "ok")
                    self.assertEqual(control.status()["cover_stop_version"], int(mode == "ok"))
                    control.invalidate_connection()
                    self.assertFalse(control.cover_supported)
                finally:
                    await control.async_shutdown()

    async def test_old_runtime_echo_cannot_enable_features_on_a_new_epoch(self):
        bridge = self.bridge("epoch_changed")
        try:
            self.assertFalse(await bridge._light_control.async_negotiate())
            self.assertFalse(bridge._light_control.supported)
            self.assertEqual(bridge._light_control.owner.cover_stop_version, 0)
        finally:
            await bridge._light_control.async_shutdown()
