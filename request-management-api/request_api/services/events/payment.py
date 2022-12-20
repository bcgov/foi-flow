
from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
import json
from request_api.models.default_method_result import DefaultMethodResult
from enum import Enum
import maya
import os
from dateutil.parser import parse
from pytz import timezone
from request_api.utils.enums import PaymentEventType

class paymentevent:
    """ FOI Event management service

    """
    def createpaymentevent(self, requestid, eventtype):
        _commentresponse = self.__createcomment(requestid, eventtype)
        _notificationresponse = self.__createnotification(requestid, eventtype)
        if _commentresponse.success == True and _notificationresponse.success == True:
            return DefaultMethodResult(True,'Payment notification posted',requestid)
        else:
            return DefaultMethodResult(False,'Unable to post Payment notification',requestid)

    def createpaymentexpiredevent(self, requestid):
        _commentresponse = self.__createcomment(requestid, PaymentEventType.expired.value)
        _notificationresponse = self.__createnotification(requestid, PaymentEventType.expired.value)
        if _commentresponse.success == True and _notificationresponse.success == True:
            return DefaultMethodResult(True,'Payment Expiry notification posted',requestid)
        else:
            return DefaultMethodResult(False,'Unable to post Payment Expiry notification',requestid)

    def __createcomment(self, requestid, eventtype):
        comment = self.__preparecomment(requestid, eventtype)
        return commentservice().createministryrequestcomment(comment, self.__defaultuserid(), 2)

    def __createnotification(self, requestid, eventtype):
        notification = self.__preparenotification(requestid, eventtype)
        return notificationservice().createnotification({"message" : notification}, requestid, "ministryrequest", "Payment", self.__defaultuserid())

    def __preparenotification(self, requestid, eventtype):
        return self.__notificationmessage(requestid, eventtype)

    def __preparecomment(self, requestid, eventtype):
        if eventtype == PaymentEventType.paid.value:
            comment = {"comment": "Applicant has paid required fee. New LDD is " + FOIMinistryRequest.getduedate(requestid).strftime("%m/%d/%Y")}
        elif eventtype == PaymentEventType.expired.value:
            comment = {"comment": "Fees were due to be paid by " + self.gettoday() + ", you may consider closing the request as abandoned."}
        elif eventtype == PaymentEventType.outstandingpaid.value:
            comment = {"comment": "Applicant has paid outstanding fee. Response package can be released."}
        elif eventtype == PaymentEventType.depositpaid.value:
            comment = {"comment": "Applicant has paid deposit."}
        else:
            comment = None
        if comment is not None:
            comment['ministryrequestid']= requestid
        return comment

    def __notificationmessage(self, requestid, eventtype):
        if eventtype == PaymentEventType.paid.value:
            return "Applicant has paid required fee, resume gathering. New LDD is " + FOIMinistryRequest.getduedate(requestid).strftime("%m/%d/%Y")
        elif eventtype == PaymentEventType.expired.value:
            return "Fees were due to be paid by " + self.gettoday() + ", you may consider closing the request as abandoned."
        elif eventtype == PaymentEventType.outstandingpaid.value:
            return "Applicant has paid outstanding fee. Response package can be released."
        elif eventtype == PaymentEventType.depositpaid.value:
            return "Applicant has paid deposit. New LDD is " + FOIMinistryRequest.getduedate(requestid).strftime("%m/%d/%Y")
        else:
            return None

    def __defaultuserid(self):
        return "Online Payment"    

    def gettoday(self):
        now_pst = maya.parse(maya.now()).datetime(to_timezone='America/Vancouver', naive=False)
        return now_pst.strftime('%m/%d/%Y') 
