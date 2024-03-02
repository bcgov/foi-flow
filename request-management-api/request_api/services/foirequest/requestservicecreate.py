
from re import T
from request_api.models.FOIRequests import FOIRequest
from request_api.models.ContactTypes import ContactType
from request_api.models.PersonalInformationAttributes import PersonalInformationAttribute
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.services.watcherservice import watcherservice
from request_api.services.foirequest.requestservicebuilder import requestservicebuilder
from request_api.services.foirequest.requestserviceministrybuilder import requestserviceministrybuilder  
from request_api.services.foirequest.requestserviceconfigurator import requestserviceconfigurator
from request_api.models.PersonalInformationAttributes import PersonalInformationAttribute
from request_api.models.FOIRequestContactInformation import FOIRequestContactInformation
from request_api.models.FOIRequestPersonalAttributes import FOIRequestPersonalAttribute
from request_api.models.FOIRequestApplicantMappings import FOIRequestApplicantMapping
from request_api.models.FOIRequestApplicants import FOIRequestApplicant
from request_api.models.RequestorType import RequestorType
from request_api.utils.enums import StateName

import json
class requestservicecreate:
    """ This class consolidates the creation of new FOI request upon scenarios: open, save by both iao and ministry. 
    """

    def saverequest(self,foirequestschema, userid, foirequestid=None, ministryid=None, filenumber=None, version=None, rawrequestid=None, wfinstanceid=None):
        activeversion = 1 if version is None else version
        
        # FOI Request    
        openfoirequest = FOIRequest()
        openfoirequest.foirawrequestid = foirequestschema.get("foirawrequestid") if rawrequestid is None else rawrequestid
        openfoirequest.version = activeversion
        openfoirequest.requesttype = foirequestschema.get("requestType")
        openfoirequest.initialdescription = foirequestschema.get("description")
        openfoirequest.receiveddate = foirequestschema.get("receivedDate")
        openfoirequest.ministryRequests = self.__prepareministries(foirequestschema, activeversion, filenumber,ministryid, userid)               
        openfoirequest.contactInformations = self.__prearecontactinformation(foirequestschema, userid)       
        if requestservicebuilder().isNotBlankorNone(foirequestschema,"fromDate","main") == True:
            openfoirequest.initialrecordsearchfromdate = foirequestschema.get("fromDate")
        if requestservicebuilder().isNotBlankorNone(foirequestschema,"toDate","main") == True:
            openfoirequest.initialrecordsearchtodate = foirequestschema.get("toDate")
        if requestservicebuilder().isNotBlankorNone(foirequestschema,"deliveryMode","main") == True:
            openfoirequest.deliverymodeid = requestserviceconfigurator().getvalueof("deliveryMode",foirequestschema.get("deliveryMode"))            
        if requestservicebuilder().isNotBlankorNone(foirequestschema,"receivedMode","main") == True:    
            openfoirequest.receivedmodeid =  requestserviceconfigurator().getvalueof("receivedMode",foirequestschema.get("receivedMode"))                
        # if requestservicebuilder().isNotBlankorNone(foirequestschema,"category","main") == True:
        #     openfoirequest.applicantcategoryid = requestserviceconfigurator().getvalueof("category",foirequestschema.get("category"))
        openfoirequest.personalAttributes = self._prearepersonalattributes(foirequestschema, userid)        
        openfoirequest.requestApplicants = self.__prepareapplicants(foirequestschema, userid)       
        if foirequestid is not None:         
           openfoirequest.foirequestid = foirequestid
        openfoirequest.wfinstanceid = wfinstanceid if wfinstanceid is not None else None
        openfoirequest.createdby = userid  
        return FOIRequest.saverequest(openfoirequest) 
    
    
    def saverequestversion(self,foirequestschema, foirequestid , ministryid, userid):
        activeversion = 1        
        filenumber =foirequestschema.get("idNumber") 
        #Identify version       
        if foirequestid is not None:
            _foirequest = FOIRequest().getrequest(foirequestid)
            if _foirequest != {}:               
               activeversion = _foirequest["version"] + 1
            else:
                return _foirequest  
            self.__disablewatchers(ministryid, foirequestschema, userid)
            result = self.saverequest(foirequestschema, userid, foirequestid,ministryid,filenumber,activeversion,_foirequest["foirawrequestid"],_foirequest["wfinstanceid"])
            if result.success == True:
                FOIMinistryRequest.deActivateFileNumberVersion(ministryid, filenumber, userid)
            return result
    
    def saveministryrequestversion(self,ministryrequestschema, foirequestid , ministryid, userid, usertype = None):        
        _foirequest = FOIRequest().getrequest(foirequestid)
        _foiministryrequest = FOIMinistryRequest().getrequestbyministryrequestid(ministryid)
        _foirequestapplicant = FOIRequestApplicantMapping().getrequestapplicantinfos(foirequestid,_foirequest["version"])
        _foirequestcontact = FOIRequestContactInformation().getrequestcontactinformation(foirequestid,_foirequest["version"])
        _foirequestpersonalattrbs = FOIRequestPersonalAttribute().getrequestpersonalattributes(foirequestid,_foirequest["version"])
        foiministryrequestarr = []     
        foirequest = requestserviceministrybuilder().createfoirequestfromobject(_foirequest, userid)
        foiministryrequest = requestserviceministrybuilder().createfoiministryrequestfromobject(_foiministryrequest, ministryrequestschema, userid, usertype)
        foiministryrequestarr.append(foiministryrequest)
        foirequest.ministryRequests = foiministryrequestarr
        foirequest.requestApplicants = requestserviceministrybuilder().createfoirequestappplicantfromobject(_foirequestapplicant, foirequestid,  _foirequest['version']+1, userid)
        foirequest.contactInformations = requestserviceministrybuilder().createfoirequestcontactfromobject( _foirequestcontact, foirequestid, _foirequest['version']+1, userid)
        foirequest.personalAttributes = requestserviceministrybuilder().createfoirequestpersonalattributefromobject(_foirequestpersonalattrbs, foirequestid, _foirequest['version']+1, userid)
        result = FOIRequest.saverequest(foirequest)
        if result.success == True:
            FOIMinistryRequest.deActivateFileNumberVersion(ministryid, _foiministryrequest['filenumber'], userid)
        return result       
    
    def __prepareministries(self,foirequestschema, activeversion, filenumber,ministryid, userid):
        foiministryrequestarr = []
        if foirequestschema.get("selectedMinistries") is not None:
            for ministry in foirequestschema.get("selectedMinistries"):
                foiministryrequestarr.append(requestservicebuilder().createministry(foirequestschema, ministry, activeversion, userid, filenumber,ministryid))           
        return foiministryrequestarr

    def _prearepersonalattributes(self, foirequestschema, userid):
        personalattributearr = []
        if foirequestschema.get("requestType") == "personal":
            attributetypes = PersonalInformationAttribute().getpersonalattributes()
            for attrb in requestserviceconfigurator().personalattributemapping():
                attrbvalue = None
                if attrb["location"] == "main" and requestservicebuilder().isNotBlankorNone(foirequestschema,attrb["key"],"main") == True:
                    attrbvalue = foirequestschema.get(attrb["key"])
                if attrb["location"] == "additionalPersonalInfo" and requestservicebuilder().isNotBlankorNone(foirequestschema, attrb["key"],"additionalPersonalInfo") == True:
                    attrbvalue = foirequestschema.get(attrb["location"])[attrb["key"]]
                if attrbvalue is not None and attrbvalue and attrbvalue != "":
                    personalattributearr.append(
                        requestservicebuilder().createpersonalattribute(attrb["name"],
                                                            attrbvalue,
                                                            attributetypes, userid)
                        )
        return personalattributearr 

    def __prearecontactinformation(self, foirequestschema, userid):
        contactinformationarr = []
        contacttypes = ContactType().getcontacttypes()        
        for contact in requestserviceconfigurator().contacttypemapping():
            if foirequestschema.get(contact["key"]) is not None:   
                contactinformationarr.append(
                    requestservicebuilder().createcontactinformation(contact["key"],
                                                            contact["name"],
                                                            foirequestschema.get(contact["key"]),
                                                            contacttypes, userid)
                    )
        return contactinformationarr
    
    def __prepareapplicants(self, foirequestschema, userid):
        requestapplicantarr = []
        selfalsoknownas=None
        selfdob=None
        selfcategoryid = requestserviceconfigurator().getvalueof("category",foirequestschema.get("category")) if requestservicebuilder().isNotBlankorNone(foirequestschema,"category","main") == True else None
        if foirequestschema.get("additionalPersonalInfo") is not None:
            applicantinfo = foirequestschema.get("additionalPersonalInfo")
            selfdob = applicantinfo["birthDate"] if requestservicebuilder().isNotBlankorNone(foirequestschema,"birthDate","additionalPersonalInfo") else None
            selfalsoknownas = applicantinfo["alsoKnownAs"] if requestservicebuilder().isNotBlankorNone(foirequestschema,"alsoKnownAs","additionalPersonalInfo") else None

        applicant = FOIRequestApplicant().getlatestprofilebyaxisapplicantid(foirequestschema.get('axisapplicantid', 0)) # temporary for axis sync, remove after axis decommissioned
        foirequestschema['foiRequestApplicantID'] = applicant.get('foirequestapplicantid', 0) # temporary for axis sync, remove after axis decommissioned
        # if foirequestschema.get('foiRequestApplicantID') is None and foirequestschema.get('requeststatusid') == 1:
        if foirequestschema.get('foiRequestApplicantID', 0) > 0:
            applicant = FOIRequestApplicant.updateapplicantprofile( # temporary for axis sync, remove after axis decommissioned
                foirequestschema['foiRequestApplicantID'],
                foirequestschema['firstName'],
                foirequestschema['lastName'],
                foirequestschema.get("middleName"),
                foirequestschema.get("businessName"),
                selfdob,
                selfalsoknownas,
                None,
                foirequestschema.get('axisapplicantid', None),
                userid
            )
            # applicant = FOIRequestApplicant().getlatestprofilebyapplicantid(foirequestschema['foiRequestApplicantID']) comment back in after axis decommission
            requestapplicant = FOIRequestApplicantMapping()
            requestapplicant.foirequestapplicantid = applicant.identifier # = applicant['foirequestapplicantid'] comment back in after axis decommission            
            requestapplicant.requestortypeid = RequestorType().getrequestortype("Self")["requestortypeid"]
            requestapplicantarr.append(requestapplicant)
        else:
            requestapplicantarr.append(
                requestservicebuilder().createapplicant(foirequestschema.get("firstName"),
                                            foirequestschema.get("lastName"),
                                            "Self",
                                            userid,
                                            foirequestschema.get("middleName"),
                                            foirequestschema.get("businessName"),
                                            selfalsoknownas,
                                            selfdob,
                                            selfcategoryid,
                                            foirequestschema.get('axisapplicantid', None),)
                )
                 
        #Prepare additional applicants
        if foirequestschema.get("additionalPersonalInfo") is not None:
            addlapplicantinfo = foirequestschema.get("additionalPersonalInfo")
            if requestservicebuilder().isNotBlankorNone(foirequestschema,"childFirstName","additionalPersonalInfo"):
                requestapplicantarr.append(
                    requestservicebuilder().createapplicant(self.__getkeyvalue(addlapplicantinfo,"childFirstName") ,
                                           self.__getkeyvalue(addlapplicantinfo,"childLastName"),
                                           "Applying for a child under 12",
                                           userid,
                                           self.__getkeyvalue(addlapplicantinfo,"childMiddleName") ,                                            
                                           None,
                                           self.__getkeyvalue(addlapplicantinfo,"childAlsoKnownAs") ,
                                           self.__getkeyvalue(addlapplicantinfo,"childBirthDate"))
                    )
            if requestservicebuilder().isNotBlankorNone(foirequestschema,"anotherFirstName","additionalPersonalInfo"):
                requestapplicantarr.append(
                    requestservicebuilder().createapplicant(self.__getkeyvalue(addlapplicantinfo,"anotherFirstName") ,
                                           self.__getkeyvalue(addlapplicantinfo,"anotherLastName") ,
                                           "Applying for other person",
                                           userid,
                                           self.__getkeyvalue(addlapplicantinfo,"anotherMiddleName") ,                                            
                                           None,
                                           self.__getkeyvalue(addlapplicantinfo,"anotherAlsoKnownAs"),
                                           self.__getkeyvalue(addlapplicantinfo,"anotherBirthDate")  )
                    )
        return requestapplicantarr
    
    def __disablewatchers(self, ministryid, requestschema, userid):
        requeststatuslabel =  requestschema.get("requeststatuslabel") if 'requeststatuslabel' in requestschema  else None
        if requeststatuslabel is not None: 
            status = requestserviceconfigurator().getstatusname(requeststatuslabel)
            if status == StateName.open.value:
                watchers = watcherservice().getministryrequestwatchers(int(ministryid), True)
                for watcher in watchers:
                    watcherschema = {"ministryrequestid":ministryid,"watchedbygroup":watcher["watchedbygroup"],"watchedby":watcher["watchedby"],"isactive":False}
                    watcherservice().createministryrequestwatcher(watcherschema, userid, None)

    def __getkeyvalue(self, inputschema, property):
        return inputschema[property] if inputschema is not None and inputschema.get(property) is not None  else ''   