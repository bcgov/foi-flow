
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
    def createemailevent(self, requestid, requesttype, stage, reason):
        try: 
            self.__createcomment(requestid, requesttype, stage, reason)
        except BusinessException as ex:            
            logging.exception(ex)
            return DefaultMethodResult(False,'Comment notifications failed',requestid)     

    def __createcomment(self, requestid, requesttype, stage, reason):
        comment = self.__preparecomment(requestid, requesttype, stage, reason)
        if requesttype == "ministryrequest":
            return commentservice().createministryrequestcomment(comment, self.__defaultuserid(), 2)
        else:
            logging.info("Unsupported requesttype")
            
    def __preparecomment(self, requestid, requesttype, stage, reason):
        comment = {"comment": self.__commentmessage(stage, reason)}
        if requesttype == "ministryrequest":
            comment['ministryrequestid']= requestid
        else:
            comment['requestid']=requestid
        return comment

    def __commentmessage(self, stage, reason):
        return  stage+' correspondence failed to send to applicant due to reason '+ reason + '. - see attachment log for details'
    
    def __defaultuserid(self):
        return "System"