#!/bin/bash

BUCKET_NAME="product-downloads-production"
REGION="us-east-2"

# Create the S3 bucket
aws s3api create-bucket \
    --bucket $BUCKET_NAME \
    --region $REGION \
    --create-bucket-configuration LocationConstraint=$REGION

# Enable versioning (optional but recommended)
aws s3api put-bucket-versioning \
    --bucket $BUCKET_NAME \
    --versioning-configuration Status=Enabled

# Enable server-side encryption (recommended)
aws s3api put-bucket-encryption \
    --bucket $BUCKET_NAME \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'

# Set a bucket policy to enforce HTTPS (recommended)
aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "EnforceHTTPS",
                "Effect": "Deny",
                "Principal": "*",
                "Action": "s3:*",
                "Resource": [
                    "arn:aws:s3:::'$BUCKET_NAME'",
                    "arn:aws:s3:::'$BUCKET_NAME'/*"
                ],
                "Condition": {
                    "Bool": {
                        "aws:SecureTransport": "false"
                    }
                }
            }
        ]
    }'

echo "S3 bucket $BUCKET_NAME has been created and configured."