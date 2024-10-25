from request_api.models.OpenInfoPublicationStauses import OpenInfoPublicationStatuses
from request_api.models.OpenInformationExemptions import OpenInformationExemptions
from request_api.models.OpenInformationStatuses import OpenInformationStatuses
from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.models.FOIMinistryRequests import FOIMinistryRequest

class openinfoservice:
    """ OpenInformation service
    This service class manages all CRUD operations related to open information
    """
    def getopeninfostatuses (self):
        return OpenInformationStatuses.getallstatuses()

    def getopeninfopublicationstatuses (self):
        return OpenInfoPublicationStatuses.getallpublicationstatuses()

    def getopeninfoexemptions (self):
        return OpenInformationExemptions.getallexemptions()
    
    def getcurrentfoiopeninforequest(self, foiministryrequestid):
       return FOIOpenInformationRequests().getcurrentfoiopeninforequest(foiministryrequestid)
    
    def createopeninforequest(self, foiopeninforequest, userid, foiministryrequestid):
        version = FOIMinistryRequest.getversionforrequest(foiopeninforequest["foiministryrequest_id"])
        foiopeninforequest['foiministryrequestversion_id'] = version
        foiopeninforequest['foiministryrequest_id'] = foiministryrequestid
        result = FOIOpenInformationRequests().createopeninfo(foiopeninforequest, userid)
        return result

    def updateopeninforequest(self, foiopeninforequest, userid, foiministryrequestid):
        prev_foiopeninforequest = self.getfoiopeninforequest_by_foiministryrequestid(foiopeninforequest["foiministryrequest_id"])
        foiministryrequestversion = FOIMinistryRequest.getversionforrequest(foiopeninforequest["foiministryrequest_id"])
        foiopeninforequest['foiministryrequestversion_id'] = foiministryrequestversion
        foiopeninforequest['foiministryrequest_id'] = foiministryrequestid
        foiopeninforequest['version'] = prev_foiopeninforequest["version"]
        foiopeninforequest["created_at"] = prev_foiopeninforequest["created_at"]
        foiopeninforequest["createdby"] = prev_foiopeninforequest["createdby"]
        result = FOIOpenInformationRequests().updateopeninfo(foiopeninforequest, userid)
        deactivateresult = None
        if result.success == True:
            foiopeninfoid = result.args[0]
            deactivateresult = FOIOpenInformationRequests().deactivatefoiopeninforequest(foiopeninfoid, userid, foiministryrequestid)
        if result and deactivateresult:
            return result
