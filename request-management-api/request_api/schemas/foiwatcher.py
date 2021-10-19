

from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of watcher operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class FOIRawRequestWatcherSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    requestid = fields.Int(data_key="requestid")
    watchedbygroup = fields.Str(data_key="watchedbygroup",allow_none=True)
    watchedby = fields.Str(data_key="watchedby")
    isactive = fields.Bool(data_key="isactive")


class FOIMinistryRequestWatcherSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    ministryrequestid = fields.Int(data_key="ministryrequestid")
    watchedbygroup = fields.Str(data_key="watchedbygroup",allow_none=True)
    watchedby = fields.Str(data_key="watchedby")
    isactive = fields.Bool(data_key="isactive")