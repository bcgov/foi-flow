from __future__ import annotations

import logging

from axis_client import AxisClient


class RecordingCursor:
    def __init__(self, rows):
        self.rows = rows
        self.description = [("filenumber",)]
        self.execute_calls = []

    def execute(self, query, params):
        self.execute_calls.append((query, params))

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows


class RecordingConnection:
    def __init__(self, rows):
        self.rows = rows
        self.cursors = []

    def cursor(self):
        cursor = RecordingCursor(self.rows)
        self.cursors.append(cursor)
        return cursor


def test_axis_client_parameterizes_office_code_and_excluded_statuses() -> None:
    connection = RecordingConnection(rows=[("XGR-2020-10982",)])
    client = AxisClient(connection, office_code="IAS", excluded_statuses=("Closed", "Completed", "On Hold"))

    result = client.fetch_parent_request("XGR-2020-10982")

    assert result == {"filenumber": "XGR-2020-10982"}
    query, params = connection.cursors[0].execute_calls[0]
    assert "office.OFFICE_CODE = ?" in query
    assert "requests.vcRequestStatus NOT IN (?, ?, ?)" in query
    assert params == ("XGR-2020-10982", "IAS", "Closed", "Completed", "On Hold")


def test_axis_client_omits_status_filter_when_no_statuses_are_excluded() -> None:
    connection = RecordingConnection(rows=[("XGR-2020-10982",)])
    client = AxisClient(connection, office_code="IAS", excluded_statuses=())

    client.fetch_parent_request("XGR-2020-10982")

    query, params = connection.cursors[0].execute_calls[0]
    assert "requests.vcRequestStatus NOT IN" not in query
    assert params == ("XGR-2020-10982", "IAS")


def test_axis_client_logs_sql_and_params(caplog) -> None:
    connection = RecordingConnection(rows=[("XGR-2020-10982",)])
    client = AxisClient(connection, office_code="IAS", excluded_statuses=("Closed",))

    with caplog.at_level(logging.DEBUG):
        client.fetch_parent_request("XGR-2020-10982")

    messages = [record.getMessage() for record in caplog.records]
    assert any("Executing AXIS query:" in message for message in messages)
    assert any("office.OFFICE_CODE = ?" in message for message in messages)
    assert any("AXIS query params: ('XGR-2020-10982', 'IAS', 'Closed')" in message for message in messages)
