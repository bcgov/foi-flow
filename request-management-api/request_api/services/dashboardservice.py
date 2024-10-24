from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRestrictedMinistryRequests import FOIRestrictedMinistryRequest
from request_api.models.FOIRawRequestWatchers import FOIRawRequestWatcher
from request_api.models.FOIRequestWatchers import FOIRequestWatcher
from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from dateutil import tz, parser
import datetime as dt
from pytz import timezone
import pytz
import maya
from request_api.auth import AuthHelper

from flask import jsonify

SHORT_DATEFORMAT = '%Y %b, %d'
LONG_DATEFORMAT = '%Y-%m-%d %H:%M:%S.%f'

class dashboardservice:
    """ FOI dashboard management service

    This service class manages dashboard retrival for both unopened and opened request with consideration of user types.

    """

    def __preparefoirequestinfo(self, request, receiveddate, receiveddateuf, idnumberprefix = ''):
        idnumber = self.__getidnumber(idnumberprefix, request.axisRequestId, request.idNumber)
        baserequestinfo = self.__preparebaserequestinfo(
            request.id, 
            request.requestType, 
            request.currentState, 
            receiveddate, 
            receiveddateuf, 
            request.assignedGroup, 
            request.assignedTo, 
            idnumberprefix + request.idNumber, 
            idnumber,
            request.version,
            request.description,
            request.recordsearchfromdate,
            request.recordsearchtodate,
        )
        baserequestinfo.update({'firstName': request.firstName})
        baserequestinfo.update({'lastName': request.lastName})
        baserequestinfo.update({'xgov': 'No'})
        baserequestinfo.update({'assignedToFirstName': request.assignedToFirstName})
        baserequestinfo.update({'duedate': request.duedate})
        baserequestinfo.update({'cfrduedate': request.cfrduedate})
        baserequestinfo.update({'applicantcategory': request.applicantcategory})
        baserequestinfo.update({'assignedToLastName': request.assignedToLastName})
        baserequestinfo.update({'onBehalfFirstName': request.onBehalfFirstName})
        baserequestinfo.update({'onBehalfLastName': request.onBehalfLastName})
        baserequestinfo.update({'onBehalfFormatted': request.onBehalfFormatted})
        baserequestinfo.update({'requestpagecount': request.requestpagecount})     
        baserequestinfo.update({'recordspagecount': request.recordspagecount})
        baserequestinfo.update({'axispagecount': request.axispagecount})
        baserequestinfo.update({'axislanpagecount': request.axislanpagecount})
        baserequestinfo.update({'bcgovcode': request.bcgovcode})
        isoipcreview = request.isoipcreview if request.isoipcreview == True else False
        baserequestinfo.update({'isoipcreview': isoipcreview})
        return baserequestinfo
        
    def __preparebaserequestinfo(self, id, requesttype, status, receiveddate, receiveddateuf, assignedgroup, assignedto, idnumber, axisrequestid, version, description, fromdate, todate):
        return {'id': id,
            'requestType': requesttype,
            'currentState': status,
            'receivedDate': receiveddate,
            'receivedDateUF': receiveddateuf,
            'assignedGroup': assignedgroup,
            'assignedTo': assignedto,            
            'idNumber': idnumber,
            'axisRequestId': axisrequestid,
            'version':version,
            'description':description,
            'fromdate':fromdate,
            'todate':todate,
        }

    def getrequestqueuepagination(self, groups=None, page=1, size=10, sortingitems=[], sortingorders=[], filterfields=[], keyword=None, additionalfilter='All', userid=None):        
        requests = FOIRawRequest.getrequestspagination(groups, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid, AuthHelper.isiaorestrictedfilemanager(), AuthHelper.getusertype())
        requestqueue = []                
        for request in requests.items:
            
            if(request.receivedDateUF is None): #request from online form has no received date in json
                _receiveddate = maya.parse(request.created_at).datetime(to_timezone='America/Vancouver', naive=False)
            else:
                _receiveddate = parser.parse(request.receivedDateUF)

            if(request.ministryrequestid == None):                
                unopenrequest = self.__preparefoirequestinfo(request, _receiveddate.strftime(SHORT_DATEFORMAT), _receiveddate.strftime(LONG_DATEFORMAT), idnumberprefix= 'U-00')
                unopenrequest.update({'assignedToFormatted': request.assignedToFormatted})
                unopenrequest.update({'isiaorestricted': request.isiaorestricted}) 

                # isawatcher = FOIRawRequestWatcher.isawatcher(request.id,userid)                                
                if request.isiaorestricted == True:
                    unopenrequest.update({'lastName': 'Restricted'})
                    unopenrequest.update({'firstName': 'Request'})
                
                requestqueue.append(unopenrequest) 

            else:
                _openrequest = self.__preparefoirequestinfo(request, _receiveddate.strftime(SHORT_DATEFORMAT), _receiveddate.strftime(LONG_DATEFORMAT))
                _openrequest.update({'ministryrequestid': request.ministryrequestid})
                _openrequest.update({'extensions': request.extensions})
                _openrequest.update({'assignedToFormatted': request.assignedToFormatted})
                _openrequest.update({'ministryAssignedToFormatted': request.ministryAssignedToFormatted})

                isiaorestricted = request.isiaorestricted if request.isiaorestricted == True else False
                _openrequest.update({'isiaorestricted': isiaorestricted})

                if isiaorestricted == True:
                    _openrequest.update({'lastName': 'Restricted'})
                    _openrequest.update({'firstName': 'Request'})

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
        requests = FOIMinistryRequest.getrequestspagination(groups, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid, AuthHelper.isiaorestrictedfilemanager(), AuthHelper.isministryrestrictedfilemanager())

        requestqueue = []
        for request in requests.items:
            _openrequest = self.__preparebaserequestinfo(request.id, request.requestType, request.currentState, 
                                                         request.receivedDate, request.receivedDateUF, request.assignedGroup, 
                                                         request.assignedTo, request.idNumber, request.axisRequestId, request.version,
                                                         request.description, request.recordsearchfromdate, request.recordsearchtodate)
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
            _openrequest.update({'assignedToFormatted': request.assignedToFormatted})
            _openrequest.update({'ministryAssignedToFormatted': request.ministryAssignedToFormatted})
            
            isministryrestricted = request.isministryrestricted if request.isministryrestricted == True else False
            _openrequest.update({'isministryrestricted': isministryrestricted})
            isoipcreview = request.isoipcreview if request.isoipcreview == True else False
            _openrequest.update({'isoipcreview': isoipcreview})
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

    def advancedsearch(self, params={'usertype': 'iao', 'groups':None, 'page':1, 'size':10, 'sortingitems':[], 'sortingorders':[], 'requeststate':[], 'requeststatus':[], 'requesttype':[], 'requestflags':[], 'publicbody':[], 'daterangetype':None, 'fromdate':None, 'todate':None, 'search':None, 'keywords':[], 'userid':None}):
        userid = AuthHelper.getuserid()

        if (params['usertype'] == "iao"):
            requests = FOIRawRequest.advancedsearch(params, userid, AuthHelper.isiaorestrictedfilemanager())
        else:
            requests = FOIMinistryRequest.advancedsearch(params, userid, AuthHelper.isministryrestrictedfilemanager())
        
        requestqueue = []
        for request in requests.items:
            if(request.receivedDateUF is None): #request from online form has no received date in json
                _receiveddate = maya.parse(request.created_at).datetime(to_timezone='America/Vancouver', naive=False)
            else:
                _receiveddate = parser.parse(request.receivedDateUF)

            if(request.ministryrequestid == None):
                unopenrequest = self.__preparefoirequestinfo(request, _receiveddate.strftime(SHORT_DATEFORMAT), _receiveddate.strftime(LONG_DATEFORMAT), idnumberprefix= 'U-00')
                unopenrequest.update({'description':request.description})
                unopenrequest.update({'assignedToFormatted': request.assignedToFormatted})
                unopenrequest.update({'isiaorestricted': request.isiaorestricted})

                requestqueue.append(unopenrequest)
            else:
                _openrequest = self.__preparefoirequestinfo(request,  _receiveddate.strftime(SHORT_DATEFORMAT), _receiveddate.strftime(LONG_DATEFORMAT))
                _openrequest.update({'ministryrequestid':request.ministryrequestid})
                _openrequest.update({'extensions': request.extensions})
                _openrequest.update({'description':request.description})
                _openrequest.update({'assignedToFormatted': request.assignedToFormatted})
                _openrequest.update({'ministryAssignedToFormatted': request.ministryAssignedToFormatted})

                isiaorestricted = request.isiaorestricted if request.isiaorestricted == True else False
                _openrequest.update({'isiaorestricted': isiaorestricted})

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

    def __getidnumber(self, idprefix, axisrequestid, filenumber):
        if axisrequestid is not None:
            return axisrequestid
        elif idprefix:
            return idprefix + filenumber
        return ""

    # def getoirequestqueuepagination(self, groups, page=1, size=10, sortingitems=[], sortingorders=[], filterfields=[], keyword=None, additionalfilter='All', userid=None):        
    #     #
    #     print(" getoirequestqueuepagination!!!!!! ")
    #     print("getusertype : ",AuthHelper.getusertype())
    #     requests = FOIOpenInformationRequests.getrequestspagination(groups, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid, AuthHelper.isiaorestrictedfilemanager(), "oi", AuthHelper.getusertype())
    #     print("requests : ",requests)
    #     requestqueue = []                
    #     for request in requests.items:
            
    #         if(request.receivedDateUF is None): #request from online form has no received date in json
    #             _receiveddate = maya.parse(request.created_at).datetime(to_timezone='America/Vancouver', naive=False)
    #         else:
    #             _receiveddate = parser.parse(request.receivedDateUF)

    #         if(request.ministryrequestid == None):                
    #             unopenrequest = self.__preparefoirequestinfo(request, _receiveddate.strftime(SHORT_DATEFORMAT), _receiveddate.strftime(LONG_DATEFORMAT), idnumberprefix= 'U-00')
    #             unopenrequest.update({'assignedToFormatted': request.assignedToFormatted})
    #             unopenrequest.update({'isiaorestricted': request.isiaorestricted}) 

    #             # isawatcher = FOIRawRequestWatcher.isawatcher(request.id,userid)                                
    #             if request.isiaorestricted == True:
    #                 unopenrequest.update({'lastName': 'Restricted'})
    #                 unopenrequest.update({'firstName': 'Request'})
                
    #             requestqueue.append(unopenrequest) 

    #         else:
    #             _openrequest = self.__preparefoirequestinfo(request, _receiveddate.strftime(SHORT_DATEFORMAT), _receiveddate.strftime(LONG_DATEFORMAT))
    #             _openrequest.update({'publicationdate': request.publicationdate})
    #             _openrequest.update({'closedate': request.closedate})
    #             _openrequest.update({'oiStatusName': request.oiStatusName})

    #             # _openrequest.update({'extensions': request.extensions})
    #             # _openrequest.update({'assignedToFormatted': request.assignedToFormatted})
    #             # _openrequest.update({'ministryAssignedToFormatted': request.ministryAssignedToFormatted})
    #             isiaorestricted = request.isiaorestricted if request.isiaorestricted == True else False
    #             _openrequest.update({'isiaorestricted': isiaorestricted})

    #             if isiaorestricted == True:
    #                 _openrequest.update({'lastName': 'Restricted'})
    #                 _openrequest.update({'firstName': 'Request'})

    #             requestqueue.append(_openrequest)   
                   

    #     meta = {
    #         'page': requests.page,
    #         'pages': requests.pages,
    #         'total': requests.total,
    #         'prev_num': requests.prev_num,
    #         'next_num': requests.next_num,
    #         'has_next': requests.has_next,
    #         'has_prev': requests.has_prev,
    #     }




    #     return jsonify({'data': requestqueue, 'meta': meta}) 
    
    def getoirequestqueuepagination(self, groups=None, page=1, size=10, sortingitems=[], sortingorders=[], filterfields=[], keyword=None, additionalfilter='All', userid=None):        
        requests = FOIOpenInformationRequests.getrequestspagination(groups, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid, AuthHelper.isiaorestrictedfilemanager(), AuthHelper.getusertype())
        requestqueue = []                
        for request in requests.items:
            _receiveddate = None
            if request.created_at:
                maya_dt = maya.parse(request.created_at)
                vancouver_dt = maya_dt.datetime(to_timezone='America/Vancouver', naive=False)
                _receiveddate = vancouver_dt.strftime("%b %d %Y")

            if request.publicationdate is None:
                _publicationdate = 'N/A'
            else:
                maya_dt = maya.parse(request.publicationdate)
                vancouver_dt = maya_dt.datetime(to_timezone='America/Vancouver', naive=False)
                _publicationdate = vancouver_dt.strftime("%b %d %Y")

            _oirequest = self.__preparefoioirequestinfo(request, _receiveddate, _receiveddate)
            
            print("request : ",request)
            _oirequest.update({
                'id': request.id,
                'ministryrequestid': request.ministryrequestid,
                'receivedDate': _receiveddate,
                'axisRequestId': request.axisRequestId,
                'requestType': 'G' if request.requestType == 'general' else 'PD',
                'recordspagecount': request.recordspagecount,
                'publicationStatus': request.oiStatusName,
                'fromClosed': request.closedate,
                'publicationDate': _publicationdate,
                'assignedTo': request.assignedToFormatted,
                'applicantType': request.applicantcategory,
                'version': request.version,
                'foiopeninforequestid': request.foiopeninforequestid,
            })

            # isiaorestricted = request.isiaorestricted if request.isiaorestricted == True else False
            # _oirequest.update({'isiaorestricted': isiaorestricted})

            # if isiaorestricted == True:
            #     _oirequest.update({'lastName': 'Restricted', 'firstName': 'Request'})

            requestqueue.append(_oirequest)   

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

    def __preparefoioirequestinfo(self, request, shortdate, longdate):
        return {
            'id': request.id,
            'idNumber': request.idNumber,
            'receivedDate': shortdate,
        }

    def __calculate_from_closed(self, closedate):
        if not closedate:
            return 'N/A'
        
        today = datetime.now().date()
        business_days = 0
        current_date = closedate.date()
        
        while current_date <= today:
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                business_days += 1
            current_date += timedelta(days=1)
        
        return str(business_days)     
          
