
from os import stat
from re import VERBOSE

from requests.api import request
from request_api.services.watcherservice import watcherservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestNotifications import FOIRequestNotification
from request_api.models.FOIRequestNotificationUsers import FOIRequestNotificationUser
from request_api.models.FOIRawRequestNotifications import FOIRawRequestNotification
from request_api.models.FOIRawRequestNotificationUsers import FOIRawRequestNotificationUser
from request_api.models.default_method_result import DefaultMethodResult
from datetime import datetime as datetime2
import os
import json


class notificationservice:
    """ FOI notification management service
    """
    
    def createnotification(self, message, requestid, requesttype, notificationtype, userid):
        foirequest = self.__getrequest(requestid, requesttype)
        notification = self.__preparenotification(message, foirequest, requesttype, notificationtype, userid)
        if notification is not None: 
            if requesttype == "ministryrequest":         
                return FOIRequestNotification.savenotification(notification)
            else:
                return FOIRawRequestNotification.savenotification(notification)
        return  DefaultMethodResult(True,'No change',requestid)
     
            
    def getnotifications(self, userid):
        return FOIRequestNotification.getconsolidatednotifications(userid, self.__getnotificationdays())
    
    
    def dismissnotification(self, userid, idnumber, notificationid):        
        if idnumber is not None and notificationid is not None:
            requesttype = self.__getnotificationtypefromid(idnumber)
            return self.__dimissusernotificationbyid(requesttype, notificationid)
        else:
            return self.__dismissnotificationbyuser(userid)

    def __dimissusernotificationbyid(self, requesttype, notificationuserid):
        notficationids = self.__getdismissparentids(requesttype, notificationuserid)
        if requesttype == "ministryrequest":         
            cresponse = FOIRequestNotificationUser.dismissnotification(notificationuserid)
            presponse = FOIRequestNotification.dismissnotification(notficationids)            
        else:
            cresponse = FOIRawRequestNotificationUser.dismissnotification(notificationuserid)
            presponse = FOIRawRequestNotificationUser.dismissnotification(notficationids)
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

    def __filterdismissparentids(self,_notficationids):
        notficationids = []
        for notification in _notficationids:
            if notification["count"] == 1:
                notficationids.append(notification["notificationid"])    
        return notficationids 
            
    def __getnotificationtypefromid(self, idnumber):
        return 'rawrequest' if idnumber.lower().startswith('u-00') else 'ministryrequest'
    
            
    def __preparenotification(self, message, foirequest, requesttype, notificationtype, userid):            
        if requesttype == "ministryrequest":
            notification = FOIRequestNotification()
            notification.requestid = foirequest["foiministryrequestid"]
            notification.idnumber = foirequest["filenumber"]
            notification.foirequestid = foirequest["foirequest_id"]
        else:
            notification = FOIRawRequestNotification()
            notification.requestid = foirequest["requestid"]     
            notification.idnumber = 'U-00' + str(foirequest['requestid'])  
        notification.notificationtypeid = self.__getnotificationtypeid(notificationtype)
        notification.version = foirequest["version"]        
        notification.createdby = userid
        notification.created_at = datetime2.now()
        notification.notification = message  
        notificationusers = self.__getnotificationusers(notificationtype, foirequest, requesttype, userid)
        users = []
        for notificationuser in notificationusers:
            users.append(self.__preparenotificationuser(requesttype, notificationuser, userid))
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

    def __getnotificationusers(self, notificationtype, foirequest, requesttype, userid):
        notificationusers = []
        if notificationtype == "Assignment":
            _users = self.__getassignees(foirequest, requesttype)
        else:
            _users = self.__getassignees(foirequest, requesttype) + self.__getwatchers(foirequest, requesttype)
        for user in _users:
            if self.__isignorable(user, notificationusers, userid) == False:
                notificationusers.append(user)
        return notificationusers
    
    
    def __isignorable(self, notificationuser, users, userid):
        if notificationuser["userid"] == userid:
            return True
        else: 
            for user in users:
                if notificationuser["userid"] == user["userid"]:
                    return True
        return False
        
        
    def __getwatchers(self, foirequest, requesttype):
        notificationusers = []
        if requesttype == "ministryrequest":
            watchers =  watcherservice().getallministryrequestwatchers(foirequest["foiministryrequestid"])
        else:
            watchers =  watcherservice().getrawrequestwatchers(foirequest['requestid'])
        for watcher in watchers:
                notificationusers.append({"userid":watcher["watchedby"], "usertype":self.__getnotificationusertypeid("Watcher")})
        return notificationusers
        
    
    def __getassignees(self, foirequest, requesttype):
        notificationusers = []
        notificationtypeid = self.__getnotificationusertypeid("Assignee")
        if requesttype == "ministryrequest" and foirequest["assignedministryperson"] is not None:
            notificationusers.append({"userid":foirequest["assignedministryperson"], "usertype":notificationtypeid})
        if foirequest["assignedto"] is not None and foirequest["assignedto"] != '':
            notificationusers.append({"userid":foirequest["assignedto"], "usertype":notificationtypeid})
        return notificationusers
            
               
    def __getrequest(self, requestid, requesttype):
        if requesttype == "ministryrequest":
            return FOIMinistryRequest.getrequestbyministryrequestid(requestid)
        else:
            return FOIRawRequest.get_request(requestid)


    def __getnotificationtypeid(self, notificationtype):
        if notificationtype == "State":
            return 1
        elif notificationtype == "Assignment":
            return 5
        
        return 0
    
    
    def __getnotificationusertypeid(self, notificationusertype):
        if notificationusertype == "Watcher":
            return 1
        elif notificationusertype == "Assignee":
            return 2
        return 0
    
    def __getnotificationdays(self):
        if 'FOI_NOTIFICATION_DAYS' in os.environ and os.getenv('FOI_NOTIFICATION_DAYS') != '':
            return os.getenv('FOI_NOTIFICATION_DAYS')
        else:
            return str(10)