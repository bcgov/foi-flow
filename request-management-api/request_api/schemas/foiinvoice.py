from marshmallow import EXCLUDE, Schema, fields, validate, INCLUDE
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE

class CFRFeeDataSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = INCLUDE
    foirequestcfrfee_id = fields.Int(data_key="cfrfeeid", required=True, allow_none=False)
    foirequestcfrfeeversion_id = fields.Int(data_key="version", required=True, allow_none=False)

class FOIRequestInvoiceSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE    
    applicant_name = fields.Str(data_key="applicantName", allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)], required=True)
    applicant_address = fields.Str(data_key="applicantAddress", allow_none=False, validate=[validate.Length(max=200, error=MAX_EXCEPTION_MESSAGE)], required=True)
    cfrfeedata = fields.Nested(CFRFeeDataSchema, data_key="cfrFeeData", allow_none=False, required=True)