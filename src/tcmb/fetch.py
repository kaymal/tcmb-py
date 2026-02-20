"""Data fetching module."""

from __future__ import annotations

import requests

from tcmb import auth, const

URL = const.BASE_URL


def _create_uri(params: dict, endpoint: str | None = None, base_url: str | None = None) -> str:
    """Create URI using the params and the evds url.

    The official api does not use `?` for query strings.
    Therefore the parameters are added to the end of the url
    instead of passing to the requests.get() function as `params`.

    Parameters
    ----------
    params:
        Query parameters.
    endpoint:
        One of
        - "categories"
        - "serieList"
        - "datagroups"
        - None
    base_url:
        Base URL of the EVDS API.
    """
    resolved_base_url = (base_url or const.BASE_URL).rstrip("/")

    if endpoint is not None:
        endpoint = endpoint + "/"
    else:
        endpoint = ""

    # create query string
    # NOTE: alternative -> urllib.parse.urlencode(params)
    #       however, this keeps None values
    query_str = "&".join([k + "=" + str(v) for k, v in params.items() if v is not None])

    return f"{resolved_base_url}/{endpoint}{query_str}"


def get_response(
    params: dict,
    headers: dict | None = None,
    endpoint: str | None = None,
    proxies: dict | None = None,
    base_url: str | None = None,
    **kwargs,
):
    """Get response.

    Parameters
    ----------
    params:
        Request parameters.
    headers:
        Request headers.
    endpoint:
        TCMB Web Service API endpoint.
        One of
        - "categories"
        - "serieList"
        - "datagroups"
        - None
    proxies:
        Dictionary mapping protocol to the URL of the proxy.
    base_url:
        Base URL of the EVDS API.
    kwargs:
        Optional keyword arguments that request takes.
    """
    # Create url for the get request
    #  NOTE: the official api does not use ? for query strings
    #  Therefore the parameters are added to the end of the url
    #  instead of passing to the get request as params
    url = _create_uri(params=params, endpoint=endpoint, base_url=base_url)

    # Get request
    res = requests.get(url, headers=headers, proxies=proxies, **kwargs)

    # Check status
    auth.check_status(res)

    return res
