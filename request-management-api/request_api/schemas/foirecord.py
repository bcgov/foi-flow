

from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE

"""
This class  consolidates schemas of record operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class DivisionSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE 
    divisionid = fields.Int(data_key="divisionid",allow_none=False)

class CreateRecordAttributeSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE 
    #divisions = fields.List(fields.Int(),data_key="divisions",required=True)
    divisions = fields.Nested(DivisionSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)

class FOIRequestCreateRecordSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    attributes = fields.Nested(CreateRecordAttributeSchema)
    s3uripath = fields.Str(data_key="s3uripath",allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
    filename = fields.Str(data_key="filename",allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])



class FOIRequestBulkCreateRecordSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    records = fields.Nested(FOIRequestCreateRecordSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)