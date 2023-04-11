import sqlite3
from pathlib import Path
from typing import Optional

from strava_reporter.config import Config


class DBHandler:
    """Apply basic SQL operations to output database.

    Attributes
    ----------

    """

    def __init__(self):
        """Set instance attributes."""
        __config = Config()
        db_path = Path(".").parent / __config.paths["db"]
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

    def add_athlete(
            self,
            name: str,
            strava_name: str,
            active: Optional[bool] = True
    ):
        table = "ATHLETES"
        values = f"('{name}', '{strava_name}', {active})"
        self._insert(table, values)

    def drop_athlete_by_strava_name(
            self,
            strava_name: str
    ):
        table = "ATHLETES"
        condition = f"strava_name = '{strava_name}'"
        self._delete(table, condition)

    def _insert(self, table: str, values: str):
        sql = f"INSERT INTO {table} VALUES {values}"
        print(sql)
        self.cur.execute(sql)
        self.conn.commit()

    def _delete(self, table: str, conditions: str):
        sql = f"DELETE FROM {table} WHERE {conditions}"
        print(sql)
        self.cur.execute(sql)
        self.conn.commit()
