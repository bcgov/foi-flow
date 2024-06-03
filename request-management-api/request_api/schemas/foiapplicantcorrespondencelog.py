from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE


class AttachmentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    filename = fields.Str(data_key="filename",required=True,allow_none=False, validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    url = fields.Str(data_key="url",required=True,allow_none=False, validate=[validate.Length(max=1000, error=MAX_EXCEPTION_MESSAGE)])
   

class FOIApplicantCorrespondenceSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    templateid = fields.Int(data_key="templateid",allow_none=True)
    correspondencemessagejson = fields.Str(data_key="correspondencemessagejson",allow_none=False)
    attachments = fields.Nested(AttachmentSchema, many=True, required=False,allow_none=True)
    emails = fields.List(fields.Str(),data_key="emails", required=False,allow_none=True)
    attributes = fields.List(
        fields.Dict(fields.Str(), fields.Str()),
        data_key="attributes",
        required=False,
    )


class FOIApplicantCorrespondenceEmailSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    email = fields.Str(data_key="email",allow_none=True ,validate=[validate.Length(max=350, error=MAX_EXCEPTION_MESSAGE)])
    