

from marshmallow import EXCLUDE, Schema, fields, validate
from request_api.utils.constants import MAX_EXCEPTION_MESSAGE

"""
This class  consolidates schemas of watcher operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class FOIRawRequestWatcherSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    requestid = fields.Int(data_key="requestid")
    watchedbygroup = fields.Str(data_key="watchedbygroup",allow_none=True, validate=[validate.Length(max=250, error=MAX_EXCEPTION_MESSAGE)])
    watchedby = fields.Str(data_key="watchedby", validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    isactive = fields.Bool(data_key="isactive")
    fullname = fields.Str(data_key="fullname",allow_none=True ,validate=[validate.Length(max=250, error=MAX_EXCEPTION_MESSAGE)])


class FOIMinistryRequestWatcherSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    ministryrequestid = fields.Int(data_key="ministryrequestid")
    watchedbygroup = fields.Str(data_key="watchedbygroup",allow_none=True, validate=[validate.Length(max=250, error=MAX_EXCEPTION_MESSAGE)])
    watchedby = fields.Str(data_key="watchedby", validate=[validate.Length(max=120, error=MAX_EXCEPTION_MESSAGE)])
    isactive = fields.Bool(data_key="isactive")
    fullname = fields.Str(data_key="fullname",allow_none=True ,validate=[validate.Length(max=250, error=MAX_EXCEPTION_MESSAGE)])