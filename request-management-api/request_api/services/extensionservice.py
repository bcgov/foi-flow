from os import stat
from re import VERBOSE
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.FOIRequestExtensions import FOIRequestExtension
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
import json
import base64
import maya

class extensionservice:
    """ FOI Extension management service
    """
    
    def getrequestextensions(self, requestid, version=None):
        requestversion =  self.__getversionforrequest(requestid) if version is None else version
        extensions = FOIRequestExtension.getextension(requestid, requestversion)
        return self.__formatcreateddate(extensions)

    def createrequestextnesion(self, ministryrequestid, extensionschema, userid):
        version = 1 #self.__getversionforrequest(ministryrequestid)
        return FOIRequestExtension.createextension(ministryrequestid, version, extensionschema['extension'], userid)
        

    def createrequestdocumentversion(self, requestid, documentid, documentschema, userid, requesttype):
        if requesttype == "ministryrequest":
           return self.createministrydocumentversion(requestid, documentid, documentschema, userid)
        else:
            return self.createrawdocumentversion(requestid, documentid, documentschema, userid)

    def deleterequestdocument(self, requestid, documentid, userid, requesttype):
        documentschema = {'isactive':False}
        return self.createrequestdocumentversion(requestid, documentid, documentschema, userid, requesttype)

    def copyrequestdocuments(self, ministryrequestid, documents, userid):
        """ Copies request documents upon updates
        """
        _documents = []
        for document in documents:
            _documents.append({"documentpath":document["documentpath"],"filename":document["filename"],"category":document["category"], "created_at":document["created_at"],"createdby": document["createdby"]})
        documentschema = {"documents": _documents}
        return self.createministryrequestdocument(ministryrequestid, documentschema, userid)


    

    def createministrydocumentversion(self, ministryrequestid, documentid, documentschema, userid):
        version = self.__getversionforrequest(ministryrequestid)
        document = FOIMinistryRequestDocument.getdocument(documentid)
        return FOIMinistryRequestDocument.createdocumentversion(ministryrequestid, version, self.__copydocumentproperties(document,documentschema,document['version']), userid)   
   
    def uploadpersonaldocuments(self, requestid, attachments):
        attachmentlist = []
        if attachments:
            for attachment in attachments:
                attachment['filestatustransition'] = 'personal'
                attachment['ministrycode'] = 'Misc'
                attachment['requestnumber'] = str(requestid)
                attachment['file'] = base64.b64decode(attachment['base64data'])
                attachment.pop('base64data')
                attachmentresponse = storageservice().upload(attachment)
                attachmentlist.append(attachmentresponse)
                
            documentschema = CreateDocumentSchema().load({'documents': attachmentlist})
            return self.createrequestdocument(requestid, documentschema, None, "rawrequest")        

    def __getversionforrequest(self, requestid):
        """ Returns the active version of the request id based on type.
        """       
        return FOIMinistryRequest.getversionforrequest(requestid)[0]
        

    def __copydocumentproperties(self, document, documentschema, version):
        document['version'] = version +1
        document['filename'] = documentschema['filename'] if 'filename' in documentschema  else document['filename']
        document['documentpath'] = documentschema['documentpath'] if 'documentpath' in documentschema else document['documentpath']
        document['category'] =  documentschema['category'] if 'category' in documentschema  else document['category']
        document['isactive'] =  documentschema['isactive'] if 'isactive' in documentschema  else True
        document['created_at'] =  documentschema['created_at'] if 'created_at' in documentschema  else None
        document['createdby'] = documentschema['createdby'] if 'createdby' in documentschema  else None
        return document

    def __formatcreateddate(self, documents):
        for document in documents:
            document = self.__pstformat(document)
        return documents

    def __pstformat(self, document):
        formatedcreateddate = maya.parse(document['created_at']).datetime(to_timezone='America/Vancouver', naive=False)
        document['created_at'] = formatedcreateddate.strftime('%Y %b %d | %I:%M %p')
        return document