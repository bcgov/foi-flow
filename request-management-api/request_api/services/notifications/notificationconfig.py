
from os import stat
from re import VERBOSE
import json
import os

class notificationconfig:
    """ Notfication config

    """
    
    def getnotificationtypeid(self, notificationtype):
        if notificationtype == "State":
            return 1
        elif "IAO Assignment" in notificationtype:
            return 5   
        elif "Ministry Assignment" in notificationtype:
            return 6  
        elif notificationtype == "CFR Due Reminder":
            return 7
        elif notificationtype == "Legislative Due Reminder":
            return 8 
        elif "Comment" in notificationtype:
            return 3   
        return 0     
    
    def getnotificationusertypeid(self, notificationusertype):
        if notificationusertype.lower() == "watcher":
            return 1
        elif notificationusertype.lower() == "assignee":
            return 2
        elif notificationusertype.lower() == "tagged user":
            return 3
        elif notificationusertype.lower() == "comment user":
            return 4
        elif notificationusertype.lower() == "comment reply user":
            return 5
        return 0
    
    def getnotificationdays(self):
        if 'FOI_NOTIFICATION_DAYS' in os.environ and os.getenv('FOI_NOTIFICATION_DAYS') != '':
            return os.getenv('FOI_NOTIFICATION_DAYS')
        else:
            return str(14)    