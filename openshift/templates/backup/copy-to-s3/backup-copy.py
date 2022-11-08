import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

print('test')

def create_s3_connection():
    print('Creating s3 connection')
    formsbucket = os.getenv('OSS_S3_FORMS_BUCKET')
    accesskey = os.getenv('OSS_S3_FORMS_ACCESS_KEY_ID') 
    secretkey = os.getenv('OSS_S3_FORMS_SECRET_ACCESS_KEY')
    s3host = os.getenv('OSS_S3_HOST')
    s3region = os.getenv('OSS_S3_REGION')
    # filepath = request.args.get('filepath')

    # print('Printing environment variables...')
    # print({formsbucket, accesskey})

    s3client = boto3.client('s3',config=Config(signature_version='s3v4'),
        endpoint_url='https://{0}/'.format(s3host),
        aws_access_key_id= accesskey,
        aws_secret_access_key= secretkey,region_name= s3region
    )

    return s3client

if __name__ == "__main__":
    s3client = create_s3_connection()