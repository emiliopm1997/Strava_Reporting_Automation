import pandas as pd
from stravalib.model import Club


class Activities(list):
    """Generalized object for activities."""

    def fill_all_activities(self, club: "Club", total_act: int):
        """
        Retrieve the activities from a club.

        Parameters
        ----------
        club : :obj:`Club`
            The club object from where the activities are registered.
        total_act : int
            The number of activities to be retreived.
        """
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
        The time the activity took.
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
        self.time = pd.Timedelta(seconds=kwargs["elapsed_time"])

    def __repr__(self) -> str:
        """Representation of the object."""
        return "{} ({})".format(self.name, self.athlete)
