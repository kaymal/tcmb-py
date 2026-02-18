import pytest
import requests

from tcmb import auth
from tcmb.errors import ApiKeyError, InvalidSeriesCode


class OkResponse:
    status_code = 200
    text = ""
    content = b""

    @staticmethod
    def json():
        return {"ok": True}


class HttpErrorResponse:
    status_code = 500
    text = "server error"
    content = b"<html><body>invalid key</body></html>"

    @staticmethod
    def json():
        return {"error": True}

    @staticmethod
    def raise_for_status():
        raise requests.exceptions.HTTPError("500 Server Error")


class InvalidSeriesResponse:
    status_code = 200
    text = "<div class='error-title'>invalid</div>"
    content = b"invalid"

    @staticmethod
    def json():
        raise requests.exceptions.JSONDecodeError("invalid", "doc", 0)


def test_check_api_key():
    with pytest.raises(ApiKeyError):
        auth.check_api_key()


def test_check_status_raises_api_key_error_on_http_error():
    with pytest.raises(ApiKeyError):
        auth.check_status(HttpErrorResponse())


def test_check_status_raises_invalid_series_code_on_non_json_error_title():
    with pytest.raises(InvalidSeriesCode):
        auth.check_status(InvalidSeriesResponse())


def test_check_status_reraises_json_decode_without_error_title():
    class NonJsonNoErrorTitle:
        status_code = 200
        text = "not json"
        content = b"not json"

        @staticmethod
        def json():
            raise requests.exceptions.JSONDecodeError("invalid", "doc", 0)

    with pytest.raises(requests.exceptions.JSONDecodeError):
        auth.check_status(NonJsonNoErrorTitle())


def test_check_api_key_calls_evds_endpoint(monkeypatch):
    captured = {}

    def mock_get(url, headers=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["timeout"] = timeout
        return OkResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    assert auth.check_api_key("fakekey") is True
    assert captured["headers"] == {"key": "fakekey"}
    assert captured["timeout"] == 30


def test_check_api_key_uses_custom_base_url(monkeypatch):
    captured = {}

    def mock_get(url, headers=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["timeout"] = timeout
        return OkResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    assert auth.check_api_key("fakekey", base_url="https://custom.evdshost.test/service/evds") is True
    assert captured["url"] == "https://custom.evdshost.test/service/evds/categories/type=json"
    assert captured["headers"] == {"key": "fakekey"}
    assert captured["timeout"] == 30
