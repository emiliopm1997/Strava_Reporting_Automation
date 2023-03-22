from access import StravaObjects
from activities import Activities
from athletes import Athletes


def main(num_activities: int):
    strava_obj = StravaObjects()

    all_activities = Activities()
    all_activities.fill_all_activities(
        strava_obj.club,
        num_activities
    )

    athletes = Athletes()
    athletes.fill_activities(all_activities)
    print(athletes.summary())


if __name__ == "__main__":
    main(15)
