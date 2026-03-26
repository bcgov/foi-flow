from __future__ import annotations

from foidb_client import FoidbClient


class RecordingCursor:
    def __init__(self, row=None):
        self.row = row
        self.execute_calls = []

    def execute(self, query, params):
        self.execute_calls.append((query, params))

    def fetchone(self):
        return self.row


class RecordingPyodbcConnection:
    __module__ = "pyodbc"

    def __init__(self, row=None):
        self.row = row
        self.cursors = []

    def cursor(self):
        cursor = RecordingCursor(self.row)
        self.cursors.append(cursor)
        return cursor


class RecordingPsycopgConnection:
    __module__ = "psycopg"

    def __init__(self, row=None):
        self.row = row
        self.cursors = []

    def cursor(self):
        cursor = RecordingCursor(self.row)
        self.cursors.append(cursor)
        return cursor


def test_foidb_client_uses_odbc_placeholders_for_pyodbc_connections() -> None:
    connection = RecordingPyodbcConnection(row=(1,))
    client = FoidbClient(connection)

    exists = client.request_exists("XGR-2020-10982")

    assert exists is True
    query, params = connection.cursors[0].execute_calls[0]
    assert "migrationreference = ?" in query
    assert params == ("XGR-2020-10982",)


def test_foidb_client_keeps_psycopg_placeholders_for_non_odbc_connections() -> None:
    connection = RecordingPsycopgConnection(row=(1,))
    client = FoidbClient(connection)

    exists = client.request_exists("XGR-2020-10982")

    assert exists is True
    query, params = connection.cursors[0].execute_calls[0]
    assert "migrationreference = %s" in query
    assert params == ("XGR-2020-10982",)
