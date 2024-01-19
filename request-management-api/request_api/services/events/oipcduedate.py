
from os import stat
from re import VERBOSE
from request_api.services.commentservice import commentservice
from request_api.services.commons.duecalculator import duecalculator
from request_api.services.notificationservice import notificationservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.NotificationTypes import NotificationType
import json
from request_api.models.default_method_result import DefaultMethodResult
from request_api.exceptions import BusinessException
from dateutil.parser import parse
from flask import current_app

class oipcduedateevent(duecalculator):
    """ FOI OIPC Due Date Event management service
    """

    
    def createdueevent(self):
        try: 
            _today = self.gettoday()
            notificationservice().dismissremindernotification("ministryrequest", self.__notificationtype())            
            ca_holidays = self.getholidays()
            _upcomingdues = FOIMinistryRequest.getupcomingoipcduerecords()
            for entry in _upcomingdues:
                _duedate = self.formatduedate(entry['duedate'])
                message = None
                if  _duedate == _today:                
                    message = self.__todayduemessage(entry)     
                elif  self.getpreviousbusinessday(entry['duedate'],ca_holidays) == _today:
                    message = self.__upcomingduemessage(entry)
                elif  self.getpreviousbusinessday_by_n(entry['duedate'],ca_holidays, 2) == _today:
                    message = self.__upcomingduemessage(entry)
                self.__createnotification(message,entry['foiministryrequestid'])
                self.__createcomment(entry, message)
            return DefaultMethodResult(True,'OIPC reminder notifications created',_today)
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('OIPC reminder Notification Error', exception.message))
            return DefaultMethodResult(False,'OIPC reminder notifications failed',_today)

    def __createnotification(self, message, requestid):
        if message is not None: 
            notificationtype = NotificationType().getnotificationtypeid(self.__notificationtype())
            return notificationservice().createnotification({"message" : message}, requestid, "ministryrequest", notificationtype, self.__defaultuserid(), False)
        
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

    def __upcomingduemessage(self, data):
        return 'OIPC Inquiry Order '+data['orderno'] +' compliance date due on ' + parse(str(data['duedate'])).strftime("%Y %b %d").upper()  

    def __todayduemessage(self, data):
        return 'OIPC Inquiry Order '+data['orderno'] +' compliance due Today'

    def __notificationtype(self):
        return "OIPC Due Reminder"

    def __defaultuserid(self):
        return "System"       