
from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of CFR Fee Form operations.

__author__      = "aparna.s@aot-technologies.com"

"""


class FOIFeeDataSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    amountpaid = fields.Float(data_key="amountpaid")
    totalamountdue = fields.Float(data_key="totalamountdue")
    estimatedlocatinghrs = fields.Float(data_key="estimatedlocatinghrs")
    actuallocatinghrs = fields.Float(data_key="actuallocatinghrs")
    estimatedproducinghrs = fields.Float(data_key="estimatedproducinghrs")
    actualproducinghrs = fields.Float(data_key="actualproducinghrs")
    estimatedpreparinghrs = fields.Float(data_key="estimatedpreparinghrs")
    actualpreparinghrs = fields.Float(data_key="actualpreparinghrs")
    estimatedelectronicpages = fields.Int(data_key="estimatedelectronicpages")
    actualelectronicpages = fields.Int(data_key="actualelectronicpages")
    estimatedhardcopypages = fields.Int(data_key="estimatedhardcopypages")
    actualhardcopypages = fields.Int(data_key="actualhardcopypages")


class FOICFRFeeSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    feedata = fields.Nested(FOIFeeDataSchema,allow_none=False)
    overallsuggestions = fields.Str(data_key="overallsuggestions")
    status = fields.Str(data_key="status",required=True)
 
class FOIFeeDataSanctionSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    amountpaid = fields.Float(data_key="amountpaid") 
    
class FOICFRFeeSanctionSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        
    feedata = fields.Nested(FOIFeeDataSanctionSchema,allow_none=False)
    status = fields.Str(data_key="status", required=True)