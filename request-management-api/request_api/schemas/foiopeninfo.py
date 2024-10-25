from marshmallow import EXCLUDE, Schema, fields

class FOIOpenInfoSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        unknown = EXCLUDE    
    oipublicationstatus_id = fields.Int(data_key="oipublicationstatus_id")
    oiexemption_id = fields.Int(data_key="oiexemption_id",allow_none=True, missing=None)
    oiassignedto = fields.Str(data_key="oiassignedto",allow_none=True, missing=None)
    oiexemptionapproved = fields.Bool(data_key="oiexemptionapproved",allow_none=True, missing=None)
    pagereference = fields.Str(data_key="pagereference",allow_none=True, missing=None)
    iaorationale = fields.Str(data_key="iaorationale",allow_none=True, missing=None)
    oifeedback = fields.Str(data_key="oifeedback",allow_none=True, missing=None)
    publicationdate = fields.Date(data_key="publicationdate",allow_none=True, missing=None)