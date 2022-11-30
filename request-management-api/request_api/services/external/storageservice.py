from unicodedata import category
from request_api.schemas.foirequestsformslist import  FOIRequestsFormsList
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import os
import uuid
import mimetypes
import logging

from request_api.models.DocumentPathMapper import DocumentPathMapper
from request_api.utils.enums import DocumentPathMapperCategory

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config


formsbucket = os.getenv('OSS_S3_FORMS_BUCKET')
accesskey = os.getenv('OSS_S3_FORMS_ACCESS_KEY_ID') 
secretkey = os.getenv('OSS_S3_FORMS_SECRET_ACCESS_KEY')
s3host = os.getenv('OSS_S3_HOST')
s3region = os.getenv('OSS_S3_REGION')
s3service = os.getenv('OSS_S3_SERVICE')
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

    def uploadbytes(self, filename, bytes, ministrycode, requestnumber):
        try: 
            auth = AWSRequestsAuth(aws_access_key=accesskey,
                aws_secret_access_key=secretkey,
                aws_host=s3host,
                aws_region=s3region,
                aws_service=s3service) 

            s3uri = 'https://{0}/{1}/{2}/{3}/{4}'.format(s3host,formsbucket, ministrycode, requestnumber, filename)        
            response = requests.put(s3uri, data=None, auth=auth)
            header = {
                'X-Amz-Date': response.request.headers['x-amz-date'],
                'Authorization': response.request.headers['Authorization'],
                'Content-Type': mimetypes.MimeTypes().guess_type(filename)[0]
            }

            #upload to S3
            requests.put(s3uri, data=bytes, headers=header)
            attachmentobj = {"success": True, 'filename': filename, 'documentpath': s3uri}
        except Exception as ex:
            logging.error(ex)
            attachmentobj = {"success": False, 'filename': filename, 'documentpath': None}   
        return attachmentobj

    def upload(self, attachment):
        docpathmapper = DocumentPathMapper().getdocumentpath("Attachments")
        formsbucket = docpathmapper['bucket']
        
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
            docpathmapper = DocumentPathMapper().getdocumentpath(category,ministrycode)
            formsbucket = docpathmapper['bucket']
            auth = AWSRequestsAuth(aws_access_key=docpathmapper['attributes']['s3accesskey'],
                    aws_secret_access_key=docpathmapper['attributes']['s3secretkey'],
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
        docpathmapper = DocumentPathMapper().getdocumentpath(category, bcgovcode)
        formsbucket = docpathmapper['bucket']
        s3client = self.__get_s3client(category, docpathmapper)
        filename, file_extension = os.path.splitext(filepath)    
        response = s3client.generate_presigned_url(
            ClientMethod='get_object',
            Params=   {'Bucket': formsbucket, 'Key': '{0}'.format(filepath),'ResponseContentType': '{0}/{1}'.format('image' if file_extension in ['.png','.jpg','.jpeg','.gif'] else 'application',file_extension.replace('.',''))},
            ExpiresIn=3600,HttpMethod='GET'
        )
        return response

    def bulk_upload_s3_presigned(self, ministryrequestid, requestfilejson, category, bcgovcode=None):
        docpathmapper = DocumentPathMapper().getdocumentpath(category, bcgovcode)
        formsbucket = docpathmapper['bucket']
        s3client = self.__get_s3client(category, docpathmapper)
        for file in requestfilejson:                
            foirequestform = FOIRequestsFormsList().load(file)                
            ministrycode = foirequestform.get('ministrycode')
            requestnumber = foirequestform.get('requestnumber')
            filestatustransition = foirequestform.get('filestatustransition')
            filename = foirequestform.get('filename')
            filenamesplittext = os.path.splitext(filename)
            uniquefilename = '{0}{1}'.format(uuid.uuid4(),filenamesplittext[1])
            filepath = self.__getfilepath(category,ministrycode,requestnumber,filestatustransition,uniquefilename)
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
        categories = set(item.value.lower() for item in DocumentPathMapperCategory)
        return category in categories

    def __get_s3client(self, category, docpathmapper):
        return boto3.client('s3',config=Config(signature_version='s3v4'),
            endpoint_url='https://{0}/'.format(self.s3host),
            aws_access_key_id= docpathmapper['attributes']['s3accesskey'],
            aws_secret_access_key= docpathmapper['attributes']['s3secretkey'],
            region_name= self.s3region
        )

    def __getbucket(self, category, programarea=None):
        docpathmapper = DocumentPathMapper().getdocumentpath(category, programarea if category.lower() == "attachments" else None)
        return docpathmapper['bucket']

    def __getfilepath(self,category,ministrycode,requestnumber,filestatustransition,uniquefilename):
        if category.lower() == 'attachments':
            return '{0}/{1}/{2}/{3}'.format(ministrycode,requestnumber,filestatustransition,uniquefilename)
        elif category.lower() == 'records':
            return '{0}/{1}'.format(requestnumber,uniquefilename)
    
    def download(self, s3uri): 

        if(accesskey is None or secretkey is None or s3host is None or formsbucket is None):
            raise ValueError('accesskey is None or secretkey is None or S3 host is None or formsbucket is None')
        
        auth = AWSRequestsAuth(aws_access_key=accesskey,
                    aws_secret_access_key=secretkey,
                    aws_host=s3host,
                    aws_region=s3region,
                    aws_service=s3service)

        templatefile= requests.get(s3uri, auth=auth)
        return templatefile


    def downloadtemplate(self, templatepath):

        if(accesskey is None or secretkey is None or s3host is None or formsbucket is None):
            raise ValueError('accesskey is None or secretkey is None or S3 host is None or formsbucket is None')
        #To DO : make the values of templatetype and templatename dynamic
        s3uri = 'https://{0}/{1}{2}'.format(s3host,formsbucket,templatepath)
        templatefile= self.download(s3uri)
        responsehtml=templatefile.text
        return responsehtml
