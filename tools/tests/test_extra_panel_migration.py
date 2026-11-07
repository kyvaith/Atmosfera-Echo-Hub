"""Pure ownership/CAS tests; no HA client, device input, or network."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "extra_panel_migration.py"
spec = importlib.util.spec_from_file_location("extra_migration", path)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)


def fixture():
    cards, states, sources, related = [], {}, {}, {}
    for slot, entity in target.OWNED_SLOTS.items():
        cards.append({"slot": slot, "entity_id": entity, "visible": True, "title": "Name", "icon": "auto",
                      "action": {"kind": "service", "service": "lock.lock", "data": {}} if slot == 3 else {"kind": "none"}})
        states[entity] = {"entity_id": entity, "state": "off", "attributes": {"device_class": "moisture"}}
        sources[entity] = {"domain": "atmosfera_demo"}
        related[entity] = {"integration": ["atmosfera_demo"], "config_entry": ["owned"]}
    cards.append({"slot": 30, "entity_id": "button.untouched", "visible": False, "action": {"kind": "default"}})
    return {"layout": {"version": 3, "revision": 355, "cards": cards, "pages": ["user-order"]}, "states": states,
        "registry": {}, "runtime_entity_source": sources, "runtime_related": related,
        "config_entries": {"owned": {"domain": "atmosfera_demo", "state": "loaded"}}}


class MigrationTests(unittest.TestCase):
    def test_only_approved_actions_change_and_unregistered_sources_require_runtime_proof(self):
        inventory = fixture()
        result = target.plan(inventory, expected_revision=355, candidate_version=92)
        self.assertEqual(result["before"], inventory["layout"])
        self.assertEqual(result["proposed"]["cards"][-1], inventory["layout"]["cards"][-1])
        self.assertEqual(result["proposed"]["pages"], ["user-order"])
        for before, after in zip(result["before"]["cards"][:-1], result["proposed"]["cards"][:-1]):
            self.assertEqual({k: v for k, v in before.items() if k != "action"}, {k: v for k, v in after.items() if k != "action"})
        target.require_unchanged(result, inventory)

    def test_spoofed_prefix_without_runtime_provider_and_entry_never_passes(self):
        entity = target.OWNED_SLOTS[3]
        for mutate in (lambda item: item["runtime_entity_source"].pop(entity),
                lambda item: item["runtime_entity_source"][entity].update(domain="other"),
                lambda item: item["runtime_related"][entity].update(config_entry=[]),
                lambda item: item["config_entries"]["owned"].update(state="not_loaded"),
                lambda item: item["registry"].update({entity: {"platform": "other", "config_entry_id": "owned"}})):
            value = fixture(); mutate(value)
            with self.assertRaises((AssertionError, KeyError, ValueError)):
                target.require_owned(value)

    def test_stale_revision_user_edit_or_storage91_blocks_plan_and_rollback(self):
        value = fixture()
        for version, revision in ((91, 355), (92, 354)):
            with self.assertRaises(AssertionError): target.plan(value, expected_revision=revision, candidate_version=version)
        result = target.plan(value, expected_revision=355, candidate_version=92)
        changed = deepcopy(value)
        changed["layout"]["cards"][-1]["visible"] = True
        with self.assertRaises(AssertionError): target.require_unchanged(result, changed)
        accepted = deepcopy(result["proposed"]); accepted["revision"] = 356
        changed["layout"] = accepted
        rollback = target.rollback_proposal(result, accepted, changed)
        self.assertEqual(rollback["expected_revision"], 356)
        changed["layout"] = deepcopy(accepted)
        changed["layout"]["cards"][-1]["visible"] = True
        with self.assertRaises(AssertionError): target.rollback_proposal(result, accepted, changed)


if __name__ == "__main__": unittest.main()
