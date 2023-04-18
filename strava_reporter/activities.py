import hashlib
import json
from typing import Any, Dict, Optional

import pandas as pd
from stravalib.model import Club

from .config import Config
from .handlers.database import DBHandler


class Activities(list):
    """Generalized object for activities."""

    def __init__(self):
        """Set instance attributes."""
        super().__init__()
        self.__config = Config()

    def fill_club_activities(
        self,
        club: "Club",
        date: pd.Timestamp,
        to_ignore: Optional[int] = 0,
        test: Optional[bool] = False,
    ):
        """
        Retrieve the activities from a club.

        Parameters
        ----------
        club : :obj:`Club`
            The club object from where the activities are registered.
        date : :obj:`pd.Timestamp`
            The date of the activity.
        to_ignore: Optional[int]
            Number of activities to ignore, starting from the top. Mainly used
            when analysis is delayed.
        test : Optional[bool]
            True for test runs, otherwise False.
        """
        self.clear()
        processed_activities = 0

        # TODO: Once there is info on db we can limit this to go until a
        # TODO: hash is repeated.
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
            activity_raw_dict["date"] = str(date)[:10]
            activity_hash = self.dict_hash(activity_raw_dict)
            activity = Activity(activity_id=activity_hash, **activity_raw_dict)

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

        if not test:
            self.__config.save()

    def dict_hash(self, dictionary: Dict[str, Any]) -> str:
        """MD5 hash of a dictionary."""
        dhash = hashlib.md5()
        encoded = json.dumps(dictionary, sort_keys=True).encode()
        dhash.update(encoded)
        return dhash.hexdigest()

    def save_activities_to_db(self, db: "DBHandler", week_number):
        """Save the activities to the database.

        Parameters
        ----------
        db : :obj:`DBHandler`
            The data base handler used to save the activities.
        """

        for activity in self:
            db.add_activity(
                activity.activity_id,
                week_number,
                activity.name,
                activity.athlete,
                activity.time.total_seconds(),
                activity.date
            )


class Activity:
    """
    Generalized object that contains an activity's information.

    Attributes
    ----------
    activity_id : str
        The unique activity id.
    athlete : str
        The athlete's name as it is outputed in Strava.
    date : str
        The date of when the activity took place.
    name : str
        The name of the activity.
    time : :obj:`pd.Timedelta`
        The time the activity took.
    """

    activity_id: str
    athlete: str
    date: str
    name: str
    time: pd.Timedelta

    def __init__(self, **kwargs):
        """Set instance attributes."""
        self.activity_id = kwargs["activity_id"]
        self.athlete = "{} {}".format(
            kwargs["athlete"]["firstname"], kwargs["athlete"]["lastname"]
        )
        self.name = kwargs["name"]
        self.date = kwargs["date"]
        self.time = pd.Timedelta(seconds=kwargs["elapsed_time"])

    def __repr__(self) -> str:
        """Representation of the object."""
        return "{} ({})".format(self.name, self.time)
