import os
from .scopes import scopes
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

class GCC:
    creds = None
    token_path = 'token.json'

    def __init__(self, creds_path):
        """
        Get access to a users data from authenticating thier email

        :param str token_path: path to the json file with client_id, and secret
        :param str creds_path: stores the json file with the credentials for request 
        """
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, scopes
                )
                self.creds = flow.run_local_server(port=0)

            with open(self.token_path, 'w', encoding="utf-8") as token:
                token.write(self.creds.to_json())
