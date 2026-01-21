from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRestrictedMinistryRequests import FOIRestrictedMinistryRequest
from request_api.models.FOIRawRequestWatchers import FOIRawRequestWatcher
from request_api.models.FOIRequestWatchers import FOIRequestWatcher
from request_api.models.FOIOpenInformationRequests import FOIOpenInformationRequests
from request_api.utils.enums import OIStatusEnum
from dateutil import tz, parser
import datetime as dt
from pytz import timezone
import pytz
import maya
from request_api.auth import AuthHelper
import holidays

from flask import jsonify

SHORT_DATEFORMAT = '%Y %b, %d'
LONG_DATEFORMAT = '%Y-%m-%d %H:%M:%S.%f'

REQUEST_TYPE_MAPPING = {
    'general': 'G',
    'personal': 'P',
    'proactivedisclosure': 'PD'
}

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
        baserequestinfo.update({'isphasedrelease': request.isphasedrelease if request.isphasedrelease == True else False})
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

        # Check if user is in OI Team
        is_oi_team = AuthHelper.getusertype() == "iao" and groups and 'OI Team' in groups     

        for request in requests.items:
            if is_oi_team:
                # Handle OI requests format
                requestqueue.append(self.__handle_oi_request(request))
            else:
                # Handle Raw requests format
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
            _openrequest.update({'isphasedrelease': request.isphasedrelease if request.isphasedrelease == True else False})
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
        is_oi_team = params['usertype'] == "iao" and params['groups'] and 'OI Team' in params['groups']

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
                unopenrequest.update({'closereason': request.closereason})
                if is_oi_team:
                    unopenrequest.update({'receivedDate': request.oiReceivedDate.strftime("%b %d %Y") if request.oiReceivedDate else None})
                    unopenrequest.update({'applicantType': request.applicantcategory})
                    unopenrequest.update({'fromClosed': self.__calculate_from_closed(request.closedate)})
                    unopenrequest.update({'publicationDate': request.publicationDate.strftime("%b %d %Y") if request.publicationDate else "N/A"})
                    unopenrequest.update({'assignedTo': "Unassigned"})
                    unopenrequest.update({'publicationStatus': "unopened"})

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
                _openrequest.update({'closereason': request.closereason})
                if is_oi_team:
                    oistatusid = request.oistatusid
                    match oistatusid:
                        case OIStatusEnum.FIRST_REVIEW.value:
                            _openrequest.update({'publicationStatus': "First Review"})
                        case OIStatusEnum.PEER_REVIEW.value:
                            _openrequest.update({'publicationStatus': "Peer Review"})
                        case OIStatusEnum.READY_TO_PUBLISH.value:
                            _openrequest.update({'publicationStatus': "Ready to Publish"})
                        case OIStatusEnum.PUBLISHED.value:
                            _openrequest.update({'publicationStatus': "Published"})
                        case OIStatusEnum.HOLD_PUBLICATION.value:
                            _openrequest.update({'publicationStatus': "HOLD Publication"})
                        case OIStatusEnum.UNPUBLISHED.value:
                            _openrequest.update({'publicationStatus': "Unpublished"})
                        case OIStatusEnum.DO_NOT_PUBLISH.value:
                            _openrequest.update({'publicationStatus': "Do Not Publish"})
                        case OIStatusEnum.EXEMPTION_REQUEST.value:
                            _openrequest.update({'publicationStatus': "Exemption Request"})
                        case _:
                            _openrequest.update({'publicationStatus': "unopened"})
                    _openrequest.update({'receivedDate': request.oiReceivedDate.strftime("%b %d %Y") if request.oiReceivedDate else None})
                    _openrequest.update({'publicationDate': request.publicationDate.strftime("%b %d %Y") if request.publicationDate else "N/A"})
                    _openrequest.update({'assignedTo': request.oiAssignedTo})
                    _openrequest.update({'fromClosed': self.__calculate_from_closed(request.closedate)})
                    _openrequest.update({'applicantType': request.applicantcategory})

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

    def __preparefoioirequestinfo(self, request, receivedDate, publicationDate, fromClosed):
        return {
            'id': request.id,
            'idNumber': request.idNumber,
            'ministryrequestid': request.ministryrequestid,
            'receivedDate': receivedDate,
            'axisRequestId': request.axisRequestId,
            'requestType': REQUEST_TYPE_MAPPING.get(request.requestType, ''),
            'recordspagecount': request.recordspagecount,
            'publicationStatus': request.oiStatusName,
            'publicationDate': publicationDate,
            'assignedTo': request.assignedToFormatted,
            'applicantType': request.applicantcategory,
            'version': request.version,
            'foiopeninforequestid': request.foiopeninforequestid,
            'currentState': request.currentState,
            'closedDate': fromClosed
        }

    def __calculate_from_closed(self, closedate):
        """Calculate business days from close date to today"""

        if not closedate:
            return "N/A"
        try:
            today = dt.datetime.now(tz=pytz.timezone('America/Vancouver')).date()
            closed_date = closedate.date() if isinstance(closedate, dt.datetime) else closedate
            business_days = 0
            canada_holidays = holidays.Canada(prov='BC', years=range(closed_date.year, today.year + 1))  
            holidays_set = set(canada_holidays)

            while closed_date <= today:
                if closed_date != closedate.date() and closed_date.weekday() < 5 and closed_date not in holidays_set:
                    business_days += 1
                closed_date += dt.timedelta(days=1)

            return str(business_days) if business_days > 0 else "N/A"
        except Exception as e:
            print("Error in calculate_from_closed: ", e)
            return "N/A"

    def __handle_oi_request(self, request):
        """Formats request data for OI team view with received date, publication date, and days since closure"""

        _receiveddate = None
        _publicationdate = 'N/A'

        # Handle received date
        if request.receivedDate:
            _receiveddate = request.receivedDate.strftime("%b %d %Y") if request.receivedDate else None
        
        # Handle publication date
        if request.publicationdate:
            _publicationdate = request.publicationdate.strftime("%b %d %Y") if request.publicationdate else None
        
        # Calculate business days
        _from_closed = self.__calculate_from_closed(request.closedate)
            
        return self.__preparefoioirequestinfo(request, _receiveddate, _publicationdate, _from_closed)