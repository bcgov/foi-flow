
from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of CFR Fee Form operations.

__author__      = "aparna.s@aot-technologies.com"

"""


class FOIFeeDataSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE
    amountpaid = fields.Float(data_key="amountpaid")
    amountdue = fields.Float(data_key="amountdue")
    locatingestimatedhrs = fields.Float(data_key="locatingestimatedhrs")
    locatingactualhrs = fields.Float(data_key="locatingactualhrs")
    producingestimatedhrs = fields.Float(data_key="producingestimatedhrs")
    producingactualhrs = fields.Float(data_key="producingactualhrs")
    preparingestimatedhrs = fields.Float(data_key="preparingestimatedhrs")
    preparingactualhrs = fields.Float(data_key="preparingactualhrs")
    electronicestimatedpages = fields.Int(data_key="electronicestimatedpages")
    electronicactualpages = fields.Int(data_key="electronicactualpages")
    hardcopyestimatedpages = fields.Int(data_key="hardcopyestimatedpages")
    hardcopyactualpages = fields.Int(data_key="hardcopyactualpages")


class FOICFRFeeSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

        unknown = EXCLUDE    
    ministryrequestid = fields.Int(data_key="ministryrequestid")
    feedata = fields.Nested(FOIFeeDataSchema,allow_none=False)
    overallsuggestions = fields.Str(data_key="overallsuggestions")
    status = fields.Str(data_key="status")