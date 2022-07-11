from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE

class FOIRequestAssigneeSchema(Schema):
    
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    assignedministrygroup = fields.Str(data_key="assignedministrygroup",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])   
    assignedministryperson = fields.Str(data_key="assignedministryperson",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    assignedministrypersonFirstName = fields.Str(data_key="assignedministrypersonFirstName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    assignedministrypersonMiddleName = fields.Str(data_key="assignedministrypersonMiddleName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    assignedministrypersonLastName = fields.Str(data_key="assignedministrypersonLastName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    assignedgroup = fields.Str(data_key="assignedGroup",allow_none=True, validate=[validate.Length(max=250, error=MAX_EXCEPTION_MESSAGE)])   
    assignedto = fields.Str(data_key="assignedTo",allow_none=True, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    assignedToFirstName = fields.Str(data_key="assignedToFirstName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    assignedToMiddleName = fields.Str(data_key="assignedToMiddleName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    assignedToLastName = fields.Str(data_key="assignedToLastName",allow_none=True, validate=[validate.Length(max=50, error=MAX_EXCEPTION_MESSAGE)])
    