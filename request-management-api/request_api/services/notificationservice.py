
from os import stat
from re import VERBOSE

from requests.api import request
from request_api.services.watcherservice import watcherservice
from request_api.services.notifications.notificationconfig import notificationconfig
from request_api.services.notifications.notificationuser import notificationuser
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestNotifications import FOIRequestNotification
from request_api.models.FOIRequestNotificationUsers import FOIRequestNotificationUser
from request_api.models.FOIRawRequestNotifications import FOIRawRequestNotification
from request_api.models.FOIRawRequestNotificationUsers import FOIRawRequestNotificationUser
from request_api.models.FOIRawRequestComments import FOIRawRequestComment
from request_api.models.FOIRequestComments import FOIRequestComment
from request_api.models.default_method_result import DefaultMethodResult
from datetime import datetime as datetime2
import os
import json
from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
from enum import Enum

class notificationservice:
    """ FOI notification management service
    """
    
    def createnotification(self, message, requestid, requesttype, notificationtype, userid, cleanup):
        extensionid = None
        foirequest = self.__getrequest(requestid, requesttype)
        if notificationtype == NotificationType.extension.value:
            extensionid = self.__getextensionidfrommesage(message)
        if cleanup == True:
            self.__cleanupnotifications(requesttype, notificationtype, foirequest, extensionid)
        return self.__createnotification(message, requestid, requesttype, notificationtype, userid, foirequest)
    
    def createremindernotification(self, message, requestid, requesttype, notificationtype, userid):
        foirequest = self.__getrequest(requestid, requesttype)
        return  self.__createnotification(message, requestid, requesttype, notificationtype, userid, foirequest)

    def createcommentnotification(self, message, comment, commenttype, requesttype, userid):
        requestid = comment["ministryrequestid"] if requesttype == "ministryrequest" else comment["requestid"]
        foirequest = self.__getrequest(requestid, requesttype)        
        return  self.__createnotification(message, requestid, requesttype, commenttype, userid, foirequest, comment)
    
    def cleanupnotifications(self, requestid, requesttype, notificationtype, extensionid=None):
        foirequest = self.__getrequest(requestid, requesttype)
        self.__cleanupnotifications(requesttype, notificationtype, foirequest, extensionid)

    def getnotifications(self, userid):
        return FOIRequestNotification.getconsolidatednotifications(userid, notificationconfig().getnotificationdays())

    def getcommentnotifications(self, commentid):
        return FOIRequestNotification.getcommentnotifications(commentid)

    def dismissnotification(self, userid, type, idnumber, notificationid):    
        if type is not None:
            return self.__dismissnotificationbytype(userid, type)
        else:    
            if idnumber is not None and notificationid is not None:
                requesttype = self.__getnotificationtypefromid(idnumber)
                return self.__dimissusernotificationbyid(requesttype, notificationid)
            else:
                return self.__dismissnotificationbyuser(userid) 
            
    def dismissremindernotification(self, requesttype, notificationtype):
        notificationid = notificationconfig().getnotificationtypeid(notificationtype)
        if requesttype == "ministryrequest": 
            _ids = FOIRequestNotification.getnotificationidsbytype(notificationid)
        else:
            _ids = FOIRawRequestNotification.getnotificationidsbytype(notificationid)
        self.__deletenotificationids(requesttype, _ids)  
    
    def dismissnotificationsbyid(self,requestid, requesttype):
        foirequest = self.__getrequest(requestid, requesttype)
        if requesttype == "ministryrequest":
            _ids = FOIRequestNotification.getnotificationidsbynumber(foirequest["filenumber"])
            if _ids:
                FOIRequestNotificationUser.dismissbynotificationid(_ids)
                FOIRequestNotification.dismissnotification(_ids)
        else:
            _ids = FOIRawRequestNotification.getnotificationidsbynumber('U-00' + str(foirequest['requestid']))
            if _ids:
                FOIRawRequestNotificationUser.dismissbynotificationid(_ids)
                FOIRawRequestNotification.dismissnotification(_ids)  
    
    def __createnotification(self, message, requestid, requesttype, notificationtype, userid, foirequest, foicomment=None):
        notification = self.__preparenotification(message, requesttype, notificationtype, userid, foirequest, foicomment)
        if notification is not None:      
            if requesttype == "ministryrequest": 
                return FOIRequestNotification.savenotification(notification)
            else:
                return FOIRawRequestNotification.savenotification(notification)
        return  DefaultMethodResult(True,'No change',requestid) 
    
    def __cleanupnotifications(self, requesttype, notificationtype, foirequest, extensionid=None):
        notificationid = notificationconfig().getnotificationtypeid(notificationtype) 
        if requesttype == "ministryrequest" and notificationid == 4:
            _ids = FOIRequestNotification.getnotificationidsbynumberandtypeandextensionid(foirequest["filenumber"], notificationid, extensionid)       
        elif requesttype == "ministryrequest":
            _ids = FOIRequestNotification.getnotificationidsbynumberandtype(foirequest["filenumber"], notificationid)
        else:
            _ids = FOIRawRequestNotification.getnotificationidsbynumberandtype('U-00' + str(foirequest['requestid']), notificationid)
        self.__deletenotificationids(requesttype, _ids) 
        
    def __deletenotificationids(self, requesttype, notificationids):
        if notificationids:
            if requesttype == "ministryrequest":
                FOIRequestNotificationUser.dismissbynotificationid(notificationids)
                FOIRequestNotification.dismissnotification(notificationids)
            else:
                FOIRawRequestNotificationUser.dismissbynotificationid(notificationids)
                FOIRawRequestNotification.dismissnotification(notificationids)            

    def __dimissusernotificationbyid(self, requesttype, notificationuserid):
        notficationids = self.__getdismissparentids(requesttype, notificationuserid)
        if requesttype == "ministryrequest":         
            cresponse = FOIRequestNotificationUser.dismissnotification(notificationuserid)
            presponse = FOIRequestNotification.dismissnotification(notficationids)            
        else:
            cresponse = FOIRawRequestNotificationUser.dismissnotification(notificationuserid)
            presponse = FOIRawRequestNotification.dismissnotification(notficationids)
        if cresponse.success == True and presponse.success == True:
            return DefaultMethodResult(True,'Notifications deleted for id',notificationuserid) 
        else:
            return DefaultMethodResult(False,'Unable to delete the notifications for id',notificationuserid)    
        
    def __dismissnotificationbyuser(self, userid):
        requestnotificationids = self.__getdismissparentidsbyuser("ministryrequest", userid)
        requestnotification = FOIRequestNotificationUser.dismissnotificationbyuser(userid)
        rawnotificationids = self.__getdismissparentidsbyuser("rawrequest", userid)
        rawnotification = FOIRawRequestNotificationUser.dismissnotificationbyuser(userid)   
        prequestnotification = FOIRequestNotification.dismissnotification(requestnotificationids) 
        prawnotification = FOIRawRequestNotification.dismissnotification(rawnotificationids)
        if requestnotification.success == True and rawnotification.success == True and prequestnotification.success == True and prawnotification.success == True:
            return DefaultMethodResult(True,'Notifications deleted for user',userid) 
        else:
            return DefaultMethodResult(False,'Unable to delete the notifications',userid)

    def __dismissnotificationbytype(self, userid, type):
        typeid = notificationconfig().getnotificationusertypeid(type)
        requestnotificationids = self.__getdismissparentidsbyuserandtype("ministryrequest", userid, typeid)
        requestnotification = FOIRequestNotificationUser.dismissnotificationbyuserandtype(userid, typeid)
        rawnotificationids = self.__getdismissparentidsbyuserandtype("rawrequest", userid, typeid)
        rawnotification = FOIRawRequestNotificationUser.dismissnotificationbyuserandtype(userid, typeid)   
        prequestnotification = FOIRequestNotification.dismissnotification(requestnotificationids) 
        prawnotification = FOIRawRequestNotification.dismissnotification(rawnotificationids)
        if requestnotification.success == True and rawnotification.success == True and prequestnotification.success == True and prawnotification.success == True:
            return DefaultMethodResult(True,'Notifications deleted for user',userid) 
        else:
            return DefaultMethodResult(False,'Unable to delete the notifications',userid)

    def __getdismissparentids(self, requesttype, notificationuserid):
        if requesttype == "ministryrequest":         
            _notficationids = FOIRequestNotificationUser.getnotificationsbyid(notificationuserid)
        else:
            _notficationids = FOIRawRequestNotificationUser.getnotificationsbyid(notificationuserid)
        return self.__filterdismissparentids(_notficationids)
        
    def __getdismissparentidsbyuser(self, requesttype, userid):
        if requesttype == "ministryrequest":         
            _notficationids = FOIRequestNotificationUser.getnotificationsbyuser(userid)
        else:
            _notficationids =  FOIRawRequestNotificationUser.getnotificationsbyuser(userid)
        return self.__filterdismissparentids(_notficationids)
    
    def __getdismissparentidsbyuserandtype(self, requesttype, userid, typeid):
        if requesttype == "ministryrequest":         
            _notficationids = FOIRequestNotificationUser.getnotificationsbyuserandtype(userid, typeid)
        else:
            _notficationids =  FOIRawRequestNotificationUser.getnotificationsbyuserandtype(userid, typeid)
        return self.__filterdismissparentids(_notficationids)

    def __filterdismissparentids(self,_notficationids):
        notficationids = []
        for notification in _notficationids:
            if notification["count"] == 1:
                notficationids.append(notification["notificationid"])    
        return notficationids 
            
    def __getnotificationtypefromid(self, idnumber):
        return 'rawrequest' if idnumber.lower().startswith('u-00') else 'ministryrequest'    
            
    def __preparenotification(self, message, requesttype, notificationtype, userid, foirequest, foicomment=None):            
        if requesttype == "ministryrequest":
            notification = FOIRequestNotification()
            notification.requestid = foirequest["foiministryrequestid"]
            notification.idnumber = foirequest["filenumber"]
            notification.foirequestid = foirequest["foirequest_id"]
        else:
            notification = FOIRawRequestNotification()
            notification.requestid = foirequest["requestid"]     
            notification.idnumber = 'U-00' + str(foirequest['requestid'])  
        notification.notificationtypeid = notificationconfig().getnotificationtypeid(notificationtype)
        notification.version = foirequest["version"]        
        notification.createdby = userid
        notification.created_at = datetime2.now()
        notification.notification = message
        notificationusers = notificationuser().getnotificationusers(notificationtype, requesttype, userid, foirequest, foicomment)
        users = []
        for _notificationuser in notificationusers:
            users.append(self.__preparenotificationuser(requesttype, _notificationuser, userid))
        notification.notificationusers = users        
        return notification if users else None
        
    def __preparenotificationuser(self, requesttype, notificationuser, userid):
        if requesttype == "ministryrequest":
            user = FOIRequestNotificationUser()
        else:
            user = FOIRawRequestNotificationUser()
        user.notificationusertypeid = notificationuser["usertype"]
        user.userid = notificationuser["userid"]
        user.createdby = userid
        user.created_at = datetime2.now()
        return user
           
    def __getrequest(self, requestid, requesttype):
        if requesttype == "ministryrequest":
            return FOIMinistryRequest.getrequestbyministryrequestid(requestid)
        else:
            return FOIRawRequest.get_request(requestid)
    
    def __getextensionidfrommesage(self, message):
        return self.__valueexists('extensionid', message)

    def __valueexists(self, key, jsonobj):
        return jsonobj[key] if key in jsonobj else None

class NotificationType(Enum):
    state = "State"
    extension = "Extension"
    iaoassignment = "IAO Assignment"
    ministryassignment = "Ministry Assignment"
    cfrduereminder = "CFR Due Reminder"
    legislativeduereminder = "Legislative Due Reminder"   
    newusercomments = "New User Comments"
    replyusercomments = "Reply User Comments"
    taggedusercomments = "Tagged User Comments"
       
    
    
    
    
        
