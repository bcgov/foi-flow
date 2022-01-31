from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestWatchers import FOIRequestWatcher
from request_api.models.FOIRawRequestWatchers import FOIRawRequestWatcher
from dateutil import tz, parser
import datetime as dt
from pytz import timezone
import pytz
import maya

from flask import jsonify

class dashboardservice:
    """ FOI dashboard management service

    This service class manages dashboard retrival for both unopened and opened request with consideration of user types.

    """

    def __preparefoirequestinfo(self, id, firstname, lastname, requesttype, status, receiveddate, receiveddateuf, assignedgroup, assignedto, idnumber, version):
        baserequestinfo = self.__preparebaserequestinfo(id, requesttype, status, receiveddate, receiveddateuf, assignedgroup, assignedto, idnumber, version)
        baserequestinfo.update({'firstName': firstname})
        baserequestinfo.update({'lastName': lastname})
        baserequestinfo.update({'xgov': 'No'})
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
            firstname , lastname, requesttype = '','',''
            _receiveddate = maya.parse(request.created_at).datetime(to_timezone='America/Vancouver', naive=False)

            if(request.version != 1 and  request.sourceofsubmission != "intake") or request.sourceofsubmission == "intake":
                firstname = request.firstName
                lastname =  request.lastName
                requesttype = request.requestType
                _receiveddate = parser.parse(request.receivedDateUF)
            elif (request.sourceofsubmission!= "intake" and request.version == 1):               
                firstname = request.contactFirstName
                lastname = request.contactLastName
                requesttype = request.requestTypeWebForm


            if(request.ministryrequestid == None):
                unopenrequest = self.__preparefoirequestinfo(request.id, firstname, lastname, requesttype,
                                                            request.currentState, _receiveddate.strftime('%Y %b, %d'), _receiveddate.strftime('%Y-%m-%d %H:%M:%S.%f'), request.assignedGroup,
                                                            request.assignedTo, 'U-00' + request.idNumber, request.version)

                requestqueue.append(unopenrequest)
            else:
                _openrequest = self.__preparefoirequestinfo(request.id, request.firstName, request.lastName, request.requestType,
                                                            request.currentState, _receiveddate.strftime('%Y %b, %d'), _receiveddate.strftime('%Y-%m-%d %H:%M:%S.%f'), request.assignedGroup,
                                                            request.assignedGroup, request.idNumber, request.version)
                _openrequest.update({'ministryrequestid':request.ministryrequestid})
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