import argparse
from strava_reporter.config import StravaObjects
from strava_reporter.activities import Activities
from strava_reporter.athletes import Athletes


def main(num_activities: int):
    """
    The main pipeline of the package.

    Parameters
    ----------
    num_activities : int
        The number of activities to be retreived.
    """
    strava_obj = StravaObjects()

    all_activities = Activities()
    all_activities.fill_club_activities(strava_obj.club)

    athletes = Athletes()
    athletes.fill_activities(all_activities)
    print(athletes.summary())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--n_records",
        help="The number of records to be retreived.",
        required=True,
        type=int,
        dest="n_records",
    )
    args = parser.parse_args()
    main(args.n_records)
