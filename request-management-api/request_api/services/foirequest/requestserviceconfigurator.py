
from re import T
from request_api.models.ProgramAreas import ProgramArea
from request_api.models.ContactTypes import ContactType
from request_api.models.DeliveryModes import DeliveryMode
from request_api.models.ReceivedModes import ReceivedMode
from request_api.models.ApplicantCategories import ApplicantCategory
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.models.SubjectCodes import SubjectCode
from request_api.models.ProactiveDisclosureCategories import ProactiveDisclosureCategory
from request_api.models.FOIProactiveDisclosureRequests import FOIProactiveDisclosureRequests
from enum import Enum
import datetime 
import secrets

class requestserviceconfigurator:
    """This class consolidates helper fiunctions and constants
    """
    
    def getstatusname(self,requeststatuslabel):
        allstatus = FOIRequestStatus().getrequeststatuses()
        for status in allstatus:
            if status["statuslabel"] == requeststatuslabel:
                return status["name"]
        return None;    
    
    def getvalueof(self,name,key):
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
            pgarea = ProgramArea().getprogramarea(key)
            return pgarea["programareaid"]
        elif name == "subjectCode":
            subjectcode = SubjectCode().getsubjectcodebyname(key)
            return subjectcode["subjectcodeid"] if subjectcode is not None else None
        elif name == "proactiveDisclosureCategory":
            pdcategory = ProactiveDisclosureCategory().getproactivedisclosurecategory(key)
            return pdcategory["proactivedisclosurecategoryid"]

    def _prepareproactivedisclosuredetails(self, foirequestschema, userid, ministryid, version):
        proactivedisclosure = FOIProactiveDisclosureRequests()
        current_proactive = FOIProactiveDisclosureRequests.getcurrentfoiproactiverequest(ministryid)
        if current_proactive and 'version' in current_proactive:
            proactivedisclosure.version = current_proactive['version'] + 1
            proactivedisclosure.proactivedisclosureid = current_proactive['proactivedisclosureid']
            # Carry over category ID if present in current version
            if 'proactivedisclosurecategory.proactivedisclosurecategoryid' in current_proactive:
                proactivedisclosure.proactivedisclosurecategoryid = current_proactive['proactivedisclosurecategory.proactivedisclosurecategoryid']
        else:
            proactivedisclosure.version = 1
        proactivedisclosure.foiministryrequest_id = ministryid
        proactivedisclosure.foiministryrequestversion_id = version
        proactivedisclosure.createdby = userid
        proactivedisclosure.created_at = datetime.datetime.now()
        
        # New Proactive Disclosure Fields
        earliest_in_schema = "earliestEligiblePublicationDate" in foirequestschema or "earliesteligiblepublicationdate" in foirequestschema
        if earliest_in_schema:
            val = foirequestschema.get("earliestEligiblePublicationDate", foirequestschema.get("earliesteligiblepublicationdate"))
            proactivedisclosure.earliesteligiblepublicationdate = val if val != "" else None
        elif current_proactive:
            proactivedisclosure.earliesteligiblepublicationdate = current_proactive.get("earliesteligiblepublicationdate")

        publicationdate_in_schema = "publicationDate" in foirequestschema or "publicationdate" in foirequestschema
        if publicationdate_in_schema:
            val = foirequestschema.get("publicationDate", foirequestschema.get("publicationdate"))
            proactivedisclosure.publicationdate = val if val != "" else None
        elif earliest_in_schema and proactivedisclosure.earliesteligiblepublicationdate:
            proactivedisclosure.publicationdate = proactivedisclosure.earliesteligiblepublicationdate
        elif current_proactive:
            proactivedisclosure.publicationdate = current_proactive.get("publicationdate")

        proactivedisclosure.reportperiod = foirequestschema.get("reportPeriod", foirequestschema.get("reportperiod", current_proactive.get("reportperiod", "")))
        proactivedisclosure.processingstatus = foirequestschema.get("processingStatus", foirequestschema.get("processingstatus", current_proactive.get("processingstatus")))
        proactivedisclosure.processingmessage = foirequestschema.get("processingMessage", foirequestschema.get("processingmessage", current_proactive.get("processingmessage")))
        proactivedisclosure.sitemap_pages = foirequestschema.get("sitemapPages", foirequestschema.get("sitemap_pages", current_proactive.get("sitemap_pages")))
        proactivedisclosure.oipublicationstatus_id = foirequestschema.get("pdPublicationStatusId", foirequestschema.get("oipublicationstatus_id", current_proactive.get("oipublicationstatus_id", 2)))
        proactivedisclosure.isactive = foirequestschema.get("isactive", True)
        
        category_name = None
        if self._isNotBlankorNone(foirequestschema, "proactiveDisclosureCategory", "main"):
            category_name = foirequestschema["proactiveDisclosureCategory"]
        elif self._isNotBlankorNone(foirequestschema, "proactivedisclosurecategory", "main"):
            category_name = foirequestschema["proactivedisclosurecategory"]

        if category_name:
            proactivedisclosure.proactivedisclosurecategoryid = self.getvalueof("proactiveDisclosureCategory", category_name)
            
        return proactivedisclosure 

    def _isNotBlankorNone(self, dataschema, key, location):        
        if location == "main":
            if key in dataschema and  dataschema.get(key) is not None and dataschema.get(key)  and dataschema.get(key)  != "":
                return True
        else:
            if dataschema.get(location) is not None and key in dataschema.get(location) and dataschema.get(location)[key] and dataschema.get(location)[key] is not None and dataschema.get(location)[key] !="":
                return True
        return False

    def getprogramareaiaocodebyid(self, programareaid):
        programarea = ProgramArea().getprogramareabyid(programareaid)
        return programarea['iaocode']

    def getpropertyvaluefromschema(self,requestschema,property):
        return requestschema.get(property) if property in requestschema  else None

    def contacttypemapping(self):
        return [{"name": ContactType.email.value, "key" : "email"},
            {"name": ContactType.homephone.value, "key" : "phonePrimary"},
            {"name": ContactType.workphone.value, "key" : "workPhonePrimary"},
            {"name": ContactType.mobilephone.value, "key" : "phoneSecondary"},
            {"name": ContactType.workphone2.value, "key" : "workPhoneSecondary"},
            {"name": ContactType.streetaddress.value, "key" : "address"},
            {"name": ContactType.streetaddress.value, "key" : "addressSecondary"},
            {"name": ContactType.streetaddress.value, "key" : "city"},
            {"name": ContactType.streetaddress.value, "key" : "province"},
            {"name": ContactType.streetaddress.value, "key" : "postal"},
            {"name": ContactType.streetaddress.value, "key" : "country"}]
        
    def personalattributemapping(self):
        return [{"name": "BC Correctional Service Number", "key" : "correctionalServiceNumber", "location":"main"},
            {"name": "BC Public Service Employee Number", "key" : "publicServiceEmployeeNumber", "location":"main"},
            {"name": "BC Personal Health Care Number", "key" : "personalHealthNumber", "location":"additionalPersonalInfo"},
            {"name": "Adoptive Mother First Name", "key" : "adoptiveMotherFirstName", "location":"additionalPersonalInfo"},
            {"name": "Adoptive Mother Last Name", "key" : "adoptiveMotherLastName", "location":"additionalPersonalInfo"},
            {"name": "Adoptive Father First Name", "key" : "adoptiveFatherFirstName", "location":"additionalPersonalInfo"},
            {"name": "Adoptive Father Last Name", "key" : "adoptiveFatherLastName", "location":"additionalPersonalInfo"}
                ]

class ContactType(Enum):
    email = "Email"    
    homephone = "Home Phone"
    workphone = "Work Phone"
    mobilephone = "Mobile Phone"
    workphone2 = "Work Phone 2"  
    streetaddress = "Street Address"             
    
    



