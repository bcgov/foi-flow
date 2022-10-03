

from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE

"""
This class  consolidates schemas of record operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class FOIRequestCreateRecordSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    divisionid = fields.Int(data_key="divisionid")
    s3uripath = fields.Str(data_key="s3uripath",allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
    filename = fields.Str(data_key="filename",allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    #attributes = fields.List(
    #    fields.Dict(fields.Str(), fields.Str()),
    #    data_key="attributes",
    #    required=False,
    #)


class FOIRequestBulkCreateRecordSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    records = fields.Nested(FOIRequestCreateRecordSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)