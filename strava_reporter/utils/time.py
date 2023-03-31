import pandas as pd


def unix_to_timestamp(ut: int) -> pd.Timestamp:
    """
    Convert Unix time to Timestamp.

    Parameters
    ----------
    ut : int
        A unix time variable.

    Returns
    -------
    :obj:`pd.Timestamp`
        The unix time transformed into a Mexico City timestamp.
    """
    ts = pd.to_datetime(ut, unit='s') \
        .tz_localize('UTC') \
        .tz_convert(tz="America/Mexico_City")
    return ts


def timestamp_to_unix(ts: pd.Timestamp) -> int:
    """
    Convert Timestamp to Unix time.

    Parameters
    ----------
    ts : :obj:`pd.Timestamp`
        A local timestamp.

    Returns
    -------
    ut : int
        A unix time variable.
    """
    return int(ts.timestamp())


def timestamp_to_compressed_str(ts: pd.Timestamp) -> str:
    """
    Convert Timestamp to a compressed date string.

    Parameters
    ----------
    ts : :obj:`pd.Timestamp`
        A local timestamp.

    Returns
    -------
    mod_date_str : str
        A string with the date as 'ddmmyyyy'.
    """
    date_str = str(ts)[:10]
    # Remove "-" and flip list
    date_lst = date_str.split("-")[::-1]
    mod_date_str = "".join(date_lst)

    return mod_date_str
