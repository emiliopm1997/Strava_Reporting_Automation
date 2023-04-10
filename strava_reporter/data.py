import sqlite3
from pathlib import Path
from typing import Optional

from .config import Config


class DBHandler:
    """Apply basic SQL operations to output database.

    Attributes
    ----------

    """

    def __init__(self):
        """Set instance attributes."""
        __config = Config()
        db_path = Path(__config.paths["db"])
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

    def add_athlete(
            self,
            name: str,
            strava_name: str,
            active: Optional[bool] = True
    ):
        self.cur.execute("""
            INSERT INTO ATHLETES VALUES
                ({}, {}, {})
        """.format(name, strava_name, active))
        self.conn.commit()
