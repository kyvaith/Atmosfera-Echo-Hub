"""Bounded notification history. HA owns retention; the display owns no archive."""

from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass
from uuid import uuid4

from .text import plain_text

CAPACITY = 100
RETENTION_SECONDS = 24 * 60 * 60
PAGE_SIZE = 8
MAX_SEQUENCE = 2**31 - 1
_ID = re.compile(r"^[a-f0-9]{32}$")


@dataclass(frozen=True, slots=True)
class Notice:
    id: str
    created: int
    title: str
    message: str


class NotificationHistory:
    """Newest first, stable IDs, bounded wire pages, no executable payloads."""

    def __init__(self, clock=time.time):
        self.clock = clock
        self.records: list[Notice] = []

    def prune(self) -> None:
        now = int(self.clock())
        self.records = [
            r for r in self.records if now - RETENTION_SECONDS < r.created <= now
        ][:CAPACITY]

    def load(self, data) -> None:
        self.records = []
        if not isinstance(data, list):
            return
        seen = set()
        for raw in data[:CAPACITY]:
            if not isinstance(raw, dict) or set(raw) != {
                "id",
                "created",
                "title",
                "message",
            }:
                continue
            if (
                not isinstance(raw["id"], str)
                or not _ID.fullmatch(raw["id"])
                or raw["id"] in seen
                or type(raw["created"]) is not int
                or not isinstance(raw["title"], str)
                or not isinstance(raw["message"], str)
            ):
                continue
            seen.add(raw["id"])
            self.records.append(
                Notice(
                    raw["id"],
                    raw["created"],
                    plain_text(raw["title"], 64),
                    plain_text(raw["message"], 384),
                )
            )
        self.records.sort(key=lambda r: r.created, reverse=True)
        self.prune()

    def dump(self) -> list[dict]:
        self.prune()
        return [asdict(r) for r in self.records]

    def add(self, title: str, message: str) -> Notice:
        self.prune()
        record = Notice(
            uuid4().hex,
            int(self.clock()),
            plain_text(title, 64),
            plain_text(message, 384),
        )
        self.records.insert(0, record)
        del self.records[CAPACITY:]
        return record

    def dismiss(self, notice_id: str) -> bool:
        self.prune()
        for index, record in enumerate(self.records):
            if record.id == notice_id:
                del self.records[index]
                return True
        return False

    def page(self, offset: int, *, version: int = 1) -> dict:
        self.prune()
        if version >= 2:
            offset = max(0, min(offset, len(self.records) - PAGE_SIZE))
        else:
            offset = min(
                offset // PAGE_SIZE * PAGE_SIZE,
                max(0, (len(self.records) - 1) // PAGE_SIZE * PAGE_SIZE),
            )
        rows = [
            {
                "id": r.id,
                "title": r.title,
                "message": r.message[: 96 if version >= 2 else 64],
                **({"created": r.created} if version >= 2 else {}),
            }
            for r in self.records[offset : offset + PAGE_SIZE]
        ]
        return {"offset": offset, "total": len(self.records), "rows": rows}

    def detail(self, notice_id: str) -> dict | None:
        self.prune()
        return next((asdict(r) for r in self.records if r.id == notice_id), None)


def decode_request(payload: str) -> dict:
    """Strict schema: a display cannot supply a user, service, URL or text."""
    if not isinstance(payload, str) or len(payload.encode("utf-8")) > 512:
        raise ValueError("Invalid notification request")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate key")
            result[key] = value
        return result

    data = json.loads(payload, object_pairs_hook=unique)
    base = {"v", "channel", "seq", "op", "offset"}
    if not isinstance(data, dict) or data.get("op") not in (
        "page",
        "open",
        "dismiss",
        "activate",
    ):
        raise ValueError("Invalid operation")
    expected = base if data["op"] == "page" else base | {"id"}
    if (
        set(data) != expected
        or type(data["v"]) is not int
        or data["v"] not in (1, 2, 3)
        or (data["op"] == "activate" and data["v"] != 3)
    ):
        raise ValueError("Invalid schema")
    if not isinstance(data["channel"], str) or not _ID.fullmatch(data["channel"]):
        raise ValueError("Invalid channel")
    if type(data["seq"]) is not int or not 1 <= data["seq"] <= MAX_SEQUENCE:
        raise ValueError("Invalid sequence")
    if (
        type(data["offset"]) is not int
        or not 0 <= data["offset"] < CAPACITY
        or (data["v"] == 1 and data["offset"] % PAGE_SIZE)
    ):
        raise ValueError("Invalid offset")
    if "id" in data and (
        not isinstance(data["id"], str) or not _ID.fullmatch(data["id"])
    ):
        raise ValueError("Invalid notification ID")
    return data
