
from re import T
from request_api.models.FOIRequests import FOIRequest
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRequestContactInformation import FOIRequestContactInformation
from request_api.models.FOIRequestPersonalAttributes import FOIRequestPersonalAttribute
from request_api.models.FOIRequestApplicantMappings import FOIRequestApplicantMapping
from request_api.models.FOIMinistryRequestDivisions import FOIMinistryRequestDivision
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
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
    
    def createfoiministryrequestfromobject(self, ministryschema, requestschema, userid):
        foiministryrequest = FOIMinistryRequest()
        foiministryrequest.foiministryrequestid = ministryschema["foiministryrequestid"] 
        foiministryrequest.version = ministryschema["version"] + 1
        foiministryrequest.foirequest_id = ministryschema["foirequest_id"] 
        foiministryrequest.foirequestversion_id = ministryschema["foirequestversion_id"] 
        foiministryrequest.description = ministryschema["description"]
        foiministryrequest.recordsearchfromdate = ministryschema['recordsearchfromdate'] if 'recordsearchfromdate' in ministryschema  else None
        foiministryrequest.recordsearchtodate = ministryschema['recordsearchtodate'] if 'recordsearchtodate' in ministryschema  else None
        foiministryrequest.filenumber = ministryschema["filenumber"]
        foiministryrequest.cfrduedate = ministryschema['cfrduedate'] if 'cfrduedate' in ministryschema  else None
        foiministryrequest.startdate = ministryschema['startdate'] if 'startdate' in ministryschema  else None
        foiministryrequest.duedate =ministryschema['duedate'] if 'duedate' in ministryschema  else None
        foiministryrequest.assignedministrygroup = requestschema['assignedministrygroup'] if 'assignedministrygroup' in requestschema  else ministryschema["assignedministrygroup"]
        foiministryrequest.assignedministryperson = requestschema['assignedministryperson'] if 'assignedministryperson' in requestschema  else ministryschema["assignedministryperson"]
        foiministryrequest.assignedgroup = requestschema['assignedgroup'] if 'assignedgroup' in requestschema  else ministryschema["assignedgroup"]
        foiministryrequest.assignedto = requestschema['assignedto'] if 'assignedto' in requestschema  else ministryschema["assignedto"]
        foiministryrequest.requeststatusid = requestschema['requeststatusid'] if  'requeststatusid' in requestschema  else  ministryschema["requeststatus.requeststatusid"]
        foiministryrequest.programareaid = ministryschema["programarea.programareaid"] if 'programarea.programareaid' in ministryschema  else None
        foiministryrequest.createdby = userid
        if 'divisions' in requestschema:
            foiministryrequest.divisions = self.createfoirequestdivision(requestschema,ministryschema["foiministryrequestid"] ,ministryschema["version"] + 1, userid)  
        else:
            divisions = FOIMinistryRequestDivision().getdivisions(ministryschema["foiministryrequestid"] ,ministryschema["version"])
            foiministryrequest.divisions = self.createfoirequestdivisionfromobject(divisions,ministryschema["foiministryrequestid"] ,ministryschema["version"] + 1, userid)  
        foiministryrequest.documents = self.createfoirequestdocuments(requestschema,ministryschema["foiministryrequestid"] ,ministryschema["version"] +1 , userid)       
        foiministryrequest.closedate = requestschema['closedate'] if 'closedate' in requestschema  else None
        foiministryrequest.closereasonid = requestschema['closereasonid'] if 'closereasonid' in requestschema  else None
        return foiministryrequest
    
    def createfoirequestdocuments(self,requestschema, ministryrequestid, activeversion, userid):
        documentarr = []
        documents = FOIMinistryRequestDocument().getdocuments(ministryrequestid, activeversion-1)
        existingdocuments = self.createfoirequestdocumentfromobject(documents,ministryrequestid ,activeversion, userid)       
        documentarr = existingdocuments
        if 'documents' in requestschema:
            newdocuments = self.createfoirequestdocument(requestschema,ministryrequestid ,activeversion, userid)  
            documentarr = newdocuments + existingdocuments
        return documentarr
    
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
            ministrydivision.foiministryrequest_id = requestid
            ministrydivision.foiministryrequestversion_id = version
            ministrydivision.createdby = userid
            divisionarr.append(ministrydivision)
        return divisionarr
   
    def createfoirequestdocumentfromobject(self, documents, requestid, activeversion, userid):
        documentarr = []
        for document in documents:
            ministrydocument = FOIMinistryRequestDocument()
            ministrydocument.documentpath = document["documentpath"]
            if 'filename' in document:
                ministrydocument.filename = document["filename"]
            if 'category' in document:
                ministrydocument.category = document['category']
            ministrydocument.version = 1
            ministrydocument.foiministryrequest_id = requestid
            ministrydocument.foiministryrequestversion_id = activeversion
            ministrydocument.created_at = document["created_at"] if 'created_at' in document else None
            ministrydocument.createdby =  document["createdby"] if 'createdby' in document else userid
            documentarr.append(ministrydocument)
        return documentarr   

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
                ministrydivision.foiministryrequest_id = requestid
                ministrydivision.foiministryrequestversion_id = version
                ministrydivision.createdby = userid
                divisionarr.append(ministrydivision)
            return divisionarr