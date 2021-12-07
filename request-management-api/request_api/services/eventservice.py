
from os import stat
from re import VERBOSE
from request_api.services.events.state import stateevent
from request_api.services.events.division import divisionevent
from request_api.models.default_method_result import DefaultMethodResult

import json


class eventservice:
    """ FOI event management service

    """
    @classmethod    
    def postevent(self, requestid, requesttype):
        stateeventresponse = stateevent().createstatetransitionevent(requestid, requesttype)
        divisioneventresponse = divisionevent().createdivisionevent(requestid)
        if stateeventresponse.success == True and divisioneventresponse.success == True:
            return DefaultMethodResult(True,'Comment posted',requestid)
        else:
            return DefaultMethodResult(False,'Unable to post Comment',requestid)

            
    
          
