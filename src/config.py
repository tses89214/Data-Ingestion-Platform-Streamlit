import os

# Database configuration
MYSQL_HOST = os.environ.get("MYSQL_HOST", "db")
MYSQL_USER = os.environ.get("MYSQL_USER", "readonly")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "readonly")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "data_ingestion")

# S3 configuration
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "storage:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "csv-file-uploader")
