
from re import T
from request_api.models.ProgramAreas import ProgramArea
from request_api.models.ContactTypes import ContactType
from request_api.models.DeliveryModes import DeliveryMode
from request_api.models.ReceivedModes import ReceivedMode
from request_api.models.ApplicantCategories import ApplicantCategory
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.models.SubjectCodes import SubjectCode
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

    def getpropertyvaluefromschema(self,requestschema,property):
        return requestschema.get(property) if property in requestschema  else None

    def generatefilenumber(self, code, id):
        tmp = str(id)
        randomnum = secrets.randbits(32)
        return code + "-" + str(datetime.date.today().year) + "-" + tmp + str(randomnum)[:5]
    
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
    
    



