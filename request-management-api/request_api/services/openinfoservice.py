from request_api.models.OpenInfoPublicationStauses import OpenInfoPublicationStatuses
from request_api.models.OpenInformationExemptions import OpenInformationExemptions
from request_api.models.OpenInformationStatuses import OpenInformationStatuses

class openinfoservice:
    """ OpenInformation service
    """
    def getopeninfostatuses (self):
        OpenInformationStatuses.getallstatuses()

    def getopeninfopublicationstatuses (self):
        OpenInfoPublicationStatuses.getallpublicationstatuses()

    def getopeninfoexemptions (self):
        OpenInformationExemptions.getallexemptions()