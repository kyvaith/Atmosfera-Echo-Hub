"""Cover endpoints and capabilities without HA, MQTT or a physical actuator."""

import importlib
from enum import IntFlag
import unittest

import test_ha_layout  # Registers only the narrow host fixture package.

cover = importlib.import_module("_atmosfera_test.cover_domain")


class CoverDomainTests(unittest.TestCase):
    def test_ha_in_memory_intflag_has_the_same_caps_as_its_json_integer(self):
        class Features(IntFlag):
            OPEN = 1
            CLOSE = 2
            STOP = 8

        value = Features.OPEN | Features.CLOSE | Features.STOP
        self.assertIsNot(type(value), int)
        self.assertEqual(self.domain(value), self.domain(11))
        self.assertEqual(self.domain(Features.OPEN).descriptor(),
                         {"open": True, "stop": False, "close": False})

    def domain(self, features=11, **services):
        return cover.CoverDomain.from_ha({"supported_features": features},
                                        {"open_cover": True, "close_cover": True, "stop_cover": True} | services)

    def observation(self, state, position=None):
        return cover.CoverObservation.from_ha(state, {"current_position": position})

    def test_each_operation_requires_its_own_feature_and_domain_service(self):
        domain = self.domain()
        self.assertEqual(domain.descriptor(), {"open": True, "stop": True, "close": True})
        self.assertEqual(self.domain(1).descriptor(), {"open": True, "stop": False, "close": False})
        self.assertEqual(self.domain(stop_cover=False).descriptor(), {"open": True, "stop": False, "close": True})
        for bad in (None, True, "11", -1, 2**31, 0, 16):
            with self.subTest(features=bad), self.assertRaises(cover.CoverDomainError):
                self.domain(bad)

    def test_partial_or_unknown_position_open_state_is_not_a_full_open_endpoint(self):
        for position in (None, 50, 99):
            value = self.observation("open", position)
            self.assertTrue(value.permits("open"))
            self.assertFalse(value.already_matches("open"))
        full = self.observation("open", 100)
        self.assertFalse(full.permits("open"))
        self.assertTrue(full.already_matches("open"))

    def test_reversing_movement_at_last_endpoint_remains_possible(self):
        opening, closing = self.observation("opening", 0), self.observation("closing", 100)
        self.assertFalse(opening.permits("open"))
        self.assertTrue(opening.permits("close"))
        self.assertTrue(opening.permits("stop"))
        self.assertFalse(closing.permits("close"))
        self.assertTrue(closing.permits("open"))
        self.assertTrue(closing.permits("stop"))

    def test_stationary_stop_and_closed_close_are_noops(self):
        for state in ("open", "closed"):
            value = self.observation(state)
            self.assertTrue(value.already_matches("stop"))
            self.assertFalse(value.permits("stop"))
        self.assertTrue(self.observation("closed").already_matches("close"))
        self.assertFalse(self.observation("closed").permits("close"))

    def test_unavailable_unknown_or_invalid_position_never_invents_a_percentage(self):
        for raw in (None, True, -1, 101, "50", 50.5, float("nan"), float("inf")):
            value = self.observation("open", raw)
            self.assertIsNone(value.position)
            self.assertTrue(value.available)
        for state in ("unknown", "unavailable", "stopped", None, True):
            value = self.observation(state, 50)
            self.assertFalse(value.available)
            self.assertIsNone(value.position)
            for operation in cover.OPERATIONS:
                self.assertFalse(self.domain().allows(operation, value))

    def test_only_semantic_capabilities_change_and_disallowed_operations_cannot_escape(self):
        self.assertEqual(self.domain(), self.domain(11 | 16 | 32))
        with self.assertRaises(cover.CoverDomainError):
            self.domain().supports("set_position")
        with self.assertRaises(cover.CoverDomainError):
            self.observation("open").permits("toggle")
