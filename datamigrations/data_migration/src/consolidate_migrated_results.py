from __future__ import annotations

import argparse
import csv
from pathlib import Path

from results_writer import RESULT_FIELDS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Consolidate migrated rows from *_results.csv files into one CSV."
    )
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    return parser


def iter_result_csvs(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*_results.csv") if path.is_file())


def collect_migrated_rows(directory: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for result_csv in iter_result_csvs(directory):
        with result_csv.open(newline="", encoding="utf-8") as csv_file:
            for row in csv.DictReader(csv_file):
                if row.get("status") != "migrated":
                    continue
                rows.append({field: row.get(field, "") for field in RESULT_FIELDS})
    return rows


def write_consolidated_results(output_csv: Path, rows: list[dict[str, str]]) -> None:
    with output_csv.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = collect_migrated_rows(args.directory)
    write_consolidated_results(args.output_csv, rows)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
