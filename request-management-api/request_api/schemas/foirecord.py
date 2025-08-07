

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

class PersonalAttributesSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE 
    person = fields.Str(data_key="person",allow_none=True)
    filetype = fields.Str(data_key="filetype",allow_none=True)
    volume = fields.Str(data_key="volume",allow_none=True)
    trackingid = fields.Str(data_key="trackingid",allow_none=True)
    personaltag = fields.Str(data_key="personaltag",allow_none=True)
    # divisions = fields.Nested(DivisionSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)

class CreateRecordAttributeSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE 
    #divisions = fields.List(fields.Int(),data_key="divisions",required=True)
    divisions = fields.Nested(DivisionSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)
    lastmodified = fields.Str(data_key="lastmodified",allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    filesize = fields.Int(data_key="filesize", allow_none=False)
    parentpdfmasterid = fields.Int(required=False,allow_none=True)
    personalattributes = fields.Nested(PersonalAttributesSchema,required=False,allow_none=True)

class FOIRequestCreateRecordSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    attributes = fields.Nested(CreateRecordAttributeSchema)
    s3uripath = fields.Str(data_key="s3uripath",allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
    filename = fields.Str(data_key="filename",allow_none=False, validate=[validate.Length(max=500, error=MAX_EXCEPTION_MESSAGE)])



class FOIRequestBulkCreateRecordSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    records = fields.Nested(FOIRequestCreateRecordSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)

class RetryRecordAttributeSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    #divisions = fields.List(fields.Int(),data_key="divisions",required=True)
    divisions = fields.Nested(DivisionSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)
    lastmodified = fields.Str(data_key="lastmodified",allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    filesize = fields.Int(data_key="filesize", allow_none=False)
    convertedfilesize = fields.Int(data_key="convertedfilesize", allow_none=True)
    trigger = fields.Str(data_key="trigger", allow_none=True)
    batch = fields.Str(data_key="batch", allow_none=False, validate=validate.Length(min=1), required=True)
    incompatible = fields.Boolean(required=True,allow_none=False)
    extension = fields.Str(validate=validate.Length(min=1, max=10), required=True,allow_none=False)
    isattachment = fields.Boolean(required=False,allow_none=False)
    personalattributes = fields.Nested(PersonalAttributesSchema,required=False,allow_none=True)

class ReplaceRecordAttributeSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    divisions = fields.Nested(DivisionSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)
    lastmodified = fields.Str(data_key="lastmodified",allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    filesize = fields.Int(data_key="filesize", allow_none=False)
    batch = fields.Str(data_key="batch", allow_none=False, validate=validate.Length(min=1), required=True)
    incompatible = fields.Boolean(required=True,allow_none=False)
    extension = fields.Str(validate=validate.Length(min=1, max=10), required=True,allow_none=False)
    isattachment = fields.Boolean(required=False,allow_none=False)
    hasfilereplaced = fields.Boolean(required=False,allow_none=False)
    personalattributes = fields.Nested(PersonalAttributesSchema,required=False,allow_none=True)

class FOIRequestRetryRecordSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    attributes = fields.Nested(RetryRecordAttributeSchema)
    s3uripath = fields.Str(data_key="s3uripath",allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
    filename = fields.Str(data_key="filename",allow_none=False, validate=[validate.Length(max=500, error=MAX_EXCEPTION_MESSAGE)])
    trigger = fields.Str(validate=validate.OneOf(['recordreplace', 'recordretry']), required=True,allow_none=False)
    service = fields.Str(validate=validate.OneOf(['deduplication', 'conversion', 'compression', 'ocr', "all"]), required=False,allow_none=False)
    documentmasterid = fields.Integer(required=True,allow_none=True)
    outputdocumentmasterid = fields.Integer(required=False,allow_none=True)
    createdby = fields.Str(validate=validate.Length(min=1),required=True,allow_none=False)

class FOIRequestReplaceRecordSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    attributes = fields.Nested(ReplaceRecordAttributeSchema)
    s3uripath = fields.Str(data_key="s3uripath",allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
    filename = fields.Str(data_key="filename",allow_none=False, validate=[validate.Length(max=500, error=MAX_EXCEPTION_MESSAGE)])
    replacements3uripath = fields.Str(data_key="replacements3uripath",allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
    replacementfilename = fields.Str(data_key="replacementfilename",allow_none=False, validate=[validate.Length(max=500, error=MAX_EXCEPTION_MESSAGE)])
    trigger = fields.Str(data_key="trigger",validate=validate.OneOf(['recordreplace', 'recordretry']),allow_none=False)
    service = fields.Str(data_key="service",validate=validate.OneOf(['deduplication', 'conversion']),allow_none=False)
    replacementof = fields.Str(data_key="replacementof",allow_none=True)
    

class FOIRequestBulkRetryRecordSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    records = fields.Nested(FOIRequestRetryRecordSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)


class FileSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE 
    recordid = fields.Int(data_key="recordid",allow_none=True)
    filename = fields.Str(data_key="filename",allow_none=False, validate=[validate.Length(max=500, error=MAX_EXCEPTION_MESSAGE)])
    s3uripath = fields.Str(data_key="s3uripath",allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
    lastmodified = fields.Str(data_key="lastmodified",allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    filesize = fields.Number(data_key="filesize")

class DownloadRecordAttributeSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE 
    files = fields.Nested(FileSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)
    divisionname = fields.Str(data_key="divisionname",allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    divisionid = fields.Int(data_key="divisionid", allow_none=False)
    divisionfilesize = fields.Number(data_key="divisionfilesize")

class FOIRequestRecordDownloadSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    requestnumber = fields.Str(data_key="requestnumber",allow_none=False, validate=[validate.Length(max=100, error=MAX_EXCEPTION_MESSAGE)])
    bcgovcode = fields.Str(data_key="bcgovcode",allow_none=False, validate=[validate.Length(max=20, error=MAX_EXCEPTION_MESSAGE)])
    category = fields.Str(data_key="category",allow_none=False, validate=[validate.Length(max=25, error=MAX_EXCEPTION_MESSAGE)])
    attributes = fields.Nested(DownloadRecordAttributeSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)
    totalfilesize = fields.Number(data_key="totalfilesize")

class RecordSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE 
    recordid = fields.Int(data_key="recordid",allow_none=True)
    documentmasterid = fields.Int(data_key="documentmasterid",allow_none=False)
    filepath = fields.String(data_key="filepath",allow_none=False,validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])

class FOIRequestRecordUpdateSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    records = fields.Nested(RecordSchema,many=True,data_key="records",required=True)
    divisions = fields.Nested(DivisionSchema,many=True,validate=validate.Length(min=1),required=False,allow_none=True)
    isdelete = fields.Boolean(required=True,allow_none=False)

class FOIRequestPersonalAttributesUpdateSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    records = fields.Nested(RecordSchema,many=True,data_key="records",required=True)
    newpersonalattributes = fields.Nested(PersonalAttributesSchema,required=True)
