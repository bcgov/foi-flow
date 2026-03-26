import csv
from pathlib import Path

from results_writer import write_results_csv


def test_write_results_csv_outputs_status_rows(tmp_path: Path) -> None:
    output_file = tmp_path / "results.csv"

    write_results_csv(
        output_file,
        [
            {
                "request_id": "XGR-2020-10982",
                "status": "migrated",
                "reason": "",
                "foirequest_id": 42,
                "started_at": "2026-03-25T10:00:00",
                "finished_at": "2026-03-25T10:00:10",
            },
            {
                "request_id": "XGR-2020-10983",
                "status": "skipped",
                "reason": "already migrated",
                "foirequest_id": "",
                "started_at": "2026-03-25T10:00:11",
                "finished_at": "2026-03-25T10:00:11",
            },
        ],
    )

    with output_file.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert rows == [
        {
            "request_id": "XGR-2020-10982",
            "status": "migrated",
            "reason": "",
            "foirequest_id": "42",
            "started_at": "2026-03-25T10:00:00",
            "finished_at": "2026-03-25T10:00:10",
        },
        {
            "request_id": "XGR-2020-10983",
            "status": "skipped",
            "reason": "already migrated",
            "foirequest_id": "",
            "started_at": "2026-03-25T10:00:11",
            "finished_at": "2026-03-25T10:00:11",
        },
    ]
