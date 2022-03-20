from unittest.mock import patch

import pytest
from tweepy import Forbidden, NotFound

from .mock_models import MockData, MockResponse


@pytest.fixture(autouse=False, scope="function")
def mock_user_notfound():
    with patch("tweepy.API") as mock_api:
        mock_api().get_user.side_effect = NotFound(response=MockResponse())
        yield


@pytest.fixture(autouse=False, scope="function")
def mock_user_suspended():
    with patch("tweepy.API") as mock_api:
        mock_api().get_user.side_effect = Forbidden(response=MockResponse())
        yield


@pytest.fixture(autouse=False, scope="class")
def mock_user_found():
    with (patch("tweepy.API") as mock_api,):
        mock_api().get_user.return_value = MockData.user_info()
        yield MockData.user_info()["username"]
