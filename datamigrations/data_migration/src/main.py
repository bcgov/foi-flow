from __future__ import annotations

import argparse
import importlib
import logging
from pathlib import Path
from typing import Callable

from axis_client import AxisClient
from config import Settings, load_settings
from csv_reader import read_request_ids
from foidb_client import FoidbClient
from migrator import RequestMigrator
from results_writer import write_results_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrate AXIS requests into FOIDB.")
    parser.add_argument("--input-csv", required=True, type=Path)
    parser.add_argument("--output-csv", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--confirm-delete", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    return parser


def _connect(module_name: str, connection_string: str):
    module = importlib.import_module(module_name)
    return module.connect(connection_string)


def create_migrator(settings: Settings, dry_run: bool = False) -> RequestMigrator:
    axis_connection = _connect(settings.axis_driver, settings.axis_connection_string)
    foidb_connection = _connect(settings.foidb_driver, settings.foidb_connection_string)
    return RequestMigrator(
        axis_client=AxisClient(
            axis_connection,
            excluded_statuses=settings.axis_excluded_statuses,
        ),
        foidb_client=FoidbClient(foidb_connection),
        created_by=settings.created_by,
        dry_run=dry_run,
    )


def run(argv: list[str] | None = None, migrator_factory: Callable[[Settings, bool], RequestMigrator] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO))

    request_ids = read_request_ids(args.input_csv)
    if args.limit is not None:
        request_ids = request_ids[: args.limit]

    settings = load_settings() if migrator_factory is None else Settings("", "", "", "")
    migrator = (migrator_factory or create_migrator)(settings, args.dry_run)

    if args.delete:
        results = [migrator.delete_request(request_id, confirm_delete=args.confirm_delete) for request_id in request_ids]
    else:
        results = [migrator.migrate_request(request_id) for request_id in request_ids]
    if args.output_csv:
        write_results_csv(args.output_csv, results)

    return 1 if any(result["status"] == "failed" for result in results) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
