
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestExtensions import FOIRequestExtension
from request_api.services.commentservice import commentservice
from request_api.services.extensionreasonservice import extensionreasonservice
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestComments import FOIRequestComment
from request_api.models.FOIRequestNotifications import FOIRequestNotification
import json
from request_api.models.default_method_result import DefaultMethodResult
from enum import Enum
from request_api.exceptions import BusinessException
import dateutil.parser

MSG_NO_CHANGE='No change'

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
                return  DefaultMethodResult(True, MSG_NO_CHANGE ,extensionid)
            else:
                commentresponse = self.createcomment(ministryrequestid, userid, username, extensionsummaryforcomment)
                if commentresponse.success == True:                    
                    message += 'Comment posted' 
            if notificationresponse.success == True and event != EventType.delete.value:
                    message += 'Notification posted' 
            return DefaultMethodResult(True, message, extensionid)             
        except BusinessException as exception:
            return DefaultMethodResult(False,'unable to post comment - '+exception.message,extensionid)

    def deleteexistingrelatedevents(self, ministryrequestid):
        try:
            notificationids = FOIRequestNotification().getextensionnotificationidsbyministry(ministryrequestid)
            if notificationids:
                self.__deleteaxisextensionnotifications(notificationids)
            FOIRequestComment().deleteextensioncommentsbyministry(ministryrequestid)
        except BusinessException as exception:
            return DefaultMethodResult(False,'Issue in deleting previous event related to ministry id - '+exception.message,ministryrequestid)  

    def createaxisextensionevent(self, ministryrequestid, extensionid, userid, username, event):
        # get all extension comments and notification of the ministry id
        # delete all comments and notification related to ministry id and extension
        # add new comments and notification for the ministry id        
        version = FOIRequestExtension.getversionforextension(extensionid)       
        curextension = FOIRequestExtension().getextensionforversion(extensionid, version)
        prevextension = FOIRequestExtension().getextensionforversion(extensionid, version[0]-1)
        extensionsummaryforcomment = self.__maintained(curextension, prevextension, event)
        message = ""
        try:
            notificationresponse = self.createnotification(ministryrequestid, extensionid, curextension, prevextension, userid, event)
            if extensionsummaryforcomment is None or (extensionsummaryforcomment and len(extensionsummaryforcomment) < 1):
                return  DefaultMethodResult(True, MSG_NO_CHANGE ,extensionid)
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
        _comment = self.__preparemessage(username, extensionsummary)
        if _comment not in [None,'']:
            return commentservice().createministryrequestcomment({"ministryrequestid": ministryrequestid, "comment": _comment}, userid, 2)
        else:
             return  DefaultMethodResult(True, MSG_NO_CHANGE ,ministryrequestid)

    def createnotification(self, ministryrequestid, extensionid, curextension, prevextension, userid, event):       
        
        nootificationrequired = self.__nonotificationrequired(curextension, prevextension, event)
        onlycleanuprequired = self.__onlycleanuprequired(curextension, prevextension, event)
        onlynotificationrequired = self.__onlynotificationrequired(curextension, prevextension, event)
        notificationandcleanup = self.__bothnotificationandcleanup(curextension, prevextension, event)
        if nootificationrequired == True:
            return DefaultMethodResult(True, "No Notification", ministryrequestid)
        elif onlycleanuprequired == True:
            self.__deleteextensionnotification(extensionid)
            return DefaultMethodResult(True, "Delete Extension", ministryrequestid)
        elif onlynotificationrequired == True or notificationandcleanup == True:
            extensionsummary = self.__createnotificationsummary(curextension, prevextension, event)
            notification = self.__preparenotification(extensionsummary)
            if notificationandcleanup == True:
                self.__deleteextensionnotification(extensionid)
            return notificationservice().createnotification({"extensionid": extensionid, "message": notification}, ministryrequestid, "ministryrequest", "Extension", userid, False)

    def __deleteaxisextensionnotifications(self, notificationids):
        notificationservice().dismissnotificationbyid("ministryrequest", notificationids)

    def __deleteextensionnotification(self, extensionid):
        _extensionnotifications = notificationservice().getextensionnotifications(extensionid)
        noticiationids = []
        for _extensionnotification in _extensionnotifications:
            noticiationids.append(_extensionnotification["notificationid"])
            notificationservice().dismissnotificationbyid("ministryrequest", noticiationids)             
        return DefaultMethodResult(True,'Extension notifications deleted', extensionid)   

    def __preparenotification(self, extensionsummary):
        ispublicbody = self.__getvalueof('ispublicbody', extensionsummary)
        isdenied = self.__getvalueof('isdenied', extensionsummary)
        isapproved = self.__getvalueof('isapproved', extensionsummary)        
        extension = self.__getvalueof('extension', extensionsummary)
        prevextension = self.__getvalueof('prevextension', extensionsummary)
        prevapprovedays =  self.__getvalueof('approvednoofdays', prevextension) if prevextension else None
        approveddays = self.__getvalueof('approvednoofdays', extension)
        prevextendeddays = self.__getvalueof('extendedduedays', prevextension) if prevextension else None
        extendedduedays = self.__getvalueof('extendedduedays', extension) 
        newduedate = self.__formatdate(self.__getvalueof('extendedduedate', extension), self.__genericdateformat())

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

    # modified attributes without changing state
    def __isstatechanged(self, curextension, prevextension, event):
        if event == EventType.modify.value and self.__getvalueof('extensionstatusid',curextension) != ExtensionStatus.pending.value and self.__getvalueof('extensionstatusid',curextension) ==  self.__getvalueof('extensionstatusid',prevextension):           
            return False
        else:
            return True

    def __getextensionreason(self, reasonid):
        return extensionreasonservice().getextensionreasonbyid(reasonid)

    def __ispublicbody(self, curextension):
        extnreson = extensionreasonservice().getextensionreasonbyid(curextension['extensionreasonid'])
        extntype = self.__getextensiontype(extnreson)
        if extntype == ExtensionType.publicbody.value:
            return True  
        return False

    # add denied or modify to denied    
    def __isdenied(self, curextension, prevextension, event):
        return self.__isvalidaction(curextension, prevextension, event, ExtensionStatus.denied.value)

    # add approved or modify to approved
    def __isapproved(self, curextension, prevextension, event):
        return self.__isvalidaction(curextension, prevextension, event, ExtensionStatus.approved.value)

    def __isvalidaction(self,curextension, prevextension, event, status):
        curextensionstatusid = self.__getvalueof('extensionstatusid',curextension)
        prevextensionstatusid = self.__getvalueof('extensionstatusid',prevextension)
        if (event == EventType.modify.value and curextensionstatusid !=  prevextensionstatusid) or (event == EventType.add.value):
            if curextensionstatusid in [ExtensionStatus.denied.value,ExtensionStatus.approved.value] and status == curextensionstatusid:
                return True
        return False

    def __nonotificationrequired(self, curextension, prevextension, event):
        curextensionstatusid = self.__getvalueof('extensionstatusid',curextension)
        prevextensionstatusid = self.__getvalueof('extensionstatusid',prevextension)
        curapproveddays = self.__getvalueof('approvednoofdays',curextension)
        prevapproveddays = self.__getvalueof('approvednoofdays',prevextension)
        if (event == EventType.add.value and curextensionstatusid == 1) or (event == EventType.modify.value and curextensionstatusid ==  prevextensionstatusid and curapproveddays == prevapproveddays):
            return True
        return False
    
    def __onlycleanuprequired(self, curextension, prevextension, event):
        curextensionstatusid = self.__getvalueof('extensionstatusid',curextension)
        prevextensionstatusid = self.__getvalueof('extensionstatusid',prevextension)
        if event == EventType.delete.value or (event == EventType.modify.value and str(prevextensionstatusid)  in [str(ExtensionStatus.denied.value), str(ExtensionStatus.approved.value)] and curextensionstatusid == 1):
            return True
        return False

    def __onlynotificationrequired(self, curextension, prevextension, event):
        if self.__isdenied(curextension, prevextension, event) == True or self.__isapproved(curextension, prevextension, event) == True or self.__ispublicbody(curextension) == True:
            return True
        return False

    def __bothnotificationandcleanup(self, curextension, prevextension, event):
        curextensionstatusid = self.__getvalueof('extensionstatusid',curextension)
        prevextensionstatusid = self.__getvalueof('extensionstatusid',prevextension)
        curapproveddays = self.__getvalueof('approvednoofdays',curextension)
        prevapproveddays = self.__getvalueof('approvednoofdays',prevextension)
        if (event == EventType.modify.value and curextensionstatusid in [ExtensionStatus.approved.value, ExtensionStatus.denied.value] and prevextensionstatusid in [ExtensionStatus.approved.value, ExtensionStatus.denied.value]) or (event == EventType.modify.value and curextensionstatusid == ExtensionStatus.approved.value and curextensionstatusid == prevextensionstatusid and prevapproveddays != curapproveddays):
            return True
        return False

    def __maintained(self, curextension, prevextension, event):   
        return self.__createextensionsummary(curextension, prevextension, event)
    
    def __createextensionsummary(self, curextension, prevextension, event):
        _extensionsummary = {'extension': curextension, 'prevextension':prevextension, 'reason': self.__getreasonfromid(self.__getvalueof("extensionreasonid", curextension)), 'action': event} 
        if event == EventType.delete.value:
            _extensionsummary['isdelete'] = True
        elif curextension["extensionstatusid"] != ExtensionStatus.pending.value and (event == EventType.modify.value or event == EventType.add.value):
            _extensionsummary['isdelete'] = False
            _extensionsummary['isdenied'] = self.__isdenied(curextension, prevextension, event)
            _extensionsummary['ispublicbody'] =  self.__ispublicbody(curextension)
            _extensionsummary['isapproved'] = self.__isapproved(curextension, prevextension, event)
        return _extensionsummary
    
    def __createnotificationsummary(self, curextension, prevextension, event):
        isdenied = self.__isdenied(curextension, prevextension, event)
        ispublicbody = self.__ispublicbody(curextension)
        isapproved = self.__isapproved(curextension, prevextension, event)
    
        if event == EventType.modify.value:
            return {'extension': curextension, 'prevextension': prevextension, 'ispublicbody': ispublicbody, 'isdenied': isdenied, 'isapproved': isapproved}
        elif event == EventType.add.value and curextension["extensionstatusid"] != ExtensionStatus.pending.value:
            return {'extension': curextension, 'ispublicbody': ispublicbody, 'isdenied': isdenied, 'isapproved': isapproved}

    def __preparemessage(self, username, extensionsummary):
        action =  self.__getvalueof('action', extensionsummary)     
        extension = self.__getvalueof('extension', extensionsummary) 
        prevextension = self.__getvalueof('prevextension', extensionsummary) 
        ispublicbody = self.__getvalueof('ispublicbody', extensionsummary)
        isapproved = self.__getvalueof('isapproved', extensionsummary)
        message = ""
        if action == EventType.delete.value:
            message = "Extension for " + self.__getvalueof('reason',extensionsummary) + " has been deleted."   
        elif action in [EventType.modify.value, EventType.add.value]:
            if self.__isstatechanged(extension, prevextension, action) == False:
                message = self.__preparemodifycomment(extensionsummary)
            else:
                if self.__getvalueof('isdenied', extensionsummary) == True:
                    message =  "The OIPC has denied a "+ str(self.__getvalueof('extendedduedays',extension)) +" day extension."
                elif isapproved == True:
                    if ispublicbody == True:
                        message = username + " has taken a "+ str(self.__getvalueof('extendedduedays',extension)) +" day Public Body extension." 
                    else:
                        message = "The OIPC has granted a "+ str(self.__getvalueof('approvednoofdays',extension) ) +" day extension." 
                    message += " The new legislated due date is "+ self.__formatdate(self.__getvalueof('extendedduedate',extension), self.__genericdateformat())
        else:
            message = "Extension for " + self.__getvalueof('reason',extensionsummary) + " has been edited."
        return message

    def __preparemodifycomment(self,extensionsummary):
        extension = self.__getvalueof('extension', extensionsummary) 
        prevextension = self.__getvalueof('prevextension', extensionsummary)
        isapproved = True if self.__getvalueof('extensionstatusid', extension)  == ExtensionStatus.approved.value else False
        comment = ""
        if self.__getvalueof('extensionreasonid', extension) != self.__getvalueof('extensionreasonid', prevextension):
            comment = "Extension reason has been updated to " + self.__getvalueof('reason', extensionsummary)   
        
        if isapproved is True:
            if self.__getvalueof('approvednoofdays', extension) != self.__getvalueof('approvednoofdays', prevextension):
                comment += " AND " if comment not in [None,""] else ""
                comment +="Approved number of days for extension has changed to " + str(self.__getvalueof('approvednoofdays', extension))+ "."            
                comment +=  " The new legislated due date is "+ self.__formatdate(self.__getvalueof('extendedduedate', extension), self.__genericdateformat())
        else:
            if self.__getvalueof('extendedduedays', extension) != self.__getvalueof('extendedduedays', prevextension):
                comment += " AND " if comment not in [None,""] else ""    
                comment +="Denied number of days for extension has changed to " + str(self.__getvalueof('extendedduedays', extension))+ "."            
        return comment

    def __getreasonfromid(self, curreasonid):
        return self.__getextensionreasonvalue(self.__getextensionreason(curreasonid))
    
    def __getextensionreasonvalue(self, extnreson):       
       return extnreson["reason"]

    def __getextensiontype(self, extnreson):       
       return extnreson["extensiontype"]

    def __getvalueof(self, key, extensionsummary):
        return extensionsummary[key] if key in extensionsummary else None

    def __formatdate(self, datevalue, format):
        return dateutil.parser.parse(datevalue).strftime(format) if datevalue is not None else None

    def __genericdateformat(self):
        return '%b %d %Y'       

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