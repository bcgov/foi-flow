from __future__ import annotations

import csv
from pathlib import Path


def read_request_ids(csv_path: Path) -> list[str]:
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("Input CSV must include a request_id column.")

        request_id_column = "request_id" if "request_id" in reader.fieldnames else "Request" if "Request" in reader.fieldnames else None
        if request_id_column is None:
            raise ValueError("Input CSV must include a request_id column.")

        request_ids: list[str] = []
        seen: set[str] = set()
        for row in reader:
            value = (row.get(request_id_column) or "").strip()
            if not value or value in seen:
                continue
            seen.add(value)
            request_ids.append(value)

    return request_ids
