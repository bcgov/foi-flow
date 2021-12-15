from marshmallow import EXCLUDE, Schema, fields


class FOIRequestsFormsList(Schema):
    class Meta:
        unknown = EXCLUDE

    ministrycode = fields.Str(data_key="ministrycode",allow_none=False)
    requestnumber = fields.Str(data_key="requestnumber",allow_none=False)
    filestatustransition = fields.Str(data_key="filestatustransition",allow_none=False) 
    filename = fields.Str(data_key="filename",allow_none=False)
    filepath = fields.Str(data_key="filepath",allow_none=True)
    authheader = fields.Str(data_key="authheader",allow_none=True)
    amzdate = fields.Str(data_key="amzdate",allow_none=True) 
    s3sourceuri = fields.Str(data_key="s3sourceuri",allow_none=True)      