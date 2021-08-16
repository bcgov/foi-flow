from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest

class dashboardservice:

    def getrequestqueue():
            
            requests = FOIRawRequest.getrequests()
            openedrequests = FOIMinistryRequest.getrequests()        
            requestqueue = []
            
            for request in requests:

                firstName , lastName, requestType = '','',''            
                if(request.version != 1 and  request.sourceofsubmission != "intake") or request.sourceofsubmission == "intake":
                    firstName = request.requestrawdata['firstName']
                    lastName =  request.requestrawdata['lastName']
                    requestType =  request.requestrawdata['requestType']
                elif (request.sourceofsubmission!= "intake" and request.version == 1):               
                    firstName = request.requestrawdata['contactInfo']['firstName']
                    lastName = request.requestrawdata['contactInfo']['lastName']
                    requestType = request.requestrawdata['requestType']['requestType']    

                _createdDate = request.created_at
                unopenrequest = {'id': request.requestid,
                                 'firstName': firstName,
                                 'lastName': lastName,
                                 'requestType': requestType,
                                 'currentState': request.status,
                                 'receivedDate': _createdDate.strftime('%Y %b, %d'),
                                 'receivedDateUF': str(_createdDate),
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
                                 'assignedTo':  openrequest["assignedTo"],
                                 'xgov': 'No',
                                 'idNumber':  openrequest["idNumber"],
                                 'version': openrequest["version"]
                                 }
                    requestqueue.append(_openrequest)
                        
            return requestqueue