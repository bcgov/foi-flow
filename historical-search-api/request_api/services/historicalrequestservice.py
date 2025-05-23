
from os import stat
from request_api.models.factRequestDetails import factRequestDetails
from request_api.models.factRequestExtensions import factRequestExtensions

class historicalrequestservice:
    """ FOI Assignee management service

    This service class interacts with Keycloak and returns eligible groups and members based on the state of application.

    """
    
    def gethistoricalrequest(self, isiaorestictedmanager,requestid):
        return factRequestDetails.getrequestbyid(isiaorestictedmanager,requestid)
    
    def gethistoricalrequestdescriptionhistory(self, requestid):
        return factRequestDetails.getdescriptionhistorybyid(requestid)    
    
    def gethistoricalrequestextensions(self, requestid):
        return factRequestExtensions.getextensionsbyrequestid(requestid)
    
    def advancedsearch(self,isiaorestictedmanager:False, params={'usertype': 'iao', 'groups':None, 'page':1, 'size':10, 'sortingitem':[], 'sortingorder':[], 'requeststate':[], 'requeststatus':[], 'requesttype':[], 'requestflags':[], 'publicbody':[], 'daterangetype':None, 'fromdate':None, 'todate':None, 'search':None, 'keywords':[], 'userid':None}):
        return factRequestDetails.getadvancedsearchresults(isiaorestictedmanager,params)
                
