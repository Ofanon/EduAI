import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
import requests
import json

client_secret_file = 'client_secrets.json'

scope = ['https://www.googleapis.com/auth/userinfo.profile']

def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('tocken.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, scope)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    st.write("Réussi")
    return creds
    

            