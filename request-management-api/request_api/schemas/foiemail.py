
from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of email operations.
"""
class FOIEmailSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    templatename = fields.Str(data_key="templateName", allow_none=True)
    applicantcorrespondenceid = fields.Int(data_key="applicantCorrespondenceId",allow_none=True)