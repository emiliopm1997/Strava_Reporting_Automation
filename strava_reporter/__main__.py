import argparse
import time
from typing import Optional

import pandas as pd

from strava_reporter.activities import Activities
from strava_reporter.athletes import Athletes
from strava_reporter.handlers.database import DBHandler
from strava_reporter.handlers.strava import StravaObjects
from strava_reporter.utils.log import LOGGER
from strava_reporter.utils.time import str_to_timestamp


def main(
    date: Optional[str] = "today",
    stop_after: Optional[int] = None,
    n_skip: Optional[int] = 0,
    test: Optional[bool] = False,
):
    """
    Run the main pipeline of the package.

    Parameters
    ----------
    date : Optional[str]
        The date of the analysis.
    stop_after : Optional[str]
        Number of activities to record.
    n_skip: Optional[int]
        Number of activities to skip.
    test : Optional[bool]
        True for test runs, otherwise False.
    """
    if date == "today" and not test:
        wait()

    LOGGER.info(
        "Processing starting at {}.".format(
            str(pd.Timestamp.now(tz="America/Mexico_City"))[:16]
        )
    )

    # Change date str to timestamp
    ts = str_to_timestamp(date)

    strava_obj = StravaObjects()
    db = DBHandler()
    week_number = db.get_week_number(ts)
    last_hashes = db.get_last_hashes(ts)

    all_activities = Activities()
    LOGGER.info("Retreiving activities...")
    all_activities.fill_club_activities(
        strava_obj.club,
        ts,
        last_hashes,
        stop_after,
        n_skip,
        test
    )

    LOGGER.info("Activities received: {}".format(len(all_activities)))
    LOGGER.info(all_activities)
    if not test:
        all_activities.save_activities_to_db(db, week_number)
        LOGGER.info("Activities saved to db...")

    LOGGER.info("Main process completed succesfully!\n")


def analyze(week_number: int):
    """
    Perform a weekly analysis with activities data.

    Parameters
    ----------
    week_number : int
        The week of interest to perform the analysis.
    """
    LOGGER.info("Analysis starting...")
    weekly_activities = Activities()
    LOGGER.info(f"Retreiving activities from week {week_number}...")
    weekly_activities.get_weekly_activities_from_db(week_number)

    athletes = Athletes()
    LOGGER.info("Assigning activities to athletes...")
    athletes.assign_activities(weekly_activities)

    LOGGER.info("Validating athlete's activities...")
    athletes.analyze(week_number)
    LOGGER.info("Analysis performed correctly!")


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--analysis",
        required=False,
        type=int,
        default=None,
        dest="analysis",
        help="The week number of the analysis to be conducted.",
    )
    parser.add_argument(
        "--date",
        required=False,
        type=str,
        default="today",
        dest="date",
        help="The date for the analysis as yyyy-mm-dd or 'today' (default).",
    )
    parser.add_argument(
        "--stop_after",
        required=False,
        type=int,
        default=None,
        dest="stop_after",
        help="The number of activities to record.",
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
        "-t",
        "--test",
        action='store_true',
        dest="test",
        help="Whether the code is being run as a test.",
    )
    args = parser.parse_args()

    if args.analysis:
        analyze(args.analysis)
    else:
        main(args.date, args.stop_after, args.n_skip, args.test)
