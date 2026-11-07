"""Bounded HA area mappings; vendor segment IDs never cross the device API."""

from collections.abc import Mapping

CLEAN_AREA = 16384
MAX_AREAS = 32
MAX_SEGMENTS_PER_AREA = 32


def has_area_capability(attributes):
    value = attributes.get("supported_features") if isinstance(attributes, Mapping) else None
    return (isinstance(value, int) and not isinstance(value, bool)
            and 0 <= value <= 2**53 - 1 and bool(value & CLEAN_AREA))


def mapped_area_ids(options):
    """Read Core's saved mapping without inventing rooms or segment names."""
    domain = options.get("vacuum") if isinstance(options, Mapping) else None
    mapping = domain.get("area_mapping") if isinstance(domain, Mapping) else None
    if not isinstance(mapping, Mapping) or not 1 <= len(mapping) <= MAX_AREAS:
        return ()
    result = []
    for area_id, segments in mapping.items():
        if (not isinstance(area_id, str) or not 1 <= len(area_id) <= 128
                or not isinstance(segments, list) or not 1 <= len(segments) <= MAX_SEGMENTS_PER_AREA
                or any(not isinstance(item, str) or not 1 <= len(item) <= 128 or not item.isprintable() for item in segments)
                or len(set(segments)) != len(segments)):
            return ()
        result.append(area_id)
    return tuple(result)


def area_command_allowed(state, attributes):
    return isinstance(state, str) and has_area_capability(attributes) and state in {"docked", "idle", "paused"}
