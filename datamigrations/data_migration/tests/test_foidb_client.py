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


def test_insert_parent_request_includes_required_version_and_isactive_columns() -> None:
    connection = RecordingPsycopgConnection(row=(11, 1))
    client = FoidbClient(connection)

    client.insert_parent_request(
        {
            "requesttype": "general",
            "receiveddate": None,
            "initialdescription": "records",
            "initialrecordsearchfromdate": None,
            "initialrecordsearchtodate": None,
            "receivedmodeid": 1,
            "applicantcategoryid": 2,
            "createdby": "migration",
            "updatedby": "migration",
            "migrationreference": "XGR-2020-10982",
        }
    )

    query, _ = connection.cursors[0].execute_calls[0]
    assert "version, requesttype, isactive" in query
    assert "isactive" in query


def test_insert_raw_request_returns_request_identifier_and_uses_schema_columns() -> None:
    connection = RecordingPsycopgConnection(row=(21, 1))
    client = FoidbClient(connection)

    result = client.insert_raw_request(
        {
            "requestrawdata": {"filenumber": "XGR-2020-10982"},
            "status": "Open",
            "notes": None,
            "assignedto": None,
            "sourceofsubmission": "Email",
            "assignedgroup": None,
            "ispiiredacted": False,
            "createdby": "migration",
            "updatedby": "migration",
            "requirespayment": False,
            "closedate": None,
            "closereasonid": None,
            "axisrequestid": "XGR-2020-10982",
            "axissyncdate": None,
            "isiaorestricted": False,
            "linkedrequests": [],
            "requeststatuslabel": "Open",
            "isconsultflag": False,
        }
    )

    assert result == {"foirawrequest_id": 21, "version": 1}
    query, _ = connection.cursors[0].execute_calls[0]
    assert 'INSERT INTO public."FOIRawRequests"' in query
    assert "requestrawdata" in query
    assert "axisrequestid" in query
    assert "requeststatuslabel" in query


def test_insert_ministry_request_uses_schema_column_names() -> None:
    connection = RecordingPsycopgConnection()
    client = FoidbClient(connection)

    client.insert_ministry_request(
        {
            "filenumber": "XGR-2020-10982",
            "description": "records",
            "recordsearchfromdate": None,
            "recordsearchtodate": None,
            "startdate": "2020-01-02 10:00:00",
            "duedate": "2020-01-30 16:00:00",
            "createdby": "migration",
            "updatedby": "migration",
            "programareaid": 2,
            "requeststatusid": 4,
            "foirequest_id": 11,
            "foirequestversion_id": 1,
            "cfrduedate": None,
            "requestpagecount": 5,
            "linkedrequests": [],
            "migrationreference": "XGR-2020-10982",
            "identityverified": None,
            "originalldd": None,
        }
    )

    query, _ = connection.cursors[0].execute_calls[0]
    assert "requeststatuslabel" in query
    assert "axispagecount" in query
    assert "requestpagecount" not in query


def test_insert_contact_information_uses_contactinformation_column() -> None:
    connection = RecordingPsycopgConnection()
    client = FoidbClient(connection)

    client.insert_contact_information(
        {
            "createdby": "migration",
            "contacttypeid": 1,
            "dataformat": "email",
            "value": "person@example.com",
            "foirequest_id": 11,
            "foirequestversion_id": 1,
        }
    )

    query, _ = connection.cursors[0].execute_calls[0]
    assert "contactinformation" in query
    assert " value," not in query


def test_find_request_bundle_queries_by_migrationreference() -> None:
    connection = RecordingPsycopgConnection(row=(11, 1, 21))
    client = FoidbClient(connection)

    bundle = client.find_request_bundle("XGR-2020-10982")

    assert bundle == {"foirequest_id": 11, "foirequestversion_id": 1, "foirawrequestid": 21}
    query, params = connection.cursors[0].execute_calls[0]
    assert "migrationreference = %s" in query
    assert params == ("XGR-2020-10982",)


def test_preview_delete_counts_returns_per_table_counts() -> None:
    connection = RecordingPsycopgConnection(row=(3,))
    client = FoidbClient(connection)

    counts = client.preview_delete_counts({"foirequest_id": 11, "foirequestversion_id": 1, "foirawrequestid": 21})

    assert counts == {
        "FOIRequestContactInformation": 3,
        "FOIRequestApplicantMappings": 3,
        "FOIRequestApplicants": 3,
        "FOIMinistryRequests": 3,
        "FOIRequests": 1,
        "FOIRawRequests": 1,
    }
    assert len(connection.cursors) == 4


def test_delete_request_bundle_executes_queries_in_fk_safe_order() -> None:
    connection = RecordingPsycopgConnection()
    client = FoidbClient(connection)

    client.delete_request_bundle({"foirequest_id": 11, "foirequestversion_id": 1, "foirawrequestid": 21})

    queries = [cursor.execute_calls[0][0] for cursor in connection.cursors]
    assert 'DELETE FROM public."FOIRequestContactInformation"' in queries[0]
    assert 'DELETE FROM public."FOIRequestApplicantMappings"' in queries[1]
    assert 'DELETE FROM public."FOIRequestApplicants"' in queries[2]
    assert 'DELETE FROM public."FOIMinistryRequests"' in queries[3]
    assert 'DELETE FROM public."FOIRequests"' in queries[4]
    assert 'DELETE FROM public."FOIRawRequests"' in queries[5]
