
from os import stat
from re import VERBOSE
import json
import os
from notification_api.dao.models.NotificationTypes import NotificationType
from notification_api.dao.models.NotificationUserTypes import NotificationUserType
notificationuserfile = open('common/notificationusertypes.json', encoding="utf8")
notificationusertypes_cache = json.load(notificationuserfile)

notificationfile = open('common/notificationtypes.json', encoding="utf8")
notificationtypes_cache = json.load(notificationfile)

class notificationconfig:
    """ Notfication config

    """
    def getnotificationtype(self, notificationtype):        
        notificationid = NotificationType().getid(notificationtype)
        if notificationid is not None:
            return notificationid
    
    def getnotificationusertype(self, notificationusertype):
        notificationuserid = NotificationUserType().getid(notificationusertype)
        if notificationuserid is not None:
            return notificationuserid
 
    
    # This method is used to get the notification user type label
    # It first tries to get the notification user type label from the cache
    # If it is not found in the cache, it fetches it from the DB
    def getnotificationusertypelabel(self, notificationusertype):
        notificationusertype_format = notificationusertype.replace(" ", "").lower()
        if notificationusertype_format in notificationusertypes_cache:
            return notificationusertypes_cache[notificationusertype_format]['notificationusertypelabel']
        else:
            print("Notification user type not found in json. Fetching from DB", notificationusertype)
            notificationusertypeobj = self.getnotificationusertype(notificationusertype)
            if notificationusertypeobj is not None:
                return notificationusertypeobj['notificationusertypelabel']
            return None
    
    def getnotificationusertypeidbylabel(self, label):
        notificationuserid = NotificationUserType().getidbylabel(label)
        if notificationuserid is not None:
            return notificationuserid
    
    
    def getnotificationdays(self):
        if 'FOI_NOTIFICATION_DAYS' in os.environ and os.getenv('FOI_NOTIFICATION_DAYS') != '':
            return os.getenv('FOI_NOTIFICATION_DAYS')
        else:
            return str(14)
    
    def getmutenotifications(self):
        if 'MUTE_NOTIFICATION' in os.environ and os.getenv('MUTE_NOTIFICATION') != '':
            return json.loads(os.getenv('MUTE_NOTIFICATION'))
        else:
            return {}