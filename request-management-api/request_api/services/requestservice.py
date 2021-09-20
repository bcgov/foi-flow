
from re import T
from request_api import version
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
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
from request_api.services.rawrequestservice import rawrequestservice
from request_api.services.external.bpmservice import bpmservice
from enum import Enum
import datetime
import random
from dateutil.parser import *
class requestservice:
    """ FOI Request management service

    This service class manages all CRUD operations related to an FOI RAW Request

    """

    def saverequest(self,fOIRequestsSchema, foirequestid=None, ministryId=None, fileNumber=None, version=None, rawRequestId=None, wfinstanceid=None):      
        activeVersion = 1 if version is None else version
        foiMinistryRequestArr = []
        contactInformationArr = []
        personalAttributeArr = []
        requestApplicantArr = []
        fOIRequestUtil = FOIRequestUtil()

        
        #Prepare ministry records  
               
        if fOIRequestsSchema.get("selectedMinistries") is not None:
            for ministry in fOIRequestsSchema.get("selectedMinistries"):
                foiMinistryRequestArr.append(fOIRequestUtil.createMinistry(fOIRequestsSchema, ministry, activeVersion,fileNumber,ministryId))           
        

        #Prepare applicant record 
        if  fOIRequestsSchema.get("additionalPersonalInfo") is not None:
            applicantInfo = fOIRequestsSchema.get("additionalPersonalInfo")
            selfdob = applicantInfo["birthDate"] if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"birthDate","additionalPersonalInfo") else None
            selfAlsoKnownAs = applicantInfo["alsoKnownAs"] if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"alsoKnownAs","additionalPersonalInfo") else None
        requestApplicantArr.append(
            fOIRequestUtil.createApplicant(fOIRequestsSchema.get("firstName"),
                                           fOIRequestsSchema.get("lastName"),
                                           "Self",
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
                                                            contactTypes)
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
                                                            attributeTypes)
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
        if wfinstanceid is not None:         
           openfOIRequest.wfinstanceid = wfinstanceid 
        
        return FOIRequest.saverequest(openfOIRequest) 

    def saveRequestVersion(self,fOIRequestsSchema, foirequestid , ministryId):
        activeVersion = 1        
        fileNumber =fOIRequestsSchema.get("idNumber") 
        #Identify version       
        if foirequestid is not None:
            _foiRequest = FOIRequest().getrequest(foirequestid)
            if _foiRequest != {}:               
               activeVersion = _foiRequest["version"] + 1
            else:
                return _foiRequest  
            FOIMinistryRequest.deActivateFileNumberVersion(ministryId, fileNumber, activeVersion)
            return self.saverequest(fOIRequestsSchema,foirequestid,ministryId,fileNumber,activeVersion,_foiRequest["foirawrequestid"],_foiRequest["wfinstanceid"])    
          
        
    def updaterequest(self,fOIRequestsSchema,foirequestid):
        fOIRequestUtil = FOIRequestUtil()
        if fOIRequestUtil.isNotBlankorNone(fOIRequestsSchema,"wfinstanceid","main") == True:
            return FOIRequest.updateWFInstance(foirequestid, fOIRequestsSchema.get("wfinstanceid"))
        if fOIRequestsSchema.get("selectedMinistries") is not None:
            allStatus = FOIRequestStatus().getrequeststatuses()
            updatedMinistries = []
            for ministry in fOIRequestsSchema.get("selectedMinistries"):
                for status in allStatus:
                    if ministry["status"] == status["name"]:
                        updatedMinistries.append({"filenumber" : ministry["filenumber"], "requeststatusid": status["requeststatusid"]})
            return FOIRequest.updateStatus(foirequestid, updatedMinistries)
    
    def postEventToWorkflow(self,workflowId, data):
         return bpmservice.complete(workflowId, data)
    
    def updateEventToWorkflow(self,fOIRequestsSchema, data):
        fileNumber = fOIRequestsSchema.get("idNumber") if 'idNumber' in fOIRequestsSchema  else None 
        assignedGroup = fOIRequestsSchema.get("assignedGroup") if 'assignedGroup' in fOIRequestsSchema  else None  
        assignedTo = fOIRequestsSchema.get("assignedTo") if 'assignedTo' in fOIRequestsSchema  else None   
        if data.get("ministries") is not None:
            for ministry in data.get("ministries"):    
                if ministry["filenumber"] == fileNumber and ministry["status"] == "Open":
                        bpmservice.openedclaim(fileNumber, assignedGroup, assignedTo)
       

       
    def getrequest(self,foirequestid,foiministryrequestid):        
        request = FOIRequest.getrequest(foirequestid)
        requestministry = FOIMinistryRequest.getrequestbyministryrequestid(foiministryrequestid)        
        requestcontactinformation = FOIRequestContactInformation.getrequestcontactinformation(foirequestid,request['version'])
        requestapplicants = FOIRequestApplicantMapping.getrequestapplicants(foirequestid,request['version'])
        personalattributes = FOIRequestPersonalAttribute.getrequestpersonalattributes(foirequestid,request['version'])

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
            'selectedMinistries':[{'code':requestministry['programarea.bcgovcode'],'name':requestministry['programarea.name'],'selected':'true'}]
         }

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

class FOIRequestUtil:   
    
    def createMinistry(self, requestSchema, ministry, activeVersion, fileNumber=None, ministryId=None):
        foiministryRequest = FOIMinistryRequest()
        foiministryRequest.__dict__.update(ministry)
        foiministryRequest.version = activeVersion
        foiministryRequest.requeststatusid = requestSchema.get("requeststatusid")
        if ministryId is not None:
            foiministryRequest.foiministryrequestid = ministryId
        foiministryRequest.isactive = True
        foiministryRequest.filenumber = self.generateFileNumber(ministry["code"], requestSchema.get("foirawrequestid")) if fileNumber is None else fileNumber
        foiministryRequest.programareaid = self.getValueOf("programArea",ministry["code"])
        foiministryRequest.description = requestSchema.get("description")
        foiministryRequest.duedate = requestSchema.get("dueDate")
        foiministryRequest.startdate = requestSchema.get("startDate")
        if self.isNotBlankorNone(requestSchema,"fromDate","main") == True:
            foiministryRequest.recordsearchfromdate = requestSchema.get("fromDate")
        if self.isNotBlankorNone(requestSchema,"toDate","main") == True:
            foiministryRequest.recordsearchtodate = requestSchema.get("toDate")        
        foiministryRequest.assignedgroup = requestSchema.get("assignedGroup")
        if self.isNotBlankorNone(requestSchema,"assignedTo","main") == True:
            foiministryRequest.assignedto = requestSchema.get("assignedTo")
        return foiministryRequest
    
    def createContactInformation(self,dataformat, name, value, contactTypes):
        contactInformation = FOIRequestContactInformation()
        contactInformation.contactinformation = value
        contactInformation.dataformat = dataformat
        for contactType in contactTypes:
            if contactType["name"] == name:
              contactInformation.contacttypeid =contactType["contacttypeid"]              
        return contactInformation
    
    def createApplicant(self,firstName, lastName, appltcategory, middleName = None,businessName = None, alsoknownas = None, dob = None):
        requestApplicant = FOIRequestApplicantMapping()
        applicant = FOIRequestApplicant()
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
    
    def createPersonalAttribute(self, name, value,attributeTypes):
        personalAttribute = FOIRequestPersonalAttribute()
        if value is not None and value !="" and value:
            for attributeType in attributeTypes:
                if attributeType["name"] == name:
                    personalAttribute.personalattributeid = attributeType["attributeid"]
                    personalAttribute.attributevalue = value
        return personalAttribute
    
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

            
    
    



