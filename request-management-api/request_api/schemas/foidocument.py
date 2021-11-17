

from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of document operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class RenameDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    filename = fields.Str(data_key="filename")

class ReplaceDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    filename = fields.Str(data_key="filename")
    documentpath = fields.Str(data_key="documentpath")
    category = fields.Str(data_key="category",allow_none=True)
    

class DocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    filename = fields.Str(data_key="filename")
    documentpath = fields.Str(data_key="documentpath")
    category = fields.Str(data_key="category",allow_none=True)   

class CreateDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    documents = fields.Nested(DocumentSchema, many=True)