
from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.auth import auth, AuthHelper
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
import json
from request_api.models.default_method_result import DefaultMethodResult

class stateevent:
    """ FOI Event management service

    """
    def createstatetransitionevent(self, requestid, requesttype):
        state = self.__haschanged(requestid, requesttype)
        if state is not None:
            _commentresponse = self.__createcomment(requestid, state, requesttype)
            if _commentresponse.success == True:
                return DefaultMethodResult(True,'Comment posted',requestid)
            else:   
                return DefaultMethodResult(False,'unable to post comment',requestid)
        return  DefaultMethodResult(True,'No change',requestid)
            
    def __haschanged(self, requestid, requesttype):
        if requesttype == "rawrequest":
            states =  FOIRawRequest.getstatenavigation(requestid)
        else:
            states = FOIMinistryRequest.getstatenavigation(requestid)
        if len(states) == 2:
            newstate = states[0]
            oldstate = states[1]
            if newstate != oldstate:
                return newstate
        return None 
    
    def __createcomment(self, requestid, state, requesttype):
        comment = self.__preparecomment(requestid, state, requesttype)
        if requesttype == "ministryrequest":
            return commentservice().createministryrequestcomment(comment, AuthHelper.getuserid(), 2)
        else:
            return commentservice().createrawrequestcomment(comment, AuthHelper.getuserid(),2)

    def __preparecomment(self, requestid, state,requesttype):
        comment = {"comment": self.__commentmessage(state)}
        if requesttype == "ministryrequest":
            comment['ministryrequestid']= requestid
        else:
            comment['requestid']=requestid
        return comment

    def __formatstate(self, state):
        return "Open" if state == "Archived" else state

    def __commentmessage(self, state):
        return  AuthHelper.getusername()+' changed the state of the request to '+self.__formatstate(state)

        
            
