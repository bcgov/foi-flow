
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestCFRFees import FOIRequestCFRFee
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from dateutil.parser import parse

from dateutil import parser
from dateutil import tz
import pytz
import maya
from request_api.models.FOIRequestCFRFees import FOIRequestCFRFee

class cfrfeeservice:
    """ FOI CFR Fee Form management service
    Supports creation, update and delete of CFR fee form
    """

    def createcfrfee(self, ministryrequestid, data, userid):
        lkupversion = FOIRequestCFRFee.getversionforrequest(ministryrequestid)
        cfrfee = FOIRequestCFRFee()
        cfrfee.__dict__.update(data)
        cfrfee.version = 1 if lkupversion is None else (lkupversion[0]+1)
        cfrfee.ministryrequestid = ministryrequestid
        cfrfee.ministryrequestversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        return FOIRequestCFRFee.createcfrfee(cfrfee, userid)
        
    def getcfrfee(self, ministryrequestid):
        return FOIRequestCFRFee.getcfrfee(ministryrequestid)
    
    def getcfrfeehistory(self, ministryrequestid):
        cfrfees = []
        _cfrfees = FOIRequestCFRFee.getcfrfeehistory(ministryrequestid)
        for cfrfee in _cfrfees:
            cfrfee['created_at'] = self.__pstformat(cfrfee['created_at'])
            cfrfees.append(cfrfee)
        return cfrfees
           
    def __pstformat(self, inpdate):
        formateddate = maya.parse(inpdate).datetime(to_timezone='America/Vancouver', naive=False)
        return formateddate.strftime('%Y %b %d | %I:%M %p')