"""Utilities module."""
import re
from datetime import datetime

import numpy as np
import pandas as pd


def standardize_date(date_str: str) -> str:
    """Standardize date string format to output DD-MM-YYYY.

    TCMB Web Service accepts dates in DD-MM-YYYY format only.
    This function converts datetime dtype and date string
    in YYYY-MM-DD format into the default TCMB format.

    Paramters
    ---------
    date_str:
        Date string in one of the following formats:
        - DD-MM-YYYY
        - DD.MM.YYYY
        - YYYY-MM-DD
        - YYYY.MM.DD

    Returns
    -------
    date_str:
        Date string in the "DD-MM-YYYY" format.
    """

    if re.match(r"\d{1,2}-\d{1,2}-\d{4}", date_str):
        date_format = "%d-%m-%Y"
    elif re.match(r"\d{1,2}.\d{1,2}.\d{4}", date_str):
        date_format = "%d.%m.%Y"
    elif re.match(r"\d{4}-\d{1,2}-\d{1,2}", date_str):
        date_format = "%Y-%m-%d"
    elif re.match(r"\d{4}.\d{1,2}.\d{1,2}", date_str):
        date_format = "%Y.%m.%d"

    return datetime.strptime(date_str, date_format).strftime("%d-%m-%Y")


def to_dataframe(data: dict) -> pd.DataFrame:
    """Convert data from the json response to pandas DataFrame."""
    df = pd.DataFrame(data)
    # drop unused column
    df = df.drop("UNIXTIME", axis=1)
    # set date as index
    # TODO: check if "Tarih" always the first column
    df = df.set_index(df.columns[0])

    # detect date format
    if re.match(r"\d+-\d+-\d{4}", df.index[0]):
        date_format = "%d-%m-%Y"
    elif re.match(r"\d+-\d{4}", df.index[0]):
        date_format = "%m-%Y"
    elif re.match(r"\d{4}-\d+", df.index[0]):
        date_format = "%Y-%m"
    elif re.match(r"\d{4}", df.index[0]):
        date_format = "%Y"
    # convert date strings to datetime
    df.index = pd.to_datetime(df.index, format=date_format)

    # replace None with NaN
    df = df.fillna(np.nan)
    # convert object columns to float
    # TODO: convert to integer when possible
    df = df.astype(float)
    # drop rows if all missing
    df = df.dropna(how="all")

    return df
