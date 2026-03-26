from __future__ import annotations

from datetime import datetime
import json
from typing import Any


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_optional_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.strptime(value, DATETIME_FORMAT)


def parse_optional_json(value: str | None) -> Any:
    if not value:
        return None
    return json.loads(value)
