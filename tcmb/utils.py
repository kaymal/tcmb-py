"""Utilities module."""
import re
from datetime import datetime


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
