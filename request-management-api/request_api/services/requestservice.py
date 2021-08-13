
from request_api import version
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.ProgramAreas import ProgramArea
from request_api.models.ApplicantCategories import ApplicantCategory
from request_api.models.ContactTypes import ContactType
from request_api.models.DeliveryModes import DeliveryMode
from request_api.models.ReceivedModes import ReceivedMode
from request_api.models.PersonalInformationAttributes import PersonalInformationAttribute
from request_api.models.FOIRequestContactInformation import FOIRequestContactInformation
from request_api.models.FOIRequestPersonalAttributes import FOIRequestPersonalAttribute
from request_api.models.FOIRequestApplicants import FOIRequestApplicant
from request_api.models.FOIRequestApplicantMappings import FOIRequestApplicantMapping
from request_api.schemas.foirequest import  FOIRequestSchema
from request_api.schemas.foirequestwrapper import  FOIRequestWrapperSchema
from enum import Enum
import datetime
import random
class requestservice:
    """ FOI Request management service

    This service class manages all CRUD operations related to an FOI RAW Request

    """

    def saverequest(foiRequest,foirequestid = None):
        fOIRequestsSchema = FOIRequestWrapperSchema().load(foiRequest)
        activeVersion = 1 
        foiMinistryRequestArr = []
        contactInformationArr = []
        personalAttributeArr = []
        requestApplicantArr = []
        fOIRequestUtil = FOIRequestUtil()
        _fOIRequest = FOIRequest()
        #Identify version       
        if foirequestid is not None:
            _foiRequest = FOIRequest.getrequest(foirequestid)
            if _foiRequest != {}:
               activeVersion = _foiRequest["version"] + 1
            else:
                return _foiRequest
        
        #Prepare ministry records
        if fOIRequestsSchema.get("selectedMinistries") is not None:
            for  ministry in  fOIRequestsSchema.get("selectedMinistries"):
                foiministryRequest = FOIMinistryRequest()
                foiministryRequest.__dict__.update(ministry)
                foiministryRequest.version = activeVersion
                foiministryRequest.requeststatusid = 1
                foiministryRequest.isactive = True 
                foiministryRequest.filenumber = fOIRequestUtil.generateFileNumber(ministry["code"], fOIRequestsSchema.get("foirawrequestid"))
                programArea = ProgramArea.getprogramarea(ministry["code"])
                foiministryRequest.programareaid = programArea["programareaid"]
                foiministryRequest.description = fOIRequestsSchema.get("description")
                foiministryRequest.duedate = fOIRequestsSchema.get("dueDate")
                foiministryRequest.assignedto = fOIRequestsSchema.get("assignedTo")
                foiMinistryRequestArr.append(foiministryRequest)           
        

        #Prepare applicant record 
        requestApplicantArr.append(
            fOIRequestUtil.createApplicant(fOIRequestsSchema.get("firstName"),
                                           fOIRequestsSchema.get("lastName"),
                                           None,
                                           fOIRequestsSchema.get("middleName"),                                            
                                           fOIRequestsSchema.get("businessName"),
                                           fOIRequestsSchema.get("alsoknownas"),
                                           fOIRequestsSchema.get("dob") )
            )
                 

        #Prepare additional applicants
        if fOIRequestsSchema.get("additionalPersonalInfo") is not None:
            addlApplicantInfo = fOIRequestsSchema.get("additionalPersonalInfo")
            if addlApplicantInfo["childFirstName"] is not None and addlApplicantInfo["childFirstName"] !="":
                requestApplicantArr.append(
                    fOIRequestUtil.createApplicant(addlApplicantInfo["childFirstName"],
                                           addlApplicantInfo["childLastName"],
                                           "Applying for a child under 12",
                                           addlApplicantInfo["childMiddleName"],                                            
                                           None,
                                           addlApplicantInfo["childAlsoKnownAs"],
                                           addlApplicantInfo["childBirthDate"] )
                    )
            if addlApplicantInfo["anotherFirstName"] is not None and addlApplicantInfo["anotherFirstName"] != "":
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
        attributeTypes = PersonalInformationAttribute().getpersonalattributes()
        for attrb in fOIRequestUtil.personalAttributeMapping():
            if attrb["location"] == "main":
                attrbvalue = fOIRequestsSchema.get(attrb["key"])
            else:
                attrbvalue = fOIRequestsSchema.get(attrb["location"])[attrb["key"]]
            if attrbvalue is not None and attrbvalue and attrbvalue != "":
                personalAttributeArr.append(
                    fOIRequestUtil.createPersonalAttribute(attrb["name"],
                                                            attrbvalue,
                                                            attributeTypes)
                    )
        # FOI Request         
        openfOIRequest = FOIRequest()
        openfOIRequest.version = activeVersion 
        openfOIRequest.requesttype = fOIRequestsSchema.get("requestType")
        openfOIRequest.ministryRequests = foiMinistryRequestArr
        openfOIRequest.contactInformations = contactInformationArr       
        
        if fOIRequestsSchema.get("deliveryMode") is not None and fOIRequestsSchema.get("deliveryMode") and fOIRequestsSchema.get("deliveryMode") != "":
            dmode = DeliveryMode().getdeliverymode(fOIRequestsSchema.get("deliveryMode"))
            openfOIRequest.deliverymodeid = dmode["deliverymodeid"]
            
        if fOIRequestsSchema.get("receivedMode") is not None and fOIRequestsSchema.get("receivedMode") and fOIRequestsSchema.get("receivedMode") != "":    
            rmode = ReceivedMode().getreceivedmode(fOIRequestsSchema.get("receivedMode"))
            openfOIRequest.receivedmodeid = rmode["receivedmodeid"]
            
        openfOIRequest.personalAttributes = personalAttributeArr
        openfOIRequest.requestApplicants = requestApplicantArr
        
        if foirequestid is not None:         
           openfOIRequest.foirequestid = foirequestid 
        
        return FOIRequest.saverequest(openfOIRequest)
    

class FOIRequestUtil:   
    
    def createContactInformation(self,dataformat, name, value, contactTypes):
        contactInformation = FOIRequestContactInformation()
        contactInformation.contactinformation = value
        contactInformation.dataformat = dataformat
        for contactType in contactTypes:
            if contactType["name"] == name:
              contactInformation.contacttypeid =contactType["contacttypeid"]              
        return contactInformation
    
    def createApplicant(self,firstName, lastName, category, middleName = None,businessName = None, alsoknownas = None, dob = None):
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
        _applicant = FOIRequestApplicant.getrequest(applicant)
        if _applicant == {} :
            _applicant = FOIRequestApplicant.saverequest(applicant)
            requestApplicant.foirequestapplicantid = _applicant.identifier
        else:
            requestApplicant.foirequestapplicantid = _applicant["foirequestapplicantid"]
        if category is not None:           
            applicantCategory = ApplicantCategory.getapplicantcategory(category)   
            requestApplicant.requestortypeid = applicantCategory["applicantcategoryid"]
        return requestApplicant
    
    def createPersonalAttribute(self, name, value,attributeTypes):
        personalAttribute = FOIRequestPersonalAttribute()
        if value is not None and value !="" and value:
            for attributeType in attributeTypes:
                if attributeType["name"] == name:
                    personalAttribute.personalattributeid = attributeType["attributeid"]
                    personalAttribute.attributevalue = value
        return personalAttribute
    
    def generateFileNumber(self, code, id):
        tmp = str(id)
        curSize = len(tmp)
        N = 5 - curSize
        randomNum = random.randint(pow(10, N-1), pow(10, N) - 1)
        return code + "-" + str(datetime.date.today().year) + "-" + tmp + str(randomNum)
    
            
    def contactTypeMapping(self):
        return [{"name": "Home Phone", "key" : "phonePrimary"},
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
            {"name": "BC Personal Health Care Number", "key" : "personalHealthNumber", "location":"main"},
            {"name": "Adoptive Mother First Name", "key" : "adoptiveMotherFirstName", "location":"additionalPersonalInfo"},
            {"name": "Adoptive Mother Last Name", "key" : "adoptiveMotherLastName", "location":"additionalPersonalInfo"},
            {"name": "Adoptive Father First Name", "key" : "adoptiveFatherFirstName", "location":"additionalPersonalInfo"},
            {"name": "Adoptive Father Last Name", "key" : "adoptiveFatherLastName", "location":"additionalPersonalInfo"}
                ]

            
    
    



