
from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
import json
from request_api.models.default_method_result import DefaultMethodResult

class stateevent:
    """ FOI Event management service

    """
    def createstatetransitionevent(self, requestid, requesttype, userid, username):
        state = self.__haschanged(requestid, requesttype)
        if state is not None:
            _commentresponse = self.__createcomment(requestid, state, requesttype, userid, username)
            _notificationresponse = self.__createnotification(requestid, state, requesttype, userid)
            if _commentresponse.success == True and _notificationresponse.success == True :
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
            if newstate != oldstate and newstate != 'Intake in Progress':
                return newstate
        return None 
    
    def __createcomment(self, requestid, state, requesttype, userid, username):
        comment = self.__preparecomment(requestid, state, requesttype, username)
        if requesttype == "ministryrequest":
            return commentservice().createministryrequestcomment(comment, userid, 2)
        else:
            return commentservice().createrawrequestcomment(comment, userid,2)

    def __createnotification(self, requestid, state, requesttype, userid):
        notification = self.__preparenotification(state)
        if state == 'Closed' or state == 'Archived' :
            notificationservice().dismissnotificationsbyrequestid(requestid, requesttype)
        return notificationservice().createnotification({"message" : notification}, requestid, requesttype, "State", userid)

    def __preparenotification(self, state):
        return self.__notificationmessage(state)

    def __preparecomment(self, requestid, state,requesttype, username):
        comment = {"comment": self.__commentmessage(state, username)}
        if requesttype == "ministryrequest":
            comment['ministryrequestid']= requestid
        else:
            comment['requestid']=requestid
        return comment

    def __formatstate(self, state):
        return "Open" if state == "Archived" else state

    def __commentmessage(self, state, username):
        return  username+' changed the state of the request to '+self.__formatstate(state)

    def __notificationmessage(self, state):
        return  'Moved to '+self.__formatstate(state)+ ' State'        
            
