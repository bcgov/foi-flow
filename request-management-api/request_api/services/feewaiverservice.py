
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestFeeWaiver import FOIRequestFeeWaiver
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.services.feewaiverstatusservice import feewaiverstatusservice
from dateutil.parser import parse

from dateutil import parser
from dateutil import tz
import pytz
import maya


class feewaiverservice:
    """ FOI CFR Fee Waiver management service
    Supports creation, update and delete of fee waiver record
    """

    def savefeewaiver(self, ministryrequestid, data, userid):
        feewaiver = self.__preparefeewaiver(ministryrequestid, data)
        feewaiver.formdata.update(data['formdata'])
        return FOIRequestFeeWaiver.createfeewaiver(feewaiver, userid)

    def __preparefeewaiver(self, ministryrequestid, data):
        feewaiver = FOIRequestFeeWaiver()
        lkupfeewaiver = self.getfeewaiver(ministryrequestid)
        _version = 1
        feewaiver.formdata = {}
        if lkupfeewaiver:
            feewaiver.__dict__.update(lkupfeewaiver)
            _version =  lkupfeewaiver['version'] + 1
        feewaiver.version = _version
        feewaiver.ministryrequestid = ministryrequestid
        feewaiver.ministryrequestversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        feewaiver.waiverstatusid = feewaiverstatusservice().getfeewaiverstatusidbyname(data['status'])
        return feewaiver


    def getfeewaiver(self, ministryrequestid):
        feewaiver = FOIRequestFeeWaiver.getfeewaiver(ministryrequestid)
        return self.__formatfeewaiver(feewaiver)

    def __formatfeewaiver(self,feewaiver):
        if feewaiver is not None and feewaiver != {}:
            feewaiver['created_at'] = self.__pstformat(feewaiver['created_at'])
            if feewaiver['waiverstatusid'] is not None:
                feewaiver['status'] = feewaiver['waiverstatus.name']
                feewaiver.pop('waiverstatus.name')
            else:
                feewaiver['status'] = None
            return feewaiver
        else:
            return {}


    def __pstformat(self, inpdate):
        formateddate = maya.parse(inpdate).datetime(to_timezone='America/Vancouver', naive=False)
        return formateddate.strftime('%Y %b %d | %I:%M %p')