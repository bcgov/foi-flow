"""Preserve webform identity verification in the raw request detail response."""

from copy import deepcopy
from datetime import datetime

import pytest

from request_api.services.rawrequest.rawrequestservicegetter import rawrequestservicegetter


@pytest.fixture
def raw_request():
    return {
        "requestid": 42,
        "version": 1,
        "sourceofsubmission": "onlineform",
        "status": "Unopened",
        "requeststatuslabel": "Unopened",
        "created_at": "2026-10-19T17:00:00Z",
        "wfinstanceid": None,
        "ispiiredacted": False,
        "isiaorestricted": False,
        "assignedgroup": "Unassigned",
        "assignedto": None,
        "axisrequestid": None,
        "axissyncdate": None,
        "linkedrequests": [],
        "closedate": None,
        "requestrawdata": {
            "requestType": {"requestType": "personal"},
            "ministry": {"selectedMinistry": []},
            "contactInfo": {
                "firstName": "Test", "middleName": None, "lastName": "Applicant",
                "businessName": None, "alsoKnownAs": None, "birthDate": "1980-01-02",
            },
            "contactInfoOptions": dict.fromkeys([
                "email", "phonePrimary", "phoneSecondary", "address", "city",
                "postal", "province", "country",
            ], ""),
            "descriptionTimeframe": {
                "description": "Test request", "fromDate": "2026-01-01",
                "toDate": "2026-10-01", "correctionalServiceNumber": None,
                "publicServiceEmployeeNumber": None, "topic": None,
            },
            "selectAbout": {"yourself": True, "child": False, "another": False},
        },
    }


@pytest.fixture
def getter(raw_request, monkeypatch):
    module = "request_api.services.rawrequest.rawrequestservicegetter"
    monkeypatch.setattr(f"{module}.FOIRawRequest.get_request", lambda _: deepcopy(raw_request))
    monkeypatch.setattr(
        f"{module}.FOIRawRequest.getLastStatusUpdateDate",
        lambda *_: datetime(2026, 10, 19),
    )
    monkeypatch.setattr(f"{module}.FOIRawRequest.getstatesummary", lambda _: [])
    monkeypatch.setattr(f"{module}.OperatingTeamEmail.getoperatingteamemail", lambda _: "test@example.com")
    monkeypatch.setattr(f"{module}.linkedrequestservice.getlinkedrequestinfo", lambda *_: [])
    monkeypatch.setattr(
        f"{module}.FOIRequestStatus.getrequeststatus",
        lambda *_: {"statuslabel": "Unopened"},
    )
    return rawrequestservicegetter()


@pytest.mark.parametrize("version", [1, 2])
@pytest.mark.parametrize("identity_verified", ["BC Services Card", None])
def test_webform_identity_is_returned_at_top_level(raw_request, getter, version, identity_verified):
    # Assignment-only versions can still contain the original webform shape.
    raw_request["version"] = version
    raw_request["requestrawdata"]["identityVerified"] = identity_verified

    response = getter.getrawrequestforid(42)

    assert response["identityVerified"] == identity_verified
    assert response["additionalPersonalInfo"]["birthDate"] == "1980-01-02"


def test_legacy_webform_without_identity_remains_unverified(raw_request, getter):
    response = getter.getrawrequestforid(42)

    assert response["identityVerified"] is None


@pytest.mark.parametrize("source,version", [("onlineform", 2), ("intake", 1)])
@pytest.mark.parametrize("identity_verified", ["BC Services Card", "Manual verification", None])
def test_saved_and_intake_requests_preserve_identity(raw_request, getter, source, version, identity_verified):
    raw_request.update(sourceofsubmission=source, version=version)
    raw_request["requestrawdata"] = {
        "rawRequestId": 42,
        "requestType": "personal",
        "identityVerified": identity_verified,
        "additionalPersonalInfo": {"birthDate": "1980-01-02", "alsoKnownAs": ""},
    }

    response = getter.getrawrequestforid(42)

    assert response["identityVerified"] == identity_verified
