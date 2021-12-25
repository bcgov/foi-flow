
from os import stat
from re import VERBOSE
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.services.commentservice import commentservice
from request_api.auth import auth, AuthHelper
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
import json
from request_api.models.default_method_result import DefaultMethodResult
from enum import Enum
from request_api.exceptions import BusinessException

class divisionevent:
    """ FOI Event management service

    """
    def createdivisionevent(self, requestid, requesttype):
        if requesttype != "ministryrequest":
            return DefaultMethodResult(True,'No division required',requestid)
        version = FOIMinistryRequest.getversionforrequest(requestid)
        curdivisions = FOIMinistryRequestDivision.getdivisions(requestid, version)
        prevdivisions = FOIMinistryRequestDivision.getdivisions(requestid, version[0]-1)
        divsisionsummary = self.__maintained(curdivisions, prevdivisions) + self.__deleted(curdivisions, prevdivisions) 
        
        try:
            for division in divsisionsummary:  
                self.createcomment(requestid, division['division'], division['stage'], division['event'])
            return DefaultMethodResult(True,'Comment posted',requestid)
        except BusinessException as exception:
            return DefaultMethodResult(False,'unable to post comment - '+exception.message,requestid)   
                
        
    def createcomment(self, requestid, division, stage, event):
        comment = {"ministryrequestid": requestid, "comment": self.__preparemessage(division, stage, event)}
        commentservice().createministryrequestcomment(comment, AuthHelper.getuserid(), 2)

    
    def __maintained(self,cdivisions, pdivisions):
        divisions = []
        for cdivision in cdivisions:
            if self.__isdivisionpresent(self.__getdivisioname(cdivision), pdivisions) == False:
               divisions.append(self.__createdivisionsummary(cdivision, EventType.add.value)) 
            else:
                if self.__isstagechanged(self.__getdivisioname(cdivision), self.__getstagename(cdivision), pdivisions) == True :
                   divisions.append(self.__createdivisionsummary(cdivision, EventType.modify.value))                      
        return divisions            
    
    def __deleted(self,cdivisions, pdivisions):
        divisions = []
        for pdivision in pdivisions:
            if self.__isdivisionpresent(self.__getdivisioname(pdivision), cdivisions) == False:      
                divisions.append(self.__createdivisionsummary(pdivision, EventType.delete.value))   
        return divisions      
    
    def __isdivisionpresent(self, divisionid, divisionlist):
        for division in divisionlist:
            if self.__getdivisioname(division) == divisionid:
                return True
        return False
    
    def __isstagechanged(self, divisionid, stageid, divisionlist):
        for division in divisionlist:
            if self.__getdivisioname(division) == divisionid and self.__getstagename(division) != stageid:
                return True
        return False
                               
    def __createdivisionsummary(self, division, event):
        return {'division': self.__getdivisioname(division), 'stage': self.__getstagename(division), 'event': event}
        
    def __getdivisioname(self, dataschema):
        return dataschema['division.name']

    def __getstagename(self, dataschema):
        return dataschema['stage.name']    

    def __preparemessage(self, division, stage, event): 
        if event == EventType.modify.value:
            return self.__formatmessage(division)+' division has been updated to stage '+ self.__formatmessage(stage)
        elif event == EventType.add.value:
            return self.__formatmessage(division)+' division has been added with stage '+ self.__formatmessage(stage) 
        else:
            return self.__formatmessage(division)+' division with stage '+ self.__formatmessage(stage) +' has been removed'  
             
        
    def __formatmessage(self, data):
        return '<i>'+data+'</i>'    

class EventType(Enum):
    add = "add"    
    delete = "delete"
    modify = "modify"
