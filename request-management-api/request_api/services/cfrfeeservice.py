
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestCFRFees import FOIRequestCFRFee
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.services.cfrfeestatusservice import cfrfeestatusservice
from request_api.services.cfrformreasonservice import cfrformreasonservice
from dateutil.parser import parse

from dateutil import parser
from dateutil import tz
import pytz
import maya
from datetime import date
from datetime import datetime
import requests
from flask import current_app

class cfrfeeservice:
    """ FOI CFR Fee Form management service
    Supports creation, update and delete of CFR fee form
    """

    def createcfrfee(self, ministryrequestid, data, userid):
        cfrfee = self.__preparecfrfee(ministryrequestid, data, data.get('cfrfeeid') is not None)
        cfrfee.__dict__.update(data)
        return FOIRequestCFRFee.createcfrfee(cfrfee, userid)
    
    def sanctioncfrfee(self, ministryrequestid, data, userid):
        cfrfee = self.__preparecfrfee(ministryrequestid, data)
        cfrfee.feedata.update(data.get('feedata', {}))
        return FOIRequestCFRFee.createcfrfee(cfrfee, userid)

    def paycfrfee(self, ministryrequestid, amountpaid):
        cfrfee = self.__preparecfrfee(ministryrequestid)
        _amountpaid = cfrfee.feedata['amountpaid'] + amountpaid
        _balanceremaining = cfrfee.feedata['balanceremaining'] - amountpaid
        cfrfee.feedata['balanceremaining'] = _balanceremaining
        cfrfee.feedata['amountpaid'] = '{:.2f}'.format(_amountpaid)
        cfrfee.feedata['paymentdate'] = datetime.now().astimezone(pytz.timezone(current_app.config['LEGISLATIVE_TIMEZONE'])).strftime('%Y-%m-%d')
        return FOIRequestCFRFee.createcfrfee(cfrfee, 'Online Payment')
    
    def __preparecfrfee(self, ministryrequestid, data={}, getprevious=True):
        cfrfee = FOIRequestCFRFee()
        lkupcfrfee = self.getcfrfee(ministryrequestid) if getprevious else None
        _version = 1
        if lkupcfrfee:
            cfrfee.__dict__.update(lkupcfrfee)
            _version =  lkupcfrfee['version'] + 1
        cfrfee.version = _version   
        cfrfee.ministryrequestid = ministryrequestid
        cfrfee.ministryrequestversion = FOIMinistryRequest.getversionforrequest(ministryrequestid)
        if "status" in data and data['status'] not in (None,''):
            cfrfee.cfrfeestatusid = cfrfeestatusservice().getcfrfeestatusidbyname(data['status'])
        if "reason" in data and data['reason'] not in (None,''):
            cfrfee.cfrformreasonid = cfrformreasonservice().getcfrformreasonidbyname(data['reason'])
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
            if cfrfee.get('version_created_at') is not None:
                cfrfee['version_created_at'] = self.__pstformat(cfrfee['version_created_at'])
            if cfrfee['cfrfeestatusid'] is not None:
                cfrfee['status'] = cfrfee['cfrfeestatus.name']
                cfrfee.pop('cfrfeestatus.name')
            else:
                cfrfee['status'] = None    
            if cfrfee['cfrformreasonid'] is not None:
                cfrfee['reason'] = cfrfee['cfrformreason.name']
                cfrfee.pop('cfrformreason.name')
            else:
                cfrfee['reason'] = None
            return cfrfee 
        else:
            return {}
        
           
    def __pstformat(self, inpdate):
        formateddate = maya.parse(inpdate).datetime(to_timezone='America/Vancouver', naive=False)
        return formateddate.strftime('%Y %b %d | %I:%M %p')
