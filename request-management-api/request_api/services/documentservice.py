
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
    def getrequestdocuments(self, requestid, requesttype):
        if requesttype == "ministryrequest":
            return FOIMinistryRequestDocument.getdocuments(requestid)
        else:
            return FOIRawRequestDocument.getdocuments(requestid)
            
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
        version = FOIMinistryRequest.getversionforrequest(ministryrequestid)[0]
        return FOIMinistryRequestDocument.createdocuments(ministryrequestid, version, documentschema['documents'], userid) 
    
    
    @classmethod    
    def createrawrequestdocument(self, requestid, documentschema, userid):
        version = FOIRawRequest.getversionforrequest(requestid)[0]
        return FOIRawRequestDocument.createdocuments(requestid, version, documentschema['documents'], userid) 
    
    @classmethod    
    def createministrydocumentversion(self, ministryrequestid, documentid, documentschema, userid):
        version = FOIMinistryRequest.getversionforrequest(ministryrequestid)[0]
        document = FOIMinistryRequestDocument.getdocument(documentid)
        return FOIMinistryRequestDocument.createdocumentversion(ministryrequestid, version, self.copydocumentproperties(document,documentschema,document['version']), userid)    


    @classmethod    
    def createrawdocumentversion(self, requestid, documentid, documentschema, userid):
        version = FOIRawRequest.getversionforrequest(requestid)[0]
        document = FOIRawRequestDocument.getdocument(documentid)
        return FOIRawRequestDocument.createdocumentversion(requestid, version, self.copydocumentproperties(document,documentschema,document['version']), userid)  
    
    @classmethod    
    def copyrequestdocuments(self, ministryrequestid, documents, userid):
        _documents = []        
        for document in documents:
            _documents.append({"documentpath":document["documentpath"],"filename":document["filename"],"category":document["category"]})
        documentschema = {"documents": _documents}
        return self.createministryrequestdocument(ministryrequestid, documentschema, userid)
    
    @classmethod    
    def copydocumentproperties(self, document, documentschema, version):
        document['version'] = version +1
        document['filename'] = documentschema['filename'] if 'filename' in documentschema  else document['filename']
        document['documentpath'] = documentschema['documentpath'] if 'documentpath' in documentschema else document['documentpath']
        document['category'] =  documentschema['category'] if 'category' in documentschema  else document['category']
        document['isactive'] =  documentschema['isactive'] if 'isactive' in documentschema  else True
        return document
        