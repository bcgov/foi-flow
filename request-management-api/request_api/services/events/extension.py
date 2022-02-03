
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

        if extensionsummary is None or (extensionsummary and len(extensionsummary) < 1):
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

    def __findmodify(self, curextension, prevextension, event):
        curextensionstatusid = curextension["extensionstatusid"] if 'extensionstatusid' in curextension else None
        prevextensionstatusid = prevextension["extensionstatusid"] if 'extensionstatusid' in prevextension else None  
        if (event == EventType.modify.value and curextensionstatusid ==  prevextensionstatusid):           
            return True
    def __getextensionreason(self, reasonid):
        return extensionreasonservice().getextensionreasonbyid(reasonid)

    def __findpublicbody(self, curextension, event):
        extnreson = extensionreasonservice().getextensionreasonbyid(curextension['extensionreasonid'])
        extntype = self.__getextensiontype(extnreson)
        if event == EventType.add.value and extntype == ExtensionType.publicbody.value:
            return True        
        
    def __finddenied(self, curextension, prevextension, event):
        curextensionstatusid = curextension["extensionstatusid"] if 'extensionstatusid' in curextension else None
        prevextensionstatusid = prevextension["extensionstatusid"] if 'extensionstatusid' in prevextension else None
        if (event == EventType.modify.value and curextensionstatusid == ExtensionStatus.denied.value and  curextensionstatusid !=  prevextensionstatusid) or (event == EventType.add.value and curextensionstatusid == ExtensionStatus.denied.value ):
            return True

    def __findapproved(self, curextension, prevextension, event):
        curextensionstatusid = curextension["extensionstatusid"] if 'extensionstatusid' in curextension else None
        prevextensionstatusid = prevextension["extensionstatusid"] if 'extensionstatusid' in prevextension else None
        if (event == EventType.modify.value and curextensionstatusid == ExtensionStatus.approved.value and  curextensionstatusid !=  prevextensionstatusid) or (event == EventType.add.value and curextensionstatusid == ExtensionStatus.approved.value):
            return True

    def __maintained(self, curextension, prevextension, event):        
        return self.__createextensionsummary(curextension, prevextension, event)
    
    def __createextensionsummary(self, curextension, prevextension, event):
        isdenied = self.__finddenied(curextension, prevextension, event)
        ispublicbody = self.__findpublicbody(curextension, event)
        isapproved = self.__findapproved(curextension, prevextension, event)        
        ismodified = self.__findmodify(curextension, prevextension, event)
        isreasonchanged = self.__reasonchanged(curextension, prevextension, event)
        prevreasonid = prevextension["extensionreasonid"] if prevextension else None
        curreasonid = curextension["extensionreasonid"] if curextension else None
        
        if event == EventType.delete.value:  
            return {'extension': curextension, 'reason': self.__getextensionreasonvalue(self.__getextensionreason(curreasonid)), 'isdelete': True}
        elif event == EventType.modify.value:
            return {'extension': curextension, 'isdenied': isdenied, 'isapproved': isapproved, 'reason': self.__getextensionreasonvalue(self.__getextensionreason(curreasonid)), 'prevreason': self.__getextensionreasonvalue(self.__getextensionreason(prevreasonid)), 'ismodified': ismodified, 'isreasonchanged': isreasonchanged, 'isdelete': False}   
        else:
            return {'extension': curextension, 'ispublicbody': ispublicbody, 'isdenied': isdenied, 'isapproved': isapproved, 'reason': self.__getextensionreasonvalue(self.__getextensionreason(curreasonid)), 'ismodified': ismodified, 'isreasonchanged': isreasonchanged, 'isdelete': False}

    def __getextensionreasonvalue(self, extnreson):       
       return extnreson["reason"]

    def __getextensiontype(self, extnreson):       
       return extnreson["extensiontype"]

    def __valueexists(self, key, extensionsummary):
        return extensionsummary[key] if key in extensionsummary else None

    def __reasonchanged(self, curextension, prevextension, event):        
        curreason = self.__getextensionreasonvalue(self.__getextensionreason(self.__valueexists('extensionreasonid', curextension)))
        prevreason = None
        prevreasonid = self.__valueexists('extensionreasonid', prevextension)
        if prevreasonid:
            prevreason = self.__getextensionreasonvalue(self.__getextensionreason(prevreasonid))
        if event == EventType.modify.value and curreason and  prevreason and curreason != prevreason:
            return True

    def __preparemessage(self, username, extensionsummary):        
        isdelete = self.__valueexists('isdelete', extensionsummary)
        ispublicbody = self.__valueexists('ispublicbody', extensionsummary)
        isdenied = self.__valueexists('isdenied', extensionsummary)
        isapproved = self.__valueexists('isapproved', extensionsummary)
        ismodified = self.__valueexists('ismodified', extensionsummary)       
        isreasonchanged = self.__valueexists('isreasonchanged', extensionsummary)
        extension = self.__valueexists('extension', extensionsummary)       
        extensionreason = self.__valueexists('reason', extensionsummary)       
        prevreason = self.__valueexists('prevreason', extensionsummary)

        approveddays = self.__valueexists('approvednoofdays', extension) 
        extendedduedays = self.__valueexists('extendedduedays', extension) 
        newduedate = self.__valueexists('extendedduedate', extension)

        if isdelete == True:
            return "Extension for " + extensionreason + " has been deleted."
        elif ismodified == True:
            return "Extension for " + extensionreason + " has been edited."
        elif isdenied == True:
            return  "The OIPC has denied a "+ str(extendedduedays) +" day extension."
        elif ispublicbody == True:
            return  username + " has taken a "+ str(extendedduedays) +" day Public Body extension. The new legislated due date is "+ self.__formatdate(newduedate, '%Y %b %d') + "."
        elif isapproved == True:
            return  "The OIPC has granted a "+ str(approveddays) +" day extension. The new legislated due date is "+ self.__formatdate(newduedate, '%Y %b %d')
        elif isreasonchanged == True:
            return "Extensions for " + prevreason + " has been edited to " + extensionreason + "."
        else:
            return "PENDING Extension for " + extensionreason + " added."
   

    def __formatdate(self, datevalue, format):
        return dateutil.parser.parse(datevalue).strftime(format) if datevalue is not None else None         

class EventType(Enum):
    add = "add"    
    delete = "delete"
    modify = "modify"

class ExtensionStatus(Enum):
    pending = 1
    approved = 2
    denied = 3

class ExtensionType(Enum):
    publicbody = "Public Body"
    oipc = "OIPC"
