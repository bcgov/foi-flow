
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
    @classmethod    
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
                
        
    @classmethod    
    def createcomment(self, requestid, division, stage, event):
        comment = {"ministryrequestid": requestid, "comment": self.__preparemessage(division, stage, event)}
        commentservice().createministryrequestcomment(comment, AuthHelper.getUserId(), 2)

    
    @classmethod    
    def __maintained(self,cdivisions, pdivisions):
        divisions = []
        for cdivision in cdivisions:
            if self.__isdivisionpresent(cdivision['division.name'], pdivisions) == False:
               divisions.append(self.__createdivisionsummary(cdivision, EventType.add.value)) 
            else:
                if self.__isstagechanged(cdivision['division.name'], cdivision['stage.name'], pdivisions) == True :
                   divisions.append(self.__createdivisionsummary(cdivision, EventType.modify.value))                      
        return divisions            
    
    @classmethod    
    def __deleted(self,cdivisions, pdivisions):
        divisions = []
        for pdivision in pdivisions:
            if self.__isdivisionpresent(pdivision['division.name'], cdivisions) == False:      
                divisions.append(self.__createdivisionsummary(pdivision, EventType.delete.value))   
        return divisions      
    
    @classmethod    
    def __isdivisionpresent(self, divisionid, divisionlist):
        for division in divisionlist:
            if division['division.name'] == divisionid:
                return True
        return False
    
    @classmethod   
    def __isstagechanged(self, divisionid, stageid, divisionlist):
        for division in divisionlist:
            if division['division.name'] == divisionid and division['stage.name'] != stageid:
                return True
        return False
                               
    @classmethod    
    def __createdivisionsummary(self, division, event):
        return {'division': division['division.name'], 'stage': division['stage.name'], 'event': event}
        

    @classmethod                
    def __preparemessage(self, division, stage, event): 
        if event == EventType.modify.value:
            return '<i>'+division+'</i>'+' division has been updated to stage '+ '<i>'+stage+'</i>' 
        elif event == EventType.add.value:
             return '<i>'+division+'</i>'+' division with stage '+ '<i>'+stage+'</i>' +' has been added'  
        else:
             return '<i>'+division+'</i>'+' division has been removed with stage '+ '<i>'+stage+'</i>' 
        
       
class EventType(Enum):
    add = "add"    
    delete = "delete"
    modify = "modify"
