"""Authentication module."""
from __future__ import annotations
import re

import requests
from requests.exceptions import HTTPError, JSONDecodeError

from tcmb.errors import ApiKeyError, InvalidSeriesCode


def _extract_error_message(response):
    """Extract error message from the html body"""
    # Extract error message from the html body
    pattern = r"<body>(.*?)</body>"
    error_msgs = re.findall(pattern, str(response.content))
    error_msg = error_msgs[0].strip("\\rn")

    return error_msg


def check_status(response):
    """Check if response is ok and authentication is done."""
    if response.status_code != 200:
        try:
            response.raise_for_status()
        except HTTPError as err:
            # get error message
            error_msg = _extract_error_message(response)
            print(f"Response Error Message: {error_msg}")

            # evds responds with an 500 Internal Server Error for almost
            # any issues. This error response is a generic "catch-all" response.
            # Therefore the traceback is printed as well as the most
            # probable cause of the HTTPError: ApiKeyError
            print(err.with_traceback(None))
            raise ApiKeyError("API key is invalid.") from err
    else:
        try:
            response.json()
        except JSONDecodeError:
            if "error-title" in response.text:
                raise InvalidSeriesCode()
            else:
                print("Cannot convert response to JSON")
                raise


def check_api_key(api_key: str | None = None) -> bool:
    """Check API key.

    TCMB Web Service does not provide a way to check the api key.
    This function allows checking api key with the "categories"
    endpoint which doesn't reques a series key parameter.

    Parameters
    ----------
    api_key:
    """
    if api_key is None:
        raise ApiKeyError("No API key provided.")

    res = requests.get(
        f"https://evds2.tcmb.gov.tr/service/evds/categories/key={api_key}"
    )
    # check if authenticated
    check_status(res)

    return True
