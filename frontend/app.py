"""
Frontend application for the data ingestion platform.

This module provides a Streamlit interface for uploading CSV files,
displaying data previews, and showing the expected schema.
"""
import io

import streamlit as st
import pandas as pd
import requests

from src.utils.auth_utils import login
from src.utils.db_utils import get_expected_schema, get_table_names


# Check if user is logged in
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login")
    login_username = st.text_input("Username")
    login_password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(login_username, login_password):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password")

else:
    st.title("CSV File Uploader")
    table_names = get_table_names()
    table_name = st.selectbox("Select a table", table_names)

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        file_name = uploaded_file.name
        file_content = uploaded_file.read()
        url = "http://backend:8500/uploadfile/"
        files = {"file": (file_name,
                          file_content, 'text/csv')}
        data = {"table_name": table_name}
        response = requests.post(url, files=files, data=data, timeout=10)

        if response.status_code == 200:
            st.success("File uploaded successfully!")
            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(io.BytesIO(file_content), nrows=5)

            # Display the DataFrame
            st.subheader("Data Preview")
            st.dataframe(df, use_container_width=True)
        else:
            st.error(
                f"Error uploading file: {response.status_code} - {response.text}")
    else:
        # Define the expected schema
        expected_schema = get_expected_schema(table_name)
        schema = pd.DataFrame(expected_schema)

        st.subheader("Expected Schema")
        st.dataframe(schema, use_container_width=True)
