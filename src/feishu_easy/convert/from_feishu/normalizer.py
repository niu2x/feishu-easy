from __future__ import annotations

from typing import Any


def normalize_title(title: Any) -> str | None:
    if not isinstance(title, str):
        return None

    text = title.strip()
    if not text:
        return None

    return text
