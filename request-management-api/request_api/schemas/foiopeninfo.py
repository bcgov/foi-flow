from marshmallow import EXCLUDE, Schema, fields

class FOIOpenInfoSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE    
    foiministryrequest_id = fields.Int(data_key="foiministryrequest_id")
    oipublicationstatus_id = fields.Int(data_key="oipublicationstatus_id")
    oiexemption_id = fields.Int(data_key="oiexemption_id",allow_none=True)
    oiassignedto = fields.Str(data_key="oiassignedto",allow_none=True)
    oiexemptionapproved = fields.Bool(data_key="oiexemptionapproved",allow_none=True)
    pagereference = fields.Str(data_key="pagereference",allow_none=True)
    iaorationale = fields.Str(data_key="iaorationale",allow_none=True)
    oifeedback = fields.Str(data_key="oifeedback",allow_none=True)
    publicationdate = fields.Date(data_key="publicationdate",allow_none=True)