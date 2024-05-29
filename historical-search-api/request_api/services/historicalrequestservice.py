
from os import stat
from request_api.models.factRequestDetails import factRequestDetails
from request_api.models.factRequestExtensions import factRequestExtensions

class historicalrequestservice:
    """ FOI Assignee management service

    This service class interacts with Keycloak and returns eligible groups and members based on the state of application.

    """
    
    def gethistoricalrequest(self, requestid):
        return factRequestDetails.getrequestbyid(requestid)
    
    def gethistoricalrequestdescriptionhistory(self, requestid):
        return factRequestDetails.getdescriptionhistorybyid(requestid)    
    
    def gethistoricalrequestextensions(self, requestid):
        return factRequestExtensions.getextensionsbyrequestid(requestid)
                
