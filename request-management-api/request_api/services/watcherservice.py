
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
    
    def createrawrequestwatcher(self, data, userid, usergroups):
        """Creates a watcher for a user with groups passed in for an unopened request.
        """
        version = FOIRawRequest.getversionforrequest(data["requestid"])
        if 'watchedbygroup' in data:
            return FOIRawRequestWatcher.savewatcher(data, version, userid)
        else:
            return FOIRawRequestWatcher.savewatcherbygroups(data, version, userid, self.__getwatchablegroups(usergroups))       

    
    def getrawrequestwatchers(self, requestid):
        """Retrieves all watchers associated with an unopened request.
        """
        return FOIRawRequestWatcher.getwatchers(requestid)
    
    
    def disablerawrequestwatchers(self, requestid, userid):
        """Remove an user from the watched list of an unopened request.
        """
        return FOIRawRequestWatcher.disablewatchers(requestid, userid)

    
    def createministryrequestwatcher(self, data, userid, usergroups):
        """Creates a watcher for a user with groups passed in for an opened request.
        """
        version = FOIMinistryRequest.getversionforrequest(data["ministryrequestid"])
        if 'watchedbygroup' in data:
            return FOIRequestWatcher.savewatcher(data, version, userid) 
        else:
            return FOIRequestWatcher.savewatcherbygroups(data, version, userid, self.__getwatchablegroups(usergroups))  
        
    
    def getministryrequestwatchers(self, ministryrequestid, isministrymember):
        """Retrieves all watchers associated with an opened request.
        """
        if isministrymember == True:
            return FOIRequestWatcher.getMinistrywatchers(ministryrequestid) 
        else:
            return FOIRequestWatcher.getNonMinistrywatchers(ministryrequestid)
    
    def getallministryrequestwatchers(self, ministryrequestid, isministryonly=False):
        ministrywatchers = FOIRequestWatcher.getMinistrywatchers(ministryrequestid)
        if isministryonly == False:
            return ministrywatchers + FOIRequestWatcher.getNonMinistrywatchers(ministryrequestid)
        return ministrywatchers 
    
        
    def disableministryrequestwatchers(self, ministryrequestid, userid):
        """Remove an user from the watched list of an opened request.
        """
        return FOIRequestWatcher.disablewatchers(ministryrequestid, userid)
    
    
    def __getwatchablegroups(self, groups):
        """Returns a list of filtered groups excluding black listed pattern.
        """
        watchablegroups = []
        for group in groups:
            if self.isexcludegroup(group) == False:
                watchablegroups.append(group)
        return watchablegroups  
               
    
    def isexcludegroup(self, input):
        """Identifies whether the given input group is present in excluded groups.
        """
        for group in self.__excludegrouppattern():
            if group in input.lower():
                return True
        return False
              
    
    def __excludegrouppattern(self):
        """Exclude KC groups matching the patterns listed.
        """
        return ["formsflow","realm","camunda"]
        
        
        