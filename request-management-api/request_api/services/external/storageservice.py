from request_api.schemas.foirequestsformslist import  FOIRequestsFormsList
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
import os
import uuid
import mimetypes
import logging

formsbucket = os.getenv('OSS_S3_FORMS_BUCKET')
accesskey = os.getenv('OSS_S3_FORMS_ACCESS_KEY_ID') 
secretkey = os.getenv('OSS_S3_FORMS_SECRET_ACCESS_KEY')
s3host = os.getenv('OSS_S3_HOST')
s3region = os.getenv('OSS_S3_REGION')
s3service = os.getenv('OSS_S3_SERVICE')
class storageservice:
    """This class is reserved for S3 storage services integration.
    """
    
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
        requests.put(s3uri, data=attachment['file'], headers=header)

        attachmentobj = {'filename': filename, 'documentpath': s3uri, 'category': filestatustransition}
        return attachmentobj
    
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


    def downloadtemplate(self, templatename): 

        s3templatefolder= "TEMPLATES"
        if(accesskey is None or secretkey is None or s3host is None or formsbucket is None):
            raise ValueError('accesskey is None or secretkey is None or S3 host is None or formsbucket is None')
        #To DO : make the values of templatetype and templatename dynamic
        templatetype= 'EMAILS'
        s3uri = 'https://{0}/{1}/{2}/{3}/{4}'.format(s3host,formsbucket,s3templatefolder,templatetype,templatename)
        templatefile= self.download(s3uri)
        responsehtml=templatefile.text
        return responsehtml