from pathlib import Path
from typing import TYPE_CHECKING, List

import pandas as pd

from .utils.log import LOGGER
from .utils.time import Week, timestamp_to_unix, unix_to_timestamp

if TYPE_CHECKING:
    from .activities import Activity
    from .athletes import Athlete

REPORT_FOLDER = Path(".").parent / "data" / "reports"


class Counter:
    """
    Counter object for athlete's weekly activities.

    Attributes
    ----------
    time_counter : Dict[int, pd.Timedelta]
        A dictionary of the total time an athlete spent performing physical
        activity. Keys represent a day of the week (in unix).
    day_counter : Dict[int, int]
        A dictionary indicating whether the activities on a given day count
        towards the challenge. Keys represent a day of the week (in unix).
    athlete_name : str
        The athlete's name.
    """

    def __init__(self, week: Week, athlete_name: str):
        """Set instance attributes."""
        week_dates = [
            timestamp_to_unix(week.week_start + pd.Timedelta(days=i))
            for i in range(7)
        ]
        self.time_counter = {x: pd.Timedelta(seconds=0) for x in week_dates}
        self.day_counter = {x: None for x in week_dates}
        self.athlete_name = athlete_name

    def add_activity(self, activity: "Activity"):
        """
        Add activity duration to counter.

        Parameters
        ----------
        activity : :obj:`Activity`
            The activity object to add.
        """
        self.time_counter[activity.date_unix] += activity.time

    def validate_activities(self):
        """Validate activities."""
        # Added 3 min tolerance.
        minimum_time = pd.Timedelta(minutes=27)
        for date, time in self.time_counter.items():
            if time >= minimum_time:
                self.day_counter[date] = 1
            elif time > pd.Timedelta(seconds=0):
                LOGGER.info(
                    "The activities of '{}' on {} are not valid.".format(
                        self.athlete_name, str(unix_to_timestamp(date))[:10]
                    )
                )


class WeeklyAnalysis:
    """
    The weekly analysis done to know the days the athletes' did activities.

    Note that even though this is a weekly analysis, this should be updated
    daily. However, the name of this analysis corresponds to the fact that the
    results are weekly based.

    Attributes
    ----------
    col_date : str
        The name of the column corresponding to the reference date.
    data : :obj:`pd.DataFrame`
        The weekly activity counts per athlete as a table.
    date : :obj:`pd.Timestamp`
        The reference date and time.
    file_path : :obj:`Path`
        The name of the file where the analysis is located. This is based on
        the week's start date and end date.
    last_monday : :obj:`pd.Timestamp`
        The date of the beginning of the week.
    """

    def __init__(self, athletes: List[str], week: Week):
        """Set instance attributes."""
        self.week = week
        file_name = "athlete_records_{}.csv".format(self.week.week_number)
        self.file_path = REPORT_FOLDER / file_name

        self.data = self._get_data_template(athletes)

    def _get_data_template(self, athletes: List[str]) -> pd.DataFrame:
        columns = []
        columns.append("ATHLETE")

        for i in range(7):
            day = self.week.week_start + pd.Timedelta(days=i)
            columns.append(day.day_name().upper())

        data = pd.DataFrame(columns=columns)
        data["ATHLETE"] = athletes
        data["TOTAL_DAYS"] = 0

        return data

    def count_athlete_activities(self, athlete: "Athlete"):
        """
        Count the daily activities of a given athlete.

        Parameters
        ----------
        athlete : Athlete
            An athlete with their data.
        """
        if not athlete.activities:
            return

        counter = Counter(self.week, athlete.name)
        for activity in athlete.activities:
            counter.add_activity(activity)
        counter.validate_activities()
        self._add_athletes_data(athlete, counter)

    def _add_athletes_data(self, athlete: "Athlete", counter: "Counter"):
        """
        Add athlete's counter to data.

        Parameters
        ----------
        athlete : "Athlete"
            The athlete's object and its data.
        counter : "Counter"
            The athlete's weekly counter.
        """
        week = {
            unix_to_timestamp(u).day_name().upper(): v
            for u, v in counter.day_counter.items()
        }
        athlete_row = self.data["ATHLETE"] == athlete.name
        for day in week.keys():
            self.data.loc[athlete_row, day] = week.get(day)
        s = self.data.loc[athlete_row, week.keys()].sum(axis=1).astype(int)
        self.data.loc[athlete_row, "TOTAL_DAYS"] = s

    def save(self):
        """Save file to csv."""
        LOGGER.info("Saving data file...")
        self.data.to_csv(self.file_path, index=False)
