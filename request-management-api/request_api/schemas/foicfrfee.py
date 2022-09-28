
from marshmallow import EXCLUDE, Schema, fields

"""
This class  consolidates schemas of CFR Fee Form operations.

__author__      = "aparna.s@aot-technologies.com"

"""


class FOIFeeDataSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    amountpaid = fields.Float(data_key="amountpaid")
    estimatedtotaldue = fields.Float(data_key="estimatedtotaldue")
    actualtotaldue = fields.Float(data_key="actualtotaldue")
    balanceremaining = fields.Float(data_key="balanceremaining")
    feewaiveramount = fields.Float(data_key="feewaiveramount")
    refundamount = fields.Float(data_key="refundamount")
    estimatedlocatinghrs = fields.Float(data_key="estimatedlocatinghrs")
    actuallocatinghrs = fields.Float(data_key="actuallocatinghrs")
    estimatedproducinghrs = fields.Float(data_key="estimatedproducinghrs")
    actualproducinghrs = fields.Float(data_key="actualproducinghrs")
    estimatediaopreparinghrs = fields.Float(data_key="estimatediaopreparinghrs")
    estimatedministrypreparinghrs = fields.Float(data_key="estimatedministrypreparinghrs")
    actualiaopreparinghrs = fields.Float(data_key="actualiaopreparinghrs")
    actualministrypreparinghrs = fields.Float(data_key="actualministrypreparinghrs")
    estimatedelectronicpages = fields.Int(data_key="estimatedelectronicpages")
    actualelectronicpages = fields.Int(data_key="actualelectronicpages")
    estimatedhardcopypages = fields.Int(data_key="estimatedhardcopypages")
    actualhardcopypages = fields.Int(data_key="actualhardcopypages")


class FOICFRFeeSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    feedata = fields.Nested(FOIFeeDataSchema,allow_none=False)
    overallsuggestions = fields.Str(data_key="overallsuggestions")
    status = fields.Str(data_key="status")
    cfrfeeid = fields.Int(data_key="cfrfeeid",required=False, allow_none=True)
    reason = fields.Str(data_key="reason")
 
class FOIFeeDataSanctionSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""

    amountpaid = fields.Float(data_key="amountpaid") 
    estimatediaopreparinghrs = fields.Float(data_key="estimatediaopreparinghrs")
    actualiaopreparinghrs = fields.Float(data_key="actualiaopreparinghrs")
    estimatedtotaldue = fields.Float(data_key="estimatedtotaldue")
    actualtotaldue = fields.Float(data_key="actualtotaldue")
    balanceremaining = fields.Float(data_key="balanceremaining")
    feewaiveramount = fields.Float(data_key="feewaiveramount")
    refundamount = fields.Float(data_key="refundamount")
    
class FOICFRFeeSanctionSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
        
    feedata = fields.Nested(FOIFeeDataSanctionSchema,allow_none=False)
    status = fields.Str(data_key="status", required=True)
    reason = fields.Str(data_key="reason")