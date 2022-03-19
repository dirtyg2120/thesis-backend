from unittest.mock import patch

import pytest
from tweepy import Forbidden, NotFound

from app.schemas.tweet import TimeSeries

from .mock_models import MockData, MockResponse


def path(target):
    PREFIX = "app.services.scrape."
    return f"{PREFIX}{target}"


@pytest.fixture(autouse=False, scope="function")
def mock_user_notfound():
    with patch(path("tweepy.API")) as mock_api:
        mock_api().get_user.side_effect = NotFound(response=MockResponse())
        yield


@pytest.fixture(autouse=False, scope="function")
def mock_user_suspended():
    with patch(path("tweepy.API")) as mock_api:
        mock_api().get_user.side_effect = Forbidden(response=MockResponse())
        yield


@pytest.fixture(autouse=False, scope="class")
def mock_user_found():
    with (
        patch(path("tweepy.API")) as mock_api,
        patch(path("tweepy.Paginator")) as mock_paginator,
        patch(path("TwitterScraper.get_frequency")) as mock_freq,
    ):
        mock_api().get_user.return_value = MockData.user_info()
        mock_paginator().flatten.return_value = MockData.tweets()
        mock_timeseries = TimeSeries(time=[""], value=[0])
        mock_freq.return_value = mock_timeseries, mock_timeseries
        yield MockData.data["username"]
