
from os import stat
from re import VERBOSE

from notification_api.services.notifications.notificationconfig import notificationconfig
from notification_api.services.notifications.notificationuser import notificationuser
from notification_api.dao.models.FOIRequestNotifications import FOIRequestNotification
from notification_api.dao.models.FOIRequestNotificationUsers import FOIRequestNotificationUser
from notification_api.dao.models.FOIMinistryRequest import FOIMinistryRequest

from notification_api.default_method_result import DefaultMethodResult
from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
import logging

class notificationservice:
    """ FOI notification management service
    """
    

    def createnotification(self, requesttype, requestid, message, notificationtype, userid):
        foirequest = self.getrequest(requestid, requesttype) 
        # Get Notification users
        notificationusers = notificationuser().getnotificationusers(notificationtype, requesttype, userid, foirequest)
        #If notification users exist
        if notificationusers is not None and len(notificationusers) > 0:
            #Create notification
            notificationid =  self.__createnotification(message, requesttype, notificationtype, userid, foirequest)
            #Create notification users
            return self.__createnotificationusers(requesttype, notificationid, notificationusers, userid)
        return  DefaultMethodResult(True,'No change',requestid)

    def __createnotification(self, message, requesttype, notificationtype, userid, foirequest):
        notification = self.__preparenotification(message, requesttype, notificationtype, userid, foirequest)
        if notification is not None and requesttype == "ministryrequest":      
            return FOIRequestNotification().savenotification(notification)
        return None

    def __createnotificationusers(self, requesttype, notificationid, notificationusers, userid):    
        for notificationuser in notificationusers:
            user = self.__preparenotificationuser(requesttype, notificationid, notificationuser, userid)
            if requesttype == "ministryrequest": 
                FOIRequestNotificationUser().savenotificationuser(user)
        return  DefaultMethodResult(True,'Notification users added',notificationid)
  
       
            
    def __preparenotification(self, message, requesttype, notificationtype, userid, foirequest):
        if requesttype == "ministryrequest":
            notification = FOIRequestNotification()
            notification.requestid = foirequest["foiministryrequestid"]
            notification.idnumber = foirequest["filenumber"]
            notification.foirequestid = foirequest["foirequest_id"]
        notification.notificationtypeid = notificationconfig().getnotificationtypeid(notificationtype)
        notification.axisnumber = foirequest["axisrequestid"]
        notification.version = foirequest["version"]        
        notification.createdby = userid
        notification.notification = message
        return notification

         
    def __preparenotificationuser(self, requesttype, notificationid, notificationuser, userid):
        if requesttype == "ministryrequest":
            user = FOIRequestNotificationUser()
        user.notificationusertypeid = notificationuser["usertype"]
        user.notificationid = notificationid
        user.userid = notificationuser["userid"]
        user.createdby = userid
        user.created_at = datetime.now()
        return user
           
    def getrequest(self, requestid, requesttype):
        if requesttype == "ministryrequest":
            return FOIMinistryRequest.getrequest(requestid)
