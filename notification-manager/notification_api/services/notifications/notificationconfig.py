
from os import stat
from re import VERBOSE
import json
import os
from notification_api.dao.models.NotificationTypes import NotificationType
from notification_api.dao.models.NotificationUserTypes import NotificationUserType

class notificationconfig:
    """ Notfication config

    """
    
    def getnotificationtypeid(self, notificationtype):        
        notificationid = NotificationType().getid(notificationtype)
        if notificationid is not None:
            return notificationid
    
    def getnotficationusertypelabel(self, notificationusertype):
        notificationuserid = NotificationUserType().getid(notificationusertype)
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