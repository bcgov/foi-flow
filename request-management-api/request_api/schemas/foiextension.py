

from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of extension operations.

__author__      = "divya.v@aot-technologies.com"

"""

class FOIMinistryRequestDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    documentpath = fields.Str(data_key="documentpath",allow_none=False)
    filename = fields.Str(data_key="filename",allow_none=False)
    category = fields.Str(data_key="category",allow_none=False)

class FOIRequestExtensionSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    extensionreasonid = fields.Int(data_key="extensionreasonid")
    extendedduedays = fields.Int(data_key="extendedduedays")
    extensionstatusid = fields.Int(data_key="extensionstatusid")
    extendedduedate = fields.Date(data_key="extendedduedate")
    decisiondate = fields.Date(data_key="decisiondate")
    approvednoofdays = fields.Int(data_key="approvednoofdays")
    version = fields.Int(data_key="version")
    foiministryrequest_id = fields.Int(data_key="foiministryrequest_id")
    foiministryrequestversion_id = fields.Int(data_key="foiministryrequestversion_id")  
    isactive = fields.Bool(data_key="isactive",allow_none=True)
    documents = fields.Nested(FOIMinistryRequestDocumentSchema, required=False, many=True, allow_none=True)