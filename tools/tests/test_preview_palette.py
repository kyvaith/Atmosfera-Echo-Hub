"""Preview palette parity and connection-scoped preference behavior; no live HA."""

from __future__ import annotations
from copy import deepcopy
import importlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import test_ha_layout as host

palette = importlib.import_module("_atmosfera_test.tile_palette")
FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures/native_tile_palette.json").read_text(
        encoding="utf-8"
    )
)


class PaletteTests(unittest.TestCase):
    def test_actual_native_role_oracle_all64_seeds(self):
        self.assertEqual(FIXTURE["schema"], "native_tile_palette_v1")
        self.assertEqual(len(FIXTURE["cases"]), 64)
        self.assertTrue(FIXTURE["origin"]["method_bodies_copied_verbatim"])
        for row in FIXTURE["cases"]:
            self.assertEqual(
                {
                    k: list(v)
                    for k, v in palette.derive_tile_palette(
                        int(row["seed"], 16)
                    ).items()
                },
                row["roles"],
            )

    def test_exact_threshold_and_bounded_seed(self):
        self.assertEqual(palette.derive_tile_palette(0x969696)["primary"][1], 0xFFFFFF)
        self.assertEqual(palette.derive_tile_palette(0x979797)["primary"][1], 0x071018)
        self.assertEqual(
            palette.derive_tile_palette(0)["primary_container"], (0x3A3A3A, 0xFFFFFF)
        )
        for value in (True, -1, 0x1000000, "AEE2FF", None):
            with self.assertRaises(ValueError):
                palette.derive_tile_palette(value)
        for value in ("#aee2ff", "aee2ff"):
            self.assertEqual(palette.observed_accent(value), "AEE2FF")
        for value in (
            True,
            17,
            None,
            "FFF",
            "ZZZZZZ",
            "0xAEE2FF",
            "AEE2FF" * 100,
            " AEE2FF",
            "AEE2FF ",
            " #AEE2FF",
            "#AEE2FF ",
            " aee2ff ",
        ):
            self.assertIsNone(palette.observed_accent(value))

    def test_stored_fallback_and_invalid_observation(self):
        _, entry = host.environment()
        entry.options["accent_color"] = "112233"
        entry.data["accent_color"] = "334455"
        self.assertEqual(host.panel._preview_accent(entry), 0x112233)
        entry.runtime_data = SimpleNamespace(observed_accent_color="AEE2FF")
        self.assertEqual(host.panel._preview_accent(entry), 0xAEE2FF)
        entry.runtime_data.observed_accent_color = "invalid"
        self.assertEqual(host.panel._preview_accent(entry), 0x112233)
        del entry.options["accent_color"]
        self.assertEqual(host.panel._preview_accent(entry), 0x334455)

    def test_legacy_wire_projection_retained(self):
        self.assertEqual(host.cards.derive_palette(0xAEE2FF)["secondary"][0], 0xDAFEFF)
        self.assertNotEqual(
            host.cards.derive_palette(0xAEE2FF), palette.derive_tile_palette(0xAEE2FF)
        )


class PreferenceTests(unittest.IsolatedAsyncioTestCase):
    async def bridge(self):
        bridge = host.BridgeTests().bridge()
        bridge._device_preference_client = None
        bridge.scheduled = []
        bridge.async_schedule_tile_push = lambda **kw: bridge.scheduled.append(kw)

        class Client:
            def __init__(self):
                self.callbacks = []
                self.queries = 0

            async def list_entities_services(self):
                self.queries += 1
                return [
                    SimpleNamespace(
                        key=77,
                        object_id="settings_accent_color",
                        name="Interface Accent Color",
                    )
                ], []

            def subscribe_states(self, cb):
                self.callbacks.append(cb)

        client = Client()
        bridge.esphome_entry.runtime_data.client = client
        await host.controller.CameraBridge._async_subscribe_device_preferences_locked(
            bridge
        )
        return bridge, client, Client

    async def test_observed_device_color_survives_hot_save_without_wire_change(self):
        bridge, client, _ = await self.bridge()
        client.callbacks[0](SimpleNamespace(key=77, state="#aee2ff"))
        self.assertEqual(bridge.observed_accent_color, "AEE2FF")
        self.assertEqual(len(client.callbacks), 1)
        bridge.entry.options["accent_color"] = "36BCF0"
        bridge.entry.options["home_layout"] = host.document([host.card()], revision=1)
        self.assertTrue(bridge.async_apply_tile_options())
        self.assertEqual(
            bridge.accent_color, "36BCF0"
        )  # Existing legacy wire semantics unchanged.
        self.assertEqual(bridge.observed_accent_color, "AEE2FF")
        bridge.entry.runtime_data = bridge
        self.assertEqual(host.panel._preview_accent(bridge.entry), 0xAEE2FF)
        self.assertFalse(bridge.hass.config_entries.updates)
        self.assertFalse(bridge.hass.services.calls)

    async def test_old_connection_callback_cannot_replace_observed_preview(self):
        bridge, first, Client = await self.bridge()
        old = first.callbacks[0]
        old(SimpleNamespace(key=77, state="AEE2FF"))
        second = Client()
        bridge.esphome_entry.runtime_data.client = second
        bridge._connection_epoch += 1
        self.assertIsNone(bridge.observed_accent_color)
        await host.controller.CameraBridge._async_subscribe_device_preferences_locked(
            bridge
        )
        self.assertIsNone(bridge.observed_accent_color)
        second.callbacks[0](SimpleNamespace(key=77, state="FBC8D5"))
        old(SimpleNamespace(key=77, state="000000"))
        self.assertEqual(bridge.observed_accent_color, "FBC8D5")
        bridge.esphome_entry.runtime_data.available = False
        self.assertIsNone(bridge.observed_accent_color)
        self.assertEqual((len(first.callbacks), len(second.callbacks)), (1, 1))

    async def test_same_client_info_epoch_retains_one_subscription_and_current_color(
        self,
    ):
        bridge, client, _ = await self.bridge()
        callback = client.callbacks[0]
        callback(SimpleNamespace(key=77, state="AEE2FF"))
        bridge._connection_epoch += 1
        await host.controller.CameraBridge._async_subscribe_device_preferences_locked(
            bridge
        )
        callback(SimpleNamespace(key=77, state="C8FBCF"))
        self.assertEqual(bridge.observed_accent_color, "C8FBCF")
        self.assertEqual((client.queries, len(client.callbacks)), (1, 1))
        callback(SimpleNamespace(key=77, state="invalid"))
        self.assertEqual(bridge.observed_accent_color, "C8FBCF")

    async def test_initial_invalid_callback_uses_stored_fallback(self):
        bridge, client, _ = await self.bridge()
        bridge.entry.options["accent_color"] = "112233"
        bridge.entry.runtime_data = bridge
        for value in ("invalid", " AEE2FF", "AEE2FF ", "#AEE2FF "):
            client.callbacks[0](SimpleNamespace(key=77, state=value))
            self.assertIsNone(bridge.observed_accent_color)
            self.assertEqual(host.panel._preview_accent(bridge.entry), 0x112233)
        self.assertEqual(len(client.callbacks), 1)
        self.assertFalse(bridge.hass.config_entries.updates)
        self.assertFalse(bridge.hass.services.calls)

    async def test_invalid_callbacks_retain_last_device_color(self):
        bridge, client, _ = await self.bridge()
        bridge.entry.options["accent_color"] = "112233"
        bridge.entry.runtime_data = bridge
        callback = client.callbacks[0]
        callback(SimpleNamespace(key=77, state="#aee2ff"))
        for value in ("invalid", " AEE2FF", "AEE2FF ", " #000000", "#000000 "):
            callback(SimpleNamespace(key=77, state=value))
            self.assertEqual(bridge.observed_accent_color, "AEE2FF")
            self.assertEqual(host.panel._preview_accent(bridge.entry), 0xAEE2FF)
        callback(SimpleNamespace(key=77, state="C8FBCF"))
        self.assertEqual(bridge.observed_accent_color, "C8FBCF")
        self.assertEqual(len(client.callbacks), 1)
        self.assertFalse(bridge.hass.config_entries.updates)
        self.assertFalse(bridge.hass.services.calls)

    async def test_actual_layout_api_returns_observed_native_roles_without_writes(self):
        hass, entry = host.environment()
        entry.options["accent_color"] = "36BCF0"
        entry.runtime_data = SimpleNamespace(observed_accent_color="AEE2FF")
        original = deepcopy(entry.options)
        connection = host.Connection()
        await host.panel.websocket_get_layout(
            hass, connection, {"id": 1, "entry_id": entry.entry_id}
        )
        result = connection.results[0]["entries"][0]
        self.assertEqual(result["accent_color"], "AEE2FF")
        self.assertEqual(
            result["colors"]["secondary"],
            dict(background=0xCAF6FF, foreground=0x071018),
        )
        self.assertEqual(
            result["colors"]["surface"], dict(background=0x222D33, foreground=0xFFFFFF)
        )
        self.assertEqual(entry.options, original)
        self.assertFalse(hass.config_entries.updates)
        self.assertFalse(hass.services.calls)


if __name__ == "__main__":
    unittest.main(verbosity=2)
