
from re import T
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestContactInformation import FOIRequestContactInformation
from request_api.models.FOIRequestPersonalAttributes import FOIRequestPersonalAttribute
from request_api.models.FOIRequestApplicantMappings import FOIRequestApplicantMapping
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.FOIRequestExtensions import FOIRequestExtension
from request_api.models.FOIRequestExtensionDocumentMappings import FOIRequestExtensionDocumentMapping
from request_api.models.FOIAssignees import FOIAssignee
from request_api.services.foirequest.requestserviceconfigurator import requestserviceconfigurator 
from datetime import datetime as datetime2

class requestserviceministrybuilder(requestserviceconfigurator):
    """ This class consolidates the helper functions for creating new foi request based on ministry actions. 
    """

    def createfoirequestfromobject(self, foiobject, userid):
        foirequest = FOIRequest()  
        foirequest.foirawrequestid = foiobject['foirawrequestid']
        foirequest.foirequestid =  foiobject['foirequestid']
        foirequest.version = foiobject["version"] + 1
        foirequest.initialdescription =  foiobject['initialdescription']
        foirequest.initialrecordsearchfromdate = foiobject['initialrecordsearchfromdate'] if 'initialrecordsearchfromdate' in foiobject  else None
        foirequest.initialrecordsearchtodate = foiobject['initialrecordsearchfromdate'] if 'initialrecordsearchfromdate' in foiobject  else None
        foirequest.receiveddate = foiobject['receiveddate'] if 'receiveddate' in foiobject  else None
        foirequest.requesttype = foiobject['requesttype']
        foirequest.wfinstanceid = foiobject['wfinstanceid']       
        foirequest.applicantcategoryid =  foiobject["applicantcategory.applicantcategoryid"]
        foirequest.deliverymodeid =  foiobject["deliverymode.deliverymodeid"]
        foirequest.receivedmodeid =  foiobject["receivedmode.receivedmodeid"]
        foirequest.createdby = userid
        return foirequest
    
    def createfoiministryrequestfromobject(self, ministryschema, requestschema, userid, actiontype = None):
        requestdict = self.createfoiministryrequestfromobject1(ministryschema, requestschema)
        foiministryrequest = FOIMinistryRequest()
        foiministryrequest.foiministryrequestid = ministryschema["foiministryrequestid"] 
        foiministryrequest.version = ministryschema["version"] + 1
        foiministryrequest.foirequest_id = ministryschema["foirequest_id"] 
        foiministryrequest.foirequestversion_id = ministryschema["foirequestversion_id"] 
        foiministryrequest.description = ministryschema["description"]
        foiministryrequest.recordsearchfromdate = requestdict['recordsearchfromdate']
        foiministryrequest.recordsearchtodate = requestdict['recordsearchtodate']
        foiministryrequest.filenumber = ministryschema["filenumber"]
        foiministryrequest.axissyncdate = ministryschema["axissyncdate"]
        foiministryrequest.axisrequestid = ministryschema["axisrequestid"]
        foiministryrequest.requestpagecount = ministryschema["requestpagecount"]
        foiministryrequest.cfrduedate = requestdict['cfrduedate']
        foiministryrequest.startdate = requestdict['startdate']
        foiministryrequest.duedate = requestdict['duedate']
        foiministryrequest.assignedministrygroup = requestdict['assignedministrygroup']
        if 'assignedministryperson' in requestschema and requestschema['assignedministryperson'] not in (None,''):
            foiministryrequest.assignedministryperson = requestschema['assignedministryperson']
            firstname = requestschema['assignedministrypersonFirstName']
            middlename = None
            lastname = requestschema['assignedministrypersonLastName']
            self.createfoiassigneefromobject(requestschema['assignedministryperson'], firstname, middlename, lastname)
        else:
            foiministryrequest.assignedministryperson = ministryschema["assignedministryperson"]

        foiministryrequest.assignedgroup = requestschema['assignedgroup'] if 'assignedgroup' in requestschema and requestschema['assignedgroup'] not in (None,'') else requestdict['assignedgroup']
        if 'assignedto' in requestschema and requestschema['assignedto'] not in (None,''):
            foiministryrequest.assignedto = requestschema['assignedto']
            fn = requestschema['assignedToFirstName'] if requestschema['assignedto'] != None else None
            mn = None
            ln = requestschema['assignedToLastName'] if requestschema['assignedto'] != None else None
            self.createfoiassigneefromobject(requestschema['assignedto'], fn, mn, ln)
        elif actiontype == "assignee":            
            foiministryrequest.assignedto = None
        else:
            foiministryrequest.assignedto = ministryschema["assignedto"]

        foiministryrequest.requeststatusid = requestdict['requeststatusid']
        foiministryrequest.programareaid = requestdict['programareaid']
        foiministryrequest.createdby = userid
        if 'divisions' in requestschema:
            foiministryrequest.divisions = self.createfoirequestdivision(requestschema,ministryschema["foiministryrequestid"] ,ministryschema["version"] + 1, userid)  
        else:
            divisions = FOIMinistryRequestDivision().getdivisions(ministryschema["foiministryrequestid"] ,ministryschema["version"])
            foiministryrequest.divisions = self.createfoirequestdivisionfromobject(divisions,ministryschema["foiministryrequestid"] ,ministryschema["version"] + 1, userid)  
        foiministryrequest.documents = self.createfoirequestdocuments(requestschema,ministryschema["foiministryrequestid"] ,ministryschema["version"] +1 , userid)
        foiministryrequest.extensions = self.createfoirequestextensions(ministryschema["foiministryrequestid"] ,ministryschema["version"] +1 , userid)       
        foiministryrequest.closedate = requestdict['closedate']
        foiministryrequest.closereasonid = requestdict['closereasonid']
        return foiministryrequest

    def createfoiministryrequestfromobject1(self, ministryschema, requestschema):  
        return {
            'recordsearchfromdate': ministryschema['recordsearchfromdate'] if 'recordsearchfromdate' in ministryschema  else None,
            'recordsearchtodate': ministryschema['recordsearchtodate'] if 'recordsearchtodate' in ministryschema  else None,
            'cfrduedate': ministryschema['cfrduedate'] if 'cfrduedate' in ministryschema  else None,
            'startdate': ministryschema['startdate'] if 'startdate' in ministryschema  else None,
            'duedate': requestschema['duedate'] if 'duedate' in requestschema else ministryschema["duedate"], #and isextension':= True 
            'assignedministrygroup': requestschema['assignedministrygroup'] if 'assignedministrygroup' in requestschema  else ministryschema["assignedministrygroup"],
            'assignedgroup': requestschema['assignedgroup'] if 'assignedgroup' in requestschema  else ministryschema["assignedgroup"],
            'requeststatusid': requestschema['requeststatusid'] if  'requeststatusid' in requestschema  else  ministryschema["requeststatus.requeststatusid"],
            'programareaid': ministryschema["programarea.programareaid"] if 'programarea.programareaid' in ministryschema  else None,
            'closedate': requestschema['closedate'] if 'closedate' in requestschema  else None,
            'closereasonid': requestschema['closereasonid'] if 'closereasonid' in requestschema  else None
        }
    
    def createfoirequestdocuments(self,requestschema, ministryrequestid, activeversion, userid):
        documentarr = []
        documents = FOIMinistryRequestDocument().getdocuments(ministryrequestid, activeversion-1)
        existingdocuments = self.createfoirequestdocumentfromobject(documents,ministryrequestid ,activeversion, userid)       
        documentarr = existingdocuments
        if 'documents' in requestschema:
            newdocuments = self.createfoirequestdocument(requestschema,ministryrequestid ,activeversion, userid)  
            documentarr = newdocuments + existingdocuments
        return documentarr

    def createfoirequestextensions(self, ministryrequestid, activeversion, userid):
        extensions = FOIRequestExtension().getextensions(ministryrequestid, activeversion-1)
                 
        existingextensions = self.createfoirequestextensionfromobject(extensions,ministryrequestid ,activeversion, userid)
        if existingextensions is not None:
            return existingextensions
        else:
            return []
    
    def createfoirequestappplicantfromobject(self, requestapplicants, requestid, version, userid): 
        requestapplicantarr = []
        for requestapplicant in requestapplicants:
            applicantmapping  = FOIRequestApplicantMapping()
            applicantmapping.foirequest_id = requestid
            applicantmapping.foirequestversion_id = version
            applicantmapping.foirequestapplicantid = requestapplicant["foirequestapplicant.foirequestapplicantid"]
            applicantmapping.requestortypeid = requestapplicant["requestortype.requestortypeid"]
            applicantmapping.createdby = userid
            requestapplicantarr.append(applicantmapping)
        return requestapplicantarr

    def createfoirequestpersonalattributefromobject(self,personalattributes, requestid, version, userid):
        personalattributesarr = []
        for personalattribute in personalattributes:
            attribute = FOIRequestPersonalAttribute()
            attribute.personalattributeid = personalattribute["personalattributeid"]
            attribute.attributevalue = personalattribute["attributevalue"]
            attribute.foirequest_id = requestid
            attribute.foirequestversion_id = version
            attribute.createdby = userid
            personalattributesarr.append(attribute)
        return personalattributesarr

    def createfoirequestcontactfromobject(self, requestcontacts, requestid, version, userid):
        requestcontactarr = []
        for requestcontact in requestcontacts:
            contactinfo  = FOIRequestContactInformation()
            contactinfo.contacttypeid = requestcontact["contacttype.contacttypeid"]
            contactinfo.foirequest_id = requestid
            contactinfo.foirequestversion_id = version
            contactinfo.contactinformation = requestcontact["contactinformation"]
            contactinfo.dataformat = requestcontact["dataformat"]
            contactinfo.createdby = userid
            requestcontactarr.append(contactinfo)
        return requestcontactarr

    def createfoirequestdivisionfromobject(self, divisions, requestid, version, userid):
        divisionarr = []
        for division in divisions:
            ministrydivision = FOIMinistryRequestDivision()
            ministrydivision.divisionid = division["division.divisionid"]
            ministrydivision.stageid = division["stage.stageid"]
            ministrydivision.divisionduedate = division["divisionduedate"]
            ministrydivision.eapproval = division["eapproval"]
            ministrydivision.foiministryrequest_id = requestid
            ministrydivision.foiministryrequestversion_id = version
            ministrydivision.createdby = userid
            divisionarr.append(ministrydivision)
        return divisionarr
   
    def createfoirequestdocumentfromobject(self, documents, requestid, activeversion, userid):
        documentarr = []
        for document in documents:
            ministrydocument = FOIMinistryRequestDocument()
            ministrydocument.foiministrydocumentid = document["foiministrydocumentid"]
            ministrydocument.documentpath = document["documentpath"]
            if 'filename' in document:
                ministrydocument.filename = document["filename"]
            if 'category' in document:
                ministrydocument.category = document['category']
            ministrydocument.version = document['version'] + 1
            ministrydocument.foiministryrequest_id = requestid
            ministrydocument.foiministryrequestversion_id = activeversion
            ministrydocument.created_at = document["created_at"]
            ministrydocument.createdby =  document["createdby"]
            ministrydocument.updated_at = datetime2.now().isoformat()
            ministrydocument.updatedby =  userid
            documentarr.append(ministrydocument)
        return documentarr       

    def createfoirequestextensionfromobject(self, extensions, requestid, activeversion, userid):
        extensionarr = [] 
        for extension in extensions:
            requestextension = FOIRequestExtension()
            requestextension.foirequestextensionid = extension["foirequestextensionid"]
            requestextension.extensionreasonid = extension["extensionreasonid"]
            requestextension.extensionstatusid = extension["extensionstatusid"]
            if 'extendedduedays' in extension:
                requestextension.extendedduedays = extension["extendedduedays"]
            if 'extendedduedate' in extension:
                requestextension.extendedduedate = extension["extendedduedate"]
            if 'decisiondate' in extension:
                requestextension.decisiondate = extension["decisiondate"]
            if 'approvednoofdays' in extension:
                requestextension.approvednoofdays = extension["approvednoofdays"]
            requestextension.version = extension["version"] + 1
            requestextension.foiministryrequest_id = requestid
            requestextension.foiministryrequestversion_id = activeversion
            requestextension.created_at = extension["created_at"]
            requestextension.createdby =  extension["createdby"]
            requestextension.updated_at = datetime2.now().isoformat()
            requestextension.updatedby =  userid            
            documets = self.createextensiondocumentfromobject(FOIRequestExtensionDocumentMapping().getextensiondocuments(extension["foirequestextensionid"], extension["version"]), extension["version"] + 1, userid)
            requestextension.extensiondocuments = documets
            extensionarr.append(requestextension)
        return extensionarr

    def createextensiondocumentfromobject(self, extensiondocuments, activeversion, userid):
        extdocumentarr = []
        for extensiondocument in extensiondocuments:
            extensiondocumentmapping = FOIRequestExtensionDocumentMapping()
            extensiondocumentmapping.foirequestextensionid = extensiondocument["foirequestextensionid"]
            extensiondocumentmapping.extensionversion = activeversion
            extensiondocumentmapping.foiministrydocumentid = extensiondocument["foiministrydocumentid"]
            extensiondocumentmapping.createdby = userid
            extdocumentarr.append(extensiondocumentmapping)
        return extdocumentarr

    def createfoirequestdocument(self, requestschema, requestid, version, userid):
        documentarr = []
        if 'documents' in  requestschema:
            for document in requestschema['documents']:
                ministrydocument = FOIMinistryRequestDocument()
                ministrydocument.documentpath = document["documentpath"]
                ministrydocument.filename = document["filename"]
                if 'category' in document:
                    ministrydocument.category = document['category']
                ministrydocument.version = 1
                ministrydocument.foiministryrequest_id = requestid
                ministrydocument.foiministryrequestversion_id = version
                ministrydocument.createdby = userid
                ministrydocument.created_at = datetime2.now().isoformat()
                documentarr.append(ministrydocument)
            return documentarr    
    
    def createfoirequestdivision(self, requestschema, requestid, version, userid):
        divisionarr = []
        if 'divisions' in  requestschema:
            for division in requestschema['divisions']:
                ministrydivision = FOIMinistryRequestDivision()
                ministrydivision.divisionid = division["divisionid"]
                ministrydivision.stageid = division["stageid"]
                ministrydivision.divisionduedate = division["divisionDueDate"] if "divisionDueDate" in division and division["divisionDueDate"] != '' else None
                ministrydivision.eapproval = division["eApproval"] if "eApproval" in division else None
                ministrydivision.foiministryrequest_id = requestid
                ministrydivision.foiministryrequestversion_id = version
                ministrydivision.createdby = userid
                divisionarr.append(ministrydivision)
            return divisionarr

    def createfoiassigneefromobject(self, username, firstname, middlename, lastname):
        return FOIAssignee.saveassignee(username, firstname, middlename, lastname)
