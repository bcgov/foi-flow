
from os import stat
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIRawRequests import FOIRawRequest
from datetime import datetime

class auditservice:
    """ FOI audit management service

    This service class interacts with datastore to retrive the audit of changes.

    """
    
    def getAuditforField(self, type, id, field, groups,isAll=False):
        if field == "description":
            return self.getAuditForDescription(type, id, groups,isAll) 
        else:
            return None
        
        
    def getAuditForDescription(self, type, id, groups,isAll):     
        _alldescriptions = []   
        if type == "ministryrequest":
            ministryRsp = self._getAuditFromMinistryRequest(id)
            _alldescriptions =  self._getAuditFromRawRequest(type, ministryRsp['foirequestid'], groups) +  ministryRsp['audit'] 
        else:
            _alldescriptions =  self._getAuditFromRawRequest(type, id, groups)     
        #Filter summary of changes
        datasummary=[]
        _data, _startDate, _endDate = None, None, None
        if len(_alldescriptions) > 0:
            for entry in _alldescriptions:
                if isAll == True or (isAll == False and _data != entry['description'] or _startDate != entry['fromdate'] or _endDate != entry['todate']):
                    datasummary.append({"description": entry['description'], "fromDate": entry['fromdate'], "toDate": entry['todate'], "createdAt": entry['createdat'], "createdBy": entry['createdby'], "status": entry['status']})
                _data = entry['description']
                _startDate =  entry['fromdate']
                _endDate = entry['todate']
        return  datasummary[::-1]
    
    
    def _getAuditFromMinistryRequest(self, id):
        _ministrydescriptions = []
        ministryrecords  = FOIMinistryRequest().getrequestById(id) 
        foirequestid = 0 
        for entry in ministryrecords:
            foirequestid = entry['foirequest_id']
            createdat = datetime.fromisoformat(entry['created_at']).strftime("%Y-%m-%d %H:%M:%S") 
            fromdate = datetime.fromisoformat(entry['recordsearchfromdate']).strftime("%Y-%m-%d") if entry['recordsearchfromdate'] is not None else None 
            todate = datetime.fromisoformat(entry['recordsearchtodate']).strftime("%Y-%m-%d") if entry['recordsearchtodate'] is not None else None
            _ministrydescriptions.append({"description": entry['description'], "fromdate": fromdate, "todate": todate, "createdat": createdat, "createdby": entry['createdby'], "status": entry['requeststatus.name']})
        return {"foirequestid" :foirequestid  , "audit":_ministrydescriptions}
    
    def _getAuditFromRawRequest(self, type, id, groups):
        _rawdescriptions = []
        if type == "ministryrequest":
            requestrecord  = FOIRequest().getrequest(id)
            rawRequestId= requestrecord['foirawrequestid']
        else:
            rawRequestId= id
        rawrecords = FOIRawRequest().getDescriptionSummaryById(rawRequestId) 
        
        if 'Intake Team' in groups or 'Flex Team' in groups or 'Processing Team' in groups:
           _rawdescriptions =  rawrecords 
        else:
            for entry in rawrecords:
                if entry['ispiiredacted'] == True:
                    _rawdescriptions.append(entry)
        return _rawdescriptions
        
            
    