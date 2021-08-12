
from request_api import version
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.ProgramAreas import ProgramArea
from request_api.models.ApplicantCategories import ApplicantCategory
from request_api.models.ContactTypes import ContactType
from request_api.models.FOIRequestContactInformation import FOIRequestContactInformation
from request_api.models.FOIRequestPersonalAttributes import FOIRequestPersonalAttribute
from request_api.models.FOIRequestApplicants import FOIRequestApplicant
from request_api.models.FOIRequestApplicantMappings import FOIRequestApplicantMapping
from request_api.schemas.foirequest import  FOIRequestSchema
from request_api.schemas.foirequestwrapper import  FOIRequestWrapperSchema
from enum import Enum
import datetime
from random import randint
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
                foiministryRequest.isactive = ministry["isSelected"]
                range = 5
                foiministryRequest.filenumber = ministry["code"] + "-"+ str(datetime.date.today().year)+"-"+ str(randint(10**(range-1), 10**(range-1)))
                programArea = ProgramArea.getprogramarea(ministry["name"])
                foiministryRequest.programareaid = programArea["programareaid"]
                foiministryRequest.description = fOIRequestsSchema.get("description")
                foiministryRequest.duedate = fOIRequestsSchema.get("dueDate")
                foiministryRequest.assignedto = fOIRequestsSchema.get("assignedTo")
                foiMinistryRequestArr.append(foiministryRequest)           
        

        #Prepare applicant record 
        requestApplicant = FOIRequestApplicantMapping()
        applicant = FOIRequestApplicant()
        applicant.firstname = fOIRequestsSchema.get("firstName")
        applicant.lastname = fOIRequestsSchema.get("lastName") 
        applicant.middlename = fOIRequestsSchema.get("middleName") if fOIRequestsSchema.get("middleName") is not None else None 
        applicant.businessname = fOIRequestsSchema.get("businessName") if fOIRequestsSchema.get("businessName") is not None else None 
        _applicant = FOIRequestApplicant.getrequest(applicant)
        if _applicant == {} :
            _applicant = FOIRequestApplicant.saverequest(applicant)
            requestApplicant.foirequestapplicantid = _applicant.identifier
        else:
            requestApplicant.foirequestapplicantid = _applicant["foirequestapplicantid"]           
        applicantCategory = ApplicantCategory.getapplicantcategory(fOIRequestsSchema.get("category"))   
        requestApplicant.requestortypeid = applicantCategory["applicantcategoryid"]
        requestApplicantArr.append(requestApplicant)
                 
      
        #Prepare contact information
        contactTypes = ContactType.getcontacttypes()
        fOIRequestUtil = FOIRequestUtil()
        for contact in fOIRequestUtil.contactTypeMapping():
            if fOIRequestsSchema.get(contact["key"]) is not None:   
                contactInformationArr.append(
                    fOIRequestUtil.createContactInformation(contact["key"],
                                                            contact["name"],
                                                            fOIRequestsSchema.get(contact["key"]),
                                                            contactTypes)
                    )

        # FOI Request
        _fOIRequest = FOIRequest()
        _fOIRequest.version = activeVersion, 
        _fOIRequest.requesttype = fOIRequestsSchema.get("requestType")
        _fOIRequest.ministryRequests = foiMinistryRequestArr
        _fOIRequest.contactInformations = contactInformationArr
        #_fOIRequest.personalAttributes = personalAttributeArr
        _fOIRequest.requestApplicants = requestApplicantArr
        
        if foirequestid is not None:         
           _fOIRequest.foirequestid = foirequestid 
        
        return FOIRequest.saverequest(_fOIRequest)
    

class FOIRequestUtil:   
    
    def createContactInformation(self,dataformat, name, value, contactTypes):
        contactInformation = FOIRequestContactInformation()
        contactInformation.contactinformation = value
        contactInformation.dataformat = dataformat
        for contactType in contactTypes:
            if contactType["name"] == name:
              contactInformation.contacttypeid =contactType["contacttypeid"]              
        return contactInformation
            
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

            
    
    



