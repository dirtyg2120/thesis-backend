from unittest.mock import patch

import pytest

from app.models import TwitterUser

from . import client

PATHS = ["check", "detail"]


@pytest.mark.parametrize("path", PATHS)
class TestScrapper:
    class TestInvalidInput:
        def assert_invalid(self, url):
            response = client.get(url)
            assert response.status_code == 400
            assert response.json() == {"detail": "'url' argument is invalid!"}
            assert TwitterUser.objects().count() == 0

        def test_no_input_url(self, path):
            url = f"/api/{path}?url="
            self.assert_invalid(url)

        @pytest.mark.parametrize("username", ["####.()32##", "/", "test/123"])
        def test_wrong_format_url(self, username, path):
            url = f"/api/{path}?url={username}"
            self.assert_invalid(url)

    class TestScrapingError:
        username = "unknown"

        def test_twitter_user_not_found(self, path, mock_user_notfound):
            response = client.get(
                f"/api/{path}?url=https://twitter.com/{self.username}"
            )
            assert response.status_code == 404
            assert response.json() == {
                "detail": f"User account @{self.username} not found"
            }
            assert TwitterUser.objects().count() == 0

        def test_twitter_user_suspended(self, path, mock_user_suspended):
            response = client.get(
                f"/api/{path}?url=https://twitter.com/{self.username}"
            )
            assert response.status_code == 403
            assert response.json() == {
                "detail": f"User account @{self.username} has been suspended"
            }
            assert TwitterUser.objects().count() == 0

    class TestUserFound:
        def assert_check_success(self, username, response):
            assert response.status_code == 200
            assert response.json()["user_info"]["username"] == username
            assert TwitterUser.objects().count() == 1

        def test_input_https_url(self, path, mock_user_found):
            assert TwitterUser.objects().count() == 0
            username = mock_user_found
            url = f"/api/{path}?url=https://twitter.com/{username}"
            response = client.get(url)
            self.assert_check_success(username, response)

        def test_input_half_url(self, path, mock_user_found):
            username = mock_user_found
            url = f"/api/{path}?url=twitter.com/{username}"
            response = client.get(url)
            self.assert_check_success(username, response)

        def test_input_username_only(self, path, mock_user_found):
            username = mock_user_found
            url = f"/api/{path}?url={username}"
            response = client.get(url)
            self.assert_check_success(username, response)

        @pytest.mark.parametrize("username", ["   ", "twitter.com", "(.)(.)"])
        def test_input_weird_usernames(self, username, path, mock_user_found):
            assert TwitterUser.objects().count() == 0
            response = client.get(f"/api/check?url={username}")
            assert response.status_code == 200
            assert TwitterUser.objects().count() == 1

        def test_check_then_detail(self, path, mock_user_found):
            username = mock_user_found
            check_response = client.get(f"/api/check?url={username}")
            self.assert_check_success(username, check_response)
            detail_response = client.get(f"/api/detail?url={username}")
            # make sure database not changed
            self.assert_check_success(username, detail_response)
            # make sure twitterAPI is not re-called
            with patch("app.services.scrape.TwitterScraper") as mock_scraper:
                mock_scraper.api.get_user.assert_not_called()
            if path == PATHS[-1]:
                pytest.skip("Only runs once")
