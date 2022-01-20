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

    def createrequestextension(self, foirequestid, ministryrequestid, extensionschema, userid):
        version = self.__getversionforrequest(ministryrequestid)
        extensionreason = extensionreasonservice().getextensionreasonbyid(extensionschema['extensionreasonid'])
        if 'extensiontype' in  extensionreason and extensionreason['extensiontype'] == 'Public Body':            
            ministryrequestschema = {
                "duedate": extensionschema['extendedduedate']
            }
            result = requestservice().saveministryrequestversion(ministryrequestschema, foirequestid, ministryrequestid, userid)
           
            if result.success == True:
                version = self.__getversionforrequest(ministryrequestid)
                extnsionresult = FOIRequestExtension.saveextension(ministryrequestid, version, extensionschema, extensionreason, userid)
        else:
            extnsionresult = FOIRequestExtension.saveextension(ministryrequestid, version, extensionschema, extensionreason, userid)
        return extnsionresult

    def createrequestextensionversion(self, foirequestid, ministryrequestid, extensionid, extensionschema, userid):
        documents = []    
        ministryversion = self.__getversionforrequest(ministryrequestid)
        extension = FOIRequestExtension.getextension(extensionid)
        updatedduedate = self.getlatestapprovedduedate(extension, extensionschema, extensionid, ministryrequestid, ministryversion)
        print("updatedduedate", updatedduedate)
        copyextension = self.__copyextensionproperties(extension, extensionschema, extension['version'])       
        if 'documents' in copyextension and copyextension['extensionstatusid'] != 1:
            documentids = self.__savedocumentversion(ministryrequestid, ministryversion, copyextension['documents'], userid)
            for documentid in documentids:
                documents.append(FOIMinistryRequestDocument().getdocument(documentid))
        extensioresult = self.saveextensiondocumentversion(ministryrequestid, ministryversion, extensionid, documents, copyextension, userid)        
        if extensioresult.success == True and updatedduedate:            
            # requestservice().updateministryrequestduedate(ministryrequestid, copyextension['extendedduedate'], userid )            
            ministryrequestschema = {
                "duedate": updatedduedate
            }
            requestservice().saveministryrequestversion(ministryrequestschema, foirequestid, ministryrequestid, userid)
        return extensioresult

    def getlatestapprovedduedate(self, extension, extensionschema, extensionid, ministryrequestid, ministryversion):
        approvedextension = None
        if extension["extensionstatusid"] == 2 and extensionschema["extensionstatusid"] != extension["extensionstatusid"]:
            approvedextension = FOIRequestExtension().getlatestapprovedextension(extensionid, ministryrequestid, ministryversion)
        extensionreason = extensionreasonservice().getextensionreasonbyid(extensionschema['extensionreasonid'])
        if approvedextension:
            return approvedextension['extendedduedate']
        elif ('extensionstatusid' in extensionschema and extensionschema['extensionstatusid'] == 2) or ('extensiontype' in  extensionreason and extensionreason['extensiontype'] == 'Public Body'):
            return extensionschema['extendedduedate']
        elif approvedextension is None and extension["extensionstatusid"] == 2:
            return FOIMinistryRequest.getrequestoriginalduedate(ministryrequestid)
        else:
            return None

    def saveextensiondocumentversion(self, ministryrequestid, ministryversion, extensionid, documents, extension, userid):
        extensionresult = FOIRequestExtension.createextensionversion(ministryrequestid, ministryversion, extension, userid)      
        if documents:
            FOIRequestExtensionDocumentMapping.saveextensiondocument(extensionid, documents, extension['version'], userid)
        return extensionresult

    def getrequestextension(self, extensionid):
        requestextension = FOIRequestExtension().getextension(extensionid)
        extensiondocuments = self.__getextensiondocuments(requestextension["foirequestextensionid"], requestextension["version"])
        documents = self.__getextensiondocumentsinfo(extensiondocuments)
        extensionreason = extensionreasonservice().getextensionreasonbyid(requestextension['extensionreasonid'])
        requestextensionwithdocuments = self.__createextensionobject(requestextension, documents, extensionreason)
        return requestextensionwithdocuments

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

    def __copyextensionproperties(self, extension, extensionschema, version):
        extension['version'] = version +1
        extension['extensionreasonid'] = extensionschema['extensionreasonid'] if 'extensionreasonid' in extensionschema  else extension['extensionreasonid']
        extension['extensionstatusid'] = extensionschema['extensionstatusid'] if 'extensionstatusid' in extensionschema  else extension['extensionstatusid']
        extension['extendedduedays'] = extensionschema['extendedduedays'] if 'extendedduedays' in extensionschema  else extension['extendedduedays']
        extension['extendedduedate'] = extensionschema['extendedduedate'] if 'extendedduedate' in extensionschema  else extension['extendedduedate']
        extension['decisiondate'] = extensionschema['decisiondate'] if 'decisiondate' in extensionschema  else extension['decisiondate']
        extension['approvednoofdays'] = extensionschema['approvednoofdays'] if 'approvednoofdays' in extensionschema  else extension['approvednoofdays']
        
        extension['documents'] = extensionschema['documents'] if 'documents' in extensionschema  else None
        extension['isactive'] =  extensionschema['isactive'] if 'isactive' in extensionschema  else True
        extension['created_at'] =  extensionschema['created_at'] if 'created_at' in extensionschema  else None
        extension['createdby'] = extensionschema['createdby'] if 'createdby' in extensionschema  else None
        return extension

    def __getversionforrequest(self, requestid):
        """ Returns the active version of the request id based on type.
        """       
        return FOIMinistryRequest.getversionforrequest(requestid)[0]

    def __formatdate(self, datevalue, format):        
        return datevalue.strftime(format) if datevalue is not None else None
        
  