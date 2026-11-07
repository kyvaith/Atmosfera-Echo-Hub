"""Bounded choice values remain exact at the eventual service boundary."""

from dataclasses import FrozenInstanceError
import importlib
import unittest

import test_ha_layout as base

choice = importlib.import_module(f"{base.layout.__package__}.choice_domain")


class ChoiceDomainTests(unittest.TestCase):
    def test_exact_order_whitespace_case_and_unicode_are_not_normalized(self):
        values = ["Eco", "eco", " Eco ", "Żółty", "A\u0301", "Á", '"\\']
        domain = choice.ChoiceDomain.from_ha({"options": values})
        values[0] = "Changed"
        self.assertEqual(domain.options[0], "Eco")
        for index, value in enumerate(domain.options):
            self.assertEqual(domain.observed_index(value), index)
            self.assertEqual(domain.service_value(index, current=domain), value)
        self.assertNotEqual(
            domain, choice.ChoiceDomain(tuple(reversed(domain.options)))
        )
        with self.assertRaises(FrozenInstanceError):
            domain.options = ()

    def test_complete_list_is_bounded_and_never_truncated_or_deduplicated(self):
        for value in (None, {}, "Eco", (), [], ["a"] * 2, [str(i) for i in range(9)]):
            with self.subTest(value=value), self.assertRaises(choice.ChoiceDomainError):
                choice.ChoiceDomain.from_options(value)
        valid = choice.ChoiceDomain.from_options([str(i) for i in range(8)])
        self.assertEqual(len(valid.options), 8)
        with self.assertRaises(choice.ChoiceDomainError):
            choice.ChoiceDomain(["a"])
        for value in (None, [], "options", {"options": iter(["a"])}):
            with self.subTest(value=value), self.assertRaises(choice.ChoiceDomainError):
                choice.ChoiceDomain.from_ha(value)

    def test_utf8_byte_bounds_and_control_or_surrogate_rejection(self):
        for text in ("a" * 32, "ą" * 16, "🌡" * 8):
            self.assertEqual(choice.ChoiceDomain.from_options([text]).value_at(0), text)
        for text in (
            "",
            "a" * 33,
            "ą" * 17,
            "🌡" * 9,
            "a\x00b",
            "a\nb",
            "a\tb",
            "\ud800",
            "\u202eabc",
            None,
            True,
            1,
        ):
            with (
                self.subTest(text=repr(text)),
                self.assertRaises(choice.ChoiceDomainError),
            ):
                choice.ChoiceDomain.from_options([text])

    def test_unknown_is_not_option_zero_and_indices_are_strict(self):
        domain = choice.ChoiceDomain.from_options(["Eco", "Boost", "Unknown"])
        for value in (None, True, 0, "", "missing", "unknown", "unavailable"):
            self.assertIsNone(domain.observed_index(value))
        self.assertEqual(domain.observed_index("Eco"), 0)
        for reserved in ("unknown", "unavailable"):
            with self.assertRaises(choice.ChoiceDomainError):
                choice.ChoiceDomain.from_options(["Eco", reserved])
        for value in (None, False, True, -1, 3, "0", 0.0):
            with self.subTest(value=value), self.assertRaises(choice.ChoiceDomainError):
                domain.value_at(value)

    def test_changed_list_cannot_reinterpret_a_captured_index(self):
        domain = choice.ChoiceDomain.from_options(["Eco", "Boost"])
        for current in (
            choice.ChoiceDomain.from_options(["Boost", "Eco"]),
            choice.ChoiceDomain.from_options(["Eco"]),
            None,
        ):
            with self.assertRaises(choice.ChoiceDomainError):
                domain.service_value(1, current=current)
        self.assertEqual(
            domain.service_value(
                1, current=choice.ChoiceDomain.from_options(["Eco", "Boost"])
            ),
            "Boost",
        )


if __name__ == "__main__":
    unittest.main()
