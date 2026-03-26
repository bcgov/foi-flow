from __future__ import annotations

from config import load_settings


def test_load_settings_uses_default_axis_filters(monkeypatch) -> None:
    monkeypatch.setenv("AXIS_DB_CONNECTION_STRING", "axis-conn")
    monkeypatch.setenv("FOIDB_DB_CONNECTION_STRING", "foidb-conn")
    monkeypatch.delenv("AXIS_OFFICE_CODE", raising=False)
    monkeypatch.delenv("AXIS_EXCLUDED_STATUSES", raising=False)

    settings = load_settings()

    assert settings.axis_office_code == "CFD"
    assert settings.axis_excluded_statuses == ("Closed", "Completed")


def test_load_settings_parses_axis_filters_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("AXIS_DB_CONNECTION_STRING", "axis-conn")
    monkeypatch.setenv("FOIDB_DB_CONNECTION_STRING", "foidb-conn")
    monkeypatch.setenv("AXIS_OFFICE_CODE", "IAS")
    monkeypatch.setenv("AXIS_EXCLUDED_STATUSES", "Closed, Completed , On Hold ")

    settings = load_settings()

    assert settings.axis_office_code == "IAS"
    assert settings.axis_excluded_statuses == ("Closed", "Completed", "On Hold")
