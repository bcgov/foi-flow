
from os import stat
from re import VERBOSE
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.FOIRawRequestDocuments import FOIRawRequestDocument
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRawRequests import FOIRawRequest
import json


class documentservice:
    """ FOI Document management service

    """
    @classmethod    
    def getrequestdocuments(self, requestid, requesttype, version=None):
        requestversion =  self.getversionforrequest(requestid,requesttype) if version is None else version
        if requesttype == "ministryrequest":
            return FOIMinistryRequestDocument.getdocuments(requestid, requestversion)
        else:
            return FOIRawRequestDocument.getdocuments(requestid, requestversion)
            
    @classmethod    
    def createrequestdocument(self, requestid, documentschema, userid, requesttype):
        if requesttype == "ministryrequest":
            return self.createministryrequestdocument(requestid, documentschema, userid)
        else:
            return self.createrawrequestdocument(requestid, documentschema, userid)
    
    @classmethod    
    def createrequestdocumentversion(self, requestid, documentid, documentschema, userid, requesttype):
        if requesttype == "ministryrequest":
           return self.createministrydocumentversion(requestid, documentid, documentschema, userid)
        else:
            return self.createrawdocumentversion(requestid, documentid, documentschema, userid)

    @classmethod    
    def deleterequestdocument(self, requestid, documentid, userid, requesttype):
        documentschema = {'isactive':False}
        return self.createrequestdocumentversion(requestid, documentid, documentschema, userid, requesttype)
      
            
    @classmethod    
    def createministryrequestdocument(self, ministryrequestid, documentschema, userid):
        version = self.getversionforrequest(ministryrequestid, "ministryrequest")
        return FOIMinistryRequestDocument.createdocuments(ministryrequestid, version, documentschema['documents'], userid) 
    
    
    @classmethod    
    def createrawrequestdocument(self, requestid, documentschema, userid):
        version = self.getversionforrequest(requestid, "rawrequest")
        return FOIRawRequestDocument.createdocuments(requestid, version, documentschema['documents'], userid) 
    
    @classmethod    
    def createministrydocumentversion(self, ministryrequestid, documentid, documentschema, userid):
        version = self.getversionforrequest(ministryrequestid, "ministryrequest")
        document = FOIMinistryRequestDocument.getdocument(documentid)
        return FOIMinistryRequestDocument.createdocumentversion(ministryrequestid, version, self.copydocumentproperties(document,documentschema,document['version']), userid)    


    @classmethod    
    def createrawdocumentversion(self, requestid, documentid, documentschema, userid):
        version = self.getversionforrequest(requestid, "rawrequest")
        document = FOIRawRequestDocument.getdocument(documentid)
        return FOIRawRequestDocument.createdocumentversion(requestid, version, self.copydocumentproperties(document,documentschema,document['version']), userid)  
    
    @classmethod    
    def copyrequestdocuments(self, ministryrequestid, documents, userid):
        _documents = []        
        for document in documents:
            _documents.append({"documentpath":document["documentpath"],"filename":document["filename"],"category":document["category"], "created_at":document["created_at"],"createdby": document["createdby"]})
        documentschema = {"documents": _documents}
        return self.createministryrequestdocument(ministryrequestid, documentschema, userid)
    
    @classmethod    
    def copydocumentproperties(self, document, documentschema, version):
        document['version'] = version +1
        document['filename'] = documentschema['filename'] if 'filename' in documentschema  else document['filename']
        document['documentpath'] = documentschema['documentpath'] if 'documentpath' in documentschema else document['documentpath']
        document['category'] =  documentschema['category'] if 'category' in documentschema  else document['category']
        document['isactive'] =  documentschema['isactive'] if 'isactive' in documentschema  else True
        document['created_at'] =  documentschema['created_at'] if 'created_at' in documentschema  else None
        document['createdby'] = documentschema['createdby'] if 'createdby' in documentschema  else None
        return document
    
    @classmethod
    def getversionforrequest(self, requestid, requesttype):
        if requesttype == "ministryrequest":
            return FOIMinistryRequest.getversionforrequest(requestid)[0]
        else:
            return FOIRawRequest.getversionforrequest(requestid)[0]
      
    @classmethod  
    def createrawrequestdocumentversion(self, requestid):
        newversion = self.getversionforrequest(requestid,"rawrequest")     
        documents = self.getrequestdocuments(requestid, "rawrequest", newversion-1)
        documentarr = []
        for document in documents:
            documentarr.append({"documentpath": document["documentpath"], "filename": document["filename"], "category": document['category'], "version": 1, "foirequest_id": requestid, "foirequestversion_id": newversion - 1, "createdby": document['createdby'], "created_at": document['created_at']     })
        return self.createrawrequestdocument(requestid, {"documents": documentarr}, None)
          
