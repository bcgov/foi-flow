"""FOIMOD-5525: payment form rules (create/update Form.io payment submissions). All data is made up."""
import pytest

from request_api.services import paymentformservice as module
from request_api.services.external.formioservice import FormioError, FormioNotConfigured, FormioNotFound
from request_api.services.paymentformservice import PAYMENT_FORMS, PaymentFormError, paymentformservice

FID = "a" * 24
SID = "b" * 24
OTHER_FID = "c" * 24
FORM_IDS = {"payfeeonline": FID, "payoutstandingform": "d" * 24}
DETAILS = {
    "idNumber": "EXM-2026-000123",
    "axisRequestId": "EXM-2026-000123",
    "currentState": "On Hold",
    "cfrfee": {"feedata": {"balanceDue": "45.00"}},
}


class FakeRequestService:
    details = DETAILS
    calls = []

    def getpaymentdetails(self, foirequestid, foiministryrequestid, includeemail=True):
        FakeRequestService.calls.append((foirequestid, foiministryrequestid, includeemail))
        return FakeRequestService.details


class FakeFormio:
    stored = {}
    getsubmission_error = None
    created = []
    getformid_calls = []
    getsubmission_calls = []
    patches = []

    def getformid(self, formname):
        FakeFormio.getformid_calls.append(formname)
        return FORM_IDS[formname]

    def createsubmission(self, formid, data):
        FakeFormio.created.append((formid, data))
        return {"formId": formid, "submissionId": SID}

    def getsubmission(self, formid, submissionid):
        FakeFormio.getsubmission_calls.append((formid, submissionid))
        if FakeFormio.getsubmission_error:
            raise FakeFormio.getsubmission_error
        return {"data": FakeFormio.stored}

    def patchsubmission(self, formid, submissionid, fields):
        FakeFormio.patches.append((formid, submissionid, fields))


@pytest.fixture(autouse=True)
def _fakes(monkeypatch):
    monkeypatch.setenv("FORMSFLOW_WEB_URL", "https://pay.test")
    monkeypatch.setattr(FakeRequestService, "details", dict(DETAILS))
    monkeypatch.setattr(FakeRequestService, "calls", [])
    monkeypatch.setattr(FakeFormio, "stored", {"ministryRequestID": "9001"})
    monkeypatch.setattr(FakeFormio, "getsubmission_error", None)
    monkeypatch.setattr(FakeFormio, "created", [])
    monkeypatch.setattr(FakeFormio, "getformid_calls", [])
    monkeypatch.setattr(FakeFormio, "getsubmission_calls", [])
    monkeypatch.setattr(FakeFormio, "patches", [])
    monkeypatch.setattr(module, "requestservice", FakeRequestService)
    monkeypatch.setattr(module, "formioservice", FakeFormio)


def _create(formtype="payonline"):
    return paymentformservice().createpaymentformsubmission(1, 9001, formtype)


def test_payment_forms_constant():
    assert PAYMENT_FORMS == {"payonline": "payfeeonline", "payoutstanding": "payoutstandingform"}


@pytest.mark.parametrize("formtype,formname", [("payonline", "payfeeonline"), ("payoutstanding", "payoutstandingform")])
def test_create_builds_n8n_parity_body(formtype, formname):
    result = _create(formtype)
    assert FakeFormio.getformid_calls == [formname]
    assert FakeFormio.created == [
        (
            FORM_IDS[formname],
            {
                "foiRequestID": "1",
                "ministryRequestID": "9001",
                "balanceDue": 45.0,
                "axisRequestId": "EXM-2026-000123",
                "fileNumber": "EXM-2026-000123",
                "paymentstatus": "NOT PAID",
                "status": "On Hold",
            },
        )
    ]
    assert result == {
        "formId": FORM_IDS[formname],
        "submissionId": SID,
        "paymentUrl": f"https://pay.test/public/form/{FORM_IDS[formname]}/submission/{SID}/edit",
    }
    assert FakeRequestService.calls == [(1, 9001, False)]


def test_create_strips_trailing_slash_of_web_url(monkeypatch):
    monkeypatch.setenv("FORMSFLOW_WEB_URL", "https://pay.test/")
    assert _create()["paymentUrl"].startswith("https://pay.test/public/form/")


def test_create_unknown_form_type_is_400():
    with pytest.raises(PaymentFormError) as err:
        _create("other")
    assert err.value.status_code == 400
    assert FakeFormio.created == []


def test_create_request_not_found_is_404(monkeypatch):
    monkeypatch.setattr(FakeRequestService, "details", None)
    with pytest.raises(PaymentFormError) as err:
        _create()
    assert err.value.status_code == 404
    assert FakeFormio.created == []


@pytest.mark.parametrize("exc", [KeyError("x"), TypeError("x")])
def test_create_unknown_ministry_request_is_404(monkeypatch, exc):
    def boom(self, *args, **kwargs):
        raise exc
    monkeypatch.setattr(FakeRequestService, "getpaymentdetails", boom)
    with pytest.raises(PaymentFormError) as err:
        _create()
    assert err.value.status_code == 404
    assert err.value.message == "Request not found"
    assert FakeFormio.created == []


def test_create_without_approved_fee_is_400(monkeypatch):
    monkeypatch.setattr(FakeRequestService, "details", {k: v for k, v in DETAILS.items() if k != "cfrfee"})
    with pytest.raises(PaymentFormError) as err:
        _create()
    assert err.value.status_code == 400
    assert FakeFormio.created == []


@pytest.mark.parametrize("balance", ["0.00", "-1.00"])
def test_create_with_no_balance_due_is_400(monkeypatch, balance):
    monkeypatch.setattr(FakeRequestService, "details", {**DETAILS, "cfrfee": {"feedata": {"balanceDue": balance}}})
    with pytest.raises(PaymentFormError) as err:
        _create()
    assert err.value.status_code == 400
    assert FakeFormio.created == []


@pytest.mark.parametrize("value", [None, "", "  "])
def test_create_without_formsflow_web_url_raises_not_configured(monkeypatch, value):
    if value is None:
        monkeypatch.delenv("FORMSFLOW_WEB_URL")
    else:
        monkeypatch.setenv("FORMSFLOW_WEB_URL", value)
    with pytest.raises(FormioNotConfigured) as err:
        _create()
    assert str(err.value) == "FORMSFLOW_WEB_URL"
    assert FakeRequestService.calls == []
    assert FakeFormio.getformid_calls == []
    assert FakeFormio.created == []


def _update(paymentstatus="PAID", status="Records Review", formid=FID, submissionid=SID, ministryrequestid=9001):
    return paymentformservice().updatepaymentformsubmission(
        ministryrequestid, formid, submissionid, paymentstatus, status
    )


def test_update_paid_patches_paymentstatus_and_status():
    assert _update() == {"formId": FID, "submissionId": SID}
    assert FakeFormio.patches == [(FID, SID, {"paymentstatus": "PAID", "status": "Records Review"})]


@pytest.mark.parametrize("status", [None, ""])
def test_update_cancel_without_status_patches_paymentstatus_only(status):
    _update("CANCELLED", status)
    assert FakeFormio.patches == [(FID, SID, {"paymentstatus": "CANCELLED"})]


def test_update_rejects_form_that_is_not_a_payment_form():
    with pytest.raises(PaymentFormError) as err:
        _update(formid=OTHER_FID)
    assert err.value.status_code == 400
    assert FakeFormio.getsubmission_calls == []
    assert FakeFormio.patches == []


@pytest.mark.parametrize("stored", [9001, "9001"])
def test_update_matches_numeric_and_string_ministry_request_id(monkeypatch, stored):
    monkeypatch.setattr(FakeFormio, "stored", {"ministryRequestID": stored})
    _update()
    assert len(FakeFormio.patches) == 1


def test_update_other_requests_submission_is_404(monkeypatch):
    monkeypatch.setattr(FakeFormio, "stored", {"ministryRequestID": "9002"})
    with pytest.raises(PaymentFormError) as err:
        _update()
    assert err.value.status_code == 404
    assert FakeFormio.patches == []


def test_update_missing_submission_is_404(monkeypatch):
    monkeypatch.setattr(FakeFormio, "getsubmission_error", FormioNotFound("Form.io returned 404"))
    with pytest.raises(PaymentFormError) as err:
        _update()
    assert err.value.status_code == 404
    assert FakeFormio.patches == []


def test_update_other_formio_errors_propagate(monkeypatch):
    monkeypatch.setattr(FakeFormio, "getsubmission_error", FormioError("Form.io unreachable"))
    with pytest.raises(FormioError):
        _update()


def test_update_unknown_payment_status_is_400():
    with pytest.raises(PaymentFormError) as err:
        _update("EXPIRED")
    assert err.value.status_code == 400
    assert FakeFormio.getsubmission_calls == []
    assert FakeFormio.patches == []
