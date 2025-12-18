from os import stat
from re import VERBOSE
from request_api.services.commons.duecalculator import duecalculator
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

class divisiondateevent(duecalculator):
    """ FOI Event management service
    """

    def createdueevent(self):
        try: 
            _today = self.gettoday()
            notificationservice().dismissremindernotification("ministryrequest", self.__notificationtype())            
            ca_holidays = self.getholidays()
            _upcomingdues = FOIMinistryRequest.getupcomingdivisionduerecords()
            for entry in _upcomingdues:
                _duedate = self.formatduedate(entry['duedate'])
                message = None
                if  _duedate == _today:                
                    message = self.__todayduemessage(entry)     
                elif  self.getpreviousbusinessday(entry['duedate'],ca_holidays) == _today:
                    message = self.__upcomingduemessage(entry)
                self.__createnotification(message,entry['foiministryrequestid'])
            return DefaultMethodResult(True,'Division reminder notifications created',_today)
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Legislative reminder Notification Error', exception.message))
            return DefaultMethodResult(False,'Division reminder notifications failed',_today)

    def __createnotification(self, message, requestid):
        if message is not None: 
            return notificationservice().createnotification({"message" : message}, requestid, "ministryrequest", self.__notificationtype(), self.__defaultuserid(), False)

    def __upcomingduemessage(self, data):
        return self.__getformattedprefix(data)+ ' due on ' + parse(str(data['duedate'])).strftime("%Y %b %d").upper()  

    def __todayduemessage(self, data):
        return self.__getformattedprefix(data)+ ' due Today'

    def __getformattedprefix(self,data):
        _message = data['divisionname']
        if data['stageid'] == 5:
            _message += " records are"
        elif data['stageid'] == 7:
            _message += " harms are"    
        elif data['stageid'] == 9:
            _message += " sign off is"        
        return _message

    def __notificationtype(self):
        return "Division Due Reminder"

    def __defaultuserid(self):
        return "System"       