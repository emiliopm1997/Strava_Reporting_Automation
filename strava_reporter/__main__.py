import argparse
import time

import pandas as pd
from typing import Optional

from strava_reporter.activities import Activities
from strava_reporter.athletes import Athletes
from strava_reporter.config import StravaObjects


def main(
    date: Optional[str] = "today",
    n_skip: Optional[int] = 0,
    test: Optional[bool] = False
):
    """
    The main pipeline of the package.

    Parameters
    ----------
    date : Optional[str]
        The date of the analysis.
    n_skip: Optional[int]
        Number of activities to skip.
    test : Optional[bool]
        True for test runs, otherwise False.
    """

    if date == "today" and not test:
        wait()

    strava_obj = StravaObjects()

    all_activities = Activities()
    all_activities.fill_club_activities(strava_obj.club, n_skip, test)

    athletes = Athletes()
    athletes.asign_activities(all_activities)
    athletes.analyze(date, test)


def wait():
    """Wait until it is close to midnight."""
    # TODO: generate more checks
    now = pd.Timestamp.now(tz="America/Mexico_City")

    # Calculate threshold.
    date = str(now)[:10]
    t = "23:50:00.0"
    dt = "{} {}".format(date, t)
    threshold_time = pd.Timestamp(dt, tz="America/Mexico_City")

    remaining_time = threshold_time - now

    # Wait until we are close to midnight.
    if remaining_time > pd.Timedelta(minutes=0):
        sleep_time = remaining_time.seconds + 5
        time.sleep(sleep_time)

    print(
        "Processing starting at {}.".format(
            str(pd.Timestamp.now(tz="America/Mexico_City"))[:16]
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date",
        required=False,
        type=str,
        default="today",
        dest="date",
        help="The date for the analysis as yyyy-mm-dd or 'today' (default).",
    )
    parser.add_argument(
        "--n_skip",
        required=False,
        type=int,
        default=0,
        dest="n_skip",
        help="The number of activities to skip.",
    )

    # TODO: Replace by unittests.
    parser.add_argument(
        "--test",
        required=False,
        type=bool,
        default=False,
        dest="test",
        help="Whether the code is being run as a test.",
    )
    args = parser.parse_args()
    main(args.date, args.n_skip, args.test)
