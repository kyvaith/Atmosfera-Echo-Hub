"""Bounded literal presentation labels; never source state or action policy."""

from copy import deepcopy

DOMAINS = frozenset(("sensor", "binary_sensor", "number", "input_number", "select", "input_select", "input_text", "input_datetime"))
MAX_LABELS = 8
MAX_TEXT_BYTES = 32
RESERVED_STATES = frozenset(("unknown", "unavailable"))


def eligible(card):
    return (card.get("type") == "sensor" and card.get("entity_id", "").partition(".")[0] in DOMAINS
            and type(card.get("slot")) is int and 2 <= card["slot"] < 32)


def validate_labels(value):
    """Keep exact keys/case/spacing; labels are literal text, not HTML/templates."""
    if not isinstance(value, dict) or len(value) > MAX_LABELS:
        raise ValueError("Expected at most eight state labels")
    for key, label in value.items():
        if key in RESERVED_STATES:
            raise ValueError("Unknown and unavailable cannot be renamed")
        for text in (key, label):
            if (not isinstance(text, str) or not text.strip() or not text.isprintable()
                    or len(text.encode("utf-8")) > MAX_TEXT_BYTES):
                raise ValueError("State and label must be printable text of 1..32 UTF-8 bytes")
    return deepcopy(value)


def mapped_label(card, source_state):
    if not eligible(card) or not isinstance(source_state, str) or source_state in RESERVED_STATES:
        return None
    labels = card.get("state_labels")
    if not isinstance(labels, dict):
        return None
    value = labels.get(source_state)
    return value if isinstance(value, str) else None
