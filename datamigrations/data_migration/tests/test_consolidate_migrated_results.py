import csv
from pathlib import Path

from consolidate_migrated_results import collect_migrated_rows, iter_result_csvs, run


def test_iter_result_csvs_returns_sorted_results_files(tmp_path: Path) -> None:
    (tmp_path / "BETA_results.csv").write_text("request_id,status\n", encoding="utf-8")
    (tmp_path / "ALPHA_results.csv").write_text("request_id,status\n", encoding="utf-8")
    (tmp_path / "ALPHA_requests.csv").write_text("request_id\n", encoding="utf-8")

    assert [path.name for path in iter_result_csvs(tmp_path)] == [
        "ALPHA_results.csv",
        "BETA_results.csv",
    ]


def test_collect_migrated_rows_filters_exact_migrated_status(tmp_path: Path) -> None:
    (tmp_path / "ALPHA_results.csv").write_text(
        "\n".join(
            [
                "request_id,status,reason,foirequest_id,started_at,finished_at",
                "CFD-2024-41700,migrated,,23102,2026-04-09T21:15:42.776513+00:00,2026-04-09T21:15:43.763609+00:00",
                "CFD-2024-41701,skipped,already migrated,,2026-04-09T21:16:00+00:00,2026-04-09T21:16:01+00:00",
                "CFD-2024-41702,MIGRATED,,23103,2026-04-09T21:17:00+00:00,2026-04-09T21:17:01+00:00",
            ]
        ),
        encoding="utf-8",
    )

    rows = collect_migrated_rows(tmp_path)

    assert rows == [
        {
            "request_id": "CFD-2024-41700",
            "status": "migrated",
            "reason": "",
            "foirequest_id": "23102",
            "started_at": "2026-04-09T21:15:42.776513+00:00",
            "finished_at": "2026-04-09T21:15:43.763609+00:00",
        }
    ]


def test_run_writes_only_migrated_rows(tmp_path: Path) -> None:
    (tmp_path / "ALPHA_results.csv").write_text(
        "\n".join(
            [
                "request_id,status,reason,foirequest_id,started_at,finished_at",
                "CFD-2024-41700,migrated,,23102,2026-04-09T21:15:42.776513+00:00,2026-04-09T21:15:43.763609+00:00",
                "CFD-2024-41701,failed,db error,,2026-04-09T21:16:00+00:00,2026-04-09T21:16:01+00:00",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "BETA_results.csv").write_text(
        "\n".join(
            [
                "request_id,status,reason,foirequest_id,started_at,finished_at",
                "CFD-2024-41702,migrated,,23104,2026-04-09T21:18:00+00:00,2026-04-09T21:18:01+00:00",
            ]
        ),
        encoding="utf-8",
    )

    output_file = tmp_path / "consolidated_migrated.csv"

    exit_code = run([str(tmp_path), "--output-csv", str(output_file)])

    assert exit_code == 0
    with output_file.open(newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert rows == [
        {
            "request_id": "CFD-2024-41700",
            "status": "migrated",
            "reason": "",
            "foirequest_id": "23102",
            "started_at": "2026-04-09T21:15:42.776513+00:00",
            "finished_at": "2026-04-09T21:15:43.763609+00:00",
        },
        {
            "request_id": "CFD-2024-41702",
            "status": "migrated",
            "reason": "",
            "foirequest_id": "23104",
            "started_at": "2026-04-09T21:18:00+00:00",
            "finished_at": "2026-04-09T21:18:01+00:00",
        },
    ]
