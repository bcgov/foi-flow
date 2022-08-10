
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestCFRFees import FOIRequestCFRFee
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.services.cfrfeestatusservice import cfrfeestatusservice
from dateutil.parser import parse

from dateutil import parser
from dateutil import tz
import pytz
import maya


class cfrfeeservice:
    """ FOI CFR Fee Form management service
    Supports creation, update and delete of CFR fee form
    """

    def createcfrfee(self, ministryrequestid, data, userid):
        cfrfee = self.__preparecfrfee(ministryrequestid, data)
        cfrfee.__dict__.update(data)
        return FOIRequestCFRFee.createcfrfee(cfrfee, userid)
    
    def sanctioncfrfee(self, ministryrequestid, data, userid):     
        cfrfee = self.__preparecfrfee(ministryrequestid, data)   
        cfrfee.feedata.update(data['feedata'])
        return FOIRequestCFRFee.createcfrfee(cfrfee, userid)

    def paycfrfee(self, ministryrequestid, amountpaid):
        cfrfee = self.__preparecfrfee(ministryrequestid)
        cfrfee.feedata['amountpaid'] += amountpaid
        return FOIRequestCFRFee.createcfrfee(cfrfee, 'Online Payment')

    def waivecfrfee(self, ministryrequestid, waivedamount, userid):
        cfrfee = self.__preparecfrfee(ministryrequestid)
        cfrfee.feedata['totalamountdue'] -= waivedamount
        return FOIRequestCFRFee.createcfrfee(cfrfee, userid)
    
    def __preparecfrfee(self, ministryrequestid, data={}):
        cfrfee = FOIRequestCFRFee()
        lkupcfrfee = self.getcfrfee(ministryrequestid)           
        _version = 1
        if lkupcfrfee:
            cfrfee.__dict__.update(lkupcfrfee)
            _version =  lkupcfrfee['version'] + 1
        cfrfee.version = _version   
        cfrfee.ministryrequestid = ministryrequestid
        cfrfee.ministryrequestversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        if "status" in data and data['status'] not in (None,''):
            cfrfee.cfrfeestatusid = cfrfeestatusservice().getcfrfeestatusidbyname(data['status'])
        return cfrfee
    
    
    def getcfrfee(self, ministryrequestid):
        cfrfee = FOIRequestCFRFee.getcfrfee(ministryrequestid)
        return self.__formatcfrfee(cfrfee)

    
    def getcfrfeehistory(self, ministryrequestid):
        cfrfees = []
        _cfrfees = FOIRequestCFRFee.getcfrfeehistory(ministryrequestid)
        for cfrfee in _cfrfees:
            cfrfees.append(self.__formatcfrfee(cfrfee))
        return cfrfees
    
    def __formatcfrfee(self,cfrfee):
        if cfrfee is not None and cfrfee != {}:
            cfrfee['created_at'] = self.__pstformat(cfrfee['created_at'])   
            if cfrfee['cfrfeestatusid'] is not None:
                cfrfee['status'] = cfrfee['cfrfeestatus.name']
                cfrfee.pop('cfrfeestatus.name')
            else:
                cfrfee['status'] = None    
            return cfrfee 
        else:
            return {}
        
           
    def __pstformat(self, inpdate):
        formateddate = maya.parse(inpdate).datetime(to_timezone='America/Vancouver', naive=False)
        return formateddate.strftime('%Y %b %d | %I:%M %p')