

from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of payment operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class FOIRequestPaymentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    paymenturl = fields.Str(data_key="paymenturl")
    paymentexpirydate = fields.Date(data_key="paymentexpirydate")


from marshmallow import validate


class PaymentFormSubmissionCreateSchema(Schema):
    """FOIMOD-5525: body of POST .../formsubmission."""

    class Meta:  # pylint: disable=too-few-public-methods
        unknown = EXCLUDE

    formType = fields.Str(required=True, validate=validate.OneOf(["payonline", "payoutstanding"]))


class PaymentFormSubmissionUpdateSchema(Schema):
    """FOIMOD-5525: body of PATCH .../formsubmission. Form.io ids are 24 lowercase hex characters."""

    class Meta:  # pylint: disable=too-few-public-methods
        unknown = EXCLUDE

    formId = fields.Str(required=True, validate=validate.Regexp(r"^[0-9a-f]{24}$"))
    submissionId = fields.Str(required=True, validate=validate.Regexp(r"^[0-9a-f]{24}$"))
    paymentStatus = fields.Str(required=True, validate=validate.OneOf(["PAID", "CANCELLED"]))
    status = fields.Str(allow_none=True, load_default=None)
