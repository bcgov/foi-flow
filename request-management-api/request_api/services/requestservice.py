
from re import T
from request_api import version
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.ProgramAreas import ProgramArea
from request_api.models.RequestorType import RequestorType
from request_api.models.ContactTypes import ContactType
from request_api.models.DeliveryModes import DeliveryMode
from request_api.models.ReceivedModes import ReceivedMode
from request_api.models.ApplicantCategories import ApplicantCategory
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.models.PersonalInformationAttributes import PersonalInformationAttribute
from request_api.models.FOIRequestContactInformation import FOIRequestContactInformation
from request_api.models.FOIRequestPersonalAttributes import FOIRequestPersonalAttribute
from request_api.models.FOIRequestApplicants import FOIRequestApplicant
from request_api.models.FOIRequestApplicantMappings import FOIRequestApplicantMapping
from request_api.schemas.foirequest import  FOIRequestSchema
from dateutil.parser import *
from request_api.schemas.foirequestwrapper import  FOIRequestWrapperSchema
from request_api.services.documentservice import documentservice
from request_api.services.rawrequestservice import rawrequestservice
from request_api.services.workflowservice import workflowservice
from request_api.services.watcherservice import watcherservice
from request_api.services.commentservice import commentservice
from enum import Enum
import datetime 
from datetime import datetime as datetime2
import random
from dateutil.parser import *
from request_api.utils.enums import MinistryTeamWithKeycloackGroup
import json
class requestservice:
    """ FOI Request management service

    This service class manages all CRUD operations related to an FOI RAW Request

    """

    def saverequest(self,fOIRequestsSchema, userId, foirequestid=None, ministryId=None, fileNumber=None, version=None, rawRequestId=None, wfinstanceid=None):      
        activeVersion = 1 if version is None else version
        foiMinistryRequestArr = []
        contactInformationArr = []
        personalAttributeArr = []
        requestApplicantArr = []
        fOIRequestUtil = FOIRequestUtil()

        
        #Prepare ministry records 
               
        if fOIRequestsSchema.get("selectedMinistries") is not None:
            for ministry in fOIRequestsSchema.get("selectedMinistries"):
                foiMinistryRequestArr.append(fOIRequestUtil.createMinistry(fOIRequestsSchema, ministry, activeVersion, userId, fileNumber,ministryId))           
        

        #Prepare applicant record 
        if  fOIRequestsSchema.get("additionalPersonalInfo") is not None:
            applicantInfo = fOIRequestsSchema.get("additionalPersonalInfo")
            selfdob = applicantInfo["birthDate"] if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"birthDate","additionalPersonalInfo") else None
            selfAlsoKnownAs = applicantInfo["alsoKnownAs"] if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"alsoKnownAs","additionalPersonalInfo") else None
        requestApplicantArr.append(
            fOIRequestUtil.createApplicant(fOIRequestsSchema.get("firstName"),
                                           fOIRequestsSchema.get("lastName"),
                                           "Self",
                                           userId,
                                           fOIRequestsSchema.get("middleName"),                                            
                                           fOIRequestsSchema.get("businessName"),
                                           selfAlsoKnownAs,
                                           selfdob)
            )
                 

        #Prepare additional applicants
        if fOIRequestsSchema.get("additionalPersonalInfo") is not None:
            addlApplicantInfo = fOIRequestsSchema.get("additionalPersonalInfo")
            if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"childFirstName","additionalPersonalInfo"):
                requestApplicantArr.append(
                    fOIRequestUtil.createApplicant(addlApplicantInfo["childFirstName"],
                                           addlApplicantInfo["childLastName"],
                                           "Applying for a child under 12",
                                           userId,
                                           addlApplicantInfo["childMiddleName"],                                            
                                           None,
                                           addlApplicantInfo["childAlsoKnownAs"],
                                           addlApplicantInfo["childBirthDate"] )
                    )
            if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"anotherFirstName","additionalPersonalInfo"):
                requestApplicantArr.append(
                    fOIRequestUtil.createApplicant(addlApplicantInfo["anotherFirstName"],
                                           addlApplicantInfo["anotherLastName"],
                                           "Applying for other person",
                                           userId,
                                           addlApplicantInfo["anotherMiddleName"],                                            
                                           None,
                                           addlApplicantInfo["anotherAlsoKnownAs"],
                                           addlApplicantInfo["anotherBirthDate"] )
                    )  
           
        #Prepare contact information
        contactTypes = ContactType().getcontacttypes()        
        for contact in fOIRequestUtil.contactTypeMapping():
            if fOIRequestsSchema.get(contact["key"]) is not None:   
                contactInformationArr.append(
                    fOIRequestUtil.createContactInformation(contact["key"],
                                                            contact["name"],
                                                            fOIRequestsSchema.get(contact["key"]),
                                                            contactTypes, userId)
                    )
                

        #Personal Attributes
        if fOIRequestsSchema.get("requestType") == "personal":
            attributeTypes = PersonalInformationAttribute().getpersonalattributes()
            for attrb in fOIRequestUtil.personalAttributeMapping():
                attrbvalue = None
                if attrb["location"] == "main" and fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,attrb["key"],"main") == True:
                    attrbvalue = fOIRequestsSchema.get(attrb["key"])
                if attrb["location"] == "additionalPersonalInfo" and fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema, attrb["key"],"additionalPersonalInfo") == True:
                    attrbvalue = fOIRequestsSchema.get(attrb["location"])[attrb["key"]]
                if attrbvalue is not None and attrbvalue and attrbvalue != "":
                    personalAttributeArr.append(
                        fOIRequestUtil.createPersonalAttribute(attrb["name"],
                                                            attrbvalue,
                                                            attributeTypes, userId)
                        )
        # FOI Request      
        openfOIRequest = FOIRequest()
        openfOIRequest.foirawrequestid = fOIRequestsSchema.get("foirawrequestid") if rawRequestId is None else rawRequestId
        openfOIRequest.version = activeVersion
        openfOIRequest.requesttype = fOIRequestsSchema.get("requestType")
        openfOIRequest.initialdescription = fOIRequestsSchema.get("description")
        openfOIRequest.receiveddate = fOIRequestsSchema.get("receivedDate")
        openfOIRequest.ministryRequests = foiMinistryRequestArr
        openfOIRequest.contactInformations = contactInformationArr       
        if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"fromDate","main") == True:
            openfOIRequest.initialrecordsearchfromdate = fOIRequestsSchema.get("fromDate")
        if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"toDate","main") == True:
            openfOIRequest.initialrecordsearchtodate = fOIRequestsSchema.get("toDate")
        if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"deliveryMode","main") == True:
            openfOIRequest.deliverymodeid = fOIRequestUtil.getValueOf("deliveryMode",fOIRequestsSchema.get("deliveryMode"))            
        if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"receivedMode","main") == True:    
            openfOIRequest.receivedmodeid =  fOIRequestUtil.getValueOf("receivedMode",fOIRequestsSchema.get("receivedMode"))        
        if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"category","main") == True:
            openfOIRequest.applicantcategoryid = fOIRequestUtil.getValueOf("category",fOIRequestsSchema.get("category"))            
        openfOIRequest.personalAttributes = personalAttributeArr
        openfOIRequest.requestApplicants = requestApplicantArr        
        if foirequestid is not None:         
           openfOIRequest.foirequestid = foirequestid
        openfOIRequest.wfinstanceid = wfinstanceid if wfinstanceid is not None else None
        openfOIRequest.createdby = userId
        return FOIRequest.saverequest(openfOIRequest) 

    def saveRequestVersion(self,fOIRequestsSchema, foirequestid , ministryId, userId):
        activeVersion = 1        
        fileNumber =fOIRequestsSchema.get("idNumber") 
        #Identify version       
        if foirequestid is not None:
            _foiRequest = FOIRequest().getrequest(foirequestid)
            if _foiRequest != {}:               
               activeVersion = _foiRequest["version"] + 1
            else:
                return _foiRequest  
            FOIMinistryRequest.deActivateFileNumberVersion(ministryId, fileNumber, activeVersion, userId)
            self.disablewatchers(ministryId, fOIRequestsSchema, userId)
            return self.saverequest(fOIRequestsSchema, userId, foirequestid,ministryId,fileNumber,activeVersion,_foiRequest["foirawrequestid"],_foiRequest["wfinstanceid"])    
    
    def saveMinistryRequestVersion(self,ministryrequestschema, foirequestid , ministryid, userid, usertype):
        _foirequest = FOIRequest().getrequest(foirequestid) 
        _foiministryrequest = FOIMinistryRequest().getrequestbyministryrequestid(ministryid)
        _foirequestapplicant = FOIRequestApplicantMapping().getrequestapplicants(foirequestid,_foirequest["version"])
        _foirequestcontact = FOIRequestContactInformation().getrequestcontactinformation(foirequestid,_foirequest["version"])
        _foirequestpersonalattrbs = FOIRequestPersonalAttribute().getrequestpersonalattributes(foirequestid,_foirequest["version"])
        foiministryrequestarr = []     
        foirequest = FOIRequestUtil().createFOIRequestFromObject(_foirequest, userid)
        foiministryrequest = FOIRequestUtil().createFOIMinistryRequestFromObject(_foiministryrequest, ministryrequestschema, userid)
        foiministryrequestarr.append(foiministryrequest)
        foirequest.ministryRequests = foiministryrequestarr
        foirequest.requestApplicants = FOIRequestUtil().createFOIRequestAppplicantFromObject(_foirequestapplicant, foirequestid,  _foirequest['version']+1, userid)
        foirequest.contactInformations = FOIRequestUtil().createFOIRequestContactFromObject( _foirequestcontact, foirequestid, _foirequest['version']+1, userid)
        foirequest.personalAttributes = FOIRequestUtil().createFOIRequestPersonalAttributeFromObject( _foirequestpersonalattrbs, foirequestid, _foirequest['version']+1, userid)
        FOIMinistryRequest.deActivateFileNumberVersion(ministryid, _foiministryrequest['filenumber'], _foiministryrequest['version']+1, userid)
        return FOIRequest.saverequest(foirequest)        
               
    def updaterequest(self,fOIRequestsSchema,foirequestid,userId):
        fOIRequestUtil = FOIRequestUtil()
        if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"wfinstanceid","main") == True:
            return FOIRequest.updateWFInstance(foirequestid, fOIRequestsSchema.get("wfinstanceid"), userId)
        if fOIRequestsSchema.get("selectedMinistries") is not None:
            allStatus = FOIRequestStatus().getrequeststatuses()
            updatedMinistries = []
            for ministry in fOIRequestsSchema.get("selectedMinistries"):
                for status in allStatus:
                    if ministry["status"] == status["name"]:
                        updatedMinistries.append({"filenumber" : ministry["filenumber"], "requeststatusid": status["requeststatusid"]})
            return FOIRequest.updateStatus(foirequestid, updatedMinistries, userId)
    
    def postEventToWorkflow(self, requestschema, data):        
        requeststatusid =  requestschema.get("requeststatusid") if 'requeststatusid' in requestschema  else None 
        if requeststatusid is not None:
            status = FOIRequestUtil().getStatusName(requeststatusid)
            workflowservice.postministryevent(requestschema, data, status)
            
    def postOpeneventtoworkflow(self, id, wfinstanceid, requestschema, ministries):        
        workflowservice.postintakeevent(id, wfinstanceid, requestschema, "Open", ministries)
       
    def copywatchers(self, rawrequestid, ministries, userid):
        watchers = watcherservice().getrawrequestwatchers(int(rawrequestid))
        for ministry in ministries:           
            for watcher in watchers:
                watcherschema = {"ministryrequestid":ministry["id"],"watchedbygroup":watcher["watchedbygroup"],"watchedby":watcher["watchedby"],"isactive":True}
                watcherservice().createministryrequestwatcher(watcherschema, userid, None)
                
    def copycomments(self, rawrequestid, ministries, userid):
        comments = commentservice().getrawrequestcomments(int(rawrequestid))
        for ministry in ministries:           
            commentservice().copyrequestcomment(ministry["id"], comments, userid)
            
    def copydocuments(Self, rawrequestid,ministries,userid):
        attachments = documentservice().getrequestdocuments(int(rawrequestid),"rawrequest")
        for ministry in ministries:
            documentservice().copyrequestdocuments(ministry["id"], attachments, userid)
                
    def disablewatchers(Self, ministryid, requestschema, userid):
        requeststatusid =  requestschema.get("requeststatusid") if 'requeststatusid' in requestschema  else None
        if requeststatusid is not None: 
            status = FOIRequestUtil().getStatusName(requeststatusid)
            if status == "Open":
                watchers = watcherservice().getministryrequestwatchers(int(ministryid), True)
                for watcher in watchers:
                    watcherschema = {"ministryrequestid":ministryid,"watchedbygroup":watcher["watchedbygroup"],"watchedby":watcher["watchedby"],"isactive":False}
                    watcherservice().createministryrequestwatcher(watcherschema, userid, None)
       
    def getrequest(self,foirequestid,foiministryrequestid):        
        request = FOIRequest.getrequest(foirequestid)
        requestministry = FOIMinistryRequest.getrequestbyministryrequestid(foiministryrequestid)        
        requestcontactinformation = FOIRequestContactInformation.getrequestcontactinformation(foirequestid,request['version'])
        requestapplicants = FOIRequestApplicantMapping.getrequestapplicants(foirequestid,request['version'])
        personalattributes = FOIRequestPersonalAttribute.getrequestpersonalattributes(foirequestid,request['version'])
        requestministrydivisions = FOIMinistryRequestDivision.getrequest(foiministryrequestid,requestministry['version'])
        #requestministrydocuments = FOIMinistryRequestDocument.getdocuments(foiministryrequestid)
        _receivedDate = parse(request['receiveddate'])
        
        baserequestInfo = {
            'id': request['foirequestid'],
            'requestType': request['requesttype'],
            'receivedDate': _receivedDate.strftime('%Y %b, %d'),
            'receivedDateUF': parse(request['receiveddate']).strftime('%Y-%m-%d %H:%M:%S.%f'),
            'deliverymodeid':request['deliverymode.deliverymodeid'],
            'deliveryMode':request['deliverymode.name'],
            'receivedmodeid':request['receivedmode.receivedmodeid'],
            'receivedMode':request['receivedmode.name'],
            'assignedGroup': requestministry["assignedgroup"],
            'assignedTo': requestministry["assignedto"],
            'idNumber':requestministry["filenumber"],
            'description': requestministry['description'],
            'fromDate': parse(requestministry['recordsearchfromdate']).strftime('%Y-%m-%d') if requestministry['recordsearchfromdate'] is not None else '',
            'toDate': parse(requestministry['recordsearchtodate']).strftime('%Y-%m-%d') if requestministry['recordsearchtodate'] is not None else '',
            'currentState':requestministry['requeststatus.name'],
            'requeststatusid':requestministry['requeststatus.requeststatusid'],
            'requestProcessStart': parse(requestministry['startdate']).strftime('%Y-%m-%d') if requestministry['startdate'] is not None else '',
            'dueDate':parse(requestministry['duedate']).strftime('%Y-%m-%d'),            
            'programareaid':requestministry['programarea.programareaid'],
            'category':request['applicantcategory.name'],
            'categoryid':request['applicantcategory.applicantcategoryid'],
            'assignedministrygroup':requestministry["assignedministrygroup"],
            'assignedministryperson':requestministry["assignedministryperson"],            
            'selectedMinistries':[{'code':requestministry['programarea.bcgovcode'],'name':requestministry['programarea.name'],'selected':'true'}],
            'divisions': FOIRequestUtil().getdivisions(requestministrydivisions),
            #'documents': FOIRequestUtil().getdocuments(requestministrydocuments),
            'onholdTransitionDate': FOIRequestUtil().getonholdtransition(foiministryrequestid),
            'lastStatusUpdateDate': FOIMinistryRequest.getLastStatusUpdateDate(foiministryrequestid, requestministry['requeststatus.requeststatusid']).strftime('%Y-%m-%d')
         }

        if requestministry['cfrduedate'] is not None:
            baserequestInfo.update({'cfrDueDate':parse(requestministry['cfrduedate']).strftime('%Y-%m-%d')})

        if(requestcontactinformation is not None):
            for contactinfo in requestcontactinformation:
                if contactinfo['contacttype.name'] == 'Email':
                    baserequestInfo.update({'email':contactinfo['contactinformation']})
                else:
                    baserequestInfo.update({contactinfo['dataformat']:contactinfo['contactinformation']})

        additionalPersonalInfo ={}
        if requestapplicants is not None:
           
            for applicant in requestapplicants:
                if applicant['requestortype.requestortypeid'] == 1:
                    baserequestInfo.update(
                        {
                            'firstName':applicant['foirequestapplicant.firstname'],
                            'middleName': applicant['foirequestapplicant.middlename'],
                            'lastName': applicant['foirequestapplicant.lastname'],
                            'businessName': applicant['foirequestapplicant.businessname'],                                                
                        }                    
                    )
                    additionalPersonalInfo.update({
                            
                            'birthDate' : parse(applicant['foirequestapplicant.dob']).strftime('%Y-%m-%d') if applicant['foirequestapplicant.dob'] is not None else '',
                            'alsoKnownAs': applicant['foirequestapplicant.alsoknownas']
                    })
                elif applicant['requestortype.requestortypeid'] == 2:
                    
                    additionalPersonalInfo.update(
                        {
                            'anotherFirstName':applicant['foirequestapplicant.firstname'],
                            'anotherMiddleName': applicant['foirequestapplicant.middlename'],
                            'anotherLastName': applicant['foirequestapplicant.lastname'],                            
                            'anotherBirthDate' : parse(applicant['foirequestapplicant.dob']).strftime('%Y-%m-%d') if applicant['foirequestapplicant.dob'] is not None else '' ,  
                            'anotherAlsoKnownAs': applicant['foirequestapplicant.alsoknownas'],                      
                        }                    
                    )
                elif applicant['requestortype.requestortypeid'] == 3:
                    additionalPersonalInfo.update(
                        {
                        'childFirstName': applicant['foirequestapplicant.firstname'],
                        'childMiddleName': applicant['foirequestapplicant.middlename'],
                        'childLastName': applicant['foirequestapplicant.lastname'],
                        'childAlsoKnownAs': applicant['foirequestapplicant.alsoknownas'],
                        'childBirthDate': parse(applicant['foirequestapplicant.dob']).strftime('%Y-%m-%d') if applicant['foirequestapplicant.dob'] is not None else '',                      
                        }                    
                    )

        baserequestInfo['additionalPersonalInfo'] = additionalPersonalInfo
        if personalattributes is not None:
            for personalattribute in personalattributes:
                if personalattribute['personalattributeid'] == 1:                   
                    baserequestInfo.update({'publicServiceEmployeeNumber': personalattribute['attributevalue']})
                elif  personalattribute['personalattributeid'] == 2 :    
                    baserequestInfo.update({'correctionalServiceNumber': personalattribute['attributevalue']})
                elif  personalattribute['personalattributeid'] == 3 :    
                    baserequestInfo.update({'personalHealthNumber': personalattribute['attributevalue']})    
                elif personalattribute['personalattributeid'] == 4:     
                    baserequestInfo.update({'adoptiveMotherFirstName': personalattribute['attributevalue']})
                elif personalattribute['personalattributeid'] == 5:     
                    baserequestInfo.update({'adoptiveMotherLastName': personalattribute['attributevalue']})
                elif personalattribute['personalattributeid'] == 6:     
                    baserequestInfo.update({'adoptiveFatherFirstName': personalattribute['attributevalue']})
                elif personalattribute['personalattributeid'] == 7:     
                    baserequestInfo.update({'adoptiveFatherLastName': personalattribute['attributevalue']})        
        

            
        return baserequestInfo


    def getrequestdetailsforministry(self,foirequestid,foiministryrequestid, authMembershipgroups):
        request = FOIRequest.getrequest(foirequestid)
        requestministry = FOIMinistryRequest.getrequestbyministryrequestid(foiministryrequestid)
        requestministrydivisions = FOIMinistryRequestDivision.getrequest(foiministryrequestid,requestministry['version'])
        #requestministrydocuments = FOIMinistryRequestDocument.getdocuments(foiministryrequestid)
        baserequestInfo = {}
        if requestministry["assignedministrygroup"] in authMembershipgroups:

            _receivedDate = parse(request['receiveddate'])        
            baserequestInfo = {
                'id': request['foirequestid'],
                'requestType': request['requesttype'],
                'receivedDate': _receivedDate.strftime('%Y %b, %d'),
                'receivedDateUF': parse(request['receiveddate']).strftime('%Y-%m-%d %H:%M:%S.%f'),
                'deliverymodeid':request['deliverymode.deliverymodeid'],
                'deliveryMode':request['deliverymode.name'],
                'receivedmodeid':request['receivedmode.receivedmodeid'],
                'receivedMode':request['receivedmode.name'],
                'assignedGroup': requestministry["assignedgroup"],
                'assignedTo': requestministry["assignedto"],
                'idNumber':requestministry["filenumber"],
                'description': requestministry['description'],
                'fromDate': parse(requestministry['recordsearchfromdate']).strftime('%Y-%m-%d') if requestministry['recordsearchfromdate'] is not None else '',
                'toDate': parse(requestministry['recordsearchtodate']).strftime('%Y-%m-%d') if requestministry['recordsearchtodate'] is not None else '',
                'currentState':requestministry['requeststatus.name'],
                'requeststatusid':requestministry['requeststatus.requeststatusid'],
                'requestProcessStart': parse(requestministry['startdate']).strftime('%Y-%m-%d') if requestministry['startdate'] is not None else '',
                'dueDate':parse(requestministry['duedate']).strftime('%Y-%m-%d'),            
                'programareaid':requestministry['programarea.programareaid'],
                'category':request['applicantcategory.name'],
                'categoryid':request['applicantcategory.applicantcategoryid'],
                'assignedministrygroup':requestministry["assignedministrygroup"],
                'assignedministryperson':requestministry["assignedministryperson"],                
                'selectedMinistries':[{'code':requestministry['programarea.bcgovcode'],'name':requestministry['programarea.name'],'selected':'true'}],
                'divisions': FOIRequestUtil().getdivisions(requestministrydivisions),
               # 'documents': FOIRequestUtil().getdocuments(requestministrydocuments),
                'onholdTransitionDate': FOIRequestUtil().getonholdtransition(foiministryrequestid)
            }

            if requestministry['cfrduedate'] is not None:
                baserequestInfo.update({'cfrDueDate':parse(requestministry['cfrduedate']).strftime('%Y-%m-%d')})

        return baserequestInfo

class FOIRequestUtil: 
    
    def createFOIRequestFromObject(self, foiobject, userid):
        foirequest = FOIRequest()  
        foirequest.foirawrequestid = foiobject['foirawrequestid']
        foirequest.foirequestid =  foiobject['foirequestid']
        foirequest.version = foiobject["version"] + 1
        foirequest.initialdescription =  foiobject['initialdescription']
        foirequest.initialrecordsearchfromdate = foiobject['initialrecordsearchfromdate'] if 'initialrecordsearchfromdate' in foiobject  else None
        foirequest.initialrecordsearchtodate = foiobject['initialrecordsearchfromdate'] if 'initialrecordsearchfromdate' in foiobject  else None
        foirequest.receiveddate = foiobject['receiveddate'] if 'receiveddate' in foiobject  else None
        foirequest.requesttype = foiobject['requesttype']
        foirequest.wfinstanceid = foiobject['wfinstanceid']       
        foirequest.applicantcategoryid =  foiobject["applicantcategory.applicantcategoryid"]
        foirequest.deliverymodeid =  foiobject["deliverymode.deliverymodeid"]
        foirequest.receivedmodeid =  foiobject["receivedmode.receivedmodeid"]
        foirequest.createdby = userid
        return foirequest
    
    def createFOIMinistryRequestFromObject(self, ministryschema, requestschema, userid):
        foiministryrequest = FOIMinistryRequest()
        foiministryrequest.foiministryrequestid = ministryschema["foiministryrequestid"] 
        foiministryrequest.version = ministryschema["version"] + 1
        foiministryrequest.foirequest_id = ministryschema["foirequest_id"] 
        foiministryrequest.foirequestversion_id = ministryschema["foirequestversion_id"] 
        foiministryrequest.description = ministryschema["description"]
        foiministryrequest.recordsearchfromdate = ministryschema['recordsearchfromdate'] if 'recordsearchfromdate' in ministryschema  else None
        foiministryrequest.recordsearchtodate = ministryschema['recordsearchtodate'] if 'recordsearchtodate' in ministryschema  else None
        foiministryrequest.filenumber = ministryschema["filenumber"]
        foiministryrequest.cfrduedate = ministryschema['cfrduedate'] if 'cfrduedate' in ministryschema  else None
        foiministryrequest.startdate = ministryschema['startdate'] if 'startdate' in ministryschema  else None
        foiministryrequest.duedate =ministryschema['duedate'] if 'duedate' in ministryschema  else None
        foiministryrequest.assignedministrygroup = requestschema['assignedministrygroup'] if 'assignedministrygroup' in requestschema  else ministryschema["assignedministrygroup"]
        foiministryrequest.assignedministryperson = requestschema['assignedministryperson'] if 'assignedministryperson' in requestschema  else ministryschema["assignedministryperson"]
        foiministryrequest.assignedgroup = requestschema['assignedgroup'] if 'assignedgroup' in requestschema  else ministryschema["assignedgroup"]
        foiministryrequest.assignedto = requestschema['assignedto'] if 'assignedto' in requestschema  else ministryschema["assignedto"]
        foiministryrequest.requeststatusid = requestschema['requeststatusid'] if  'requeststatusid' in requestschema  else  ministryschema["requeststatus.requeststatusid"]
        foiministryrequest.programareaid = ministryschema["programarea.programareaid"] if 'programarea.programareaid' in ministryschema  else None
        foiministryrequest.createdby = userid
        if 'divisions' in requestschema:
            foiministryrequest.divisions = FOIRequestUtil().createFOIRequestDivision(requestschema,ministryschema["foiministryrequestid"] ,ministryschema["version"] + 1, userid)  
        else:
            divisions = FOIMinistryRequestDivision().getrequest(ministryschema["foiministryrequestid"] ,ministryschema["version"])
            foiministryrequest.divisions = FOIRequestUtil().createFOIRequestDivisionFromObject(divisions,ministryschema["foiministryrequestid"] ,ministryschema["version"] + 1, userid)  
        foiministryrequest.documents = FOIRequestUtil().createFOIRequestDocuments(requestschema,ministryschema["foiministryrequestid"] ,ministryschema["version"] +1 , userid)       
        foiministryrequest.closedate = requestschema['closedate'] if 'closedate' in requestschema  else None
        foiministryrequest.closereasonid = requestschema['closereasonid'] if 'closereasonid' in requestschema  else None
        return foiministryrequest
    
    def createFOIRequestDocuments(self,requestschema, ministryrequestid, activeversion, userid):
        if 'documents' in requestschema:
            return FOIRequestUtil().createFOIRequestDocument(requestschema,ministryrequestid ,activeversion, userid)  
        else:
            documents = FOIMinistryRequestDocument().getdocuments(ministryrequestid, activeversion-1)
            return FOIRequestUtil().createFOIRequestDocumentFromObject(documents,ministryrequestid ,activeversion, userid)       
        
    
    def createFOIRequestAppplicantFromObject(self, requestapplicants, requestid, version, userid): 
        requestapplicantarr = []
        for requestapplicant in requestapplicants:
            applicantmapping  = FOIRequestApplicantMapping()
            applicantmapping.foirequest_id = requestid
            applicantmapping.foirequestversion_id = version
            applicantmapping.foirequestapplicantid = requestapplicant["foirequestapplicant.foirequestapplicantid"]
            applicantmapping.requestortypeid = requestapplicant["requestortype.requestortypeid"]
            applicantmapping.createdby = userid
            requestapplicantarr.append(applicantmapping)
        return requestapplicantarr

    def createFOIRequestContactFromObject(self, requestcontacts, requestid, version, userid):
        requestcontactarr = []
        for requestcontact in requestcontacts:
            contactinfo  = FOIRequestContactInformation()
            contactinfo.contacttypeid = requestcontact["contacttype.contacttypeid"]
            contactinfo.foirequest_id = requestid
            contactinfo.foirequestversion_id = version
            contactinfo.contactinformation = requestcontact["contactinformation"]
            contactinfo.dataformat = requestcontact["dataformat"]
            contactinfo.createdby = userid
            requestcontactarr.append(contactinfo)
        return requestcontactarr
    
    def createFOIRequestDivision(self, requestschema, requestid, version, userid):
        divisionarr = []
        if 'divisions' in  requestschema:
            for division in requestschema['divisions']:
                ministrydivision = FOIMinistryRequestDivision()
                ministrydivision.divisionid = division["divisionid"]
                ministrydivision.stageid = division["stageid"]
                ministrydivision.foiministryrequest_id = requestid
                ministrydivision.foiministryrequestversion_id = version
                ministrydivision.createdby = userid
                divisionarr.append(ministrydivision)
            return divisionarr

    def createFOIRequestDocument(self, requestschema, requestid, version, userid):
        documentarr = []
        if 'documents' in  requestschema:
            for document in requestschema['documents']:
                ministrydocument = FOIMinistryRequestDocument()
                ministrydocument.documentpath = document["documentpath"]
                ministrydocument.filename = document["filename"]
                if 'category' in document:
                    ministrydocument.category = document['category']
                ministrydocument.version = 1
                ministrydocument.foiministryrequest_id = requestid
                ministrydocument.foiministryrequestversion_id = version
                ministrydocument.createdby = userid
                documentarr.append(ministrydocument)
            return documentarr        
        
    
    def createFOIRequestDivisionFromObject(self, divisions, requestid, version, userid):
        divisionarr = []
        for division in divisions:
            ministrydivision = FOIMinistryRequestDivision()
            ministrydivision.divisionid = division["division.divisionid"]
            ministrydivision.stageid = division["stage.stageid"]
            ministrydivision.foiministryrequest_id = requestid
            ministrydivision.foiministryrequestversion_id = version
            ministrydivision.createdby = userid
            divisionarr.append(ministrydivision)
        return divisionarr
   
    def createFOIRequestDocumentFromObject(self, documents, requestid, activeversion, userid):
        documentarr = []
        for document in documents:
            ministrydocument = FOIMinistryRequestDocument()
            ministrydocument.documentpath = document["documentpath"]
            if 'filename' in document:
                ministrydocument.filename = document["filename"]
            if 'category' in document:
                ministrydocument.category = document['category']
            ministrydocument.version = 1
            ministrydocument.foiministryrequest_id = requestid
            ministrydocument.foiministryrequestversion_id = activeversion
            ministrydocument.created_at = document["created_at"] if 'created_at' in document else None
            ministrydocument.createdby =  document["createdby"] if 'createdby' in document else userid
            documentarr.append(ministrydocument)
        return documentarr   
    
    def createFOIRequestPersonalAttributeFromObject(self,personalattributes, requestid, version, userid):
        personalattributesarr = []
        for personalattribute in personalattributes:
            attribute = FOIRequestPersonalAttribute()
            attribute.personalattributeid = personalattribute["personalattributeid"]
            attribute.attributevalue = personalattribute["attributevalue"]
            attribute.foirequest_id = requestid
            attribute.foirequestversion_id = version
            attribute.createdby = userid
            personalattributesarr.append(attribute)
        return personalattributesarr
        
    
    def createMinistry(self, requestSchema, ministry, activeVersion, userId, fileNumber=None, ministryId=None):               
        foiministryRequest = FOIMinistryRequest()
        foiministryRequest.__dict__.update(ministry)
        foiministryRequest.requeststatusid = requestSchema.get("requeststatusid")
        if ministryId is not None:
            foiministryRequest.foiministryrequestid = ministryId
            activeVersion = FOIMinistryRequest.getversionforrequest(ministryId)[0]+1
        foiministryRequest.isactive = True
        foiministryRequest.filenumber = self.generateFileNumber(ministry["code"], requestSchema.get("foirawrequestid")) if fileNumber is None else fileNumber
        foiministryRequest.programareaid = self.getValueOf("programArea",ministry["code"])
        foiministryRequest.description = requestSchema.get("description")
        foiministryRequest.duedate = requestSchema.get("dueDate")
        if requestSchema.get("cfrDueDate") is not None and requestSchema.get("cfrDueDate")  != "":
            foiministryRequest.cfrduedate = requestSchema.get("cfrDueDate")        
        foiministryRequest.startdate = requestSchema.get("startDate")
        foiministryRequest.created_at = datetime2.now().isoformat()
        foiministryRequest.createdby = userId
        requeststatusid =  requestSchema.get("requeststatusid") if 'requeststatusid' in requestSchema  else None
        if requeststatusid is not None:
            status = FOIRequestUtil().getStatusName(requeststatusid)       
            if status == "Call For Records" or status == "Review" or status == "Consult" or status == "Fee Assessed" or status == "Ministry Sign Off" or status == "Response":
                foiministryRequest.assignedministrygroup = MinistryTeamWithKeycloackGroup[ministry["code"]].value
        if self.isNotBlankorNone(requestSchema,"fromDate","main") == True:
            foiministryRequest.recordsearchfromdate = requestSchema.get("fromDate")
        if self.isNotBlankorNone(requestSchema,"toDate","main") == True:
            foiministryRequest.recordsearchtodate = requestSchema.get("toDate")        
        foiministryRequest.assignedgroup = requestSchema.get("assignedGroup")
        if self.isNotBlankorNone(requestSchema,"assignedTo","main") == True:
            foiministryRequest.assignedto = requestSchema.get("assignedTo")
        if self.isNotBlankorNone(requestSchema,"assignedministrygroup","main") == True:
            foiministryRequest.assignedministrygroup = requestSchema.get("assignedministrygroup")
        if self.isNotBlankorNone(requestSchema,"assignedministryperson","main") == True:
            foiministryRequest.assignedministryperson = requestSchema.get("assignedministryperson")
        if ministryId is not None:
            divisions = FOIMinistryRequestDivision().getrequest(ministryId , activeVersion-1)
            foiministryRequest.divisions = FOIRequestUtil().createFOIRequestDivisionFromObject(divisions, ministryId, activeVersion, userId)  
            foiministryRequest.documents = FOIRequestUtil().createFOIRequestDocuments(requestSchema,ministryId , activeVersion , userId)       
        foiministryRequest.version = activeVersion
        foiministryRequest.closedate = requestSchema.get("closedate") if 'closedate' in requestSchema  else None
        foiministryRequest.closereasonid = requestSchema.get("closereasonid") if 'closereasonid' in requestSchema  else None
        return foiministryRequest
    
    def createContactInformation(self,dataformat, name, value, contactTypes, userId):
        contactInformation = FOIRequestContactInformation()
        contactInformation.contactinformation = value
        contactInformation.dataformat = dataformat
        contactInformation.createdby = userId
        for contactType in contactTypes:
            if contactType["name"] == name:
              contactInformation.contacttypeid =contactType["contacttypeid"]              
        return contactInformation
    
    def createApplicant(self,firstName, lastName, appltcategory, userId, middleName = None,businessName = None, alsoknownas = None, dob = None):
        requestApplicant = FOIRequestApplicantMapping()
        applicant = FOIRequestApplicant()
        applicant.createdby = userId
        if firstName is not None and firstName != "":
            applicant.firstname = firstName
        if lastName is not None and lastName != "":
            applicant.lastname = lastName
        if middleName is not None and middleName != "":
            applicant.middlename = middleName
        if businessName is not None and businessName != "":
           applicant.businessname = businessName
        if alsoknownas is not None and alsoknownas != "":
            applicant.alsoknownas = alsoknownas
        if dob is not None and dob != "":
            applicant.dob = dob
        _applicant = FOIRequestApplicant().getrequest(applicant)
        if _applicant == {} :
            _applicant = FOIRequestApplicant().saverequest(applicant)
            requestApplicant.foirequestapplicantid = _applicant.identifier
        else:
            requestApplicant.foirequestapplicantid = _applicant["foirequestapplicantid"]
        if appltcategory is not None:           
            requestertype = RequestorType().getrequestortype(appltcategory)  
            requestApplicant.requestortypeid = requestertype["requestortypeid"]
        return requestApplicant
    
    def createPersonalAttribute(self, name, value,attributeTypes, userId):
        personalAttribute = FOIRequestPersonalAttribute()
        personalAttribute.createdby = userId
        if value is not None and value !="" and value:
            for attributeType in attributeTypes:
                if attributeType["name"] == name:
                    personalAttribute.personalattributeid = attributeType["attributeid"]
                    personalAttribute.attributevalue = value
        return personalAttribute
    
    def getdivisions(self, ministrydivisions):
        divisions = []
        if ministrydivisions is not None:            
            for ministrydivision in ministrydivisions:
                division = {
                    "foiministrydivisionid": ministrydivision["foiministrydivisionid"],
                    "divisionid": ministrydivision["division.divisionid"],
                    "divisionname": ministrydivision["division.name"],
                    "stageid": ministrydivision["stage.stageid"],
                    "stagename": ministrydivision["stage.name"],
                    } 
                divisions.append(division)
        return divisions
    
    def getdocuments(self, ministrydocuments):
        documents = []
        if ministrydocuments is not None:            
            for ministrydocument in ministrydocuments:
                document = {
                    "documentpath": ministrydocument["documentpath"],
                    "filename": ministrydocument["filename"],
                    "createdby": ministrydocument["createdby"],
                    "createdat": parse(ministrydocument["created_at"]).strftime('%Y-%m-%d %H:%M:%S.%f')
                    } 
                documents.append(document)
        return documents
    
    def getonholdtransition(self, foiministryrequestid):
        onholddate = None
        transitions = FOIMinistryRequest.getrequeststatusById(foiministryrequestid)
        for entry in transitions:
            if entry['requeststatusid'] == 11:
                onholddate = parse(str(entry['created_at'])).strftime("%Y-%m-%d")
            else:
                if onholddate is not None:
                    break;
        return onholddate;
    
    def getStatusName(self,requeststatusid):
        allStatus = FOIRequestStatus().getrequeststatuses()
        for status in allStatus:
            if status["requeststatusid"] == requeststatusid:
                return status["name"]
        return None;
    
    def geteventtype(self,filenumber, version, status):
        ministryreq = FOIMinistryRequest.getrequestbyfilenumberandversion(filenumber,version-1)
        prevstatus = ministryreq["requeststatus.name"]
        event = "save" if prevstatus == status else "complete"
        return event
    
    
    def getValueOf(self,name,key):
        if name == "receivedMode":
            rmode = ReceivedMode().getreceivedmode(key)
            return rmode["receivedmodeid"]
        elif name == "deliveryMode":
            dmode = DeliveryMode().getdeliverymode(key)
            return dmode["deliverymodeid"]
        elif name == "category":
            applcategory = ApplicantCategory().getapplicantcategory(key)
            return applcategory["applicantcategoryid"]
        elif name == "programArea":
            pgArea = ProgramArea().getprogramarea(key)
            return pgArea["programareaid"]
        
    
    def generateFileNumber(self, code, id):
        tmp = str(id)
        curSize = len(tmp)
        N = 5 - curSize
        randomNum = random.randint(pow(10, N-1), pow(10, N) - 1)
        return code + "-" + str(datetime.date.today().year) + "-" + tmp + str(randomNum)
    
    def isNotBlankorNone(self, dataSchema, key, location):
        if location == "main":
            if key in dataSchema and  dataSchema.get(key) is not None and dataSchema.get(key)  and dataSchema.get(key)  != "":
                return True
        if location == "additionalPersonalInfo":
            if key in dataSchema.get(location) and dataSchema.get(location)[key] and dataSchema.get(location)[key] is not None and dataSchema.get(location)[key] !="":     
                return True
        return False          
    
            
    def contactTypeMapping(self):
        return [{"name": "Email", "key" : "email"},
            {"name": "Home Phone", "key" : "phonePrimary"},
            {"name": "Work Phone", "key" : "workPhonePrimary"},
            {"name": "Mobile Phone", "key" : "phoneSecondary"},
            {"name": "Work Phone 2", "key" : "workPhoneSecondary"},
            {"name": "Street Address", "key" : "address"},
            {"name": "Street Address", "key" : "addressSecondary"},
            {"name": "Street Address", "key" : "city"},
            {"name": "Street Address", "key" : "province"},
            {"name": "Street Address", "key" : "postal"},
            {"name": "Street Address", "key" : "country"}]
        
    def personalAttributeMapping(self):
        return [{"name": "BC Correctional Service Number", "key" : "correctionalServiceNumber", "location":"main"},
            {"name": "BC Public Service Employee Number", "key" : "publicServiceEmployeeNumber", "location":"main"},
            {"name": "BC Personal Health Care Number", "key" : "personalHealthNumber", "location":"additionalPersonalInfo"},
            {"name": "Adoptive Mother First Name", "key" : "adoptiveMotherFirstName", "location":"additionalPersonalInfo"},
            {"name": "Adoptive Mother Last Name", "key" : "adoptiveMotherLastName", "location":"additionalPersonalInfo"},
            {"name": "Adoptive Father First Name", "key" : "adoptiveFatherFirstName", "location":"additionalPersonalInfo"},
            {"name": "Adoptive Father Last Name", "key" : "adoptiveFatherLastName", "location":"additionalPersonalInfo"}
                ]

            
    
    



