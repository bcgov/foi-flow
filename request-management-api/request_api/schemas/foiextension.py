

from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of extension operations.

__author__      = "divya.v@aot-technologies.com"

"""

class FOIMinistryRequestDocumentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    foiministrydocumentid = fields.Int(data_key="foiministrydocumentid",required=False, allow_none=True)
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
    extendedduedate = fields.Str(data_key="extendedduedate")
    decisiondate = fields.Str(data_key="decisiondate",required=False, allow_none=True)
    approvednoofdays = fields.Int(data_key="approvednoofdays", required=False, allow_none=True)
    version = fields.Int(data_key="version")
    foiministryrequest_id = fields.Int(data_key="foiministryrequest_id")
    foiministryrequestversion_id = fields.Int(data_key="foiministryrequestversion_id")  
    isactive = fields.Bool(data_key="isactive",allow_none=True)
    documents = fields.Nested(FOIMinistryRequestDocumentSchema, required=False, many=True, allow_none=True)