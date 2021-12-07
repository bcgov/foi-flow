
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
    def createdivisionevent(self, requestid):
        version = FOIMinistryRequest.getversionforrequest(requestid)
        curdivisions = FOIMinistryRequestDivision.getdivisions(requestid, version)
        prevdivisions = FOIMinistryRequestDivision.getdivisions(requestid, version[0]-1)
        divsisionsummary = []        
        divsisionsummary = self.__maintained(curdivisions, prevdivisions) + self.__deleted(curdivisions, prevdivisions) 
        message =  self.__preparemessage(divsisionsummary)
        try:
            self.createcomment(requestid,message['add'])
            self.createcomment(requestid,message['edit'])  
            self.createcomment(requestid,message['delete'])  
            return DefaultMethodResult(True,'Comment posted',requestid)
        except BusinessException as exception:
            return DefaultMethodResult(False,'unable to post comment - '+exception.message,requestid)   
                
        
    @classmethod    
    def createcomment(self, requestid, comment):
        if comment is not None: 
            commentservice().createministryrequestcomment(self.__preparecomment(requestid,comment), AuthHelper.getUserId(), 2)

    
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
    def __preparecomment(self, requestid, message):
        return {"ministryrequestid": requestid, "comment": message}

    @classmethod                
    def __preparemessage(self, divisions):
        if not divisions:
            return None
        add, edit, delete = [], [], []
        for division in divisions:
            if division['event'] == EventType.add.value:
                add.append(division['division']+' stage selected '+ division['stage'])
            elif  division['event'] == EventType.modify.value:
                edit.append(division['division']+' stage selected '+ division['stage'])
            else:
                delete.append(division['division'])
        return {"add": self.__formatmessage(add,EventType.add.value), "edit": self.__formatmessage(edit,EventType.modify.value), "delete": self.__formatmessage(delete,EventType.delete.value)}
    
    @classmethod                
    def __formatmessage(self, divisions, event): 
        if not divisions:
            return None
        else:
            return ",".join(divisions) + self.__messagesuffix(event)
        
    @classmethod                
    def __messagesuffix(self, event): 
        if event == EventType.add.value:
            return ' added' 
        elif event == EventType.modify.value:
            return ' modified' 
        else:
            return ' deleted' 
        
class EventType(Enum):
    add = "add"    
    delete = "delete"
    modify = "modify"
