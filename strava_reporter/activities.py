from stravalib.model import Club
import pandas as pd


class Activities(list):
    def fill_all_activities(self, club: Club, total_act: int):
        self.clear()
        counter = 0
        # result_fetcher only limits to 30 results
        for activity_raw in club.activities:
            activity = Activity(**activity_raw.to_dict())
            self.append(activity)
            counter += 1

            if counter == total_act:
                break


class Activity:
    athlete: str
    distance: float
    name: str
    sport_type: str
    time: pd.Timedelta

    # TODO: Validate activities

    def __init__(self, **kwargs):
        self.athlete = "{} {}".format(kwargs["athlete"]["firstname"],
                                      kwargs["athlete"]["lastname"])
        self.name = kwargs["name"]
        self.distance = kwargs["distance"]
        self.sport_type = kwargs["type"]
        self.time = pd.Timedelta(seconds=kwargs["elapsed_time"])

    def __repr__(self) -> str:
        return "{} ({})".format(self.name, self.athlete)
