from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

import main


DEFAULT_LIMIT = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate missing *_results.csv files for request CSVs in a directory."
    )
    parser.add_argument("directory", type=Path)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--log-level", default="INFO")
    return parser


def iter_request_csvs(directory: Path) -> list[Path]:
    return sorted(path for path in directory.glob("*_requests.csv") if path.is_file())


def build_output_path(request_csv: Path) -> Path:
    if not request_csv.name.endswith("_requests.csv"):
        raise ValueError(f"Expected a *_requests.csv file, got '{request_csv.name}'")
    return request_csv.with_name(request_csv.name.replace("_requests.csv", "_results.csv"))


def collect_pending_request_files(directory: Path, limit: int = DEFAULT_LIMIT) -> list[Path]:
    pending: list[Path] = []
    for request_csv in iter_request_csvs(directory):
        if build_output_path(request_csv).exists():
            continue
        pending.append(request_csv)
        if len(pending) >= limit:
            break
    return pending


def build_main_argv(request_csv: Path, output_csv: Path, log_level: str) -> list[str]:
    argv = [
        "--input-csv",
        str(request_csv),
        "--output-csv",
        str(output_csv),
        "--skip-suffix-requests",
    ]
    if log_level.upper() != "INFO":
        argv.extend(["--log-level", log_level])
    return argv


def run(
    argv: list[str] | None = None,
    command_runner: Callable[[list[str]], int] | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    runner = command_runner or main.run

    pending_files = collect_pending_request_files(args.directory, limit=args.limit)
    exit_codes = [
        runner(build_main_argv(request_csv, build_output_path(request_csv), args.log_level))
        for request_csv in pending_files
    ]
    return 1 if any(code != 0 for code in exit_codes) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
