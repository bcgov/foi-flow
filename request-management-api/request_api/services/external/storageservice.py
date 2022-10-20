from unicodedata import category
from request_api.schemas.foirequestsformslist import  FOIRequestsFormsList
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import os
import uuid
import mimetypes

from request_api.models.DocumentPathMapper import DocumentPathMapper

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

class storageservice:
    """This class is reserved for S3 storage services integration.
    """
    accesskey = os.getenv('OSS_S3_FORMS_ACCESS_KEY_ID') 
    secretkey = os.getenv('OSS_S3_FORMS_SECRET_ACCESS_KEY')
    recordsaccesskey = os.getenv('OSS_S3_RECORDS_ACCESS_KEY_ID')
    recordssecretkey = os.getenv('OSS_S3_RECORDS_SECRET_ACCESS_KEY')
    s3host = os.getenv('OSS_S3_HOST')
    s3region = os.getenv('OSS_S3_REGION')
    s3service = os.getenv('OSS_S3_SERVICE') 
    s3environment = os.getenv('OSS_S3_ENVIRONMENT') 
    s3timeout = 3600

    def upload(self, attachment):        
        formsbucket = self.__getbucket("Attachments")
        
        if(self.accesskey is None or self.secretkey is None or self.s3host is None or formsbucket is None):
            raise ValueError('accesskey is None or secretkey is None or S3 host is None or formsbucket is None')

        foirequestform = FOIRequestsFormsList().load(attachment)
        ministrycode = foirequestform.get('ministrycode')
        requestnumber = foirequestform.get('requestnumber')
        filestatustransition = foirequestform.get('filestatustransition')
        filename = foirequestform.get('filename')
        filenamesplittext = os.path.splitext(filename)
        uniquefilename = '{0}{1}'.format(uuid.uuid4(),filenamesplittext[1])

        auth = AWSRequestsAuth(aws_access_key=self.accesskey,
                aws_secret_access_key=self.secretkey,
                aws_host=self.s3host,
                aws_region=self.s3region,
                aws_service=self.s3service) 

        s3uri = 'https://{0}/{1}/{2}/{3}/{4}/{5}'.format(self.s3host,formsbucket,ministrycode,requestnumber,filestatustransition,uniquefilename)        
        response = requests.put(s3uri, data=None, auth=auth)

        header = {
            'X-Amz-Date': response.request.headers['x-amz-date'],
            'Authorization': response.request.headers['Authorization'],
            'Content-Type': mimetypes.MimeTypes().guess_type(filename)[0]
        }

        #upload to S3
        requests.put(s3uri, data=attachment['file'], headers=header)

        attachmentobj = {'filename': filename, 'documentpath': s3uri, 'category': filestatustransition}
        return attachmentobj

    def bulk_upload(self, requestfilejson, category):
        
        if(self.accesskey is None or self.secretkey is None or self.s3host is None):
            return {'status': "Configuration Issue", 'message':"accesskey is None or secretkey is None or S3 host is None or formsbucket is None"}, 500

        for file in requestfilejson:                
            foirequestform = FOIRequestsFormsList().load(file)                
            ministrycode = foirequestform.get('ministrycode')
            requestnumber = foirequestform.get('requestnumber')
            filestatustransition = foirequestform.get('filestatustransition')
            filename = foirequestform.get('filename')
            s3sourceuri = foirequestform.get('s3sourceuri')
            filenamesplittext = os.path.splitext(filename)
            uniquefilename = '{0}{1}'.format(uuid.uuid4(),filenamesplittext[1]) 
            formsbucket = self.__getbucket(category,ministrycode)               
            auth = AWSRequestsAuth(aws_access_key=self.accesskey,
                    aws_secret_access_key=self.secretkey,
                    aws_host=self.s3host,
                    aws_region=self.s3region,
                    aws_service=self.s3service) 

            s3uri = s3sourceuri if s3sourceuri is not None else 'https://{0}/{1}/{2}/{3}/{4}/{5}'.format(self.s3host, formsbucket,ministrycode,requestnumber,filestatustransition,uniquefilename)        
            response = requests.put(s3uri,data=None,auth=auth) if s3sourceuri is None  else requests.get(s3uri,auth=auth)

            file['filepath']=s3uri
            file['authheader']=response.request.headers['Authorization'] 
            file['amzdate']=response.request.headers['x-amz-date']
            file['uniquefilename']=uniquefilename if s3sourceuri is None else ''
            file['filestatustransition']=filestatustransition  if s3sourceuri is None else ''
        return requestfilejson

    def retrieve_s3_presigned(self, filepath, category="attachments", bcgovcode=None):
        formsbucket = self.__getbucket(category, bcgovcode)
        s3client = self.__get_s3client(category)
        filename, file_extension = os.path.splitext(filepath)    
        response = s3client.generate_presigned_url(
            ClientMethod='get_object',
            Params=   {'Bucket': formsbucket, 'Key': '{0}'.format(filepath),'ResponseContentType': '{0}/{1}'.format('image' if file_extension in ['.png','.jpg','.jpeg','.gif'] else 'application',file_extension.replace('.',''))},
            ExpiresIn=3600,HttpMethod='GET'
        )
        return response

    def bulk_upload_s3_presigned(self, ministryrequestid, requestfilejson, category):
        s3client = self.__get_s3client(category)
        for file in requestfilejson:                
            foirequestform = FOIRequestsFormsList().load(file)                
            ministrycode = foirequestform.get('ministrycode')
            requestnumber = foirequestform.get('requestnumber')
            filestatustransition = foirequestform.get('filestatustransition')
            filename = foirequestform.get('filename')
            filenamesplittext = os.path.splitext(filename)
            uniquefilename = '{0}{1}'.format(uuid.uuid4(),filenamesplittext[1])
            filepath = self.__getfilepath(category,ministrycode,requestnumber,filestatustransition,uniquefilename)
            formsbucket = self.__getbucket(category,ministrycode)
            response = s3client.generate_presigned_url(
                ClientMethod='put_object',
                Params=   {
                    'Bucket': formsbucket,
                    'Key': '{0}'.format(filepath)                        
                },
                ExpiresIn=self.s3timeout, HttpMethod='PUT'
                )
            file['filepath']=response
            file['filepathdb']='https://{0}/{1}/{2}'.format(self.s3host,formsbucket,filepath)
            file['uniquefilename']=uniquefilename        
        return requestfilejson    

    def is_valid_category(self, category):
        docpathmappers = DocumentPathMapper().getdocumentpath()
        for docpathmapper in docpathmappers:
            if docpathmapper['category'].lower() == category:
                return True
        return False    

    def __get_s3client(self, category):
        return boto3.client('s3',config=Config(signature_version='s3v4'),
            endpoint_url='https://{0}/'.format(self.s3host),
            aws_access_key_id= self.accesskey if category == 'attachments' else self.recordsaccesskey,
            aws_secret_access_key= self.secretkey if category == 'attachments' else self.recordssecretkey,
            region_name= self.s3region
        )

    def __getbucket(self, category, programarea=None):
        docpathmappers = DocumentPathMapper().getdocumentpath()
        defaultbucket = None
        for docpathmapper in docpathmappers:
            if docpathmapper['category'].lower() == "attachments":
                defaultbucket = self.__formatbucketname(docpathmapper['bucket'], programarea)
            if docpathmapper['category'].lower() == category.lower():
                return self.__formatbucketname(docpathmapper['bucket'], programarea)
        return  defaultbucket 

    def __formatbucketname(self, bucket, bcgovcode):
        _bucket = bucket.replace('$environment', self.s3environment)
        if bcgovcode is not None:
            _bucket = _bucket.replace('$bcgovcode', bcgovcode.lower())
        return _bucket        

    def __getfilepath(self,category,ministrycode,requestnumber,filestatustransition,uniquefilename):
        if category.lower() == 'attachments':
            return '{0}/{1}/{2}/{3}'.format(ministrycode,requestnumber,filestatustransition,uniquefilename)
        elif category.lower() == 'records':
            return '{0}/{1}'.format(requestnumber,uniquefilename)
