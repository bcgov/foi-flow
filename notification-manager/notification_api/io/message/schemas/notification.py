from marshmallow import EXCLUDE, fields

"""
This class  consolidates schemas of Notifications.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""


class NotificationPublishSchema(object):
    batch = fields.Str(data_key="batch", allow_none=False)
    ministryrequestid = fields.Int(data_key="ministryrequestid", allow_none=False)
    serviceid = fields.Str(data_key="serviceid", allow_none=False)
    errorflag = fields.Str(data_key="errorflag", allow_none=False)
    createdby = fields.Str(data_key="message", allow_none=False)


class NotificationHarmsPDFStitchPublishSchema(object):
    ministryrequestid = fields.Int(data_key="ministryrequestid", allow_none=False)
    serviceid = fields.Str(data_key="serviceid", allow_none=False)
    errorflag = fields.Str(data_key="errorflag", allow_none=False)
    createdby = fields.Str(data_key="message", allow_none=False)
    totalskippedfilecount = fields.Int(
        data_key="totalskippedfilecount", allow_none=True
    )
    totalskippedfiles = fields.List(
        fields.String(), data_key="totalskippedfiles", allow_none=True
    )


class NotificationRedlineResponsePDFStitchPublishSchema(object):
    ministryrequestid = fields.Int(data_key="ministryrequestid", allow_none=False)
    serviceid = fields.Str(data_key="serviceid", allow_none=False)
    errorflag = fields.Str(data_key="errorflag", allow_none=False)
    createdby = fields.Str(data_key="message", allow_none=False)
    feeoverridereason= fields.Str(data_key="feeoverridereason", allow_none=True)
