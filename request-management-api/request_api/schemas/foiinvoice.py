from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE

class FOIRequestInvoiceSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE    
    applicant_name = fields.Str(data_key="applicantName", allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)], required=True)
    applicant_address = fields.Str(data_key="applicantAddress", allow_none=False, validate=[validate.Length(max=200, error=MAX_EXCEPTION_MESSAGE)], required=True)

    # TO DO ADD FEE DATA TO THIS SCHEMA (USE THE CFR FEE DATA SCHEMA FOR REFERENCE)
