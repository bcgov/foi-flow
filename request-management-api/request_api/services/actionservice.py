
from os import stat
from request_api.services.external.dmnservice import dmnservice


class actionservice:
    """ FOI action alias state management service

    This service class interacts with camunda to retrieve the possible actions.

    """
    
    def getActionByTypeAndStatus(self, requestType, status):
        return dmnservice().evaluateAction(requestType, status) 
            
    