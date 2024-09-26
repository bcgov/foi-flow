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
    
    def getfoiopeninforequest_by_foiministryrequestid(self):
        pass
    
    def createopeninforequest(self, foiopeninforequest, userid):
        version = FOIMinistryRequest.getversionforrequest(foiopeninforequest["foiministryrequest_id"])
        foiopeninforequest['foiministryrequestversion_id'] = version
        result = FOIOpenInformationRequests.createopeninfo(foiopeninforequest, userid)
        return result

    def updateopeninforequest(self, foiopeninforequest, userid):
        prev_foiopeninforequest = self.getfoiopeninforequest_by_foiministryrequestid(foiopeninforequest["foiministryrequest_id"])
        foiministryrequestversion = FOIMinistryRequest.getversionforrequest(foiopeninforequest["foiministryrequest_id"])
        foiopeninforequest['foiministryrequestversion_id'] = foiministryrequestversion
        foiopeninforequest['version'] = prev_foiopeninforequest["version"]
        foiopeninforequest["created_at"] = prev_foiopeninforequest["created_at"]
        foiopeninforequest["createdby"] = prev_foiopeninforequest["createdby"]
        result = FOIOpenInformationRequests.updateopeninfo(foiopeninforequest, userid)
        if result.success:
            pass #DEACTIVATE PREVIOUS FOIOPENINFO REQUEST isactive=False
        return result
