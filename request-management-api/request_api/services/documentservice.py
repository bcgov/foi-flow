
from os import stat
from re import VERBOSE
from request_api.models.FOIMinistryRequestDocuments import FOIMinistryRequestDocument
from request_api.models.FOIRawRequestDocuments import FOIRawRequestDocument
from request_api.models.FOIMinistryRequests import FOIMinistryRequest
from request_api.models.FOIRawRequests import FOIRawRequest
import json

import maya

from request_api.schemas.foirequestsformslist import  FOIRequestsFormsList
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import os
import uuid
import mimetypes

class documentservice:
    """ FOI Document management service

    """
    @classmethod    
    def getrequestdocuments(self, requestid, requesttype, version=None):
        requestversion =  self.getversionforrequest(requestid,requesttype) if version is None else version
        if requesttype == "ministryrequest":
            documents = FOIMinistryRequestDocument.getdocuments(requestid, requestversion)
            return self.formatcreateddateforall(documents)
        else:
            documents = FOIRawRequestDocument.getdocuments(requestid, requestversion)
            return self.formatcreateddateforall(documents)
            
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
    def formatcreateddateforall(self, documents):
        for document in documents:
            document = self.formatcreateddate(document)
        return documents

    @classmethod    
    def formatcreateddate(self, document):
        formatedCreatedDate = maya.parse(document['created_at']).datetime(to_timezone='America/Vancouver', naive=False)
        document['created_at'] = formatedCreatedDate.strftime('%Y %b %d | %I:%M %p')
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
      
    @classmethod  
    def uploadToS3(self, attachment):
        # print(attachment)

        #get S3 auth
        formsbucket = os.getenv('OSS_S3_FORMS_BUCKET')
        accesskey = os.getenv('OSS_S3_FORMS_ACCESS_KEY_ID') 
        secretkey = os.getenv('OSS_S3_FORMS_SECRET_ACCESS_KEY')
        s3host = os.getenv('OSS_S3_HOST')
        s3region = os.getenv('OSS_S3_REGION')
        s3service = os.getenv('OSS_S3_SERVICE')

        if(accesskey is None or secretkey is None or s3host is None or formsbucket is None):
            raise ValueError('accesskey is None or secretkey is None or S3 host is None or formsbucket is None')

        foirequestform = FOIRequestsFormsList().load(attachment)
        ministrycode = foirequestform.get('ministrycode')
        requestnumber = foirequestform.get('requestnumber')
        filestatustransition = foirequestform.get('filestatustransition')
        filename = foirequestform.get('filename')
        filenamesplittext = os.path.splitext(filename)
        uniquefilename = '{0}{1}'.format(uuid.uuid4(),filenamesplittext[1])

        auth = AWSRequestsAuth(aws_access_key=accesskey,
                aws_secret_access_key=secretkey,
                aws_host=s3host,
                aws_region=s3region,
                aws_service=s3service) 

        s3uri = 'https://{0}/{1}/{2}/{3}/{4}/{5}'.format(s3host,formsbucket,ministrycode,requestnumber,filestatustransition,uniquefilename)        
        response = requests.put(s3uri, data=None, auth=auth)

        header = {
            'X-Amz-Date': response.request.headers['x-amz-date'],
            'Authorization': response.request.headers['Authorization'],
            'Content-Type': mimetypes.MimeTypes().guess_type(filename)[0]
        }

        #upload to S3
        newresponse = requests.put(s3uri, data=attachment['file'], headers=header)

        attachmentobj = {'filename': filename, 'documentpath': s3uri, 'category': filestatustransition}
        return attachmentobj
