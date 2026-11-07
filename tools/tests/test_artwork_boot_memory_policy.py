"""Keep compressed artwork away from the startup internal-RAM budget."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from esphome import yaml_util
from esphome.components.packages import do_packages_pass, merge_packages
from esphome.components.substitutions import do_substitution_pass
from esphome.core import CORE

ROOT = Path(os.environ.get("AEH_SOURCE_ROOT", Path(__file__).resolve().parents[2]))
OVERLAY = os.environ.get("AEH_ARTWORK_OVERLAY_ROOT")
BASELINE = os.environ.get("AEH_ARTWORK_BASE_ROOT")
OPTION = "prefer_external_download_buffer"


def load_product(root, overlay=None):
    CORE.reset()
    CORE.config_path = root / "atmosfera-echo-hub.yaml"
    config = yaml_util.load_yaml(CORE.config_path)
    if overlay:
        for package, path in (
            ("player_artwork", "modules/player/artwork.yaml"),
            ("immich_runtime", "modules/immich/runtime.yaml"),
        ):
            config["packages"][package] = yaml_util.load_yaml(Path(overlay) / path)
    config = do_packages_pass(config, command_line_substitutions={})
    config = do_substitution_pass(config, {})
    return merge_packages(config)


def plain(value):
    if isinstance(value, dict):
        return {str(key): plain(child) for key, child in value.items()}
    if isinstance(value, list):
        return [plain(child) for child in value]
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    return str(value)


class ArtworkBootMemoryPolicyTests(unittest.TestCase):
    def test_both_long_lived_compressed_inputs_prefer_psram_at_construction(self):
        config = load_product(ROOT, OVERLAY)
        images = {str(item["id"]): item for item in config["artwork_image"]}
        self.assertEqual(set(images), {"album_art_background", "immich_photo_image"})
        for image_id, capacity in (
            ("album_art_background", 262144),
            ("immich_photo_image", 786432),
        ):
            with self.subTest(image=image_id):
                image = images[image_id]
                self.assertIs(image[OPTION], True)
                self.assertIs(image["hardware_jpeg"], True)
                self.assertEqual(image["buffer_size"], capacity)
        self.assertNotIn("scheduler_pool_max_items", config["esphome"])

    @unittest.skipUnless(BASELINE, "Set AEH_ARTWORK_BASE_ROOT for the frozen preimage")
    def test_only_two_allocator_preferences_change_the_merged_product(self):
        before = plain(load_product(Path(BASELINE)))
        after = plain(load_product(ROOT, OVERLAY))
        for image in after["artwork_image"]:
            image.pop(OPTION)
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
