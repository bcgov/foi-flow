from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping, Any


RESULT_FIELDS = [
    "request_id",
    "status",
    "reason",
    "foirequest_id",
    "started_at",
    "finished_at",
]


def write_results_csv(output_path: Path, results: Iterable[Mapping[str, Any]]) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        for result in results:
            writer.writerow({field: result.get(field, "") for field in RESULT_FIELDS})
