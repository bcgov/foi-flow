"""FOIMOD-5523: events sent to n8n must not carry applicant personal data.

Each event builder in workflowservice is fed a request schema full of (made-up) personal data, the way the API
passes the full request record. The payload written to the n8n outbox may hold only the reviewed fields below.
Adding a field to an event makes these tests fail on purpose: review it with the privacy owner, then add it to
ALLOWED_METADATA_KEYS."""
import json
from unittest.mock import patch

import pytest

from request_api.services.workflowservice import workflowservice

OUTBOX = "request_api.services.external.n8nworkflowservice.workflowoutboxservice"

# Reviewed fields. assignedTo (staff user id) stays until the exported n8n workflows show whether it is used.
ALLOWED_METADATA_KEYS = {
    "id", "rawRequestId", "status", "previousstatus", "ministries", "assignedGroup", "assignedTo",
    "assignedministrygroup", "ministryRequestID", "foiRequestID", "foiRequestId", "isPaymentActive",
    "paymentExpiryDate", "axisRequestId", "issync", "isofflinepayment", "nextStateName", "paymenturl",
    "applicantcorrespondenceid", "templatename",
}
ALLOWED_MINISTRY_KEYS = {"id", "foirequestid", "filenumber", "assignedgroup"}
ALLOWED_ENVELOPE_KEYS = {"event", "event_id", "occurred_at", "foiRequestMetaData", "id", "paymentstatus"}

PERSONAL = {
    "firstName": "Janeprivate", "middleName": "Quinnprivate", "lastName": "Zyxprivate",
    "email": "jane.private@example.com", "birthDate": "1980-01-01", "personalHealthNumber": "9000000000",
    "correctionalServiceNumber": "CS-000000", "publicServiceEmployeeNumber": "PSE-000000",
    "address": "100 Private Street", "phonePrimary": "250-000-0000", "childFirstName": "Samprivate",
    "childBirthDate": "2010-01-01", "anotherFirstName": "Patprivate", "adoptiveMotherFirstName": "Leeprivate",
    "description": "All records about me held by the Private Branch",
    "assignedToFirstName": "Alexprivate", "assignedToLastName": "Staffprivate",
}

FULL_RECORD = {
    **PERSONAL,
    "idNumber": "EXM-2026-000123", "axisRequestId": "EXM-2026-000123", "currentState": "On Hold",
    "assignedGroup": "Example Intake Team", "assignedTo": "example.staff@idir",
    "assignedgroup": "Example Intake Team", "assignedto": "example.staff@idir",
    "assignedministrygroup": "EXM Ministry Team",
    "cfrfee": {"feedata": {"balanceDue": "45.00", "paymenturl": "https://forms.example/form/a/submission/b",
                           "paymentexpirydate": "2026-12-21"}},
}


@pytest.fixture(autouse=True)
def _n8n(monkeypatch):
    monkeypatch.setenv("WF_DEFAULT_ENGINE", "n8n")


@pytest.fixture
def outbox():
    with patch(OUTBOX) as outbox_class:
        yield outbox_class.return_value


def _payloads(outbox):
    return [call[0][0] for call in outbox.enqueue.call_args_list]


def _assert_no_personal_data(payloads):
    assert payloads, "no event was sent to n8n"
    for payload in payloads:
        assert set(payload) <= ALLOWED_ENVELOPE_KEYS, set(payload) - ALLOWED_ENVELOPE_KEYS
        metadata = json.loads(payload["foiRequestMetaData"])
        assert set(metadata) <= ALLOWED_METADATA_KEYS, set(metadata) - ALLOWED_METADATA_KEYS
        for ministry in metadata.get("ministries") or []:
            assert set(ministry) <= ALLOWED_MINISTRY_KEYS, set(ministry) - ALLOWED_MINISTRY_KEYS
        serialized = json.dumps(payload)
        for key, value in PERSONAL.items():
            assert value not in serialized, "%s leaked into the %s event" % (key, payload["event"])


@patch("request_api.services.workflowservice.FOIRequest.getrawrequestidbyfoirequestid", return_value=7001)
@pytest.mark.parametrize("status", ["Open", "Intake in Progress", "Redirect"])
def test_intake_events(_rawid, outbox, status):
    ministries = [{**PERSONAL, "id": 9001, "foirequestid": 8001, "filenumber": "EXM-2026-000123",
                   "assignedgroup": "Example Intake Team"}]
    with patch.object(workflowservice, "_workflowservice__hasreopened", return_value=False):
        workflowservice().postunopenedevent(8001, None, FULL_RECORD, status, ministries)
    _assert_no_personal_data(_payloads(outbox))


@patch("request_api.services.workflowservice.FOIRequest.getrawrequestidbyfoirequestid", return_value=7001)
@patch("request_api.services.workflowservice.FOIMinistryRequest.getofflinepaymentflag", return_value=False)
@patch("request_api.services.workflowservice.paymentservice.getpaymentexpirydate", return_value="2026-12-21")
@pytest.mark.parametrize("usertype", ["iao", "ministry"])
def test_opened_request_events(_expiry, _offline, _rawid, outbox, usertype):
    data = {"ministries": [{"id": 9001, "foirequestid": 8001, "filenumber": "EXM-2026-000123", "version": 4,
                            "status": "On Hold", "assignedministrygroup": "EXM Ministry Team"}]}
    with patch.object(workflowservice, "_workflowservice__getpreviousministrystatus", return_value="Fee Estimate"), \
            patch.object(workflowservice, "_workflowservice__getministrystatus", return_value="Fee Estimate"), \
            patch.object(workflowservice, "_workflowservice__isprocessing", return_value=True), \
            patch.object(workflowservice, "_workflowservice__ispaymentactive", return_value=True), \
            patch.object(workflowservice, "_workflowservice__hasreopened", return_value=False):
        workflowservice().postopenedevent(9001, None, FULL_RECORD, data, "On Hold", usertype)
    _assert_no_personal_data(_payloads(outbox))


@patch("request_api.services.workflowservice.FOIRequest.getrawrequestidbyfoirequestid", return_value=7001)
@pytest.mark.parametrize("paymentstatus", ["PAID", "CANCELLED", "EXPIRED"])
def test_fee_events(_rawid, outbox, paymentstatus):
    workflowservice().postfeeevent(8001, 9001, FULL_RECORD, paymentstatus, "Call For Records")
    _assert_no_personal_data(_payloads(outbox))


@patch("request_api.services.workflowservice.FOIRequest.getrawrequestidbyfoirequestid", return_value=7001)
@patch("request_api.services.workflowservice.FOIMinistryRequest.getrequest", return_value={"foirequest_id": 8001})
def test_correspondence_events(_ministry, _rawid, outbox):
    workflowservice().postcorrenspodenceevent(None, 9001, FULL_RECORD, 555, "Fee Estimate Letter",
                                              [{"paymentExpiryDate": "2026-12-21"}])
    _assert_no_personal_data(_payloads(outbox))


def test_the_check_catches_a_leak(outbox):
    """Guards the guard: a payload carrying the applicant's email must fail the check."""
    leaking = [{"event": "x", "event_id": "y", "occurred_at": "z",
                "foiRequestMetaData": json.dumps({"id": "EXM-2026-000123", "email": PERSONAL["email"]})}]
    with pytest.raises(AssertionError):
        _assert_no_personal_data(leaking)
