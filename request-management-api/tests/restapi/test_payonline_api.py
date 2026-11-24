"""FOIMOD-5523: access to GET /api/foirequests/{id}/ministryrequest/{mid}/payonline.

Only the workflow engines' Keycloak clients may read payment details. The check rolls out in two steps,
WORKFLOW_CLIENT_ACCESS_MODE=log (default, lets every caller through and logs who would be refused) and then
"enforce". The service layer is faked; its rules are covered in tests/services/test_paymentdetails.py."""
import logging
import sys
from unittest.mock import MagicMock

import pytest
from flask import g
from jose import jwt as josejwt

try:
    import weasyprint  # noqa: F401
except OSError:
    # its native libraries are missing on some dev machines; it is not used by these tests
    sys.modules["weasyprint"] = MagicMock()

from tests.restapi.flask_app import shared_test_client  # noqa: E402
from request_api.auth import jwt as jwt_manager  # noqa: E402
import request_api.resources.foirequest as foirequest  # noqa: E402

URL = "/api/foirequests/8001/ministryrequest/9001/payonline"
N8N_CLIENT = "n8n-service"
CAMUNDA_CLIENT = "camunda-service"
DETAILS = {"idNumber": "EXM-2026-000123", "axisRequestId": "EXM-2026-000123", "currentState": "On Hold",
           "email": "jane.example@example.com", "hasEmail": True,
           "isofflinepayment": False, "cfrfee": {"feedata": {"balanceDue": "45.00"}}}

N8N = {"azp": N8N_CLIENT, "groups": []}
CAMUNDA = {"azp": CAMUNDA_CLIENT, "groups": []}
STAFF = {"azp": "foi-web", "groups": ["/Intake Team"], "preferred_username": "example.staff@idir"}


class FakeRequestService:
    response = DETAILS
    calls = []

    def getpaymentdetails(self, foirequestid, foiministryrequestid, includeemail=True):
        FakeRequestService.calls.append((foirequestid, foiministryrequestid))
        FakeRequestService.includeemail = includeemail
        return FakeRequestService.response

    def getrequestdetails(self, *args, **kwargs):
        raise AssertionError("payonline must not return the full request record")


@pytest.fixture(scope="module")
def client():
    return shared_test_client()


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setattr(FakeRequestService, "response", DETAILS)
    monkeypatch.setattr(FakeRequestService, "calls", [])
    monkeypatch.setattr(foirequest, "requestservice", FakeRequestService)
    monkeypatch.setenv("N8N_SERVICE_ACCOUNT_CLIENT_ID", N8N_CLIENT)
    monkeypatch.setenv("WORKFLOW_CLIENT_IDS", CAMUNDA_CLIENT)
    monkeypatch.delenv("WORKFLOW_CLIENT_ACCESS_MODE", raising=False)
    monkeypatch.setenv("WF_DEFAULT_ENGINE", "camunda")


def _as(monkeypatch, claims):
    """Skips signature validation but keeps every other decorator in the chain."""
    def validate(*args, **kwargs):
        g.jwt_oidc_token_info = claims
    token = josejwt.encode(claims, "unused", algorithm="HS256")
    monkeypatch.setattr(jwt_manager, "_require_auth_validation", validate)
    monkeypatch.setattr(jwt_manager, "get_token_auth_header", lambda: token)
    return {"Authorization": "Bearer " + token}


@pytest.mark.parametrize("claims", [N8N, CAMUNDA], ids=["n8n", "camunda"])
@pytest.mark.parametrize("mode", [None, "log", "enforce"])
def test_workflow_clients_get_only_the_payment_details(client, monkeypatch, claims, mode):
    if mode:
        monkeypatch.setenv("WORKFLOW_CLIENT_ACCESS_MODE", mode)
    response = client.get(URL, headers=_as(monkeypatch, claims))
    assert response.status_code == 200
    assert response.get_json() == DETAILS
    assert FakeRequestService.calls == [(8001, 9001)]


def test_log_mode_is_the_default_and_lets_other_callers_through(client, monkeypatch, caplog):
    with caplog.at_level(logging.WARNING):
        response = client.get(URL, headers=_as(monkeypatch, STAFF))
    assert response.status_code == 200
    assert response.get_json() == DETAILS
    assert "would refuse client=foi-web" in caplog.text
    assert "example.staff" not in caplog.text


def test_unknown_mode_behaves_as_log_mode(client, monkeypatch):
    monkeypatch.setenv("WORKFLOW_CLIENT_ACCESS_MODE", "enforced-typo")
    assert client.get(URL, headers=_as(monkeypatch, STAFF)).status_code == 200


def test_enforce_mode_refuses_other_callers(client, monkeypatch, caplog):
    monkeypatch.setenv("WORKFLOW_CLIENT_ACCESS_MODE", "enforce")
    with caplog.at_level(logging.WARNING):
        response = client.get(URL, headers=_as(monkeypatch, STAFF))
    assert response.status_code == 403
    assert FakeRequestService.calls == []
    assert "refused client=foi-web" in caplog.text


def test_enforce_mode_fails_closed_when_no_client_is_configured(client, monkeypatch):
    monkeypatch.setenv("WORKFLOW_CLIENT_ACCESS_MODE", "enforce")
    monkeypatch.setenv("N8N_SERVICE_ACCOUNT_CLIENT_ID", "")
    monkeypatch.setenv("WORKFLOW_CLIENT_IDS", " , ")
    for claims in (N8N, CAMUNDA, STAFF, {"groups": []}):
        assert client.get(URL, headers=_as(monkeypatch, claims)).status_code == 403


def test_several_workflow_client_ids_can_be_listed(client, monkeypatch):
    monkeypatch.setenv("WORKFLOW_CLIENT_ACCESS_MODE", "enforce")
    monkeypatch.setenv("WORKFLOW_CLIENT_IDS", "other-client, camunda-service")
    assert client.get(URL, headers=_as(monkeypatch, CAMUNDA)).status_code == 200


def test_the_clientid_claim_is_accepted_like_azp(client, monkeypatch):
    monkeypatch.setenv("WORKFLOW_CLIENT_ACCESS_MODE", "enforce")
    assert client.get(URL, headers=_as(monkeypatch, {"clientId": CAMUNDA_CLIENT, "groups": []})).status_code == 200


def test_mismatched_ids_return_404(client, monkeypatch):
    monkeypatch.setattr(FakeRequestService, "response", None)
    response = client.get(URL, headers=_as(monkeypatch, CAMUNDA))
    assert response.status_code == 404
    assert response.get_json()["status"] is False


def test_a_request_without_a_token_is_rejected(client):
    assert client.get(URL).status_code == 401


def test_camunda_client_is_allowed_by_default(client, monkeypatch):
    """No environment change is needed for Camunda: WORKFLOW_CLIENT_IDS defaults to forms-flow-bpm."""
    monkeypatch.setenv("WORKFLOW_CLIENT_ACCESS_MODE", "enforce")
    monkeypatch.delenv("WORKFLOW_CLIENT_IDS")
    assert client.get(URL, headers=_as(monkeypatch, {"azp": "forms-flow-bpm", "groups": []})).status_code == 200
    assert client.get(URL, headers=_as(monkeypatch, STAFF)).status_code == 403


def test_an_empty_list_overrides_the_default_and_allows_only_n8n(client, monkeypatch):
    monkeypatch.setenv("WORKFLOW_CLIENT_ACCESS_MODE", "enforce")
    monkeypatch.setenv("WORKFLOW_CLIENT_IDS", "")
    assert client.get(URL, headers=_as(monkeypatch, {"azp": "forms-flow-bpm", "groups": []})).status_code == 403
    assert client.get(URL, headers=_as(monkeypatch, N8N)).status_code == 200


@pytest.mark.parametrize("engine, includeemail", [("camunda", True), ("", True), ("n8n", False)])
def test_the_email_address_is_sent_only_when_the_engine_is_camunda(client, monkeypatch, engine, includeemail):
    """Camunda's BPMN reads the address, so it keeps getting it; n8n gets hasEmail only."""
    monkeypatch.setenv("WF_DEFAULT_ENGINE", engine)
    assert client.get(URL, headers=_as(monkeypatch, N8N)).status_code == 200
    assert FakeRequestService.includeemail is includeemail
