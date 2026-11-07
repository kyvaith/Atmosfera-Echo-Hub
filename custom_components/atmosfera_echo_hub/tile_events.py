"""Bounded stateless card declarations; no service or transport authority."""

from .layout import CAROUSEL_SLOT_COUNT as SLOT_COUNT

EVENT_TYPE_PRESS = "press"
MAX_EVENT_CARDS = SLOT_COUNT - 2
PANEL_ACTION = {"kind": "control", "control": "panel", "property": "tile_event"}


def is_event_definition(card, *, visible_only=True):
    """A validated explicit Action may never retain an entity/service target."""
    return bool(
        isinstance(card, dict)
        and card.get("action") in ({"kind": "event"}, PANEL_ACTION)
        and card.get("type") == "action"
        and card.get("entity_id") == ""
        and not card.get("service")
        and type(card.get("slot")) is int
        and 2 <= card["slot"] < SLOT_COUNT
        and isinstance(card.get("id"), str)
        and 0 < len(card["id"]) <= 64
        and (not visible_only or card.get("visible") is True)
    )


def is_event_card(card, *, visible_only=True):
    """The original direct route; a panel launcher must never fire on Home."""
    return is_event_definition(card, visible_only=visible_only) and card["action"] == {"kind": "event"}


def is_event_panel(card, *, visible_only=True):
    return is_event_definition(card, visible_only=visible_only) and card["action"] == PANEL_ACTION


def event_unique_id(device_id, card_id):
    """Card identity survives moves and title changes on the same display."""
    return f"{device_id}_tile_event_{card_id}"
