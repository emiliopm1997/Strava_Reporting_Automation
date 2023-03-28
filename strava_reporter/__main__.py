import time

import pandas as pd

from strava_reporter.activities import Activities
from strava_reporter.athletes import Athletes
from strava_reporter.config import StravaObjects


def main():
    """The main pipeline of the package."""
    wait()

    strava_obj = StravaObjects()

    all_activities = Activities()
    all_activities.fill_club_activities(strava_obj.club)

    athletes = Athletes()
    athletes.asign_activities(all_activities)
    athletes.analyze()


def wait():
    """Wait until it is close to midnight."""
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
    main()
