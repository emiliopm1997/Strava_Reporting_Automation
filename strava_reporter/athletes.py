from pathlib import Path
from typing import List

import pandas as pd

from .activities import Activities
from .analysis import WeeklyAnalysis
from .handlers.database import DBHandler
from .utils.log import LOGGER
from .utils.time import Week

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
    """

    def __init__(self, name: str, strava_name: str):
        """Set instance attributes."""
        self.name = name
        self.strava_name = strava_name
        self.activities = Activities()

    def __repr__(self) -> str:
        """Representation of the object."""
        return "{} ({})".format(self.name, self.activities)


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
        self._db = DBHandler()
        athletes_raw = self._db.get_active_athletes()

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
            LOGGER.info("Athlete '{}' was not found.".format(attr))
            return None
        return getattr(self, attr)

    def assign_activities(self, activities: "Activities"):
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

    def analyze(self, week_number: int):
        """
        Analyze the daily activities and save the data on a csv.

        week_number : int
            The week number of the analysis
        """
        week_data = Week(**self._db.get_week_information(week_number))
        analysis = WeeklyAnalysis(self.athlete_names, week_data)

        # Update table based on the athletes activity.
        for athlete_name in self.athlete_strava_names:
            athlete = self.get_athlete(athlete_name)
            analysis.count_athlete_activities(athlete)

        analysis.save()
