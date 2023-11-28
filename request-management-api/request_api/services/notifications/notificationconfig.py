
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
        elif notificationtype == "Extension":
            return 4 
        elif "IAO Assignment" in notificationtype:
            return 5   
        elif "Ministry Assignment" in notificationtype:
            return 6  
        elif notificationtype == "CFR Due Reminder":
            return 7
        elif notificationtype == "Legislative Due Reminder":
            return 8 
        elif notificationtype == "New User Comments":
            return 3   
        elif notificationtype == "Reply User Comments":
            return 9  
        elif notificationtype == "Tagged User Comments":
            return 10 
        elif notificationtype == "CFR Fee Form":
            return 11  
        elif notificationtype == "Group Members":
            return 12        
        elif notificationtype == "Division Due Reminder":
            return 13
        elif notificationtype == "Watcher":
            return 14
        elif notificationtype == "User Assignment Removal":
            return 15
        elif notificationtype == "Email Failure":
            return 16 
        elif notificationtype == "Payment":
            return 17
        elif notificationtype == "Section 5 Pending Reminder":
            return 20             
        return 0     
    
    def getnotificationusertypeid(self, notificationusertype):
        if notificationusertype.lower() == "watcher":
            return 1
        elif notificationusertype.lower() == "assignee" or "comment"  or "group members" in notificationusertype.lower():
            return 2
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