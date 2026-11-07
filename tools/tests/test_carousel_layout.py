"""Stable page identities and capacity across legacy and carousel layouts."""

import pytest

from test_ha_layout import layout


def test_carousel_order_preserves_bindings_and_exports():
    order = ["home-1", "home-5", "home-3"]
    card = {
        "id": "demo-fifth-number",
        "slot": 31,
        "type": "entity",
        "entity_id": "number.atmosfera_demo_number",
        "title": "Test liczby",
        "icon": "action",
        "palette": "primary",
        "visible": True,
        "action": {"kind": "control", "control": "number"},
    }
    saved = layout.validate_layout(
        {"version": 3, "profile": layout.PROFILE_ID, "revision": 2, "cards": [card],
         "home_order": order}
    )
    assert saved["cards"][0]["slot"] == 31
    assert saved["home_order"] == order
    assert layout.import_layout(layout.export_layout(saved), 2) == saved
    assert layout.device_profile(carousel=True)["slots"][31]["page_id"] == "home-5"
    with pytest.raises(layout.LayoutError):
        layout.validate_layout({key: value for key, value in saved.items() if key != "home_order"})


@pytest.mark.parametrize("order", [
    ["home-2", "home-1", "home-3"], ["home-1", "home-5"],
    ["home-1", "home-3", "home-3"], ["home-1", "home-3", "home-6"],
    ["home-1", "home-3", {}],
])
def test_bad_routes_are_rejected(order):
    with pytest.raises(layout.LayoutError) as error:
        layout.validate_home_order(order)
    assert error.value.code == "invalid_carousel"
