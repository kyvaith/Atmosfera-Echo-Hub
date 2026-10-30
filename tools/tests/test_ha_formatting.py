"""Golden formatting and HA-adapter shim checks; no HA or device is operated."""

from __future__ import annotations

import importlib
import sys
import types
import unittest
from copy import deepcopy
from datetime import UTC, datetime
from decimal import (
    ROUND_DOWN,
    ROUND_UP,
    Clamped,
    Inexact,
    InvalidOperation,
    Overflow,
    Rounded,
    Subnormal,
    Underflow,
    localcontext,
)
from pathlib import Path
from unittest.mock import patch

COMPONENT = Path(__file__).resolve().parents[2] / "custom_components" / "atmosfera_echo_hub"
PACKAGE = "_atmosfera_formatting_test"
package = types.ModuleType(PACKAGE)
package.__path__ = [str(COMPONENT)]
sys.modules[PACKAGE] = package
formatting = importlib.import_module(f"{PACKAGE}.formatting")


class FormattingTests(unittest.TestCase):
    def test_precision_options_precedence_and_zero(self):
        for options, expected in (
            ({"sensor": {"display_precision": 0, "suggested_display_precision": 4}}, 0),
            ({"sensor": {"display_precision": 2, "suggested_display_precision": 4}}, 2),
            ({"sensor": {"display_precision": None, "suggested_display_precision": 3}}, 3),
            ({"sensor": {"suggested_display_precision": 1}}, 1),
        ):
            with self.subTest(options=options):
                self.assertEqual(formatting.sensor_precision("12.3456", options), expected)

    def test_precision_is_bounded_strict_integer_and_missing_registry_is_safe(self):
        for value, expected in ((-100, 0), (100, 6), (10**500, 6)):
            self.assertEqual(formatting.sensor_precision("1.234", {"sensor": {"display_precision": value}}), expected)
        for value in (True, False, "2", 2.0, [], {}, None):
            with self.subTest(value=value):
                self.assertEqual(formatting.sensor_precision("1.234", {"sensor": {"display_precision": value}}), 3)
        for value in (None, [], {}, {"sensor": None}, {"sensor": []}, {"other": {"display_precision": 0}}):
            self.assertEqual(formatting.sensor_precision("12.34", value), 2)

    def test_read_only_registry_mappings_are_read_without_mutation(self):
        options = types.MappingProxyType({"sensor": types.MappingProxyType({"display_precision": 2})})
        self.assertEqual(formatting.sensor_text("12.345", "V", registry_options=options), "12.34 V")
        self.assertEqual(dict(options["sensor"]), {"display_precision": 2})

    def test_state_decimal_precision_and_scientific_notation_are_capped(self):
        for raw, expected in (("12", 0), ("12.3400", 4), ("1.23456789", 6), ("1.2e-4", 5), ("1.2e3", 0)):
            self.assertEqual(formatting.sensor_precision(raw), expected)

    def test_numeric_golden_values_and_locale(self):
        cases = (
            ("21.345", "°C", None, "en", None, "21.345 °C"),
            ("21.345", "°C", None, "pl-PL", {"sensor": {"display_precision": 1}}, "21,3 °C"),
            ("12.300", "kWh", None, "en", None, "12.300 kWh"),
            ("2.675", "V", None, "en", {"sensor": {"display_precision": 2}}, "2.68 V"),
            ("1.23456789", "", None, "pl_PL", None, "1,234568"),
            ("1.2e3", "W", None, "en", None, "1200 W"),
            (".125", "%", None, "en", None, "0.125 %"),
            ("-0.0001", "V", None, "en", {"sensor": {"display_precision": 2}}, "0.00 V"),
            ("-0", "", None, "pl", None, "0"),
            (" 12.50 ", "<b>V</b>", None, "en", None, "12.50 V"),
        )
        for raw, unit, device_class, language, options, expected in cases:
            with self.subTest(raw=raw, language=language):
                self.assertEqual(formatting.sensor_text(raw, unit, device_class, language, options), expected)

    def test_malformed_nonfinite_and_huge_values_are_unknown(self):
        for value in ("NaN", "sNaN", "Infinity", "+inf", "-inf",
                      "1.2.3", "1_000", "1,5", "", " ", True, None, [], {}):
            with self.subTest(value=value):
                self.assertEqual(formatting.sensor_text(value, "V"), "Unknown")
                self.assertEqual(formatting.sensor_text(value, "V", language="pl"), "Nieznany")

    def test_numeric_bounds_and_negative_zero(self):
        self.assertEqual(formatting.sensor_text("1000000000000000", "W"), "1000000000000000 W")
        self.assertEqual(formatting.sensor_text("1000000000000001", "W"), "Out of range")
        self.assertEqual(formatting.sensor_text("1e-1000000", "V"), "0.000000 V")
        self.assertEqual(formatting.sensor_text("-1e-1000000", "V"), "0.000000 V")
        self.assertNotIn("−", formatting.sensor_text("-12.5", "V"))

    def test_finite_numbers_outside_numeric_or_representation_bounds_are_not_missing_data(self):
        for value in ("1000000000000001", "-1000000000000001", "1e999999999", "1e999999999999999999999999", "9" * 500):
            with self.subTest(value=value):
                self.assertEqual(formatting.sensor_text(value, "V"), "Out of range")
                self.assertEqual(formatting.sensor_text(value, "V", language="pl"), "Poza zakresem")

    def test_custom_text_enum_and_timestamp_are_not_mistaken_for_numeric_measurements(self):
        for value in ("ready_to_use", "Comfort", "eco mode"):
            self.assertIsNone(formatting.sensor_text(value))
        for device_class in ("enum", "timestamp", "date", "uptime"):
            self.assertIsNone(formatting.sensor_text("1", device_class=device_class))
        self.assertIsNone(formatting.sensor_text("normal", unit={"bad": True}))

    def test_units_stay_as_ha_reports_them_and_output_is_bounded_plain_text(self):
        self.assertEqual(formatting.sensor_text("12.34", "<b>custom unit</b>"), "12.34 custom unit")
        self.assertEqual(formatting.sensor_text("5", {"not": "unit"}), "5")
        self.assertEqual(formatting.sensor_text("5", "KWh"), "5 KWh")
        result = formatting.sensor_text("123456789012345.123456", "<b>" + "x" * 1000 + "</b>")
        self.assertLessEqual(len(result), 40)
        self.assertNotIn("<", result)

    def test_fixed_unit_duration_golden_cases(self):
        for raw, unit, expected in (
            ("0", "s", "0 s"), ("90", "s", "1 min 30 s"),
            ("3661", "s", "1 h 1 min"), ("61.25", "s", "1 min 1.25 s"),
            ("1.5", "h", "1 h 30 min"), ("1.5", "d", "1 d 12 h"),
            ("1", "w", "7 d"), ("1500", "ms", "1.500 s"),
            ("250", "ms", "250 ms"), ("1000000", "μs", "1.000000 s"),
            ("250", "μs", "250 us"),
            ("-90", "s", "-1 min 30 s"), ("0.5", "s", "0.5 s"),
        ):
            with self.subTest(raw=raw, unit=unit):
                self.assertEqual(formatting.sensor_text(raw, unit, "duration", "en"), expected)

    def test_duration_locale_precision_and_no_accidental_generic_unit_conversion(self):
        self.assertEqual(formatting.sensor_text("61.25", "s", "duration", "pl"), "1 min 1,25 s")
        options = {"sensor": {"display_precision": 0}}
        self.assertEqual(formatting.sensor_text("89.6", "s", "duration", registry_options=options), "1 min 30 s")
        self.assertEqual(formatting.sensor_text("90", "s"), "90 s")
        self.assertEqual(formatting.sensor_text("2.5", "m", "duration"), "2.5 m")
        self.assertEqual(formatting.sensor_text("1", "y", "duration"), "1 y")
        self.assertEqual(formatting.sensor_text("-0.0", "s", "duration"), "0.0 s")

    def test_duration_bounds_and_invalid_values(self):
        for value in ("NaN", "Infinity", "12.3.4"):
            self.assertEqual(formatting.sensor_text(value, "d", "duration"), "Unknown")
        for value in ("1e100", "999999999", "-999999999"):
            self.assertEqual(formatting.sensor_text(value, "d", "duration"), "Out of range")
            self.assertEqual(formatting.sensor_text(value, "d", "duration", "pl"), "Poza zakresem")
        for raw in ("0", "0.1", "-90", "316224000", "-316224000"):
            value = formatting.sensor_text(raw, "s", "duration")
            self.assertLessEqual(len(value), 40)
            self.assertNotIn("−", value)

    def test_duration_and_numeric_formatting_do_not_depend_on_callers_decimal_context(self):
        with localcontext() as context:
            context.prec = 3
            self.assertEqual(formatting.sensor_text("316224000", "s", "duration"), "3660 d")
            self.assertEqual(formatting.sensor_text("123456789.1234", "V"), "123456789.1234 V")
            self.assertEqual(context.prec, 3)

    def test_owned_context_isolates_rounding_exponents_traps_and_parser_flags(self):
        for rounding in (ROUND_DOWN, ROUND_UP):
            with self.subTest(rounding=rounding), localcontext() as context:
                context.prec, context.Emin, context.Emax, context.rounding = 3, -2, 2, rounding
                for signal in (Inexact, Rounded, Overflow, Underflow, Subnormal, Clamped):
                    context.traps[signal] = True
                context.clear_flags()
                original = context.copy()
                options = {"sensor": {"display_precision": 1}}
                self.assertEqual(formatting.sensor_text("1.25", "V", registry_options=options), "1.2 V")
                self.assertEqual(formatting.sensor_text("100", "h", "duration"), "4 d 4 h")
                self.assertEqual(formatting.sensor_text("250", "μs", "duration"), "250 us")
                self.assertEqual(formatting.sensor_text("1e999999999999999999999999", "V"), "Out of range")
                self.assertEqual(formatting.sensor_text("NaN", "V"), "Unknown")
                self.assertEqual(dict(context.flags), dict(original.flags))
                self.assertEqual(dict(context.traps), dict(original.traps))
                self.assertEqual((context.prec, context.Emin, context.Emax, context.rounding), (3, -2, 2, rounding))
                self.assertFalse(context.flags[InvalidOperation])

    def test_new_duration_units_and_range_labels_use_existing_ascii_glyphs(self):
        values = [formatting.sensor_text("250", "μs", "duration", locale) for locale in ("en", "pl")]
        values += [formatting.sensor_text("1e20", "s", "duration", locale) for locale in ("en", "pl")]
        for value in values:
            self.assertTrue(value.isascii(), value)
            self.assertLessEqual(len(value), 40)
        self.assertEqual(values[:2], ["250 us", "250 us"])

    def test_exceptional_states_are_localized_before_other_formatting(self):
        for raw, en, pl in (("unknown", "Unknown", "Nieznany"), ("unavailable", "Unavailable", "Niedostępny")):
            self.assertEqual(formatting.sensor_text(raw, "s", "duration", "en"), en)
            self.assertEqual(formatting.sensor_text(raw, "s", "duration", "pl"), pl)

    def test_binary_known_class_fallbacks_and_no_unknown_to_safe_closed(self):
        for device_class in ("door", "window", "opening", "garage_door"):
            self.assertEqual(formatting.binary_fallback("on", device_class, "en"), "Open")
            self.assertEqual(formatting.binary_fallback("off", device_class, "pl"), "Zamknięte")
        for device_class in ("motion", "occupancy"):
            self.assertEqual(formatting.binary_fallback("on", device_class, "pl"), "Wykryto")
            self.assertEqual(formatting.binary_fallback("off", device_class, "en"), "Clear")
        self.assertEqual(formatting.binary_fallback("on", "presence", "en"), "Present")
        self.assertEqual(formatting.binary_fallback("off", "presence", "pl"), "Brak obecności")
        for state in ("unknown", "unavailable", "tampered_custom", "True", "1"):
            self.assertIsNone(formatting.binary_fallback(state, "door", "pl"))
        for device_class in (None, {}, "battery"):
            self.assertIsNone(formatting.binary_fallback("off", device_class))

    def test_language_selection_is_local_and_has_no_process_locale_side_effect(self):
        for language in ("pl", "PL-pl", "pl_PL"):
            self.assertEqual(formatting.display_language(language), "pl")
        for language in (None, {}, "de", "en-GB"):
            self.assertEqual(formatting.display_language(language), "en")


class SunEventFormattingTests(unittest.TestCase):
    NOW = datetime(2026, 10, 26, 10, 0, tzinfo=UTC)
    ATTRS = {"next_rising": "2026-10-27T05:42:00+00:00", "next_setting": "2026-10-26T15:21:00+00:00"}

    def render(self, state="above_horizon", attrs=None, zone="Europe/Warsaw", language="en", now=None):
        return formatting.sun_event_text(state, self.ATTRS if attrs is None else attrs, zone, language,
                                         now=self.NOW if now is None else now)

    def test_next_event_uses_chronological_instants_and_translated_date_time(self):
        self.assertEqual(self.render(), "Set 26.10 16:21")
        self.assertEqual(self.render(language="pl-PL"), "Zach. 26.10 16:21")
        attrs = dict(self.ATTRS, next_setting="2026-10-27T15:19:00+00:00")
        self.assertEqual(self.render(state="below_horizon", attrs=attrs, language="pl"), "Wsch. 27.10 06:42")
        # The earliest UTC instant wins, not string sort or the source horizon state.
        attrs = {"next_rising": "2026-10-27T09:00:00+14:00", "next_setting": "2026-10-26T20:00:00+00:00"}
        self.assertEqual(self.render(attrs=attrs, zone="UTC"), "Rise 26.10 19:00")

    def test_year_boundary_orders_full_UTC_dates_while_caption_is_compact(self):
        attrs = {"next_rising": "2027-01-01T05:42:00Z", "next_setting": "2026-12-31T23:30:00Z"}
        now = datetime(2026, 12, 31, 22, 0, tzinfo=UTC)
        self.assertEqual(self.render(attrs=attrs, now=now), "Set 01.01 00:30")
        self.assertEqual(self.render(attrs=attrs, now=now, language="pl"), "Zach. 01.01 00:30")

    def test_date_crosses_midnight_and_fractional_hour_timezone_is_preserved(self):
        attrs = {"next_rising": "2026-10-27T08:00:00Z", "next_setting": "2026-10-26T22:15:00Z"}
        self.assertEqual(self.render(attrs=attrs, zone="Asia/Kathmandu"), "Set 27.10 04:00")
        self.assertEqual(self.render(attrs=attrs, zone="America/New_York"), "Set 26.10 18:15")

    def test_spring_and_autumn_DST_convert_event_instant_without_fixed_offset(self):
        for date, expected in (("2026-03-28", "02:30"), ("2026-03-29", "03:30"),
                               ("2026-10-24", "03:30"), ("2026-10-25", "02:30")):
            attrs = {"next_rising": date + "T01:30:00+00:00", "next_setting": date + "T16:00:00+00:00"}
            reference = datetime.fromisoformat(date + "T00:00:00+00:00")
            self.assertEqual(self.render(attrs=attrs, now=reference), "Rise " + datetime.fromisoformat(date).strftime("%d.%m") + " " + expected)

    def test_missing_or_invalid_event_is_unknown_without_guessing_from_horizon(self):
        for raw in (None, True, {}, 0, "", "x" * 129, "bad", "2026-10-27T06:30:00", "2026-10-27T06:30:00+24:00"):
            for name in ("next_rising", "next_setting"):
                attrs = dict(self.ATTRS, **{name: raw})
                with self.subTest(name=name, raw=raw):
                    self.assertEqual(self.render(attrs=attrs), "Unknown")
                    self.assertEqual(self.render(attrs=attrs, language="pl"), "Nieznany")
        self.assertEqual(self.render(attrs={}), "Unknown")
        self.assertEqual(self.render(attrs=[]), "Unknown")

    def test_unknown_unavailable_invalid_timezone_and_clock_never_infer_event(self):
        for state, expected in (("unknown", "Nieznany"), ("unavailable", "Niedostępny"), ("on", "Nieznany"), (None, "Nieznany"), ({}, "Nieznany")):
            self.assertEqual(self.render(state=state, language="pl"), expected)
        for zone in (None, "", "Invalid/Zone", [], "x" * 129, "../UTC", "UTC\x00"):
            self.assertEqual(self.render(zone=zone), "Unknown")
        self.assertEqual(self.render(now=datetime(2026, 10, 26)), "Unknown")
        self.assertEqual(self.render(now="now"), "Unknown")

    def test_stale_equal_or_exhausted_events_do_not_render_past_data_as_next(self):
        for attrs in (dict(self.ATTRS, next_rising="2026-10-26T09:59:00+00:00"),
                      dict(self.ATTRS, next_setting="2026-10-26T10:00:00+00:00"),
                      {"next_rising": self.ATTRS["next_rising"], "next_setting": self.ATTRS["next_rising"]}):
            self.assertEqual(self.render(attrs=attrs), "Unknown")

    def test_output_and_input_are_bounded_without_process_locale_or_state_mutation(self):
        attrs = types.MappingProxyType(dict(self.ATTRS))
        before = dict(attrs)
        for language in ("en", "pl", "de", None):
            value = self.render(attrs=attrs, language=language)
            self.assertLessEqual(len(value), 40)
            self.assertNotIn("\n", value)
            self.assertNotIn("\x00", value)
        self.assertEqual(dict(attrs), before)


class State:
    def __init__(self, entity_id, state="on", attributes=None):
        self.entity_id, self.state, self.attributes = entity_id, state, attributes or {}


class Registry:
    def __init__(self, entries=None):
        self.entries, self.calls = entries or {}, []

    def async_get(self, entity_id):
        self.calls.append(entity_id)
        return self.entries.get(entity_id)


def _module(name, **values):
    result = types.ModuleType(name)
    result.__path__ = []
    result.__dict__.update(values)
    return result


class CardFormattingAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Restore the original HA modules after import, so discover may combine
        # this pure/shim suite with existing layout tests in either order.
        modules = {
            name: _module(name) for name in ("homeassistant", "homeassistant.helpers")
        }
        modules.update({
            "homeassistant.const": _module("homeassistant.const", ATTR_ENTITY_ID="entity_id"),
            "homeassistant.core": _module("homeassistant.core", HomeAssistant=object, State=State),
            "homeassistant.helpers.entity_registry": _module("homeassistant.helpers.entity_registry", async_get=lambda hass: hass.entity_registry),
            "homeassistant.helpers.device_registry": _module("homeassistant.helpers.device_registry", async_get=lambda hass: hass.device_registry),
            "homeassistant.helpers.area_registry": _module("homeassistant.helpers.area_registry", async_get=lambda hass: hass.area_registry),
            "homeassistant.helpers.translation": _module(
                "homeassistant.helpers.translation", async_translate_state=lambda _hass, state, *_rest: state,
                async_get_cached_translations=lambda hass, language, category: hass.translations.get((language, category), {})),
        })
        with patch.dict(sys.modules, modules):
            cls.cards = importlib.import_module(f"{PACKAGE}.cards")

    def environment(self, entries=None, language="en", translations=None):
        return types.SimpleNamespace(
            entity_registry=Registry(entries), config=types.SimpleNamespace(language=language),
            translations=translations or {},
        )

    def test_numeric_runtime_states_read_public_registry_options(self):
        entry = types.SimpleNamespace(options={"sensor": {"display_precision": 1, "suggested_display_precision": 3}})
        hass = self.environment({"sensor.room": entry})
        state = State("sensor.room", "22.348", {"unit_of_measurement": "°C"})
        self.assertEqual(self.cards._state_subtitle(hass, state, "pl"), "22,3 °C")
        self.assertEqual(hass.entity_registry.calls, ["sensor.room"])

    def test_missing_registry_and_entries_without_options_use_bounded_state_precision(self):
        state = State("sensor.room", "22.348765432", {"unit_of_measurement": "°C", "suggested_display_precision": 0})
        for entries in ({}, {"sensor.room": types.SimpleNamespace()}):
            hass = self.environment(entries)
            self.assertEqual(self.cards._state_subtitle(hass, state), "22.348765 °C")
        # A random state attribute does not stand in for HA's registry contract.
        self.assertEqual(self.cards._state_subtitle(self.environment(), State("sensor.room", "12.34", {"suggested_display_precision": 0})), "12.34")

    def test_number_and_input_number_use_current_state_unit_without_sensor_registry_options(self):
        for domain in ("number", "input_number"):
            hass = self.environment(language="pl")
            state = State(f"{domain}.target", "23.50", {"unit_of_measurement": "°C"})
            self.assertEqual(self.cards._state_subtitle(hass, state), "23,50 °C")
            self.assertEqual(hass.entity_registry.calls, [])

    def test_missing_unknown_and_unavailable_never_render_as_closed(self):
        hass = self.environment(language="pl")
        self.assertEqual(self.cards._state_subtitle(hass, None), "Niedostępny")
        for state, expected in (("unknown", "Nieznany"), ("unavailable", "Niedostępny"), ({}, "Nieznany")):
            result = self.cards._state_subtitle(hass, State("binary_sensor.door", state, {"device_class": "door"}))
            self.assertEqual(result, expected)

    def test_binary_class_and_platform_translations_win_over_semantic_fallbacks(self):
        entry = types.SimpleNamespace(platform="example", translation_key="contact")
        translations = {
            ("pl", "entity"): {"component.example.entity.binary_sensor.contact.state.on": "Własne otwarcie"},
            ("pl", "entity_component"): {"component.binary_sensor.entity_component.door.state.on": "Otwarte HA"},
        }
        hass = self.environment({"binary_sensor.door": entry}, language="en", translations=translations)
        state = State("binary_sensor.door", "on", {"device_class": "door"})
        self.assertEqual(self.cards._state_subtitle(hass, state, "pl"), "Własne otwarcie")
        hass.translations[("pl", "entity")] = {}
        self.assertEqual(self.cards._state_subtitle(hass, state, "pl"), "Otwarte HA")
        hass.translations[("pl", "entity_component")] = {"component.binary_sensor.entity_component._.state.on": "Włączony"}
        self.assertEqual(self.cards._state_subtitle(hass, state, "pl"), "Otwarte")

    def test_binary_fallback_uses_display_or_server_language_and_retains_custom_states(self):
        hass = self.environment(language="en")
        state = State("binary_sensor.window", "off", {"device_class": "window"})
        self.assertEqual(self.cards._state_subtitle(hass, state), "Closed")
        self.assertEqual(self.cards._state_subtitle(hass, state, "pl"), "Zamknięte")
        custom = State("binary_sensor.window", "tampered_custom", {"device_class": "window"})
        self.assertEqual(self.cards._state_subtitle(hass, custom, "pl"), "Tampered Custom")

    def test_custom_sensor_translations_remain_available_and_bounded(self):
        hass = self.environment(translations={("pl", "entity_component"): {
            "component.sensor.entity_component.enum.state.ready": "<b>Gotowe</b> " + "x" * 80,
        }})
        state = State("sensor.mode", "ready", {"device_class": "enum"})
        result = self.cards._state_subtitle(hass, state, "pl")
        self.assertTrue(result.startswith("Gotowe "))
        self.assertLessEqual(len(result), 40)
        self.assertNotIn("<", result)

    def test_presentation_keeps_titles_custom_icons_layout_and_actions_unchanged(self):
        state = State("binary_sensor.window", "on", {"device_class": "window"})
        hass = self.environment()
        hass.states = types.SimpleNamespace(get=lambda _entity_id: state)
        card = {"id": "stable", "slot": 2, "type": "sensor", "entity_id": "binary_sensor.window",
                "title": "Moje okno", "icon": "lock", "palette": "surface", "visible": True,
                "action": {"kind": "none"}}
        original = deepcopy(card)
        payload = self.cards.presentation_payload(hass, [card], language="pl")
        rendered = payload["cards"][2]
        self.assertEqual(rendered["subtitle"], "Otwarte")
        self.assertEqual(rendered["title"], "Moje okno")
        self.assertEqual(rendered["icon"], self.cards.ICONS["lock"])
        self.assertEqual(card, original)
        self.assertEqual(len(payload["cards"]), 16)
        self.assertEqual(payload["version"], 1)
        self.assertNotIn("action", rendered)

    def test_scene_and_button_timestamp_and_existing_service_resolution_are_unchanged(self):
        hass = self.environment()
        raw = "2026-10-24T10:00:00+00:00"
        for domain in ("scene", "button", "input_button"):
            self.assertEqual(self.cards._state_subtitle(hass, State(f"{domain}.test", raw)), raw)


    def test_sun_adapter_uses_current_HA_timezone_and_display_language(self):
        hass = self.environment(language="en")
        hass.config.time_zone = "Europe/Warsaw"
        attrs = {"next_rising": "2099-10-27T05:42:00+00:00", "next_setting": "2099-10-26T15:21:00+00:00"}
        state = State("sun.sun", "above_horizon", attrs)
        self.assertEqual(self.cards._state_subtitle(hass, state, "pl"), "Zach. 26.10 16:21")
        hass.config.time_zone = "Asia/Kathmandu"
        self.assertEqual(self.cards._state_subtitle(hass, state), "Set 26.10 21:06")
        self.assertEqual(hass.entity_registry.calls, [])
        del hass.config.time_zone
        self.assertEqual(self.cards._state_subtitle(hass, state), "Unknown")

    def test_sun_passive_presentation_has_full16_without_action_or_availability_field(self):
        hass = self.environment(language="pl")
        hass.config.time_zone = "UTC"
        state = State("sun.qa_owned", "below_horizon", {"next_rising": "2099-10-26T05:42:00Z", "next_setting": "2099-10-26T15:21:00Z"})
        hass.states = types.SimpleNamespace(get=lambda entity: state if entity == state.entity_id else None)
        card = {"id": "sun-card", "slot": 15, "type": "sensor", "entity_id": state.entity_id,
                "title": "Słońce", "icon": "clock", "palette": "surface", "visible": True,
                "action": {"kind": "none"}}
        original = deepcopy(card)
        payload = self.cards.presentation_payload(hass, [card], language="pl", press_enabled_supported=True)
        self.assertEqual(len(payload["cards"]), 16)
        chosen = payload["cards"][15]
        self.assertEqual(chosen["subtitle"], "Wsch. 26.10 05:42")
        self.assertEqual(chosen["title"], "Słońce")
        self.assertEqual(chosen["icon"], self.cards.ICONS["clock"])
        self.assertNotIn("action", chosen)
        self.assertNotIn("control_kind", chosen)
        self.assertNotIn("press_enabled", chosen)
        self.assertEqual(card, original)


if __name__ == "__main__":
    unittest.main()
