
import streamlit as st
import requests
import io
import os
import json
from pypdf import PdfReader
st.title("Session-based PDF Search")

# Inputs
session_id = st.text_input("Session ID", value="user_123")
user_query = st.text_input("Ask a question about the file:")
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if st.button("Search"):
    if uploaded_file and user_query:
        # Prepare file and form data
 
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        payload = {
            "user_query": user_query,
            "session_id": session_id
        }
        
        with st.spinner("Searching..."):

                file_name = 'config.json'
                if os.path.exists(file_name):
                    with open(file_name, 'r') as file:
                        config = json.load(file)
                        os.environ['BACKEND_API_URL'] = config.get("BACKEND_API_URL") # Loading the API Key

# Read the variable, or fall back to localhost if it is missing
                backend_base = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")
                print(f"BACKEND_API_URL: {backend_base}")
# Clean up any missing or extra trailing slashes to prevent "https://onrender.com"
                backend_base = backend_base.rstrip("/")
                full_url = f"{backend_base}/uploadfile/"

# Make the request safely
                response = requests.post(full_url, files=files, data=payload)
                print(f"BACKEND_API_URL: {full_url}")
                if response.status_code == 200:
                    answer = response.json().get("response")
                    st.write("### Agent Response:")
                    st.info(answer)
                else:
                    st.error("API Error" + str(response.status_code) + ": " + response.text)

    else:
        st.warning("Please provide both a file and a query.")