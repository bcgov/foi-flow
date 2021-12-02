
from os import stat
from re import VERBOSE
from request_api.services.events.state import stateevent
import json


class eventservice:
    """ FOI event management service

    """
    @classmethod    
    def postevent(self, requestid, requesttype):
        return stateevent().createstatetransitionevent(requestid, requesttype)
            
    
          
