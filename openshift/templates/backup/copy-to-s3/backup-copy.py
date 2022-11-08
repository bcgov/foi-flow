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

def create_s3_connection():
    print('Creating s3 connection')

    # filepath = request.args.get('filepath')

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

    print('Created s3 client')

    return s3client

# def upload_directory(s3client, path, bucketname):
#     for root,dirs,files in os.walk(path):
#         for file in files:
#             s3client.upload_file(os.path.join(root,file), bucketname, file)


def upload_directory(client, local_directory, bucket, destination):
    print('Beginning upload_directory of: ' + local_directory)
    for root, dirs, files in os.walk(local_directory):
        for filename in files:

            # construct the full local path
            local_path = os.path.join(root, filename)

            # construct the full Dropbox path
            relative_path = os.path.relpath(local_path, local_directory)
            s3_path = os.path.join(destination, relative_path)

            # relative_path = os.path.relpath(os.path.join(root, filename))

            print('Searching "%s" in "%s"' % (s3_path, bucket))
            try:
                client.head_object(Bucket=bucket, Key=s3_path)
                print("Path found on S3! Skipping %s..." % s3_path)

                # try:
                    # client.delete_object(Bucket=bucket, Key=s3_path)
                # except:
                    # print "Unable to delete %s..." % s3_path
            except:
                print("Uploading %s..." % s3_path)
                client.upload_file(local_path, bucket, s3_path)


if __name__ == "__main__":
    BACKUP_DIRECTORY = os.getenv('BACKUP_DIRECTORY')
    s3client = create_s3_connection()
    # TODO: Do we want this as an env var? Probably not.
    destination_folder = '/foi-backups/'

    upload_directory(s3client, BACKUP_DIRECTORY, BACKUP_BUCKET, destination_folder)

    # print('s3client')
    # print(s3client)
