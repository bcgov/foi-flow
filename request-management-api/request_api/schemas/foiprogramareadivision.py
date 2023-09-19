from marshmallow import EXCLUDE, Schema, fields, validates_schema, ValidationError
from request_api.services.programareadivisionservice import programareadivisionservice

class FOIProgramAreaDivisionSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    programareaid = fields.Int(data_key="programareaid")
    name = fields.Str(data_key="name")
    isactive = fields.Bool(data_key="isactive",allow_none=True)
    sortorder = fields.Int(data_key="sortorder",allow_none=True)
    issection = fields.Bool(data_key="issection", allow_none=False)
    parentid = fields.Int(data_key="parentid", allow_none=True)
    specifictopersonalrequests = fields.Bool(data_key="specifictopersonalrequests", allow_none=True)

    @validates_schema
    def validate_parentid(self, data):
        parentdivision = programareadivisionservice().getparentdivisionforsection(data.parentid)
        print(parentdivision)
        if data.parentid is not None and len(parentdivision) <=  0:
            raise ValidationError("parentid provided does not return a valid parent division")