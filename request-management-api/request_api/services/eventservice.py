
from os import stat
from re import VERBOSE
from request_api.services.events.state import stateevent
from request_api.services.events.division import divisionevent
from request_api.models.default_method_result import DefaultMethodResult
from request_api.exceptions import BusinessException
import json
from flask import current_app

class eventservice:
    """ FOI event management service

    """
    async def postevent(self, requestid, requesttype, userid, username):
        try: 
            stateeventresponse = stateevent().createstatetransitionevent(requestid, requesttype, userid, username)
            divisioneventresponse = divisionevent().createdivisionevent(requestid, requesttype, userid)
            if stateeventresponse.success == False or divisioneventresponse.success == False: 
                current_app.logger.error("FOI Notification failed for event for request= %s ; state response=%s ; division response=%s" % (requestid, stateeventresponse.success, divisioneventresponse.success))
        except BusinessException as exception:            
            current_app.logger.error("%s,%s" % ('FOI Notification Error', exception.message))
            
    
          
