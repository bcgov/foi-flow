from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of bpm operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class VariableSchema(Schema):
    type = fields.Str()
    value = fields.Str()
    
 
class MessageSchema(Schema):

    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    messageName = fields.Str(data_key="messageName")
    processInstanceId = fields.Str(data_key="processInstanceId")
    processVariables = fields.Dict(keys=fields.String(),values=fields.Nested(VariableSchema))
    localCorrelationKeys = fields.Dict(keys=fields.String(),values=fields.Nested(VariableSchema))
    correlationKeys = fields.Dict(keys=fields.String(),values=fields.Nested(VariableSchema))
    
class VariableMessageSchema(Schema):
    
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE

    variables = fields.Dict(keys=fields.String(),values=fields.Nested(VariableSchema))
    