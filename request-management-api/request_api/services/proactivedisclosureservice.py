from request_api.models.FOIProactiveDisclosureRequests import FOIProactiveDisclosureRequests
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.auth import AuthHelper

class proactivedisclosureservice:
    """ Proactive Disclosure service
    This service class manages CRUD operations related to proactive disclosure
    """
    
    def getcurrentfoiproactiverequest(self, foiministryrequestid):
       return FOIProactiveDisclosureRequests().getcurrentfoiproactiverequest(foiministryrequestid)
    
    def updateproactivedisclosure(self, foiproactiverequest, userid, foiministryrequestid):
        foiministryrequestversion = FOIMinistryRequest().getversionforrequest(foiministryrequestid)
        proactive_disclosure_data = {
            "foiministryrequest_id": foiministryrequestid,
            "foiministryrequestversion_id": foiministryrequestversion
        }
        if "oipublicationstatus_id" in foiproactiverequest:
            proactive_disclosure_data["oipublicationstatus_id"] = foiproactiverequest["oipublicationstatus_id"]
        if "earliesteligiblepublicationdate" in foiproactiverequest:
            val = foiproactiverequest["earliesteligiblepublicationdate"]
            proactive_disclosure_data["earliesteligiblepublicationdate"] = val if val != "" else None
            # Auto-sync publicationdate from earliesteligiblepublicationdate when it changes
            if proactive_disclosure_data["earliesteligiblepublicationdate"]:
                proactive_disclosure_data["publicationdate"] = proactive_disclosure_data["earliesteligiblepublicationdate"]
        # Publicationdate always overrides the auto-synced value
        if "publicationdate" in foiproactiverequest:
            val = foiproactiverequest["publicationdate"]
            proactive_disclosure_data["publicationdate"] = val if val != "" else None
        if "proactivedisclosurecategoryid" in foiproactiverequest:
            proactive_disclosure_data["proactivedisclosurecategoryid"] = foiproactiverequest["proactivedisclosurecategoryid"]
        if "reportperiod" in foiproactiverequest:
            proactive_disclosure_data["reportperiod"] = foiproactiverequest["reportperiod"]    
        result = FOIProactiveDisclosureRequests().savefoiproactiverequest(proactive_disclosure_data, userid)
        if result.success:
            FOIProactiveDisclosureRequests.deActivateOldVersion(foiministryrequestid, userid)
        return result
