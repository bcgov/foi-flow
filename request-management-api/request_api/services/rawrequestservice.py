
import re
from typing import Counter

from flask.signals import request_started
from sqlalchemy.sql.expression import false
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.models.FOIRequestStatus import FOIRequestStatus
from dateutil.parser import *
from datetime import datetime
import json
import asyncio
import os
from request_api.utils.redispublisher import RedisPublisherService
import maya
from request_api.services.workflowservice import workflowservice
from request_api.services.documentservice import documentservice
from request_api.services.eventservice import eventservice
from request_api.models.FOIRawRequestDocuments import FOIRawRequestDocument

from request_api.exceptions import BusinessException, Error

class rawrequestservice:        
    
    """ FOI Request management service

    This service class manages all CRUD operations related to an FOI RAW Request

    """

    def saverawrequest(requestdatajson,sourceofsubmission, userId,notes):
        assigneeGroup = requestdatajson["assignedGroup"] if requestdatajson.get("assignedGroup") != None else None
        assignee = requestdatajson["assignedTo"] if requestdatajson.get("assignedTo") != None else None
        ispiiredacted = requestdatajson["ispiiredacted"] if 'ispiiredacted' in requestdatajson  else False
        requirespayment = rawrequestservice.doesRequirePayment(requestdatajson)                
        result = FOIRawRequest.saverawrequest(_requestrawdata=requestdatajson,notes=notes, requirespayment=requirespayment, ispiiredacted=ispiiredacted,sourceofsubmission=sourceofsubmission,userId=userId,assigneegroup=assigneeGroup,assignee=assignee)
        if result.success:
            redispubservice = RedisPublisherService()
            data = {}
            data['id'] = result.identifier
            data['assignedGroup'] = assigneeGroup
            data['assignedTo'] = assignee
            json_data = json.dumps(data)
            asyncio.run(redispubservice.publishtoredischannel(json_data))
        return result
    
    @staticmethod
    def doesRequirePayment(requestdatajson):                
        if 'requestType' not in requestdatajson:            
            raise BusinessException(Error.DATA_NOT_FOUND)
        if requestdatajson['requestType'] == "personal":     
            return False
        if 'contactInfo' in requestdatajson:            
            if requestdatajson['requestType']== "general":                
                if requestdatajson['contactInfo']['IGE']:                    
                    return False
                return True
            elif requestdatajson['requestType'] == "personal":                
                return False
        else:
            if 'requiresPayment' not in requestdatajson:                
                return True ## Default PAYMENT TRUE ?
            return requestdatajson['requiresPayment']
            
        raise BusinessException(Error.DATA_NOT_FOUND)
        
    def saverawrequestversion(_requestdatajson, _requestid, _assigneeGroup, _assignee, status, userId):
        ispiiredacted = _requestdatajson["ispiiredacted"] if 'ispiiredacted' in _requestdatajson  else False
        #Get documents
        result = FOIRawRequest.saverawrequestversion(_requestdatajson, _requestid, _assigneeGroup, _assignee, status,ispiiredacted, userId)
        documentservice().createrawrequestdocumentversion(_requestid)
        eventservice().postevent(_requestid,"rawrequest")
        return result

   
    def updateworkflowinstance(wfinstanceid, requestid, userId):
        return FOIRawRequest.updateworkflowinstance(wfinstanceid, requestid, userId)

    def updateworkflowinstancewithstatus(wfinstanceid, requestid,status,notes, userId):
        return FOIRawRequest.updateworkflowinstancewithstatus(wfinstanceid,requestid,status,notes, userId)    
    
    def postEventToWorkflow(self, id, wfinstanceid, requestsschema, status):
        return workflowservice().postunopenedevent(id, wfinstanceid, requestsschema, status)

    def getrawrequests():
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
            assignedgroupvalue = request.assignedgroup if request.assignedgroup else "Unassigned" 
            assignedtovalue = request.assignedto if request.assignedto else "Unassigned"
            _createdDate = request.created_at
            unopenrequest = {'id': request.requestid,
                             'firstName': firstName,
                             'lastName': lastName,
                             'requestType': requestType,
                             'currentState': request.status,
                             'receivedDate': _createdDate.strftime('%Y %b, %d'),
                             'receivedDateUF': str(_createdDate),
                             'assignedGroup': assignedgroupvalue,
                             'assignedTo': assignedtovalue,
                             'xgov': 'No',
                             'idNumber': 'U-00' + str(request.requestid),
                             'version':request.version
                             }
            unopenedrequests.append(unopenrequest)

        return unopenedrequests

    def getrawrequest(requestid):
        request = FOIRawRequest.get_request(requestid)
        if request != {} and request['version'] == 1 and  request['sourceofsubmission'] != "intake":
            requestrawdata = request['requestrawdata']
            requestType = requestrawdata['requestType']['requestType']
            ispersonal = True if requestType == 'personal' else False
            contactInfo = requestrawdata.get('contactInfo')
            decriptionTimeframe = requestrawdata.get('descriptionTimeframe')
            contactInfoOptions = requestrawdata.get('contactInfoOptions')
           
            #_createdDate = parse(request['created_at'])
            _fromdate = parse(decriptionTimeframe['fromDate'])
            _todate = parse(decriptionTimeframe['toDate'])
            dt = maya.parse(request['created_at']).datetime(to_timezone='America/Vancouver', naive=False)
            _createdDate = dt
            baserequestInfo = {'id': request['requestid'],
                               'wfinstanceid': request['wfinstanceid'],
                               'ispiiredacted': request['ispiiredacted'],
                               'sourceOfSubmission': request['sourceofsubmission'],
                               'requestType': requestType,
                               'firstName': contactInfo['firstName'],
                               'middleName': requestrawdata['contactInfo']['middleName'],
                               'lastName': contactInfo['lastName'],
                               'businessName': contactInfo['businessName'],                               
                               'currentState': request['status'],
                               'receivedDate': _createdDate.strftime('%Y %b, %d'),
                               'receivedDateUF': _createdDate.strftime('%Y-%m-%d %H:%M:%S.%f'),
                               'assignedGroup': "Unassigned",
                               'assignedTo': "Unassigned",
                               'xgov': 'No',
                               'idNumber': 'U-00' + str(request['requestid']),
                               'email': contactInfoOptions['email'],
                               'phonePrimary': contactInfoOptions['phonePrimary'],
                               'phoneSecondary': contactInfoOptions['phoneSecondary'],
                               'address': contactInfoOptions['address'],
                               'city': contactInfoOptions['city'],
                               'postal': contactInfoOptions['postal'],
                               'province': contactInfoOptions['province'],
                               'country': contactInfoOptions['country'],
                               'description': decriptionTimeframe['description'],
                               'fromDate': _fromdate.strftime('%Y-%m-%d'),
                               'toDate': _todate.strftime('%Y-%m-%d'),
                               'correctionalServiceNumber': decriptionTimeframe['correctionalServiceNumber'],
                               'publicServiceEmployeeNumber': decriptionTimeframe['publicServiceEmployeeNumber'],
                               'topic': decriptionTimeframe['topic'],
                               'selectedMinistries': requestrawdata['ministry']['selectedMinistry'],
                               'lastStatusUpdateDate': FOIRawRequest.getLastStatusUpdateDate(requestid, request['status']).strftime('%Y-%m-%d'),
                               'stateTransition': FOIRawRequest.getstatesummary(requestid)
                               }
            
            if ispersonal:
                childInformation = requestrawdata.get('childInformation')
                anotherpersonInformation = requestrawdata.get(
                    'anotherInformation')
                adoptiveParents = requestrawdata.get('adoptiveParents')

                haschildInfo = True if childInformation != None else False
                hasanotherpersonInfo = True if anotherpersonInformation != None else False
                hasadoptiveParentInfo = True if adoptiveParents != None else False

                additionalpersonalInfo = {
                    'alsoKnownAs': contactInfo['alsoKnownAs'],
                    'requestFor': requestrawdata['selectAbout'],
                    'birthDate': parse(contactInfo['birthDate']).strftime('%Y-%m-%d') if contactInfo['birthDate'] is not None else '',

                    'childFirstName': childInformation['firstName'] if haschildInfo else '',
                    'childMiddleName': childInformation['middleName'] if haschildInfo else '',
                    'childLastName': childInformation['lastName'] if haschildInfo else '',
                    'childAlsoKnownAs': childInformation['alsoKnownAs'] if haschildInfo else '',
                    'childBirthDate': parse(childInformation['dateOfBirth']).strftime('%Y-%m-%d') if haschildInfo and childInformation['dateOfBirth'] is not None else '',

                    'anotherFirstName': anotherpersonInformation['firstName'] if hasanotherpersonInfo else '',
                    'anotherMiddleName': anotherpersonInformation['middleName'] if hasanotherpersonInfo else '',
                    'anotherLastName': anotherpersonInformation['lastName'] if hasanotherpersonInfo else '',
                    'anotherAlsoKnownAs': anotherpersonInformation['alsoKnownAs'] if hasanotherpersonInfo else '',
                    'anotherBirthDate': parse(anotherpersonInformation['dateOfBirth']).strftime('%Y-%m-%d')  if hasanotherpersonInfo and anotherpersonInformation['dateOfBirth'] is not None else '',

                    'adoptiveMotherFirstName': adoptiveParents['motherFirstName'] if hasadoptiveParentInfo else '',
                    'adoptiveMotherLastName': adoptiveParents['motherLastName'] if hasadoptiveParentInfo else '',
                    'adoptiveFatherLastName': adoptiveParents['fatherLastName'] if hasadoptiveParentInfo else '',
                    'adoptiveFatherFirstName': adoptiveParents['fatherFirstName'] if hasadoptiveParentInfo else ''
                }
                baserequestInfo['additionalPersonalInfo'] = additionalpersonalInfo
            return baserequestInfo
        elif request != {} and request['version'] != 1 and  request['sourceofsubmission'] != "intake":
            
            request['requestrawdata']['currentState'] = request['status']            
            requeststatus = FOIRequestStatus().getrequeststatusid(request['status'])
            request['requestrawdata']['requeststatusid'] =  requeststatus['requeststatusid']
            request['requestrawdata']['lastStatusUpdateDate'] = FOIRawRequest.getLastStatusUpdateDate(requestid, request['status']).strftime('%Y-%m-%d')
            if request['status'] == 'Closed':
                request['requestrawdata']['stateTransition']= FOIRawRequest.getstatesummary(requestid)
            return request['requestrawdata']    
        elif request != {} and request['sourceofsubmission'] == "intake":            
            request['requestrawdata']['wfinstanceid'] = request['wfinstanceid']
            request['requestrawdata']['currentState'] = request['status']
            requeststatus = FOIRequestStatus().getrequeststatusid(request['status'])
            request['requestrawdata']['requeststatusid'] =  requeststatus['requeststatusid']            
            request['requestrawdata']['lastStatusUpdateDate'] = FOIRawRequest.getLastStatusUpdateDate(requestid, request['status']).strftime('%Y-%m-%d')
            request['requestrawdata']['stateTransition']= FOIRawRequest.getstatesummary(requestid)
            return request['requestrawdata']
        else:
            return None
