
from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
import json
from request_api.models.default_method_result import DefaultMethodResult

class paymentevent:
    """ FOI Event management service

    """
    def createpaymentevent(self, requestid):
        _commentresponse = self.__createcomment(requestid)
        _notificationresponse = self.__createnotification(requestid)
        if _commentresponse.success == True and _notificationresponse.success == True:
            return DefaultMethodResult(True,'Payment notification posted',requestid)
        else:
            return DefaultMethodResult(False,'Unable to post Payment notification',requestid)

    def __createcomment(self, requestid):
        comment = self.__preparecomment(requestid)
        return commentservice().createministryrequestcomment(comment, self.__defaultuserid(), 2)

    def __createnotification(self, requestid):
        notification = self.__preparenotification(requestid)
        return notificationservice().createnotification({"message" : notification}, requestid, "ministryrequest", "State", self.__defaultuserid())

    def __preparenotification(self, requestid):
        return self.__notificationmessage(requestid)

    def __preparecomment(self, requestid):
        comment = {"comment": "Applicant has paid required fee. New LDD is " + FOIMinistryRequest.getduedate(requestid).strftime("%m/%d/%Y")}
        comment['ministryrequestid']= requestid
        return comment

    def __notificationmessage(self, requestid):
        return "Applicant has paid required fee, resume gathering. New LDD is " + FOIMinistryRequest.getduedate(requestid).strftime("%m/%d/%Y")

    def __defaultuserid(self):
        return "Online Payment"    