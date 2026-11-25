"""FOIMOD-5525: workflow-only endpoints that create/update the applicant's Form.io payment submission.
The service layer is faked (its rules are covered in tests/services); these tests cover validation,
error mapping, access control and that the existing Camunda payment routes are unaffected."""
import sys
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

from tests.restapi.flask_app import shared_test_client  # noqa: E402
from request_api.auth import jwt as jwt_manager  # noqa: E402
from request_api.services.external.formioservice import FormioError, FormioNotConfigured  # noqa: E402
from request_api.services.paymentformservice import PaymentFormError  # noqa: E402
from request_api.services.paymentformservice import paymentformservice as RealPaymentFormService  # noqa: E402
import request_api.resources.foipayment as foipayment  # noqa: E402

URL = "/api/foipayment/8001/ministryrequest/9001/formsubmission"
FID = "a" * 24
SID = "b" * 24
N8N_CLIENT = "n8n-service"
CAMUNDA_CLIENT = "camunda-service"
N8N = {"azp": N8N_CLIENT, "groups": []}
CAMUNDA = {"azp": CAMUNDA_CLIENT, "groups": []}
STAFF = {"azp": "foi-web", "groups": ["/Intake Team"], "preferred_username": "example.staff@idir"}
FORMIO_SETTINGS = ("FORMIO_URL", "FORMIO_PAYMENT_USER_EMAIL", "FORMIO_PAYMENT_USER_PASSWORD", "FORMSFLOW_WEB_URL")


class FakePaymentFormService:
    calls = []
    error = None

    def createpaymentformsubmission(self, requestid, ministryrequestid, formtype):
        FakePaymentFormService.calls.append(("create", requestid, ministryrequestid, formtype))
        if FakePaymentFormService.error:
            raise FakePaymentFormService.error
        return {"formId": FID, "submissionId": SID, "paymentUrl": "https://example.test/public/form/x"}

    def updatepaymentformsubmission(self, requestid, ministryrequestid, formid, submissionid, paymentstatus,
                                    status=None):
        FakePaymentFormService.calls.append(
            ("update", requestid, ministryrequestid, formid, submissionid, paymentstatus, status))
        if FakePaymentFormService.error:
            raise FakePaymentFormService.error
        return {"formId": formid, "submissionId": submissionid}


@pytest.fixture(scope="module")
def client():
    return shared_test_client()


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setattr(FakePaymentFormService, "calls", [])
    monkeypatch.setattr(FakePaymentFormService, "error", None)
    monkeypatch.setattr(foipayment, "paymentformservice", FakePaymentFormService)
    monkeypatch.setenv("N8N_SERVICE_ACCOUNT_CLIENT_ID", N8N_CLIENT)
    monkeypatch.setenv("WORKFLOW_CLIENT_IDS", CAMUNDA_CLIENT)
    monkeypatch.delenv("WORKFLOW_CLIENT_ACCESS_MODE", raising=False)


def _as(monkeypatch, claims):
    """Skips signature validation but keeps every other decorator in the chain."""
    def validate(*args, **kwargs):
        g.jwt_oidc_token_info = claims
    token = josejwt.encode(claims, "unused", algorithm="HS256")
    monkeypatch.setattr(jwt_manager, "_require_auth_validation", validate)
    monkeypatch.setattr(jwt_manager, "get_token_auth_header", lambda: token)
    return {"Authorization": "Bearer " + token}


def _patch_body(**overrides):
    body = {"formId": FID, "submissionId": SID, "paymentStatus": "PAID"}
    body.update(overrides)
    return body


def test_post_returns_201_with_ids_and_url(client, monkeypatch):
    response = client.post(URL, json={"formType": "payonline"}, headers=_as(monkeypatch, N8N))
    assert response.status_code == 201
    assert response.get_json() == {"formId": FID, "submissionId": SID,
                                   "paymentUrl": "https://example.test/public/form/x"}
    assert FakePaymentFormService.calls == [("create", 8001, 9001, "payonline")]


@pytest.mark.parametrize("body", [{"formType": "other"}, {}, {"formType": ""}])
def test_post_rejects_unknown_form_type(client, monkeypatch, body):
    response = client.post(URL, json=body, headers=_as(monkeypatch, N8N))
    assert response.status_code == 400
    assert response.get_json() == {"status": False, "message": "Invalid request"}
    assert FakePaymentFormService.calls == []


def test_patch_returns_200(client, monkeypatch):
    response = client.patch(URL, json=_patch_body(), headers=_as(monkeypatch, N8N))
    assert response.status_code == 200
    assert response.get_json() == {"formId": FID, "submissionId": SID}
    assert FakePaymentFormService.calls == [("update", 8001, 9001, FID, SID, "PAID", None)]


def test_patch_passes_status_through(client, monkeypatch):
    response = client.patch(URL, json=_patch_body(paymentStatus="CANCELLED", status="On Hold"),
                            headers=_as(monkeypatch, N8N))
    assert response.status_code == 200
    assert FakePaymentFormService.calls == [("update", 8001, 9001, FID, SID, "CANCELLED", "On Hold")]


@pytest.mark.parametrize("field", ["formId", "submissionId"])
@pytest.mark.parametrize("bad", ["", "undefined", "../x", "A" * 24, "a" * 23])
def test_patch_rejects_malformed_ids(client, monkeypatch, field, bad):
    response = client.patch(URL, json=_patch_body(**{field: bad}), headers=_as(monkeypatch, N8N))
    assert response.status_code == 400
    assert bad not in response.get_data(as_text=True) or bad == ""
    assert FakePaymentFormService.calls == []


def test_patch_rejects_expired_status(client, monkeypatch):
    response = client.patch(URL, json=_patch_body(paymentStatus="EXPIRED"), headers=_as(monkeypatch, N8N))
    assert response.status_code == 400
    assert FakePaymentFormService.calls == []


@pytest.mark.parametrize("method,body", [("post", {"formType": "payonline"}), ("patch", _patch_body())])
@pytest.mark.parametrize("exc,code,message", [
    (PaymentFormError(404, "x"), 404, "x"),
    (FormioNotConfigured("FORMIO_URL"), 503, "Payment form service is not configured"),
    (FormioError("boom"), 502, "Payment form service unavailable"),
])
def test_errors_map_to_status(client, monkeypatch, method, body, exc, code, message):
    FakePaymentFormService.error = exc
    response = getattr(client, method)(URL, json=body, headers=_as(monkeypatch, N8N))
    assert response.status_code == code
    assert response.get_json() == {"status": False, "message": message}
    text = response.get_data(as_text=True)
    assert "boom" not in text and "FORMIO_URL" not in text


@pytest.mark.parametrize("mode,code", [(None, 201), ("enforce", 403)])
def test_staff_token_follows_workflow_client_mode(client, monkeypatch, mode, code):
    if mode:
        monkeypatch.setenv("WORKFLOW_CLIENT_ACCESS_MODE", mode)
    response = client.post(URL, json={"formType": "payonline"}, headers=_as(monkeypatch, STAFF))
    assert response.status_code == code


def test_existing_payment_routes_unchanged_without_formio_settings(client, monkeypatch):
    for name in FORMIO_SETTINGS:
        monkeypatch.delenv(name, raising=False)
    # the real paymentformservice is used here: it must answer 503 from the missing setting, without the DB
    monkeypatch.setattr(foipayment, "paymentformservice", RealPaymentFormService)
    seen = []

    class FakePaymentService:
        def createpayment(self, requestid, ministryrequestid, schema):
            seen.append(("create", requestid, ministryrequestid))
            return SimpleNamespace(success=True, message="ok", identifier=1)

        def cancelpayment(self, requestid, ministryrequestid, schema):
            seen.append(("cancel", requestid, ministryrequestid))
            return SimpleNamespace(success=True, message="ok", identifier=2)

    monkeypatch.setattr(foipayment, "paymentservice", FakePaymentService)
    headers = _as(monkeypatch, CAMUNDA)
    base = "/api/foipayment/8001/ministryrequest/9001"
    assert client.post(base, json={}, headers=headers).status_code == 200
    assert client.post(base + "/cancel", json={}, headers=headers).status_code == 200
    assert seen == [("create", "8001", "9001"), ("cancel", "8001", "9001")]
    response = client.post(URL, json={"formType": "payonline"}, headers=headers)
    assert response.status_code == 503
    assert response.get_json() == {"status": False, "message": "Payment form service is not configured"}
