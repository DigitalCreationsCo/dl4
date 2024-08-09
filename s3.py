import boto3
from botocore.exceptions import ClientError
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()

BUCKET_NAME = os.environ.get('AWS_S3_BUCKET')
REGION = os.environ.get('AWS_REGION')
s3_client = boto3.client('s3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=REGION
)


print(f"Bucket: {BUCKET_NAME}")
print(f"Region: {REGION}")
print(f"Access Key ID: {os.environ.get('AWS_ACCESS_KEY_ID')[:5]}...")  # Print first 5 chars for security
print(f"Secret Access Key: {os.environ.get('AWS_SECRET_ACCESS_KEY')[:5]}...")

def upload_file_to_s3(file, object_name=None, ACL='private'):
    if object_name is None:
        object_name = secure_filename(file.filename)
    
    print(f"Upload file::Object Name: {object_name}")
    try:
        s3_client.put_object(Body=file, Bucket=BUCKET_NAME, Key=object_name, ACL=ACL)
    except ClientError as e:
        print(f"An error occurred: {e}")
        print(f"Error Code: {e.response['Error']['Code']}")
        print(f"Error Message: {e.response['Error']['Message']}")
        return None
    return f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{object_name}"

def get_file_from_s3(object_name):
    print(f"Get file::Object Name: {object_name}")

    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=object_name)
        return response['Body'].read()
    except ClientError as e:
        print(e)
        return None

def delete_file_from_s3(object_name):
    print(f"Delete file::Object Name: {object_name}")

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