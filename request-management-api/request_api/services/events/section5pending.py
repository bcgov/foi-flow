from os import stat
from re import VERBOSE
from request_api.services.commons.duecalculator import duecalculator
from request_api.services.notificationservice import notificationservice
from request_api.services.commentservice import commentservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.default_method_result import DefaultMethodResult
from enum import Enum
from request_api.exceptions import BusinessException
from datetime import datetime 
from flask import current_app
from dateutil.parser import parse

class section5pendingevent(duecalculator):
    """ FOI Event management service for section 5 pending state
    """
    
    def createdueevent(self):
        try: 
            _today = self.gettoday()
            notificationservice().dismissremindernotification("rawrequest", self.__notificationtype())
            section5pendings = FOIRawRequest.getlatestsection5pendings()
            for entry in section5pendings:
                duedate = self.formatduedate(entry['duedate'])
                message = None
                if  _today == duedate:                
                    message = self.__passeddueremindermessage()
                self.__createnotification(message, entry['requestid'])
                self.__createcomment(entry, message)
            return DefaultMethodResult(True,'Section 5 Pending passed due notification created',_today)
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Section 5 Pending passed due notification Error', exception.message))
            return DefaultMethodResult(False,'Section 5 Pending passed due notification failed',_today)     
        
    def __createnotification(self, message, requestid):
        if message is not None: 
            return notificationservice().createremindernotification({"message" : message}, requestid, "rawrequest", self.__notificationtype(), self.__defaultuserid())
        
    def __createcomment(self, entry, message):
        if message is not None: 
            _comment = self.__preparecomment(entry, message)
            return commentservice().createrawrequestcomment(_comment, self.__defaultuserid(), 2)
    
    def __preparecomment(self, foirequest, message):
        _comment = dict()
        _comment['comment'] = message
        _comment['requestid'] = foirequest["requestid"]
        _comment['version'] = foirequest["version"]
        _comment['taggedusers'] = None
        _comment['parentcommentid'] = None
        return _comment
                    
    def __passeddueremindermessage(self):
        return "10 business days has passed awaiting section 5, you can consider closing the request as abandoned"
    
    def __notificationtype(self):
        return "Section 5 Pending Reminder"
    
    def __defaultuserid(self):
        return "System"
