
from os import stat
from re import VERBOSE
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
import json
from dateutil.parser import *
import datetime 


class documentservice:
    """ FOI watcher management service

    """
    @classmethod    
    def getministryrequestdocuments(self, ministryrequestid):
        return FOIMinistryRequestDocument.getdocuments(ministryrequestid)
 
    @classmethod    
    def createministryrequestdocument(self, ministryrequestid, documentschema, userid):
        version = FOIMinistryRequest.getversionforrequest(ministryrequestid)[0]
        return FOIMinistryRequestDocument.createdocuments(ministryrequestid, version, documentschema['documents'], userid) 
    
    @classmethod    
    def renameministryrequestdocument(self, ministryrequestid, documentid, documentschema, userid):
        return self.createministrydocumentversion(ministryrequestid, documentid, documentschema, userid)
    
    @classmethod    
    def replaceministryrequestdocument(self, ministryrequestid, documentid,documentschema,  userid):
        return self.createministrydocumentversion(ministryrequestid, documentid, documentschema, userid)
    
    @classmethod    
    def deleteministryrequestdocument(self, ministryrequestid, documentid, userid):
        documentschema = {'isactive':False}
        return self.createministrydocumentversion(ministryrequestid, documentid, documentschema, userid)
     
    
    @classmethod    
    def createministrydocumentversion(self, ministryrequestid, documentid, documentschema, userid):
        version = FOIMinistryRequest.getversionforrequest(ministryrequestid)[0]
        document = FOIMinistryRequestDocument.getdocument(documentid)
        document['version'] = document['version'] +1
        document['filename'] = documentschema['filename'] if 'filename' in documentschema  else document['filename']
        document['documentpath'] = documentschema['documentpath'] if 'documentpath' in documentschema else document['documentpath']
        document['category'] =  documentschema['category'] if 'category' in documentschema  else document['category']
        document['isactive'] =  documentschema['isactive'] if 'isactive' in documentschema  else True
        return FOIMinistryRequestDocument.createdocumentversion(ministryrequestid, version, document, userid)    
