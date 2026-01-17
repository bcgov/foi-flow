
from re import T
from request_api.models.ProgramAreas import ProgramArea
from request_api.models.ContactTypes import ContactType
from request_api.models.DeliveryModes import DeliveryMode
from request_api.models.ReceivedModes import ReceivedMode
from request_api.models.ApplicantCategories import ApplicantCategory
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.models.SubjectCodes import SubjectCode
from request_api.models.ProactiveDisclosureCategories import ProactiveDisclosureCategory
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
            print("Key:",key)
            pdcategory = ProactiveDisclosureCategory().getproactivedisclosurecategory(key)
            print("pdcategory:",pdcategory)
            return pdcategory["proactivedisclosurecategoryid"]

    def getpropertyvaluefromschema(self,requestschema,property):
        return requestschema.get(property) if property in requestschema  else None

    def generatefilenumber(self, code, id):
        tmp = str(id)
        randomnum = secrets.randbits(32)
        return code + "-" + str(datetime.date.today().year) + "-" + tmp + str(randomnum)[:5]
    
    def generatepdfilenumber(self, code, foirequestschema):
        file_number = ""
        pd_category =  foirequestschema["proactivedisclosurecategory"].lower()
        reportperiod = foirequestschema["reportperiod"] if 'reportperiod' in foirequestschema else ""
        if (foirequestschema.get("startDate") is not None):
            startdate = foirequestschema.get("startDate")
        elif (foirequestschema.get("requestProcessStart") is not None):
            startdate = foirequestschema.get("requestProcessStart")
        year= startdate[:4]
        randomnum = secrets.randbits(32)
        ending_id= str(randomnum)[:5]
        match pd_category:
            case "calendars":
                file_number = "CAL-" + code + "-" + year + "-" + self._getpdrequestreportperiodabbr(reportperiod) + "-" +ending_id
                print("\nfile_number=",file_number)
                return file_number
            case "briefing notes":
                return reportperiod + "-" +ending_id
            case _:
                return file_number
        return file_number
    

    def _getpdrequestreportperiodabbr(self,month_name: str) -> str:
    #Converts full month name/ report period to 
    # shorten uppercase abbreviation.
        month_map = {
            "january": "JAN",
            "february": "FEB",
            "march": "MAR",
            "april": "APR",
            "may": "MAY",
            "june": "JUN",
            "july": "JUL",
            "august": "AUG",
            "september": "SEP",
            "october": "OCT",
            "november": "NOV",
            "december": "DEC",
            "quarter 1": "Q1",
            "quarter 2": "Q2",
            "quarter 3": "Q3",
            "quarter 4": "Q4",
            "fiscal year": "FISCAL",
        }
        abbr = month_map.get(month_name.lower())
        if abbr is None:
            raise ValueError(f"Invalid month name: {month_name}")
        return abbr

    
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
    
    



