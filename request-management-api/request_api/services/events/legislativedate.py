
from os import stat
from re import VERBOSE
from request_api.services.notifications.duecalculator import duecalculator
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
import json
from request_api.models.default_method_result import DefaultMethodResult
from enum import Enum
from request_api.exceptions import BusinessException
from datetime import datetime 
import holidays
import maya
import os
from flask import current_app
from dateutil.parser import parse

class legislativedateevent(duecalculator):
    """ FOI Event management service

    """
           
    def createdueevent(self):
        try: 
            _today = self.gettoday()
            notificationservice().dismissremindernotification("ministryrequest", self.__notificationtype())            
            ca_holidays = self.getholidays()
            _upcomingdues = FOIMinistryRequest.getupcominglegislativeduerecords()
            for entry in _upcomingdues:
                _duedate = self.formatduedate(entry['duedate'])
                message = None
                if  _duedate == _today:                
                    message = self.__todayduemessage()     
                elif  self.getpreviousbusinessday(entry['duedate'],ca_holidays) == _today:
                    message = self.__upcomingduemessage(_duedate)
                self.__createnotification(message,entry['foiministryrequestid'])
            return DefaultMethodResult(True,'Legislative reminder notifications created',_today)
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Legislative reminder Notification Error', exception.message))
            return DefaultMethodResult(False,'Legislative reminder notifications failed',_today)
        
    def __createnotification(self, message, requestid):
        if message is not None: 
            return notificationservice().createnotification({"message" : message}, requestid, "ministryrequest", self.__notificationtype(), self.__defaultuserid(), None, False)
                    
    def __upcomingduemessage(self, duedate):
        return 'Legislative Due Date due on ' + parse(str(duedate)).strftime("%Y %b %d").upper()  
   
    def __todayduemessage(self):
        return 'Legislative Due Date is Today'
    
    def __notificationtype(self):
        return "Legislative Due Reminder"
    
    def __defaultuserid(self):
        return "System"         

