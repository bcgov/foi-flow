"""Auth and request handling of the workflow outbox endpoints (service layer faked; its rules are
covered in tests/services/test_workflowoutboxservice.py). Exercises the real decorator chain."""
import sys
import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from flask import g
from jose import jwt as josejwt

try:
    import weasyprint  # noqa: F401
except OSError:
    # its native libraries are missing on some dev machines; it is not used by these tests
    sys.modules["weasyprint"] = MagicMock()

from request_api import create_app  # noqa: E402
from request_api.auth import jwt as jwt_manager  # noqa: E402
from request_api.services.workflowoutboxservice import AckResult  # noqa: E402
import request_api.resources.foiworkflow as foiworkflow  # noqa: E402

EVENT_ID = str(uuid.uuid4())
SERVICE_ACCOUNT = "n8n-service"


class FakeOutbox:
    """Records calls and returns whatever the test sets on the class."""
    ack_result = (AckResult.updated, SimpleNamespace(eventid=EVENT_ID, status="COMPLETED"))
    replay_results = {}
    calls = []

    @staticmethod
    def todict(row):
        return {"eventid": row.eventid, "status": row.status}

    def acknowledge(self, eventid, status, error=None, executionid=None):
        FakeOutbox.calls.append(("acknowledge", eventid, status, error, executionid))
        return FakeOutbox.ack_result

    def replay(self, eventid):
        FakeOutbox.calls.append(("replay", eventid))
        return FakeOutbox.replay_results.get(eventid, (AckResult.updated, SimpleNamespace(eventid=eventid, status="PENDING")))

    def listevents(self, statuses, limit, offset):
        FakeOutbox.calls.append(("list", statuses, limit, offset))
        return [{"eventid": EVENT_ID}]


@pytest.fixture(scope="module")
def client():
    return create_app().test_client()


@pytest.fixture(autouse=True)
def _fake(monkeypatch):
    FakeOutbox.calls = []
    FakeOutbox.ack_result = (AckResult.updated, SimpleNamespace(eventid=EVENT_ID, status="COMPLETED"))
    FakeOutbox.replay_results = {}
    monkeypatch.setattr(foiworkflow, "workflowoutboxservice", FakeOutbox)
    monkeypatch.setenv("N8N_SERVICE_ACCOUNT_CLIENT_ID", SERVICE_ACCOUNT)


def _as(monkeypatch, claims):
    """Skips signature validation but keeps every other decorator in the chain."""
    def validate(*args, **kwargs):
        g.jwt_oidc_token_info = claims
    token = josejwt.encode(claims, "unused", algorithm="HS256")
    monkeypatch.setattr(jwt_manager, "_require_auth_validation", validate)
    monkeypatch.setattr(jwt_manager, "get_token_auth_header", lambda: token)
    return {"Authorization": "Bearer " + token}


N8N = {"azp": SERVICE_ACCOUNT, "groups": []}
ADMIN = {"azp": "foi-web", "groups": ["/FOI Admin"], "preferred_username": "admin"}
USER = {"azp": "foi-web", "groups": ["/Intake Team"], "preferred_username": "user"}

ENDPOINTS = [
    ("put", "/api/foiworkflow/events/" + EVENT_ID, {"status": "COMPLETED"}),
    ("get", "/api/foiworkflow/events", None),
    ("post", "/api/foiworkflow/events/%s/replay" % EVENT_ID, None),
    ("post", "/api/foiworkflow/events/replay", {"eventids": [EVENT_ID]}),
]


@pytest.mark.parametrize("method,url,body", ENDPOINTS)
def test_unauthenticated_calls_are_rejected(client, method, url, body):
    response = getattr(client, method)(url, json=body)
    assert response.status_code == 401
    assert FakeOutbox.calls == []


# --- acknowledgement: service account only -------------------------------------------------------

def test_acknowledgement_accepts_the_n8n_service_account(client, monkeypatch):
    headers = _as(monkeypatch, N8N)
    response = client.put("/api/foiworkflow/events/" + EVENT_ID, headers=headers,
                          json={"status": "FAILED", "error": "Send Email failed", "executionid": 1234})
    assert response.status_code == 200
    assert FakeOutbox.calls == [("acknowledge", EVENT_ID, "FAILED", "Send Email failed", "1234")]


@pytest.mark.parametrize("claims", [ADMIN, USER])
def test_acknowledgement_rejects_other_authenticated_users(client, monkeypatch, claims):
    headers = _as(monkeypatch, claims)
    assert client.put("/api/foiworkflow/events/" + EVENT_ID, headers=headers, json={"status": "COMPLETED"}).status_code == 401
    assert FakeOutbox.calls == []


def test_acknowledgement_fails_closed_when_the_service_account_is_not_configured(client, monkeypatch):
    monkeypatch.delenv("N8N_SERVICE_ACCOUNT_CLIENT_ID")
    headers = _as(monkeypatch, {"azp": None, "groups": []})
    assert client.put("/api/foiworkflow/events/" + EVENT_ID, headers=headers, json={"status": "COMPLETED"}).status_code == 401


@pytest.mark.parametrize("body", [{}, {"status": "DELIVERED"}, {"status": "PENDING"}, {"status": 5}])
def test_acknowledgement_requires_completed_or_failed(client, monkeypatch, body):
    headers = _as(monkeypatch, N8N)
    assert client.put("/api/foiworkflow/events/" + EVENT_ID, headers=headers, json=body).status_code == 400
    assert FakeOutbox.calls == []


def test_acknowledgement_requires_a_uuid_event_id(client, monkeypatch):
    headers = _as(monkeypatch, N8N)
    assert client.put("/api/foiworkflow/events/not-a-uuid", headers=headers, json={"status": "COMPLETED"}).status_code == 400


@pytest.mark.parametrize("result,code", [(AckResult.unchanged, 200), (AckResult.notfound, 404), (AckResult.conflict, 409)])
def test_acknowledgement_maps_the_service_result_to_a_status_code(client, monkeypatch, result, code):
    monkeypatch.setattr(FakeOutbox, "ack_result", (result, SimpleNamespace(eventid=EVENT_ID, status="DEAD") if result != AckResult.notfound else None))
    headers = _as(monkeypatch, N8N)
    assert client.put("/api/foiworkflow/events/" + EVENT_ID, headers=headers, json={"status": "COMPLETED"}).status_code == code


# --- list / replay: any authenticated user --------------------------------------------------------

def test_admin_lists_dead_and_failed_by_default(client, monkeypatch):
    headers = _as(monkeypatch, ADMIN)
    response = client.get("/api/foiworkflow/events", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["events"] == [{"eventid": EVENT_ID}]
    assert FakeOutbox.calls == [("list", ["DEAD", "FAILED"], 100, 0)]


def test_listing_accepts_a_status_filter_and_rejects_unknown_statuses(client, monkeypatch):
    headers = _as(monkeypatch, ADMIN)
    assert client.get("/api/foiworkflow/events?status=delivered,pending&limit=5&offset=10", headers=headers).status_code == 200
    assert FakeOutbox.calls == [("list", ["DELIVERED", "PENDING"], 5, 10)]
    assert client.get("/api/foiworkflow/events?status=bogus", headers=headers).status_code == 400
    assert client.get("/api/foiworkflow/events?limit=abc", headers=headers).status_code == 400


def test_admin_replays_one_event_with_its_existing_event_id(client, monkeypatch):
    headers = _as(monkeypatch, ADMIN)
    response = client.post("/api/foiworkflow/events/%s/replay" % EVENT_ID, headers=headers)
    assert response.status_code == 200
    assert FakeOutbox.calls == [("replay", EVENT_ID)]


@pytest.mark.parametrize("result,code", [(AckResult.notfound, 404), (AckResult.conflict, 409)])
def test_replay_maps_not_found_and_not_replayable(client, monkeypatch, result, code):
    monkeypatch.setattr(FakeOutbox, "replay_results", {EVENT_ID: (result, SimpleNamespace(eventid=EVENT_ID, status="COMPLETED") if result == AckResult.conflict else None)})
    headers = _as(monkeypatch, ADMIN)
    assert client.post("/api/foiworkflow/events/%s/replay" % EVENT_ID, headers=headers).status_code == code


def test_bulk_replay_reports_each_event(client, monkeypatch):
    other = str(uuid.uuid4())
    monkeypatch.setattr(FakeOutbox, "replay_results", {other: (AckResult.conflict, SimpleNamespace(eventid=other, status="COMPLETED"))})
    headers = _as(monkeypatch, ADMIN)
    response = client.post("/api/foiworkflow/events/replay", headers=headers, json={"eventids": [EVENT_ID, other]})
    assert response.status_code == 200
    assert response.get_json()["results"] == {EVENT_ID: "updated", other: "conflict"}


@pytest.mark.parametrize("body", [{}, {"eventids": []}, {"eventids": "x"}, {"eventids": ["nope"]}, {"eventids": [EVENT_ID] * 501}])
def test_bulk_replay_validates_the_event_ids(client, monkeypatch, body):
    headers = _as(monkeypatch, ADMIN)
    assert client.post("/api/foiworkflow/events/replay", headers=headers, json=body).status_code == 400
    assert FakeOutbox.calls == []
