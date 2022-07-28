
from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
from request_api.exceptions import BusinessException
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
import json
from request_api.models.default_method_result import DefaultMethodResult
import logging

class emailevent:
    """ FOI Event management service
    """
    def createemailevent(self, requestid, requesttype, stage, reason, userid):
        try: 
            _commentresponse = self.__createcomment(requestid, requesttype, stage, reason, userid)
            _notificationresponse = self.__createnotification(requestid, requesttype, stage, userid)
            if _commentresponse.success == True and _notificationresponse.success == True and _notificationresponse.success == True:
                return DefaultMethodResult(True,'Email Failure Notification posted',requestid)
            else:   
                return DefaultMethodResult(False,'Email Failure Notification - failed',requestid)
        except BusinessException as ex:            
            logging.exception(ex)
            return DefaultMethodResult(False,'Email Failure Notification - failed',requestid)     

    def __createcomment(self, requestid, requesttype, stage, reason, userid):
        comment = self.__preparecomment(requestid, requesttype, stage, reason)
        if requesttype == "ministryrequest":
            return commentservice().createministryrequestcomment(comment, userid, 2)
        else:
            logging.info("Unsupported requesttype")
    
    def __createnotification(self, requestid, requesttype, stage, userid):
        notification = self.__preparenotification(stage)
        return notificationservice().createnotification({"message" : notification}, requestid, requesttype, "Email Failure",  "System")

    def __preparenotification(self, stage):
        return self.__notificationmessage(stage)
            
    def __preparecomment(self, requestid, requesttype, stage, reason):
        comment = {"comment": self.__commentmessage(stage, reason)}
        if requesttype == "ministryrequest":
            comment['ministryrequestid']= requestid
        else:
            comment['requestid']=requestid
        return comment

    def __commentmessage(self, stage, reason):
        return  stage+' correspondence failed to send to applicant due to reason: "<i>'+reason+'"</i>. - see attachment log for details.'
    
    def __notificationmessage(self, stage):
        return  stage+' correspondence failed to send to applicant. - see attachment log for details.' 
    
    def __defaultuserid(self):
        return "System"