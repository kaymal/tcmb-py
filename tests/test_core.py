import pytest
import requests
import pandas as pd

from tcmb import Client
from tcmb import core


# custom class to be the mock return value
# will override the requests.Response returned from requests.get
class MockResponse:
    status_code = 200

    @staticmethod
    def json():
        """mock json() method returns a testing dictionary."""
        return {"mock_key": "mock_response"}

    @staticmethod
    def raise_for_status():
        return None


class ReadResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return {"items": self.payload}


@pytest.fixture
def mock_response(monkeypatch):
    """Requests.get() mocked to return {'mock_key':'mock_response'}."""

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")


def test_client(mock_response):
    client = Client(api_key="fakekey")
    assert client.api_key == "fakekey"


def test_get_response(mock_response):
    client = Client(api_key="fakekey")
    result = client._get_response(params={"mock_param_key": "mock_param_value"})
    assert result.json()["mock_key"] == "mock_response"


def test_categories(mock_response):
    client = Client(api_key="fakekey")
    result = client.categories
    assert result["mock_key"] == "mock_response"


def test_datagroups(mock_response):
    client = Client(api_key="fakekey")
    result = client.datagroups
    assert result["mock_key"] == "mock_response"


def test_read_formats_params_and_returns_dataframe(monkeypatch):
    captured = {}

    def mock_get_response(params, headers=None, **kwargs):
        captured["params"] = params
        captured["headers"] = headers
        captured["kwargs"] = kwargs
        return ReadResponse([{"Tarih": "01-01-2024", "TP_DK_USD_S_YTL": "30.25"}])

    monkeypatch.setattr(core.fetch, "get_response", mock_get_response)

    data = core.read(
        series="TP.DK.USD.S.YTL",
        start="2011-06-18",
        end="17.12.2009",
        freq="M",
        api_key="fakekey",
    )

    assert captured["params"]["series"] == "TP.DK.USD.S.YTL"
    assert captured["params"]["startDate"] == "18-06-2011"
    assert captured["params"]["endDate"] == "17-12-2009"
    assert captured["params"]["frequency"] == 5
    assert captured["headers"]["key"] == "fakekey"
    assert captured["kwargs"]["base_url"] == "https://evds3.tcmb.gov.tr/igmevdsms-dis/"
    assert list(data.columns) == ["TP_DK_USD_S_YTL"]


def test_read_uses_wildcards_and_merges_headers(monkeypatch):
    captured = {}
    called = {}

    def mock_wildcard_search(pattern):
        called["pattern"] = pattern
        return ["TP.DK.USD.A.YTL", "TP.DK.USD.S.YTL"]

    def mock_get_response(params, headers=None, **kwargs):
        captured["params"] = params
        captured["headers"] = headers
        captured["kwargs"] = kwargs
        return ReadResponse(
            [
                {
                    "Tarih": "01-01-2024",
                    "TP_DK_USD_A_YTL": "30.00",
                    "TP_DK_USD_S_YTL": "30.25",
                }
            ]
        )

    monkeypatch.setattr(core.utils, "wildcard_search", mock_wildcard_search)
    monkeypatch.setattr(core.fetch, "get_response", mock_get_response)

    headers = {"foo": "bar"}
    data = core.read(series="TP.DK.USD.*.YTL", headers=headers, api_key="fakekey")

    assert called["pattern"] == "TP.DK.USD.*.YTL"
    assert captured["params"]["series"] == "TP.DK.USD.A.YTL-TP.DK.USD.S.YTL"
    assert captured["headers"]["foo"] == "bar"
    assert captured["headers"]["key"] == "fakekey"
    assert set(data.columns) == {"TP_DK_USD_A_YTL", "TP_DK_USD_S_YTL"}


def test_client_read_forwards_arguments(monkeypatch, mock_response):
    captured = {}

    def mock_read(**kwargs):
        captured.update(kwargs)
        return pd.DataFrame([{"TP_DK_USD_S_YTL": 30.25}], index=pd.to_datetime(["2024-01-01"]))

    monkeypatch.setattr(core, "read", mock_read)

    client = Client(api_key="fakekey")
    result = client.read(
        series="TP.DK.USD.S.YTL",
        headers={"x-test": "1"},
        metadata=False,
        foo="bar",
    )

    assert captured["series"] == "TP.DK.USD.S.YTL"
    assert captured["api_key"] == "fakekey"
    assert captured["headers"] == {"x-test": "1"}
    assert captured["foo"] == "bar"
    assert list(result.columns) == ["TP_DK_USD_S_YTL"]


def test_client_allows_custom_base_url(monkeypatch):
    captured = {}

    def mock_check_api_key(api_key, base_url=None):
        captured["api_key"] = api_key
        captured["base_url"] = base_url
        return True

    monkeypatch.setattr(core.auth, "check_api_key", mock_check_api_key)

    client = Client(api_key="fakekey", base_url="https://evds4.tcmb.gov.tr/igmevdsms-dis/")

    assert client.base_url == "https://evds4.tcmb.gov.tr/igmevdsms-dis/"
    assert captured["api_key"] == "fakekey"
    assert captured["base_url"] == "https://evds4.tcmb.gov.tr/igmevdsms-dis/"


def test_client_read_metadata_populates_attrs(monkeypatch, mock_response):
    def mock_read(**kwargs):
        return pd.DataFrame([{"TP_DK_USD_S_YTL": 30.25}], index=pd.to_datetime(["2024-01-01"]))

    def mock_get_series_metadata(self, series=None, datagroup=None):
        return {"SERIE_CODE": series}

    monkeypatch.setattr(core, "read", mock_read)
    monkeypatch.setattr(Client, "get_series_metadata", mock_get_series_metadata)

    client = Client(api_key="fakekey")
    result = client.read(series="TP.DK.USD.S.YTL", metadata=True)

    assert result.attrs["TP.DK.USD.S.YTL"] == {"SERIE_CODE": "TP.DK.USD.S.YTL"}


def test_get_categories_metadata_calls_endpoint(monkeypatch, mock_response):
    captured = {}

    def mock_get_response(self, params, headers=None, endpoint=None, **kwargs):
        captured["params"] = params
        captured["headers"] = headers
        captured["endpoint"] = endpoint
        return MockResponse()

    monkeypatch.setattr(Client, "_get_response", mock_get_response)

    client = Client(api_key="fakekey")
    result = client.get_categories_metadata()

    assert captured["params"] == {"type": "json"}
    assert captured["headers"] == {"key": "fakekey"}
    assert captured["endpoint"] == "categories"
    assert result == {"mock_key": "mock_response"}


def test_get_datagroups_metadata_validation():
    client = Client.__new__(Client)
    client.api_key = "fakekey"

    with pytest.raises(ValueError, match="code"):
        client.get_datagroups_metadata(mode=1)

    with pytest.raises(ValueError, match="code"):
        client.get_datagroups_metadata(mode=2)


def test_get_datagroups_metadata_empty_response_raises(monkeypatch, mock_response):
    class EmptyResponse:
        content = b""

        @staticmethod
        def json():
            return []

    def mock_get_response(self, params, headers=None, endpoint=None, **kwargs):
        return EmptyResponse()

    monkeypatch.setattr(Client, "_get_response", mock_get_response)

    client = Client(api_key="fakekey")
    with pytest.raises(ValueError, match="No data on respose"):
        client.get_datagroups_metadata()


def test_get_datagroups_metadata_mode_and_code(monkeypatch, mock_response):
    captured = {}

    def mock_get_response(self, params, headers=None, endpoint=None, **kwargs):
        captured["params"] = params
        captured["headers"] = headers
        captured["endpoint"] = endpoint
        return MockResponse()

    monkeypatch.setattr(Client, "_get_response", mock_get_response)

    client = Client(api_key="fakekey")
    result = client.get_datagroups_metadata(mode=2, code=1)

    assert captured["params"] == {"mode": "2", "code": 1, "type": "json"}
    assert captured["headers"] == {"key": "fakekey"}
    assert captured["endpoint"] == "datagroups"
    assert result == {"mock_key": "mock_response"}


def test_get_series_metadata_validation():
    client = Client.__new__(Client)
    client.api_key = "fakekey"

    with pytest.raises(ValueError, match="One of `series` or `code`"):
        client.get_series_metadata()


def test_get_series_metadata_series_and_datagroup(monkeypatch, mock_response):
    captured = {}

    def mock_get_response(self, params, headers=None, endpoint=None, **kwargs):
        captured["params"] = params
        captured["headers"] = headers
        captured["endpoint"] = endpoint
        return MockResponse()

    monkeypatch.setattr(Client, "_get_response", mock_get_response)

    client = Client(api_key="fakekey")

    result_series = client.get_series_metadata(series="TP.DK.USD.S.YTL")
    assert captured["params"] == {"code": "TP.DK.USD.S.YTL", "type": "json"}
    assert captured["endpoint"] == "serieList"
    assert captured["headers"] == {"key": "fakekey"}
    assert result_series == {"mock_key": "mock_response"}

    result_dg = client.get_series_metadata(datagroup="bie_yssk")
    assert captured["params"] == {"code": "bie_yssk", "type": "json"}
    assert captured["endpoint"] == "serieList"
    assert captured["headers"] == {"key": "fakekey"}
    assert result_dg == {"mock_key": "mock_response"}
