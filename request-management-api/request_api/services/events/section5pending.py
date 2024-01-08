from os import stat
from re import VERBOSE
from request_api.services.commons.duecalculator import duecalculator
from request_api.services.notificationservice import notificationservice
from request_api.services.commentservice import commentservice
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.NotificationTypes import NotificationType
from request_api.models.default_method_result import DefaultMethodResult
from enum import Enum
from request_api.exceptions import BusinessException
from request_api.utils.commons.datetimehandler import datetimehandler
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
            notificationtype = NotificationType().getnotificationtypeid(self.__notificationtype())
            for entry in section5pendings:
                _dateofstatechange = datetimehandler().formatdate(entry['created_at'])
                businessdayselapsed = self.getbusinessdaysbetween(_dateofstatechange)
                if businessdayselapsed >= 10 and self.isbusinessday(_today):
                    message = self.__passeddueremindermessage()
                    commentexists = False
                    existingcomments = commentservice().getrawrequestcomments(entry['requestid'])
                    for comment in existingcomments:
                        if comment['text'] == message: #checks if comment already exists
                            commentexists = True
                    if not commentexists:
                        self.__createcomment(entry, message)
                    self.__createnotification(message, entry['requestid'], notificationtype)
            return DefaultMethodResult(True,'Section 5 Pending passed due notification created',_today)
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('Section 5 Pending passed due notification Error', exception.message))
            return DefaultMethodResult(False,'Section 5 Pending passed due notification failed',_today)     
        
    def __createnotification(self, message, requestid, notificationtype):
        if message is not None: 
            return notificationservice().createremindernotification({"message" : message}, requestid, "rawrequest", notificationtype, self.__defaultuserid())
        
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
