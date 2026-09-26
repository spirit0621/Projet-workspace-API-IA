import os.path
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from services import secrets_manager

# TOUTES les autorisations nécessaires pour l'assistant Ultime
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/forms.responses.readonly'
]

def get_credentials():
    creds = None
    token_info = secrets_manager.load_oauth_token_dict()
    if token_info:
        try:
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            try:
                secrets_manager.save_oauth_token_dict(json.loads(creds.to_json()))
            except Exception:
                pass
        else:
            client_config = secrets_manager.load_oauth_credentials_dict()
            if client_config:
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=0)
            elif os.path.exists('credentials.json'):
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                print("Erreur: credentials.json introuvable (ni en local, ni dans Secret Manager).")
                sys.exit(1)

            try:
                secrets_manager.save_oauth_token_dict(json.loads(creds.to_json()))
            except Exception:
                pass

    return creds
