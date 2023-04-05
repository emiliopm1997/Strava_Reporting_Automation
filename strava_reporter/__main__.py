import argparse
import time
from typing import Optional

import pandas as pd

from strava_reporter.activities import Activities
from strava_reporter.athletes import Athletes
from strava_reporter.config import StravaObjects, ZappierData
from strava_reporter.utils.log import LOGGER
from strava_reporter.utils.time import str_to_timestamp


def main(
    date: Optional[str] = "today",
    n_skip: Optional[int] = 0,
    test: Optional[bool] = False,
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

    LOGGER.info(
        "Processing starting at {}.".format(
            str(pd.Timestamp.now(tz="America/Mexico_City"))[:16]
        )
    )

    # Change date str to timestamp
    ts = str_to_timestamp(date)

    strava_obj = StravaObjects()

    all_activities = Activities()
    LOGGER.info("Retreiving activities...")
    all_activities.fill_club_activities(strava_obj.club, n_skip, test)
    LOGGER.info("Activities received: {}".format(len(all_activities)))

    zappier_data = ZappierData(ts)

    if zappier_data.n_activities == len(all_activities):
        LOGGER.info("Zappier and API activities match.")
    else:
        LOGGER.warning(
            "Zappier and API activities do NOT match. {}/{}".format(
                zappier_data.n_activities, len(all_activities)
            )
        )

    athletes = Athletes()
    LOGGER.info("Assigning activities to athletes...")
    athletes.assign_activities(all_activities)

    LOGGER.info("Validating athlete's activities...")
    athletes.analyze(ts, test)
    LOGGER.info("Main process completed succesfully!\n")


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
