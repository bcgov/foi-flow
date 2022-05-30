
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestCFRFees import FOIRequestCFRFee
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from dateutil.parser import parse

from dateutil import parser
from dateutil import tz
import pytz
import maya


class cfrfeeservice:
    """ FOI CFR Fee Form management service
    Supports creation, update and delete of CFR fee form
    """

    def createcfrfee(self, data, userid):
        ministryrequestversion = FOIMinistryRequest.getversionforrequest(data["ministryrequestid"])  
        return FOIRequestCFRFee.createcfrfee(data, ministryrequestversion, userid)
        
    def updatecfrfee(self, data, userid):
        return FOIRequestCFRFee.updatecfrfee(data, userid)       
        
    def getcfrfee(self, ministryrequestid):
        cfrfeeforms = FOIRequestCFRFee.getcfrfee(ministryrequestid)
        return self.__formatcfrfee(cfrfeeforms)
           
    def __formatcfrfee(self, cfrfeeforms):
        for cfrfee in cfrfeeforms:
            formattedcfrfee = self.__cfrfeeformat(cfrfee)
        return formattedcfrfee

    def __cfrfeeformat(self, cfrfeeform):
        return {
                "cfrfeeid": cfrfeeform['cfrfeeid'],
                "ministryrequestid":cfrfeeform["ministryrequestid"],
                "feedata": cfrfeeform['feedata'],
                "overallsuggestions": cfrfeeform['overallsuggestions']
        }