import hashlib
import json
from typing import Any, Dict, List, Optional

import pandas as pd
from stravalib.model import Club

from .utils.time import str_to_timestamp, timestamp_to_unix
from .handlers.database import DBHandler


class Activities(list):
    """Generalized object for activities."""

    def get_weekly_activities_from_db(self, week_number: int):
        """
        Retrieve activities from a specific week in the db.

        Parameters
        ----------
        week_number : int
            The week number corresponding to the data we want to retrieve.
        """
        db = DBHandler()
        weekly_activities = db.get_weekly_activities(week_number)

        for activity in weekly_activities:
            self.append(Activity(**activity))

    def fill_club_activities(
        self,
        club: "Club",
        date: pd.Timestamp,
        last_hashes: List[str],
        stop_after: Optional[int] = None,
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
        last_hashes : List[str]
            A list of the hashes from the previous date.
        stop_after : Optional[int]
            Number of activities to read before stopping.
        to_ignore: Optional[int]
            Number of activities to ignore, starting from the top. Mainly used
            when analysis is delayed.
        test : Optional[bool]
            True for test runs, otherwise False.
        """
        self.clear()
        processed_activities = 0

        ignored = 0

        # Note: result_fetcher only limits to 30 results
        for activity_raw in club.activities:

            # Skip activities
            if to_ignore > ignored:
                ignored += 1
                continue

            activity_raw_dict = activity_raw.to_dict()
            # Get hash on yesterday's date to check whether this activity was
            # already processed.
            activity_raw_dict["date"] = str(date - pd.Timedelta(days=1))[:10]
            activity_hash = self.dict_hash(activity_raw_dict)

            if activity_hash in last_hashes:
                break
            else:
                # Correct the hash.
                activity_raw_dict["date"] = str(date)[:10]
                activity_hash = self.dict_hash(activity_raw_dict)

            activity = Activity(activity_id=activity_hash, **activity_raw_dict)
            self.append(activity)
            processed_activities += 1

            if processed_activities == stop_after:
                break

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
                str(activity.date)[:10],
                activity.date_unix
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
    date : :obj:`pd.Timestamp`
        The date of when the activity took place.
    date_unix : int
        The date in unix format.
    name : str
        The name of the activity.
    time : :obj:`pd.Timedelta`
        The time the activity took.
    """

    activity_id: str
    athlete: str
    date: pd.Timestamp
    date_unix: int
    name: str
    time: pd.Timedelta

    def __init__(self, **kwargs):
        """Set instance attributes."""
        self.activity_id = kwargs["activity_id"]

        if isinstance(kwargs["athlete"], str):
            self.athlete = kwargs["athlete"]
        else:
            self.athlete = "{} {}".format(
                kwargs["athlete"]["firstname"], kwargs["athlete"]["lastname"]
            )

        self.name = kwargs["name"]
        self.date = str_to_timestamp(kwargs["date"])
        self.date_unix = timestamp_to_unix(self.date)
        secs = (kwargs["elapsed_time"]
                if kwargs.get("elapsed_time")
                else kwargs.get("duration_secs"))
        self.time = pd.Timedelta(seconds=secs)

    def __repr__(self) -> str:
        """Representation of the object."""
        return "{} ({}, {})".format(self.name, self.athlete, self.time)
