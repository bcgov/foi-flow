
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestExtensions import FOIRequestExtension
from request_api.services.commentservice import commentservice
from request_api.services.extensionreasonservice import extensionreasonservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
import json
from request_api.models.default_method_result import DefaultMethodResult
from enum import Enum
from request_api.exceptions import BusinessException

class extensionevent:
    """ FOI Event management service

    """
    def createextensionevent(self, requestid, userid, username):        
        version = FOIMinistryRequest.getversionforrequest(requestid)
        approvedextension = FOIRequestExtension().getlatestapprovedextension(requestid, version)
        try:
            if approvedextension and len(approvedextension) != 0:
                extensionreason = extensionreasonservice().getextensionreasonbyid(approvedextension['extensionreasonid'])
                self.createcomment(requestid, userid, username, extensionreason['extensiontype'],  EventType.add.value)
            else:
                return  DefaultMethodResult(True,'No change',requestid)        
        except BusinessException as exception:
            return DefaultMethodResult(False,'unable to post comment - '+exception.message,requestid)        
        
                
        
    def createcomment(self, requestid, division, stage, event, userid):
        comment = {"ministryrequestid": requestid, "comment": self.__preparemessage(division, stage, event)}
        commentservice().createministryrequestcomment(comment, userid, 2)

    
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
