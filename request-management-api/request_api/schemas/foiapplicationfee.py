from marshmallow import EXCLUDE, Schema, fields, validate

"""
This class  consolidates schemas of Application Fee Form operations.
"""


class FOIApplicationFeeDataSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
    applicationfeeid = fields.Int(data_key="applicationfeeid",required=False, allow_none=True)
    applicationfeestatus = fields.String(data_key="applicationfeestatus", allow_none=True)
    amountpaid = fields.Float(data_key="amountpaid", allow_none=True)
    paymentsource = fields.String(data_key="paymentsource", allow_none=True)
    paymentdate = fields.String(data_key="paymentdate", allow_none=True)
    orderid = fields.String(data_key="orderid", allow_none=True)
    transactionnumber = fields.String(data_key="transactionnumber", allow_none=True)
    refundamount = fields.Float(data_key="refundamount", allow_none=True)
    refunddate = fields.String(data_key="refunddate", allow_none=True)
    reasonforrefund = fields.String(data_key="reasonforrefund", allow_none=True)
    receipts = fields.List(fields.Nested('FOIApplicationFeeReceiptDataSchema'), data_key="receipts", allow_none=True)
    receiptfilepath = fields.String(data_key="receiptfilepath", allow_none=True)
    receiptfilename = fields.String(data_key="receiptfilename", allow_none=True)
    created_at = fields.String(data_key="created_at", allow_none=True)
    createdby = fields.String(data_key="createdby", allow_none=True)
    updated_at = fields.String(data_key="updated_at", allow_none=True)
    updatedby = fields.String(data_key="updatedby", allow_none=True)

class FOIApplicationFeeReceiptDataSchema(Schema):
    class Meta:  # pylint: disable=too-few-public-methods
        """Exclude unknown fields in the deserialized output."""
    receiptid = fields.Integer(data_key="receiptid",required=False, allow_none=True)
    created_at = fields.String(data_key="created_at",required=False, allow_none=True)
    applicationfeeid = fields.Int(data_key="applicationfeeid",required=False, allow_none=True)
    createdby = fields.String(data_key="createdby",required=False, allow_none=True)
    receiptfilepath = fields.String(data_key="receiptfilepath", allow_none=True)
    receiptfilename = fields.String(data_key="receiptfilename", allow_none=True)
    updated_at = fields.String(data_key="updated_at",required=False, allow_none=True)
    updatedby = fields.String(data_key="updatedby",required=False, allow_none=True)
    isactive = fields.Boolean(data_key="isactive", allow_none=True)