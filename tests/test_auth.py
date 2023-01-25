import pytest

from tcmb import auth
from tcmb.errors import ApiKeyError


def test_check_api_key():
    with pytest.raises(ApiKeyError):
        auth.check_api_key()
