
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
    @classmethod    
    def createstatetransitionevent(self, requestid, requesttype):
        state = self.__haschanged(requestid, requesttype)
        if state is not None:
            _commentresponse = self.__createcomment(requestid, state, requesttype)
            #self.__createnotification(requestid, state)
            if _commentresponse.success == True:
                return DefaultMethodResult(True,'Comment posted',requestid)
            else:   
                return DefaultMethodResult(True,'unable to post comment',requestid)
        
            
    @classmethod                 
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
    
    @classmethod
    def __createcomment(self, requestid, state, requesttype):
        if requesttype == "ministryrequest":
            state = self.getstatusname(state)
        comment = self.__preparecomment(requestid, state,requesttype)
        if requesttype == "ministryrequest":   
            return commentservice().createministryrequestcomment(comment, AuthHelper.getUserId(), 2)
        else:
            return commentservice().createrawrequestcomment(comment, AuthHelper.getUserId(),2)            
        
    @classmethod    
    def __createnotification(self, requestid, state):
        self.__preparenotification(state)
         
    @classmethod         
    def __preparecomment(self, requestid, state,requesttype):
        comment = {"comment": self.__commentmessage(state)}
        if requesttype == "ministryrequest":
            comment['ministryrequestid']= requestid 
        else:
            comment['requestid']=requestid
        return comment
    
    @classmethod    
    def __preparenotification(self, state):
        return self.__notificationmessage(state)
    
    @classmethod
    def getstatusname(self,requeststatusid):
        allstatus = FOIRequestStatus().getrequeststatuses()
        for status in allstatus:
            if status["requeststatusid"] == requeststatusid:
                return status["name"]
        return None; 
        
    @classmethod            
    def __commentmessage(self, state):
        return  AuthHelper.getUserName()+' changed the state of the request to '+state
    
    @classmethod   
    def __notificationmessage(self, state):
        return  'Moved to '+state+ ' state'
        
            
