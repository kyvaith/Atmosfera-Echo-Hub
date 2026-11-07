"""Demo selection uses actual provider objects and preserves their features."""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_entity_control  # Install the existing narrow HA module fixtures.

SOURCE = Path(__file__).resolve().parents[1] / "ha_demo/atmosfera_demo/entities.py"
spec = importlib.util.spec_from_file_location("_demo_provider_selection", SOURCE)
demo = importlib.util.module_from_spec(spec)
with patch.object(sys.modules["homeassistant.components.climate"], "ClimateEntityFeature",
                  SimpleNamespace(TARGET_TEMPERATURE_RANGE=2), create=True):
    spec.loader.exec_module(demo)


class DemoProviderSelectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_two_distinct_fans_keep_actual_provider_capabilities_and_ids(self):
        entities = [SimpleNamespace(entity_id=None, unique_id=f"fan{i + 1}",
                    supported_features=56 if i == 4 else 55) for i in range(5)]
        hass, entry = object(), object()
        captured = []
        async def setup(actual_hass, actual_entry, add):
            self.assertIs(actual_hass, hass)
            self.assertIs(actual_entry, entry)
            add(entities, True)
        with patch.object(demo, "import_module", return_value=SimpleNamespace(async_setup_entry=setup)) as load:
            await demo.demo_platform("fan")(hass, entry, lambda items, update: captured.append((items, update)))
        load.assert_called_once_with("homeassistant.components.demo.fan")
        selected, update = captured[0]
        self.assertEqual(selected, [entities[2], entities[4]])
        self.assertTrue(update)
        self.assertEqual([item.entity_id for item in selected],
                         ["fan.atmosfera_demo_fan", "fan.atmosfera_demo_fan_presets"])
        self.assertEqual([(item.unique_id, item.supported_features) for item in selected], [("fan3", 55), ("fan5", 56)])
        self.assertTrue(all(entities[i].entity_id is None for i in (0, 1, 3)))

    async def test_humidity_provider_bindings_remain_distinct(self):
        entities = [SimpleNamespace(entity_id=None, supported_features=i) for i in range(3)]
        captured = []
        async def setup(hass, entry, add):
            add(entities)
        with patch.object(demo, "import_module", return_value=SimpleNamespace(async_setup_entry=setup)):
            await demo.demo_platform("humidifier")(None, None, lambda items, update: captured.extend(items))
        self.assertEqual(captured, [entities[0], entities[2]])
        self.assertEqual([item.entity_id for item in captured],
                         ["humidifier.atmosfera_demo_humidity", "humidifier.atmosfera_demo_humidity_modes"])
        self.assertEqual([item.supported_features for item in captured], [0, 2])
