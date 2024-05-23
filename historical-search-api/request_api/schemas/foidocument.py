

from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE

"""
This class  consolidates schemas of document operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class RenameDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    filename = fields.Str(data_key="filename",required=True,allow_none=False)

class ReclassifyDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    category = fields.Str(data_key="category",required=True,allow_none=False)

class ReplaceDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    filename = fields.Str(data_key="filename",required=True,allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    documentpath = fields.Str(data_key="documentpath",required=True,allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
    category = fields.Str(data_key="category",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    

class DocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    filename = fields.Str(data_key="filename",required=True,allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    documentpath = fields.Str(data_key="documentpath",required=True,allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
    category = fields.Str(data_key="category",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])   

class CreateDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    documents = fields.Nested(DocumentSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)