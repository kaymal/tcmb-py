"""Utilities module."""
import json
import re
import os.path
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


def wildcard_search(
    pattern: str, items: list | None = None, use_package_data: bool = True
) -> list:
    """Search for items using regex pattern that can contain wildcard characters.

    Parameters
    ----------
    pattern:
        The regex pattern to use for searching, which may contain wildcard
        characters. The wildcard characters are represented as an asterisk (*)
        or a question mark (?). The asterisk (*) represents any number of characters,
        while the question mark (?) represents a single character.
        Additionally, omitting the value has the same effect as using an asterisk.
    items:
        Use the list of items to search through. If None, items in the
        package data is used. Note that package data may not be up to date.
        The user can choose to fetch series data from TCMB instead of
        using the flat file in package data by using the "update" parameter.
    use_package_data:
        Whether to use package resources or fetch all series keys from
        the TCMB database. If False, fetching may take up to 5 minutes.

    Returns
    -------
    A list of items that match the regex pattern.

    Example
    -------
    >>> wildcard_search('TP.API.REP.TL.*', items=items)
    ['TP.API.REP.TL.A12',
     'TP.API.REP.TL.A23',
     'TP.API.REP.TL.G1',
     'TP.API.REP.TL.G1530',
     'TP.API.REP.TL.G214']

    >>> wildcard_search('TP.API.REP.TL.A??', items=items)
    ['TP.API.REP.TL.A12', 'TP.API.REP.TL.A23']

    """
    if items is None:
        items = []

        if use_package_data:
            file_path = os.path.join(
                os.path.dirname(__file__), "resources", "series.json"
            )

            with open(file_path, "r") as file:
                dg_series = json.load(file)

        else:
            from tcmb._data import fetch_dg_series_codes

            dg_series = fetch_dg_series_codes()

        # merge series of all datagroups into one list
        for item in dg_series.values():
            items.extend(item)

    # Replace the wildcard characters with a regex-friendly equivalent.
    pattern = pattern.replace("*", ".*").replace("?", ".")

    # Compile the regex pattern for efficiency.
    compiled_regex = re.compile(pattern)

    # Use list comprehension to find matching items.
    matching_items = [item for item in items if compiled_regex.search(item)]

    return matching_items
