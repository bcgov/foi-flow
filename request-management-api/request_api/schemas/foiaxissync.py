from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE

class FOIAxisProgramDetailsSchema(Schema):
    
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    iaocode = fields.Str(data_key="iaocode",allow_none=False) 
    requesttype = fields.Str(data_key="requesttype",allow_none=False)     
    
class FOIRequestAxisSyncSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    data = fields.Nested(FOIAxisProgramDetailsSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)
