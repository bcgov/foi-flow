
from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
from request_api.services.cfrfeeservice import cfrfeeservice
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
            _cfrresponse = self.__createcfrentry(state, requestid, userid)
            if _commentresponse.success == True and _notificationresponse.success == True and _cfrresponse.success == True:
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
        _notificationtype = "State"
        if state == 'Call For Records' and requesttype == "ministryrequest":
            foirequest = notificationservice().getrequest(requestid, requesttype)
            _notificationtype = "Group Members" if foirequest['assignedministryperson'] is None else "State"
        notification = self.__preparenotification(state)
        if state == 'Closed' or state == 'Archived' :
            notificationservice().dismissnotificationsbyrequestid(requestid, requesttype)
        response = notificationservice().createnotification({"message" : notification}, requestid, requesttype, "State", userid)
        if _notificationtype == "Group Members":
            notification = self.__preparegroupmembernotification(state)
            groupmemberresponse = notificationservice().createnotification({"message" : notification}, requestid, requesttype, _notificationtype, userid)
            if response.success == True and groupmemberresponse.success == True :
                return DefaultMethodResult(True,'Notification added',requestid)
            else:   
                return DefaultMethodResult(False,'Unable to add notification',requestid)
        if response.success == True:
            return DefaultMethodResult(True,'Notification added',requestid)
        return  DefaultMethodResult(True,'No change',requestid)
            

    def __preparenotification(self, state):
        return self.__notificationmessage(state)

    def __preparegroupmembernotification(self, state):
        return self.__groupmembernotificationmessage(state)

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

    def __createcfrentry(self, state, ministryrequestid, userid):
        cfrfee = cfrfeeservice().getcfrfee(ministryrequestid)
        print("cfrfee == ", cfrfee)
        print("cfrfee['cfrfeestatusid'] == ", cfrfee['cfrfeestatusid'])
        if (state == "Fee Estimate" and cfrfee['cfrfeestatusid'] in (None, '')):
            return cfrfeeservice().sanctioncfrfee(ministryrequestid, {"status": "review"}, userid)
        else:
            return DefaultMethodResult(True,'No action needed',ministryrequestid)

    def __groupmembernotificationmessage(self, state):
        return  'New request is in '+state  
            
