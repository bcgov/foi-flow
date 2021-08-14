from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest

class dashboardservice:

    def getrequestqueue():
            
            requests = FOIRawRequest.getrequests()        
            unopenedrequests = []
            
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
                unopenedrequests.append(unopenrequest)

                openedrequests = FOIMinistryRequest.getrequests()
                unopenedrequests.append(openedrequests)


            return unopenedrequests