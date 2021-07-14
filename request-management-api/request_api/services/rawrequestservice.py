
from request_api.models.FOIRawRequests import FOIRawRequest
from dateutil.parser import *
from datetime import datetime
import json
import asyncio
import os 
from request_api.utils.redispublisher import RedisPublisherService

class rawrequestservice:
    """ FOI Request management service
    
    This service class manages all CRUD operations related to an FOI RAW Request
    
    """

    

    def saverawrequest(requestdatajson):
        result = FOIRawRequest.saverawrequest(requestdatajson)        
        if result.success :
                redispubservice = RedisPublisherService()
                data = {}
                data['id'] = result.identifier
                json_data = json.dumps(data)
                asyncio.run(redispubservice.publishtoredischannel(json_data))
        return result

    def updateworkflowinstance(wfinstanceid, requestid):
        result = FOIRawRequest.updateworkflowinstance(wfinstanceid, requestid)
        return result

    def getrawrequests():
        requests = FOIRawRequest.getrequests()
        unopenedrequests =[]
        for request in requests:
                    _createdDate = parse(request['created_at'])
                    unopenrequest = {'id': request['requestid'],
                                     'firstName': request['requestrawdata']['contactInfo']['firstName'],
                                     'lastName': request['requestrawdata']['contactInfo']['lastName'],
                                     'requestType': request['requestrawdata']['requestType']['requestType'],                                     
                                     'currentState': 'Unopened',
                                     'receivedDate': _createdDate.strftime('%Y %b, %d'),
                                     'receivedDateUF': request['created_at'],
                                     'assignedTo': "Unassigned",
                                     'xgov': 'No',
                                     'idNumber': 'U-00' + str(request['requestid'])
                                     }
                    unopenedrequests.append(unopenrequest)

        return  unopenedrequests           

    def getrawrequest(requestid):        
        request = FOIRawRequest.get_request(requestid)
        
        if request != {} :        
            requestrawdata = request['requestrawdata']
            requestType = requestrawdata['requestType']['requestType']
            ispersonal = True if requestType == 'personal' else False
            contactInfo = requestrawdata.get('contactInfo')
            decriptionTimeframe = requestrawdata.get('descriptionTimeframe')
            contactInfoOptions = requestrawdata.get('contactInfoOptions')
            _createdDate = parse(request['created_at'])

            baserequestInfo = {'id' : request['requestid'] ,
                            'requestType':requestType,
                            'firstName':contactInfo['firstName'],
                            'middleName':requestrawdata['contactInfo']['middleName'],
                            'lastName':contactInfo['lastName'],
                            'businessName':contactInfo['businessName'],                        
                            'currentState':'Unopened',#request['created_at']
                            'receivedDate':_createdDate.strftime('%Y %b, %d'),
                            'receivedDateUF':request['created_at'],
                            'assignedTo': "Unassigned",
                            'xgov':'No',
                            'idNumber': 'U-00'+ str(request['requestid']),
                            'email':contactInfoOptions['email'],
                            'phonePrimary':contactInfoOptions['phonePrimary'],
                            'phoneSecondary':contactInfoOptions['phoneSecondary'],
                            'address':contactInfoOptions['address'],
                            'city':contactInfoOptions['city'],
                            'postal':contactInfoOptions['postal'],
                            'province':contactInfoOptions['province'],
                            'country':contactInfoOptions['country'],
                            'description':decriptionTimeframe['description'],
                            'fromDate':decriptionTimeframe['fromDate'],
                            'toDate':decriptionTimeframe['toDate'],
                            'correctionalServiceNumber':decriptionTimeframe['correctionalServiceNumber'],
                            'publicServiceEmployeeNumber':decriptionTimeframe['publicServiceEmployeeNumber'],
                            'topic':decriptionTimeframe['topic'],
                            'selectedMinistries':requestrawdata['ministry']['selectedMinistry'],
                            }            
            if ispersonal:
                    childInformation = requestrawdata.get('childInformation')
                    anotherpersonInformation = requestrawdata.get('anotherInformation')                                   
                    adoptiveParents = requestrawdata.get('adoptiveParents')
                
                    haschildInfo = True if childInformation != None  else False
                    hasanotherpersonInfo = True if anotherpersonInformation != None  else False
                    hasadoptiveParentInfo = True if   adoptiveParents != None else False

                    additionalpersonalInfo =  {
                                'alsoKnownAs':contactInfo['alsoKnownAs'],
                                'requestFor':requestrawdata['selectAbout'],
                                'birthDate':contactInfo['birthDate'] ,
                                
                                'childFirstName':childInformation['firstName'] if haschildInfo   else '',
                                'childMiddleName':childInformation['middleName'] if haschildInfo else '',
                                'childLastName':childInformation['lastName'] if haschildInfo else '',
                                'childAlsoKnownAs':childInformation['alsoKnownAs'] if haschildInfo else '',                    
                                'childBirthDate':childInformation['dateOfBirth'] if haschildInfo else '',

                                'anotherFirstName':anotherpersonInformation['firstName'] if hasanotherpersonInfo else '',
                                'anotherMiddleName':anotherpersonInformation['middleName'] if hasanotherpersonInfo else '',
                                'anotherLastName':anotherpersonInformation['lastName'] if hasanotherpersonInfo else '',
                                'anotherAlsoKnownAs':anotherpersonInformation['alsoKnownAs'] if hasanotherpersonInfo else '',
                                'anotherBirthDate':anotherpersonInformation['dateOfBirth'] if hasanotherpersonInfo else '',

                                'adoptiveMotherFirstName' : adoptiveParents['motherFirstName'] if hasadoptiveParentInfo else '',
                                'adoptiveMotherLastName' : adoptiveParents['motherLastName'] if hasadoptiveParentInfo else '',
                                'adoptiveFatherLastName' : adoptiveParents['fatherLastName'] if hasadoptiveParentInfo else '',
                                'adoptiveFatherFirstName' : adoptiveParents['fatherFirstName'] if hasadoptiveParentInfo else ''
                            } 
                    baserequestInfo['additionalPersonalInfo'] = additionalpersonalInfo                    
            return baserequestInfo
        else:
            return None        
