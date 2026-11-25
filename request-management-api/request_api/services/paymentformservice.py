import os

from request_api.services.external.formioservice import FormioNotConfigured, FormioNotFound, formioservice
from request_api.services.requestservice import requestservice

"""
Payment rules on top of the Form.io client (FOIMOD-5525): create the applicant's payment submission and
update its payment status. Errors carry short fixed messages: no ids, Form.io bodies or payment URLs.
"""

PAYMENT_FORMS = {"payonline": "payfeeonline", "payoutstanding": "payoutstandingform"}
PAYMENT_STATUSES = ("PAID", "CANCELLED")


class PaymentFormError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class paymentformservice:

    def createpaymentformsubmission(self, requestid: int, ministryrequestid: int, formtype: str) -> dict:
        formname = PAYMENT_FORMS.get(formtype)
        if formname is None:
            raise PaymentFormError(400, "Unknown payment form type")
        webkey = "FORMSFLOW_WEB_URL"
        weburl = (os.getenv(webkey) or "").strip().rstrip("/")
        if not weburl:
            raise FormioNotConfigured(webkey)
        details = requestservice().getpaymentdetails(requestid, ministryrequestid, includeemail=False)
        if details is None:
            raise PaymentFormError(404, "Request not found")
        try:
            balancedue = float(details["cfrfee"]["feedata"]["balanceDue"])
        except (KeyError, TypeError, ValueError):
            raise PaymentFormError(400, "No approved fee estimate for this request") from None
        if balancedue <= 0:
            raise PaymentFormError(400, "No balance due for this request")
        client = formioservice()
        formid = client.getformid(formname)
        created = client.createsubmission(
            formid,
            {
                "ministryRequestID": str(ministryrequestid),
                "balanceDue": balancedue,
                "axisRequestId": details.get("axisRequestId"),
                "fileNumber": details.get("idNumber"),
                "paymentstatus": "NOT PAID",
                "status": details.get("currentState"),
            },
        )
        return {
            "formId": created["formId"],
            "submissionId": created["submissionId"],
            "paymentUrl": f"{weburl}/public/form/{created['formId']}/submission/{created['submissionId']}/edit",
        }

    def updatepaymentformsubmission(
        self,
        requestid: int,
        ministryrequestid: int,
        formid: str,
        submissionid: str,
        paymentstatus: str,
        status: str | None = None,
    ) -> dict:
        if paymentstatus not in PAYMENT_STATUSES:
            raise PaymentFormError(400, "Unknown payment status")
        client = formioservice()
        if formid not in {client.getformid(name) for name in PAYMENT_FORMS.values()}:
            raise PaymentFormError(400, "Not a payment form")
        try:
            submission = client.getsubmission(formid, submissionid)
        except FormioNotFound:
            raise PaymentFormError(404, "Payment submission not found") from None
        data = submission.get("data")
        stored = data.get("ministryRequestID") if isinstance(data, dict) else None
        if stored is None or str(stored) != str(ministryrequestid):
            raise PaymentFormError(404, "Payment submission not found")
        fields = {"paymentstatus": paymentstatus}
        if status:
            fields["status"] = status
        client.patchsubmission(formid, submissionid, fields)
        return {"formId": formid, "submissionId": submissionid}
