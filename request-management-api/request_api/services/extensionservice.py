from datetime import datetime
from os import stat
from re import VERBOSE
from request_api.models.FOIRequestExtensions import FOIRequestExtension
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.FOIRequestExtensionDocumentMappings import FOIRequestExtensionDocumentMapping
from request_api.services.requestservice import requestservice
from request_api.services.documentservice import documentservice
from request_api.services.extensionreasonservice import extensionreasonservice
import json
import base64

class extensionservice:
    """ FOI Extension management service
    """

    def getrequestextensions(self, requestid, version=None):
        extensions = []
        created_atdateformat = '%Y-%m-%d %H:%M:%S.%f'
        otherdateformat = '%Y-%m-%d'
        requestversion =  self.__getversionforrequest(requestid) if version is None else version
        extensionrecords = FOIRequestExtension.getextensions(requestid, requestversion)        
        for entry in extensionrecords:               
                extensions.append({"foirequestextensionid": entry["foirequestextensionid"], 
                    "extensionreasonid": entry["extensionreasonid"], 
                    "extensionreson": entry["reason"],
                    "extensiontype": entry["extensiontype"],
                    "extensionstatusid": entry["extensionstatusid"], 
                    "extensionstatus": entry["name"],
                    "extendedduedays": entry["extendedduedays"], 
                    "extendedduedate": self.__formatdate(entry["extendedduedate"], otherdateformat),  
                    "decisiondate": self.__formatdate(entry["decisiondate"], otherdateformat), 
                    "approvednoofdays": entry["approvednoofdays"], 
                    "created_at": self.__formatdate(entry["created_at"], created_atdateformat),  
                    "createdby": entry["createdby"]})        
        return extensions
    def getrequestextension(self, extensionid):
        requestextension = FOIRequestExtension().getextension(extensionid)
        extensiondocuments = self.__getextensiondocuments(requestextension["foirequestextensionid"], requestextension["version"])
        documents = self.__getextensiondocumentsinfo(extensiondocuments)
        extensionreason = extensionreasonservice().getextensionreasonbyid(requestextension['extensionreasonid'])
        requestextensionwithdocuments = self.__createextensionobject(requestextension, documents, extensionreason)
        return requestextensionwithdocuments
        
    def createrequestextension(self, foirequestid, ministryrequestid, extensionschema, userid):
        version = self.__getversionforrequest(ministryrequestid)
        extensionreason = extensionreasonservice().getextensionreasonbyid(extensionschema['extensionreasonid'])
        
        ispublicbodyextension = 'extensiontype' in  extensionreason and extensionreason['extensiontype'] == 'Public Body'
        if ('extensionstatusid' in extensionschema and extensionschema['extensionstatusid'] == 2) or ispublicbodyextension:            
            ministryrequestschema = {
                "duedate": extensionschema['extendedduedate']
            }
            result = requestservice().saveministryrequestversion(ministryrequestschema, foirequestid, ministryrequestid, userid)
            
            if ispublicbodyextension:
                extensionschema['decisiondate'] = self.__formatdate(datetime.now(), '%Y-%m-%d')
                extensionschema['approvednoofdays'] = extensionschema['extendedduedays']
           
            if result.success == True:
                version = self.__getversionforrequest(ministryrequestid)
                extnsionresult = FOIRequestExtension.saveextension(ministryrequestid, version, extensionschema, extensionreason, userid)
        else:
            extnsionresult = FOIRequestExtension.saveextension(ministryrequestid, version, extensionschema, extensionreason, userid)
        if 'documents' in extensionschema and extensionschema['extensionstatusid'] != 1:
            self.saveextensiondocument(extensionschema, ministryrequestid, version, userid, extnsionresult.identifier)
        return extnsionresult

    def createrequestextensionversion(self, foirequestid, ministryrequestid, extensionid, extensionschema, userid):
        updatedduedate = None
        ministryversion = self.__getversionforrequest(ministryrequestid)
        extension = FOIRequestExtension.getextension(extensionid)
        extensionversion = extension['version']
        prevstatus = extension["extensionstatusid"]
        currentstatus = extensionschema["extensionstatusid"]
        isstatuschangedfromapproved = self.__isstatuschangedfromapproved(prevstatus, currentstatus)
        if isstatuschangedfromapproved == True:
            # gets the latest approved request
            approvedextension = self.getlatestapprovedrequest(extensionid, ministryrequestid, ministryversion)
            # gets the latest approved due date if any else gets the original due date
            updatedduedate = self.getlatestapprovedduedate(prevstatus, ministryrequestid, approvedextension)
       
        isdeletedocument = self.__isdeletedocument(isstatuschangedfromapproved, extensionid, extensionversion)
        if isdeletedocument == True:
            self.deletedocuments(extensionid, extensionversion, ministryrequestid, userid)  
       
        #copyextension has the updated extension with data passed from FE with the new version of extension       
        updatedextension = self.__copyextensionproperties(extension, extensionschema, extensionversion)
        # if current state is approved then gets the current extended due date
        extendedduedate = self.getextendedduedate(updatedextension)
 
        extensionresult = FOIRequestExtension.createextensionversion(ministryrequestid, ministryversion, updatedextension, userid)
        # save documents if it is part of current extension (update to the ministrydocuments table and extensiondocumentmapping table)
        if 'documents' in updatedextension and updatedextension['extensionstatusid'] != 1:
            self.saveextensiondocument(updatedextension['documents'], ministryrequestid, ministryversion, userid, extensionid)
        # updates the duedate to extendedduedate or updatedduedate
        # new ministry, extension, extensionmapping and document version gets created
        if extensionresult.success == True and (isstatuschangedfromapproved == True or updatedextension['extensionstatusid'] == 2):
            ministryrequestschema = {
                "duedate": extendedduedate if extendedduedate else updatedduedate
            }
            requestservice().saveministryrequestversion(ministryrequestschema, foirequestid, ministryrequestid, userid)
        return extensionresult
    
    def __isstatuschangedfromapproved(self, prevstatus,  currentstatus):        
        if prevstatus == 2 and currentstatus != prevstatus:
            return True

    def getduedatetoupdate(self, extension, ministryrequestid, updatedextension, approvedextension):        
        # gets the latest approved due date if any else gets the original due date
        updatedduedate = self.getlatestapprovedduedate(extension, ministryrequestid, approvedextension)
        # if current state is approved then gets the current extended due date
        extendedduedate = self.getextendedduedate(updatedextension) 
        return extendedduedate if extendedduedate else updatedduedate

    def saveextensiondocument(self, extensiondocuments, ministryrequestid, ministryversion, userid, extensionid):
        documents = []        
        documentids = self.__savedocumentversion(ministryrequestid, ministryversion, extensiondocuments, userid)
        for documentid in documentids:
            documents.append(FOIMinistryRequestDocument().getdocument(documentid))      
        self.saveextensiondocumentversion(extensionid, documents, userid)

    def __isdeletedocument(self, isstatuschangedfromapproved, extensionid, extensionversion):
        isdeletedocument = False
        documents = self.__getextensiondocuments(extensionid, extensionversion)
        # 1. if prev status is Approved and current status is Pending or Denied
        # 2. Prev extension has documents
        # if any of the above condition is true then deletedocuments
        if isstatuschangedfromapproved == True or documents:
            isdeletedocument = True            
        return isdeletedocument

    def deletedocuments(self,extensionid, extensionversion, ministryrequestid, userid): 
        documents = self.__getextensiondocuments(extensionid, extensionversion)        
        for document in documents:
            documentservice().deleterequestdocument(ministryrequestid, document["foiministrydocumentid"], userid, "ministryrequest")
  
    def getextendedduedate(self, extensionschema):
        extensionreason = extensionreasonservice().getextensionreasonbyid(extensionschema['extensionreasonid'])
        # if status is Approved or reason is Public Body then directly take the extendedduedate
        if ('extensionstatusid' in extensionschema and extensionschema['extensionstatusid'] == 2) or extensionreason['extensiontype'] == 'Public Body':
            return extensionschema['extendedduedate']

    def getlatestapprovedrequest(self, extensionid, ministryrequestid, ministryversion):
            return FOIRequestExtension().getlatestapprovedextension(extensionid, ministryrequestid, ministryversion)

    def getlatestapprovedduedate(self, prevstatus, ministryrequestid, approvedextension):       
        if approvedextension and len(approvedextension) != 0:            
            return approvedextension['extendedduedate']
        # if Prev extension status was Approved and no approved extension in FOIRequestExtension table then get the original DueDate from FOIMinisrtRequests table   
        elif prevstatus == 2 and not approvedextension:           
            duedate = FOIMinistryRequest.getrequestoriginalduedate(ministryrequestid)           
            return duedate
        #if current and prev status is Pending or Denied
        else:
            return None

    def saveextensiondocumentversion(self, extensionid, documents, userid):
        extensionversion = self.__getextensionversion(extensionid)
        if documents:
           return FOIRequestExtensionDocumentMapping.saveextensiondocument(extensionid, documents, extensionversion, userid)
        

    def __getextensionversion(self, extensionid):
        return FOIRequestExtension().getversionforextension(extensionid)

    def __createextensionobject(self, requestextension, documents, extensionreason):
        
        decisiondate = requestextension['decisiondate'] if 'decisiondate' in requestextension  else None
        approvednoofdays = requestextension['approvednoofdays'] if 'approvednoofdays' in requestextension  else None
        extension = {
            "foirequestextensionid": requestextension["foirequestextensionid"],
            "extensionreasonid": requestextension["extensionreasonid"],
            "extensionstatusid": requestextension["extensionstatusid"],
            "extendedduedays": requestextension["extendedduedays"],
            "extendedduedate": requestextension["extendedduedate"],
            "extensiontype": extensionreason["extensiontype"],
            "decisiondate": decisiondate,
            "approvednoofdays": approvednoofdays,
            "documents": documents
        }
        return extension

    def __getextensiondocuments(self, extensionid, extensionversion):
        return FOIRequestExtensionDocumentMapping().getextensiondocuments(extensionid, extensionversion)

    def __getextensiondocumentsinfo(self, extensiondocuments):
        reqdocuments = []
        for extensiondocument in extensiondocuments:
            document = FOIMinistryRequestDocument().getdocument(extensiondocument["foiministrydocumentid"])            
            reqdocuments.append({"foiministrydocumentid": document["foiministrydocumentid"], "filename": document["filename"], "documentpath": document["documentpath"], "category": document["category"]})
        return reqdocuments

    def __savedocumentversion(self, ministryrequestid, ministryversion, extensiondocumentschema, userid):
        documentids = []        
        for document in extensiondocumentschema:
            if 'foiministrydocumentid' in document:
                documentid = document['foiministrydocumentid']
            else:
                documentid = 0            
            documentresult = documentservice().createministrydocumentversion(ministryrequestid, documentid, document, userid)
            documentids.append(documentresult.identifier)
        return documentids

    def __copyextensionproperties(self, copyextension, extensionschema, version):
        copyextension['version'] = version +1
        copyextension['extensionreasonid'] = extensionschema['extensionreasonid'] if 'extensionreasonid' in extensionschema  else copyextension['extensionreasonid']
        copyextension['extensionstatusid'] = extensionschema['extensionstatusid'] if 'extensionstatusid' in extensionschema  else copyextension['extensionstatusid']
        copyextension['extendedduedays'] = extensionschema['extendedduedays'] if 'extendedduedays' in extensionschema  else copyextension['extendedduedays']
        copyextension['extendedduedate'] = extensionschema['extendedduedate'] if 'extendedduedate' in extensionschema  else copyextension['extendedduedate']
        copyextension['decisiondate'] = extensionschema['decisiondate'] if 'decisiondate' in extensionschema  else copyextension['decisiondate']
        copyextension['approvednoofdays'] = extensionschema['approvednoofdays'] if 'approvednoofdays' in extensionschema  else copyextension['approvednoofdays']
        
        copyextension['documents'] = extensionschema['documents'] if 'documents' in extensionschema  else None
        copyextension['isactive'] =  extensionschema['isactive'] if 'isactive' in extensionschema  else True
        copyextension['created_at'] =  extensionschema['created_at'] if 'created_at' in extensionschema  else None
        copyextension['createdby'] = extensionschema['createdby'] if 'createdby' in extensionschema  else None
        return copyextension

    def __getversionforrequest(self, requestid):
        """ Returns the active version of the request id based on type.
        """       
        return FOIMinistryRequest.getversionforrequest(requestid)[0]

    def __formatdate(self, datevalue, format):        
        return datevalue.strftime(format) if datevalue is not None else None
        
  