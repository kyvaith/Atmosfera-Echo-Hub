"""Offline HA-produced closed wire fixtures and worst printable JSON bounds."""

import argparse
from datetime import datetime
import importlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/tests"))
import test_ha_layout as base
import test_extra_panels as tests

sequence = 0


def escaped(length):
    global sequence
    sequence += 1
    return ''.join('"' if sequence & (1 << index) else '\\' for index in range(length))


def maxima():
    result = {}
    for name in ("sensor", "binary_sensor", "alarm_control_panel", "calendar", "lock"):
        value = tests.snapshot(name)
        value.update(kind="state", channel="a" * 32, open_seq=2**31 - 1, slot=31,
                     card_id="a" * 64, revision=2**53 - 1, token="b" * 32,
                     state_seq=2**31 - 1, state_generation=2**31 - 1, title=escaped(160))
        value["panel_state"]["updated_text"] = escaped(48)
        if name in {"sensor", "binary_sensor"}: value["panel_caps"]["device_class"] = "c" * 32
        state = value["panel_state"]
        if name == "sensor": state.update(value_status="value", value_text=escaped(96), unit_text=escaped(24))
        elif name in {"binary_sensor", "alarm_control_panel"}:
            state.update(text_status="value", state_text=escaped(96))
            if name == "alarm_control_panel": state["phase"] = "armed_custom_bypass"
        elif name == "calendar":
            for key, limit in (("summary", 128), ("start_text", 40), ("end_text", 40), ("zone_text", 48), ("location", 96), ("description", 64)):
                state[key] = escaped(limit)
            state["truncated_fields"] = 7
        encoded = tests.codec.encode(value, extra_profiles=("info", "lock"))
        result[name] = {"json": encoded, "size_utf8": len(encoded.encode()), "value": value}
    offers = [{"name": chr(97 + index) * 24, "version": 255} for index in range(8)]
    query = json.loads(tests.features.payload("a" * 32, offers))
    for name, value in (("extra_query", query), ("extra_bind_success", query | {"accepted": True})):
        encoded = json.dumps(value, separators=(",", ":"))
        result[name] = {"json": encoded, "size_utf8": len(encoded.encode()), "value": value}
    return result


def actual(inventory):
    result = {}
    for entity, original in inventory["states"].items():
        family = entity.partition(".")[0]
        if family not in tests.extra.INFO_DOMAINS | {"lock"}: continue
        for source in (original["state"], "unknown", "unavailable"):
            hass, state = tests.environment(family, source, original["attributes"])
            state.entity_id = entity
            state.last_updated = datetime.fromisoformat(original["last_updated"])
            hass.config.time_zone = inventory["core"]["time_zone"]
            model = tests.extra.ExtraDomain.from_ha(hass, state)
            observation = tests.extra.ExtraObservation.from_ha(hass, state, model, "pl")
            value = tests.snapshot(family)
            value.update(panel_caps=model.descriptor(), panel_state=observation.descriptor(), available=observation.available,
                         eligible_actions=observation.eligible(model))
            encoded = tests.codec.encode(value, extra_profiles=("info", "lock"))
            result[entity + "/" + source] = {"json": encoded, "size_utf8": len(encoded.encode()), "value": value}
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    maximum = maxima()
    (args.output / "maxima.json").write_text(json.dumps(maximum, ensure_ascii=False, indent=2), encoding="utf8")
    values = actual(json.loads(args.inventory.read_text(encoding="utf8")))
    (args.output / "actual.json").write_text(json.dumps(values, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps({name: row["size_utf8"] for name, row in maximum.items()}))
