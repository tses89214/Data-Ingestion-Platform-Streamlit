"""
FastAPI backend for data ingestion platform.

This module provides the API endpoints for uploading and processing CSV files,
validating their schema, and storing them in a MinIO S3 bucket.
"""
import os
from datetime import datetime
import tempfile
import csv
from io import StringIO
import logging

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import mysql.connector
import boto3

from src.utils.db_utils import get_expected_schema, validate_df_schema
import src.utils.s3_utils as s3_utils

app = FastAPI()

# Initialize MinIO client
s3 = s3_utils.create_s3_client()

try:
    # Check if the bucket exists and create it if it doesn't
    s3_utils.check_and_create_bucket(s3)
except Exception as ex:
    logging.info("Error checking or creating bucket: %s", ex)
    raise


@app.get("/")
async def root():
    """
    Returns a simple message indicating the backend is running.

    Returns:
        dict: A dictionary containing the message.
    """
    return {"message": "FastAPI backend is running"}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...), table_name: str = Form(...)):
    """
    Uploads a CSV file, validates its schema, and stores it in MinIO.

    Args:
        file (UploadFile, optional): The CSV file to upload. Defaults to File(...).
        table_name (str, optional): The name of the table associated with the file. Defaults to Form(...).

    Returns:
        dict: A dictionary containing the filename and a success message, or an error message.
    """
    try:
        contents = await file.read()
        # Basic file validation (e.g., check file size, file type)
        # Example: Limit file size to 200MB
        if len(contents) > 200 * 1024 * 1024:
            return JSONResponse(
                content={"error": "File size too large"}, status_code=400
            )

        if file.content_type not in ["text/csv", "application/vnd.ms-excel"]:
            return JSONResponse(
                content={"error": "Invalid file type"}, status_code=400
            )

        # Read the file contents as a string
        # Read the file contents as a string
        contents_str = contents.decode('utf-8')
        csv_file = StringIO(contents_str)
        csv_reader = csv.reader(csv_file)

        # Extract column names from the first row
        next(csv_reader)

        # Read the data into a list of lists
        data = list(csv_reader)

        # Get the expected schema from the database
        expected_schema = get_expected_schema(table_name=table_name)

        # Validate the data schema
        task_status, task_msg = validate_df_schema(data, expected_schema)
        if not task_status:
            return JSONResponse(
                content={"error": task_msg},
                status_code=400,
            )

        # Generate file name
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{current_time}.csv"
        object_name = f"{table_name}/{file_name}"

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(contents)
            temp_file_path = temp_file.name

        # Upload the file to MinIO
        try:
            s3_utils.upload_file_to_s3(s3, temp_file_path, object_name)
            msg = f"File '{file_name}' uploaded to '{s3_utils.S3_BUCKET_NAME}/{table_name}' successfully"
            logging.info(msg)
        except boto3.exceptions.S3UploadFailedError as s3ufe:
            logging.info("Error uploading file: %s", s3ufe)
            return JSONResponse(
                content={"error": f"Error uploading file to S3: {str(s3ufe)}"},
                status_code=500,
            )
        finally:
            # Delete the temporary file
            os.remove(temp_file_path)

        return {
            "filename": file.filename,
            "message": "File uploaded successfully",
        }
    except FileNotFoundError as fnfe:
        return JSONResponse(content={"error": f"File not found: {str(fnfe)}"}, status_code=400)
    except csv.Error as csve:
        return JSONResponse(content={"error": f"CSV error: {str(csve)}"}, status_code=400)
    except mysql.connector.Error as sqle:
        return JSONResponse(content={"error": f"Database error: {str(sqle)}"}, status_code=500)
    except boto3.exceptions.S3UploadFailedError as s3ufe:
        return JSONResponse(content={"error": f"S3 upload error: {str(s3ufe)}"}, status_code=500)
