
from os import stat
from re import VERBOSE
from request_api.services.commons.duecalculator import duecalculator
from request_api.services.notificationservice import notificationservice
from request_api.services.commentservice import commentservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestComments import FOIRequestComment
from request_api.models.NotificationTypes import NotificationType
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
import time as t

class cfrdateevent(duecalculator):
    """ FOI Event management service

    """
    def createdueevent(self):
        try: 
            _today = self.gettoday()
            notificationservice().dismissremindernotification("ministryrequest", self.__notificationtype()) 

            ca_holidays = self.getholidays()
            _upcomingdues = FOIMinistryRequest.getupcomingcfrduerecords()
            notificationtype = NotificationType().getnotificationtypeid(self.__notificationtype())
            for entry in _upcomingdues:
                _duedate = self.formatduedate(entry['cfrduedate']) 
                message = None
                if  _duedate == _today:                
                    message = self.__todayduemessage()   
                elif  self.getpreviousbusinessday(entry['cfrduedate'],ca_holidays) == _today:
                    message = self.__upcomingduemessage(_duedate)   
                self.__createnotification(message,entry['foiministryrequestid'], notificationtype)
                self.__createcomment(entry, message)
            return DefaultMethodResult(True,'CFR reminder notifications created',_today)
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('CFR reminder Notification Error', exception.message))
            return DefaultMethodResult(False,'CFR reminder notifications failed',_today)     
        
    def __createnotification(self, message, requestid, notificationtype):
        if message is not None: 
            return notificationservice().createremindernotification({"message" : message}, requestid, "ministryrequest", notificationtype, self.__defaultuserid())
        
    def __createcomment(self, entry, message):
        if message is not None: 
            _comment = self.__preparecomment(entry, message)
            return commentservice().createcomments(_comment, self.__defaultuserid(), 2)
    
    def __preparecomment(self, foirequest, message):
        _comment = dict()
        _comment['comment'] = message
        _comment['ministryrequestid'] = foirequest["foiministryrequestid"]
        _comment['version'] = foirequest["version"]
        _comment['taggedusers'] = None
        _comment['parentcommentid'] = None
        return _comment
                    
    def __upcomingduemessage(self, duedate):
        return 'Call for Records due on ' + parse(str(duedate)).strftime("%Y %b %d").upper()
   
    def __todayduemessage(self):
        return 'Call for Records due Today'
    
    def __notificationtype(self):
        return "CFR Due Reminder"
    
    def __defaultuserid(self):
        return "System"