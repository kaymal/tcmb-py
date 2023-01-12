import os
import pytest

from tcmb import core
from tcmb.errors import ApiKeyError


def test_check_api_key():
    with pytest.raises(ApiKeyError):
        os.environ.pop("TCMB_API_KEY", None)
        _ = core.Client()
