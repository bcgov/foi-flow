
from typing import Counter

from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from dateutil.parser import parse
import maya
from request_api.models.FOIAssignees import FOIAssignee

class rawrequestservicegetter:
    """ This class consolidates retrival of FOI raw request for actors: iao. 
    """

    def getallrawrequests(self):
        requests = FOIRawRequest.getrequests()        
        unopenedrequests = []
        for request in requests:
            firstname , lastname, requesttype = '','',''            
            if(request.version != 1 and  request.sourceofsubmission != "intake") or request.sourceofsubmission == "intake":
                firstname = request.requestrawdata['firstName']
                lastname =  request.requestrawdata['lastName']
                requesttype =  request.requestrawdata['requestType']
            elif (request.sourceofsubmission!= "intake" and request.version == 1):               
                firstname = request.requestrawdata['contactInfo']['firstName']
                lastname = request.requestrawdata['contactInfo']['lastName']
                requesttype = request.requestrawdata['requestType']['requestType']   
            
            assignedgroupvalue = request.assignedgroup if request.assignedgroup else "Unassigned" 
            assignedtovalue = request.assignedto if request.assignedto else "Unassigned"
            dt = maya.parse(request.created_at).datetime(to_timezone='America/Vancouver', naive=False)
            _createddate = dt

            unopenrequest = {'id': request.requestid,
                             'firstName': firstname,
                             'lastName': lastname,
                             'requestType': requesttype,
                             'currentState': request.status,
                             'receivedDate': request.requestrawdata["receivedDate"] if "receivedDate" in request.requestrawdata else _createddate.strftime('%Y %b, %d'),
                             'receivedDateUF':request.requestrawdata["receivedDateUF"] if "receivedDateUF" in request.requestrawdata else str(_createddate),
                             'assignedGroup': assignedgroupvalue,
                             'assignedTo': assignedtovalue,
                             'xgov': 'No',
                             'idNumber': 'U-00' + str(request.requestid),
                             'axisRequestId': request.axisrequestid,
                             'version':request.version
                             }
            unopenedrequests.append(unopenrequest)

        return unopenedrequests

    def getrawrequestforid(self, requestid):
        request = FOIRawRequest.get_request(requestid)
        request = self.__attachministriesinfo(request)
        if request != {} and (request['version'] == 1 or request['status'] == 'Unopened') and  request['sourceofsubmission'] != "intake":
            requestrawdata = request['requestrawdata']
            requesttype = requestrawdata['requestType']['requestType']
            baserequestinfo = self.__preparebaserequestinfo(requestid, request, requesttype, requestrawdata)
            if self.__ispersonalrequest(requesttype):
                baserequestinfo['additionalPersonalInfo'] = self.__prepareadditionalpersonalinfo(requestrawdata)
            return baserequestinfo
        elif request != {} and request['version'] != 1 and  request['sourceofsubmission'] != "intake":       
            request['requestrawdata']['currentState'] = request['status']            
            requeststatus = FOIRequestStatus().getrequeststatusid(request['status'])
            request['requestrawdata']['requeststatusid'] =  requeststatus['requeststatusid']
            request['requestrawdata']['lastStatusUpdateDate'] = FOIRawRequest.getLastStatusUpdateDate(requestid, request['status']).strftime(self.__generaldateformat())
            if request['status'] == 'Closed':
                request['requestrawdata']['stateTransition']= FOIRawRequest.getstatesummary(requestid)
            request['requestrawdata']['wfinstanceid'] = request['wfinstanceid']
            request['requestrawdata']['closedate']= request['closedate']
            return request['requestrawdata']    
        elif request != {} and request['sourceofsubmission'] == "intake":
            requestrawdata = request['requestrawdata']
            requesttype = requestrawdata['requestType']             
            additionalpersonalinfo = None           
            if self.__ispersonalrequest(requesttype) and requestrawdata.get('additionalPersonalInfo') is not None:                
                additionalpersonalinfo = self.__prepareadditionalpersonalinfoforintakesubmission(requestrawdata)

            request['requestrawdata']['additionalPersonalInfo'] = additionalpersonalinfo              
            
            request['requestrawdata']['wfinstanceid'] = request['wfinstanceid']
            request['requestrawdata']['currentState'] = request['status']
            requeststatus = FOIRequestStatus().getrequeststatusid(request['status'])
            request['requestrawdata']['requeststatusid'] =  requeststatus['requeststatusid']            
            request['requestrawdata']['lastStatusUpdateDate'] = FOIRawRequest.getLastStatusUpdateDate(requestid, request['status']).strftime(self.__generaldateformat())
            request['requestrawdata']['stateTransition']= FOIRawRequest.getstatesummary(requestid)
            request['requestrawdata']['closedate']= request['closedate']
            return request['requestrawdata']
        else:
            return None
        
    def getrawrequestfieldsforid(self, requestid, fields):   
        request = FOIRawRequest.get_request(requestid)    
        fieldsresp = {}
        for field in fields:
            if field == "ministries" and request['status'] == 'Archived':
                fieldsresp['openedMinistries']= FOIMinistryRequest.getministriesopenedbyuid(request["requestid"])
        return fieldsresp         
    
    def getaxisequestids(self):
        return FOIRawRequest.getDistinctAXISRequestIds()

    def getcountofaxisequestidbyaxisequestid(self, axisrequestid):
        return FOIRawRequest.getCountOfAXISRequestIdbyAXISRequestId(axisrequestid)
        
    def __attachministriesinfo(self,request):        
        if request != {} and request['status'] == 'Archived':
            request['requestrawdata']['openedMinistries']= FOIMinistryRequest.getministriesopenedbyuid(request["requestid"])
        return request
        
    def __preparebaserequestinfo(self, requestid, request, requesttype, requestrawdata):
        contactinfo = requestrawdata.get('contactInfo')
        dt = maya.parse(request['created_at']).datetime(to_timezone='America/Vancouver', naive=False)
        _createddate = dt
        decriptiontimeframe = requestrawdata.get('descriptionTimeframe')
        contactinfooptions = requestrawdata.get('contactInfoOptions')           
        _fromdate = parse(decriptiontimeframe['fromDate'])
        _todate = parse(decriptiontimeframe['toDate'])
        assignee = None
        if ("assignedto" in request and request["assignedto"] not in (None,'')):
            assignee = FOIAssignee.getassignee(request["assignedto"])
        return {'id': request['requestid'],
                               'wfinstanceid': request['wfinstanceid'],
                               'ispiiredacted': request['ispiiredacted'],
                               'sourceOfSubmission': request['sourceofsubmission'],
                               'requestType': requesttype,
                               'firstName': contactinfo['firstName'],
                               'middleName': requestrawdata['contactInfo']['middleName'],
                               'lastName': contactinfo['lastName'],
                               'businessName': contactinfo['businessName'],                               
                               'currentState': request['status'],
                               'receivedDate': requestrawdata["receivedDate"] if "receivedDate" in requestrawdata else _createddate.strftime('%Y %b, %d'),
                               'receivedDateUF':requestrawdata["receivedDateUF"] if "receivedDateUF" in requestrawdata else _createddate.strftime('%Y-%m-%d %H:%M:%S.%f'),
                               'assignedGroup': request["assignedgroup"] if "assignedgroup" in request else "Unassigned",
                               'assignedTo': request["assignedto"] if "assignedto" in request else "Unassigned",
                               'assignedToFirstName': assignee["firstname"] if assignee is not None and "firstname" in assignee else None,
                               'assignedToLastName': assignee["lastname"] if assignee is not None and "lastname" in assignee else None,
                               'xgov': 'No',
                               'idNumber': 'U-00' + str(request['requestid']),
                               'axisRequestId': request['axisrequestid'],
                               'axisSyncDate': request['axissyncdate'],
                               'email': contactinfooptions['email'],
                               'phonePrimary': contactinfooptions['phonePrimary'],
                               'phoneSecondary': contactinfooptions['phoneSecondary'],
                               'address': contactinfooptions['address'],
                               'city': contactinfooptions['city'],
                               'postal': contactinfooptions['postal'],
                               'province': contactinfooptions['province'],
                               'country': contactinfooptions['country'],
                               'description': decriptiontimeframe['description'],
                               'fromDate': _fromdate.strftime(self.__generaldateformat()),
                               'toDate': _todate.strftime(self.__generaldateformat()),
                               'correctionalServiceNumber': decriptiontimeframe['correctionalServiceNumber'],
                               'publicServiceEmployeeNumber': decriptiontimeframe['publicServiceEmployeeNumber'],
                               'topic': decriptiontimeframe['topic'],
                               'selectedMinistries': requestrawdata['ministry']['selectedMinistry'],
                               'lastStatusUpdateDate': FOIRawRequest.getLastStatusUpdateDate(requestid, request['status']).strftime(self.__generaldateformat()),
                               'stateTransition': FOIRawRequest.getstatesummary(requestid),
                               'closedate': request['closedate'] if request['closedate'] is not None else None
                               }

    def __prepareadditionalpersonalinfo(self, requestrawdata):
        childinformation = requestrawdata.get('childInformation')
        anotherpersoninformation = requestrawdata.get('anotherInformation')
        adoptiveparents = requestrawdata.get('adoptiveParents')

        haschildinfo = self.__ispersonalinfopresent(childinformation)
        hasanotherpersoninfo = self.__ispersonalinfopresent(anotherpersoninformation)
        hasadoptiveparentinfo = self.__ispersonalinfopresent(adoptiveparents)
        contactinfo = requestrawdata.get('contactInfo')
        return  {
                    'alsoKnownAs': contactinfo['alsoKnownAs'],
                    'requestFor': requestrawdata['selectAbout'],
                    'birthDate': parse(contactinfo['birthDate']).strftime(self.__generaldateformat()) if contactinfo['birthDate'] is not None else '',

                    'childFirstName': self.__getpropertyvalue(childinformation,'firstName', haschildinfo),
                    'childMiddleName': self.__getpropertyvalue(childinformation,'middleName', haschildinfo),
                    'childLastName': self.__getpropertyvalue(childinformation,'lastName', haschildinfo),
                    'childAlsoKnownAs': self.__getpropertyvalue(childinformation,'alsoKnownAs', haschildinfo),
                    'childBirthDate': parse(childinformation['dateOfBirth']).strftime(self.__generaldateformat()) if haschildinfo and childinformation['dateOfBirth'] is not None else '',

                    'anotherFirstName': self.__getpropertyvalue(anotherpersoninformation,'firstName', hasanotherpersoninfo),
                    'anotherMiddleName': self.__getpropertyvalue(anotherpersoninformation,'middleName', hasanotherpersoninfo),
                    'anotherLastName': self.__getpropertyvalue(anotherpersoninformation,'lastName', hasanotherpersoninfo),
                    'anotherAlsoKnownAs': self.__getpropertyvalue(anotherpersoninformation,'alsoKnownAs', hasanotherpersoninfo),
                    'anotherBirthDate': parse(anotherpersoninformation['dateOfBirth']).strftime(self.__generaldateformat())  if hasanotherpersoninfo and anotherpersoninformation['dateOfBirth'] is not None else '',

                    'adoptiveMotherFirstName': self.__getpropertyvalue(adoptiveparents,'motherFirstName', hasadoptiveparentinfo),
                    'adoptiveMotherLastName': self.__getpropertyvalue(adoptiveparents,'motherLastName', hasadoptiveparentinfo),
                    'adoptiveFatherLastName': self.__getpropertyvalue(adoptiveparents,'fatherLastName', hasadoptiveparentinfo),
                    'adoptiveFatherFirstName': self.__getpropertyvalue(adoptiveparents,'fatherFirstName', hasadoptiveparentinfo)
                }
    
    def __prepareadditionalpersonalinfoforintakesubmission(self,requestrawdata):                  
        _childandanotherpersoninfo = requestrawdata['additionalPersonalInfo']         
        additionalpersonalinfo = {                    
                        'childFirstName': _childandanotherpersoninfo['childFirstName'] if _childandanotherpersoninfo.get('childFirstName') is not None else '',
                        'childMiddleName': _childandanotherpersoninfo['childMiddleName'] if _childandanotherpersoninfo.get('childMiddleName') is not None else '',
                        'childLastName': _childandanotherpersoninfo['childLastName'] if _childandanotherpersoninfo.get('childLastName') is not None else '',
                        'childAlsoKnownAs':_childandanotherpersoninfo['childAlsoKnownAs'] if _childandanotherpersoninfo.get('childAlsoKnownAs') is not None else '',
                        'childBirthDate': _childandanotherpersoninfo['childBirthDate'] if _childandanotherpersoninfo.get('childBirthDate') is not None else '',
                        'anotherFirstName': _childandanotherpersoninfo['anotherFirstName'] if _childandanotherpersoninfo.get('anotherFirstName') is not None else '',
                        'anotherMiddleName': _childandanotherpersoninfo['anotherMiddleName'] if _childandanotherpersoninfo.get('anotherMiddleName') is not None else '',
                        'anotherLastName':_childandanotherpersoninfo['anotherLastName'] if _childandanotherpersoninfo.get('anotherLastName') is not None else '',
                        'anotherAlsoKnownAs': _childandanotherpersoninfo['anotherAlsoKnownAs'] if _childandanotherpersoninfo.get('anotherAlsoKnownAs') is not None else '',
                        'anotherBirthDate':  _childandanotherpersoninfo['anotherBirthDate'] if _childandanotherpersoninfo.get('anotherBirthDate') is not None else '', 
                        'personalHealthNumber' : _childandanotherpersoninfo['personalHealthNumber'] if _childandanotherpersoninfo.get('personalHealthNumber') is not None else '',                  
                        'birthDate': _childandanotherpersoninfo['birthDate'] if _childandanotherpersoninfo.get('birthDate') is not None else ''
                    }                 
        return additionalpersonalinfo    

    def __getpropertyvalue(self, inputschema, property, criteria):
        return inputschema[property] if inputschema is not None and criteria  else ''
    
    def __ispersonalrequest(self, requesttype):
        return True if requesttype == 'personal' else False
    
    def __ispersonalinfopresent(self, criteria):
        return True if criteria != None else False    

    def __generaldateformat(self):
        return '%Y-%m-%d'