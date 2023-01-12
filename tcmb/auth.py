from __future__ import annotations

import requests

from tcmb.errors import ApiKeyError


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
    # check if response is ok
    if res.status_code != 200:
        try:
            res.raise_for_status()
        except Exception as err:
            print(err.with_traceback(None))
            raise ApiKeyError("API key is invalid.")

    return True
