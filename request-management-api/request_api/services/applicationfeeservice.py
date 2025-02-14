from request_api.models.FOIRequestApplicationFees import FOIRequestApplicationFee
from request_api.models.FOIRequestApplicationFeeReceipts import FOIRequestApplicationFeeReceipt
import maya
from datetime import date
from datetime import datetime
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.Payment import Payment
from request_api.services.events.applicationfeeform import applicationfeeformevent

class applicationfeeservice:
    """ FOI Application Fee Form management service
    Supports creation, update and delete of Application fee form
    """
    def saveapplicationfee(self, rawrequestid, requestid, ministryrequestid, data, userid = 'system', username = 'system'):
        applicationfee = self.__prepareapplicationfee(rawrequestid, data, data.get('applicationfeeid') is not None)
        result = FOIRequestApplicationFee.saveapplicationfee(applicationfee, userid)
        if result.success == True and applicationfeeservice().applicationfeestatushaschanged(rawrequestid):
            data['applicationfeestatus'] = applicationfee.applicationfeestatus
            applicationfeeformevent().createfeestatuschangeevent(rawrequestid, requestid, ministryrequestid, data, userid, username)
        if result.success == True and applicationfeeservice().applicationfeerefundupdated(rawrequestid):
            applicationfeeformevent().createfeerefundevent(rawrequestid, requestid, ministryrequestid, data['refundamount'], userid, username)
        return result
    
    def getapplicationfee(self, rawrequestid, requestid = None, ministryrequestid = None):
        applicationfee = FOIRequestApplicationFee.getapplicationfee(rawrequestid)
        # Check for raw requests (from online form) with IGE status
        payments = Payment.find_application_fee_payments_by_requestid(rawrequestid)
        receipts = FOIRequestApplicationFeeReceipt.getapplicationfeereceipts(applicationfee.get('applicationfeeid'))
        if receipts != []:
            applicationfee['receipts'] = receipts
        if applicationfee == {}:
            request = FOIRawRequest.get_request(rawrequestid)
            for payment in payments:
                applicationfee['applicationfeestatus'] = 'paid'
                applicationfee['amountpaid'] = payment["total"]
                applicationfee['paymentdate'] = payment["completed_on"]
                applicationfee['paymentsource'] = 'creditcardonline'
                applicationfee['orderid'] = payment["order_id"]
                applicationfee['transactionnumber'] = payment["transaction_number"]
                applicationfee['paymentid'] = payment["payment_id"]
            if request != {}:
                isIGE = request.get('requestrawdata', {}).get('contactInfo', {}).get('IGE', {})
                if isIGE:
                    applicationfee['applicationfeestatus'] = 'na-ige'
                    applicationfee['paymentsource'] = 'init'
            if applicationfee != {}:
                self.saveapplicationfee(rawrequestid, requestid, ministryrequestid, applicationfee, 'system')
        if 'paymentsource' in applicationfee and applicationfee['paymentsource'] == 'creditcardonline':
            for payment in payments:
                applicationfee['paymentid'] = payment["payment_id"]
        return self.__formatapplicationfee(applicationfee)
    
    def saveapplicationfeereceipt(self, applicationfeereceipt):
        receipt = FOIRequestApplicationFeeReceipt()
        receipt.createdby = applicationfeereceipt.get('createdby', None)
        receipt.receiptfilename = applicationfeereceipt.get('receiptfilename', None)
        receipt.receiptfilepath = applicationfeereceipt.get('receiptfilepath', None)
        receipt.applicationfeeid = applicationfeereceipt.get('applicationfeeid', None)
        receipt.isactive = applicationfeereceipt.get('isactive', None)
        return FOIRequestApplicationFeeReceipt.saveapplicationfeereceipt(receipt)
    
    def deactivateapplicationfeereceipt(self, applicationfeereceiptid, userid):
        return FOIRequestApplicationFeeReceipt.deactivateapplicationfeereceipt(applicationfeereceiptid, userid)

    def applicationfeestatushaschanged(self, rawrequestid):
        return FOIRequestApplicationFee.applicationfeestatushaschanged(rawrequestid)

    def applicationfeerefundupdated(self, rawrequestid):
        return FOIRequestApplicationFee.applicationfeerefundamountupdated(rawrequestid)

    def __prepareapplicationfee(self, rawrequestid, data={}, getprevious=True):
        applicationfee = FOIRequestApplicationFee()
        lkupapplicationfee = self.getapplicationfee(rawrequestid) if getprevious else None
        _version = 1
        if lkupapplicationfee:
            applicationfee.__dict__.update(lkupapplicationfee)
            _version =  lkupapplicationfee['version'] + 1
            applicationfee.updated_at = None
            applicationfee.updatedby = None
        applicationfee.applicationfeestatus = data.get('applicationfeestatus', None)   
        applicationfee.version = _version
        applicationfee.rawrequestid = rawrequestid
        applicationfee.amountpaid = data.get('amountpaid', None)
        applicationfee.paymentsource = data.get('paymentsource', None)
        applicationfee.paymentdate = data.get('paymentdate', None)
        v = [applicationfee.amountpaid, applicationfee.paymentsource, applicationfee.paymentdate]
        setstatustopaid = False if None in v or '' in v or 0 in v or 'init' in v else True
        # If newly selected date with datepicker (format as string 'YYYY-MM-DD'), add time to create a datetime object
        if setstatustopaid and applicationfee.applicationfeestatus == 'init':
            applicationfee.applicationfeestatus = 'paid'
        if applicationfee.paymentdate and isinstance(applicationfee.paymentdate, str) and len(applicationfee.paymentdate) < 11 and applicationfee.paymentdate.count('-') == 2:
            parseddateobject = applicationfee.paymentdate.split('-')
            datetime_object = datetime(int(parseddateobject[0]), int(parseddateobject[1]), int(parseddateobject[2]), 17, 0, 0)
            applicationfee.paymentdate = datetime_object
        applicationfee.orderid = data.get('orderid', None)
        applicationfee.transactionnumber = data.get('transactionnumber', None)
        applicationfee.refundamount = data.get('refundamount', None)
        if 'refunddate' in data and isinstance(data['refunddate'], str) and len(data['refunddate']) < 11 and data['refunddate'].count('-') == 2:
            parseddateobject = data['refunddate'].split('-')
            datetime_object = datetime(int(parseddateobject[0]), int(parseddateobject[1]), int(parseddateobject[2]), 17, 0, 0)
            applicationfee.refunddate = datetime_object
        applicationfee.reasonforrefund = data.get('reasonforrefund', None)
        return applicationfee

    def __formatapplicationfee(self,applicationfee):
        if applicationfee is not None and applicationfee != {}:
            if applicationfee.get('paymentdate') is not None:
                applicationfee['paymentdate'] = self.__pstformat(applicationfee['paymentdate'])
            if applicationfee.get('refunddate') is not None:
                applicationfee['refunddate'] = self.__pstformat(applicationfee['refunddate'])
            return applicationfee 
        else:
            return {}

    def __pstformat(self, inpdate):
        formateddate = maya.parse(inpdate).datetime(naive=False)
        return formateddate.strftime('%Y-%m-%d %H:%M:%S.%f')