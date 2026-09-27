"""Small text normalization helpers shared by display integrations."""

from __future__ import annotations

import html
from html.parser import HTMLParser
from typing import Any


class _PlainTextParser(HTMLParser):
    """Collect visible text without carrying markup to the display."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data:
            self.parts.append(data)


def plain_text(value: Any, maximum: int) -> str:
    """Return bounded text with entities decoded and HTML markup removed."""
    parser = _PlainTextParser()
    parser.feed(str(value or ""))
    parser.close()
    text = html.unescape(" ".join(parser.parts))
    text = " ".join(text.replace("\n", " ").replace("\r", " ").split())
    return text[:maximum]
