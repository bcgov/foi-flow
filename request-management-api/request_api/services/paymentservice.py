
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestPayments import FOIRequestPayment
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
import json
from dateutil.parser import parse
import datetime 

from dateutil import parser
from dateutil import tz
from pytz import timezone
import pytz
import maya


class paymentservice:
    """ FOI payment management service
    Supports creation, update and delete of payment
    """
    
    def createpayment(self, requestid, ministryrequestid, data):
        #ersion, foirequestid, ministryrequestid, ministryrequestversion, data, userid
        payment = FOIRequestPayment()
        ministryversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        payment.foirequestid = requestid
        payment.ministryrequestid = ministryrequestid
        payment.ministryrequestversion = ministryversion
        payment.paymenturl = data['paymenturl']
        payment.version = 1
        payment.createdby = 'System'
        _payment = FOIRequestPayment.getpayment(requestid, ministryrequestid)
        if _payment is not None and _payment != {}:
            payment.version = _payment["version"] + 1
            payment.paymentid = _payment["paymentid"]
            
        return FOIRequestPayment.savepayment(payment) 

    def getpayment(self, requestid, ministryrequestid):
        return FOIRequestPayment.getpayment(requestid, ministryrequestid) 