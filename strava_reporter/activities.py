import hashlib
import json
from typing import Any, Dict, Optional

import pandas as pd
from stravalib.model import Club

from .config import Config


class Activities(list):
    """Generalized object for activities."""

    def __init__(self):
        """Set instance attributes."""
        super().__init__()
        self.__config = Config()

    def fill_club_activities(self, club: "Club", to_ignore: Optional[int] = 0):
        """
        Retrieve the activities from a club.

        Parameters
        ----------
        club : :obj:`Club`
            The club object from where the activities are registered.
        to_ignore: Optional[int]
            Number of activities to ignore, starting from the top. Mainly used
            when analysis is delayed.
        """
        self.clear()
        processed_activities = 0

        last_activities = self.__config.last_three_activities
        last_activities_new = []
        candidates_to_stop = []
        hashed_activities = 3
        ignored = 0

        # Note: result_fetcher only limits to 30 results
        for activity_raw in club.activities:

            # Skip activities
            if to_ignore > ignored:
                ignored += 1
                continue

            is_candidate = False
            activity_raw_dict = activity_raw.to_dict()
            activity_hash = self.dict_hash(activity_raw_dict)
            activity = Activity(**activity_raw_dict)

            # The first 3 activity hashes will be directly saved.
            if processed_activities < hashed_activities:
                last_activities_new.append(activity_hash)

            # Check if the activity matches the last activities hashes.
            if activity_hash == last_activities[len(candidates_to_stop)]:
                candidates_to_stop.append(activity)
                is_candidate = True

            # Actions taken if last activities are candidates of being the
            # previous last.
            if len(candidates_to_stop) == hashed_activities:
                # When the last three activities are found (as the pattern).
                break
            elif len(candidates_to_stop) > 0 and not is_candidate:
                # When the last activity candidate prove to actually not be
                # the last three.
                self += self + candidates_to_stop
                candidates_to_stop.clear()

            if not is_candidate:
                self.append(activity)
            processed_activities += 1

        self.__config.last_three_activities = last_activities_new
        self.__config.save()

    def dict_hash(self, dictionary: Dict[str, Any]) -> str:
        """MD5 hash of a dictionary."""
        dhash = hashlib.md5()
        encoded = json.dumps(dictionary, sort_keys=True).encode()
        dhash.update(encoded)
        return dhash.hexdigest()


class Activity:
    """
    Generalized object that contains an activity's information.

    Attributes
    ----------
    athlete : str
        The athlete's name as it is outputed in Strava.
    distance : float
        The distance covered in the activity.
    name : str
        The name of the activity.
    sport_type : str
        The type of sport that categorizes the activity.
    time : :obj:`pd.Timedelta`
        The time the activity took (in minutes).
    """

    athlete: str
    distance: float
    name: str
    sport_type: str
    time: pd.Timedelta

    def __init__(self, **kwargs):
        """Set instance attributes."""
        self.athlete = "{} {}".format(
            kwargs["athlete"]["firstname"], kwargs["athlete"]["lastname"]
        )
        self.name = kwargs["name"]
        self.distance = kwargs["distance"]
        self.sport_type = kwargs["type"]
        # In minutes
        self.time = pd.Timedelta(seconds=kwargs["elapsed_time"] / 60)

    def __repr__(self) -> str:
        """Representation of the object."""
        return "{} ({})".format(self.name, self.athlete)
