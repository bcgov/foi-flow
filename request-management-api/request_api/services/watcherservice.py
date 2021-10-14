
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestWatchers import FOIRequestWatcher
from request_api.models.FOIRawRequestWatchers import FOIRawRequestWatcher
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest

import json
class watcherservice:
    """ FOI watcher management service

    """
    @classmethod
    def createrawrequestwatcher(cls, data, userid):
        version = FOIRawRequest.getversionforrequest(data["requestid"])
        return FOIRawRequestWatcher.savewatcher(data, version, userid)

    @classmethod
    def getrawrequestwatchers(cls, requestid):
        return FOIRawRequestWatcher.getwatchers(requestid)
    
    @classmethod
    def disablerawrequestwatchers(cls, requestid, userid):
        return FOIRawRequestWatcher.disablewatchers(requestid, userid)

    @classmethod    
    def createministryrequestwatcher(cls, data, userid):
        version = FOIMinistryRequest.getversionforrequest(data["ministryrequestid"])
        return FOIRequestWatcher.savewatcher(data, version, userid) 
    
    @classmethod
    def getministryrequestwatchers(cls, ministryrequestid):
        return FOIRequestWatcher.getwatchers(ministryrequestid)
    
    @classmethod
    def disableministryrequestwatchers(cls, ministryrequestid, userid):
        return FOIRequestWatcher.disablewatchers(ministryrequestid, userid)