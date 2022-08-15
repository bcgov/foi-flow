

from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of payment operations.

__author__      = "sumathi.thirumani@aot-technologies.com"

"""
class FOIRequestPaymentSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    paymenturl = fields.Str(data_key="paymenturl")
    paymentexpirydate = fields.Date(data_key="paymentexpirydate")