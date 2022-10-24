
from os import stat
from re import VERBOSE
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.FOIRawRequestDocuments import FOIRawRequestDocument
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRawRequests import FOIRawRequest
from request_api.schemas.foidocument import CreateDocumentSchema
from request_api.services.external.storageservice import storageservice
from request_api.models.FOIApplicantCorrespondenceAttachments import FOIApplicantCorrespondenceAttachment

import json
import base64
import maya

class documentservice:
    """ FOI Document management service
    """
    
    def getrequestdocuments(self, requestid, requesttype, version=None):
        requestversion =  self.__getversionforrequest(requestid,requesttype) if version is None else version
        documents = FOIMinistryRequestDocument.getdocuments(requestid, requestversion) if requesttype == "ministryrequest" else FOIRawRequestDocument.getdocuments(requestid, requestversion)
        return self.__formatcreateddate(documents)
    
    def getactiverequestdocuments(self, requestid, requesttype, version=None):
        requestversion =  self.__getversionforrequest(requestid,requesttype) if version is None else version
        documents = FOIMinistryRequestDocument.getactivedocuments(requestid) if requesttype == "ministryrequest" else FOIRawRequestDocument.getdocuments(requestid, requestversion)
        return self.__formatcreateddate(documents)
    
    def getrequestdocumentsbyrole(self, requestid, requesttype, isministrymember):
        documents = self.getactiverequestdocuments(requestid, requesttype)
        if isministrymember:
            for document in documents:
                if document["category"] == "personal":
                    document["documentpath"] = ""        
        return documents

    def createrequestdocument(self, requestid, documentschema, userid, requesttype):
        if requesttype == "ministryrequest":
            return self.createministryrequestdocument(requestid, documentschema, userid)
        else:
            return self.createrawrequestdocument(requestid, documentschema, userid)

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

    def createministryrequestdocument(self, ministryrequestid, documentschema, userid):
        version = self.__getversionforrequest(ministryrequestid, "ministryrequest")
        return FOIMinistryRequestDocument.createdocuments(ministryrequestid, version, documentschema['documents'], userid)

    def createrawrequestdocument(self, requestid, documentschema, userid):
        version = self.__getversionforrequest(requestid, "rawrequest")
        return FOIRawRequestDocument.createdocuments(requestid, version, documentschema['documents'], userid)

    def createministrydocumentversion(self, ministryrequestid, documentid, documentschema, userid):
        version = self.__getversionforrequest(ministryrequestid, "ministryrequest")        
        document = FOIMinistryRequestDocument.getdocument(documentid)
        FOIMinistryRequestDocument.deActivateministrydocumentsversion(documentid, document['version']+1, userid)
        if document:
           return FOIMinistryRequestDocument.createdocumentversion(ministryrequestid, version, self.__copydocumentproperties(document,documentschema,document['version']), userid)          
        elif isinstance(documentschema, list):            
            return FOIMinistryRequestDocument.createdocuments(ministryrequestid, version, documentschema, userid)
        else:
            return FOIMinistryRequestDocument.createdocument(ministryrequestid, version, documentschema, userid)
        
        
    def createrawdocumentversion(self, requestid, documentid, documentschema, userid):
        version = self.__getversionforrequest(requestid, "rawrequest")
        document = FOIRawRequestDocument.getdocument(documentid)
        FOIRawRequestDocument.deActivaterawdocumentsversion(documentid, document['version']+1, userid)
        return FOIRawRequestDocument.createdocumentversion(requestid, version, self.__copydocumentproperties(document,documentschema,document['version']), userid)

    def createrawrequestdocumentversion(self, requestid):
        newversion = self.__getversionforrequest(requestid,"rawrequest")
        documents = self.getrequestdocuments(requestid, "rawrequest", newversion-1)
        documentarr = []
        for document in documents:
            documentarr.append({"documentpath": document["documentpath"], "filename": document["filename"], "category": document['category'], "version": 1, "foirequest_id": requestid, "foirequestversion_id": newversion - 1, "createdby": document['createdby'], "created_at": document['created_at']     })
        return self.createrawrequestdocument(requestid, {"documents": documentarr}, None)

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

    def getattachments(self, requestid, requesttype, category):        
        documents = self.getlatestdocumentsforemail(requestid, requesttype, category)  
        return self.__getattachmentlist(documents)
    
    def getreceiptattachments(self, ministryrequestid, category):
        print("category = ", category)
        _documents = FOIMinistryRequestDocument().getlatestreceiptdocumentforemail(ministryrequestid, category)
        documents = self.__formatcreateddate(_documents) 
        return self.__getattachmentlist(documents)
    
    def getlatestdocumentsforemail(self, requestid, requesttype, category, version=None):
        requestversion =  self.__getversionforrequest(requestid,requesttype) if version is None else version
        print("requestversion = ",requestversion)
        documents = FOIMinistryRequestDocument.getlatestdocumentsforemail(requestid, requestversion, category) if requesttype == "ministryrequest" else FOIRawRequestDocument.getdocuments(requestid, requestversion)
        return self.__formatcreateddate(documents)    

    def getapplicantcorrespondenceattachmentsbyapplicantcorrespondenceid(self, applicantcorrespondenceid):
        documents = FOIApplicantCorrespondenceAttachment.getapplicantcorrespondenceattachmentsbyapplicantcorrespondenceid(applicantcorrespondenceid)
        if(documents is None):
            raise ValueError('No template found')
        attachmentlist = []
        for document in documents:  
            filename = document.get('attachmentfilename')
            s3uri = document.get('attachmentdocumenturipath')
            attachment= storageservice().download(s3uri)
            attachdocument = {"filename": filename, "file": attachment, "url": s3uri}
            attachmentlist.append(attachdocument)
        return attachmentlist
    
    def __getattachmentlist(self, documents):
        if(documents is None):
            raise ValueError('No template found')
        attachmentlist = []
        for document in documents:  
            filename = document.get('filename')
            s3uri = document.get('documentpath')
            attachment= storageservice().download(s3uri)
            attachdocument = {"filename": filename, "file": attachment, "url": s3uri}
            attachmentlist.append(attachdocument)
        return attachmentlist
    
    def __getversionforrequest(self, requestid, requesttype):
        """ Returns the active version of the request id based on type.
        """
        if requesttype == "ministryrequest":
            document = FOIMinistryRequest.getversionforrequest(requestid)
        else:
            document = FOIRawRequest.getversionforrequest(requestid)
        if document:
            return document[0]

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



