
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestExtensions import FOIRequestExtension
from request_api.services.commentservice import commentservice
from request_api.services.extensionreasonservice import extensionreasonservice
from request_api.services.notificationservice import notificationservice
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
        extensionsummaryforcomment = self.__maintained(curextension, prevextension, event)
        message = ""
        try:
            notificationresponse = self.createnotification(ministryrequestid, extensionid, curextension, prevextension, userid, event)
            if extensionsummaryforcomment is None or (extensionsummaryforcomment and len(extensionsummaryforcomment) < 1):
                return  DefaultMethodResult(True,'No change',extensionid)
            else:
                commentresponse = self.createcomment(ministryrequestid, userid, username, extensionsummaryforcomment)
                if commentresponse.success == True:                    
                    message += 'Comment posted' 
            if notificationresponse.success == True and event != EventType.delete.value:
                    message += 'Notification posted' 
            return DefaultMethodResult(True, message, extensionid)             
        except BusinessException as exception:
            return DefaultMethodResult(False,'unable to post comment - '+exception.message,extensionid) 
        
    def createcomment(self, ministryrequestid, userid, username, extensionsummary):        
        comment = {"ministryrequestid": ministryrequestid, "comment": self.__preparemessage(username, extensionsummary)}
        return commentservice().createministryrequestcomment(comment, userid, 2)

    def createnotification(self, ministryrequestid, extensionid, curextension, prevextension, userid, event):       
        
        nootificationrequired = self.__nonotificationrequired(curextension, prevextension, event)
        onlycleanuprequired = self.__onlycleanuprequired(curextension, prevextension, event)
        onlynotificationrequired = self.__onlynotificationrequired(curextension, prevextension, event)
        notificationandcleanup = self.__bothnotificationandcleanup(curextension, prevextension, event)
       
        if nootificationrequired == True:
            return DefaultMethodResult(True, "No Notification", ministryrequestid)
        elif onlycleanuprequired == True:
            notificationservice().cleanupnotifications(ministryrequestid, "ministryrequest", "Extension", extensionid)
            return DefaultMethodResult(True, "Delete Extension", ministryrequestid)
        elif onlynotificationrequired == True or notificationandcleanup == True:
            extensionsummary = self.__createnotificationsummary(curextension, prevextension, event)
            notification = self.__preparenotification(extensionsummary)
            return notificationservice().createnotification({"extensionid": extensionid, "message": notification}, ministryrequestid, "ministryrequest", "Extension", userid, notificationandcleanup)

    def __preparenotification(self, extensionsummary):
        ispublicbody = self.__valueexists('ispublicbody', extensionsummary)
        isdenied = self.__valueexists('isdenied', extensionsummary)
        isapproved = self.__valueexists('isapproved', extensionsummary)        
        extension = self.__valueexists('extension', extensionsummary)
        prevextension = self.__valueexists('prevextension', extensionsummary)

        prevapprovedays =  self.__valueexists('approvednoofdays', prevextension) if prevextension else None
        approveddays = self.__valueexists('approvednoofdays', extension)
        prevextendeddays = self.__valueexists('extendedduedays', prevextension) if prevextension else None
        extendedduedays = self.__valueexists('extendedduedays', extension) 
        newduedate = self.__formatdate(self.__valueexists('extendedduedate', extension), self.__genericdateformat())

        approveddayschanged = True if prevapprovedays != approveddays else False
        extendeddayschanged = True if prevextendeddays and prevextendeddays != extendedduedays else False

      
        if isdenied == True:
            return  "Extension request to OIPC has been denied."
        elif ispublicbody == True and isapproved == True or (extendeddayschanged == True):
            return "Extension taken for " + str(extendedduedays) + " days. The new legislated due date is "+ newduedate + "."
        elif isapproved == True and not ispublicbody or (approveddayschanged == True):
            return "Extension taken for " + str(approveddays) + " days. The new legislated due date is "+ newduedate + "."            
        else:
            return "Extension has been edited."

    # modify any state
    def __findmodify(self, curextension, prevextension, event):
        curextensionstatusid = self.__valueexists('extensionstatusid', curextension)
        prevextensionstatusid = self.__valueexists('extensionstatusid', prevextension) 
        if (event == EventType.modify.value and curextensionstatusid ==  prevextensionstatusid):           
            return True

    def __getextensionreason(self, reasonid):
        return extensionreasonservice().getextensionreasonbyid(reasonid)

    def __findpublicbody(self, curextension):
        extnreson = extensionreasonservice().getextensionreasonbyid(curextension['extensionreasonid'])
        extntype = self.__getextensiontype(extnreson)
        if extntype == ExtensionType.publicbody.value:
            return True  

    # add denied or modify to denied    
    def __finddenied(self, curextension, prevextension, event):
        curextensionstatusid = self.__valueexists('extensionstatusid', curextension)
        prevextensionstatusid = self.__valueexists('extensionstatusid', prevextension)
        if (event == EventType.modify.value and curextensionstatusid == ExtensionStatus.denied.value and  curextensionstatusid !=  prevextensionstatusid) or (event == EventType.add.value and curextensionstatusid == ExtensionStatus.denied.value ):
            return True

    # add approved or modify to approved
    def __findapproved(self, curextension, prevextension, event):
        curextensionstatusid = curextension["extensionstatusid"] if 'extensionstatusid' in curextension else None
        prevextensionstatusid = prevextension["extensionstatusid"] if 'extensionstatusid' in prevextension else None
        if (event == EventType.modify.value and curextensionstatusid == ExtensionStatus.approved.value and  curextensionstatusid !=  prevextensionstatusid) or (event == EventType.add.value and curextensionstatusid == ExtensionStatus.approved.value):
            return True

    def __nonotificationrequired(self, curextension, prevextension, event):
        curextensionstatusid = self.__valueexists('extensionstatusid', curextension)
        prevextensionstatusid = self.__valueexists('extensionstatusid', prevextension)
        curapproveddays = self.__valueexists('approvednoofdays', curextension)
        prevapproveddays = self.__valueexists('approvednoofdays', prevextension)
        if (event == EventType.add.value and curextensionstatusid == 1) or (event == EventType.modify.value and curextensionstatusid ==  prevextensionstatusid and curapproveddays == prevapproveddays):
            return True
    
    def __onlycleanuprequired(self, curextension, prevextension, event):
        curextensionstatusid = self.__valueexists('extensionstatusid', curextension)
        prevextensionstatusid = self.__valueexists('extensionstatusid', prevextension)
        if event == EventType.delete.value or (event == EventType.modify.value and str(prevextensionstatusid)  in [str(ExtensionStatus.denied.value), str(ExtensionStatus.approved.value)] and curextensionstatusid == 1):
            return True
    def __onlynotificationrequired(self, curextension, prevextension, event):
        isdenied = self.__finddenied(curextension, prevextension, event)
        ispublicbody = self.__findpublicbody(curextension)
        isapproved = self.__findapproved(curextension, prevextension, event)
        if isdenied == True or isapproved == True or ispublicbody == True:
            return True

    def __bothnotificationandcleanup(self, curextension, prevextension, event):
        curextensionstatusid = self.__valueexists('extensionstatusid', curextension)
        prevextensionstatusid = self.__valueexists('extensionstatusid', prevextension)
        curapproveddays = self.__valueexists('approvednoofdays', curextension)
        prevapproveddays = self.__valueexists('approvednoofdays', prevextension)
        if (event == EventType.modify.value and curextensionstatusid in [ExtensionStatus.approved.value, ExtensionStatus.denied.value] and prevextensionstatusid in [ExtensionStatus.approved.value, ExtensionStatus.denied.value]) or (event == EventType.modify.value and curextensionstatusid == ExtensionStatus.approved.value and curextensionstatusid == prevextensionstatusid and prevapproveddays != curapproveddays):
            return True
        else:
            return False

    def __maintained(self, curextension, prevextension, event):        
        return self.__createextensionsummary(curextension, prevextension, event)
    
    def __createextensionsummary(self, curextension, prevextension, event):
        isdenied = self.__finddenied(curextension, prevextension, event)
        ispublicbody = self.__findpublicbody(curextension)
        isapproved = self.__findapproved(curextension, prevextension, event)
        ismodified = self.__findmodify(curextension, prevextension, event)        
        curreasonid = self.__valueexists("extensionreasonid", curextension)        
        curreason = self.__getextensionreasonvalue(self.__getextensionreason(curreasonid))        
        if event == EventType.delete.value:
            return {'extension': curextension, 'reason': curreason, 'isdelete': True}
        elif event == EventType.modify.value and not ismodified and curextension["extensionstatusid"] != ExtensionStatus.pending.value:
            return {'extension': curextension, 'ispublicbody': ispublicbody, 'isdenied': isdenied, 'isapproved': isapproved, 'reason': self.__getextensionreasonvalue(self.__getextensionreason(curreasonid)), 'isdelete': False}   
        elif event == EventType.add.value and curextension["extensionstatusid"] != ExtensionStatus.pending.value:
            return {'extension': curextension, 'ispublicbody': ispublicbody, 'isdenied': isdenied, 'isapproved': isapproved, 'reason': self.__getextensionreasonvalue(self.__getextensionreason(curreasonid)), 'isdelete': False}
    
    def __createnotificationsummary(self, curextension, prevextension, event):
        isdenied = self.__finddenied(curextension, prevextension, event)
        ispublicbody = self.__findpublicbody(curextension)
        isapproved = self.__findapproved(curextension, prevextension, event)
    
        if event == EventType.modify.value:
            return {'extension': curextension, 'prevextension': prevextension, 'ispublicbody': ispublicbody, 'isdenied': isdenied, 'isapproved': isapproved}
        elif event == EventType.add.value and curextension["extensionstatusid"] != ExtensionStatus.pending.value:
            return {'extension': curextension, 'ispublicbody': ispublicbody, 'isdenied': isdenied, 'isapproved': isapproved}

    def __getextensionreasonvalue(self, extnreson):       
       return extnreson["reason"]

    def __getextensiontype(self, extnreson):       
       return extnreson["extensiontype"]

    def __valueexists(self, key, extensionsummary):
        return extensionsummary[key] if key in extensionsummary else None

    def __preparemessage(self, username, extensionsummary):        
        isdelete = self.__valueexists('isdelete', extensionsummary)
        ispublicbody = self.__valueexists('ispublicbody', extensionsummary)
        isdenied = self.__valueexists('isdenied', extensionsummary)
        isapproved = self.__valueexists('isapproved', extensionsummary)
        
        extension = self.__valueexists('extension', extensionsummary)       
        extensionreason = self.__valueexists('reason', extensionsummary)       
        
        approveddays = self.__valueexists('approvednoofdays', extension) 
        extendedduedays = self.__valueexists('extendedduedays', extension) 
        newduedate = self.__valueexists('extendedduedate', extension)

        if isdelete == True:
            return "Extension for " + extensionreason + " has been deleted."       
        elif isdenied == True:
            return  "The OIPC has denied a "+ str(extendedduedays) +" day extension."
        elif ispublicbody == True and isapproved == True:
            return  username + " has taken a "+ str(extendedduedays) +" day Public Body extension. The new legislated due date is "+ self.__formatdate(newduedate, self.__genericdateformat()) + "."
        elif isapproved == True and not ispublicbody:
            return  "The OIPC has granted a "+ str(approveddays) +" day extension. The new legislated due date is "+ self.__formatdate(newduedate, self.__genericdateformat())
        else:
            return "Extension for " + extensionreason + " has been edited."
   

    def __formatdate(self, datevalue, format):
        return dateutil.parser.parse(datevalue).strftime(format) if datevalue is not None else None

    def __genericdateformat(self):
        return '%Y %b %d'       

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

class ExtensionSummaryFor(Enum):
    comments = "comments"
    notification = "notification"

