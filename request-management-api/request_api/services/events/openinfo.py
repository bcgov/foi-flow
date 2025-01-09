
from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
import json
from request_api.models.default_method_result import DefaultMethodResult

class openinfoevent:
    """ FOI Event management service

    """
    def createopeninfoevent(self, ministryrequestid, requestid, userid, username):
        _commentresponse = self.__createcomment(requestid, userid, username)
        _notificationresponse = self.__createnotification(requestid, userid)
        if _commentresponse.success == True and _notificationresponse.success == True:
            return DefaultMethodResult(True,'Comment posted',requestid)
        else:
            return DefaultMethodResult(False,'unable to post comment',requestid)

    def __createcomment(self, requestid, userid, username):
        comment = self.__preparecomment(requestid, userid, username)
        return commentservice().createministryrequestcomment(comment, userid, 2)

    def __createnotification(self, requestid, userid):
        notification = self.__preparenotification(requestid)
        response = notificationservice().createnotification({"message" : notification}, requestid, "ministryrequest", "fill in here", userid)
        if response.success == True:
            return DefaultMethodResult(True,'Notification added',requestid)
        return  DefaultMethodResult(True,'Unable to post notification',requestid)

    def __preparenotification(self, requestid):
        return self.__notificationmessage(requestid)

    def __preparecomment(self, requestid, userid, username):
        comment = "fill in here"
        return comment

    def __notificationmessage(self, requestid):
        return "fill in here"
