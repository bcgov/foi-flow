
from os import stat
from re import VERBOSE
from request_api.services.events.state import stateevent
from request_api.services.events.division import divisionevent
from request_api.services.events.assignment import assignmentevent
from request_api.services.events.cfrdate import cfrdateevent
from request_api.services.events.comment import commentevent
from request_api.services.events.legislativedate import legislativedateevent
from request_api.services.events.divisiondate import divisiondateevent
from request_api.services.events.extension import extensionevent
from request_api.models.default_method_result import DefaultMethodResult
from request_api.exceptions import BusinessException
import json
from flask import current_app
class eventservice:
    """ FOI event management service

    """
    
    async def postevent(self, requestid, requesttype, userid, username, isministryuser,assigneename=''):
        self.posteventsync(requestid, requesttype, userid, username, isministryuser,assigneename)
    
    def posteventsync(self, requestid, requesttype, userid, username, isministryuser,assigneename=''):
        try: 
            stateeventresponse = stateevent().createstatetransitionevent(requestid, requesttype, userid, username)
            divisioneventresponse = divisionevent().createdivisionevent(requestid, requesttype, userid)
            assignmentresponse = assignmentevent().createassignmentevent(requestid, requesttype, userid, isministryuser,assigneename,username)           
            if stateeventresponse.success == False or divisioneventresponse.success == False or assignmentresponse.success == False: 
                current_app.logger.error("FOI Notification failed for event for request= %s ; state response=%s ; division response=%s ; assignment response=%s" % (requestid, stateeventresponse.message, divisioneventresponse.message, assignmentresponse.message))
        except BusinessException as exception:            
            self.__logbusinessexception(exception)
 
    def posteventforextension(self, ministryrequestid, extensionid, userid, username, event):
        try:
            extensioneventresponse = extensionevent().createextensionevent(ministryrequestid, extensionid, userid, username, event)
            if extensioneventresponse.success == False: 
                current_app.logger.error("FOI Notification failed for event for extension= %s" % (extensionid))
        except BusinessException as exception:            
            self.__logbusinessexception(exception)
    
    def posteventforaxisextension(self, ministryrequestid, extensionids, userid, username, event):
        try:
            for extensionid in extensionids:
                extensioneventresponse = extensionevent().createaxisextensionevent(ministryrequestid, extensionid, userid, username, event)
                if extensioneventresponse.success == False: 
                    current_app.logger.error("FOI Notification failed for event for extension= %s" % (extensionid))
        except BusinessException as exception:            
            self.__logbusinessexception(exception)
            
    def postreminderevent(self):
        try:
            cfreventresponse = cfrdateevent().createdueevent() 
            legislativeeventresponse = legislativedateevent().createdueevent()   
            divisioneventresponse = divisiondateevent().createdueevent()   
            if cfreventresponse.success == False or legislativeeventresponse.success == False or divisioneventresponse.success == False:
                current_app.logger.error("FOI Notification failed for reminder event response=%s ; legislative response=%s ; division response=%s" % (cfreventresponse.message, legislativeeventresponse.message, divisioneventresponse.message,))     
                return DefaultMethodResult(False,'Due reminder notifications failed',cfreventresponse.identifier)
            return DefaultMethodResult(True,'Due reminder notifications created',cfreventresponse.identifier)
        except BusinessException as exception:            
            self.__logbusinessexception(exception)
       
    async def postcommentevent(self, commentid, requesttype, userid, isdelete=False):
        try:
            commentresponse = commentevent().createcommentevent(commentid, requesttype, userid, isdelete) 
            if commentresponse.success == False :
                current_app.logger.error("FOI Notification failed for comment event=%s" % (commentresponse.message))     
                return DefaultMethodResult(False,'Comment notifications failed',commentresponse.identifier)
            return DefaultMethodResult(True,'Comment notifications created',commentresponse.identifier)
        except BusinessException as exception:            
            self.__logbusinessexception(exception)
        
    def __logbusinessexception(self, exception):
        current_app.logger.error("%s,%s" % ('FOI Comment Notification Error', exception.message))