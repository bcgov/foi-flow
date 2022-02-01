
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
import dateutil.parser

class extensionevent:
    """ FOI Event management service

    """
    def createextensionevent(self, ministryrequestid, extensionid, userid, username, event):        
        version = FOIRequestExtension.getversionforextension(extensionid)       
        curextension = FOIRequestExtension().getextensionforversion(extensionid, version)
        prevextension = FOIRequestExtension().getextensionforversion(extensionid, version[0]-1)
        extensionsummary = self.__maintained(curextension, prevextension, event)

        if extensionsummary is None or (extensionsummary and len(extensionsummary) <1):
            return  DefaultMethodResult(True,'No change',extensionid)
        else:
            try:
                self.createcomment(ministryrequestid, userid, username, extensionsummary)
                return DefaultMethodResult(True,'Comment posted',extensionid)
            except BusinessException as exception:
                return DefaultMethodResult(False,'unable to post comment - '+exception.message,extensionid)  
            
        
                
        
    def createcomment(self, ministryrequestid, userid, username, extensionsummary):        
        comment = {"ministryrequestid": ministryrequestid, "comment": self.__preparemessage(username, extensionsummary)}
        commentservice().createministryrequestcomment(comment, userid, 2)

    # work on denied or approved with modify
    def __maintained(self, curextension, prevextension, event):
            if event == EventType.delete.value:    
                return self.__createextensionsummary(prevextension, event)
            else: 
                return self.__createextensionsummary(curextension, event)
    
    def __createextensionsummary(self, extension, event):
        extnreson = extensionreasonservice().getextensionreasonbyid(extension['extensionreasonid'])
        return {'extension': extension, 'extensiontype': self.__getextensiontype(extnreson), 'reason': self.__getextensionreason(extnreson), 'event': event}

    def __getextensionreason(self, extnreson):       
       return extnreson["reason"]

    def __getextensiontype(self, extnreson):       
       return extnreson["extensiontype"]

    def __preparemessage(self, username, extensionsummary):        
        extension = extensionsummary["extension"] if 'extension' in extensionsummary else None
        event = extensionsummary["event"] if 'event' in extensionsummary else None
        extensiontype = extensionsummary["extensiontype"] if 'extensiontype' in extensionsummary else None         
        extensionreason = extensionsummary["reason"] if 'reason' in extensionsummary else None         
        approveddays = extension["approvednoofdays"] if 'approvednoofdays' in extension else extension["extendedduedays"]
        extendedduedays = extension["extendedduedays"] if 'extendedduedays' in extension else approveddays
        newduedate = extension["extendedduedate"] if 'extendedduedate' in extension else None
        statusid = extension["extensionstatusid"] if 'extensionstatusid' in extension else None

        # add status condition based on the US update
        if event == EventType.add.value and extensiontype == 'Public Body':
            return  username + " has taken a "+ str(extendedduedays) +" day Public Body extension. The new legislated due date is "+ self.__formatdate(newduedate, '%Y %b %d') + "."
        elif event == EventType.add.value and extensiontype == 'OIPC' and statusid == 2:            
            return  "The OIPC has granted a "+ str(approveddays) +" day extension. The new legislated due date is "+ self.__formatdate(newduedate, '%Y %b %d')
        elif statusid == 3:            
            return  "The OIPC has denied a "+ str(extendedduedays) +" day extension."
        elif event == EventType.modify.value:
            return "Extension for " + extensionreason + " has been edited."
        else:
            return "Extension for " + extensionreason + " has been deleted."

    def __formatdate(self, datevalue, format):
        return dateutil.parser.parse(datevalue).strftime(format) if datevalue is not None else None         

class EventType(Enum):
    add = "add"    
    delete = "delete"
    modify = "modify"
