
from os import stat
from re import VERBOSE
import json
import os
from request_api.models.NotificationTypes import NotificationType
from request_api.models.NotificationUserTypes import NotificationUserType
notificationuserfile = open('common/notificationusertypes.json', encoding="utf8")
notificationusertypes_cache = json.load(notificationuserfile)

notificationfile = open('common/notificationtypes.json', encoding="utf8")
notificationtypes_cache = json.load(notificationfile)

class notificationconfig:
    """ Notfication config

    """

    # This method is used to get the notification user type label
    # It first tries to get the notification user type label from the cache
    # If it is not found in the cache, it fetches it from the DB
    def getnotificationtypelabel(self, notificationtype):
        notificationtype_format = notificationtype.replace(" ", "").lower()
        if notificationtype_format in notificationtypes_cache:
            return notificationtypes_cache[notificationtype_format]['notificationtypelabel']
        else:
            print("Notification type not found in cache. Fetching from DB", notificationtype)
            id = NotificationType().getnotificationtypeid(notificationtype)
            if id is not None:
                return id['notificationtypelabel']
            return None
    
    def getnotificationtypeid(self, notificationtype):
        id = NotificationType().getnotificationtypeid(notificationtype)
        if id is not None:
            return id['notificationtypeid']
        return None

    # This method is used to get the notification user type label
    # It first tries to get the notification user type label from the cache
    # If it is not found in the cache, it fetches it from the DB
    def getnotificationusertypelabel(self, notificationusertype):
        notificationusertype_format = notificationusertype.replace(" ", "").lower()
        if notificationusertype_format in notificationusertypes_cache:
            return notificationusertypes_cache[notificationusertype_format]['notificationusertypelabel']
        else:
            print("Notification user type not found in cache. Fetching from DB", notificationusertype)
            id = NotificationUserType().getnotificationusertypesid(notificationusertype)
            if id is not None:
                return id['notificationusertypelabel']
            return None
    
    def getnotificationusertypeid(self, notificationusertype):
        id = NotificationUserType().getnotificationusertypesid(notificationusertype)
        if id is not None:
            return id['notificationusertypeid']
        return None
    
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