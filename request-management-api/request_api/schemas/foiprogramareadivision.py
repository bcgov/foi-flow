from marshmallow import EXCLUDE, Schema, fields

class FOIProgramAreaDivisionSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    programareaid = fields.Int(data_key="programareaid")
    name = fields.Str(data_key="name")
    isactive = fields.Bool(data_key="isactive",allow_none=True)
