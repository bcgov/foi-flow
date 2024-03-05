
from re import T
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.models.RequestorType import RequestorType
from request_api.models.FOIRequestContactInformation import FOIRequestContactInformation
from request_api.models.FOIRequestPersonalAttributes import FOIRequestPersonalAttribute
from request_api.models.FOIRequestApplicants import FOIRequestApplicant
from request_api.models.FOIRequestApplicantMappings import FOIRequestApplicantMapping
from request_api.models.FOIRequestTeams import FOIRequestTeam
from request_api.models.FOIRequestStatus import FOIRequestStatus
from request_api.models.FOIRequestOIPC import FOIRequestOIPC

from datetime import datetime as datetime2
from request_api.utils.enums import MinistryTeamWithKeycloackGroup, StateName
from request_api.services.foirequest.requestserviceconfigurator import requestserviceconfigurator 
from request_api.services.foirequest.requestserviceministrybuilder import requestserviceministrybuilder 


import json
class requestservicebuilder(requestserviceconfigurator):
    """ This class consolidates the helper functions for creating new foi request based on iao actions. 
    """

    def createministry(self, requestschema, ministry, activeversion, userid, filenumber=None, ministryid=None):
        foiministryrequest = FOIMinistryRequest()
        foiministryrequest.__dict__.update(ministry)
        foiministryrequest.requeststatusid = self.__getrequeststatusid(requestschema.get("requeststatuslabel"))
        foiministryrequest.requeststatuslabel = requestschema.get("requeststatuslabel")        
        foiministryrequest.isactive = True
        foiministryrequest.axisrequestid = requestschema.get("axisRequestId")
        foiministryrequest.axissyncdate = requestschema.get("axisSyncDate")
        foiministryrequest.requestpagecount = requestschema.get("requestPageCount")
        foiministryrequest.filenumber = self.generatefilenumber(ministry["code"], requestschema.get("foirawrequestid")) if filenumber is None else filenumber
        foiministryrequest.programareaid = self.getvalueof("programArea",ministry["code"])
        foiministryrequest.description = requestschema.get("description")
        foiministryrequest.duedate = requestschema.get("dueDate")
        foiministryrequest.linkedrequests = requestschema.get("linkedRequests")
        foiministryrequest.identityverified = requestschema.get("identityVerified")
        foiministryrequest.originalldd = requestschema.get("originalDueDate")
        if requestschema.get("isoipcreview") is not None and requestschema.get("isoipcreview")  != "":
            foiministryrequest.isoipcreview = requestschema.get("isoipcreview")
            foiministryrequest.oipcreviews = self.prepareoipc(requestschema, ministryid, activeversion, userid)
            
        if requestschema.get("cfrDueDate") is not None and requestschema.get("cfrDueDate")  != "":
            foiministryrequest.cfrduedate = requestschema.get("cfrDueDate")
        startdate = ""
        if (requestschema.get("startDate") is not None):
            startdate = requestschema.get("startDate")
        elif (requestschema.get("requestProcessStart") is not None):
            startdate = requestschema.get("requestProcessStart")
        foiministryrequest.startdate = startdate
        foiministryrequest.createdby = userid
        requeststatuslabel =  self.getpropertyvaluefromschema(requestschema, 'requeststatuslabel')
        if requeststatuslabel is not None:
            status = self.getstatusname(requeststatuslabel)
        if self.isNotBlankorNone(requestschema,"fromDate","main") == True:
            foiministryrequest.recordsearchfromdate = requestschema.get("fromDate")
        if self.isNotBlankorNone(requestschema,"toDate","main") == True:
            foiministryrequest.recordsearchtodate = requestschema.get("toDate")
        self.__updateassignedtoandgroup(foiministryrequest, requestschema, ministry, status, filenumber, ministryid)
        self.__updateministryassignedtoandgroup(foiministryrequest, requestschema, ministry, status)

        if ministryid is not None:
            foiministryrequest.foiministryrequestid = ministryid
            activeversion = FOIMinistryRequest.getversionforrequest(ministryid)[0]+1
            divisions = FOIMinistryRequestDivision().getdivisions(ministryid , activeversion-1)
            foiministryrequest.divisions = requestserviceministrybuilder().createfoirequestdivisionfromobject(divisions, ministryid, activeversion, userid)  
            foiministryrequest.documents = requestserviceministrybuilder().createfoirequestdocuments(requestschema,ministryid , activeversion , userid)
            foiministryrequest.extensions = requestserviceministrybuilder().createfoirequestextensions(ministryid, activeversion, userid)
            if 'subjectCode' in requestschema and requestschema['subjectCode'] is not None and requestschema['subjectCode'] != '':
                foiministryrequest.subjectcode = requestserviceministrybuilder().createfoirequestsubjectcode(requestschema, ministryid, activeversion, userid)
        foiministryrequest.version = activeversion
        foiministryrequest.closedate = self.getpropertyvaluefromschema(requestschema, 'closedate')
        foiministryrequest.closereasonid = self.getpropertyvaluefromschema(requestschema, 'closereasonid')
        if self.getpropertyvaluefromschema(requestschema, 'isofflinepayment') is not None:
            foiministryrequest.isofflinepayment =  self.getpropertyvaluefromschema(requestschema, 'isofflinepayment')    
        return foiministryrequest

    def __updateministryassignedtoandgroup(self, foiministryrequest, requestschema, ministry, status):
        if self.__isgrouprequired(status):
                foiministryrequest.assignedministrygroup = MinistryTeamWithKeycloackGroup[ministry["code"]].value
        if self.isNotBlankorNone(requestschema,"assignedministrygroup","main") == True:
            foiministryrequest.assignedministrygroup = requestschema.get("assignedministrygroup")
        if self.isNotBlankorNone(requestschema,"assignedministryperson","main") == True and requestschema.get("reopen") != True:
            foiministryrequest.assignedministryperson = requestschema.get("assignedministryperson")
            requestserviceministrybuilder().createfoiassigneefromobject(requestschema.get("assignedministryperson"), requestschema.get("assignedministrypersonFirstName"), requestschema.get("assignedministrypersonMiddleName"), requestschema.get("assignedministrypersonLastName"))
        else:
            foiministryrequest.assignedministryperson = None

    def __updateassignedtoandgroup(self, foiministryrequest, requestschema, ministry, status, filenumber=None, ministryid=None):
        foiministryrequest.assignedgroup = requestschema.get("assignedGroup")
        if self.isNotBlankorNone(requestschema,"assignedTo","main") == True:
            foiministryrequest.assignedto = requestschema.get("assignedTo")
            requestserviceministrybuilder().createfoiassigneefromobject(requestschema.get("assignedTo"), requestschema.get("assignedToFirstName"), requestschema.get("assignedToMiddleName"), requestschema.get("assignedToLastName"))
        else:
            foiministryrequest.assignedto = None

    def __isgrouprequired(self,status):
        if status == StateName.callforrecords.value or status == StateName.recordsreview.value or status == StateName.consult.value or status == StateName.feeestimate.value or status == StateName.ministrysignoff.value or status == StateName.response.value:
            return True
        else:
            return False
        
    def __getgroupname(self, requesttype, bcgovcode):
        return 'Flex Team' if  requesttype == "general" else FOIRequestTeam.getdefaultprocessingteamforpersonal(bcgovcode)
    
    def __getrequeststatusid(self, requeststatuslabel):
        state = FOIRequestStatus.getrequeststatusbylabel(
            requeststatuslabel
        )
        stateid = (
            state.get("requeststatusid")
            if isinstance(state, dict) and state.get("requeststatusid") not in (None, "")
            else ""
        )
        return stateid
    
    def createcontactinformation(self,dataformat, name, value, contacttypes, userid):
        contactinformation = FOIRequestContactInformation()
        contactinformation.contactinformation = value
        contactinformation.dataformat = dataformat
        contactinformation.createdby = userid
        for contacttype in contacttypes:
            if contacttype["name"] == name:
              contactinformation.contacttypeid =contacttype["contacttypeid"]              
        return contactinformation
    
    def createapplicant(self,firstname, lastname, appltcategory, userid, middlename = None, businessname = None, alsoknownas = None, dob = None):
        requestapplicant = FOIRequestApplicantMapping()
        _applicant = FOIRequestApplicant().createapplicant(firstname, lastname, middlename, businessname, alsoknownas, dob, userid)
        requestapplicant.foirequestapplicantid = _applicant.identifier
        if appltcategory is not None:           
            requestertype = RequestorType().getrequestortype(appltcategory)  
            requestapplicant.requestortypeid = requestertype["requestortypeid"]
        return requestapplicant
    
    def createpersonalattribute(self, name, value,attributetypes, userid):
        personalattribute = FOIRequestPersonalAttribute()
        personalattribute.createdby = userid
        if value is not None and value !="" and value:
            for attributetype in attributetypes:
                if attributetype["name"] == name:
                    personalattribute.personalattributeid = attributetype["attributeid"]
                    personalattribute.attributevalue = value
        return personalattribute
    
    def prepareoipc(self, requestschema, ministryrequestid, version, userid):
        oipcarr = []
        if 'oipcdetails' in  requestschema:
            for oipc in requestschema['oipcdetails']:
                oipcreview = FOIRequestOIPC()
                oipcreview.foiministryrequest_id = ministryrequestid
                oipcreview.foiministryrequestversion_id=version
                oipcreview.oipcno = oipc["oipcno"]
                oipcreview.reviewtypeid = oipc["reviewtypeid"]
                oipcreview.reasonid = oipc["reasonid"]
                oipcreview.statusid = oipc["statusid"]
                oipcreview.outcomeid = oipc["outcomeid"]
                oipcreview.investigator = oipc["investigator"] if oipc["investigator"] not in (None, "") else None
                oipcreview.isinquiry = oipc["isinquiry"]
                oipcreview.isjudicialreview = oipc["isjudicialreview"]
                oipcreview.issubsequentappeal = oipc["issubsequentappeal"]
                oipcreview.issubsequentappeal = oipc["issubsequentappeal"]
                oipcreview.receiveddate = oipc["receiveddate"] if oipc["receiveddate"] not in (None, "") else None
                oipcreview.closeddate = oipc["closeddate"] if oipc["closeddate"] not in (None, "") else None 
                if oipc["isinquiry"] == True:
                    oipcreview.inquiryattributes = self.__formatoipcattributes(oipc["inquiryattributes"])
                oipcreview.createdby=userid
                oipcreview.created_at= datetime2.now().isoformat()
                oipcarr.append(oipcreview)
            return oipcarr
        
    def __formatoipcattributes(self, inquiryattributes):
        if inquiryattributes not in (None, "") and inquiryattributes["inquirydate"] in ("","null"):
            inquiryattributes["inquirydate"] = None
        return inquiryattributes
    

    def isNotBlankorNone(self, dataschema, key, location):        
        if location == "main":
            if key in dataschema and  dataschema.get(key) is not None and dataschema.get(key)  and dataschema.get(key)  != "":
                return True
        else:
            if dataschema.get(location) is not None and key in dataschema.get(location) and dataschema.get(location)[key] and dataschema.get(location)[key] is not None and dataschema.get(location)[key] !="":
                return True
        return False          
    
            

    



