from pathlib import Path
from typing import List, Optional

import pandas as pd

REPORT_FOLDER = Path(".").parent / "reports"


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

    def __init__(self, athletes: List[str], date: Optional[str] = "today"):
        """Set instance attributes."""

        self.date = (
            pd.Timestamp.now(tz="America/Mexico_City") 
            if date == "today"
            else pd.Timestamp(date, tz="America/Mexico_City")
            )
        self.last_monday = self.date - pd.Timedelta(
            days=self.date.day_of_week
        )
        self.file_path = REPORT_FOLDER / self._get_file_name()
        self.col_date = self._get_column_name(self.date)

        if self.file_path.exists():
            self.data = pd.read_csv(self.file_path)
        else:
            self.data = self._get_data_template(athletes)

    def _get_file_name(self) -> str:
        next_sunday = self.last_monday + pd.Timedelta(days=6)

        data_name = "athlete_records_{}_{}.csv".format(
            self._custom_date_to_str(self.last_monday),
            self._custom_date_to_str(next_sunday),
        )
        return data_name

    def _custom_date_to_str(self, date: pd.Timestamp) -> str:
        date_str = str(date)[:10]
        # Remove "-" and flip list
        date_lst = date_str.split("-")[::-1]
        mod_date_str = "".join(date_lst)

        return mod_date_str

    def _get_data_template(self, athletes: List[str]) -> pd.DataFrame:
        columns = []
        columns.append("ATHLETE")
        for i in range(7):
            day = self.last_monday + pd.Timedelta(days=i)
            columns.append(self._get_column_name(day))

        data = pd.DataFrame(columns=columns)
        data["ATHLETE"] = athletes
        data["TOTAL_DAYS"] = 0

        return data

    def _get_column_name(self, day: pd.Timestamp) -> str:
        day_name = day.day_name().upper()[:3]
        col_name = "{}_{}".format(day_name, self._custom_date_to_str(day)[:4])
        return col_name

    def count_athlete_activity(self, athlete: str):
        """
        Count the daily activities of a given athlete.

        Parameters
        ----------
        athlete : str
            The name of the athlete that completed the daily activity.
        """

        self.data.loc[self.data["ATHLETE"] == athlete, self.col_date] = 1

    def update_total_counts(self):
        """Update the total counts of every athlete."""
        cols_to_sum = [
            col
            for col in self.data.columns
            if col not in ["ATHLETE", "TOTAL_DAYS"]
        ]

        self.data["TOTAL_DAYS"] = self.data[cols_to_sum].sum(axis=1)

    def save(self):
        """Save file to csv."""
        self.data.to_csv(self.file_path, index=False)
