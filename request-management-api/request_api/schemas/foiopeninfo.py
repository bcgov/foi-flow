from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE


class FOIOpenInfoAdditionalFileSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE    
    s3uripath = fields.Str(data_key="s3uripath",allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
    filename = fields.Str(data_key="filename",allow_none=False, validate=[validate.Length(max=500, error=MAX_EXCEPTION_MESSAGE)])

class FOIOpenInfoSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE    
    oipublicationstatus_id = fields.Int(data_key="oipublicationstatus_id")
    oiexemption_id = fields.Int(data_key="oiexemption_id",allow_none=True, missing=None)
    oiassignedto = fields.Str(data_key="oiassignedto",allow_none=True, missing=None)
    oiexemptionapproved = fields.Bool(data_key="oiexemptionapproved",allow_none=True, missing=None)
    pagereference = fields.Str(data_key="pagereference",allow_none=True, missing=None)
    iaorationale = fields.Str(data_key="iaorationale",allow_none=True, missing=None)
    oifeedback = fields.Str(data_key="oifeedback",allow_none=True, missing=None)
    publicationdate = fields.Str(data_key="publicationdate",allow_none=True, missing=None)
    oiexemptiondate = fields.Str(data_key="oiexemptiondate",allow_none=True, missing=None)
    copyrightsevered = fields.Bool(data_key="copyrightsevered",allow_none=True, missing=None)

class FOIOpenInfoAdditionalFilesSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE
    additionalfiles = fields.List(fields.Nested(FOIOpenInfoAdditionalFileSchema), required=True,allow_none=False)

class FOIOpenInfoAdditionalFilesDeleteSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE
    fileids = fields.List(fields.Int(),data_key="fileids",required=True,allow_none=False)
