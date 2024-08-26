

from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of watcher operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class FOIRawRequestCommentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    requestid = fields.Int(data_key="requestid")
    comment = fields.Str(data_key="comment")
    parentcommentid = fields.Int(data_key="parentcommentid",allow_none=True)
    isactive = fields.Bool(data_key="isactive",allow_none=True)
    taggedusers = fields.Str(data_key="taggedusers")
    commenttypeid= fields.Int(data_key="commenttypeid",allow_none=True)

class FOIMinistryRequestCommentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    ministryrequestid = fields.Int(data_key="ministryrequestid")
    comment = fields.Str(data_key="comment")
    parentcommentid = fields.Int(data_key="parentcommentid",allow_none=True)
    isactive = fields.Bool(data_key="isactive",allow_none=True)
    taggedusers = fields.Str(data_key="taggedusers")
    commenttypeid= fields.Int(data_key="commenttypeid",allow_none=True)
    
class EditFOIRawRequestCommentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    comment = fields.Str(data_key="comment")
    taggedusers = fields.Str(data_key="taggedusers")
    commenttypeid= fields.Int(data_key="commenttypeid",allow_none=True)




class EditFOIMinistryRequestCommentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    comment = fields.Str(data_key="comment")
    taggedusers = fields.Str(data_key="taggedusers")
    