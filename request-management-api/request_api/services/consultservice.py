
from os import stat
from re import VERBOSE
from request_api.models.FOIMinistryRequestConsults import FOIMinistryRequestConsults
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.ProgramAreas import ProgramArea
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.services.requestservice import requestservice
import json
class consultservice:
    """ FOI consult management service
    """
    
    def getconsultrequests(self, ministryrequestid):
        """Retrieves all consults associated with an opened request."""
        created_consults = FOIMinistryRequestConsults().getinternalconsults(ministryrequestid)

        enriched_consults = []
        for consult in created_consults:
            programarea = ProgramArea.getprogramareabyId(consult['programareaid'])
            status = FOIRequestStatus.getrequeststatusbyId(consult['requeststatusid'])

            enriched_consults.append({
                "id": consult['foiministryrequestconsultid'],
                "fileNumber": consult['filenumber'],
                "consultAssignedTo": consult['consultassignedto'],
                "consultDueDate": consult['consultduedate'],
                "programAreaId": consult['programareaid'],
                "programAreaName": programarea['name'] if programarea else None,
                "requestStatusId": consult['requeststatusid'],
                "requestStatusName": status['name'] if status else None,
                "consultTypeId": consult['consulttypeid'],
                "subjectCode": consult['consultsubjectcode'],
                "created_at": consult['created_at'],
            })

        return enriched_consults
    
    def createconsultrequest(self, foiconsult, userid, foiministryrequestid, assigneedata):
        """Create the consult request."""
        foiministryrequest = FOIMinistryRequest().getrequestbyministryrequestid(foiministryrequestid)
        for consult in foiconsult:
            consult['foiMinistryRequestVersionId'] = foiministryrequest['version']
            consult['foiMinistryRequestId'] = foiministryrequestid
            consult['requeststatusid'] = foiministryrequest['requeststatus.requeststatusid']
        created_consults = FOIMinistryRequestConsults().createconsults(foiconsult, userid, assigneedata)


        enriched_consults = []
        for consult in created_consults:
            programarea = ProgramArea.getprogramareabyId(consult.programareaid)
            status = FOIRequestStatus.getrequeststatusbyId(consult.requeststatusid)
            enriched_consults.append({
                "id": consult.foiministryrequestconsultid,
                "fileNumber": consult.filenumber,
                "consultAssignedTo": consult.consultassignedto,
                "consultDueDate": consult.consultduedate,
                "programAreaId": consult.programareaid,
                "programAreaName": programarea['name'] if programarea else None,
                "requestStatusId": consult.requeststatusid,
                "requestStatusName": status['name'] if status else None,
                "consultTypeId": consult.consulttypeid,
                "subjectCode": consult.consultsubjectcode,
                "created_at": consult.created_at,
            })

        return enriched_consults
    
    def updateconsultrequest(self, foiconsult, userid, foiministryrequestid):
        """Create/Updates the consult request."""
        foiministryrequestversion = FOIMinistryRequest().getversionforrequest(foiministryrequestid)
        foiconsult['foiMinistryRequestVersionId'] = foiministryrequestversion
        foiconsult['foiMinistryRequestId'] = foiministryrequestid
        result = FOIMinistryRequestConsults().updateconsults(foiconsult, userid)
        return None
    
    def getoriginalrequestDetailsByAxisRequestId(self, axisrequestid):
        """Get the request details based on axisrequestid."""
        foiministryrequest = FOIMinistryRequestConsults().getoriginalrequestDetailsByAxisRequestId(axisrequestid)
        if foiministryrequest:
            result = requestservice().getrequestdetails(foiministryrequest['foirequest_id'],foiministryrequest['foiministryrequestid'])
        else:
            result = None    
        return result