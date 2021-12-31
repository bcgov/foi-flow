
from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
import json
from request_api.models.default_method_result import DefaultMethodResult

class assignmentevent:
    """ FOI Event management service

    """
    def createassignmentevent(self, requestid, requesttype, userid):
        ischanged = self.__haschanged(requestid, requesttype)
        if ischanged == True:
            notificationresponse = self.__createnotification(requestid, requesttype, userid)
            if notificationresponse.success == True:
                return DefaultMethodResult(True,'Notification posted',requestid)
            else:   
                return DefaultMethodResult(False,'unable to post notification',requestid)
        return  DefaultMethodResult(True,'No change',requestid)

    def __createnotification(self, requestid, requesttype, userid):
        notification = self.__preparenotification()
        return notificationservice().createnotification(notification, requestid, requesttype, "Assignment", userid)

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
            
