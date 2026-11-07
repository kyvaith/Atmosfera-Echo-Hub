"""Admission for explicit standard StateVacuumEntity commands (Core 2026.7)."""

from collections.abc import Mapping

FEATURES = {"start": 8192, "pause": 4, "stop": 8, "return_to_base": 16,
            "locate": 512, "clean_spot": 1024}
ACTIVITIES = frozenset(("cleaning", "docked", "idle", "paused", "returning", "error"))
ALLOWED = {
    "start": frozenset(("docked", "idle", "paused")),
    "pause": frozenset(("cleaning", "returning")),
    "stop": frozenset(("cleaning", "paused", "returning")),
    "return_to_base": frozenset(("cleaning", "idle", "paused")),
    "locate": ACTIVITIES,
    "clean_spot": frozenset(("docked", "idle", "paused")),
}


def supported_operations(attributes):
    """Accept real Core IntFlags, never coerce bool or legacy power flags."""
    value = attributes.get("supported_features") if isinstance(attributes, Mapping) else None
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 2**53 - 1:
        return ()
    return tuple(operation for operation, feature in FEATURES.items() if value & feature)


def command_allowed(state, attributes, operation):
    """Check observed activity without predicting or substituting a command."""
    return (isinstance(state, str) and operation in FEATURES
            and operation in supported_operations(attributes) and state in ALLOWED[operation])
