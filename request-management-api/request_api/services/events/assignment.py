
from cmath import asin
from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
import json
from request_api.models.default_method_result import DefaultMethodResult
from request_api.utils.enums import CommentType

class assignmentevent:
    """ FOI Event management service

    """
    def createassignmentevent(self, requestid, requesttype, userid, isministryuser,assigneename,username):
        ischanged = self.__haschanged(requestid, requesttype)        
        commentrespose = self.__createcomment(assigneename,username,requestid,userid,requesttype)        
        if ischanged == True:
            notificationresponse = self.__createnotification(requestid, requesttype, userid, isministryuser)          
            
            if notificationresponse.success == True and commentrespose.success == True:
                return DefaultMethodResult(True,'Assignment Notification, Comment has been created',requestid)
            else:   
                return DefaultMethodResult(False,'unable to create notification and/or comment for assignment',requestid)            

        return  DefaultMethodResult(True,'No change',requestid)

    def __createnotification(self, requestid, requesttype, userid, isministryuser):
        notification = self.__preparenotification()
        return notificationservice().createnotification({"message" : notification}, requestid, requesttype, self.__assignmenttype(isministryuser), userid)

    def __preparenotification(self):
        return self.__notificationmessage()
            
    def __haschanged(self, requestid, requesttype):
        assignments = self.__getassignments(requestid, requesttype)
        if len(assignments) ==1 and self.__isnoneorblank(assignments[0]) == False:
            return True
        if len(assignments) == 2 and \
            ((assignments[0]['assignedto'] != assignments[1]['assignedto'] and self.__isnoneorblank(assignments[0]['assignedto']) == False) \
            or (requesttype == "ministryrequest" and \
                assignments[0]['assignedministryperson'] != assignments[1]['assignedministryperson'] \
                    and self.__isnoneorblank(assignments[0]['assignedministryperson']) == False)):
            return True
        return False
    
    def __isnoneorblank(self, value):
        if value is not None and value != '':
            return False
        return True
    def __getassignments(self, requestid, requesttype):
        if requesttype == "ministryrequest":
            return FOIMinistryRequest.getassignmenttransition(requestid)
        else:
            return FOIRawRequest.getassignmenttransition(requestid)

    def __notificationmessage(self):
        return  'New Request Assigned to You.'        
            
    def __assignmenttype(self, isministryuser):
        return 'Ministry Assignment' if isministryuser == True else 'IAO Assignment'

    def __createcomment(self, assigneename, username,requestid,userid,requesttype):
        if(assigneename !=''):
            _commentmessage ='{0} assigned this request to {1}'.format(username,assigneename)
            if requesttype == "ministryrequest":                
                comment = {"ministryrequestid": requestid, "comment": _commentmessage}                    
                return commentservice().createministryrequestcomment(comment, userid, CommentType.SystemGenerated.value)
            else:
                comment = {"requestid": requestid, "comment": _commentmessage}                    
                return commentservice().createrawrequestcomment(comment, userid, CommentType.SystemGenerated.value)    
        else:
            return  DefaultMethodResult(True,'No Assignee',requestid)    
        