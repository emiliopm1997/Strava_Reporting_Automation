import json
import os
from copy import deepcopy
from pathlib import Path
from typing import Set

import pandas as pd
from dotenv import load_dotenv
from stravalib.client import Client
from stravalib.exc import AccessUnauthorized

from .log import LOGGER

CONFIG_JSON = Path(".").parent / "config" / "config.json"
CONFIG_JSON_OLD = Path(".").parent / "config" / "old_config.json"


class Config:
    def __init__(self):
        """Set instance attributes."""
        with open(CONFIG_JSON, "r") as f:
            self.__conf_old = json.load(f)

        for k, v in self.__conf_old.items():
            setattr(self, k, v)

    def save(self):
        """Save the updated config."""
        self.last_updated = str(pd.Timestamp.now(tz="America/Mexico_City"))

        LOGGER.info("Saving old config...")
        with open(CONFIG_JSON_OLD, "w") as outfile:
            json.dump(self.__conf_old, outfile)

        config_new = deepcopy(self.__dict__)
        config_new.pop("_Config__conf_old")
        LOGGER.info("Saving new config...")
        with open(CONFIG_JSON, "w") as outfile:
            json.dump(config_new, outfile)


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
            LOGGER.info("Access granted with Access Token.")
        except (AccessUnauthorized, ValueError):
            self.client = Client()
            print("Access required through Code.")
            self._request_token()
            self.club = self.client.get_club(self.__config.club_id)
            LOGGER.info("Access granted with Code.")

    def get_athletes_in_club(self) -> Set[str]:
        """
        Retrieve the athletes that are members of the club.

        Returns
        -------
        Set[str]
            The athletes names.
        """
        counter = 0
        threshold = 250

        members = set()

        # Iterate over activities and extract club members.
        for activity in self.club.activities:
            counter += 1
            act_dict = activity.to_dict()
            name = "{} {}".format(
                act_dict["athlete"]["firstname"],
                act_dict["athlete"]["lastname"],
            )
            members.add(name)
            if counter == threshold:
                break

        return members

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
