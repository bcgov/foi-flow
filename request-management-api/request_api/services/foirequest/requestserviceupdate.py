
from re import T
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.services.foirequest.requestservicebuilder import requestservicebuilder 

import json
class requestserviceupdate(requestservicebuilder):
    """ This class consolidates update of FOI request for actors: iao and ministry. 
    """

    def updaterequest(self,foirequestschema,foirequestid,userid):
        print("foirequestschema == ",foirequestschema)
        if self.isNotBlankorNone(foirequestschema,"wfinstanceid","main") == True:
            return FOIRequest.updateWFInstance(foirequestid, foirequestschema.get("wfinstanceid"), userid)
        if foirequestschema.get("selectedMinistries") is not None:
            allstatus = FOIRequestStatus().getrequeststatuses()
            updatedministries = []
            for ministry in foirequestschema.get("selectedMinistries"):
                for status in allstatus:
                    if ministry["status"] == status["name"]:
                        updatedministries.append({"filenumber" : ministry["filenumber"], "requeststatusid": status["requeststatusid"]})
            return FOIRequest.updateStatus(foirequestid, updatedministries, userid)
    
    def updateministryrequestduedate(self, ministryrequestid, duedate, userid):
        return FOIMinistryRequest().updateduedate(ministryrequestid, duedate, userid)