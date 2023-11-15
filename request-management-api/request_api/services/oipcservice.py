from request_api.models.OIPCReviewTypes import OIPCReviewTypes
from request_api.models.OIPCStatuses import OIPCStatuses
from request_api.models.OIPCReasons import OIPCReasons
from request_api.models.OIPCOutcomes import OIPCOutcomes
from request_api.models.OIPCInquiryOutcomes import OIPCInquiryOutcomes

class oipcservice:
    """ OIPC service
    """
    def getreviewtypes(self):
        return OIPCReviewTypes.getreviewtypes()

    def getreasons(self):
        return OIPCReasons.getreasons()

    def getstatuses(self):
        return OIPCStatuses.getstatuses()

    def getoutcomes(self):
        return OIPCOutcomes.getoutcomes()

    def getinquiryoutcomes(self):
        return OIPCInquiryOutcomes.getinquiryoutcomes()