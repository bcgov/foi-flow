"""OCR failures use the existing record failure contract without provider details."""

from copy import deepcopy

import pytest

from request_api.services.records.recordservicegetter import recordservicegetter


@pytest.fixture
def records_api(monkeypatch):
    uploaded = {
        "recordid": 1, "documentmasterid": 10, "filename": "record.pdf",
        "batchid": 1, "created_at": "2026-09-29T12:00:00Z",
        "createdby": "tester", "attributes": {"divisions": []},
    }
    processing = {
        **uploaded, "filepath": "records/record.pdf", "isduplicate": False,
        "isredactionready": False, "trigger": "recordupload",
        "conversionstatus": "completed", "deduplicationstatus": "completed",
        "compressionstatus": "completed", "ocractivemqstatus": "completed",
        "azureocrjobstatus": "running", "ocrfilepath": None,
        "selectedfileprocessversion": None, "attachments": [],
    }
    module = "request_api.services.records.recordservicegetter"
    monkeypatch.setattr(f"{module}.FOIMinistryRequest.getmetadata", lambda _: {"programareaid": 1})
    monkeypatch.setattr(f"{module}.ProgramAreaDivision.getallprogramareatags", lambda _: [])
    monkeypatch.setattr(f"{module}.FOIRequestRecord.fetch", lambda *_: [deepcopy(uploaded)])
    service = recordservicegetter()
    monkeypatch.setattr(service, "makedocreviewerrequest", lambda *_: ([deepcopy(processing)], None))
    return service, processing


@pytest.mark.parametrize("status_field", ["ocractivemqstatus", "azureocrjobstatus"])
@pytest.mark.parametrize("message", [None, 'https://azure.example/operationLocation', '{"operationLocation":"https://azure.example/job"}', {"error": "internal details"}])
def test_ocr_failures_return_only_stage_for_records_and_attachments(records_api, status_field, message):
    service, processing = records_api
    processing.update({status_field: "error", "message": message})
    processing["attachments"] = [{**deepcopy(processing), "documentmasterid": 11}]

    record = service.fetch(1, 2)["records"][0]

    assert record["failed"] == "OCR"
    assert record["attachments"][0]["failed"] == "OCR"
    assert record["isredactionready"] is False
    assert record["ocrfilepath"] is None


def test_ocr_running_failed_then_successful(records_api):
    service, processing = records_api
    running = service.fetch(1, 2)["records"][0]
    assert "failed" not in running
    assert running["iscompressed"] is True
    assert running["isredactionready"] is False

    processing["azureocrjobstatus"] = "error"
    assert service.fetch(1, 2)["records"][0]["failed"] == "OCR"

    processing.update(azureocrjobstatus="completed", isredactionready=True, ocrfilepath="records/recordOCR.pdf")
    completed = service.fetch(1, 2)["records"][0]
    assert "failed" not in completed
    assert completed["isredactionready"] is True
    assert completed["ocrfilepath"] == "records/recordOCR.pdf"


@pytest.mark.parametrize("stage", ["conversion", "deduplication", "compression"])
def test_earlier_failure_stages_keep_precedence(records_api, stage):
    service, processing = records_api
    processing.update({f"{stage}status": "error", "azureocrjobstatus": "error"})
    assert service.fetch(1, 2)["records"][0]["failed"] == stage
