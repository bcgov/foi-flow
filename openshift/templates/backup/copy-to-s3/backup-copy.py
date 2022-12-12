import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

BACKUP_BUCKET = os.getenv('OSS_S3_BACKUP_BUCKET')
ACCESS_KEY = os.getenv('OSS_S3_FORMS_ACCESS_KEY_ID') 
SECRET_KEY = os.getenv('OSS_S3_FORMS_SECRET_ACCESS_KEY')
S3_HOST = os.getenv('OSS_S3_HOST')
S3_REGION = os.getenv('OSS_S3_REGION')
BACKUP_DIRECTORY = os.getenv('BACKUP_DIRECTORY')
S3_SERVICE = os.getenv('OSS_S3_SERVICE')
UPLOAD_DIRECTORY = os.getenv('UPLOAD_DIRECTORY') or '/dev/'

# Optional env value.  If true, will not upload to S3, will only log
DRY_RUN = os.getenv('DRY_RUN') or False

def create_s3_connection():
    print('Creating s3 connection')
    print('Printing environment variables...')
    print({BACKUP_BUCKET, ACCESS_KEY, S3_HOST})

    s3client = boto3.client('s3',config=Config(signature_version='s3v4'),
        endpoint_url='https://{0}/'.format(S3_HOST),
        aws_access_key_id= ACCESS_KEY,
        aws_secret_access_key= SECRET_KEY,region_name=S3_REGION 
    )

    print('Created s3 client')
    return s3client

def upload_directory(client, local_directory, bucket, destination):
    print('Beginning upload_directory of: ' + local_directory)
    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            # construct the full local path
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, local_directory)
            s3_path = os.path.join(destination, relative_path)

            print('Searching "%s" in "%s"' % (s3_path, bucket))

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
    destination_folder = UPLOAD_DIRECTORY
    upload_directory(s3client, BACKUP_DIRECTORY, BACKUP_BUCKET, destination_folder)
