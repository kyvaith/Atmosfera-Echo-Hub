"""Focused offline fixtures for the proposed numeric-domain boundary."""

import importlib.util
import json
import sys
import unittest
from dataclasses import FrozenInstanceError
from decimal import FloatOperation, Inexact, Rounded, localcontext
from pathlib import Path

# Import the pure module directly, without executing the HA integration package.
_ROOT = Path(__file__).resolve().parents[2]
_SOURCE = _ROOT / "custom_components" / "atmosfera_echo_hub" / "numeric_domain.py"
_SPEC = importlib.util.spec_from_file_location("_atmosfera_numeric_domain_test", _SOURCE)
assert _SPEC is not None and _SPEC.loader is not None
_NUMERIC = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _NUMERIC
_SPEC.loader.exec_module(_NUMERIC)
MAX_STEPS = _NUMERIC.MAX_STEPS
NumericDomain = _NUMERIC.NumericDomain
NumericDomainError = _NUMERIC.NumericDomainError


def domain(low="-2.5", high="1", step="0.25", unit="°C"):
    return NumericDomain.from_ha({"min": low, "max": high, "step": step, "unit_of_measurement": unit})


class NumericDomainTests(unittest.TestCase):
    def test_signed_fractional_round_trip_fixtures(self):
        fixtures = (
            ("-2.5", "1", "0.25", ("-2.5", "-2.25", "0", "1"), (0, 1, 10, 14)),
            ("-0.2", "0.2", "0.15", ("-0.2", "-0.05", "0.1"), (0, 1, 2)),
            ("-0.000002", "0.000002", "0.000001", ("-0.000002", "0", "0.000002"), (0, 2, 4)),
            ("1000000000000", "1000000000000", "0.000001", ("1000000000000",), (0,)),
        )
        for low, high, step, values, indices in fixtures:
            selected = domain(low, high, step)
            for value, index in zip(values, indices, strict=True):
                with self.subTest(low=low, step=step, value=value):
                    self.assertEqual(selected.exact_index(value), index)
                    self.assertEqual(str(selected.value_at(index)), value)

    def test_every_reachable_step_is_bijective(self):
        for selected in (domain(), domain("-1.2", "3.1", "0.07"), domain("0", "1", "0.03")):
            values = [selected.value_at(index) for index in range(selected.max_index + 1)]
            self.assertEqual(values, sorted(set(values)))
            self.assertEqual([selected.exact_index(value) for value in values], list(range(selected.max_index + 1)))

    def test_non_aligned_max_is_bound_not_invented_endpoint(self):
        selected = domain("0", "1", "0.3")
        self.assertEqual(selected.max_index, 3)
        self.assertEqual(str(selected.value_at(3)), "0.9")
        self.assertEqual(selected.descriptor()["max"], "1")
        self.assertIsNone(selected.observed_index("1"))
        self.assertEqual(selected.nearest_index("1"), 3)
        with self.assertRaisesRegex(NumericDomainError, "index"):
            selected.value_at(4)

    def test_minimum_is_lattice_anchor_not_zero(self):
        selected = domain("-0.2", "0.2", "0.15")
        self.assertEqual(str(selected.value_at(1)), "-0.05")
        self.assertIsNone(selected.observed_index("0"))

    def test_zero_is_exact_numeric_value_and_index_zero_is_minimum(self):
        selected = domain("-1", "1", "0.25", "%")
        self.assertEqual(str(selected.command_value(0, current=selected)), "-1")
        self.assertEqual(str(selected.command_value(4, current=selected)), "0")
        self.assertIsNotNone(selected.command_value(4, current=selected))
        self.assertEqual(str(domain("0", "1", "0.25").command_value(0, current=domain("0", "1", "0.25"))), "0")

    def test_unknown_invalid_and_float_noise_do_not_fabricate_zero(self):
        selected = domain("0", "1", "0.1")
        for value in (None, "unknown", "unavailable", "", True, [], "0.15", "-1", "2", float("nan"), float("inf"), 0.1 + 0.2):
            with self.subTest(value=repr(value)):
                self.assertIsNone(selected.observed_index(value))
        self.assertEqual(selected.observed_index("0"), 0)
        self.assertEqual(selected.observed_index(0.3), 3)

    def test_exact_decimal_work_is_independent_of_global_context(self):
        with localcontext() as context:
            context.prec = 1
            context.traps[Inexact] = context.traps[Rounded] = context.traps[FloatOperation] = True
            selected = domain(-1.234567, 1.234567, 0.000007)
            value = selected.value_at(100_000)
            self.assertEqual(str(value), "-0.534567")
            self.assertEqual(selected.exact_index(value), 100_000)
            self.assertEqual(selected.nearest_index("-0.534566"), 100_000)
            self.assertEqual(NumericDomain.from_descriptor(selected.descriptor()), selected)

    def test_one_million_intervals_boundary(self):
        selected = domain("0", "1", "0.000001")
        self.assertEqual(selected.max_index, MAX_STEPS)
        self.assertEqual(str(selected.value_at(MAX_STEPS)), "1")
        for low, high in (("0", "1.000001"), ("-0.000001", "1")):
            with self.subTest(low=low, high=high), self.assertRaisesRegex(NumericDomainError, "step_limit"):
                domain(low, high, "0.000001")

    def test_six_places_are_normalized_exactly_without_rounding(self):
        selected = domain("-0.0000010000", "0.0000010000", "1e-6")
        self.assertEqual(selected.descriptor()["min"], "-0.000001")
        self.assertEqual(selected.descriptor()["step"], "0.000001")
        for value in ("0.0000001", "-0.0000001", "1.0000001"):
            with self.subTest(value=value), self.assertRaisesRegex(NumericDomainError, "precision"):
                domain(value, "2", "1")
        self.assertEqual(domain("-0.0000000", "+1.0000000", "0.1000000").descriptor()["min"], "0")

    def test_strict_numeric_types_lexemes_and_magnitude(self):
        invalid = (True, False, None, {}, [], " 0", "0 ", "01", ".1", "1.", "1,5", "１２", "NaN", "Infinity", "1e1000", "1e-1000", "1" * 65, "1000000000000.000001", -(10**100))
        for value in invalid:
            with self.subTest(value=repr(value)), self.assertRaises(NumericDomainError):
                domain(value, "1", "0.1")

    def test_missing_or_invalid_provider_metadata_is_not_defaulted(self):
        for attrs in ({}, {"min": 0, "max": 1}, {"min": 0, "step": 1}, {"max": 1, "step": 1}, None, []):
            with self.subTest(attrs=attrs), self.assertRaises(NumericDomainError):
                NumericDomain.from_ha(attrs)
        for low, high, step in (("2", "1", "1"), ("0", "1", "0"), ("0", "1", "-0.1")):
            with self.subTest(step=step), self.assertRaises(NumericDomainError):
                domain(low, high, step)

    def test_unit_is_bounded_utf8_and_plain_text(self):
        for unit in ("", "%", "°C", "m³/h", "x" * 32, "℃" * 10):
            with self.subTest(unit=unit):
                self.assertEqual(domain(unit=unit).unit, unit)
        for unit in (None, 1, "x" * 33, "℃" * 11, "a\n", "\x00", "\x7f", "\u202e", "\ud800"):
            with self.subTest(unit=repr(unit)), self.assertRaises(NumericDomainError):
                domain(unit=unit)

    def test_strict_integer_index_and_one_step_direction(self):
        selected = domain()
        for index in (True, False, 0.0, "0", None, -1, selected.max_index + 1):
            with self.subTest(index=index), self.assertRaises(NumericDomainError):
                selected.value_at(index)
        for direction in (True, False, 0, 2, -2, 1.0, "1", None):
            with self.subTest(direction=direction), self.assertRaises(NumericDomainError):
                selected.adjacent_index(0, direction)
        self.assertEqual(selected.adjacent_index(0, -1), 0)
        self.assertEqual(selected.adjacent_index(0, 1), 1)
        self.assertEqual(selected.adjacent_index(selected.max_index, 1), selected.max_index)
        self.assertEqual(selected.adjacent_index(selected.max_index, -1), selected.max_index - 1)

    def test_single_reachable_value_has_no_stepper_motion(self):
        selected = domain("1", "1.1", "1")
        self.assertEqual(selected.max_index, 0)
        self.assertEqual(selected.adjacent_index(0, -1), 0)
        self.assertEqual(selected.adjacent_index(0, 1), 0)

    def test_explicit_midpoint_quantization_always_chooses_larger_value(self):
        selected = domain("-1", "1", "0.5")
        for value, expected in (("-0.75", 1), ("-0.25", 2), ("0.25", 3), ("0.75", 4), ("-0.750001", 0)):
            with self.subTest(value=value):
                self.assertEqual(selected.nearest_index(value), expected)
        for value in ("-1.000001", "1.000001"):
            with self.assertRaisesRegex(NumericDomainError, "value_range"):
                selected.nearest_index(value)

    def test_live_domain_change_rejects_old_candidate(self):
        selected = domain()
        for changed in (domain("-2.25"), domain(high="1.25"), domain(step="0.5"), domain(unit="K"), None):
            with self.subTest(changed=changed), self.assertRaisesRegex(NumericDomainError, "domain_changed"):
                selected.command_value(4, current=changed)
        equivalent = domain("-2.5000", "1.000", "0.250000", "°C")
        self.assertEqual(selected.command_value(4, current=equivalent), selected.value_at(4))

    def test_descriptor_round_trip_canonical_and_bounded(self):
        selected = domain()
        encoded = json.dumps(selected.descriptor(), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        self.assertLess(len(encoded.encode("utf-8")), 512)
        self.assertEqual(NumericDomain.from_descriptor(json.loads(encoded)), selected)
        external = selected.descriptor()
        external["min"] = "999"
        self.assertEqual(selected.descriptor()["min"], "-2.5")

    def test_descriptor_rejects_noncanonical_extra_and_wrong_fields(self):
        selected = domain()
        changes = ({"schema": "light_brightness_v1"}, {"min": -2.5}, {"min": "-2.500"}, {"max": "+1"}, {"step": "2.5e-1"}, {"max_index": True}, {"max_index": 13}, {"extra": 0}, {"unit": None})
        for change in changes:
            with self.subTest(change=change), self.assertRaises(NumericDomainError):
                NumericDomain.from_descriptor(selected.descriptor() | change)
        missing = selected.descriptor()
        del missing["unit"]
        with self.assertRaises(NumericDomainError):
            NumericDomain.from_descriptor(missing)

    def test_service_boundary_retains_signed_decimal_intent_and_numeric_zero(self):
        selected = domain("-1", "1", "0.1")
        for index in range(selected.max_index + 1):
            value = selected.service_value(index, current=selected)
            self.assertIn(type(value), (int, float))
            self.assertEqual(selected.exact_index(value), index)
        self.assertIs(type(selected.service_value(10, current=selected)), int)
        self.assertEqual(selected.service_value(10, current=selected), 0)

    def test_lossy_float_service_boundary_is_refused(self):
        for selected in (domain("999999999999.999999", "1000000000000", "0.000001"),
                         domain("-1000000000000", "-999999999999.999999", "0.000001")):
            index = 0 if selected.minimum_micro > 0 else 1
            self.assertEqual(str(selected.command_value(index, current=selected)),
                             "999999999999.999999" if index == 0 else "-999999999999.999999")
            with self.assertRaisesRegex(NumericDomainError, "service_precision"):
                selected.service_value(index, current=selected)
        selected = domain("1000000000000", "1000000000000", "1")
        self.assertEqual(selected.service_value(0, current=selected), 10**12)

    def test_service_boundary_rechecks_live_domain_and_index(self):
        selected = domain()
        with self.assertRaisesRegex(NumericDomainError, "domain_changed"):
            selected.service_value(0, current=domain(unit="K"))
        with self.assertRaisesRegex(NumericDomainError, "index"):
            selected.service_value(True, current=selected)

    def test_immutable_domain_cannot_be_changed_mid_interaction(self):
        selected = domain()
        with self.assertRaises(FrozenInstanceError):
            selected.step_micro = 1
        for values in ((True, 1, 1, ""), (0, 1, 0, ""), (0, 1, -1, ""), (0, 1, 1, None)):
            with self.subTest(values=values), self.assertRaises(NumericDomainError):
                NumericDomain(*values)


if __name__ == "__main__":
    unittest.main()
