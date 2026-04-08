from __future__ import annotations

from datetime import datetime
import json
from typing import Any


DATETIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
]


def parse_optional_datetime(value: str | datetime | None) -> datetime | None:
    if not value:
        return None

    # If it's already a datetime, just return it
    if isinstance(value, datetime):
        return value

    # Try parsing string formats
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue

    return None


def parse_optional_json(value: str | None) -> Any:
    if not value:
        return None
    return json.loads(value)
