
from os import stat
from re import VERBOSE
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.services.commentservice import commentservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
import json
from request_api.models.default_method_result import DefaultMethodResult
from enum import Enum
from request_api.exceptions import BusinessException
from dateutil.parser import parse
from request_api.utils.enums import CommentType

class divisionevent:
    """ FOI Event management service

    """
    def createdivisionevent(self, requestid, requesttype, userid):
        if requesttype != "ministryrequest":
            return DefaultMethodResult(True,'No division required',requestid)
        version = FOIMinistryRequest.getversionforrequest(requestid)
        curdivisions = FOIMinistryRequestDivision.getdivisions(requestid, version)
        prevdivisions = FOIMinistryRequestDivision.getdivisions(requestid, version[0]-1)
        divisionsummary = self.__maintained(curdivisions, prevdivisions) + self.__deleted(curdivisions, prevdivisions)
        if divisionsummary is None or (divisionsummary and len(divisionsummary) <1):
            return  DefaultMethodResult(True,'No change',requestid)
        try:
            for division in divisionsummary:  
                self.createcomment(requestid, division, userid)
            return DefaultMethodResult(True,'Comment posted',requestid)
        except BusinessException as exception:
            return DefaultMethodResult(False,'unable to post comment - '+exception.message,requestid)   
                
        
    def createcomment(self, requestid, division, userid):
        comment = {"ministryrequestid": requestid, "comment": self.__preparemessage(division)}
        print('Comment type is {0}'.format(CommentType.DivisionStages.value))
        commentservice().createministryrequestcomment(comment, userid, CommentType.DivisionStages.value)

    
    def __maintained(self,cdivisions, pdivisions):
        divisions = []
        for cdivision in cdivisions:
            if self.__isdivisionpresent(self.__getdivisioname(cdivision), pdivisions) == False:
               divisions.append(self.__createdivisionsummary(cdivision, EventType.add.value)) 
            else:
                if self.__isstagechanged(self.__getdivisioname(cdivision), self.__getstagename(cdivision), pdivisions) == True or self.__isdivisionduedatechanged(self.__getdivisioname(cdivision), self.__getdivisionduedate(cdivision), pdivisions) or self.__iseapprovalchanged(self.__getdivisioname(cdivision), self.__geteaproval(cdivision), pdivisions) or self.__isdivisionreceiveddatechanged(self.__getdivisioname(cdivision), self.__getdivisionreceiveddate(cdivision), pdivisions) :
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

    def __isdivisionduedatechanged(self, divisionid, cdivisionduedate, divisionlist):
        for division in divisionlist:
            if self.__getdivisioname(division) == divisionid and self.__getdivisionduedate(division) != cdivisionduedate:
                return True
        return False

    def __iseapprovalchanged(self, divisionid, ceapproval, divisionlist):
        for division in divisionlist:
            if self.__getdivisioname(division) == divisionid and self.__geteaproval(division) != ceapproval:
                return True
        return False
    
    def __isdivisionreceiveddatechanged(self, divisionid, cdivisionreceiveddate, divisionlist):
        for division in divisionlist:
            if self.__getdivisioname(division) == divisionid and self.__getdivisionreceiveddate(division) != cdivisionreceiveddate:
                return True
        return False

    def __createdivisionsummary(self, division, event):
        return {'division': self.__getdivisioname(division), 
        'stage': self.__getstagename(division), 
        'divisionduedate':self.__getdivisionduedate(division), 
        'eapproval': self.__geteaproval(division),
        'divisionreceiveddate': self.__getdivisionreceiveddate(division),
        'event': event}
        
    def __getdivisioname(self, dataschema):
        return dataschema['division.name']

    def __getstagename(self, dataschema):
        return dataschema['stage.name']
    
    def __getdivisionduedate(self, dataschema):
        return parse(dataschema['divisionduedate']).strftime(self.__genericdateformat()) if dataschema['divisionduedate'] is not None else None
    
    def __geteaproval(self, dataschema):
        return dataschema['eapproval']

    def __getdivisionreceiveddate(self, dataschema):
        return parse(dataschema['divisionreceiveddate']).strftime(self.__genericdateformat()) if dataschema['divisionreceiveddate'] is not None else None

    def __preparemessage(self, division):
        message = ""
        if division['eapproval'] is not None:
            message = ' E-App/Other reference Number: ' + division['eapproval']
        if division['divisionduedate'] is not None:
            message += ' Due on ' + division['divisionduedate']
        if division['divisionreceiveddate'] is not None:
            message += ' Received on ' + division['divisionreceiveddate']

        if division['event'] == EventType.modify.value:
            return self.__formatmessage(division['division'])+' division has been updated to stage '+ self.__formatmessage(division['stage']) + message 
        elif division['event'] == EventType.add.value:
            return self.__formatmessage(division['division'])+' division has been added with stage '+ self.__formatmessage(division['stage']) + message
        else:
            return self.__formatmessage(division['division'])+' division with stage '+ self.__formatmessage(division['stage']) + message + ' has been removed'  
             
        
    def __formatmessage(self, data):
        return '<i>'+data+'</i>'    
    def __genericdateformat(self):
        return '%Y-%m-%d'
class EventType(Enum):
    add = "add"    
    delete = "delete"
    modify = "modify"
