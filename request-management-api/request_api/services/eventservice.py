
from os import stat
from re import VERBOSE
from request_api.services.events.state import stateevent
from request_api.services.events.division import divisionevent
from request_api.services.events.oipc import oipcevent
from request_api.services.events.assignment import assignmentevent
from request_api.services.events.cfrdate import cfrdateevent
from request_api.services.events.comment import commentevent
from request_api.services.events.watcher import watcherevent
from request_api.services.events.legislativedate import legislativedateevent
from request_api.services.events.divisiondate import divisiondateevent
from request_api.services.events.oipcduedate import oipcduedateevent
from request_api.services.events.extension import extensionevent
from request_api.services.events.cfrfeeform import cfrfeeformevent
from request_api.services.events.attachment import attachmentevent
from request_api.services.events.payment import paymentevent
from request_api.services.events.email import emailevent
from request_api.services.events.section5pending import section5pendingevent
from request_api.models.default_method_result import DefaultMethodResult
from request_api.exceptions import BusinessException
from request_api.utils.enums import PaymentEventType
import time as timer

import json
from flask import current_app
class eventservice:
    """ FOI event management service

    """
    
    async def postevent(self, requestid, requesttype, userid, username, isministryuser,assigneename=''):
        self.posteventsync(requestid, requesttype, userid, username, isministryuser,assigneename)
    
    def posteventsync(self, requestid, requesttype, userid, username, isministryuser,assigneename=''):
        print("\n ..... postevent is triggered ...... \n")
        try: 
            stateeventresponse = stateevent().createstatetransitionevent(requestid, requesttype, userid, username)
            divisioneventresponse = divisionevent().createdivisionevent(requestid, requesttype, userid)
            assignmentresponse = assignmentevent().createassignmentevent(requestid, requesttype, userid, isministryuser,assigneename,username)           
            oipcresponse = oipcevent().createoipcevent(requestid, requesttype, userid)
            if stateeventresponse.success == False or divisioneventresponse.success == False or assignmentresponse.success == False or oipcresponse.success == False: 
                current_app.logger.error("FOI Notification failed for event for request= %s ; state response=%s ; division response=%s ; assignment response=%s ; oipc response=%s" % (requestid, stateeventresponse.message, divisioneventresponse.message, assignmentresponse.message, oipcresponse.message))
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
                extensioneventresponse = extensionevent().createextensionevent(ministryrequestid, extensionid, userid, username, event)
                if extensioneventresponse.success == False: 
                    current_app.logger.error("FOI Notification failed for event for extension= %s" % (extensionid))
        except BusinessException as exception:            
            self.__logbusinessexception(exception)

    def postreminderevent(self):
        try:
            cfreventresponse = cfrdateevent().createdueevent() 
            legislativeeventresponse = legislativedateevent().createdueevent()   
            divisioneventresponse = divisiondateevent().createdueevent()   
            oipceventresponse = oipcduedateevent().createdueevent() 
            paymentremindereventresponse = paymentevent().createpaymentreminderevent()
            section5pendingresponse = section5pendingevent().createdueevent()            
            if cfreventresponse.success == False or legislativeeventresponse.success == False or divisioneventresponse.success == False or paymentremindereventresponse.success == False or section5pendingresponse == False or oipceventresponse == False:
                current_app.logger.error("FOI Notification failed for reminder event response=%s ; legislative response=%s ; division response=%s ; payment response=%s ; section5pending response=%s ; oipcduereminder response=%s" % (cfreventresponse.message, legislativeeventresponse.message, divisioneventresponse.message, paymentremindereventresponse.message, section5pendingresponse.message, oipceventresponse.message))
                return DefaultMethodResult(False,'Due reminder notifications failed',cfreventresponse.identifier)
            return DefaultMethodResult(True,'Due reminder notifications created',cfreventresponse.identifier)
        except BusinessException as exception:            
            self.__logbusinessexception(exception)
       
    async def postcommentevent(self, commentid, requesttype, userid, isdelete=False, existingtaggedusers=False):
        try:
            commentresponse = commentevent().createcommentevent(commentid, requesttype, userid, isdelete, existingtaggedusers)
            if commentresponse.success == False :
                current_app.logger.error("FOI Notification failed for comment event=%s" % (commentresponse.message))     
                return DefaultMethodResult(False,'Comment notifications failed',commentresponse.identifier)
            return DefaultMethodResult(True,'Comment notifications created',commentresponse.identifier)
        except BusinessException as exception:            
            self.__logbusinessexception(exception)
    
    def posteventforwatcher(self, requestid, request, requesttype, userid, username):
        try:
            if request['isrestricted']:
                watcherresponse = watcherevent().createwatchereventforrestricted(requestid, request, requesttype, userid, username)
            else:
                watcherresponse = watcherevent().createwatcherevent(requestid, request, requesttype, userid, username)
            if watcherresponse.success == False: 
                current_app.logger.error("FOI Notification failed for event for request= %s ; watcher response=%s" % (requestid, watcherresponse.message))
        except BusinessException as exception:            
            self.__logbusinessexception(exception)


    async def posteventforsanctioncfrfeeform(self, ministryrequestid, userid, username):
        self.__posteventforsanctioncfrfeeform(ministryrequestid, userid, username)
    
    async def posteventforcfrfeeform(self, ministryrequestid, userid, username):
        try:
            feewaivercommentresponse, refundcommentresponse= cfrfeeformevent().createeventforupdatedamounts(ministryrequestid, userid, username)                
            if feewaivercommentresponse.success == False or refundcommentresponse.success == False: 
                current_app.logger.error("FOI Comment failed for amount update event for CFRFEEFORM= %s" % (ministryrequestid))
        except BusinessException as exception:            
            self.__logbusinessexception(exception)

    async def postpaymentevent(self, requestid, paymenteventtype = PaymentEventType.paid.value):
        try:
            paymeneteventresponse = paymentevent().createpaymentevent(requestid, paymenteventtype)
            if paymeneteventresponse.success == False:
                current_app.logger.error("FOI Notification failed for payment event for request= %s ; event response=%s" % (requestid, paymeneteventresponse.message))
        except BusinessException as exception:
            self.__logbusinessexception(exception)

    def posteventforemailfailure(self, ministryrequestid, requesttype, stage, reason, userid):
        try:
            emaileventresponse = emailevent().createemailevent(ministryrequestid, requesttype, stage, reason, userid)
            if emaileventresponse.success == False: 
                    current_app.logger.error("FOI Notification failed for email event = %s" % (emaileventresponse))
        except BusinessException as exception:            
            self.__logbusinessexception(exception) 

    def postpaymentexpiryevent(self, ministryrequestid):
        try:
            paymeneteventresponse = paymentevent().createpaymentexpiredevent(ministryrequestid)
            if paymeneteventresponse.success == False:
                current_app.logger.error("FOI Expiry Notification failed for payment event for request= %s ; event response=%s" % (ministryrequestid, paymeneteventresponse.message))
            return paymeneteventresponse
        except BusinessException as exception:
            self.__logbusinessexception(exception)

    def __logbusinessexception(self, exception):
        current_app.logger.error("%s,%s" % ('FOI Comment Notification Error', exception.message))
    
    def __posteventforsanctioncfrfeeform(self, ministryrequestid, userid, username):
        try:           
            cfrfeeeventresponse = cfrfeeformevent().createstatetransitionevent(ministryrequestid, userid, username)
            if cfrfeeeventresponse.success == False: 
                current_app.logger.error("FOI Notification failed for event for CFRFEEFORM= %s" % (ministryrequestid))
        except BusinessException as exception:            
            self.__logbusinessexception(exception)