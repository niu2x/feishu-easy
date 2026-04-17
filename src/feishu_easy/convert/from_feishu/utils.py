from __future__ import annotations

from typing import Any


def extract_dict(data: Any, path: str) -> Any:
    current: Any = data
    for part in path.split("/"):
        if isinstance(current, dict):
            if part not in current:
                return None
            current = current[part]
            continue

        if isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                return None
            if index < 0 or index >= len(current):
                return None
            current = current[index]
            continue

        return None

    return current
