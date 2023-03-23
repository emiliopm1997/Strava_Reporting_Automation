import json
from pathlib import Path
from typing import List

import pandas as pd
from activities import Activities

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
        The activities that the athlete has completed
    """

    def __init__(self, name: str, strava_name: str):
        """Set instance attributes."""
        self.name = name
        self.strava_name = strava_name
        self.activities = Activities()

    @property
    def activity_count(self):
        return len(self.activities)

    def __repr__(self) -> str:
        """Representation of the object."""
        return "{} ({})".format(self.name, self.activity_count)

    # TODO: Validate activities (maybe in Activities)
    # 1) The sum of the activity time in a day is greater than 30 min
    # 2) The activity must have a picture or evidence of come sort (this
    # is probably not going to happen)


class Athletes:
    """
    Generalized object for athletes.

    Attributes
    ----------
    athlete_names : List[str]
        The registered athletes in the challenge.
    """

    athlete_names: List[str] = []

    def __init__(self):
        with open(ATHLETES_JSON, "r") as f:
            athletes_raw = json.load(f)

        for athlete in athletes_raw:
            setattr(self, athlete["strava_name"], Athlete(**athlete))
            self.athlete_names.append(athlete["strava_name"])

    def get_athlete(self, attr: str) -> "Athlete":
        """
        Get a specific registered athlete.

        Parameters
        ----------
        attr : str
            The name of the athlete that wants to be retreived.

        Returns
        -------
        :obj:`Activities`
            The athlete in question.

        Raises
        ------
        AttributeError
            If the athlete is not registered.
        """
        if attr not in self.athlete_names:
            raise AttributeError("Athlete '{}' was not found.".format(attr))
        return getattr(self, attr)

    def fill_activities(self, activities: "Activities"):
        """
        Asign the activities to its corresponding athlete.

        Parameters
        ----------
        activities : :obj:`Activities`
            The activities to be assigned.
        """
        for activity in activities:
            athlete = self.get_athlete(activity.athlete)
            athlete.activities.append(activity)

    def summary(self) -> pd.DataFrame:
        """Count the number of activities per athlete.

        Returns
        -------
        :obj:`pd.DataFrame`
            A table with the count of every athlete's activities.
        """
        cols = ["athlete", "activities"]
        summary_df = pd.DataFrame(columns=cols)
        for athlete_name in self.athlete_names:
            athlete = self.get_athlete(athlete_name)
            row = pd.DataFrame(
                [[athlete.name, athlete.activity_count]], columns=cols
            )
            summary_df = pd.concat([summary_df, row], ignore_index=True)

        return summary_df
