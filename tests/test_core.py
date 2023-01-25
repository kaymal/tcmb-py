import pytest
import requests

from tcmb import Client


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
