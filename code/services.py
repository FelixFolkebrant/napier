import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def get_service(scopes):
    creds = None
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
    creds = flow.run_local_server(port=8080)
    gmail_service = build("gmail", "v1", credentials=creds)
    docs_service = build("docs", "v1", credentials=creds)
    return {"gmail": gmail_service, "docs": docs_service}
