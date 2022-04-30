from unittest.mock import patch

import pytest
import tweepy

from app.models import BotPrediction

from .helpers.mock_models import MockData, MockResponse

PATHS = ["check", "detail"]


@pytest.fixture
def mock_user_notfound(mock_tweepy_api):
    mock_tweepy_api().get_user.side_effect = tweepy.NotFound(response=MockResponse())


@pytest.fixture
def mock_user_suspended(mock_tweepy_api):
    mock_tweepy_api().get_user.side_effect = tweepy.Forbidden(response=MockResponse())


@pytest.mark.parametrize("path", PATHS)
class TestScrapper:
    class TestInvalidInput:
        def assert_invalid(self, client, url):
            response = client.get(url)
            assert response.status_code == 400
            assert response.json() == {"detail": "'url' argument is invalid!"}
            assert BotPrediction.objects().count() == 0

        def test_no_input_url(self, client, path):
            url = f"/api/{path}?url="
            self.assert_invalid(client, url)

        @pytest.mark.parametrize("username", ["####.()32##", "/", "test/123"])
        def test_wrong_format_url(self, client, username, path):
            url = f"/api/{path}?url={username}"
            self.assert_invalid(client, url)

    class TestScrapingError:
        username = "unknown"

        def test_twitter_user_not_found(self, client, path, mock_user_notfound):
            response = client.get(
                f"/api/{path}?url=https://twitter.com/{self.username}"
            )
            assert response.status_code == 404
            assert response.json() == {
                "detail": f"User account @{self.username} not found"
            }
            assert BotPrediction.objects().count() == 0

        def test_twitter_user_suspended(self, client, path, mock_user_suspended):
            response = client.get(
                f"/api/{path}?url=https://twitter.com/{self.username}"
            )
            assert response.status_code == 403
            assert response.json() == {
                "detail": f"User account @{self.username} has been suspended"
            }
            assert BotPrediction.objects().count() == 0

    @pytest.mark.usefixtures("mock_user_found")
    class TestUserFound:
        username = MockData.user_info()._json["username"]

        def assert_check_success(self, client, username, response):
            assert response.status_code == 200
            assert response.json()["user_info"]["username"] == username
            assert BotPrediction.objects().count() == 1

        def test_input_https_url(self, client, path):
            assert BotPrediction.objects().count() == 0
            username = self.username
            url = f"/api/{path}?url=https://twitter.com/{username}"
            response = client.get(url)
            self.assert_check_success(client, username, response)

        def test_input_username_only(self, client, path):
            username = self.username
            url = f"/api/{path}?url={username}"
            response = client.get(url)
            self.assert_check_success(client, username, response)

        def test_tweet_as_url_input(self, client, path):
            username = self.username
            tweet_url = f"https://twitter.com/{username}/status/1504573289435484160"
            response = client.get(f"/api/{path}?url={tweet_url}")
            self.assert_check_success(client, username, response)

        @pytest.mark.parametrize("username", ["   ", "twitter.com", "(.)(.)"])
        def test_input_weird_usernames(self, client, username, path):
            assert BotPrediction.objects().count() == 0
            response = client.get(f"/api/check?url={username}")
            assert response.status_code == 200
            assert BotPrediction.objects().count() == 1

        def test_check_then_detail(self, client, path):
            username = self.username
            check_response = client.get(f"/api/check?url={username}")
            self.assert_check_success(client, username, check_response)
            detail_response = client.get(f"/api/detail?url={username}")
            # make sure database not changed
            self.assert_check_success(client, username, detail_response)
            # make sure twitterAPI is not re-called
            with patch("app.services.scrape.TwitterScraper") as mock_scraper:
                mock_scraper.api.get_user.assert_not_called()
            if path == PATHS[-1]:
                pytest.skip("Only runs once")
