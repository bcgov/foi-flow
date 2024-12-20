
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestPayments import FOIRequestPayment
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.services.document_generation_service import DocumentGenerationService
from request_api.models.default_method_result import DefaultMethodResult
from request_api.services.applicantcorrespondence.applicantcorrespondencelog import applicantcorrespondenceservice
from request_api.utils.enums import PaymentEventType, StateName

import json
from dateutil.parser import parse
from datetime import datetime
import asyncio

from dateutil import parser
from dateutil import tz
from pytz import timezone
import pytz
import maya
import logging
import re

class paymentservice:
    """ FOI payment management service
    Supports creation, update and delete of payment
    """
    
    def createpayment(self, requestid, ministryrequestid, data, createdby='System'):
        payment = FOIRequestPayment()
        ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        payment.foirequestid = requestid
        payment.ministryrequestid = ministryrequestid
        payment.ministryrequestversion = ministryversion
        payment.paymenturl = data['paymenturl'] if 'paymenturl' in data else None
        payment.paymentexpirydate = data['paymentExpiryDate'] if 'paymentExpiryDate' in data else self.getpaymentexpirydate(requestid, ministryrequestid)
        payment.version = 1
        payment.createdby = createdby
        _payment = FOIRequestPayment.getpayment(requestid, ministryrequestid)
        if _payment is not None and _payment != {}:
            payment.version = _payment["version"] + 1
            payment.paymentid = _payment["paymentid"]            
        return FOIRequestPayment.savepayment(payment)

    def updatepayment(self, paymentid, data, userid):
        return FOIRequestPayment.updatepayment(paymentid, data["paymenturl"], userid)
    
    def createpaymentversion(self, request_id, ministry_request_id, amountpaid):
        payment = self.__createpaymentinstance(request_id, ministry_request_id)
        if payment is not None and payment != {}:            
            payment.paidamount = amountpaid            
        return FOIRequestPayment.savepayment(payment)

    def cancelpayment(self, request_id, ministry_request_id, paymentschema):
        payment = self.__createpaymentinstance(request_id, ministry_request_id)
        if payment is not None and payment != {}:   
            payment.paymenturl = paymentschema['paymenturl']        
            payment.paymentexpirydate = datetime.now().isoformat()  
            payment.createdby = 'System_Cancel'
        return FOIRequestPayment.savepayment(payment)

    def __createpaymentinstance(self, request_id, ministry_request_id):
        _payment = FOIRequestPayment.getpayment(request_id, ministry_request_id)
        ministryversion = FOIMinistryRequest.getversionforrequest(ministry_request_id)
        payment = FOIRequestPayment()
        payment.foirequestid = request_id
        payment.ministryrequestid = ministry_request_id
        payment.ministryrequestversion = ministryversion
        if _payment is not None and _payment != {}:            
            payment.paymenturl = _payment['paymenturl']
            payment.paymentexpirydate = _payment['paymentexpirydate']
            payment.version = _payment['version'] + 1
            payment.createdby = 'System'
            payment.paymentid = _payment["paymentid"]
        return payment


    def getpayment(self, requestid, ministryrequestid):
        return FOIRequestPayment.getpayment(requestid, ministryrequestid)

    def getpaymentexpirydate(self, requestid, ministryrequestid):
        payment = FOIRequestPayment.getpayment(requestid, ministryrequestid)
        paymentexpirydate = payment["paymentexpirydate"] if payment not in (None, {}) else None
        if paymentexpirydate is not None:
            return parse(str(paymentexpirydate)).strftime("%Y-%m-%d")
        return ""

    def createpaymentreceipt(self, request_id, ministry_request_id, data, parsed_args, previously_paid_amount):
        try:
            data['previous_amt_paid'] = '{:.2f}'.format(previously_paid_amount)
            templatename = self.__getlatesttemplatename(ministry_request_id)
            balancedue = float(data['cfrfee']['feedata']["balanceDue"])
            prevstate = data["stateTransition"][1]["status"] if "stateTransition" in data and len(data["stateTransition"])  > 2 else None
            basepath = 'request_api/receipt_templates/'
            receiptname = 'cfr_fee_payment_receipt'
            attachmentcategory = "FEE-ESTIMATE-PAYMENT-RECEIPT"
            filename = f"Fee Estimate Payment Receipt {re.sub(r'[^a-zA-Z0-9]', '', data['cfrfee']['created_at'])}.pdf"
            if balancedue > 0:
                receipt_template_path= basepath + self.getreceiptename('HALFPAYMENT') +".docx"
                receiptname = self.getreceiptename('HALFPAYMENT')
            else:
                receiptname = self.getreceiptename('FULLPAYMENT')
                if prevstate.lower() == "response" or (templatename and templatename == 'PAYOUTSTANDING'):
                    receiptname = self.getreceiptename('PAYOUTSTANDING')
                    attachmentcategory = "OUTSTANDING-PAYMENT-RECEIPT"
                    filename = f"Fee Balance Outstanding Payment Receipt {re.sub(r'[^a-zA-Z0-9]', '', data['cfrfee']['created_at'])}.pdf"
                receipt_template_path= basepath + receiptname + ".docx"
            data['waivedAmount'] = data['cfrfee']['feedata']['estimatedlocatinghrs'] * 30 if data['cfrfee']['feedata']['estimatedlocatinghrs'] < 3 else 90
            data.update({'paymentInfo': {
                'paymentDate': parsed_args.get('trnDate'),
                'orderId': parsed_args.get('trnOrderId'),
                'transactionId': parsed_args.get('pbcTxnNumber'),
                'cardType': parsed_args.get('cardType')
            }})
            document_service : DocumentGenerationService = DocumentGenerationService(receiptname)
            receipt = document_service.generate_receipt(data,receipt_template_path)
            document_service.upload_receipt(filename, receipt.content, ministry_request_id, data['bcgovcode'], data['idNumber'], attachmentcategory)
            return DefaultMethodResult(True,'Payment Receipt created',ministry_request_id)
        except Exception as ex:   
            logging.exception(ex)         
            return DefaultMethodResult(False,'Unable to create Payment Receipt',ministry_request_id)

    def postpayment(self, ministry_request_id, data):
        prevstate = data["stateTransition"][1]["status"] if "stateTransition" in data and len(data["stateTransition"])  > 2 else None
        nextstatename = StateName.callforrecords.value
                
        balancedue = float(data['cfrfee']['feedata']["balanceDue"])
        paymenteventtype = PaymentEventType.paid.value
        if balancedue > 0:
            paymenteventtype = PaymentEventType.depositpaid.value
        if prevstate.lower() == "response":
            nextstatename = StateName.response.value
        templatename = self.__getlatesttemplatename(ministry_request_id)
        #outstanding
        if balancedue == 0 and ((templatename and templatename == 'PAYOUTSTANDING') or prevstate.lower() == "response"):
            paymenteventtype = PaymentEventType.outstandingpaid.value
            nextstatename = StateName.response.value
        return nextstatename, paymenteventtype

    def getreceiptename(self, key):
        if key == "HALFPAYMENT":
            return "cfr_fee_payment_receipt_half"
        elif key == "FULLPAYMENT":
            return "cfr_fee_payment_receipt_full"
        elif key == "PAYOUTSTANDING":
            return "outstanding_fee_payment_receipt"
        else:
            logging.info("Unknown key")
            return None
    
    def __getlatesttemplatename(self, ministryrequestid):
        latestcorrespondence = applicantcorrespondenceservice().getlatestapplicantcorrespondence(ministryrequestid)
        _latesttemplateid = latestcorrespondence['templateid'] if 'templateid' in latestcorrespondence else None
        if _latesttemplateid:
            return applicantcorrespondenceservice().gettemplatebyid(_latesttemplateid).name
        return None
