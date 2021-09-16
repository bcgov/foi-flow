
from os import stat
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIRawRequests import FOIRawRequest

class auditservice:
    """ FOI audit management service

    This service class interacts with datastore to retrive the audit of changes.

    """
    
    def getAuditforField(self, type, id, field):
        if field == "description":
             return self.getAuditForDescription(type, id)
        else:
            return None
        
        
    def getAuditForDescription(self, type, id):     
        _alldescriptions = []   
        if type == "ministryrequest":
            ministryRsp = self._getAuditFromMinistryRequest(id)
            _alldescriptions =  self._getAuditFromRawRequest(type, ministryRsp['foirequestid']) +  ministryRsp['audit'] 
        else:
            _alldescriptions =  self._getAuditFromRawRequest(type, id)     
        #Filter summary of changes
        datasummary=[]
        _data = None
        for entry in _alldescriptions:
            if _data != entry['description']:
                datasummary.append({"description": entry['description'], "fromDate": entry['fromdate'], "toDate": entry['todate'], "createdAt": entry['createdat'], "createdBy": entry['createdby'], "status": entry['status']})
            _data = entry['description']
        return  datasummary[::-1]
    
    
    def _getAuditFromMinistryRequest(self, id):
        _ministrydescriptions = []
        ministryrecords  = FOIMinistryRequest().getrequestById(id) 
        foirequestid = 0 
        for entry in ministryrecords:
            foirequestid = entry['foirequest_id']
            _ministrydescriptions.append({"description": entry['description'], "fromdate": entry['recordsearchfromdate'], "todate": entry['recordsearchtodate'], "createdat": entry['created_at'], "createdby": entry['assignedto'], "status": entry['requeststatus.name']})
        return {"foirequestid" :foirequestid  , "audit":_ministrydescriptions}
    
    def _getAuditFromRawRequest(self, type, id):
        if type == "ministryrequest":
            requestrecord  = FOIRequest().getrequest(id)
            rawRequestId= requestrecord['foirawrequestid']
        else:
            rawRequestId= id
        return FOIRawRequest().getDescriptionSummaryById(rawRequestId) 
        
            
    