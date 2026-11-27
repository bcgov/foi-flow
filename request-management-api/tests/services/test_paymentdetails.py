"""FOIMOD-5523: the payment details returned by GET .../payonline.

The Camunda BPMN foi-initial-payment-submission.bpmn reads this response with Spin:
  S(response).prop("axisRequestId").stringValue()
  S(response).prop("cfrfee").prop("feedata").prop("balanceDue").stringValue()
  S(response).prop("idNumber").stringValue()
  S(response).prop("email").stringValue()
  S(response).prop("isofflinepayment").boolValue()
Spin throws when a key is missing or has the wrong JSON type, so the trimmed response must keep exactly the keys,
nesting, types and edge cases of the full record (getrequestdetails), and nothing else. n8n reads the same keys plus
currentState ("FOI Fee Initiation" > "Compute Payment Vars"). All data is made up."""
import copy
import json

import pytest

import request_api.services.foirequest.requestservicegetter as getter_module
from request_api.services.foirequest.requestservicegetter import requestservicegetter

FOIREQUESTID = 8001
MINISTRYREQUESTID = 9001
# Camunda reads the first five; n8n ("FOI Fee Initiation" > "Compute Payment Vars") also reads currentState.
WORKFLOW_KEYS = {"idNumber", "axisRequestId", "email", "isofflinepayment", "cfrfee", "currentState"}
# hasEmail is new (not in the full record): whether the applicant has an email, to replace email later.

# Personal data that the full record carries and the payment details must never contain.
PERSONAL = {
    "firstName": "Jane", "lastName": "Example", "birthDate": "1980-01-01",
    "personalHealthNumber": "9000000000", "address": "100 Example Street",
    "phonePrimary": "250-000-0000", "description": "All records about me held by the Example Branch",
    "childFirstName": "Sam", "assignedToFirstName": "Alex",
}


def _scenario(**overrides):
    base = {
        "ministry": {"foirequest_id": FOIREQUESTID, "filenumber": "EXM-2026-000123", "axisrequestid": "EXM-2026-000123",
                     "requeststatus.name": "On Hold"},
        "offline": False,
        "contacts": [{"contacttype.name": "Email", "contactinformation": "jane.example@example.com", "dataformat": "email"},
                     {"contacttype.name": "Phone", "contactinformation": "250-000-0000", "dataformat": "phonePrimary"}],
        "approvedcfrfee": {"feedata": {"actualtotaldue": 100.0, "estimatedtotaldue": 80.0, "feewaiveramount": 0}},
        "cfrfee": {"feedata": {"amountpaid": 0}},
        "payment": {},
    }
    base.update(overrides)
    return base


SCENARIOS = {
    "actual total": (_scenario(), "100.00"),
    "estimated total only": (_scenario(approvedcfrfee={"feedata": {"actualtotaldue": 0, "estimatedtotaldue": 80.0, "feewaiveramount": 0}}), "80.00"),
    "partly paid": (_scenario(cfrfee={"feedata": {"amountpaid": 40.0}}), "60.00"),
    "fee waiver": (_scenario(approvedcfrfee={"feedata": {"actualtotaldue": 100.0, "estimatedtotaldue": 80.0, "feewaiveramount": 25.0}}), "75.00"),
    "payment row exists": (_scenario(payment={"paidamount": None, "paymenturl": "https://forms.example/form/a/submission/b",
                                              "created_at": "2026-11-20T10:00:00", "paymentexpirydate": "2026-12-21T00:00:00"}), "100.00"),
    "no approved fee": (_scenario(approvedcfrfee={}), None),
    "no email contact": (_scenario(contacts=[{"contacttype.name": "Phone", "contactinformation": "250-000-0000", "dataformat": "phonePrimary"}]), "100.00"),
    "offline payment": (_scenario(offline=True), "100.00"),
    "missing AXIS id": (_scenario(ministry={"foirequest_id": FOIREQUESTID, "filenumber": "EXM-2026-000123", "axisrequestid": None,
                                            "requeststatus.name": "On Hold"}), "100.00"),
}


class _Ministry:
    def __init__(self, data):
        self.data = data

    def getrequestbyministryrequestid(self, ministryrequestid):
        return copy.deepcopy(self.data["ministry"])

    def getofflinepaymentflag(self, ministryrequestid):
        return self.data["offline"]


def _install(monkeypatch, data):
    """Fakes the database reads that requestservicegetter makes."""
    monkeypatch.setattr(getter_module, "FOIMinistryRequest", _Ministry(data))
    monkeypatch.setattr(getter_module.FOIRequest, "getrequest", staticmethod(lambda foirequestid: {"version": 3}))
    monkeypatch.setattr(getter_module.FOIRequestContactInformation, "getrequestcontactinformation",
                        staticmethod(lambda foirequestid, version: copy.deepcopy(data["contacts"])))

    class _CfrFee:
        def getapprovedcfrfee(self, ministryrequestid):
            return copy.deepcopy(data["approvedcfrfee"])

        def getcfrfee(self, ministryrequestid):
            return copy.deepcopy(data["cfrfee"])

    class _Payment:
        def getpayment(self, foirequestid, ministryrequestid):
            return copy.deepcopy(data["payment"])

    monkeypatch.setattr(getter_module, "cfrfeeservice", _CfrFee)
    monkeypatch.setattr(getter_module, "paymentservice", _Payment)


def _fullrecord(data):
    """What getrequest returns for the keys Camunda reads (requestservicegetter.getrequest/__preparebaseinfo),
    plus personal data the payment details must leave out."""
    record = {"idNumber": data["ministry"]["filenumber"], "axisRequestId": data["ministry"]["axisrequestid"],
              "currentState": data["ministry"]["requeststatus.name"], "isofflinepayment": data["offline"], **PERSONAL}
    for contact in data["contacts"]:
        if contact["contacttype.name"] == "Email":
            record["email"] = contact["contactinformation"]
    return record


def _camunda_reads(response):
    """Mimics the Spin calls in the BPMN after a JSON round trip: KeyError on a missing key, TypeError on a wrong type."""
    body = json.loads(json.dumps(response))

    def string(value):
        if not isinstance(value, str):
            raise TypeError("Spin stringValue() needs a string, got %r" % (value,))
        return value

    def boolean(value):
        if not isinstance(value, bool):
            raise TypeError("Spin boolValue() needs a boolean, got %r" % (value,))
        return value

    return {
        "axisRequestId": string(body["axisRequestId"]),
        "fee": string(body["cfrfee"]["feedata"]["balanceDue"]),
        "fileNumber": string(body["idNumber"]),
        "email": string(body["email"]),
        "isofflinepayment": boolean(body["isofflinepayment"]),
    }


@pytest.mark.parametrize("name", SCENARIOS)
def test_payment_details_match_the_full_record_for_the_keys_camunda_reads(monkeypatch, name):
    data, _ = SCENARIOS[name]
    _install(monkeypatch, data)
    monkeypatch.setattr(requestservicegetter, "getrequest", lambda self, rid, mid: _fullrecord(data))

    full = requestservicegetter().getrequestdetails(FOIREQUESTID, MINISTRYREQUESTID)
    trimmed = requestservicegetter().getpaymentdetails(FOIREQUESTID, MINISTRYREQUESTID)

    expected = {key: full[key] for key in WORKFLOW_KEYS if key in full}
    if "cfrfee" in expected:
        expected["cfrfee"] = {"feedata": {"balanceDue": full["cfrfee"]["feedata"]["balanceDue"]}}
    expected["hasEmail"] = bool(full.get("email"))
    assert json.dumps(trimmed, sort_keys=True) == json.dumps(expected, sort_keys=True)


@pytest.mark.parametrize("name", SCENARIOS)
def test_balance_due_keeps_its_value_and_two_decimal_string_format(monkeypatch, name):
    data, balancedue = SCENARIOS[name]
    _install(monkeypatch, data)
    response = requestservicegetter().getpaymentdetails(FOIREQUESTID, MINISTRYREQUESTID)
    if balancedue is None:
        assert "cfrfee" not in response
    else:
        assert response["cfrfee"]["feedata"]["balanceDue"] == balancedue


@pytest.mark.parametrize("name", ["actual total", "estimated total only", "partly paid", "fee waiver",
                                  "payment row exists", "offline payment"])
def test_camunda_can_read_every_variable_it_needs(monkeypatch, name):
    data, balancedue = SCENARIOS[name]
    _install(monkeypatch, data)
    variables = _camunda_reads(requestservicegetter().getpaymentdetails(FOIREQUESTID, MINISTRYREQUESTID))
    assert variables["fee"] == balancedue
    assert variables["fileNumber"] == "EXM-2026-000123"
    assert variables["email"] == "jane.example@example.com"
    assert variables["isofflinepayment"] is data["offline"]


@pytest.mark.parametrize("name", ["no approved fee", "no email contact", "missing AXIS id"])
def test_edge_cases_fail_for_camunda_exactly_as_the_full_record_does(monkeypatch, name):
    """These cases already stop Camunda today; FOIMOD-5523 must not change that behaviour."""
    data, _ = SCENARIOS[name]
    _install(monkeypatch, data)
    monkeypatch.setattr(requestservicegetter, "getrequest", lambda self, rid, mid: _fullrecord(data))
    full = requestservicegetter().getrequestdetails(FOIREQUESTID, MINISTRYREQUESTID)
    trimmed = requestservicegetter().getpaymentdetails(FOIREQUESTID, MINISTRYREQUESTID)
    errors = []
    for response in (full, trimmed):
        try:
            _camunda_reads(response)
            errors.append(None)
        except (KeyError, TypeError) as error:
            errors.append(type(error))
    assert errors[0] is not None
    assert errors[0] == errors[1]


def test_payment_details_contain_no_personal_data_beyond_the_email(monkeypatch):
    data, _ = SCENARIOS["payment row exists"]
    _install(monkeypatch, data)
    response = requestservicegetter().getpaymentdetails(FOIREQUESTID, MINISTRYREQUESTID)
    assert set(response) == WORKFLOW_KEYS | {"hasEmail"}
    assert response["cfrfee"] == {"feedata": {"balanceDue": "100.00"}}
    serialized = json.dumps(response)
    for value in PERSONAL.values():
        assert value not in serialized
    assert "paymenturl" not in serialized
    assert "forms.example" not in serialized


def test_payment_details_never_load_the_full_record(monkeypatch):
    data, _ = SCENARIOS["actual total"]
    _install(monkeypatch, data)

    def fail(*args, **kwargs):
        raise AssertionError("the full request record must not be loaded")

    monkeypatch.setattr(requestservicegetter, "getrequest", fail)
    monkeypatch.setattr(requestservicegetter, "getrequestdetails", fail)
    assert requestservicegetter().getpaymentdetails(FOIREQUESTID, MINISTRYREQUESTID)["idNumber"] == "EXM-2026-000123"


def test_returns_none_when_the_ministry_request_belongs_to_another_request(monkeypatch):
    data, _ = SCENARIOS["actual total"]
    _install(monkeypatch, data)
    assert requestservicegetter().getpaymentdetails(FOIREQUESTID + 1, MINISTRYREQUESTID) is None


def test_n8n_can_read_the_request_status(monkeypatch):
    """n8n's "Compute Payment Vars" reads currentState and writes it to the Form.io submission as status."""
    data, _ = SCENARIOS["actual total"]
    _install(monkeypatch, data)
    response = requestservicegetter().getpaymentdetails(FOIREQUESTID, MINISTRYREQUESTID)
    assert response["currentState"] == "On Hold"


@pytest.mark.parametrize("contacts, expected", [
    ([{"contacttype.name": "Email", "contactinformation": "jane.example@example.com", "dataformat": "email"}], True),
    ([{"contacttype.name": "Email", "contactinformation": "", "dataformat": "email"}], False),
    ([{"contacttype.name": "Email", "contactinformation": None, "dataformat": "email"}], False),
    ([{"contacttype.name": "Phone", "contactinformation": "250-000-0000", "dataformat": "phonePrimary"}], False),
    ([], False),
], ids=["email", "empty email", "null email", "no email contact", "no contacts"])
def test_has_email_says_whether_the_applicant_can_be_emailed(monkeypatch, contacts, expected):
    """hasEmail is always a boolean, so n8n can decide 'no email, no online payment' without the address."""
    data, _ = SCENARIOS["actual total"]
    _install(monkeypatch, {**data, "contacts": contacts})
    response = requestservicegetter().getpaymentdetails(FOIREQUESTID, MINISTRYREQUESTID)
    assert response["hasEmail"] is expected
    assert json.loads(json.dumps(response))["hasEmail"] is expected


def _camunda_outcome(response):
    """The process variables Camunda sets from payonline, or the error that stops it."""
    try:
        return _camunda_reads(response)
    except (KeyError, TypeError) as error:
        return type(error)


@pytest.mark.parametrize("name", SCENARIOS)
def test_camunda_behaviour_is_unchanged(monkeypatch, name):
    """Camunda sets exactly the same process variables (or fails the same way) as with the full record, in every
    case. Extra keys (currentState, hasEmail) are ignored: the BPMN copies only its five output parameters, and
    everything after that step (gateway, Form.io submission, emails) works from those variables."""
    data, _ = SCENARIOS[name]
    _install(monkeypatch, data)
    monkeypatch.setattr(requestservicegetter, "getrequest", lambda self, rid, mid: _fullrecord(data))
    before = _camunda_outcome(requestservicegetter().getrequestdetails(FOIREQUESTID, MINISTRYREQUESTID))
    after = _camunda_outcome(requestservicegetter().getpaymentdetails(FOIREQUESTID, MINISTRYREQUESTID))
    assert after == before


@pytest.mark.parametrize("name", SCENARIOS)
def test_n8n_never_gets_the_email_address(monkeypatch, name):
    """With includeemail=False (WF_DEFAULT_ENGINE=n8n) the address is left out; hasEmail still says if there is one."""
    data, _ = SCENARIOS[name]
    _install(monkeypatch, data)
    withemail = requestservicegetter().getpaymentdetails(FOIREQUESTID, MINISTRYREQUESTID)
    response = requestservicegetter().getpaymentdetails(FOIREQUESTID, MINISTRYREQUESTID, includeemail=False)
    assert "email" not in response
    assert "jane.example@example.com" not in json.dumps(response)
    assert response["hasEmail"] is withemail["hasEmail"]
    assert {k: v for k, v in withemail.items() if k != "email"} == response
