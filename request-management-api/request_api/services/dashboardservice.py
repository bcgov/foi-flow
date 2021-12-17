from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestWatchers import FOIRequestWatcher
from request_api.models.FOIRawRequestWatchers import FOIRawRequestWatcher
from dateutil import parser
from dateutil import tz
import datetime as dt
from pytz import timezone
import pytz
import maya

class dashboardservice:
    """ FOI dashboard management service

    This service class manages dashboard retrival for both unopened and opened request with consideration of user types.

    """

    def getrequestqueue(self, groups=None):            
            requests = []
            openedrequests = []
            if "Intake Team" in groups or groups is None:                
                requests = FOIRawRequest.getrequests()

            for group in groups:
                _teamrequests = FOIMinistryRequest.getrequests(group)
                openedrequests+=_teamrequests
                        
            requestqueue = []
            
            for request in requests:

                firstname , lastname, requesttype = '','',''
                dt = maya.parse(request.created_at).datetime(to_timezone='America/Vancouver', naive=False)
                _receiveddate = dt
                
                                
                if(request.version != 1 and  request.sourceofsubmission != "intake") or request.sourceofsubmission == "intake":
                    firstname = request.requestrawdata['firstName']
                    lastname =  request.requestrawdata['lastName']
                    requesttype =  request.requestrawdata['requestType']
                    _receiveddate = parser.parse(request.requestrawdata['receivedDateUF'])
                elif (request.sourceofsubmission!= "intake" and request.version == 1):               
                    firstname = request.requestrawdata['contactInfo']['firstName']
                    lastname = request.requestrawdata['contactInfo']['lastName']
                    requesttype = request.requestrawdata['requestType']['requestType']

                rawrequestwatchers = FOIRawRequestWatcher.getwatchers(request.requestid)
                unopenrequest = self.__preparefoirequestinfo(request.requestid, firstname, lastname, requesttype, 
                                                              request.status, _receiveddate.strftime('%Y %b, %d'), _receiveddate.strftime('%Y-%m-%d %H:%M:%S.%f'), request.assignedgroup, 
                                                              request.assignedto, 'U-00' + str(id), request.version, rawrequestwatchers)
                requestqueue.append(unopenrequest)

            for openrequest in openedrequests : 
                    watchers = FOIRequestWatcher.getNonMinistrywatchers(openrequest['ministryrequestid'])
                    _openrequest = self.__preparefoirequestinfo(openrequest["id"], openrequest["firstName"], openrequest["lastName"],
                                                                 openrequest["requestType"], openrequest["currentState"], openrequest["receivedDate"], 
                                                                 openrequest["receivedDateUF"], openrequest["assignedGroup"], openrequest["assignedTo"],
                                                                 openrequest["idNumber"], openrequest["version"], watchers)
                    _openrequest['ministryrequestid'] = openrequest['ministryrequestid']
                    requestqueue.append(_openrequest)                        
            return requestqueue

    def getministryrequestqueue (self, groups=None):
            openedrequests = []            
            for group in groups:
                _teamrequests = FOIMinistryRequest.getrequests(group)
                openedrequests+=_teamrequests
                        
            requestqueue = []
            
            for openrequest in openedrequests : 
                    watchers = FOIRequestWatcher.getMinistrywatchers(openrequest['ministryrequestid'])
                    _openrequest = self.__preparebaserequestinfo(openrequest["id"], openrequest["requestType"], openrequest["currentState"], 
                                                                 openrequest["receivedDate"], openrequest["receivedDateUF"], openrequest["assignedGroup"], 
                                                                 openrequest["assignedTo"], openrequest["idNumber"], openrequest["version"], watchers)
                    _openrequest['assignedministrygroup'] = openrequest['assignedministrygroup'],
                    _openrequest['assignedministryperson'] = openrequest['assignedministryperson'],
                    _openrequest['cfrstatus'] = 'Select Division',
                    _openrequest['cfrduedate'] = openrequest["cfrDueDate"],
                    _openrequest['duedate'] = openrequest["dueDate"],
                    _openrequest['ministryrequestid'] = openrequest["ministryrequestid"],
                    _openrequest['applicantcategory'] = openrequest["applicantcategory"]                    
                    requestqueue.append(_openrequest)
            return requestqueue 
    
    def __preparefoirequestinfo(self, id, firstname, lastname, requesttype, status, receiveddate, receiveddateuf, assignedgroup, assignedto, idnumber, version, watchers):
        baserequestinfo = self.__preparebaserequestinfo(id, requesttype, status, receiveddate, receiveddateuf, assignedgroup, assignedto, idnumber, version, watchers)
        baserequestinfo['firstName'] = firstname
        baserequestinfo['lastName'] = lastname
        baserequestinfo['xgov'] = 'No'
        return baserequestinfo
        
    def __preparebaserequestinfo(self, id, requesttype, status, receiveddate, receiveddateuf, assignedgroup, assignedto, idnumber, version, watchers):
        return {'id': id,
            'requestType': requesttype,
            'currentState': status,
            'receivedDate': receiveddate,
            'receivedDateUF': receiveddateuf,
            'assignedGroup': assignedgroup,
            'assignedTo': assignedto,            
            'idNumber': idnumber,
            'version':version,
            'watchers':watchers
        }