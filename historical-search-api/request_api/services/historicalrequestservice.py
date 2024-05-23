
from os import stat
from request_api.models.FOIAssignees import FOIAssignee

class historicalrequestservice:
    """ FOI Assignee management service

    This service class interacts with Keycloak and returns eligible groups and members based on the state of application.

    """
    
    def gethistoricalrequest(self, requestid):
        
                
