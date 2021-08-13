
import re
from request_api import version
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestContactInformation import FOIRequestContactInformation
from request_api.models.FOIRequestPersonalAttributes import FOIRequestPersonalAttribute
from request_api.models.FOIRequestApplicants import FOIRequestApplicant
from request_api.models.FOIRequestApplicantMappings import FOIRequestApplicantMapping
from request_api.schemas.foirequest import  FOIRequestSchema


class requestservice:
    """ FOI Request management service

    This service class manages all CRUD operations related to an FOI RAW Request

    """

    def saverequest(foiRequest,foirequestid = None):
        fOIRequestsSchema = FOIRequestSchema().load(foiRequest)
        fOIRequestTypeSchema = fOIRequestsSchema.get("requestType")
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
        if fOIRequestsSchema.get("ministryRequests") is not None:
            for  ministry in  fOIRequestsSchema.get("ministryRequests"):
                foiministryRequest = FOIMinistryRequest()
                foiministryRequest.__dict__.update(ministry)
                foiministryRequest.version = activeVersion
                foiministryRequest.requeststatusid = 1
                foiMinistryRequestArr.append(foiministryRequest)
           
        #Prepare contact information records
        if fOIRequestsSchema.get("contactInformations") is not None:
            for  contact in  fOIRequestsSchema.get("contactInformations"):
                contactInformation = FOIRequestContactInformation()
                contactInformation.__dict__.update(contact)
                contactInformationArr.append(contactInformation)
                
        #Prepare personal attribute records
        if fOIRequestsSchema.get("personalAttributes") is not None:
            for  attribute in  fOIRequestsSchema.get("personalAttributes"):
                pAttribute = FOIRequestPersonalAttribute()
                pAttribute.__dict__.update(attribute)
                personalAttributeArr.append(pAttribute)

        #Prepare applicant records 
        if fOIRequestsSchema.get("requestApplicants") is not None:
            for  reqapplicant in  fOIRequestsSchema.get("requestApplicants"):
                requestApplicant = FOIRequestApplicantMapping()
                applicant = FOIRequestApplicant()
                applicant.__dict__.update(reqapplicant.get("applicant")) 
                _applicant = FOIRequestApplicant.getrequest(applicant)  
                if _applicant == {} :
                    _applicant = FOIRequestApplicant.saverequest(applicant)
                    requestApplicant.foirequestapplicantid = _applicant.identifier
                else:
                    requestApplicant.foirequestapplicantid = _applicant["foirequestapplicantid"]             
                
                requestApplicant.requestortypeid = reqapplicant.get("requestortypeid")
                requestApplicantArr.append(requestApplicant)
                
        # FOI Request
        _fOIRequest = FOIRequest()
        _fOIRequest.__dict__.update(fOIRequestTypeSchema)
        _fOIRequest.version = activeVersion, 
        _fOIRequest.requesttype = fOIRequestTypeSchema.get("requestType")
        _fOIRequest.ministryRequests = foiMinistryRequestArr
        _fOIRequest.contactInformations = contactInformationArr
        _fOIRequest.personalAttributes = personalAttributeArr
        _fOIRequest.requestApplicants = requestApplicantArr
        
        if foirequestid is not None:         
           _fOIRequest.foirequestid = foirequestid 
        
        return FOIRequest.saverequest(_fOIRequest)
            
    def getrequest(foirequestid,foiministryrequestid):
        
        request = FOIRequest.getrequest(foirequestid)
        requestministry = FOIMinistryRequest.getrequestbyministryrequestid(foiministryrequestid)        
        requestcontactinformation = FOIRequestContactInformation.getrequestcontactinformation(foirequestid,request['version'])
        return requestcontactinformation
    



