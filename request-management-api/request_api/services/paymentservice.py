
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestPayments import FOIRequestPayment
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.services.document_generation_service import DocumentGenerationService
from request_api.services.external.storageservice import storageservice
from request_api.models.default_method_result import DefaultMethodResult

import json
from dateutil.parser import parse
import datetime 

from dateutil import parser
from dateutil import tz
from pytz import timezone
import pytz
import maya
import logging

class paymentservice:
    """ FOI payment management service
    Supports creation, update and delete of payment
    """
    
    def createpayment(self, requestid, ministryrequestid, data):
        payment = FOIRequestPayment()
        ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        payment.foirequestid = requestid
        payment.ministryrequestid = ministryrequestid
        payment.ministryrequestversion = ministryversion
        payment.paymenturl = data['paymenturl']
        payment.paymentexpirydate = data['paymentexpirydate']
        payment.version = 1
        payment.createdby = 'System'
        _payment = FOIRequestPayment.getpayment(requestid, ministryrequestid)
        if _payment is not None and _payment != {}:
            payment.version = _payment["version"] + 1
            payment.paymentid = _payment["paymentid"]
            
        return FOIRequestPayment.savepayment(payment) 

    def getpayment(self, requestid, ministryrequestid):
        return FOIRequestPayment.getpayment(requestid, ministryrequestid) 

    def createpaymentreceipt(self, request_id, ministry_request_id, data, parsed_args):
        try:
            balancedue = float(data['cfrfee']['feedata']["balanceDue"])
            basepath = 'request_api/receipt_templates/'
            receiptname = 'cfr_fee_payment_receipt'
            if balancedue > 0:
                receipt_template_path= basepath + self.getreceiptename('HALFPAYMENT') +".docx"
                receiptname = self.getreceiptename('HALFPAYMENT')
            else:
                receipt_template_path= basepath + self.getreceiptename('FULLPAYMENT')+".docx"
                receiptname = self.getreceiptename('FULLPAYMENT')
            data['waivedAmount'] = data['cfrfee']['feedata']['estimatedlocatinghrs'] * 30 if data['cfrfee']['feedata']['estimatedlocatinghrs'] < 3 else 90
            data.update({'paymentInfo': {
                'paymentDate': parsed_args.get('trnDate'),
                'orderId': parsed_args.get('trnOrderId'),
                'transactionId': parsed_args.get('pbcTxnNumber'),
                'cardType': parsed_args.get('cardType')
            }})
            document_service : DocumentGenerationService = DocumentGenerationService(receiptname)
            receipt = document_service.generate_receipt(data,receipt_template_path)
            document_service.upload_receipt('fee_estimate_payment_receipt.pdf', receipt.content, ministry_request_id, data['bcgovcode'], data['idNumber'])
            return DefaultMethodResult(True,'Payment Receipt created',ministry_request_id)
        except Exception as ex:   
            logging.exception(ex)         
            return DefaultMethodResult(False,'Unable to create Payment Receipt',ministry_request_id)

    def getreceiptename(self, key):
        if key == "HALFPAYMENT":
            return "cfr_fee_payment_receipt_half"
        elif key == "FULLPAYMENT":
            return "cfr_fee_payment_receipt_full"
        else:
            logging.info("Unknown key")
            return None
