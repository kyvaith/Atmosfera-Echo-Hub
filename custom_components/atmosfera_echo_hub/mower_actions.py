"""Product admission for explicitly configured standard mower commands."""

from collections.abc import Mapping

FEATURES = {"start_mowing": 1, "pause": 2, "dock": 4}
ACTIVITIES = frozenset(("docked", "paused", "mowing", "returning", "error"))
ALLOWED = {
    "start_mowing": frozenset(("docked", "paused")),
    "pause": frozenset(("mowing", "returning")),
    "dock": frozenset(("mowing", "paused")),
}


def supported_operations(attributes):
    """Read Core feature flags without coercion or inferring a command."""
    value = attributes.get("supported_features") if isinstance(attributes, Mapping) else None
    # Core preserves IntFlag in State.attributes; JSON encodes the same value
    # as an ordinary integer. Bool remains an invalid capability observation.
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 2**53 - 1:
        return ()
    return tuple(operation for operation, feature in FEATURES.items() if value & feature)


def command_allowed(state, attributes, operation):
    """Reject error/unknown, redundant movement and missing capabilities."""
    return (isinstance(state, str) and operation in FEATURES
            and operation in supported_operations(attributes) and state in ALLOWED[operation])
