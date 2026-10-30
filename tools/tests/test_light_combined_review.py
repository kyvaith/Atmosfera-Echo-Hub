"""Independent host shims only; candidate source is never modified."""

import asyncio
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
import test_light_integration as t  # noqa: E402


class IndependentContinuationTests(unittest.IsolatedAsyncioTestCase):
    async def test_legacy_get_save_cannot_downgrade_control_document(self):
        source = t.layout.validate_layout(t.control_doc())
        hass, entry = t.base.environment(source)
        get = t.base.Connection()
        await t.base.panel.websocket_get_tiles(hass, get, {"id": 1})
        reply = get.results[-1]["entries"][0]["cards"]
        save = t.base.Connection()
        await t.base.panel.websocket_save_tiles(
            hass, save, {"id": 2, "entry_id": entry.entry_id, "cards": reply}
        )
        self.assertEqual(save.errors[0][0], "incompatible_editor")
        self.assertEqual(hass.config_entries.updates, [])
        self.assertEqual(entry.options["home_layout"], source)

    async def run_state_race(self, remove):
        bridge = t.Bridge()
        transport = bridge._light_control
        try:
            self.assertTrue(await transport.async_negotiate())
            msg = t.light.envelope(
                "open",
                channel=transport.owner.channel,
                open_seq=1,
                slot=2,
                card_id="card-2",
                revision=4,
            )
            await transport.async_report(t.wire(msg), t.Context())
            bridge.gate_kind = "light_control_update"
            transport.state_changed()
            await asyncio.wait_for(bridge.entered.wait(), 0.2)
            first = transport._state_task
            if remove:
                bridge.hass.states.items.clear()
            else:
                state = bridge.hass.states.get("light.test")
                state.state = "on"
                state.attributes["brightness"] = 255
            for _ in range(100):
                transport.state_changed()
            self.assertIs(transport._state_task, first)
            self.assertEqual(len(bridge.tasks), 1)
            bridge.release.set()
            await first
            if remove:
                self.assertIsNone(transport.owner._selection)
                self.assertEqual(bridge.models[-1]["kind"], "close")
                self.assertEqual(bridge.models[-1]["reason"], "entity_unavailable")
            else:
                self.assertIsNotNone(transport.owner._selection)
                self.assertEqual(
                    (
                        bridge.models[-1]["kind"],
                        bridge.models[-1]["on"],
                        bridge.models[-1]["brightness_pct"],
                    ),
                    ("state", True, 100),
                )
                self.assertEqual(bridge.models[-1]["state_seq"], 3)
            self.assertEqual(bridge.hass.services.calls, [])
        finally:
            bridge.release.set()
            await transport.async_shutdown()
            if bridge.tasks:
                await asyncio.gather(*bridge.tasks, return_exceptions=True)

    async def test_entity_removal_during_await_emit_is_not_lost(self):
        await self.run_state_race(True)

    async def test_latest_valid_state_after_await_emit_uses_one_task(self):
        await self.run_state_race(False)


if __name__ == "__main__":
    unittest.main()
