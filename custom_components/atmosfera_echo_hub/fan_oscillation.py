"""Strict observed oscillation; never infer a fan's oscillation from its power."""

from collections.abc import Mapping


def oscillation_value(entity_id, state, attributes):
    """A missing or malformed attribute is unknown, including numeric zero/one."""
    if not entity_id.startswith("fan.") or state not in ("on", "off") or not isinstance(attributes, Mapping):
        return None
    features = attributes.get("supported_features")
    if not isinstance(features, int) or isinstance(features, bool) or features < 0 or not features & 2:
        return None
    value = attributes.get("oscillating")
    return value if type(value) is bool else None
