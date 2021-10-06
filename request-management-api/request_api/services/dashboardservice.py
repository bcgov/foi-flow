from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from dateutil import parser
from dateutil import tz
import datetime as dt
from pytz import timezone
import pytz
import maya

class dashboardservice:



    def getrequestqueue(groups=None):
            
            requests = []
            openedrequests = []
            if "Intake Team" in groups or groups is None:                
                requests = FOIRawRequest.getrequests()

            for group in groups:
                _teamrequests = FOIMinistryRequest.getrequests(group)
                openedrequests+=_teamrequests
                        
            requestqueue = []
            
            for request in requests:

                firstName , lastName, requestType = '','',''
               
                _receivedDate = request.created_at
                                
                dt = maya.parse(_receivedDate).datetime(to_timezone='America/Vancouver', naive=False)
                _receivedDate = dt
                
                                
                if(request.version != 1 and  request.sourceofsubmission != "intake") or request.sourceofsubmission == "intake":
                    firstName = request.requestrawdata['firstName']
                    lastName =  request.requestrawdata['lastName']
                    requestType =  request.requestrawdata['requestType']
                    _receivedDate = parser.parse(request.requestrawdata['receivedDateUF'])
                elif (request.sourceofsubmission!= "intake" and request.version == 1):               
                    firstName = request.requestrawdata['contactInfo']['firstName']
                    lastName = request.requestrawdata['contactInfo']['lastName']
                    requestType = request.requestrawdata['requestType']['requestType']

                
                unopenrequest = {'id': request.requestid,
                                 'firstName': firstName,
                                 'lastName': lastName,
                                 'requestType': requestType,
                                 'currentState': request.status,
                                 'receivedDate': _receivedDate.strftime('%Y %b, %d'),
                                 'receivedDateUF': _receivedDate.strftime('%Y-%m-%d %H:%M:%S.%f'),
                                 'assignedGroup': request.assignedgroup,
                                 'assignedTo': request.assignedto,
                                 'xgov': 'No',
                                 'idNumber': 'U-00' + str(request.requestid),
                                 'version':request.version
                                 }
                requestqueue.append(unopenrequest)

            for openrequest in openedrequests : 
                    _openrequest = {'id': openrequest["id"],
                                 'firstName':  openrequest["firstName"],
                                 'lastName':  openrequest["lastName"],
                                 'requestType':  openrequest["requestType"],
                                 'currentState':  openrequest["currentState"],
                                 'receivedDate':  openrequest["receivedDate"],
                                 'receivedDateUF':  openrequest["receivedDateUF"],
                                 'assignedGroup':  openrequest["assignedGroup"],
                                 'assignedTo':  openrequest["assignedTo"],
                                 'xgov': 'No',
                                 'idNumber':  openrequest["idNumber"],
                                 'version': openrequest["version"],
                                 'ministryrequestid':openrequest['ministryrequestid']
                                 }
                    requestqueue.append(_openrequest)
                        
            return requestqueue

    def getministryrequestqueue (groups=None):
            openedrequests = []
            
            for group in groups:
                _teamrequests = FOIMinistryRequest.getrequests(group)
                openedrequests+=_teamrequests
                        
            requestqueue = []
            
            for openrequest in openedrequests : 
                    _openrequest = {'id': openrequest["id"],                                 
                                 'requestType':  openrequest["requestType"],
                                 'currentState':  openrequest["currentState"],
                                 'receivedDate':  openrequest["receivedDate"],
                                 'receivedDateUF':  openrequest["receivedDateUF"],
                                 'assignedGroup':  openrequest["assignedGroup"],
                                 'assignedTo':  openrequest["assignedTo"],
                                 'assignedministrygroup':  openrequest["assignedministrygroup"],
                                 'assignedministryperson':  openrequest["assignedministryperson"],
                                 'cfrstatus': 'Select Division',
                                 'cfrduedate': openrequest["cfrDueDate"],
                                 'duedate': openrequest["dueDate"],
                                 'idNumber':  openrequest["idNumber"],
                                 'version': openrequest["version"],
                                 'ministryrequestid':openrequest['ministryrequestid'],
                                 'applicantcategory':openrequest['applicantcategory'],
                                 'watchers':[]
                                 }
                    requestqueue.append(_openrequest)
                        
            return requestqueue          