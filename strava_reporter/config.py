import json
import os
import pandas as pd
from pathlib import Path

from dotenv import load_dotenv
from stravalib.client import Client
from stravalib.exc import AccessUnauthorized

CONFIG_JSON = Path(".").parent / "config" / "config.json"
CONFIG_JSON_TEST = Path(".").parent / "config" / "config2.json"


class Config:
    def __init__(self):
        """Set instance attributes."""
        with open(CONFIG_JSON, "r") as f:
            config = json.load(f)

        for k, v in config.items():
            setattr(self, k, v)

    def save(self):
        """Save the updated config."""
        self.last_updated = str(pd.Timestamp.now())[:10]

        with open(CONFIG_JSON_TEST, 'w') as outfile:
            json.dump(self.__dict__, outfile)


class StravaObjects:
    """Access Strava with account and retrieve the club object."""

    def __init__(self):
        """Set instance attributes."""
        self._load_environment_variables()
        self._read_environment_variables()
        self.__config = Config()

        try:
            if not self.__access_token:
                raise ValueError
            self.client = Client(self.__access_token)
            self.club = self.client.get_club(self.__config.club_id)
            print("Access granted with Access Token.")
        except (AccessUnauthorized, ValueError):
            self.client = Client()
            print("Access required through Code.")
            self._request_token()
            self.club = self.client.get_club(self.__config.club_id)
            print("Access granted with Code.")

    def _load_environment_variables(self):
        load_dotenv(Path(".").parent / ".env")

    def _read_environment_variables(self):
        self.__client_id = int(os.environ.get("CLIENT_ID"))
        self.__client_secret = os.environ.get("CLIENT_SECRET")
        self.__access_token = os.environ.get("ACCESS_TOKEN")

    def _request_token(self):
        authorize_url = self.client.authorization_url(
            client_id=self.__client_id,
            redirect_uri="http://127.0.0.1:5000/authorization",
            scope=self.__config.scope,
        )
        print(authorize_url)
        code = input("Insert code: ")

        token_response = self.client.exchange_code_for_token(
            client_id=self.__client_id,
            client_secret=self.__client_secret,
            code=code,
        )
        self.client.access_token = token_response["access_token"]
        self.client.refresh_token = token_response["refresh_token"]
        self.client.expires_at = token_response["expires_at"]
