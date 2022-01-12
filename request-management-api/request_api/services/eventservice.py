
from os import stat
from re import VERBOSE
from request_api.services.events.state import stateevent
from request_api.services.events.division import divisionevent
from request_api.services.events.assignment import assignmentevent
from request_api.models.default_method_result import DefaultMethodResult
from request_api.exceptions import BusinessException
import json
from flask import current_app

class eventservice:
    """ FOI event management service

    """
    async def postevent(self, requestid, requesttype, userid, username, isministryuser):
        try: 
            stateeventresponse = stateevent().createstatetransitionevent(requestid, requesttype, userid, username)
            divisioneventresponse = divisionevent().createdivisionevent(requestid, requesttype, userid)
            assignmentresponse = assignmentevent().createassignmentevent(requestid, requesttype, userid, isministryuser)
            if stateeventresponse.success == False or divisioneventresponse.success == False or assignmentresponse.success == False: 
                current_app.logger.error("FOI Notification failed for event for request= %s ; state response=%s ; division response=%s ; assignment response=%s" % (requestid, stateeventresponse.message, divisioneventresponse.message, assignmentresponse.message))
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('FOI Notification Error', exception.message))
            
    
          
