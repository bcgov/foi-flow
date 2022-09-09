from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE

class FOIApplicantCorrespondenceSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    templateid = fields.Int(data_key="templateid",allow_none=True)
    correspondencemessagejson = fields.Str(data_key="correspondencemessagejson",allow_none=False)
    
    