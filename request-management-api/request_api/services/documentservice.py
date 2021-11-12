
from os import stat
from re import VERBOSE
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
import json
from dateutil.parser import *
import datetime 


class documentservice:
    """ FOI watcher management service

    """
    @classmethod    
    def getministryrequestdocuments(self, ministryrequestid):
        version = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        return FOIMinistryRequestDocument.getdocuments(ministryrequestid, version[0])
    
     
    
