import pytest

from app.models import Report

from .mock_models import MockData

TWITTER_ID = MockData.user_info()["id_str"]


@pytest.fixture
def checked_twitter_account(client, mock_user_found):
    username = MockData.user_info()["username"]
    response = client.get(
        "/api/check", params={"url": f"https://twitter.com/{username}"}
    )
    assert response.status_code == 200
    assert response.json()["user_info"]["username"] == username
    assert Report.objects().count() == 0


@pytest.fixture
def reported_twitter_account(client, checked_twitter_account):
    response = client.post(
        f"/api/send-report/{TWITTER_ID}",
    )
    assert response.status_code == 200
    assert Report.objects().count() == 1
