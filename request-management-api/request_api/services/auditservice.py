
from os import stat
from request_api.auth import AuthHelper
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIRawRequests import FOIRawRequest
from datetime import datetime
from request_api.utils.enums import RequestType
import dateutil.parser
import maya
class auditservice:
    """ FOI audit management service

    This service class interacts with datastore to retrive the audit of changes.

    """
    
    def getauditforfield(self, type, id, field, isall=False):
        if field == "description":
            return self.__getauditfordescription(type, id, isall) 
        else:
            return None
        
        
    def __getauditfordescription(self, type, id, isall):     
        _alldescriptions = []   
        if type == "ministryrequest":
            ministryrsp = self.__getauditfromministryrequest(id)
            _alldescriptions =  self.__getauditfromrawrequest(type, ministryrsp['foirequestid']) +  ministryrsp['audit'] 
        else:
            _alldescriptions =  self.__getauditfromrawrequest(type, id)     
        #Filter summary of changes
        datasummary=[]
        _data, _startdate, _enddate = None, None, None
        if len(_alldescriptions) > 0:
            for entry in _alldescriptions:
                if isall == True or (isall == False and _data != entry['description'] or _startdate != entry['fromdate'] or _enddate != entry['todate']):
                    datasummary.append({"description": entry['description'], "fromDate": entry['fromdate'], "toDate": entry['todate'], "createdAt": entry['createdat'], "createdBy": entry['createdby'], "status": entry['status']})
                _data = entry['description']
                _startdate =  entry['fromdate']
                _enddate = entry['todate']
        return  datasummary[::-1]
    
    
    def __getauditfromministryrequest(self, id):
        _ministrydescriptions = []
        ministryrecords  = FOIMinistryRequest().getrequestById(id) 
        foirequestid = 0 
        for entry in ministryrecords:
            foirequestid = entry['foirequest_id']
            createdat =  maya.parse(entry['created_at']).datetime(to_timezone='America/Vancouver', naive=False).strftime('%Y-%m-%d %H:%M:%S')
            fromdate = datetime.fromisoformat(entry['recordsearchfromdate']).strftime("%Y-%m-%d") if entry['recordsearchfromdate'] is not None else None 
            todate = datetime.fromisoformat(entry['recordsearchtodate']).strftime("%Y-%m-%d") if entry['recordsearchtodate'] is not None else None
            _ministrydescriptions.append({"description": entry['description'], "fromdate": fromdate, "todate": todate, "createdat": createdat, "createdby": entry['createdby'], "status": entry['requeststatus.name']})
        return {"foirequestid" :foirequestid  , "audit":_ministrydescriptions}
    
    def __getauditfromrawrequest(self, type, id):
        _rawdescriptions = []
        if type == "ministryrequest":
            requestrecord  = FOIRequest().getrequest(id)
            rawrequestid= requestrecord['foirawrequestid']
        else:
            rawrequestid= id
        rawrecords = FOIRawRequest().getDescriptionSummaryById(rawrequestid) 
        
        
        for entry in rawrecords:
            createdat =  maya.parse(entry['createdat']).datetime(to_timezone='America/Vancouver', naive=False).strftime('%Y-%m-%d %H:%M:%S')
            fromdate =dateutil.parser.parse(entry['fromdate']).strftime('%Y-%m-%d') if entry['fromdate'] is not None else None 
            todate = dateutil.parser.parse(entry['todate']).strftime('%Y-%m-%d') if entry['todate'] is not None else None
            if AuthHelper.getusertype() == "iao":
                _rawdescriptions.append({"description": entry['description'], "fromdate": fromdate, "todate": todate, "createdat": createdat , "createdby": entry['createdby'], "status": entry['status']})        
            else:
                if requestrecord['requesttype'] == 'personal' or entry['ispiiredacted'] == True:
                    _rawdescriptions.append({"description": entry['description'], "fromdate": fromdate, "todate": todate, "createdat": createdat , "createdby": entry['createdby'], "status": entry['status']})            
        return _rawdescriptions
        
            
    