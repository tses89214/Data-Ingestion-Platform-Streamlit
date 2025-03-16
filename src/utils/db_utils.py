"""Database utility functions for the data ingestion platform.

This module provides functions for connecting to the database, retrieving the
expected schema for a table, validating the schema of a DataFrame, and
retrieving a list of table names.
"""
import logging
import time

import mysql.connector
import numpy as np

from src import config

# Database configuration
MYSQL_HOST = config.MYSQL_HOST
MYSQL_USER = config.MYSQL_USER
MYSQL_PASSWORD = config.MYSQL_PASSWORD
MYSQL_DATABASE = config.MYSQL_DATABASE

# Function to connect to the database with retry mechanism


def connect_to_db(max_retries=5, delay=2):
    """Connects to the database with a retry mechanism.

    Args:
        max_retries (int, optional): The maximum number of connection attempts. Defaults to 5.
        delay (int, optional): The delay between connection attempts in seconds. Defaults to 2.

    Returns:
        mysql.connector.connection.MySQLConnection: A database connection object, or None if the connection fails.
    """
    for _ in range(max_retries):
        try:
            db = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )
            logging.info("Connected to the database.")
            return db
        except mysql.connector.Error as e:
            logging.warning(
                "Database connection error: %s. Retrying in %d seconds...", e, delay)
            time.sleep(delay)
    logging.error("Failed to connect to the database after multiple retries.")
    return None


def get_expected_schema(table_name: str):
    """Retrieves the expected schema for a given table from the database.

    Args:
        table_name (str): The name of the table to retrieve the schema for.

    Returns:
        list: A list of dictionaries, where each dictionary represents a column in the schema and contains 'column_name' and 'data_type' keys.
    """
    db = connect_to_db()
    if db is None:
        return []
    cursor = db.cursor(dictionary=True)
    query = "SELECT column_name, data_type FROM expected_schema WHERE table_name = %s"
    cursor.execute(query, (table_name,))
    schema = cursor.fetchall()
    db.close()
    return schema


def validate_df_schema(data, expected_schema):
    """Validates the schema of a list of lists against an expected schema.

    Args:
        data (list): A list of lists representing the data to validate.
        expected_schema (list): A list of dictionaries, where each dictionary
                                 represents a column in the expected schema and
                                 contains 'column_name' and 'data_type' keys.

    Returns:
        tuple: (bool, str) - task_status (True if schema is valid, False otherwise)
               and task_msg (str) - "ok" if schema is valid, error message otherwise.
    """
    try:
        # Check if all expected columns are present in the data
        expected_columns = [item['column_name'] for item in expected_schema]
        if len(data[0]) != len(expected_columns):
            msg = f"Number of columns does not match expected schema. Expected: {len(expected_columns)}, Got: {len(data[0])}"
            logging.error(msg)
            return False, msg

        # Check data types of each column
        for j, expected_column in enumerate(expected_schema):
            column_name = expected_column['column_name']
            expected_type = expected_column['data_type'].lower()

            for i, row in enumerate(data):
                value = row[j]

                if expected_type == 'integer':
                    try:
                        int(value)
                    except ValueError:
                        msg = f"Column '{column_name}', Row {i+1}: Expected integer, got '{value}'."
                        logging.error(msg)
                        return False, msg
                elif expected_type == 'string':
                    if not isinstance(value, str):
                        msg = f"Column '{column_name}', Row {i+1}: Expected string, got '{value}'."
                        logging.error(msg)
                        return False, msg
                elif expected_type == 'float':
                    try:
                        float(value)
                    except ValueError:
                        msg = f"Column '{column_name}', Row {i+1}: Expected float, got '{value}'."
                        logging.error(msg)
                        return False, msg
                elif expected_type == 'datetime':
                    try:
                        np.datetime64(value)
                    except ValueError:
                        msg = f"Column '{column_name}', Row {i+1}: Expected datetime, got '{value}'."
                        logging.error(msg)
                        return False, msg
                else:
                    msg = f"Unknown data type: {expected_type}"
                    logging.warning(msg)
                    return False, msg

        logging.info("Data schema validation successful.")
        return True, "ok"

    except ValueError as e:
        msg = f"Schema validation error: {e}"
        logging.error(msg)
        return False, msg
    except TypeError as e:
        msg = f"Schema validation error: {e}"
        logging.error(msg)
        return False, msg
    except Exception as e:
        msg = f"Unexpected error during schema validation: {e}"
        logging.error(msg)
        return False, msg


def get_table_names():
    """Retrieves a list of all table names from the database.

    Returns:
        list: A list of table names.
    """
    db = connect_to_db()
    if db is None:
        return []
    cursor = db.cursor()
    query = "SELECT DISTINCT table_name FROM expected_schema"
    cursor.execute(query)
    table_names = [table[0] for table in cursor.fetchall()]
    db.close()
    return table_names
