
import gspread
import pandas as pd

from ..utils.path_index import GOOGLE_CONFIG
from ..utils.time import timestamp_to_unix


class ZapierHandler:
    """
    Strava data stored in Zappier.

    Attributes
    ----------
    n_activities : int
        The number of activities registered on a given day in Zappier.
    """

    def __init__(self, ts: pd.Timestamp):
        """Set instance attributes."""
        service_account = gspread.service_account(GOOGLE_CONFIG)
        ssheet = service_account.open("Stravadictos Activities")
        wsheet = ssheet.worksheet("Sheet1")

        #! If no significant diff, this will be implemented in a new func.
        start = timestamp_to_unix(ts)
        end = timestamp_to_unix(ts + pd.Timedelta(days=1))

        df_all = pd.DataFrame(wsheet.get_all_records())
        df = df_all[df_all["UNIX_UPLOAD_TIME"].between(start, end)]
        self.n_activities = df.shape[1]
