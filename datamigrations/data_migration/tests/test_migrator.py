from __future__ import annotations

from pathlib import Path

import main
from main import run
from migrator import RequestMigrator


class FakeAxisClient:
    def __init__(self, parent=None, ministry=None, applicants=None, contacts=None):
        self.parent = parent
        self.ministry = ministry or {}
        self.applicants = applicants or []
        self.contacts = contacts or []

    def fetch_parent_request(self, request_id: str):
        return self.parent

    def fetch_ministry_request(self, request_id: str):
        return self.ministry

    def fetch_applicants(self, request_id: str):
        return self.applicants

    def fetch_contact_information(self, request_id: str):
        return self.contacts


class FakeFoidbClient:
    def __init__(self, exists: bool = False):
        self.exists = exists
        self.calls = []

    def request_exists(self, request_id: str) -> bool:
        self.calls.append(("request_exists", request_id))
        return self.exists

    def begin_request(self):
        self.calls.append(("begin_request",))

    def commit_request(self):
        self.calls.append(("commit_request",))

    def rollback_request(self):
        self.calls.append(("rollback_request",))

    def insert_parent_request(self, payload):
        self.calls.append(("insert_parent_request", payload["migrationreference"]))
        return {"foirequest_id": 11, "version": 1}

    def resolve_received_mode_id(self, received_mode_name: str) -> int:
        self.calls.append(("resolve_received_mode_id", received_mode_name))
        return 5

    def resolve_applicant_category_id(self, category_name: str | None) -> int | None:
        self.calls.append(("resolve_applicant_category_id", category_name))
        return 9 if category_name else None

    def resolve_program_area_id(self, iao_code: str = "CFD") -> int:
        self.calls.append(("resolve_program_area_id", iao_code))
        return 2

    def resolve_request_status_id(self, name: str = "Open") -> int:
        self.calls.append(("resolve_request_status_id", name))
        return 4

    def insert_ministry_request(self, payload):
        self.calls.append(("insert_ministry_request", payload["migrationreference"]))

    def insert_applicant(self, payload):
        self.calls.append(("insert_applicant", payload["firstname"], payload["lastname"]))
        return 7

    def resolve_requestor_type_id(self, requestor_type_name: str) -> int:
        self.calls.append(("resolve_requestor_type_id", requestor_type_name))
        return 3

    def insert_applicant_mapping(self, payload):
        self.calls.append(("insert_applicant_mapping", payload["migrationreference"]))

    def insert_contact_information(self, payload):
        self.calls.append(("insert_contact_information", payload["value"]))


def test_migrate_request_skips_when_request_already_exists() -> None:
    migrator = RequestMigrator(axis_client=FakeAxisClient(), foidb_client=FakeFoidbClient(exists=True))

    result = migrator.migrate_request("XGR-2020-10982")

    assert result["status"] == "skipped"
    assert result["reason"] == "already migrated"


def test_migrate_request_rolls_back_when_parent_request_missing() -> None:
    foidb_client = FakeFoidbClient(exists=False)
    migrator = RequestMigrator(axis_client=FakeAxisClient(parent=None), foidb_client=foidb_client)

    result = migrator.migrate_request("XGR-2020-10982")

    assert result["status"] == "failed"
    assert result["reason"] == "request not found in AXIS"
    assert ("rollback_request",) in foidb_client.calls


def test_migrate_request_commits_successful_request() -> None:
    axis_client = FakeAxisClient(
        parent={
            "requestType": "general",
            "receivedDate": "2020-01-02 10:00:00",
            "requestdescription": "records",
            "reqDescriptionFromDate": "",
            "reqDescriptionToDate": "",
            "receivedMode": "Email",
            "category": "Media",
            "filenumber": "XGR-2020-10982",
        },
        ministry={
            "filenumber": "XGR-2020-10982",
            "requestdescription": "records",
            "reqDescriptionFromDate": "",
            "reqDescriptionToDate": "",
            "requestProcessStart": "2020-01-02 10:00:00",
            "dueDate": "2020-01-30 16:00:00",
            "cfrDueDate": "",
            "requestPageCount": "5",
            "linkedRequests": "[]",
            "identityVerified": '"yes"',
            "originalDueDate": "2020-01-28 16:00:00",
        },
        applicants=[
            {
                "firstName": "Jane",
                "lastName": "Doe",
                "middleName": "",
                "birthDate": "1990-01-01 00:00:00",
                "businessName": "",
                "requestid": "XGR-2020-10982",
                "MainApplicant": 1,
            }
        ],
        contacts=[
            {
                "email": "jane@example.com",
                "address1": "",
                "address2": "",
                "city": "",
                "zipcode": "",
                "work1": "",
                "work2": "",
                "mobile": "",
                "home": "",
                "country": "Canada",
                "province": "BC",
                "requests": "XGR-2020-10982",
            }
        ],
    )
    foidb_client = FakeFoidbClient(exists=False)
    migrator = RequestMigrator(axis_client=axis_client, foidb_client=foidb_client)

    result = migrator.migrate_request("XGR-2020-10982")

    assert result["status"] == "migrated"
    assert result["foirequest_id"] == 11
    assert ("commit_request",) in foidb_client.calls


def test_main_processes_csv_and_writes_optional_results(tmp_path: Path) -> None:
    csv_file = tmp_path / "requests.csv"
    output_file = tmp_path / "results.csv"
    csv_file.write_text("request_id\nXGR-2020-10982\n", encoding="utf-8")

    class FakeAppMigrator:
        def migrate_request(self, request_id: str):
            return {
                "request_id": request_id,
                "status": "skipped",
                "reason": "already migrated",
                "foirequest_id": "",
                "started_at": "2026-03-25T10:00:00",
                "finished_at": "2026-03-25T10:00:00",
            }

    exit_code = run(
        [
            "--input-csv",
            str(csv_file),
            "--output-csv",
            str(output_file),
        ],
        migrator_factory=lambda settings, dry_run=False: FakeAppMigrator(),
    )

    assert exit_code == 0
    assert output_file.exists()


def test_create_migrator_passes_axis_filter_settings(monkeypatch) -> None:
    axis_connection = object()
    foidb_connection = object()
    captured = {}

    settings = main.Settings(
        axis_driver="axis-driver",
        axis_connection_string="axis-conn",
        foidb_driver="foidb-driver",
        foidb_connection_string="foidb-conn",
        axis_office_code="IAS",
        axis_excluded_statuses=("Closed", "Completed", "On Hold"),
    )

    def fake_connect(module_name: str, connection_string: str):
        if module_name == "axis-driver":
            return axis_connection
        if module_name == "foidb-driver":
            return foidb_connection
        raise AssertionError(module_name)

    class FakeAxisClient:
        def __init__(self, connection, office_code, excluded_statuses):
            captured["axis"] = (connection, office_code, excluded_statuses)

    class FakeFoidbClient:
        def __init__(self, connection):
            captured["foidb"] = connection

    monkeypatch.setattr(main, "_connect", fake_connect)
    monkeypatch.setattr(main, "AxisClient", FakeAxisClient)
    monkeypatch.setattr(main, "FoidbClient", FakeFoidbClient)

    main.create_migrator(settings)

    assert captured["axis"] == (axis_connection, "IAS", ("Closed", "Completed", "On Hold"))
    assert captured["foidb"] is foidb_connection
