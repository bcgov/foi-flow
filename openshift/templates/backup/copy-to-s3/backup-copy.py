import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from dotenv import load_dotenv

# Boto3 backups
# aws_requests_auth
# from aws_requests_auth.aws_auth import AWSRequestsAuth

load_dotenv()


BACKUP_BUCKET = os.getenv('OSS_S3_BACKUP_BUCKET')
ACCESS_KEY = os.getenv('OSS_S3_FORMS_ACCESS_KEY_ID') 
SECRET_KEY = os.getenv('OSS_S3_FORMS_SECRET_ACCESS_KEY')
S3_HOST = os.getenv('OSS_S3_HOST')
S3_REGION = os.getenv('OSS_S3_REGION')
BACKUP_DIRECTORY = os.getenv('BACKUP_DIRECTORY')
S3_SERVICE = os.getenv('OSS_S3_SERVICE')


# Optional env value.  If true, will not upload to S3, will only log
DRY_RUN = os.getenv('DRY_RUN') or False

def create_s3_connection():
    print('Creating s3 connection')
    print('Printing environment variables...')
    print({BACKUP_BUCKET, ACCESS_KEY, S3_HOST})
    # print({S3_HOST})
    # print({ACCESS_KEY})
    # print({BACKUP_BUCKET})

    s3client = boto3.client('s3',config=Config(signature_version='s3v4'),
        endpoint_url='https://{0}/'.format(S3_HOST),
        aws_access_key_id= ACCESS_KEY,
        aws_secret_access_key= SECRET_KEY,region_name=S3_REGION 
    )

    # TODO - Try this way if boto3 fails
    # auth = AWSRequestsAuth(aws_access_key=ACCESS_KEY,
    #     aws_secret_access_key=SECRET_KEY,
    #     aws_host=S3_HOST,  # check if should be formatted like   'https://{0}/'.format(S3_HOST)
    #     aws_region=S3_REGION,
    #     aws_service=S3_SERVICE) 

    print('Created s3 client')
    return s3client

    # return auth

def upload_directory(client, local_directory, bucket, destination):
    print('Beginning upload_directory of: ' + local_directory)
    for root, dirs, files in os.walk(local_directory):
        for filename in files:

            # construct the full local path
            local_path = os.path.join(root, filename)

            relative_path = os.path.relpath(local_path, local_directory)
            s3_path = os.path.join(destination, relative_path)

            # relative_path = os.path.relpath(os.path.join(root, filename))

            print('Searching "%s" in "%s"' % (s3_path, bucket))

            # TODO: Re-write this into normal if/else, no need to try/except it
            # USE POSTMAN FOR "nosuchbucket" test.
            # Add StackOverFlow post of current suggestion of uploading backup-container to S3
            try:
                if DRY_RUN:
                    print("DRY-RUN: Path found on S3! Skipping %s..." % s3_path)
                else:
                    client.head_object(Bucket=bucket, Key=s3_path)
                    print("Path found on S3! Skipping %s..." % s3_path)
            except:
                if DRY_RUN:
                    print("DRY-RUN: Uploading %s..." % s3_path)
                else:
                    print("Uploading %s..." % s3_path)
                    client.upload_file(local_path, bucket, s3_path)


if __name__ == "__main__":
    s3client = create_s3_connection()
    # TODO: Do we want this as an env var? Probably not.
    destination_folder = '/foi-backups/'

    upload_directory(s3client, BACKUP_DIRECTORY, BACKUP_BUCKET, destination_folder)

    # print('s3client')
    # print(s3client)
