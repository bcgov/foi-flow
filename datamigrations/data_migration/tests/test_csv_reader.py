from pathlib import Path

import pytest

from csv_reader import read_request_ids


def test_read_request_ids_deduplicates_and_ignores_blank_rows(tmp_path: Path) -> None:
    csv_file = tmp_path / "requests.csv"
    csv_file.write_text(
        "request_id\nXGR-2020-10982\n\nXGR-2020-10982\n XGR-2021-00001 \n",
        encoding="utf-8",
    )

    assert read_request_ids(csv_file) == ["XGR-2020-10982", "XGR-2021-00001"]


def test_read_request_ids_requires_request_id_column(tmp_path: Path) -> None:
    csv_file = tmp_path / "requests.csv"
    csv_file.write_text("id\nXGR-2020-10982\n", encoding="utf-8")

    with pytest.raises(ValueError, match="request_id"):
        read_request_ids(csv_file)


def test_read_request_ids_accepts_request_header_as_fallback(tmp_path: Path) -> None:
    csv_file = tmp_path / "requests.csv"
    csv_file.write_text(
        "Request\nXGR-2020-10982\n XGR-2021-00001 \n",
        encoding="utf-8",
    )

    assert read_request_ids(csv_file) == ["XGR-2020-10982", "XGR-2021-00001"]


def test_read_request_ids_prefers_request_id_when_both_headers_exist(tmp_path: Path) -> None:
    csv_file = tmp_path / "requests.csv"
    csv_file.write_text(
        "request_id,Request\nXGR-2020-10982,COR-2020-00001\n",
        encoding="utf-8",
    )

    assert read_request_ids(csv_file) == ["XGR-2020-10982"]
