"""Static product action wiring; not full ESPHome config or device evidence."""

from pathlib import Path

import yaml


class Loader(yaml.SafeLoader):
    pass


Loader.add_multi_constructor(
    "!", lambda loader, _tag, node: loader.construct_scalar(node)
)


def test_tile_payload_supplies_device_accent_to_the_single_atomic_projection():
    root = Path(__file__).resolve().parents[2]
    data = yaml.load(
        (root / "modules/common/core.yaml").read_text(encoding="utf-8"), Loader=Loader
    )
    action = next(
        action
        for action in data["api"]["actions"]
        if action["action"] == "home_tiles_set_config"
    )
    configurations = [
        item["lvgl_material.tiles.configure"]
        for item in action["then"]
        if "lvgl_material.tiles.configure" in item
    ]
    assert len(configurations) == 1
    assert configurations[0]["payload"] == "return payload;"
    assert configurations[0]["accent_override"] == "return id(ui_accent_color);"
    assert not any("set_accent(" in item.get("lambda", "") for item in action["then"])
