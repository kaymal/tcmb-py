"""Core module.

This module allows user to read data from
Turkish Central Bank's (TCMB) EVDS Web Service.

See for details:
----------------
EN: https://evds2.tcmb.gov.tr/help/videos/EVDS_Web_Service_Usage_Guide.pdf
TR: https://evds2.tcmb.gov.tr/help/videos/EVDS_Web_Servis_Kullanim_Kilavuzu.pdf

"""
from __future__ import annotations
from datetime import date
from functools import cached_property
import os

import pandas as pd

from tcmb import const, auth, utils, fetch


def read(
    series: str | list[str],
    start: str | None = None,
    end: str | None = None,
    agg: str | list[str] | None = None,
    formulas: str | None = None,
    freq: str | int | None = None,
    seperator: str = ".",
    headers: dict | None = None,
    api_key: str | None = None,
    **kwargs,
) -> pd.DataFrame:
    """Read data from TCMB's EVDS Web Service.

    Parameters
    ----------
    series:
        Time series key. If str, wildcard characters (*) and (?) can be used.
        The wildcard characters are represented as an asterisk (*)
        or a question mark (?). The asterisk (*) represents any number of characters,
        while the question mark (?) represents a single character.
        Additionally, omitting the value has the same effect as using an asterisk.
    start: str or datetime-like
        Start date of the series in DD-MM-YYYY, YYYY-MM-DD, or datetime-like
        format.
    end: str or datetime-like
        End date of the series in DD-MM-YYYY, YYYY-MM-DD, or datetime-like
        format.
    agg: {None, "avg", "min", "max", "first", "last", "sum"}
        Aggregation type of the result. If type of the `series` is string,
        type of the `agg` must also be string. If `series` is a list,
        `agg` can be either a `str` or a `list`.
    formulas:
        Compute values such as percentage change, difference,
        year-over-year (YoY) chanhe, Year-to-date (YTD) change,
        moving average.
        - 0: level
        - 1: percentage change
        - 2: difference
        - 3: YoY percentage change
        - 4: YoY difference
        - 5: YTD percentage change
        - 6: YTD difference
        - 7: moving average
        - 8: moving sum
    freq:
        Frequency of the series. Either frequency string or int to be used.
        - None: the default frequency of the series is taken.
        - "D": 1,      # daily
        - "B": 2,      # business
        - "W-FRI": 3,  # weekly (friday)
        - "W": 3,      # weekly (friday)
        - "M": 5,      # monthly
        - "Q": 6,      # quarterly
        - "2Q": 7,     # semi-annual
        - "A": 8,      # annual
        - "Y": 8,      # annual
    seperator:
        Delimiter to use.
    api_key:
        API key of the user. If None, environment variable with
        the name "TCMB_API_KEY" will be used to as the api_key. If
        the api_key argument is not passed or it is not exported to the
        environment, ApiKeyError is raised.
    **kwargs:
        Keyword arguments passed to the request.

    Returns
    -------
    df: Pandas DataFrame.

    References
    ----------
    - https://evds2.tcmb.gov.tr/help/videos/EVDS_Web_Service_Usage_Guide.pdf

    Example
    -------
    import tcmb

    # read one series
    df = tcmb.read("TP.DK.USD.S.YTL")

    # read multiple series
    df = tcmb.read(["TP.DK.USD.S.YTL", "TP.DK.EUR.S.YTL"])

    # read series with wildcarding
    df = tcmb.read("TP.DK.*.S.YTL"])
    """
    api_key = api_key or os.environ.get("TCMB_API_KEY")

    # convert freq string to
    if isinstance(freq, str):
        freq = const.FREQ_MAPPING[freq]

    # wildcard search if any of the following case
    if isinstance(series, str):
        if ("*" in series) or ("?" in series) or (".." in series):
            series = utils.wildcard_search(series)

    # convert list to str seperated by "-"
    # as descibed in the api reference
    if isinstance(series, list):
        series = "-".join(series)

    # convert list to str seperated by "-"
    if isinstance(agg, list):
        agg = "-".join(agg)

    # convert date string formats to "DD-MM-YYYY"
    if start:
        start = utils.standardize_date(start)
    if end:
        end = utils.standardize_date(end)

    params = {
        "series": series,
        "startDate": start or "01-01-1970",
        "endDate": end or date.today().strftime("%d-%m-%Y"),
        "type": "json",  # csv, xml, json
        "aggregationTypes": agg,
        "key": api_key,
        "formulas": formulas,
        "frequency": freq,
        "decimalSeperator": seperator,
        **kwargs,
    }

    res = fetch.get_response(params=params, headers=headers)

    # convert response JSON to DataFrame
    #   time series data is in the "items"
    data = utils.to_dataframe(res.json()["items"])

    return data


class Client:
    """Base class for TCMB web service access.

    Parameters
    ----------
    api_key:
        API key of the user. If None, environment variable with
        the name "TCMB_API_KEY" will be used to as the api_key. If
        the api_key argument is not passed or it is not exported to the
        environment, ApiKeyError is raised.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("TCMB_API_KEY")
        auth.check_api_key(self.api_key)

    @staticmethod
    def _get_response(
        params: dict,
        headers: dict | None = None,
        endpoint: str | None = None,
        proxies: dict | None = None,
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
        kwargs:
            Optional keyword arguments that request takes.
        """
        res = fetch.get_response(
            params=params,
            headers=headers,
            endpoint=endpoint,
            proxies=proxies,
            **kwargs,
        )

        return res

    def read(
        self,
        series: str | list[str],
        start: str | None = None,
        end: str | None = None,
        agg: str | list[str] | None = None,
        formulas: str | None = None,
        freq: str | int | None = None,
        seperator: str = ".",
        headers: dict | None = None,
        metadata: bool = False,
        **kwargs,
    ) -> pd.DataFrame | dict:
        """Read data from TCMB's EVDS Web Service.

        Parameters
        ----------
        series:
            Time series key. e.g. "TP.DK.USD.S.YTL"
        start: str or datetime-like
            Start date of the series in DD-MM-YYYY, YYYY-MM-DD, or datetime-like
            format.
        end: str or datetime-like
            End date of the series in DD-MM-YYYY, YYYY-MM-DD, or datetime-like
            format.
        agg: {None, "avg", "min", "max", "first", "last", "sum"}
            Aggregation type of the result. If type of the `series` is string,
            type of the `agg` must also be string. If `series` is a list,
            `agg` can be either a `str` or a `list`.
        formulas:
            Compute values such as percentage change, difference,
            year-over-year (YoY) chanhe, Year-to-date (YTD) change,
            moving average.
            - 0: level
            - 1: percentage change
            - 2: difference
            - 3: YoY percentage change
            - 4: YoY difference
            - 5: YTD percentage change
            - 6: YTD difference
            - 7: moving average
            - 8: moving sum
        freq:
            Frequency of the series. Either frequency string or int to be used.
            - None: the default frequency of the series is taken.
            - "D": 1,      # daily
            - "B": 2,      # business
            - "W-FRI": 3,  # weekly (friday)
            - "W": 3,      # weekly (friday)
            - "M": 5,      # monthly
            - "Q": 6,      # quarterly
            - "2Q": 7,     # semi-annual
            - "A": 8,      # annual
            - "Y": 8,      # annual
        seperator:
            Delimiter to use.
        metadata:
            Whether to read metadata for the series. If True, get requests are
            performed as many as the number of series keys passed. The metadata
            can be accessed using the `.attrs` attribute of the pandas.DataFrame.
            e.g. df.attrs
        **kwargs:
            Keyword arguments passed to the request.

        Returns
        -------
        df: Pandas DataFrame.

        References
        ----------
        - https://evds2.tcmb.gov.tr/help/videos/EVDS_Web_Service_Usage_Guide.pdf

        Example
        -------
        df = client.read(["...", "..."])
        """
        df = read(
            series=series,
            start=start,
            end=end,
            agg=agg,
            formulas=formulas,
            freq=freq,
            seperator=seperator,
            headers=headers,
            api_key=self.api_key,
            **kwargs,
        )

        # if metadata is true, save metadata info
        # to the .attrs attribute of the DataFrame
        #   it can be accessed using attrs: e.g. "df.attrs"
        if metadata:
            attrs: dict[str, dict] = {}

            for series_item in series.split("-"):
                attrs[series_item] = self.get_series_metadata(series_item)

            df.attrs = attrs

        return df

    def get_categories_metadata(self):
        """Get the list of the metadata of all categories."""
        params = {
            "type": "json",
            "key": self.api_key,
        }

        res = self._get_response(params=params, endpoint="categories")

        return res.json()

    def get_datagroups_metadata(
        self, mode: int = 0, code: str | int | None = None
    ) -> pd.DataFrame:
        """Get datagroups metadata.

        The metadata of the datagroups include the following:
        ['DATAGROUP_CODE', 'CATEGORY_ID', 'DATAGROUP_NAME', 'DATAGROUP_NAME_ENG',
         'FREQUENCY_STR', 'FREQUENCY', 'DATASOURCE', 'DATASOURCE_ENG',
         'METADATA_LINK', 'METADATA_LINK_ENG', 'REV_POL_LINK',
         'REV_POL_LINK_ENG', 'APP_CHA_LINK', 'APP_CHA_LINK_ENG', 'START_DATE',
         'END_DATE']

        Parameters
        ----------
        mode: {0, 1, 2}
            Apply filtering according to the following options.
            - 0: Return all data groups of all categories
            - 1: Return information of the selected data group
            - 2: Return information of all data groups of a category
            If 1 or 2 is passed, "code" argument must also be passed.
        code:
            - If mode=1, the user must pass a "datagroup code"
              e.g. datagroups(mode=1, code="bie_yssk")
            - If mode=2, the user must pass a "category code" (category ID).
              e.g. datagroups(mode=2, code=2)

        """
        if (mode > 0) and (code is None):
            raise ValueError("If mode=1 or mode=2, 'code' argument must be passed.")

        params = {
            "mode": str(mode),
            "code": code,
            "type": "json",
            "key": self.api_key,
        }

        res = self._get_response(params=params, endpoint="datagroups")

        json_data = res.json()

        # if no data (empty response)
        if not json_data:
            raise ValueError(
                "No data on respose, check `mode` and `code` parameters.\n"
                f"Response: {res.content}"
            )

        return json_data

    def get_series_metadata(
        self, series: str | None = None, datagroup: str | None = None
    ) -> dict | list[dict]:
        """Get the metadata of the series.

        The metadata of the series include the following:
        ['SERIE_CODE', 'DATAGROUP_CODE', 'SERIE_NAME', 'SERIE_NAME_ENG',
         'FREQUENCY_STR', 'DEFAULT_AGG_METHOD_STR', 'DEFAULT_AGG_METHOD',
         'TAG', 'TAG_ENG', 'DATASOURCE', 'DATASOURCE_ENG', 'METADATA_LINK',
         'METADATA_LINK_ENG', 'REV_POL_LINK', 'REV_POL_LINK_ENG',
         'APP_CHA_LINK', 'APP_CHA_LINK_ENG', 'START_DATE', 'END_DATE']

        Parameters
        ----------
        series:
            Time series key. e.g. "TP.DK.USD.S.YTL"
            Onde of `series` or `code` must be passed.
        datagroup:
            Data group code. eg. "bie_yssk".
            One of `series` or `code` must be passed.

        Returns
        -------
        One of
        - Dict of metadata of one time series
        - List of multiple metadata of multiple time series
        """
        if (series is None) and (datagroup is None):
            raise ValueError("One of `series` or `code` arguments must be passed.")

        params = {
            "code": series or datagroup,
            "type": "json",
            "key": self.api_key,
        }

        res = self._get_response(params=params, endpoint="serieList")

        return res.json()

    @cached_property
    def categories(self):
        """Get categories metadata and save as a property."""
        return self.get_categories_metadata()

    @cached_property
    def datagroups(self):
        """Get datagroups metadata and save as a property."""
        return self.get_datagroups_metadata()

    def __repr__(self) -> str:
        return "tcmb client"
