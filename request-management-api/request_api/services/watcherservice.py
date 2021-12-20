
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
    def createrawrequestwatcher(self, data, userid, usergroups):
        version = FOIRawRequest.getversionforrequest(data["requestid"])
        if 'watchedbygroup' in data:
            return FOIRawRequestWatcher.savewatcher(data, version, userid)
        else:
            return FOIRawRequestWatcher.savewatcherbygroups(data, version, userid, self.getwatchablegroups(usergroups))

    @classmethod
    def getrawrequestwatchers(self, requestid):
        return FOIRawRequestWatcher.getwatchers(requestid)
    
    @classmethod
    def disablerawrequestwatchers(self, requestid, userid):
        return FOIRawRequestWatcher.disablewatchers(requestid, userid)

    @classmethod    
    def createministryrequestwatcher(self, data, userid, usergroups):
        version = FOIMinistryRequest.getversionforrequest(data["ministryrequestid"])
        if 'watchedbygroup' in data:
            return FOIRequestWatcher.savewatcher(data, version, userid) 
        else:
            return FOIRequestWatcher.savewatcherbygroups(data, version, userid, self.getwatchablegroups(usergroups))
        
        
    @classmethod
    def getministryrequestwatchers(self, ministryrequestid, isministrymember):
        if isministrymember == True:
            return FOIRequestWatcher.getMinistrywatchers(ministryrequestid) 
        else:
            return FOIRequestWatcher.getNonMinistrywatchers(ministryrequestid)
    
    @classmethod
    def disableministryrequestwatchers(self, ministryrequestid, userid):
        return FOIRequestWatcher.disablewatchers(ministryrequestid, userid)
    
    @classmethod
    def getwatchablegroups(self, groups):
        watchablegroups = []
        for group in groups:
            if self.isexcludegroup(group) == False:
                watchablegroups.append(group)
        return watchablegroups  
               
    @classmethod    
    def isexcludegroup(self, input):
        for group in self.excludegrouppattern():
            if group in input.lower():
                return True
        return False
              
    @classmethod    
    def excludegrouppattern(self):
        return ["formsflow","realm","camunda"]
        
        
        