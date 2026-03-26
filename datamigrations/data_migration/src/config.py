from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    axis_driver: str
    axis_connection_string: str
    foidb_driver: str
    foidb_connection_string: str
    axis_office_code: str = "CFD"
    axis_excluded_statuses: tuple[str, ...] = ("Closed", "Completed")
    created_by: str = "cfdmigration"


def _normalize_foidb_connection_string(value: str | None) -> str | None:
    if value is None:
        return None

    candidate = value.strip()
    if not candidate:
        return candidate

    if "=" in candidate or ";" in candidate:
        return candidate

    return f"DSN={candidate};"


def load_settings() -> Settings:
    required = {
        "AXIS_DB_DRIVER": os.getenv("AXIS_DB_DRIVER", "pyodbc"),
        "AXIS_DB_CONNECTION_STRING": os.getenv("AXIS_DB_CONNECTION_STRING"),
        "FOIDB_DB_DRIVER": os.getenv("FOIDB_DB_DRIVER", "pyodbc"),
        "FOIDB_DB_CONNECTION_STRING": _normalize_foidb_connection_string(os.getenv("FOIDB_DB_CONNECTION_STRING")),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(sorted(missing))}")

    return Settings(
        axis_driver=required["AXIS_DB_DRIVER"],
        axis_connection_string=required["AXIS_DB_CONNECTION_STRING"] or "",
        foidb_driver=required["FOIDB_DB_DRIVER"],
        foidb_connection_string=required["FOIDB_DB_CONNECTION_STRING"] or "",
        axis_office_code=os.getenv("AXIS_OFFICE_CODE", "CFD").strip() or "CFD",
        axis_excluded_statuses=tuple(
            status.strip()
            for status in os.getenv("AXIS_EXCLUDED_STATUSES", "Closed,Completed").split(",")
            if status.strip()
        ),
        created_by=os.getenv("DATA_MIGRATION_CREATED_BY", "cfdmigration"),
    )
