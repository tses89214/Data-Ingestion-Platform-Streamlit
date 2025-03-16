"""Authentication utility functions for the data ingestion platform.

This module provides functions for authenticating users and handling login.
"""
import bcrypt
import streamlit as st

from src.utils.db_utils import connect_to_db


def authenticate_user(username, password):
    """Authenticates a user against the database.

    Args:
        username (str): The username to authenticate.
        password (str): The password to authenticate.

    Returns:
        bool: True if the user is authenticated, False otherwise.
    """
    db = connect_to_db()
    if db is not None:
        cursor = db.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result:
            hashed_password = result[0]
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                st.session_state.logged_in = True
                return True
            else:
                return False
        else:
            return False
        cursor.close()
        db.close()
    else:
        return False

# Function to handle login


def login(username, password):
    """Handles user login.

    Args:
        username (str): The username to login.
        password (str): The password to login.

    Returns:
        bool: True if the login is successful, False otherwise.
    """
    if authenticate_user(username, password):
        return True
    else:
        return False
