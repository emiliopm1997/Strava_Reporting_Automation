import os
from dotenv import load_dotenv
from pathlib import Path
from stravalib.client import Client

SCOPE = ['read_all', 'profile:read_all', 'activity:read_all']
CLUB_ID = 1099692


class StravaObjects:
    """Access Strava with account and retrieve the club object."""

    def __init__(self):
        self._load_environment_variables()
        self._read_environment_variables()

        if self.__access_token:
            self.client = Client(self.__access_token)
        else:
            self.client = Client()
            self._request_token()

        self.club = self.client.get_club(CLUB_ID)

    def _load_environment_variables(self):
        load_dotenv(Path(".").parent / ".env")

    def _read_environment_variables(self):
        self.__client_id = int(os.environ.get('CLIENT_ID'))
        self.__client_secret = os.environ.get('CLIENT_SECRET')
        self.__access_token = os.environ.get('ACCESS_TOKEN')

    def _request_token(self):
        authorize_url = self.client.authorization_url(
            client_id=self.__client_id,
            redirect_uri='http://127.0.0.1:5000/authorization',
            scope=SCOPE
        )
        print(authorize_url)
        code = input("Insert code: ")

        token_response = self.client.exchange_code_for_token(
            client_id=self.__client_id,
            client_secret=self.__client_secret,
            code=code
        )
        self.client.access_token = token_response['access_token']
        self.client.refresh_token = token_response['refresh_token']
        self.client.expires_at = token_response['expires_at']
