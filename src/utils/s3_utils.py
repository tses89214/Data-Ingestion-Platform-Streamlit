"""
This module provides utility functions for interacting with an S3-compatible object storage service,
specifically designed for use with MinIO. It includes functions for creating an S3 client,
checking for and creating a bucket, and uploading files to the bucket.
"""
import os

import boto3

from src import config

MINIO_ENDPOINT = config.MINIO_ENDPOINT
MINIO_ACCESS_KEY = config.MINIO_ACCESS_KEY
MINIO_SECRET_KEY = config.MINIO_SECRET_KEY
S3_BUCKET_NAME = config.S3_BUCKET_NAME


def create_s3_client():
    """
    Creates and returns an S3 client.
    """
    s3 = boto3.client(
        "s3",
        endpoint_url=f"http://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )  # Use http for local MinIO
    return s3


def check_and_create_bucket(s3):
    """Checks if the S3 bucket exists. If not, attempts to create it."""
    try:
        s3.head_bucket(Bucket=S3_BUCKET_NAME)
    except Exception:
        try:
            s3.create_bucket(Bucket=S3_BUCKET_NAME)
            print("Bucket '{S3_BUCKET_NAME}' created successfully")
        except Exception:
            print("Error creating bucket")
            raise


def upload_file_to_s3(s3, file_path, object_name=None):
    """Uploads the file to the specified S3 bucket."""
    if object_name is None:
        object_name = os.path.basename(file_path)
    try:
        with open(file_path, "rb") as file_data:
            contents = file_data.read()
            s3.put_object(Bucket=S3_BUCKET_NAME,
                          Key=object_name, Body=contents)
        print(
            f"File '{file_path}' uploaded to '{S3_BUCKET_NAME}/{object_name}'")
    except Exception as e:
        print("Error uploading file:", e)
        raise
