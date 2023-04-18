import shutil
import sqlite3
import pandas as pd
from copy import deepcopy
from pathlib import Path
from typing import List, Optional

from ..config import Config
from ..utils.log import LOGGER
from ..utils.time import timestamp_to_unix, str_to_timestamp


class _AthletesTable:
    """Private object used to modify items in the ATHLETES table."""

    __table = "ATHLETES"

    def add_athlete(
            self,
            name: str,
            strava_name: str,
            active: Optional[bool] = True,
            weeks_completed: Optional[int] = 0
    ):
        """
        Add an athlete to the database.

        Parameters
        ----------
        name : str
            The athlete full name.
        strava_name : str
            The athlete name as it appears in Strava. See get_athletes_in_club
            method inside the StravaObjects class.
        active : Optional[bool]
            True if the athlete is participating in the current challenge.
            Otherwise, False. The default is True.
        weeks_completed : Optional[int]
            The number of weeks that the athlete has completed the challenge.
            The default is 0.
        """
        values = f"('{name}', '{strava_name}', {active}, {weeks_completed})"
        self._insert(self.__table, values)

    def drop_athlete_by_strava_name(
            self,
            strava_name: str
    ):
        """
        Drop athlete by Strava name.

        Parameters
        ----------
        strava_name : str
            The athlete name as it appears in Strava. See get_athletes_in_club
            method inside the StravaObjects class.
        """
        condition = f"strava_name = '{strava_name}'"
        self._delete(self.__table, condition)

    def update_weeks_completed_in_athlete(
            self,
            strava_name: str,
            new_weeks: int
    ):
        """
        Update the number of weeks completed by an athlete.

        Parameters
        ----------
        strava_name : str
            The athlete name as it appears in Strava. See get_athletes_in_club
            method inside the StravaObjects class.
        new_weeks : int
            The number of weeks that the athlete has completed.
        """
        changes = f"weeks_completed = {new_weeks}"
        condition = f"strava_name = '{strava_name}'"
        self._update(self.__table, changes, condition)


class _WeeksTable:
    """Private object used to modify items in the WEEKS table."""

    __table = "WEEKS"

    def fill_weeks(self, start_date: str, end_date: str):
        """
        Fill the weeks data in the data base based on the start and end date.

        Parameters
        ----------
        start_date : str
            The start date as 'YYYY-MM-DD'.
        end_date : str
            The end date as 'YYYY-MM-DD'.
        """
        # Transform into timestamp.
        start_date = str_to_timestamp(start_date)
        end_date = str_to_timestamp(end_date)

        self._validate_weeks_dates(start_date, end_date)

        # Fill the WEEKS table with the corresponding dates.
        monday = start_date
        week_n = 1

        while monday < end_date:
            sunday = monday + pd.Timedelta(days=6)

            # The second unix is given the fact that we would like to account
            # for Sunday.
            values = "({}, '{}', '{}', {}, {})".format(
                week_n,
                str(monday)[:10],
                str(sunday)[:10],
                timestamp_to_unix(monday),
                timestamp_to_unix(monday + pd.Timedelta(days=7)),
            )
            self._insert(self.__table, values)
            monday += pd.Timedelta(days=7)
            week_n += 1

    def _validate_weeks_dates(self, start_date: str, end_date: str):
        msg = ""
        if start_date.day_name() != "Monday":
            msg = "Start date is not Monday."
        elif end_date.day_name() != "Sunday":
            msg = "End date is not Sunday."

        if msg:
            LOGGER.error(msg)
            raise ValueError(msg)

    def get_week_number(self, ts: pd.Timestamp) -> int:
        """
        Retreive the corresponding week number based on a date.

        Parameters
        ----------
        ts : :obj:`pd.Timestamp`
            A local timestamp.

        Returns
        -------
        int
            The week number.
        """
        unix_ts = timestamp_to_unix(ts)
        col = "week_number"
        additionals = ("WHERE {} BETWEEN week_start_unix "
                       "AND week_end_unix".format(unix_ts))
        res = self._select(col, self.__table, additionals)
        return res[0][0]


class _ActivitiesTable:
    """Private object used to modify items in the ACTIVITIES table."""

    __table = "ACTIVITIES"

    def add_activity(
            self,
            activity_id: str,
            week_number: int,
            name: str,
            athlete: str,
            duration_secs: int,
            date: str
    ):
        """
        Add an activity to the database.

        Parameters
        ----------
        activity_id : str
            The activity's hash.
        week_number : int
            The week number corresponding to this activity.
        name :  str
            The activity name.
        athlete : str
            The athlete name as it appears in Strava. See get_athletes_in_club
            method inside the StravaObjects class.
        duration_secs : int
            The number of seconds that this activity lasted.
        date : int
            The date corresponding to this activity expressed as 'YYYY-MM-DD'.
        """
        values = "('{}', {}, '{}', '{}', {}, '{}')".format(
            activity_id,
            week_number,
            name,
            athlete,
            duration_secs,
            date
        )
        self._insert(self.__table, values)


class DBHandler(_ActivitiesTable, _AthletesTable, _WeeksTable):
    """
    Data base handler for athletes, activities, weeks, and debts.

    Attributes
    ----------
    conn : :obj:`sqlite3.dbapi2.Connection`
        A 'Connection' object pointing to the data base.
    cur : :obj:`sqlite3.dbapi2.Cursor`
        A 'Cursor' object based on the previous connection.
    """

    def __init__(self, set_template: Optional[bool] = False):
        """Set instance attributes."""
        __config = Config()
        db_path = Path(".").parent / deepcopy(__config.paths["db"])
        db_template_path = (
            Path(".").parent / deepcopy(__config.paths["db_template"])
        )

        if not set_template:
            self._validate_db(db_path, db_template_path)
            self.conn = sqlite3.connect(db_path)
        else:
            self.conn = sqlite3.connect(db_template_path)
        self.cur = self.conn.cursor()

    def _validate_db(self, db_path: Path, db_template_path: Path):

        # Check if db exists, if not copy from template.
        if not db_path.exists() and not db_template_path.exists():
            msg = "Neither database nor template found in data folder."
            LOGGER.error(msg)
            raise FileNotFoundError(msg)
        elif not db_path.exists():
            LOGGER.info("Copying database from template...")
            shutil.copy(db_template_path, db_path)

    def _insert(self, table: str, values: str):
        sql = f"INSERT INTO {table} VALUES {values}"
        print(sql)
        self.cur.execute(sql)
        self.conn.commit()

    def _update(self, table: str, changes: str, condition: str):
        sql = f"UPDATE {table} SET {changes} WHERE {condition}"
        print(sql)
        self.cur.execute(sql)
        self.conn.commit()

    def _delete(self, table: str, conditions: str):
        sql = f"DELETE FROM {table} WHERE {conditions}"
        print(sql)
        self.cur.execute(sql)
        self.conn.commit()

    def _select(self, what: str, table: str, additionals: str) -> List:
        sql = f"SELECT {what} FROM {table} {additionals}"
        print(sql)
        result = self.cur.execute(sql).fetchall()
        return result
