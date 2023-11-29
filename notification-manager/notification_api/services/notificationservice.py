
from os import stat
from re import VERBOSE

from notification_api.services.notifications.notificationconfig import notificationconfig
from notification_api.services.notifications.notificationuser import notificationuser
from notification_api.dao.models.FOIRequestNotifications import FOIRequestNotification
from notification_api.dao.models.FOIRequestNotificationUsers import FOIRequestNotificationUser
from notification_api.dao.models.FOIMinistryRequest import FOIMinistryRequest

from notification_api.services.external.keycloakadminservice import KeycloakAdminService
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

            #mute notifications for ministry users
            mutenotification = self.__mutenotification(requesttype, notificationtype, foirequest)
            ministryusers = []
            usergroupfromkeycloak = KeycloakAdminService().getmembersbygroupname(foirequest["assignedministrygroup"])
            if usergroupfromkeycloak is not None and len(usergroupfromkeycloak) > 0:
                for user in usergroupfromkeycloak[0].get("members"):
                    ministryusers.append(user["username"])

            #Create notification users
            return self.__createnotificationusers(requesttype, notificationid, notificationusers, userid, mutenotification, ministryusers)
        return  DefaultMethodResult(True,'No change',requestid)

    def __createnotification(self, message, requesttype, notificationtype, userid, foirequest):
        notification = self.__preparenotification(message, requesttype, notificationtype, userid, foirequest)
        if notification is not None and requesttype == "ministryrequest":      
            return FOIRequestNotification().savenotification(notification)
        return None

    def __createnotificationusers(self, requesttype, notificationid, notificationusers, userid, mute=False, ministryusers=[]):    
        for notificationuser in notificationusers:
            if requesttype == "ministryrequest":
                user = self.__preparenotificationuser(notificationid, notificationuser, userid, mute, ministryusers)
                FOIRequestNotificationUser().savenotificationuser(user)
        return  DefaultMethodResult(True,'Notification users added',notificationid)
  
       
            
    def __preparenotification(self, message, requesttype, notificationtype, userid, foirequest):
        if requesttype == "ministryrequest":
            notification = FOIRequestNotification()
            notification.requestid = foirequest["foiministryrequestid"]
            notification.idnumber = foirequest["filenumber"]
            notification.foirequestid = foirequest["foirequest_id"]
        notification.notificationtypelabel = notificationconfig().getnotificationtypelabel(notificationtype)
        notification.axisnumber = foirequest["axisrequestid"]
        notification.version = foirequest["version"]        
        notification.createdby = userid
        notification.notification = message
        return notification

         
    def __preparenotificationuser(self, notificationid, notificationuser, userid, mute, ministryusers):
        user = FOIRequestNotificationUser()
        if notificationuser["userid"] in ministryusers:
            user.isdeleted = mute
        else:
            user.isdeleted = False
        user.notificationusertypelabel = notificationuser["usertype"]
        user.notificationid = notificationid
        user.userid = notificationuser["userid"]
        user.createdby = userid
        user.created_at = datetime.now()
        return user
           
    def getrequest(self, requestid, requesttype):
        if requesttype == "ministryrequest":
            return FOIMinistryRequest.getrequest(requestid)

    def __mutenotification(self, requesttype, notificationtype, request):
        #get mute conditions from env
        mutenotifications = notificationconfig().getmutenotifications()
        bcgovcode = request["bcgovcode"].upper()
        if requesttype == "ministryrequest" and bcgovcode in mutenotifications:
            if request["requesttype"].upper() in (_requesttype.upper() for _requesttype in mutenotifications[bcgovcode]["request_types"]):
                if request["requeststatus"].upper() in (_state.upper() for _state in mutenotifications[bcgovcode]["state_exceptions"]):
                    return False
                if notificationtype.upper() in (_notificationtype.upper() for _notificationtype in mutenotifications[bcgovcode]["type_exceptions"]):
                    return False
                return True
            else:
                return False
        else:
            return False