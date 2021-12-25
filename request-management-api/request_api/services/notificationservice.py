
from os import stat
from re import VERBOSE
from request_api.services.watcherservice import watcherservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestNotifications import FOIRequestNotification
from request_api.models.FOIRequestNotificationUsers import FOIRequestNotificationUser
from request_api.models.FOIRawRequestNotifications import FOIRawRequestNotification
from request_api.models.FOIRawRequestNotificationUsers import FOIRawRequestNotificationUser
from datetime import datetime as datetime2

import json


class notificationservice:
    """ FOI notification management service
    """
    
    def createnotification(self, message, requestid, requesttype, notificationtype, userid):
        foirequest = self.__getrequest(requestid, requesttype)
        notification = self.__preparenotification(message, foirequest, requesttype, notificationtype, userid)
        if requesttype == "ministryrequest":         
            FOIRequestNotification.savenotification(notification)
        else:
            FOIRawRequestNotification.savenotification(notification)
            
    def getnotifications(self, userid):
        return FOIRequestNotification.getconsolidatednotifications(userid)

    def __preparenotification(self, message, foirequest, requesttype, notificationtype, userid):            
        if requesttype == "ministryrequest":
            notification = FOIRequestNotification()
            notification.requestid = foirequest["foiministryrequestid"]
            notification.idnumber = foirequest["filenumber"]
        else:
            notification = FOIRawRequestNotification()
            notification.requestid = foirequest["requestid"]     
            notification.idnumber = 'U-00' + str(foirequest['requestid'])  
        notification.notificationtypeid = self.__getnotificationtypeid(notificationtype)
        notification.version = foirequest["version"]        
        notification.createdby = userid
        notification.created_at = datetime2.now()
        notification.notification = message  
        notificationusers = self.__getnotificationusers(foirequest, requesttype)
        users = []
        for notificationuser in notificationusers:
            users.append(self.__preparenotificationuser(requesttype, notificationuser, userid))
        notification.notificationusers = users
        return notification    
    

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

   
    def __getnotificationusers(self, foirequest, requesttype):
        notificationusers = []
        _users = self.__getwatchers(foirequest, requesttype) + self.__getassignees(foirequest, requesttype)
        for user in _users:
            if self.__isduplicate(user, notificationusers) == False:
                notificationusers.append(user)
        return notificationusers
    
    
    def __isduplicate(self, notificationuser, users):
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
        return 0
    
    
    def __getnotificationusertypeid(self, notificationusertype):
        if notificationusertype == "Watcher":
            return 1
        elif notificationusertype == "Assignee":
            return 2
        return 0