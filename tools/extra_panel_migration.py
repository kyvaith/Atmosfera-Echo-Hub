"""Pure preparation of an owned Info/Lock migration; never connects or writes HA."""

from copy import deepcopy
import hashlib
import json

OWNED_SLOTS = {2: "binary_sensor.atmosfera_demo_contact", 3: "lock.atmosfera_demo_lock",
    11: "alarm_control_panel.atmosfera_demo_alarm", 12: "calendar.atmosfera_demo_agenda",
    13: "sensor.atmosfera_demo_sensor"}


def require_owned(inventory):
    """Names/State attributes alone do not prove a mock provider, even without registry."""
    cards = {card["slot"]: card for card in inventory["layout"]["cards"]}
    for slot, entity in OWNED_SLOTS.items():
        assert cards[slot]["entity_id"] == entity and cards[slot]["visible"] is True
        assert inventory["states"][entity]["entity_id"] == entity
        assert inventory["runtime_entity_source"][entity]["domain"] == "atmosfera_demo"
        related = inventory["runtime_related"][entity]
        assert related["integration"] == ["atmosfera_demo"]
        entry_id, = related["config_entry"]
        entry = inventory["config_entries"][entry_id]
        assert entry["domain"] == "atmosfera_demo" and entry["state"] == "loaded"
        registered = inventory["registry"].get(entity)
        if registered is not None:
            assert registered["platform"] == "atmosfera_demo" and registered["config_entry_id"] == entry_id
            assert registered["disabled_by"] is None and registered["unique_id"]


def plan(inventory, *, expected_revision, candidate_version, correct_moisture_label=False):
    """Make reviewable data for a future explicit HA compare-and-swap operation."""
    assert type(candidate_version) is int and candidate_version >= 92, "91 is storage-only"
    before = inventory["layout"]
    assert type(expected_revision) is int and before["revision"] == expected_revision
    require_owned(inventory)
    after = deepcopy(before)
    for card in after["cards"]:
        if card["slot"] not in OWNED_SLOTS:
            continue
        expected_action = {"kind": "service", "service": "lock.lock", "data": {}} if card["slot"] == 3 else {"kind": "none"}
        assert card["action"] == expected_action, "Existing action changed; re-review rather than overwrite"
        card["action"] = {"kind": "control", "control": "panel", "property": "lock" if card["slot"] == 3 else "info"}
        if correct_moisture_label and card["slot"] == 2:
            assert inventory["states"][card["entity_id"]]["attributes"].get("device_class") == "moisture"
            card["title"], card["icon"] = "Czujnik zalania", "auto"
    # HA owns assigning the successor revision after the successful CAS.
    return {"candidate_version": candidate_version, "expected_revision": expected_revision,
            "before_sha256": hashlib.sha256(json.dumps(before, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(),
            "before": deepcopy(before), "proposed": after,
            "scope": "Only owned slots2/3/11/12/13; prepared offline, not saved or applied"}


def require_unchanged(plan_value, fresh_inventory):
    require_owned(fresh_inventory)
    assert fresh_inventory["layout"] == plan_value["before"], "CAS precondition changed; rebuild review from latest layout"


def rollback_proposal(plan_value, accepted_layout, fresh_inventory):
    """Never replay a stale whole-layout backup over later user changes."""
    require_owned(fresh_inventory)
    expected = deepcopy(plan_value["proposed"])
    assert type(accepted_layout["revision"]) is int and accepted_layout["revision"] == plan_value["expected_revision"] + 1
    expected["revision"] = accepted_layout["revision"]
    assert accepted_layout == expected and fresh_inventory["layout"] == accepted_layout
    restored = deepcopy(plan_value["before"])
    restored["revision"] = accepted_layout["revision"]
    return {"expected_revision": accepted_layout["revision"], "proposed": restored}
