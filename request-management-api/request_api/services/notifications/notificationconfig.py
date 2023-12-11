
from os import stat
from re import VERBOSE
import json
import os
from request_api.models.NotificationTypes import NotificationType
from request_api.models.NotificationUserTypes import NotificationUserType

class notificationconfig:
    """ Notfication config

    """

    def getnotificationtypelabel(self, notificationtype):
        id = NotificationType().getnotificationtypeid(notificationtype)
        if id is not None:
            return id['notificationtypelabel']
        return 0
    
    def getnotificationtypeid(self, notificationtype):
        id = NotificationType().getnotificationtypeid(notificationtype)
        if id is not None:
            return id['notificationtypeid']
        return 0

    def getnotificationusertypelabel(self, notificationusertype):
        print(notificationusertype)
        id = NotificationUserType().getnotificationusertypesid(notificationusertype)
        print(id)
        if id is not None:
            return id['notificationusertypelabel']
        return 0
    
    def getnotificationusertypeid(self, notificationusertype):
        print(notificationusertype)
        id = NotificationUserType().getnotificationusertypesid(notificationusertype)
        print(id)
        if id is not None:
            return id['notificationusertypeid']
        return 0
    
    def getnotificationdays(self):
        if 'FOI_NOTIFICATION_DAYS' in os.environ and os.getenv('FOI_NOTIFICATION_DAYS') != '':
            return os.getenv('FOI_NOTIFICATION_DAYS')
        else:
            return str(14)
    
    def getmutenotifications(self):
<<<<<<< HEAD
        if 'MUTE_NOTIFICATION' in os.environ and os.getenv('MUTE_NOTIFICATION') != '':
=======
        if 'MUTE_NOTIFICATION' in os.environ:
>>>>>>> 21ce0b5a5 (mute notifications for mcf #4548)
            return json.loads(os.getenv('MUTE_NOTIFICATION'))
        else:
            return {}