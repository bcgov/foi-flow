
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
        if requestservicebuilder().isNotBlankorNone(foirequestschema,"category","main") == True:
            openfoirequest.applicantcategoryid = requestserviceconfigurator().getvalueof("category",foirequestschema.get("category"))
        openfoirequest.personalAttributes = self._prearepersonalattributes(foirequestschema, userid)        
        # openfoirequest.requestApplicants = self.__prepareapplicants(foirequestschema, userid)       
        print('SETTING APPLICANTS: ', foirequestschema.get("requestApplicants"))
        if foirequestschema.get("requestApplicants"):
            openfoirequest.requestApplicants = foirequestschema.get("requestApplicants")     
        else:
            openfoirequest.requestApplicants = self.__prepareapplicants(foirequestschema, userid)       
        if foirequestid is not None:         
           openfoirequest.foirequestid = foirequestid
        openfoirequest.wfinstanceid = wfinstanceid if wfinstanceid is not None else None
        openfoirequest.createdby = userid
        # openfoirequest_dict = openfoirequest.__dict__
        # print("\n---------openfoirequest in saveRequest:",openfoirequest_dict)     
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
        #print("\n------foiministryrequestarr in __prepareministries:",foiministryrequestarr)           
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
        # selfalsoknownas=None
        # selfdob=None
        # if foirequestschema.get("additionalPersonalInfo") is not None:
        #     applicantinfo = foirequestschema.get("additionalPersonalInfo")
        #     selfdob = applicantinfo["birthDate"] if requestservicebuilder().isNotBlankorNone(foirequestschema,"birthDate","additionalPersonalInfo") else None
        #     selfalsoknownas = applicantinfo["alsoKnownAs"] if requestservicebuilder().isNotBlankorNone(foirequestschema,"alsoKnownAs","additionalPersonalInfo") else None
        
        if not foirequestschema.get('foiRequestApplicantID'): # temporary for axis sync, remove after axis decommissioned
            applicant = self.__getapplicant(foirequestschema.get('axisapplicantid'), foirequestschema.get('foiRequestApplicantID', 0))
            foirequestschema['foiRequestApplicantID'] = applicant.get('foirequestapplicantid', 0)
        # if foirequestschema.get('foiRequestApplicantID') is None and foirequestschema.get('requeststatusid') == 1:
        applicantdata = foirequestschema.get("applicantdata")
        applicant_id = foirequestschema.get('foiRequestApplicantID')
        child_applicant_id = foirequestschema.get("foiRequestChildApplicantID")
        onbehalfof_applicant_id = foirequestschema.get("foiRequestOnBehalfOfApplicantID")
        applicanttype = None
        updated_applicant_id = None
        print('\n\n*****\n\nfoirequestschema: ', foirequestschema)
        print('\n\napplicantdata: ', applicantdata)
        if applicantdata:
            actiontype = applicantdata.get("actiontype")
            applicanttype = applicantdata.get("applicanttype")
            applicant = applicantdata.get("applicant")
            # handlers = {
            #     ("applicant", "reassign"): self._reassign_applicant,
            #     ("applicant", "update"): self._update_applicant,
            #     ("applicant", "create"): self._create_applicant,

            #     ("child", "reassign"): self._reassign_child,
            #     ("child", "update"): self._update_child,
            #     ("child", "create"): self._create_child,

            #     ("onbehalfof", "reassign"): self._reassign_onbehalfof,
            #     ("onbehalfof", "update"): self._update_onbehalfof,
            #     ("onbehalfof", "create"): self._create_onbehalfof,
            # }
            # handler = handlers.get((applicanttype, actiontype))

            # if not handler:
            #     return requestapplicantarr

            handler_name = f"_{actiontype}_{applicanttype}"
            handler = getattr(self, handler_name, None)
            print("\n\n***handler_name: ", handler_name)
            print("***handler: ", handler)
            if not handler:
                raise ValueError(f"No handler for _{actiontype}_{applicanttype}")

            if handler:
                updated_applicant_id = handler(foirequestschema, applicantdata, userid)

                if applicanttype == "applicant":
                    applicant_id = updated_applicant_id
                elif applicanttype == "child":
                    child_applicant_id = updated_applicant_id
                elif applicanttype == "onbehalfof":
                    onbehalfof_applicant_id = updated_applicant_id

        print('\n\n***applicant_id: ', applicant_id)
        print('***child_applicant_id: ', child_applicant_id)
        print('***onbehalfof_applicant_id: ', onbehalfof_applicant_id)

        self._update_all_applicant_mappings(
            applicant_id,
            child_applicant_id,
            onbehalfof_applicant_id,
            requestapplicantarr
        )
        return requestapplicantarr
    
    # Applicant handlers
    def _reassign_applicant(self, foirequestschema, applicantdata, userid):
        return applicantdata["applicant"]["foiRequestApplicantID"]
    
    def _update_applicant(self, foirequestschema, applicantdata, userid):
        updatedapplicant = FOIRequestApplicant.from_request_data(foirequestschema, applicantdata, "applicant")
        applicant_id = applicantdata["applicant"]["foiRequestApplicantID"]
        applicant_save_result = FOIRequestApplicant.update_applicant_profile(updatedapplicant, applicant_id, userid)
        return applicant_save_result.identifier
    
    def _create_applicant(self, foirequestschema, applicantdata, userid):
        newapplicant = FOIRequestApplicant.from_request_data(foirequestschema, applicantdata, "applicant", is_new=True)
        applicant_create_result = FOIRequestApplicant.save_instance(newapplicant, userid)
        return applicant_create_result.identifier
    
    def _reassign_child(self, foirequestschema, applicantdata, userid):
        return applicantdata["applicant"]["foiRequestApplicantID"]
    
    def _update_child(self, foirequestschema, applicantdata, userid):
        updatedchildapplicant = FOIRequestApplicant.from_request_data(foirequestschema, applicantdata, "child")
        applicant_id = applicantdata["applicant"]["foiRequestApplicantID"]
        child_save_result = FOIRequestApplicant.update_applicant_profile(updatedchildapplicant, applicant_id, userid)
        return child_save_result.identifier
    
    def _create_child(self, foirequestschema, applicantdata, userid):
        newapplicant = FOIRequestApplicant.from_request_data(foirequestschema, applicantdata, "child", is_new=True)
        applicant_create_result = FOIRequestApplicant.save_instance(newapplicant, userid)
        return applicant_create_result.identifier
    
    def _reassign_onbehalfof(self, foirequestschema, applicantdata, userid):
        return applicantdata["applicant"]["foiRequestApplicantID"]
    
    def _update_onbehalfof(self, foirequestschema, applicantdata, userid):
        updatedonbehalfofapplicant = FOIRequestApplicant.from_request_data(foirequestschema, applicantdata, "onbehalfof")
        applicant_id = applicantdata["applicant"]["foiRequestApplicantID"]
        onbehalfof_save_result = FOIRequestApplicant.update_applicant_profile(updatedonbehalfofapplicant, applicant_id, userid)
        return onbehalfof_save_result.identifier
    
    def _create_onbehalfof(self, foirequestschema, applicantdata, userid):
        newapplicant = FOIRequestApplicant.from_request_data(foirequestschema, applicantdata, "onbehalfof", is_new=True)
        applicant_create_result = FOIRequestApplicant.save_instance(newapplicant, userid)
        return applicant_create_result.identifier
    
    def _update_applicant_mapping(self, applicantid, requestortypeid, requestapplicantarr):
        requestapplicant = FOIRequestApplicantMapping()
        requestapplicant.foirequestapplicantid = applicantid
        requestapplicant.requestortypeid = requestortypeid
        requestapplicantarr.append(requestapplicant)

    def _update_all_applicant_mappings(self, applicant_id, child_applicant_id, onbehalfof_applicant_id, requestapplicantarr):
        requestortypeid = RequestorType().getrequestortype("Self")["requestortypeid"]
        child_requestortypeid = RequestorType().getrequestortype("Applying for a child under 12")["requestortypeid"]
        onbehalfof_requestortypeid = RequestorType().getrequestortype("Applying for other person")["requestortypeid"]
        if applicant_id:
            self._update_applicant_mapping(applicant_id, requestortypeid, requestapplicantarr)
        if child_applicant_id:
            self._update_applicant_mapping(child_applicant_id, child_requestortypeid, requestapplicantarr)
        if onbehalfof_applicant_id:
            self._update_applicant_mapping(onbehalfof_applicant_id, onbehalfof_requestortypeid, requestapplicantarr)

    def __getapplicant(self, axisapplicantid, foirequestapplicantid):
        applicant = {}
        if axisapplicantid:
            applicant = FOIRequestApplicant().getlatestprofilebyaxisapplicantid(axisapplicantid) # temporary for axis sync, remove after axis decommissioned
        if applicant == {}:
            applicant = FOIRequestApplicant().getlatestprofilebyapplicantid(foirequestapplicantid)
        return applicant
    
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
    