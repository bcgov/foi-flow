
from os import stat
from re import VERBOSE
import json
import os
from notification_api.dao.models.NotificationTypes import NotificationType

class notificationconfig:
    """ Notfication config

    """
    
    def getnotificationtypeid(self, notificationtype):        
       
        if "IAO Assignment" in notificationtype:
            return 5   
        elif "Ministry Assignment" in notificationtype:
            return 6  
        else:
            notificationid = NotificationType().getid(notificationtype)
            if notificationid is not None:
                return notificationid
        return 0     
    
    def getnotificationusertypeid(self, notificationusertype):
        if notificationusertype.lower() == "watcher":
            return 1
        elif notificationusertype.lower() == "assignee" or "comment"  or "group members" in notificationusertype.lower():
            return 2
        elif notificationusertype.lower() == "comment user":
            return 3
        elif notificationusertype.lower() == "triggered user":
            return 4
        return 0
    
    def getnotificationdays(self):
        if 'FOI_NOTIFICATION_DAYS' in os.environ and os.getenv('FOI_NOTIFICATION_DAYS') != '':
            return os.getenv('FOI_NOTIFICATION_DAYS')
        else:
            return str(14)
    
    def getmutenotifications(self):
        if 'MUTE_NOTIFICATION' in os.environ:
            return json.loads(os.getenv('MUTE_NOTIFICATION'))
        else:
            return {}