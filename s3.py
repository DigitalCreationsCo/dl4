import boto3
from botocore.exceptions import ClientError
import os
from werkzeug.utils import secure_filename

BUCKET_NAME = os.environ.get('AWS_S3_BUCKET')
REGION = os.environ.get('AWS_REGION')
s3_client = boto3.client('s3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=REGION
)


def upload_file_to_s3(file, object_name=None):
    if object_name is None:
        object_name = secure_filename(file.filename)

    try:
        s3_client.upload_fileobj(file, BUCKET_NAME, object_name)
    except ClientError as e:
        print(e)
        return None
    return f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{object_name}"

def get_file_from_s3(object_name):
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=object_name)
        return response['Body'].read()
    except ClientError as e:
        print(e)
        return None

def delete_file_from_s3(object_name):
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=object_name)
        return True
    except ClientError as e:
        print(e)
        return False
    
def get_signed_url(object_key):
    try:
        signed_url = s3_client.generate_presigned_url('get_object',
                                                      Params={'Bucket': BUCKET_NAME,
                                                              'Key': object_key},
                                                      ExpiresIn=3600)  # URL expires in 1 hour
        return signed_url
    except ClientError as e:
        print(e)
        return None