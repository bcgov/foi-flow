from request_api.models.OpenInfoPublicationStauses import OpenInfoPublicationStatuses
from request_api.models.OpenInformationExemptions import OpenInformationExemptions
from request_api.models.OpenInformationStatuses import OpenInformationStatuses

class openinfoservice:
    """ OpenInformation service
    """
    def getopeninfostatuses (self):
        return OpenInformationStatuses.getallstatuses()

    def getopeninfopublicationstatuses (self):
        return OpenInfoPublicationStatuses.getallpublicationstatuses()

    def getopeninfoexemptions (self):
        return OpenInformationExemptions.getallexemptions()