
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
from request_api.services.external.keycloakadminservice import KeycloakAdminService
from request_api.models.OperatingTeams import OperatingTeam

class notificationservice:
    """ FOI notification management service
    """
    
    def createnotification(self, message, requestid, requesttype, notificationtype, userid, previousassignee, iscleanup=True):
        foirequest = self.getrequest(requestid, requesttype)
        if iscleanup == True:
            self.__cleanupnotifications(requesttype, notificationtype, foirequest)
        return self.__createnotification(message, requestid, requesttype, notificationtype, userid, foirequest, previousassignee)

    def createremindernotification(self, message, requestid, requesttype, notificationtype, userid):
        foirequest = self.getrequest(requestid, requesttype)
        return  self.__createnotification(message, requestid, requesttype, notificationtype, userid, foirequest)
    
    def createcommentnotification(self, message, comment, commenttype, requesttype, userid):
        requestid = comment["ministryrequestid"] if requesttype == "ministryrequest" else comment["requestid"]
        foirequest = self.getrequest(requestid, requesttype)        
        return  self.__createnotification(message, requestid, requesttype, commenttype, userid, foirequest, None, comment)

    def getnotifications(self, userid):
        return FOIRequestNotification.getconsolidatednotifications(userid, notificationconfig().getnotificationdays())

    def getcommentnotifications(self, commentid):
        return FOIRequestNotification.getcommentnotifications(commentid)
    
    def getextensionnotifications(self, extensionid):
        return FOIRequestNotification.getextensionnotifications(extensionid)

    def dismissnotification(self, userid, type, idnumber, notificationuserid):    
        if type is not None:
            return self.__dismissnotificationbytype(userid, type)
        else:    
            if idnumber is not None and notificationuserid is not None:
                requesttype = self.__getnotificationtypefromid(idnumber)
                return self.__dimissnotificationbyuserid(requesttype, notificationuserid)
            else:
                return self.__dismissnotificationbyuser(userid) 
            
    def dismissnotificationbyid(self, requesttype, notificationids): 
        return self.__deletenotificationids(requesttype, notificationids)    
            
    def dismissremindernotification(self, requesttype, notificationtype):
        notificationid = notificationconfig().getnotificationtypeid(notificationtype)
        if requesttype == "ministryrequest": 
            _ids = FOIRequestNotification.getnotificationidsbytype(notificationid)
        else:
            _ids = FOIRawRequestNotification.getnotificationidsbytype(notificationid)
        self.__deletenotificationids(requesttype, _ids)  
    
    def dismissnotificationsbyrequestid(self,requestid, requesttype):
        foirequest = self.getrequest(requestid, requesttype)
        if requesttype == "ministryrequest":
            idnumber = foirequest["filenumber"]
            _ids = FOIRequestNotification.getnotificationidsbynumber(idnumber)
            if _ids:
                FOIRequestNotificationUser.dismissbynotificationid(_ids)
                FOIRequestNotification.dismissnotification(_ids)
        else:
            _ids = FOIRawRequestNotification.getnotificationidsbynumber('U-00' + str(foirequest['requestid']))
            if _ids:
                FOIRawRequestNotificationUser.dismissbynotificationid(_ids)
                FOIRawRequestNotification.dismissnotification(_ids)  
    
    def __createnotification(self, message, requestid, requesttype, notificationtype, userid, foirequest, previousassignee=None, foicomment=None):
        notification = self.__preparenotification(message, requesttype, notificationtype, userid, foirequest, previousassignee, foicomment)
        if notification is not None:      
            if requesttype == "ministryrequest": 
                return FOIRequestNotification.savenotification(notification)
            else:
                return FOIRawRequestNotification.savenotification(notification)
        return  DefaultMethodResult(True,'No change',requestid) 
    
    def __cleanupnotifications(self, requesttype, notificationtype, foirequest):
        notificationtypeids = self.__getcleanupnotificationids(notificationtype)
        if requesttype == "ministryrequest":
            idnumber = foirequest["filenumber"]
            _ids = FOIRequestNotification.getnotificationidsbynumberandtype(idnumber, notificationtypeids)
        else:
            _ids = FOIRawRequestNotification.getnotificationidsbynumberandtype('U-00' + str(foirequest['requestid']), notificationtypeids[0])
        self.__deletenotificationids(requesttype, _ids) 

    def cleanupwatchernotifications(self, requestid, requesttype, notificationtype, userid):
        notificationtypeids = self.__getcleanupnotificationids(notificationtype)
        foirequest = self.getrequest(requestid, requesttype)
        if requesttype == "ministryrequest":
            idnumber = foirequest["filenumber"]
            _ids = FOIRequestNotification.getnotificationidsbynumberandtype(idnumber, notificationtypeids)
        else:
            _ids = FOIRawRequestNotification.getnotificationidsbynumberandtype('U-00' + str(foirequest['requestid']), notificationtypeids[0])
        self.__deletenotificationbyuserandid(requesttype, _ids, userid) 
        

    def __getcleanupnotificationids(self, notificationtype):
        notificationtypeids = []
        notificationid = notificationconfig().getnotificationtypeid(notificationtype)
        notificationtypeids.append(notificationid)
        if notificationtype == "State" or notificationtype.endswith("Assignment"):
            notificationtypeids.append(notificationconfig().getnotificationtypeid("Group Members"))   
        return notificationtypeids


    def __deletenotificationids(self, requesttype, notificationids):
        if notificationids:
            if requesttype == "ministryrequest":
                cresponse = FOIRequestNotificationUser.dismissbynotificationid(notificationids)
                presponse = FOIRequestNotification.dismissnotification(notificationids)
            else:
                cresponse = FOIRawRequestNotificationUser.dismissbynotificationid(notificationids)
                presponse = FOIRawRequestNotification.dismissnotification(notificationids)  
            if cresponse.success == True and presponse.success == True:
                return DefaultMethodResult(True,'Notifications deleted for id','|'.join(map(str, notificationids))) 
            else:
                return DefaultMethodResult(False,'Unable to delete the notifications for id','|'.join(map(str, notificationids)))          

    def __dimissnotificationbyuserid(self, requesttype, notificationuserid):
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

    def __deletenotificationbyuserandid(self, requesttype, notificationids,userid):
        if notificationids:
            if requesttype == "ministryrequest":
                requestnotificationids= FOIRequestNotificationUser.getnotificationidsbyuserandid(userid, notificationids)
                cresponse = FOIRequestNotificationUser.dismissbynotificationid(requestnotificationids)
                presponse = FOIRequestNotification.dismissnotification(requestnotificationids)
                if cresponse.success == True and presponse.success == True:
                    return DefaultMethodResult(True,'Notifications deleted for id','|'.join(map(str, notificationids))) 
                else:
                    return DefaultMethodResult(False,'Unable to delete the notifications for id','|'.join(map(str, notificationids))) 
            else:
                rawnotificationids= FOIRawRequestNotificationUser.getnotificationidsbyuserandid(userid, notificationids)
                cresponse = FOIRawRequestNotificationUser.dismissbynotificationid(rawnotificationids)
                presponse = FOIRawRequestNotification.dismissnotification(rawnotificationids)  
                if cresponse.success == True and presponse.success == True:
                    return DefaultMethodResult(True,'Notifications deleted for id','|'.join(map(str, notificationids))) 
                else:
                    return DefaultMethodResult(False,'Unable to delete the notifications for id','|'.join(map(str, notificationids))) 

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
            
    def __preparenotification(self, message, requesttype, notificationtype, userid, foirequest, previousassignee=None, foicomment=None):
        if requesttype == "ministryrequest":
            notification = FOIRequestNotification()
            notification.requestid = foirequest["foiministryrequestid"]
            notification.idnumber = foirequest["filenumber"]
            notification.foirequestid = foirequest["foirequest_id"]
        else:
            notification = FOIRawRequestNotification()
            notification.requestid = foirequest["requestid"]
            notification.idnumber ='U-00' + str(foirequest['requestid'])

        notification.notificationtypeid = notificationconfig().getnotificationtypeid(notificationtype)
        notification.axisnumber = foirequest["axisrequestid"]
        notification.version = foirequest["version"]        
        notification.createdby = userid
        notification.notification = message
        notificationusers = notificationuser().getnotificationusers(notificationtype, requesttype, userid, foirequest, foicomment, previousassignee)
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
        return user
           
    def getrequest(self, requestid, requesttype):
        if requesttype == "ministryrequest":
            return FOIMinistryRequest.getrequestbyministryrequestid(requestid)
        else:
            return FOIRawRequest.get_request(requestid)

       
    
    
    
    
        
