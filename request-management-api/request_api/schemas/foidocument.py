

from marshmallow import EXCLUDE, Schema, fields, validate

"""
This class  consolidates schemas of document operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class RenameDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    filename = fields.Str(data_key="filename",required=True,allow_none=False)

class ReplaceDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    filename = fields.Str(data_key="filename",required=True,allow_none=False)
    documentpath = fields.Str(data_key="documentpath",required=True,allow_none=False)
    category = fields.Str(data_key="category",allow_none=True)
    

class DocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    filename = fields.Str(data_key="filename",required=True,allow_none=False)
    documentpath = fields.Str(data_key="documentpath",required=True,allow_none=False)
    category = fields.Str(data_key="category",allow_none=True)   

class CreateDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    documents = fields.Nested(DocumentSchema, many=True, validate=validate.Length(min=1), required=True,allow_none=False)