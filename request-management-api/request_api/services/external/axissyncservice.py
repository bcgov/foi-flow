import requests
import os
from enum import Enum
from request_api.services.programareaservice import programareaservice
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.default_method_result import DefaultMethodResult
import more_itertools
from datetime import datetime as datetime2
from request_api.services.external.keycloakadminservice import KeycloakAdminService
from flask import current_app
import json
class axissyncservice:

    AXIS_BASE_URL = os.getenv('AXIS_API_URL', None)
    DEFAULT_SYNC_BATCHSIZE = 250
    AXIS_SYNC_BATCHSIZE = int(os.getenv('AXIS_SYNC_BATCHSIZE')) if os.getenv('AXIS_SYNC_BATCHSIZE') not in (None,'') else DEFAULT_SYNC_BATCHSIZE

    def syncpagecounts(self, axispgmrequests): 
        for entry in axispgmrequests:
            self.__syncpagecounts(entry["iaocode"], entry["requesttype"])
        return DefaultMethodResult(True,'Batch execution completed', axispgmrequests)

    def __syncpagecounts(self, iaocode, requesttype):
        programeara = programareaservice().getprogramareabyiaocode(iaocode)
        requests = FOIMinistryRequest.getrequest_by_pgmarea_type(programeara['programareaid'], requesttype)
        for batch in list(more_itertools.batched(requests, self.AXIS_SYNC_BATCHSIZE)):
            batchrequest = list(batch)
            axisids = self.__getaxisids(batchrequest)
            #Fetch pagecount from axis : Begin
            axis_pageinfo = self.axis_getpageinfo(axisids)
            #Fetch pagecount from axis : End
            if axis_pageinfo != {}:
                response = FOIMinistryRequest.bulk_update_axispagecount(self.updatepagecount(batchrequest, axis_pageinfo))
                if response.success == False:
                    print("batch update failed for ids=", axisids)
            else:
                print("axis page response is empty for ids=", axisids) 
        return DefaultMethodResult(True,'Batch execution completed for iaocode=%s | requesttype=%s', iaocode, requesttype)       
        

    def axis_getpageinfo(self, axis_payload):
        try:
            if self.AXIS_BASE_URL not in (None,''):
                access_token = KeycloakAdminService().get_token()
                axis_page_endpoint = f'{self.AXIS_BASE_URL}/api/requestspagecount'
                response = requests.post(
                    axis_page_endpoint,
                    headers={
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json'
                            },
                            timeout=current_app.config.get('CONNECT_TIMEOUT'),
                            data=json.dumps(axis_payload)
                    )
                response.raise_for_status()
                if response.status_code == 200:
                    return response.json()
            return {}
        except Exception as ex:
            print('Exception occured in fetching page details', ex)
            return {}

    def updatepagecount(self, requests, axisresponse):
        for entry in requests:
            axisrequestid = entry["axisrequestid"]
            entry["updatedby"] = 'System'
            entry["updated_at"] = datetime2.now()
            entry["axispagecount"] = axisresponse[axisrequestid]["requestpagepount"] if axisrequestid in axisresponse else entry["axispagecount"]
            entry["axislanpagecount"] = axisresponse[axisrequestid]["lanpagepount"] if axisrequestid in axisresponse else entry["axislanpagecount"]
        return requests


    def __getaxisids(self, requests):
        return [entry['axisrequestid'] for entry in requests]
    

