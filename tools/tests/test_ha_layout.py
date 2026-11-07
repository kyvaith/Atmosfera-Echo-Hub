"""Host model/HA-adapter checks; fake services never operate real devices."""

from __future__ import annotations

import asyncio
from copy import deepcopy
import importlib
import json
from enum import IntFlag
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
COMPONENT = ROOT / "custom_components" / "atmosfera_echo_hub"


def module(name, **values):
    result = types.ModuleType(name)
    result.__path__ = []
    result.__dict__.update(values)
    sys.modules[name] = result
    return result


class State:
    def __init__(self, entity_id, state="on", attributes=None):
        self.entity_id, self.state, self.attributes = entity_id, state, attributes or {}


class Registry:
    def __init__(self, entries=None):
        self.entries, self.calls = entries or {}, []

    def async_get(self, identifier):
        self.calls.append(identifier)
        return self.entries.get(identifier)

    def async_get_area(self, identifier):
        return self.async_get(identifier)


def identity(function):
    return function


module("homeassistant")
module("homeassistant.components")
module("homeassistant.components.climate", DATA_COMPONENT="climate")
module("homeassistant.components.fan", DATA_COMPONENT="fan")
module("homeassistant.helpers")
module("homeassistant.const", ATTR_ENTITY_ID="entity_id",
       Platform=types.SimpleNamespace(SELECT="select", NOTIFY="notify", EVENT="event"))
module("homeassistant.core", HomeAssistant=object, State=State, callback=identity)
module("homeassistant.helpers.entity_registry", async_get=lambda hass: hass.entity_registry)
module("homeassistant.helpers.service", async_get_cached_service_description=lambda hass, domain, service: getattr(hass, "service_descriptions", {}).get((domain, service)))
module("homeassistant.helpers.device_registry", async_get=lambda hass: hass.device_registry)
module("homeassistant.helpers.area_registry", async_get=lambda hass: hass.area_registry)
module("homeassistant.helpers.translation", async_get_cached_translations=lambda *_: {},
       async_translate_state=lambda _hass, state, *_rest: state)
module("homeassistant.components.panel_custom")
module("homeassistant.components.http", StaticPathConfig=lambda *args: args)
module("homeassistant.components.websocket_api",
       websocket_command=lambda schema: lambda function: function,
       require_admin=identity, async_response=identity, ActiveConnection=object)
package = module("_atmosfera_test")
package.__path__ = [str(COMPONENT)]
layout = importlib.import_module("_atmosfera_test.layout")
cards = importlib.import_module("_atmosfera_test.cards")
panel = importlib.import_module("_atmosfera_test.panel")

# HA adapters are exercised with narrow interfaces, not a running HA instance.
sys.modules["homeassistant.const"].ATTR_FRIENDLY_NAME = "friendly_name"
sys.modules["homeassistant.const"].CONF_HOST = "host"
sys.modules["homeassistant.const"].EVENT_CORE_CONFIG_UPDATE = "core_config_updated"
sys.modules["homeassistant.core"].CALLBACK_TYPE = object
sys.modules["homeassistant.core"].Event = object
module("homeassistant.config_entries", ConfigEntry=object)
module("homeassistant.exceptions", HomeAssistantError=RuntimeError)
module("homeassistant.components.camera")
module("homeassistant.components.camera.helper", get_camera_from_entity_id=lambda *_: None)
module("homeassistant.components.network", async_get_source_ip=lambda *_: None)
module("homeassistant.helpers.event", async_call_later=lambda *_: lambda: None,
       async_track_state_change_event=lambda *_: lambda: None,
       async_track_time_interval=lambda *_: lambda: None)
module("homeassistant.helpers.network", NoURLAvailableError=ValueError, get_url=lambda *_: "")
sys.modules["homeassistant.helpers.translation"].async_get_translations = lambda *_: None
controller = importlib.import_module("_atmosfera_test.controller")


def card(slot=2, entity="light.kitchen", **updates):
    result = {
        "id": f"card-{slot}", "slot": slot, "type": "entity", "entity_id": entity,
        "title": "Kitchen", "icon": "light", "palette": "primary",
        "visible": slot >= 2, "action": {"kind": "default"},
    }
    result.update(updates)
    return result


def document(items=None, revision=0):
    return {"version": 2, "profile": layout.PROFILE_ID, "revision": revision,
            "cards": [card()] if items is None else items}


class Services:
    def __init__(self, names):
        self.names, self.calls = set(names), []

    def has_service(self, domain, operation):
        return f"{domain}.{operation}" in self.names

    async def async_call(self, *args, **kwargs):
        self.calls.append((args, kwargs))


class States:
    def __init__(self, items=()):
        self.items = {state.entity_id: state for state in items}

    def get(self, entity_id):
        return self.items.get(entity_id)

    def async_all(self):
        return list(self.items.values())


class ConfigEntries:
    def __init__(self, entry):
        self.entry, self.updates = entry, []

    def async_get_entry(self, entry_id):
        return self.entry if entry_id == self.entry.entry_id else None

    def async_loaded_entries(self, domain):
        return [self.entry] if domain == self.entry.domain else []

    def async_update_entry(self, entry, *, options):
        entry.options = options
        self.updates.append(deepcopy(options))


class Connection:
    def __init__(self):
        self.results, self.errors = [], []

    def send_result(self, message_id, result):
        self.results.append(result)

    def send_error(self, message_id, code, message):
        self.errors.append((code, message))


def environment(doc=None, states=(), services=()):
    entry = types.SimpleNamespace(
        entry_id="test-entry", domain="atmosfera_echo_hub", title="Test panel",
        data={}, options={
            "home_layout": doc or document(),
            "cameras": ["camera.door"], "stream_fps": 17,
            "stream_width": 800, "stream_height": 800,
            "future_setting": {"keep": True},
        }, runtime_data=None,
    )
    hass = types.SimpleNamespace(
        states=States(states), services=Services(services),
        config_entries=ConfigEntries(entry), config=types.SimpleNamespace(language="en"),
        entity_registry=Registry(), device_registry=Registry(), area_registry=Registry(),
    )
    return hass, entry


class ModelTests(unittest.TestCase):
    def assert_error(self, code, operation):
        with self.assertRaises(layout.LayoutError) as caught:
            operation()
        self.assertEqual(code, caught.exception.code)

    def test_profile_is_bounded_and_independent(self):
        profile = layout.device_profile()
        self.assertEqual(list(range(16)), [slot["slot"] for slot in profile["slots"]])
        self.assertEqual({11, 12}, {slot["slot"] for slot in profile["slots"] if slot["page_id"] == "home-2" and slot["slot"] > 10})
        profile["slots"][2]["x"] = 1234
        self.assertEqual(55, layout.device_profile()["slots"][2]["x"])

    def test_defaults_migrate_hidden_reserved(self):
        migrated = layout.migrate_legacy(cards.normalize_cards(None))
        self.assertFalse(migrated["cards"][0]["visible"])
        self.assertEqual("legacy-02", migrated["cards"][2]["id"])

    def test_migration_is_deterministic(self):
        source = cards.normalize_cards(None)
        self.assertEqual(layout.migrate_legacy(source), layout.migrate_legacy(source))

    def test_ids_survive_moves(self):
        draft = document()
        draft["cards"][0]["slot"] = 15
        self.assertEqual("card-2", layout.validate_layout(draft)["cards"][0]["id"])

    def test_duplicate_ids_fail(self):
        self.assert_error("duplicate_card_id", lambda: layout.validate_layout(document([card(), card(3, id="card-2")])))

    def test_duplicate_slots_fail(self):
        self.assert_error("duplicate_slot", lambda: layout.validate_layout(document([card(), card(id="different")])))

    def test_unknown_slot_fails(self):
        self.assert_error("invalid_layout", lambda: layout.validate_layout(document([card(16)])))

    def test_reserved_visible_fails(self):
        self.assert_error("reserved_slot", lambda: layout.validate_layout(document([card(0, visible=True)])))

    def test_boolean_slot_is_not_integer(self):
        self.assert_error("invalid_layout", lambda: layout.validate_layout(document([card(False)])))

    def test_unknown_profile_fails(self):
        draft = document()
        draft["profile"] = "other"
        self.assert_error("incompatible_profile", lambda: layout.validate_layout(draft))

    def test_future_version_fails(self):
        draft = document()
        draft["version"] = 4
        self.assert_error("unsupported_version", lambda: layout.validate_layout(draft))

    def test_unknown_secret_metadata_fails(self):
        draft = document()
        draft["access_token"] = "private"
        self.assert_error("invalid_layout", lambda: layout.validate_layout(draft))

    def test_unknown_card_field_fails(self):
        self.assert_error("invalid_layout", lambda: layout.validate_layout(document([card(headers={"Authorization": "secret"})])))

    def test_byte_bound_is_utf8(self):
        draft = document()
        draft["unexpected"] = "Ą" * 20000
        self.assert_error("payload_too_large", lambda: layout.validate_layout(draft))

    def test_nan_is_not_json(self):
        self.assert_error("invalid_layout", lambda: layout.validate_layout(document([card(action={"kind": "service", "service": "light.turn_on", "data": {"brightness_pct": float("nan")}})])))

    def test_sensor_is_read_only(self):
        self.assert_error("unsupported_action", lambda: layout.validate_layout(document([card(type="sensor")])))
        self.assertEqual("sensor", layout.validate_layout(document([card(type="sensor", action={"kind": "none"})]))["cards"][0]["type"])

    def test_title_is_normalized(self):
        actual = layout.validate_layout(document([card(title="<b>A &amp; B</b>\n kitchen")]))
        self.assertEqual("A & B kitchen", actual["cards"][0]["title"])

    def test_malformed_nested_fields_have_structured_errors(self):
        for updates in ({"action": {"kind": {}}}, {"icon": []}, {"palette": {}}):
            with self.subTest(updates=updates), self.assertRaises(layout.LayoutError):
                layout.validate_layout(document([card(**updates)]))

    def test_revision_conflict(self):
        self.assert_error("revision_conflict", lambda: layout.next_revision(4, 3))

    def test_revision_bool_fails(self):
        self.assert_error("invalid_layout", lambda: layout.next_revision(1, True))

    def test_native_report_numbers_preserve_exact_integer_type(self):
        self.assertEqual(12, layout.parse_report_integer("12", 0, 15, "slot"))
        for value in (True, 1.5, "1.5", "-1", " "):
            with self.subTest(value=value):
                self.assert_error("invalid_layout", lambda: layout.parse_report_integer(value, 0, 15, "slot"))

    def test_export_has_no_revision_or_host_metadata(self):
        backup = layout.export_layout(document(revision=4))
        self.assertNotIn("revision", backup["layout"])
        self.assertNotIn("entry_id", json.dumps(backup))
        self.assertEqual(9, layout.import_layout(backup, 9)["revision"])

    def test_import_wrong_profile_fails(self):
        backup = layout.export_layout(document())
        backup["layout"]["profile"] = "bad"
        self.assert_error("incompatible_profile", lambda: layout.import_layout(backup, 0))

    def test_import_revision_injection_fails(self):
        backup = layout.export_layout(document())
        backup["layout"]["revision"] = 10
        self.assert_error("invalid_backup", lambda: layout.import_layout(backup, 0))

    def test_action_domain_cannot_be_retargeted(self):
        self.assert_error("unsupported_action", lambda: layout.validate_action({"kind": "service", "service": "switch.turn_on"}, "light.kitchen"))

    def test_unknown_service_cannot_bypass_catalogue(self):
        self.assert_error("unsupported_action", lambda: layout.validate_action({"kind": "service", "service": "cover.toggle"}, "cover.garage"))

    def test_unsupported_legacy_service_migrates_disabled(self):
        migrated = layout.migrate_legacy([{"slot": 2, "entity_id": "cover.garage", "service": "cover.toggle"}])
        self.assertEqual({"kind": "none"}, migrated["cards"][0]["action"])

    def test_unlock_and_alarm_denied(self):
        for entity, service in (("lock.front", "lock.unlock"), ("alarm_control_panel.home", "alarm_control_panel.alarm_disarm")):
            with self.subTest(service=service):
                self.assert_error("unsupported_action", lambda: layout.validate_action({"kind": "service", "service": service}, entity))

    def test_generic_service_cannot_bypass_protected_domain(self):
        self.assert_error("unsupported_action", lambda: layout.validate_action({"kind": "service", "service": "homeassistant.toggle"}, "lock.front"))

    def test_action_extra_fields_cannot_carry_credentials(self):
        self.assert_error("invalid_action_data", lambda: layout.validate_action({"kind": "service", "service": "light.turn_on", "data": {"token": "secret"}}, "light.kitchen"))

    def test_brightness_range_and_type(self):
        for value in (-1, 101, True, "50"):
            with self.subTest(value=value):
                self.assert_error("invalid_action_data", lambda: layout.validate_action({"kind": "service", "service": "light.turn_on", "data": {"brightness_pct": value}}, "light.kitchen"))

    def test_rgb_validates_channels(self):
        self.assert_error("invalid_action_data", lambda: layout.validate_action({"kind": "service", "service": "light.turn_on", "data": {"rgb_color": [0, 256, 0]}}, "light.kitchen"))

    def test_climate_range_must_be_complete_and_ordered(self):
        for data in ({"target_temp_low": 20}, {"target_temp_low": 23, "target_temp_high": 20}):
            self.assert_error("invalid_action_data", lambda: layout.validate_action({"kind": "service", "service": "climate.set_temperature", "data": data}, "climate.room"))

    def test_missing_required_action_parameter_fails(self):
        self.assert_error("invalid_action_data", lambda: layout.validate_action({"kind": "service", "service": "number.set_value", "data": {}}, "number.room"))

    def test_step_is_checked(self):
        self.assert_error("invalid_action_data", lambda: layout.validate_field(2.5, {"type": "number", "min": 0, "max": 10, "step": 1}, "value"))

    def test_large_integer_has_structured_rejection(self):
        self.assert_error("invalid_action_data", lambda: layout.validate_field(10**500, {"type": "number", "min": 0, "max": 1e12}, "value"))

    def test_step_check_has_no_relative_tolerance_escape(self):
        self.assert_error("invalid_action_data", lambda: layout.validate_field(10**10 + 0.5, {"type": "number", "min": 0, "max": 1e12, "step": 1}, "value"))

    def test_invalid_live_step_magnitude_is_bounded(self):
        self.assert_error("invalid_action_data", lambda: layout.validate_field(1000, {"type": "number", "min": 0, "max": 10000, "step": 1e-320}, "value"))

    def test_backup_boolean_version_is_rejected(self):
        backup = layout.export_layout(document())
        backup["version"] = True
        self.assert_error("invalid_backup", lambda: layout.import_layout(backup, 0))

    def test_profile_geometry_matches_product_yaml(self):
        source = (ROOT / "modules/lvgl/pages/tiles_m3.yaml").read_text(encoding="utf-8")
        self.assertIn("x: 55", source)
        self.assertEqual([55, 176, 220, 248], [layout.device_profile()["slots"][2][key] for key in ("x", "y", "width", "height")])


class AdapterTests(unittest.TestCase):
    def test_full_wire_hides_deleted_and_reserved_slots(self):
        hass, _ = environment(states=[State("light.kitchen")])
        projected = cards.presentation_payload(hass, [card(15)])
        self.assertEqual(1, projected["version"])
        self.assertEqual(16, len(projected["cards"]))
        self.assertFalse(projected["cards"][2]["visible"])
        self.assertTrue(projected["cards"][15]["visible"])

    def test_wire_does_not_leak_entity_ids_or_action_data(self):
        hass, _ = environment(states=[State("light.kitchen")])
        wire = cards.presentation_payload(hass, [card(action={"kind": "service", "service": "light.turn_on", "data": {"brightness_pct": 50}})])
        self.assertNotIn("entity_id", json.dumps(wire))
        self.assertNotIn("brightness_pct", json.dumps(wire))
        self.assertEqual("card-2", wire["cards"][2]["id"])
        self.assertEqual("", wire["cards"][3]["id"])

    def test_lock_and_cover_have_no_default_action(self):
        for entity, state in (("lock.front", "locked"), ("cover.garage", "closed")):
            hass, _ = environment(states=[State(entity, state)], services=["lock.unlock", "cover.open_cover"])
            self.assertIsNone(cards.resolve_action(hass, card(entity=entity)))

    def test_unknown_unavailable_and_missing_never_execute(self):
        for state in (None, State("light.kitchen", "unknown"), State("light.kitchen", "unavailable")):
            hass, _ = environment(states=[] if state is None else [state], services=["light.toggle"])
            self.assertIsNone(cards.resolve_action(hass, card()))

    def test_typed_action_is_revalidated_with_live_capabilities(self):
        state = State("light.kitchen", attributes={"supported_color_modes": ["onoff"]})
        hass, _ = environment(states=[state], services=["light.turn_on"])
        self.assertIsNone(cards.resolve_action(hass, card(action={"kind": "service", "service": "light.turn_on", "data": {"brightness_pct": 50}})))

    def test_valid_typed_action_is_only_resolved_not_dispatched(self):
        state = State("light.kitchen", attributes={"supported_color_modes": ["brightness"]})
        hass, _ = environment(states=[state], services=["light.turn_on"])
        resolved = cards.resolve_action(hass, card(action={"kind": "service", "service": "light.turn_on", "data": {"brightness_pct": 50}}))
        self.assertEqual({"entity_id": "light.kitchen", "brightness_pct": 50}, resolved.data)
        self.assertEqual([], hass.services.calls)

    def test_select_option_follows_live_options(self):
        hass, _ = environment(states=[State("select.mode", attributes={"options": ["a"]})], services=["select.select_option"])
        self.assertIsNone(cards.resolve_action(hass, card(entity="select.mode", action={"kind": "service", "service": "select.select_option", "data": {"option": "b"}})))

    def test_cover_feature_check(self):
        hass, _ = environment(states=[State("cover.blind", attributes={"supported_features": 2})], services=["cover.open_cover", "cover.close_cover"])
        actions = {item["service"] for item in cards.entity_actions(hass, hass.states.get("cover.blind"))}
        self.assertEqual({"cover.close_cover"}, actions)

    def test_featureless_entities_have_no_control_catalogue(self):
        cases = {
            "fan.room": ["fan.turn_on", "fan.turn_off", "fan.toggle", "fan.set_percentage"],
            "media_player.room": ["media_player.turn_on", "media_player.media_play"],
            "vacuum.room": ["vacuum.start", "vacuum.stop"],
            "lawn_mower.room": ["lawn_mower.start_mowing", "lawn_mower.dock"],
        }
        for entity, services in cases.items():
            with self.subTest(entity=entity):
                state = State(entity, attributes={"supported_features": 0})
                hass, _ = environment(states=[state], services=services)
                self.assertEqual([], cards.entity_actions(hass, state))

    def test_media_play_pause_is_state_and_feature_checked(self):
        state = State("media_player.room", "playing", {"supported_features": 1})
        hass, _ = environment(states=[state], services=["media_player.media_play_pause"])
        self.assertEqual(1, len(cards.entity_actions(hass, state)))
        state.state = "paused"
        self.assertEqual([], cards.entity_actions(hass, state))

    def test_runtime_intflag_capabilities_are_not_lost(self):
        class CoverFeature(IntFlag):
            CLOSE = 2

        state = State("cover.blind", attributes={"supported_features": CoverFeature.CLOSE})
        hass, _ = environment(states=[state], services=["cover.close_cover"])
        self.assertEqual(1, len(cards.entity_actions(hass, state)))

    def test_catalogue_excludes_raw_secret_attributes(self):
        hass, _ = environment(states=[State("light.kitchen", attributes={"friendly_name": "Kitchen", "access_token": "private", "entity_picture": "/secret?token=private"})])
        catalogue = cards.entity_catalogue(hass)
        self.assertNotIn("private", json.dumps(catalogue))
        self.assertEqual("Kitchen", catalogue["entities"][0]["name"])

    def test_catalogue_limits_and_query(self):
        hass, _ = environment(states=[State("sensor.a"), State("sensor.b"), State("switch.c")])
        self.assertTrue(cards.entity_catalogue(hass, domains=["sensor"], limit=1)["truncated"])
        self.assertEqual(1, cards.entity_catalogue(hass, query="switch.c")["total"])

    def test_save_preserves_camera_and_unknown_options(self):
        hass, entry = environment()
        saved = panel._save(hass, entry, 0, document())
        self.assertEqual(1, saved["revision"])
        self.assertEqual(["camera.door"], entry.options["cameras"])
        self.assertEqual({"keep": True}, entry.options["future_setting"])
        self.assertEqual(17, entry.options["stream_fps"])

    def test_conflicting_save_has_no_partial_update(self):
        hass, entry = environment(document(revision=2))
        before = deepcopy(entry.options)
        with self.assertRaises(layout.LayoutError):
            panel._save(hass, entry, 1, document(revision=1))
        self.assertEqual(before, entry.options)
        self.assertEqual([], hass.config_entries.updates)

    def test_invalid_live_action_save_has_no_partial_update(self):
        hass, entry = environment(states=[State("light.kitchen", attributes={"supported_color_modes": ["onoff"]})], services=["light.turn_on"])
        draft = document([card(action={"kind": "service", "service": "light.turn_on", "data": {"brightness_pct": 50}})])
        with self.assertRaises(layout.LayoutError):
            panel._save(hass, entry, 0, draft)
        self.assertEqual([], hass.config_entries.updates)

    def test_reserved_card_cannot_be_rewritten(self):
        base = document([card(0), card()])
        hass, entry = environment(base)
        draft = deepcopy(base)
        draft["cards"][0]["title"] = "Rewritten"
        with self.assertRaises(layout.LayoutError):
            panel._save(hass, entry, 0, draft)
        self.assertEqual([], hass.config_entries.updates)

    def test_status_does_not_invent_applied_ack(self):
        _, entry = environment()
        entry.runtime_data = types.SimpleNamespace(sent_revision=0, tile_device_available=True)
        status = panel._status(entry)
        self.assertIsNone(status["applied_revision"])
        self.assertFalse(status["pending"])

    def test_import_preview_never_updates_options(self):
        hass, entry = environment()
        connection = Connection()
        backup = layout.export_layout(document([card(3)]))
        asyncio.run(panel.websocket_import_layout(hass, connection, {
            "id": 1, "entry_id": entry.entry_id, "backup": backup,
            "expected_revision": 0, "dry_run": True,
        }))
        self.assertEqual([], connection.errors)
        self.assertEqual([], hass.config_entries.updates)
        self.assertTrue(connection.results[0]["dry_run"])

    def test_invalid_import_never_partially_applies(self):
        hass, entry = environment()
        connection = Connection()
        backup = layout.export_layout(document())
        backup["token"] = "private"
        asyncio.run(panel.websocket_import_layout(hass, connection, {
            "id": 1, "entry_id": entry.entry_id, "backup": backup,
            "expected_revision": 0, "dry_run": False,
        }))
        self.assertTrue(connection.errors)
        self.assertEqual([], hass.config_entries.updates)

    def test_import_stale_revision_never_applies(self):
        hass, entry = environment(document(revision=2))
        connection = Connection()
        asyncio.run(panel.websocket_import_layout(hass, connection, {
            "id": 1, "entry_id": entry.entry_id,
            "backup": layout.export_layout(document()),
            "expected_revision": 1, "dry_run": False,
        }))
        self.assertEqual("revision_conflict", connection.errors[0][0])
        self.assertEqual([], hass.config_entries.updates)

    def test_get_returns_actual_contract_and_no_private_metadata(self):
        hass, entry = environment()
        connection = Connection()
        asyncio.run(panel.websocket_get_layout(hass, connection, {"id": 1}))
        result = connection.results[0]
        self.assertEqual(2, result["version"])
        self.assertEqual("echo-hub-m3-v1", result["entries"][0]["profile"]["id"])
        self.assertEqual(16, len(result["entries"][0]["profile"]["slots"]))
        self.assertNotIn("future_setting", json.dumps(result))


class CatalogueAreaTests(unittest.TestCase):
    def catalogue_environment(self, states, entities=None, devices=None, areas=None):
        hass, entry = environment(states=states)
        hass.entity_registry = Registry({
            key: types.SimpleNamespace(area_id=area, device_id=device)
            for key, (area, device) in (entities or {}).items()
        })
        hass.device_registry = Registry({
            key: types.SimpleNamespace(area_id=area) for key, area in (devices or {}).items()
        })
        hass.area_registry = Registry({
            key: types.SimpleNamespace(id=key, name=name, picture="private", floor_id="private")
            for key, name in (areas or {}).items()
        })
        return hass, entry

    def test_entity_area_overrides_device_area(self):
        hass, _ = self.catalogue_environment([State("light.kitchen")],
            {"light.kitchen": ("kitchen", "device")}, {"device": "living"},
            {"kitchen": "Kuchnia", "living": "Salon"})
        row = cards.entity_catalogue(hass)["entities"][0]
        self.assertEqual(("kitchen", "Kuchnia"), (row["area_id"], row["area_name"]))
        self.assertEqual([], hass.device_registry.calls)

    def test_device_area_is_fallback_only_without_entity_assignment(self):
        hass, _ = self.catalogue_environment([State("light.kitchen")],
            {"light.kitchen": (None, "device")}, {"device": "living"}, {"living": "Salon"})
        row = cards.entity_catalogue(hass)["entities"][0]
        self.assertEqual(("living", "Salon"), (row["area_id"], row["area_name"]))

    def test_stale_entity_override_does_not_choose_devices_other_area(self):
        hass, _ = self.catalogue_environment([State("light.kitchen")],
            {"light.kitchen": ("removed", "device")}, {"device": "living"}, {"living": "Salon"})
        result = cards.entity_catalogue(hass)
        self.assertIsNone(result["entities"][0]["area_id"])
        self.assertIsNone(result["entities"][0]["area_name"])
        self.assertEqual([], result["areas"])
        self.assertEqual([], hass.device_registry.calls)

    def test_stale_device_or_device_area_produces_no_area(self):
        for devices in ({}, {"removed": "deleted-area"}):
            hass, _ = self.catalogue_environment([State("sensor.room")],
                {"sensor.room": (None, "removed")}, devices)
            row = cards.entity_catalogue(hass)["entities"][0]
            self.assertIsNone(row["area_id"])
            self.assertIsNone(row["area_name"])

    def test_registered_entity_without_area_or_device_is_eligible(self):
        hass, _ = self.catalogue_environment([State("sensor.room")], {"sensor.room": (None, None)})
        result = cards.entity_catalogue(hass)
        self.assertEqual(1, result["total"])
        self.assertIsNone(result["entities"][0]["area_id"])

    def test_unregistered_yaml_runtime_entity_stays_eligible_without_fabricated_area(self):
        hass, _ = self.catalogue_environment([State("sensor.yaml", "unavailable", {
            "area_id": "invented", "device_id": "invented", "friendly_name": "YAML sensor"})])
        row = cards.entity_catalogue(hass)["entities"][0]
        self.assertEqual("sensor.yaml", row["entity_id"])
        self.assertFalse(row["available"])
        self.assertIsNone(row["area_id"])
        self.assertIsNone(row["area_name"])
        self.assertEqual([], hass.device_registry.calls)
        self.assertEqual([], hass.area_registry.calls)

    def test_registry_entries_absent_from_runtime_never_create_entities_or_facets(self):
        hass, _ = self.catalogue_environment([State("sensor.active")],
            {"sensor.active": ("active", None), "sensor.stale": ("stale", None)},
            areas={"active": "Active", "stale": "Stale"})
        result = cards.entity_catalogue(hass)
        self.assertEqual(["sensor.active"], [row["entity_id"] for row in result["entities"]])
        self.assertEqual([{"area_id": "active", "area_name": "Active"}], result["areas"])
        self.assertNotIn("sensor.stale", hass.entity_registry.calls)

    def test_area_name_is_bounded_unicode_plain_text_without_registry_details(self):
        hass, _ = self.catalogue_environment([State("sensor.room")],
            {"sensor.room": ("bath", None)}, areas={"bath": "<b>Łazienka</b>\n" + "x" * 100})
        result = cards.entity_catalogue(hass)
        self.assertEqual(80, len(result["entities"][0]["area_name"]))
        self.assertTrue(result["entities"][0]["area_name"].startswith("Łazienka "))
        self.assertNotIn("private", json.dumps(result))
        self.assertNotIn("floor_id", json.dumps(result))
        self.assertNotIn("device_id", json.dumps(result))

    def test_registries_resolved_once_and_device_area_lookups_cached_per_request(self):
        states = [State(f"sensor.room_{number}") for number in range(8)]
        hass, _ = self.catalogue_environment(states,
            {state.entity_id: (None, "shared") for state in states},
            {"shared": "room"}, {"room": "Room"})
        with patch.object(cards, "async_get_entity_registry", return_value=hass.entity_registry) as entity_get, \
                patch.object(cards, "async_get_device_registry", return_value=hass.device_registry) as device_get, \
                patch.object(cards, "async_get_area_registry", return_value=hass.area_registry) as area_get:
            self.assertEqual(8, cards.entity_catalogue(hass)["total"])
        for getter in (entity_get, device_get, area_get):
            getter.assert_called_once_with(hass)
        self.assertEqual(["shared"], hass.device_registry.calls)
        self.assertEqual(["room"], hass.area_registry.calls)
        # No cross-request cache retains old metadata after an HA rename.
        hass.area_registry.entries["room"].name = "Renamed"
        self.assertEqual("Renamed", cards.entity_catalogue(hass)["entities"][0]["area_name"])

    def test_area_filter_precedes_entity_limit_and_keeps_full_match_counts(self):
        states = [State(f"sensor.a{number:03}") for number in range(250)] + [State("sensor.z_target")]
        hass, _ = self.catalogue_environment(states, {"sensor.z_target": ("target", None)}, areas={"target": "Target"})
        result = cards.entity_catalogue(hass, area_id="target", limit=1)
        self.assertEqual(["sensor.z_target"], [row["entity_id"] for row in result["entities"]])
        self.assertEqual(1, result["total"])
        self.assertFalse(result["truncated"])
        unassigned = cards.entity_catalogue(hass, area_id="")
        self.assertEqual(250, unassigned["total"])
        self.assertEqual(200, len(unassigned["entities"]))
        self.assertTrue(unassigned["truncated"])

    def test_area_facets_stay_stable_before_query_domain_and_area_filters(self):
        hass, _ = self.catalogue_environment([State("light.alpha"), State("switch.beta"), State("other.ignored")],
            {"light.alpha": ("z", None), "switch.beta": ("a", None), "other.ignored": ("ignored", None)},
            areas={"a": "Alpha", "z": "Zulu", "ignored": "Ignored"})
        result = cards.entity_catalogue(hass, query="beta", domains=["switch"], area_id="a", limit=1)
        self.assertEqual(["switch.beta"], [row["entity_id"] for row in result["entities"]])
        self.assertEqual([{"area_id": "a", "area_name": "Alpha"}, {"area_id": "z", "area_name": "Zulu"}], result["areas"])
        self.assertEqual(2, result["area_total"])
        self.assertFalse(result["areas_truncated"])
        self.assertEqual(result["areas"], cards.entity_catalogue(hass, area_id="missing")["areas"])

    def test_area_facets_are_bounded_without_limiting_filterable_entities(self):
        states = [State(f"sensor.a{number:03}") for number in range(501)]
        hass, _ = self.catalogue_environment(states,
            {state.entity_id: (f"area{number:03}", None) for number, state in enumerate(states)},
            areas={f"area{number:03}": f"Area {number:03}" for number in range(501)})
        result = cards.entity_catalogue(hass, area_id="area500", limit=1)
        self.assertEqual(500, len(result["areas"]))
        self.assertEqual(501, result["area_total"])
        self.assertTrue(result["areas_truncated"])
        self.assertEqual("sensor.a500", result["entities"][0]["entity_id"])
        self.assertEqual(1, result["total"])

    def test_invalid_area_filter_is_structured_and_has_no_registry_work(self):
        hass, _ = self.catalogue_environment([State("sensor.room")])
        for value in (True, 5, [], "x" * 257):
            with self.subTest(value=value), self.assertRaises(layout.LayoutError) as error:
                cards.entity_catalogue(hass, area_id=value)
            self.assertEqual("invalid_filter", error.exception.code)
        self.assertEqual([], hass.entity_registry.calls)

    def test_websocket_passes_area_filter_and_preserves_validation_errors(self):
        hass, entry = self.catalogue_environment([State("sensor.a"), State("sensor.z")],
            {"sensor.z": ("room", None)}, areas={"room": "Room"})
        connection = Connection()
        message = {"id": 1, "entry_id": entry.entry_id, "query": "", "limit": 1, "area_id": "room"}
        asyncio.run(panel.websocket_get_catalogue(hass, connection, message))
        self.assertEqual("sensor.z", connection.results[0]["entities"][0]["entity_id"])
        connection = Connection()
        asyncio.run(panel.websocket_get_catalogue(hass, connection, {**message, "area_id": True}))
        self.assertEqual("invalid_filter", connection.errors[0][0])
        self.assertEqual([], connection.results)


class BridgeTests(unittest.IsolatedAsyncioTestCase):
    def bridge(self):
        hass, entry = environment(states=[State("light.kitchen")])
        bridge = controller.CameraBridge.__new__(controller.CameraBridge)
        bridge.hass, bridge.entry = hass, entry
        bridge._closed = False
        bridge._notifications = types.SimpleNamespace(setup=unittest.mock.AsyncMock(), lock=asyncio.Lock(), push=unittest.mock.AsyncMock())
        bridge._connection_epoch = 0
        bridge._native_status_lock = asyncio.Lock()
        bridge._native_status_epoch = -1
        bridge._context_press_version = 0
        bridge._native_context_required = False
        bridge.accepted_revision = bridge.snapshot_ready = None
        bridge.pending_slots = None
        bridge._native_status_requery_task = bridge._native_status_requery_key = None
        bridge.hass.async_create_task = asyncio.create_task
        bridge._background_tasks, bridge._active_push_tasks = set(), set()
        bridge._listeners = set()
        bridge._unsubscribers, bridge._device_preference_keys = [], {}
        bridge._tile_unsubscribe = None
        bridge._tile_registry_unsubscribers = []
        bridge._remove_debounce = bridge._remove_tile_debounce = None
        bridge.camera_entity_ids = ["camera.door"]
        bridge.stream_width = bridge.stream_height = 800
        bridge.stream_fps = 17
        bridge.tile_cards, bridge.tile_entity_ids = [card()], ["light.kitchen"]
        bridge.layout, bridge.saved_revision = document(), 0
        bridge.sent_revision = None
        bridge.accent_color, bridge.device_locale = "36BCF0", None
        bridge._tile_push_lock = asyncio.Lock()
        bridge._last_tile_payload = ""
        bridge._find_api_action = lambda _: object()
        bridge.calls = []

        async def preferences():
            return None

        async def execute(_action, data):
            bridge.calls.append(data)

        bridge._async_subscribe_device_preferences = preferences
        bridge.esphome_entry = types.SimpleNamespace(
            runtime_data=types.SimpleNamespace(
                available=True, client=types.SimpleNamespace(execute_service=execute)
            )
        )
        return bridge

    async def test_send_revision_only_after_successful_api_call(self):
        bridge = self.bridge()
        self.assertIsNone(bridge.sent_revision)
        self.assertTrue(await bridge.async_push_tiles())
        self.assertEqual(0, bridge.sent_revision)
        self.assertEqual(16, len(json.loads(bridge.calls[0]["payload"])["cards"]))
        self.assertEqual(0, json.loads(bridge.calls[0]["payload"])["revision"])
        self.assertEqual("echo-hub-m3-v1", json.loads(bridge.calls[0]["payload"])["profile"])

    async def test_unchanged_revision_is_deduplicated(self):
        bridge = self.bridge()
        await bridge.async_push_tiles()
        await bridge.async_push_tiles()
        self.assertEqual(1, len(bridge.calls))

    async def test_new_revision_sends_even_with_identical_presentation(self):
        bridge = self.bridge()
        await bridge.async_push_tiles()
        bridge.saved_revision = 1
        await bridge.async_push_tiles()
        self.assertEqual(2, len(bridge.calls))
        self.assertEqual(1, bridge.sent_revision)

    async def test_failed_send_is_not_marked_sent(self):
        bridge = self.bridge()

        async def fail(*_):
            raise TimeoutError

        bridge.esphome_entry.runtime_data.client.execute_service = fail
        self.assertFalse(await bridge.async_push_tiles())
        self.assertIsNone(bridge.sent_revision)

    async def test_hot_layout_replaces_only_tile_listener(self):
        bridge = self.bridge()
        removed, registered, scheduled = [], [], []
        def camera_unsubscribe():
            removed.append("camera")
        bridge._unsubscribers = [camera_unsubscribe]
        bridge._tile_unsubscribe = lambda: removed.append("old-tile")
        bridge.entry.options["home_layout"] = document([card(3, entity="switch.new")], revision=1)
        bridge.async_schedule_tile_push = lambda **kwargs: scheduled.append(kwargs)
        original = controller.async_track_state_change_event

        def track(_hass, entities, _callback):
            registered.append(list(entities))
            return lambda: removed.append("new-tile")

        controller.async_track_state_change_event = track
        try:
            self.assertTrue(bridge.async_apply_tile_options())
        finally:
            controller.async_track_state_change_event = original
        self.assertEqual(["old-tile"], removed)
        self.assertEqual([["switch.new"]], registered)
        self.assertEqual([camera_unsubscribe], bridge._unsubscribers)
        self.assertEqual(1, bridge.saved_revision)
        self.assertEqual([{"delay": 0}], scheduled)

    async def test_camera_change_requests_existing_reload_path(self):
        bridge = self.bridge()
        bridge.entry.options["cameras"] = ["camera.other"]
        self.assertFalse(bridge.async_apply_tile_options())
        self.assertEqual(["camera.door"], bridge.camera_entity_ids)

    async def test_shutdown_cancels_owned_tasks_and_exact_listeners(self):
        bridge = self.bridge()
        removed = []
        bridge._tile_unsubscribe = lambda: removed.append("tile")
        bridge._unsubscribers = [lambda: removed.append("camera")]
        task = asyncio.create_task(asyncio.Event().wait())
        bridge._background_tasks.add(task)
        await bridge.async_shutdown()
        self.assertTrue(task.cancelled())
        self.assertEqual(["camera", "tile"], removed)
        self.assertFalse(bridge.tile_device_available)
        self.assertIsNone(bridge._tile_unsubscribe)

    async def test_closed_bridge_never_sends_or_reschedules(self):
        bridge = self.bridge()
        bridge._closed = True
        self.assertFalse(await bridge.async_push_tiles())
        self.assertFalse(await bridge.async_push_sources())
        bridge.async_schedule_tile_push()
        self.assertEqual([], bridge.calls)

    async def test_tile_action_retains_calling_user_context(self):
        bridge = self.bridge()
        bridge.sent_revision = bridge.saved_revision
        bridge.hass.services.names.add("light.toggle")
        context = types.SimpleNamespace(user_id="restricted-user")
        await bridge.async_press_tile(2, context=context)
        self.assertIs(context, bridge.hass.services.calls[0][1]["context"])

    async def test_permission_rejection_cannot_become_system_action(self):
        bridge = self.bridge()
        bridge.sent_revision = bridge.saved_revision
        bridge.hass.services.names.add("light.toggle")
        context = types.SimpleNamespace(user_id="restricted-user")
        operated = []

        async def permission_checked(*_args, **kwargs):
            if getattr(kwargs.get("context"), "user_id", None) == "restricted-user":
                raise RuntimeError("Denied by entity permissions")
            operated.append("light")

        bridge.hass.services.async_call = permission_checked
        with self.assertLogs(controller._LOGGER, level="WARNING"):
            await bridge.async_press_tile(2, context=context)
        self.assertEqual([], operated)

    async def test_pending_layout_never_executes_legacy_slot_tap(self):
        bridge = self.bridge()
        bridge.hass.services.names.add("light.toggle")
        await bridge.async_press_tile(2)
        self.assertEqual([], bridge.hass.services.calls)

    async def test_reconnect_resends_unchanged_presentation(self):
        bridge = self.bridge()
        bridge.hass.async_create_task = asyncio.create_task
        bridge.async_schedule_push = lambda **_kwargs: None
        bridge.async_schedule_tile_push = lambda **_kwargs: None
        await bridge.async_push_tiles()
        bridge._esphome_device_updated()
        self.assertIsNone(bridge.sent_revision)
        await asyncio.gather(*bridge._background_tasks)
        self.assertTrue(await bridge.async_push_tiles())
        self.assertEqual(2, len(bridge.calls))

    async def test_runtime_replaced_during_preferences_uses_new_client(self):
        bridge = self.bridge()
        new_calls = []

        async def execute(_action, data):
            new_calls.append(data)

        async def preferences():
            bridge.esphome_entry.runtime_data = types.SimpleNamespace(
                available=True, client=types.SimpleNamespace(execute_service=execute)
            )

        bridge._async_subscribe_device_preferences = preferences
        self.assertTrue(await bridge.async_push_tiles())
        self.assertEqual([], bridge.calls)
        self.assertEqual(1, len(new_calls))

    async def test_old_connection_result_is_not_marked_sent(self):
        bridge = self.bridge()
        started, release = asyncio.Event(), asyncio.Event()

        async def execute(_action, _data):
            started.set()
            await release.wait()

        bridge.esphome_entry.runtime_data.client.execute_service = execute
        task = asyncio.create_task(bridge.async_push_tiles())
        await started.wait()
        bridge._connection_epoch += 1
        bridge.esphome_entry.runtime_data = types.SimpleNamespace(available=False)
        release.set()
        self.assertFalse(await task)
        self.assertIsNone(bridge.sent_revision)

    def negotiated_bridge(self):
        bridge = self.bridge()
        bridge.hass.services.names.add("light.toggle")
        bridge.sent_revision = bridge.saved_revision
        bridge._context_press_version = 1
        bridge._native_context_required = True
        return bridge

    async def test_correlated_press_accepts_exact_current_identity(self):
        bridge = self.negotiated_bridge()
        context = types.SimpleNamespace(user_id="original-user")
        await bridge.async_press_tile(2, card_id="card-2", revision=0, context=context)
        self.assertEqual(1, len(bridge.hass.services.calls))
        self.assertIs(context, bridge.hass.services.calls[0][1]["context"])

    async def test_correlated_press_rejects_old_card_id(self):
        bridge = self.negotiated_bridge()
        await bridge.async_press_tile(2, card_id="old-card", revision=0)
        self.assertEqual([], bridge.hass.services.calls)

    async def test_correlated_press_rejects_old_revision(self):
        bridge = self.negotiated_bridge()
        bridge.saved_revision = bridge.sent_revision = 1
        await bridge.async_press_tile(2, card_id="card-2", revision=0)
        self.assertEqual([], bridge.hass.services.calls)

    async def test_correlated_press_rejects_boolean_revision(self):
        bridge = self.negotiated_bridge()
        await bridge.async_press_tile(2, card_id="card-2", revision=False)
        self.assertEqual([], bridge.hass.services.calls)

    async def test_context_press_requires_explicit_negotiation(self):
        bridge = self.bridge()
        bridge.sent_revision = 0
        bridge.hass.services.names.add("light.toggle")
        await bridge.async_press_tile(2, card_id="card-2", revision=0)
        self.assertEqual([], bridge.hass.services.calls)

    async def test_legacy_press_cannot_bypass_negotiated_context(self):
        bridge = self.negotiated_bridge()
        await bridge.async_press_tile(2)
        self.assertEqual([], bridge.hass.services.calls)

    async def test_legacy_press_is_denied_during_capability_probe(self):
        bridge = self.bridge()
        bridge.sent_revision = 0
        bridge._native_context_required = True
        bridge.hass.services.names.add("light.toggle")
        await bridge.async_press_tile(2)
        self.assertEqual([], bridge.hass.services.calls)

    async def test_status_probe_reads_only_advertised_response_action(self):
        bridge = self.bridge()
        await bridge._async_refresh_native_status(force=True)
        self.assertEqual([], bridge.calls)
        self.assertEqual(0, bridge.context_press_version)

    def status_bridge(self, response):
        bridge = self.bridge()
        status_action = types.SimpleNamespace(supports_response=controller.SupportsResponseType.ONLY)
        bridge._find_api_action = lambda name: status_action if name == "home_tiles_get_status" else object()

        async def execute(_action, _data, **kwargs):
            bridge.calls.append(kwargs)
            return types.SimpleNamespace(success=True, response_data=json.dumps(response).encode())

        bridge.esphome_entry.runtime_data.client.execute_service = execute
        return bridge

    async def test_status_probe_negotiates_source_acceptance_not_application(self):
        bridge = self.status_bridge({
            "profile": layout.PROFILE_ID, "context_press_version": 1,
            "configured_context_version": 1, "revision": 0, "snapshot_ready": True,
        })
        await bridge._async_refresh_native_status(force=True)
        self.assertEqual(1, bridge.context_press_version)
        self.assertEqual(0, bridge.accepted_revision)
        self.assertTrue(bridge.snapshot_ready)
        self.assertEqual({"return_response": True, "timeout": 5.0}, bridge.calls[0])
        bridge.entry.runtime_data = bridge
        self.assertIsNone(panel._status(bridge.entry)["applied_revision"])

    async def test_legacy_configured_mode_is_not_source_acceptance(self):
        bridge = self.status_bridge({
            "profile": layout.PROFILE_ID, "context_press_version": 1,
            "configured_context_version": 0, "revision": 0, "snapshot_ready": True,
        })
        await bridge._async_refresh_native_status(force=True)
        self.assertEqual(1, bridge.context_press_version)
        self.assertIsNone(bridge.accepted_revision)
        self.assertIsNone(bridge.snapshot_ready)

    async def test_status_probe_rejects_malformed_version(self):
        bridge = self.status_bridge({
            "profile": layout.PROFILE_ID, "context_press_version": True,
            "configured_context_version": 1, "revision": 0, "snapshot_ready": True,
        })
        await bridge._async_refresh_native_status(force=True)
        self.assertEqual(0, bridge.context_press_version)
        self.assertTrue(bridge._native_context_required)

    async def test_status_probe_deduplicates_known_ready_revision(self):
        bridge = self.status_bridge({
            "profile": layout.PROFILE_ID, "context_press_version": 1,
            "configured_context_version": 1, "revision": 0, "snapshot_ready": True,
        })
        await bridge._async_refresh_native_status()
        await bridge._async_refresh_native_status()
        self.assertEqual(1, len(bridge.calls))

    async def test_status_reports_pending_slot_mask_without_application_claim(self):
        bridge = self.status_bridge({
            "profile": layout.PROFILE_ID, "context_press_version": 1,
            "configured_context_version": 1, "revision": 0,
            "snapshot_ready": False, "pending_slots": 1 << 15,
        })
        await bridge._async_refresh_native_status(force=True)
        bridge.entry.runtime_data = bridge
        status = panel._status(bridge.entry)
        self.assertEqual(1 << 15, status["pending_slots"])
        self.assertFalse(status["snapshot_ready"])
        self.assertIsNone(status["applied_revision"])

    async def test_status_rejects_inconsistent_or_invalid_pending_mask(self):
        for pending in (True, -1, 2**16, 4):
            bridge = self.status_bridge({
                "profile": layout.PROFILE_ID, "context_press_version": 1,
                "configured_context_version": 1, "revision": 0,
                "snapshot_ready": True, "pending_slots": pending,
            })
            await bridge._async_refresh_native_status(force=True)
            self.assertIsNone(bridge.accepted_revision)

    def requery_bridge(self):
        bridge = self.status_bridge({
            "profile": layout.PROFILE_ID, "context_press_version": 1,
            "configured_context_version": 1, "revision": 0,
            "snapshot_ready": False, "pending_slots": 4,
        })
        bridge._native_context_required = True
        bridge.sent_revision = 0
        return bridge

    async def test_native_status_requery_stops_after_three_attempts(self):
        bridge = self.requery_bridge()
        with patch.object(controller, "_NATIVE_STATUS_REQUERY_DELAYS", (0, 0, 0)):
            bridge._schedule_native_status_requery(0, 0)
            task = bridge._native_status_requery_task
            await task
        self.assertEqual(3, len(bridge.calls))
        self.assertFalse(bridge.snapshot_ready)
        self.assertIsNone(bridge._native_status_requery_task)
        self.assertIsNone(bridge._native_status_requery_key)

    async def test_native_status_requery_stops_when_ready(self):
        bridge = self.status_bridge({
            "profile": layout.PROFILE_ID, "context_press_version": 1,
            "configured_context_version": 1, "revision": 0,
            "snapshot_ready": True, "pending_slots": 0,
        })
        bridge._native_context_required, bridge.sent_revision = True, 0
        with patch.object(controller, "_NATIVE_STATUS_REQUERY_DELAYS", (0, 0, 0)):
            bridge._schedule_native_status_requery(0, 0)
            await bridge._native_status_requery_task
        self.assertEqual(1, len(bridge.calls))
        bridge._schedule_native_status_requery(0, 0)
        self.assertIsNone(bridge._native_status_requery_task)

    async def test_native_status_requery_coalesces_latest_revision(self):
        bridge = self.requery_bridge()
        bridge._schedule_native_status_requery(0, 0)
        previous = bridge._native_status_requery_task
        bridge._schedule_native_status_requery(0, 0)
        self.assertIs(previous, bridge._native_status_requery_task)
        bridge.saved_revision = bridge.sent_revision = 1
        bridge._schedule_native_status_requery(1, 0)
        current = bridge._native_status_requery_task
        self.assertIsNot(previous, current)
        await asyncio.gather(previous, return_exceptions=True)
        self.assertTrue(previous.cancelled())
        bridge._cancel_native_status_requery()
        await asyncio.gather(current, return_exceptions=True)
        self.assertEqual([], bridge.calls)

    async def test_native_status_requery_aborts_on_revision_or_epoch_change(self):
        for field in ("saved_revision", "_connection_epoch"):
            bridge = self.requery_bridge()
            with patch.object(controller, "_NATIVE_STATUS_REQUERY_DELAYS", (0, 0, 0)):
                bridge._schedule_native_status_requery(0, 0)
                task = bridge._native_status_requery_task
                setattr(bridge, field, 1)
                await task
            self.assertEqual([], bridge.calls)

    async def test_native_status_requery_cancelled_on_disconnect(self):
        bridge = self.requery_bridge()
        bridge._schedule_native_status_requery(0, 0)
        task = bridge._native_status_requery_task
        bridge.esphome_entry.runtime_data.available = False
        bridge._esphome_device_updated()
        await asyncio.gather(task, return_exceptions=True)
        self.assertTrue(task.cancelled())
        self.assertIsNone(bridge._native_status_requery_task)
        self.assertEqual([], bridge.calls)

    async def test_native_status_requery_cancelled_on_shutdown(self):
        bridge = self.requery_bridge()
        bridge._schedule_native_status_requery(0, 0)
        task = bridge._native_status_requery_task
        await bridge.async_shutdown()
        self.assertTrue(task.cancelled())
        self.assertIsNone(bridge._native_status_requery_task)
        self.assertEqual([], bridge.calls)

    async def test_hot_revision_cancels_native_status_requery(self):
        bridge = self.requery_bridge()
        bridge._schedule_native_status_requery(0, 0)
        task = bridge._native_status_requery_task
        bridge.entry.options["home_layout"] = document(revision=1)
        bridge.async_schedule_tile_push = lambda **_kwargs: None
        with patch.object(controller, "async_track_state_change_event", return_value=lambda: None):
            self.assertTrue(bridge.async_apply_tile_options())
        await asyncio.gather(task, return_exceptions=True)
        self.assertTrue(task.cancelled())
        self.assertIsNone(bridge.snapshot_ready)
        self.assertIsNone(bridge.pending_slots)

    async def test_status_response_from_old_epoch_does_not_claim_acceptance(self):
        bridge = self.requery_bridge()
        entered, resume = asyncio.Event(), asyncio.Event()

        async def execute(*_args, **_kwargs):
            entered.set()
            await resume.wait()
            return types.SimpleNamespace(success=True, response_data=json.dumps({
                "profile": layout.PROFILE_ID, "context_press_version": 1,
                "configured_context_version": 1, "revision": 0,
                "snapshot_ready": True, "pending_slots": 0,
            }).encode())

        bridge.esphome_entry.runtime_data.client.execute_service = execute
        task = asyncio.create_task(bridge._async_refresh_native_status(force=True))
        await entered.wait()
        bridge._connection_epoch += 1
        resume.set()
        await task
        self.assertIsNone(bridge.accepted_revision)
        self.assertIsNone(bridge.snapshot_ready)



class DeviceIdentityTests(unittest.TestCase):
    def identity_environment(self, **fields):
        hass, entry = environment()
        entry.data["device_id"] = "selected-device"
        hass.device_registry = Registry({"selected-device": types.SimpleNamespace(**fields)})
        return hass, entry

    def test_read_only_projection_uses_selected_registry_device_not_entry_title(self):
        hass, entry = self.identity_environment(name="Registry name", name_by_user="Kitchen display",
            manufacturer="Maker", model="Panel model", sw_version="2026.11.0-dev",
            serial_number="private-serial", connections={"private-mac"}, configuration_url="private-url")
        before = deepcopy((entry.data, entry.options))
        connection = Connection()
        asyncio.run(panel.websocket_get_layout(hass, connection, {"id": 1}))
        result = connection.results[0]["entries"][0]
        self.assertEqual(result["device_identity"], {
            "source": "home_assistant_device_registry", "registry_entry_present": True,
            "name": "Kitchen display", "manufacturer": "Maker", "model": "Panel model",
            "software_version": "2026.11.0-dev"})
        self.assertEqual(hass.device_registry.calls, ["selected-device"])
        self.assertNotIn("private-", json.dumps(result))
        self.assertEqual((entry.data, entry.options), before)
        self.assertEqual(hass.config_entries.updates, [])
        self.assertEqual(hass.services.calls, [])

    def test_offline_runtime_keeps_registry_details_without_live_probe(self):
        hass, entry = self.identity_environment(name="Stored display", sw_version="stored-build")
        entry.runtime_data = types.SimpleNamespace(tile_device_available=False)
        connection = Connection()
        asyncio.run(panel.websocket_get_layout(hass, connection, {"id": 1, "entry_id": entry.entry_id}))
        result = connection.results[0]["entries"][0]
        self.assertFalse(result["status"]["device_available"])
        self.assertEqual(result["device_identity"]["software_version"], "stored-build")
        self.assertEqual(hass.services.calls, [])
        self.assertNotIn("live", result["device_identity"])

    def test_missing_device_id_or_removed_registry_entry_is_explicitly_unknown(self):
        hass, entry = environment()
        for identifier in (None, "removed-device", False, "x" * 257):
            entry.data["device_id"] = identifier
            identity = panel._device_identity(hass, entry)
            self.assertFalse(identity["registry_entry_present"])
            self.assertTrue(all(identity[key] is None for key in ("name", "manufacturer", "model", "software_version")))
        self.assertEqual(hass.device_registry.calls, ["removed-device"])

    def test_partial_and_hostile_metadata_is_bounded_plain_text_with_name_fallback(self):
        hass, entry = self.identity_environment(name="  Original <b>display</b> ", name_by_user="  ",
            manufacturer="M" * 20000, model=12, sw_version="  line\nvalue\x00\x7f  ")
        with patch.object(panel, "plain_text", wraps=panel.plain_text) as normalize:
            result = panel._device_identity(hass, entry)
        self.assertTrue(all(len(call.args[0]) <= 320 for call in normalize.call_args_list))
        self.assertEqual(result["name"], "Original display")
        self.assertEqual(result["manufacturer"], "M" * 80)
        self.assertIsNone(result["model"])
        self.assertEqual(result["software_version"], "line value")
        self.assertTrue(result["registry_entry_present"])

    def test_each_read_resolves_current_registry_without_retaining_a_device_snapshot(self):
        hass, entry = self.identity_environment(name="Old", sw_version="old")
        first = panel._device_identity(hass, entry)
        hass.device_registry.entries["selected-device"] = types.SimpleNamespace(name="New", sw_version="new")
        second = panel._device_identity(hass, entry)
        self.assertEqual(first["name"], "Old")
        self.assertEqual(second["name"], "New")
        self.assertEqual(second["software_version"], "new")
        del hass.device_registry.entries["selected-device"]
        self.assertFalse(panel._device_identity(hass, entry)["registry_entry_present"])


class SunReadOnlyContractTests(unittest.TestCase):
    def test_Sun_text_policy_tracks_actual_product_subtitle_fonts_and_widths(self):
        import re
        source = (ROOT / "modules/lvgl/pages/tiles_m3.yaml").read_text(encoding="utf-8")
        labels = {2:"tile_cover_subtitle",3:"tile_lock_subtitle",4:"tile_alarm_subtitle",5:"tile_garage_subtitle",
                  6:"tile_fan_subtitle",7:"tile_fan_speed_subtitle",8:"tile_switch_subtitle",9:"tile_scene_subtitle",
                  10:"tile_trigger_subtitle",11:"tile_window_subtitle",12:"tile_presence_subtitle",
                  13:"tile_sensor_value",14:"tile_clock_value",15:"home_run_title"}
        for slot, identifier in labels.items():
            match = re.search(r"(?m)^( +)id: " + identifier + r"\s*$", source)
            self.assertIsNotNone(match)
            indentation = len(match[1])
            properties = {}
            for line in source[match.end():].splitlines():
                if not line.strip():
                    continue
                if len(line) - len(line.lstrip()) < indentation:
                    break
                if field := re.match(r"\s*(width|text_font|long_mode): (.+)$", line):
                    properties[field[1]] = field[2]
            self.assertEqual(properties["long_mode"], "CLIP")
            if slot in layout.SUN_TEXT_SLOTS:
                self.assertEqual(properties["text_font"], "roboto_16")
                self.assertGreaterEqual(int(properties["width"]), 136)
            else:
                self.assertEqual(properties["text_font"], "roboto_34")
                self.assertEqual(int(properties["width"]), 240)

    def test_profile_advertises_independent_exact_text_placement_policy(self):
        expected = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15]
        profile = layout.device_profile()
        self.assertEqual(profile["sun_text_slots"], expected)
        profile["sun_text_slots"].append(13)
        self.assertEqual(layout.device_profile()["sun_text_slots"], expected)

    def test_both_large_value_places_are_rejected_even_hidden_in_both_versions(self):
        for version in (2, 3):
            for slot in (0, 1, 13, 14):
                for visible in (False, True):
                    item = card(slot, entity="sun.sun", type="sensor", visible=visible, icon="clock", action={"kind": "none"})
                    source = document([item], revision=41)
                    source["version"] = version
                    with self.subTest(version=version, slot=slot, visible=visible), self.assertRaises(layout.LayoutError):
                        layout.validate_layout(source)
                    backup = {"format": "atmosfera-layout", "version": 1, "layout": {k:v for k,v in source.items() if k != "revision"}}
                    with self.assertRaises(layout.LayoutError):
                        layout.import_layout(backup, 42)

    def test_all_normal_text_places_validate_move_and_export_import_without_extra_fields(self):
        for version in (2, 3):
            for slot in layout.SUN_TEXT_SLOTS:
                item = card(slot, id="stable-sun", entity="sun.sun", type="sensor", icon="clock", action={"kind": "none"})
                source = document([item], revision=41)
                source["version"] = version
                valid = layout.validate_layout(source)
                self.assertEqual(valid["cards"], [item])
                restored = layout.import_layout(layout.export_layout(valid), 42)
                self.assertEqual(restored["cards"], [item])
                self.assertEqual(restored["version"], version)
                self.assertNotIn("sun_text_slots", restored)

    def test_sun_requires_information_none_in_both_versions_and_roundtrips(self):
        item = card(entity="sun.sun", type="sensor", icon="clock", action={"kind": "none"})
        for version in (2, 3):
            source = document([item], revision=41)
            source["version"] = version
            valid = layout.validate_layout(source)
            self.assertEqual(valid["cards"][0], item)
            restored = layout.import_layout(layout.export_layout(valid), 42)
            self.assertEqual(restored["cards"], [item])
            self.assertEqual(restored["revision"], 42)

    def test_server_rejects_all_sun_configured_default_and_control_actions(self):
        actions = ({"kind": "default"}, {"kind": "service", "service": "homeassistant.turn_on", "data": {}},
                   {"kind": "service", "service": "sun.turn_on", "data": {}},
                   {"kind": "control", "control": "light"}, {"kind": "none", "service": "sun.turn_on"})
        for action in actions:
            for version in (2, 3):
                with self.subTest(action=action, version=version), self.assertRaises(layout.LayoutError):
                    layout.validate_action(action, "sun.sun", layout_version=version)
        for kind in ("entity", "action"):
            with self.assertRaises(layout.LayoutError):
                layout.validate_layout(document([card(entity="sun.sun", type=kind, action={"kind": "none"})]))

    def test_live_resolver_never_dispatches_sun_even_with_services_or_raw_legacy_card(self):
        for raw_state in ("above_horizon", "below_horizon", "unknown", "unavailable", None):
            states = [] if raw_state is None else [State("sun.sun", raw_state)]
            hass, _ = environment(states=states, services=["sun.turn_on", "homeassistant.turn_on"])
            for updates in ({}, {"service": "homeassistant.turn_on"},
                            {"action": {"kind": "service", "service": "homeassistant.turn_on", "data": {}}}):
                item = card(entity="sun.sun", **updates)
                self.assertIsNone(cards.resolve_action(hass, item))
            for state in states:
                self.assertEqual(cards.entity_actions(hass, state), [])
            self.assertEqual(hass.services.calls, [])

    def test_catalogue_lists_actual_sun_as_passive_filtered_runtime_state(self):
        hass, _ = environment(states=[State("sun.sun", "above_horizon", {"friendly_name": "Słońce"}), State("sensor.temp", "20")])
        result = cards.entity_catalogue(hass, query="słoń", domains=["sun"])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["entities"][0]["entity_id"], "sun.sun")
        self.assertEqual(result["entities"][0]["actions"], [])
        self.assertNotIn("number_control", result["entities"][0])
        self.assertEqual(cards.entity_catalogue(hass, domains=["sensor"])["total"], 1)


class SunLifecycleTests(unittest.IsolatedAsyncioTestCase):
    def bridge(self):
        bridge = BridgeTests.bridge(self)
        bridge.tile_cards = [card(15, entity="sun.sun", type="sensor", action={"kind": "none"})]
        return bridge

    async def test_timezone_only_refresh_is_coalesced_for_visible_Sun_and_not_cameras(self):
        bridge = self.bridge()
        scheduled = []
        bridge.async_schedule_tile_push = lambda **kwargs: scheduled.append(kwargs)
        bridge.async_schedule_push = lambda **_kwargs: self.fail("Sun timezone must not refresh cameras")
        bridge._core_config_updated(types.SimpleNamespace(data={"language": "pl"}))
        self.assertEqual(scheduled, [])
        bridge._core_config_updated(types.SimpleNamespace(data={"time_zone": "Asia/Kathmandu"}))
        self.assertEqual(scheduled, [{"delay": 0}])
        bridge.tile_cards[0]["visible"] = False
        bridge._core_config_updated(types.SimpleNamespace(data={"time_zone": "UTC"}))
        bridge.tile_cards[0]["visible"] = True
        bridge.tile_cards[0]["entity_id"] = "sensor.temperature"
        bridge._core_config_updated(types.SimpleNamespace(data={"time_zone": "UTC"}))
        bridge.tile_cards[0]["entity_id"] = "sun.sun"
        bridge._closed = True
        bridge._core_config_updated(types.SimpleNamespace(data={"time_zone": "UTC"}))
        self.assertEqual(scheduled, [{"delay": 0}])

    async def test_setup_owns_one_config_listener_and_shutdown_removes_it_with_existing_owners(self):
        bridge = self.bridge()
        bridge.esphome_entry.runtime_data = None
        events, removed = [], []
        bridge.hass.bus = types.SimpleNamespace(async_listen=lambda event, callback: (
            events.append((event, callback)) or (lambda: removed.append("config"))))
        bridge.async_schedule_push = lambda **_kwargs: None
        bridge.async_schedule_tile_push = lambda **_kwargs: None
        def track_state(_hass, entities, _callback):
            role = "camera" if entities == bridge.camera_entity_ids else "tile"
            return lambda: removed.append(role)
        with patch.object(controller, "async_track_state_change_event", track_state), patch.object(
            controller, "async_track_time_interval", lambda *_args: lambda: removed.append("existing-periodic")
        ):
            await bridge.async_setup()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0][0], "core_config_updated")
            self.assertEqual(events[0][1], bridge._core_config_updated)
            self.assertEqual(len(bridge._unsubscribers), 3)
            await bridge.async_shutdown()
        self.assertEqual(removed.count("config"), 1)
        self.assertCountEqual(removed, ["camera", "tile", "config", "existing-periodic"])
        self.assertEqual(bridge._unsubscribers, [])


    async def test_actual_tile_dispatch_remains_zero_for_passive_and_raw_service_attempts(self):
        bridge = self.bridge()
        bridge.sent_revision = bridge.saved_revision
        bridge.hass.services.names.update(("homeassistant.turn_on", "sun.turn_on"))
        for raw in ("above_horizon", "below_horizon", "unknown", "unavailable"):
            bridge.hass.states.items["sun.sun"] = State("sun.sun", raw)
            for action in ({"kind": "none"}, {"kind": "default"},
                           {"kind": "service", "service": "homeassistant.turn_on", "data": {}}):
                bridge.tile_cards[0]["action"] = action
                bridge._context_press_version = 0
                await bridge.async_press_tile(15)
                bridge._context_press_version = 1
                await bridge.async_press_tile(15, card_id="card-15", revision=bridge.saved_revision)
        self.assertEqual(bridge.hass.services.calls, [])
        self.assertEqual(bridge.calls, [])

    async def test_timezone_refresh_changes_only_local_caption_with_same_UTC_state_and_revision(self):
        bridge = self.bridge()
        bridge.hass.config.time_zone = "Europe/Warsaw"
        attrs = {"next_rising": "2099-10-27T05:42:00Z", "next_setting": "2099-10-26T15:21:00Z"}
        state = State("sun.sun", "above_horizon", attrs)
        bridge.hass.states.items["sun.sun"] = state
        scheduled = []
        bridge.async_schedule_tile_push = lambda **kwargs: scheduled.append(kwargs)
        self.assertTrue(await bridge.async_push_tiles())
        first = json.loads(bridge.calls[0]["payload"])
        bridge.hass.config.time_zone = "Asia/Kathmandu"
        bridge._core_config_updated(types.SimpleNamespace(data={"time_zone": "Asia/Kathmandu"}))
        self.assertEqual(scheduled, [{"delay": 0}])
        self.assertTrue(await bridge.async_push_tiles())
        second = json.loads(bridge.calls[1]["payload"])
        self.assertEqual(first["cards"][15]["subtitle"], "Set 26.10 16:21")
        self.assertEqual(second["cards"][15]["subtitle"], "Set 26.10 21:06")
        first["cards"][15]["subtitle"] = second["cards"][15]["subtitle"]
        self.assertEqual(first, second)
        self.assertIs(bridge.hass.states.items["sun.sun"], state)
        self.assertEqual(state.attributes, attrs)
        self.assertEqual(bridge.hass.services.calls, [])


if __name__ == "__main__":
    unittest.main()
