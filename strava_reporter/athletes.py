import json
from pathlib import Path
from typing import List

import pandas as pd

from .activities import Activities
from .analysis import WeeklyAnalysis

ATHLETES_JSON = Path(".").parent / "config" / "athletes.json"


class Athlete:
    """
    Generalized object that contains the athlete's information.

    Attributes
    ----------
    name : str
        The athlete's complete name.
    strava_name: str
        The athlete's name as it is outputed in Strava.
    activities: :obj:`Activities`
        The activities that the athlete has completed.
    total_time: :obj:`pd.Timedelta`
        Total activity time that the athlete has completed.
    """

    def __init__(self, name: str, strava_name: str):
        """Set instance attributes."""
        self.name = name
        self.strava_name = strava_name
        self.activities = Activities()

    @property
    def total_time(self):
        total_time = pd.Timedelta(minutes=0)
        for activity in self.activities:
            total_time += activity.time
        return total_time

    def __repr__(self) -> str:
        """Representation of the object."""
        return "{} ({})".format(self.name, self.activity_count)


class Athletes:
    """
    Generalized object for athletes.

    Attributes
    ----------
    athlete_names : List[str]
        The registered athletes in the challenge.
    athlete_strava_names : List[str]
        The registered athletes in the challenge as they appear in Strava.
    """

    athlete_names: List[str] = []
    athlete_strava_names: List[str] = []

    def __init__(self):
        """Set instance attributes."""
        with open(ATHLETES_JSON, "r") as f:
            athletes_raw = json.load(f)

        for athlete in athletes_raw:
            setattr(self, athlete["strava_name"], Athlete(**athlete))
            self.athlete_names.append(athlete["name"])
            self.athlete_strava_names.append(athlete["strava_name"])

    def get_athlete(self, attr: str) -> "Athlete":
        """
        Get a specific registered athlete.

        Parameters
        ----------
        attr : str
            The name of the athlete that wants to be retreived.

        Returns
        -------
        :obj:`Athlete`
            The athlete in question.
        """
        if attr not in self.athlete_strava_names:
            print("Athlete '{}' was not found.".format(attr))
            return None
        return getattr(self, attr)

    def asign_activities(self, activities: "Activities"):
        """
        Asign the activities to its corresponding athlete.

        Parameters
        ----------
        activities : :obj:`Activities`
            The activities to be assigned.
        """
        for activity in activities:
            athlete = self.get_athlete(activity.athlete)

            # To only assign activities of active athletes.
            if athlete:
                athlete.activities.append(activity)

    def analyze(self):
        """Analyze the daily activities and save the data on a csv."""
        # Added 3 min tolerance.
        minimum_time = pd.Timedelta(minutes=27)

        analysis = WeeklyAnalysis(self.athlete_names)

        # Update table based on the athletes activity.
        for athlete_name in self.athlete_strava_names:
            athlete = self.get_athlete(athlete_name)

            # Validate that the total activity is greater than the min time.
            if athlete.total_time >= minimum_time:
                analysis.count_athlete_activity(athlete=athlete.name)

        analysis.update_total_counts()
        analysis.save()
