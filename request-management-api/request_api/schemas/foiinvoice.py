from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE

class FOIRequestInvoiceSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE    
    created_by = fields.Str(data_key="created_by", allow_None=False)
    applicant_name = fields.Str(data_key="applicant_name", allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    applicant_address = fields.Str(data_key="applicant_address", allow_none=False, validate=[validate.Length(max=200, error=MAX_EXCEPTION_MESSAGE)])
