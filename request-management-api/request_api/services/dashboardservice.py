from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestWatchers import FOIRequestWatcher
from request_api.models.FOIRawRequestWatchers import FOIRawRequestWatcher
from request_api.services.extensionservice import extensionservice
from dateutil import tz, parser
import datetime as dt
from pytz import timezone
import pytz
import maya

from flask import jsonify

SHORT_DATEFORMAT = '%Y %b, %d'
LONG_DATEFORMAT = '%Y-%m-%d %H:%M:%S.%f'

class dashboardservice:
    """ FOI dashboard management service

    This service class manages dashboard retrival for both unopened and opened request with consideration of user types.

    """

    def __init__(self):
        self.extension_service = extensionservice()

    def __preparefoirequestinfo(self, request, receiveddate, receiveddateuf, idnumberprefix = ''):
        baserequestinfo = self.__preparebaserequestinfo(
            request.id, 
            request.requestType, 
            request.currentState, 
            receiveddate, 
            receiveddateuf, 
            request.assignedGroup, 
            request.assignedTo, 
            idnumberprefix + request.idNumber, 
            request.version
        )
        baserequestinfo.update({'firstName': request.firstName})
        baserequestinfo.update({'lastName': request.lastName})
        baserequestinfo.update({'xgov': 'No'})
        baserequestinfo.update({'assignedToFirstName': request.assignedToFirstName})
        baserequestinfo.update({'duedate': request.duedate})
        baserequestinfo.update({'applicantcategory': request.applicantcategory})
        baserequestinfo.update({'assignedToLastName': request.assignedToLastName})
        baserequestinfo.update({'onBehalfFirstName': request.onBehalfFirstName})
        baserequestinfo.update({'onBehalfLastName': request.onBehalfFirstName})
        return baserequestinfo
        
    def __preparebaserequestinfo(self, id, requesttype, status, receiveddate, receiveddateuf, assignedgroup, assignedto, idnumber, version):
        return {'id': id,
            'requestType': requesttype,
            'currentState': status,
            'receivedDate': receiveddate,
            'receivedDateUF': receiveddateuf,
            'assignedGroup': assignedgroup,
            'assignedTo': assignedto,            
            'idNumber': idnumber,
            'version':version
        }

    def getrequestqueuepagination(self, groups=None, page=1, size=10, sortingitems=[], sortingorders=[], filterfields=[], keyword=None, additionalfilter='All', userid=None):
        requests = FOIRawRequest.getrequestspagination(groups, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid)
        
        requestqueue = []
        for request in requests.items:
            _receiveddate = maya.parse(request.created_at).datetime(to_timezone='America/Vancouver', naive=False)

            if(request.version != 1 and  request.sourceofsubmission != "intake") or request.sourceofsubmission == "intake":
                _receiveddate = parser.parse(request.receivedDateUF)

            if(request.ministryrequestid == None):
                unopenrequest = self.__preparefoirequestinfo(request, _receiveddate.strftime(SHORT_DATEFORMAT), _receiveddate.strftime(LONG_DATEFORMAT), idnumberprefix= 'U-00')

                requestqueue.append(unopenrequest)
            else:
                extensionscount = self.extension_service.getrequestextensionscount(requestid = request.ministryrequestid)
                _openrequest = self.__preparefoirequestinfo(request, _receiveddate.strftime(SHORT_DATEFORMAT), _receiveddate.strftime(LONG_DATEFORMAT))
                _openrequest.update({'ministryrequestid':request.ministryrequestid})
                _openrequest.update({'extensions': extensionscount})
                requestqueue.append(_openrequest)    

        meta = {
            'page': requests.page,
            'pages': requests.pages,
            'total': requests.total,
            'prev_num': requests.prev_num,
            'next_num': requests.next_num,
            'has_next': requests.has_next,
            'has_prev': requests.has_prev,
        }

        return jsonify({'data': requestqueue, 'meta': meta})

    def getministryrequestqueuepagination (self, groups=None, page=1, size=10, sortingitems=[], sortingorders=[], filterfields=[], keyword=None, additionalfilter='All', userid=None):
        requests = FOIMinistryRequest.getrequestspagination(groups, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid)

        requestqueue = []
        for request in requests.items:
            _openrequest = self.__preparebaserequestinfo(request.id, request.requestType, request.currentState, 
                                                         request.receivedDate, request.receivedDateUF, request.assignedGroup, 
                                                         request.assignedTo, request.idNumber, request.version)
            _openrequest.update({'assignedministrygroup': request.assignedministrygroup})
            _openrequest.update({'assignedministryperson': request.assignedministryperson})
            _openrequest.update({'cfrstatus':'Select Division'})
            _openrequest.update({'cfrduedate': request.cfrduedate})
            _openrequest.update({'duedate': request.duedate})
            _openrequest.update({'ministryrequestid': request.ministryrequestid})
            _openrequest.update({'applicantcategory': request.applicantcategory})
            _openrequest.update({'bcgovcode': request.bcgovcode})
            _openrequest.update({'assignedToFirstName': request.assignedToFirstName})
            _openrequest.update({'assignedToLastName': request.assignedToLastName})
            _openrequest.update({'assignedministrypersonFirstName': request.assignedministrypersonFirstName})
            _openrequest.update({'assignedministrypersonLastName': request.assignedministrypersonLastName})
            requestqueue.append(_openrequest)

        meta = {
            'page': requests.page,
            'pages': requests.pages,
            'total': requests.total,
            'prev_num': requests.prev_num,
            'next_num': requests.next_num,
            'has_next': requests.has_next,
            'has_prev': requests.has_prev,
        }

        return jsonify({'data': requestqueue, 'meta': meta})

    def advancedsearch(self, params={'groups':None, 'page':1, 'size':10, 'sortingitems':[], 'sortingorders':[], 'requeststate':[], 'requeststatus':[], 'requesttype':[], 'publicbody':[], 'fromdate':None, 'todate':None, 'search':None, 'keywords':[], 'userid':None}):
        requests = FOIRawRequest.advancedsearch(params)
        
        requestqueue = []
        for request in requests.items:
            _receiveddate = maya.parse(request.created_at).datetime(to_timezone='America/Vancouver', naive=False)

            if(request.version != 1 and  request.sourceofsubmission != "intake") or request.sourceofsubmission == "intake":
                _receiveddate = parser.parse(request.receivedDateUF)

            if(request.ministryrequestid == None):
                unopenrequest = self.__preparefoirequestinfo(request.id, _receiveddate.strftime(SHORT_DATEFORMAT), _receiveddate.strftime(LONG_DATEFORMAT), idnumberprefix= 'U-00')
                unopenrequest.update({'description':request.description})
                requestqueue.append(unopenrequest)
            else:
                _openrequest = self.__preparefoirequestinfo(request,  _receiveddate.strftime(SHORT_DATEFORMAT), _receiveddate.strftime(LONG_DATEFORMAT))
                _openrequest.update({'ministryrequestid':request.ministryrequestid})
                _openrequest.update({'description':request.description})
                requestqueue.append(_openrequest)    

        meta = {
            'page': requests.page,
            'pages': requests.pages,
            'total': requests.total,
            'prev_num': requests.prev_num,
            'next_num': requests.next_num,
            'has_next': requests.has_next,
            'has_prev': requests.has_prev,
        }

        return jsonify({'data': requestqueue, 'meta': meta})