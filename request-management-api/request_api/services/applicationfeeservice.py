from request_api.models.FOIRequestApplicationFees import FOIRequestApplicationFee
import maya
from datetime import date
from datetime import datetime
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.Payment import Payment

class applicationfeeservice:
    """ FOI Application Fee Form management service
    Supports creation, update and delete of Application fee form
    """
    def saveapplicationfee(self, requestid, data, userid):
        applicationfee = self.__prepareapplicationfee(requestid, data, data.get('applicationfeeid') is not None)
        return FOIRequestApplicationFee.saveapplicationfee(applicationfee, userid)
    
    def getapplicationfee(self, requestid):
        applicationfee = FOIRequestApplicationFee.getapplicationfee(requestid)
        # Check for raw requests (from online form) with IGE status
        payments = Payment.find_application_fee_payments_by_requestid(requestid)
        if applicationfee == {}:
            request = FOIRawRequest.get_request(requestid)
            payments = Payment.find_application_fee_payments_by_requestid(requestid)
            for payment in payments:
                applicationfee['applicationfeestatus'] = 'paid'
                applicationfee['amountpaid'] = payment.total
                applicationfee['paymentdate'] = payment.completed_on
                applicationfee['paymentsource'] = 'creditcardonline'
                applicationfee['orderid'] = payment.order_id
                applicationfee['transactionnumber'] = payment.transaction_number
                applicationfee['paymentid'] = payment.payment_id
            if request != {}:
                isIGE = request.get('requestrawdata', {}).get('contactInfo', {}).get('IGE', {})
                if isIGE:
                    applicationfee['applicationfeestatus'] = 'na-ige'
                    applicationfee['paymentsource'] = 'init'
            if applicationfee != {}:
                self.saveapplicationfee(requestid, applicationfee, 'system')
        return self.__formatapplicationfee(applicationfee)
    
    def __prepareapplicationfee(self, requestid, data={}, getprevious=True):
        applicationfee = FOIRequestApplicationFee()
        lkupapplicationfee = self.getapplicationfee(requestid) if getprevious else None
        _version = 1
        if lkupapplicationfee:
            applicationfee.__dict__.update(lkupapplicationfee)
            _version =  lkupapplicationfee['version'] + 1
            applicationfee.updated_at = None
            applicationfee.updatedby = None
        applicationfee.applicationfeestatus = data.get('applicationfeestatus', None)   
        applicationfee.version = _version
        applicationfee.requestid = requestid
        applicationfee.amountpaid = data.get('amountpaid', None)
        applicationfee.paymentsource = data.get('paymentsource', None)
        applicationfee.paymentdate = data.get('paymentdate', None)
        # If newly selected date with datepicker (format as string 'YYYY-MM-DD'), add time to create a datetime object
        if applicationfee.paymentdate and isinstance(applicationfee.paymentdate, str) and len(applicationfee.paymentdate) < 11 and applicationfee.paymentdate.count('-') == 2:
            parseddateobject = applicationfee.paymentdate.split('-')
            datetime_object = datetime(int(parseddateobject[0]), int(parseddateobject[1]), int(parseddateobject[2]), 17, 0, 0)
            applicationfee.paymentdate = datetime_object
        applicationfee.orderid = data.get('orderid', None)
        applicationfee.transactionnumber = data.get('transactionnumber', None)
        applicationfee.reasonforrefund = data.get('reasonforrefund', None)
        applicationfee.receiptfilename = data.get('receiptfilename', None)
        applicationfee.receiptfilepath = data.get('receiptfilepath', None)
        return applicationfee

    def __formatapplicationfee(self,applicationfee):
        if applicationfee is not None and applicationfee != {}:
            if applicationfee.get('paymentdate') is not None:
                applicationfee['paymentdate'] = self.__pstformat(applicationfee['paymentdate'])
            return applicationfee 
        else:
            return {}

    def __pstformat(self, inpdate):
        formateddate = maya.parse(inpdate).datetime(naive=False)
        return formateddate.strftime('%Y-%m-%d %H:%M:%S.%f')
