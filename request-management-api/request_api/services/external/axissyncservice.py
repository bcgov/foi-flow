import requests
import os
from enum import Enum
from request_api.services.programareaservice import programareaservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.default_method_result import DefaultMethodResult
import more_itertools
from datetime import datetime as datetime2

class axissyncservice:

    BATCH_SIZE = int(os.getenv('AXISSYNC_BATCH_SIZE', 100))

    def syncpagecounts(self, bcgovcode, requesttype='personal'):
        programeara = programareaservice().getprogramareabyiaocode(bcgovcode)
        requests = FOIMinistryRequest.getrequest_by_pgmarea_type(programeara['programareaid'], requesttype)
        for batch in list(more_itertools.batched(requests, self.BATCH_SIZE)):
            batchedrequests = list(batch)
            axisids = self.__getaxisids(batchedrequests)
            #Fetch pagecount from axis : Begin
            
            #Fetch pagecount from axis : End
            response = FOIMinistryRequest.bulk_update_axispagecount(self.updatepagecount(batchedrequests, {}))
            if response.success == False:
                print("batch update failed for ids=", axisids)
        
        return DefaultMethodResult(True,'Batch execution completed', bcgovcode)
            
    def updatepagecount(self, requests, axisresponse):
        for entry in requests:
            axisrequestid = entry["axisrequestid"]
            entry["updatedby"] = 'System'
            entry["updated_at"] = datetime2.now()
            entry["axispagecount"] = axisresponse[axisrequestid] if axisrequestid in axisresponse else entry["axispagecount"]
        return requests


    def __getaxisids(self, requests):
        return [entry['axisrequestid'] for entry in requests]
