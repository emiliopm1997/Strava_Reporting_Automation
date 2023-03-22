import json
import pandas as pd
from pathlib import Path

from activities import Activities

ATHLETES_JSON = Path(".").parent / "config" / "athletes.json"


class Athlete:
    def __init__(self, name: str, strava_name: str):
        self.name = name
        self.strava_name = strava_name
        self.activities = Activities()

    @property
    def activity_count(self):
        return len(self.activities)

    def __repr__(self) -> str:
        return "{} ({})".format(self.name, self.activity_count)


class Athletes:
    """Generalized object for athletes"""
    athlete_names: list = []

    def __init__(self):
        with open(ATHLETES_JSON, "r") as f:
            athletes_raw = json.load(f)

        for athlete in athletes_raw:
            setattr(self, athlete["strava_name"], Athlete(**athlete))
            self.athlete_names.append(athlete["strava_name"])

    def get_athlete(self, attr: str) -> Athlete:
        if attr not in self.athlete_names:
            raise AttributeError("Athlete '{}' was not found.".format(attr))
        return getattr(self, attr)

    def fill_activities(self, activities: Activities):
        for activity in activities:
            athlete = self.get_athlete(activity.athlete)
            athlete.activities.append(activity)

    def summary(self) -> pd.DataFrame:
        cols = ["athlete", "activities"]
        summary_df = pd.DataFrame(columns=cols)
        for athlete_name in self.athlete_names:
            athlete = self.get_athlete(athlete_name)
            row = pd.DataFrame([[athlete.name, athlete.activity_count]],
                               columns=cols)
            summary_df = pd.concat([summary_df, row], ignore_index=True)

        return summary_df
