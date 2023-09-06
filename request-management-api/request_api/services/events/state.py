
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
    def createstatetransitionevent(self, requestid, requesttype, userid, username, ministryrequestschema):
        state = self.__haschanged(requestid, requesttype)
        if state is not None:
            _commentresponse = self.__createcommentwrapper(requestid, state, requesttype, userid, username, ministryrequestschema)
            _notificationresponse = self.__createnotification(requestid, state, requesttype, userid, ministryrequestschema)
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
    
    def __createcommentwrapper(self, requestid, state, requesttype, userid, username, ministryrequestschema):
        if state == 'Archived':
            _openedministries = FOIMinistryRequest.getministriesopenedbyuid(requestid)
            for ministry in _openedministries:
                response=self.__createcomment(ministry["ministryrequestid"], state, 'ministryrequest', userid, username, ministryrequestschema)
        else:
            response=self.__createcomment(requestid, state, requesttype, userid, username, ministryrequestschema)
        return response
        
    
    def __createcomment(self, requestid, state, requesttype, userid, username, ministryrequestschema):
        comment = self.__preparecomment(requestid, state, requesttype, username, ministryrequestschema)
        if requesttype == "ministryrequest":
            return commentservice().createministryrequestcomment(comment, userid, 2)
        else:
            return commentservice().createrawrequestcomment(comment, userid,2)


    def __createnotification(self, requestid, state, requesttype, userid, ministryrequestschema):
        _notificationtype = "State"
        if state == 'Call For Records' and requesttype == "ministryrequest":
            foirequest = notificationservice().getrequest(requestid, requesttype)
            _notificationtype = "Group Members" if foirequest['assignedministryperson'] is None else "State"
        notification = self.__preparenotification(state, ministryrequestschema)
        if state == 'Closed' or state == 'Archived' :
            notificationservice().dismissnotificationsbyrequestid(requestid, requesttype)
        if state == 'Archived':
            _openedministries = FOIMinistryRequest.getministriesopenedbyuid(requestid)
            for ministry in _openedministries:
                response = notificationservice().createnotification({"message" : notification}, ministry["ministryrequestid"], 'ministryrequest', "State", userid)
        else:
            response = notificationservice().createnotification({"message" : notification}, requestid, requesttype, "State", userid)
        if _notificationtype == "Group Members":
            notification = self.__preparegroupmembernotification(state, requestid)
            groupmemberresponse = notificationservice().createnotification({"message" : notification}, requestid, requesttype, _notificationtype, userid)
            if response.success == True and groupmemberresponse.success == True :
                return DefaultMethodResult(True,'Notification added',requestid)
            else:   
                return DefaultMethodResult(False,'Unable to add notification',requestid)
        if response.success == True:
            return DefaultMethodResult(True,'Notification added',requestid)
        return  DefaultMethodResult(True,'No change',requestid)
            
    def __preparenotification(self, state, ministryrequestschema):
        return self.__notificationmessage(state, ministryrequestschema)

    def __preparegroupmembernotification(self, state, requestid):
        if state == 'Call For Records':
            return self.__notificationcfrmessage(requestid)
        return self.__groupmembernotificationmessage(state)

    def __preparecomment(self, requestid, state,requesttype, username, ministryrequestschema):
        comment = {"comment": self.__commentmessage(state, username, ministryrequestschema)}
        if requesttype == "ministryrequest":
            comment['ministryrequestid']= requestid
        else:
            comment['requestid']=requestid
        return comment

    def __formatstate(self, state):
        return "Open" if state == "Archived" else state

    def __commentmessage(self, state, username, ministryrequestschema):
        if state == "Response":
            return f"{username} changed the state of the request to {self.__formatstate(state)}. Approved by {ministryrequestschema['ministrysignoffapproval']['approvername']}, {ministryrequestschema['ministrysignoffapproval']['approvertitle']} on {ministryrequestschema['ministrysignoffapproval']['approveddate']}"
        return  username+' changed the state of the request to '+self.__formatstate(state)

    def __notificationmessage(self, state, ministryrequestschema):
        if state == "Response":
            return f"Moved to {self.__formatstate(state)} State. Approved by {ministryrequestschema['ministrysignoffapproval']['approvername']}, {ministryrequestschema['ministrysignoffapproval']['approvertitle']} on {ministryrequestschema['ministrysignoffapproval']['approveddate']}" 
        return  'Moved to '+self.__formatstate(state)+ ' State'        

    def __notificationcfrmessage(self, requestid):
        metadata = FOIMinistryRequest.getmetadata(requestid)
        return "New "+metadata['requesttype'].capitalize()+" request is in Call For Records"

    def __createcfrentry(self, state, ministryrequestid, userid):
        cfrfee = cfrfeeservice().getcfrfee(ministryrequestid)
        if (state == "Fee Estimate" and cfrfee['cfrfeestatusid'] in (None, '')):
            return cfrfeeservice().sanctioncfrfee(ministryrequestid, {"status": "review"}, userid)
        else:
            return DefaultMethodResult(True,'No action needed',ministryrequestid)

    def __groupmembernotificationmessage(self, state):
        return  'New request is in '+state  
    
    def create_signoff_approval_event(self, requestid, userid, username, approval):
        print("[user] has changed the state of the request to response. Approved by [approver name/title] on [date approved]")
        ministryrequest = FOIMinistryRequest().getrequest(requestid)
        if ministryrequest.requeststatusid == 10:
            comment = f"{username} has changed the state of the request to response. Approved by [approver name/title] on [date approved]"
            commentservice().createministryrequestcomment(comment, userid, 2)
            ## Create Notification
            ## ADD A TRY EXCEPT FINALLY?
        ## find ministry request with id, check if state is 10/ministry signoff if so -> create a comment and create a notification (copy code from createevent here??)
        ## comment will come with custom message and type 2 id, gotta look into what notif is needed.
        ##NEED TO GET THE APPROVAL OBJ HERE SOMEHOW