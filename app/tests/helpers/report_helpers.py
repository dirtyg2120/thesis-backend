import pytest

from app.models import Report

from .. import client
from .mock_models import MockData

TWITTER_ID = MockData.user_info()["id_str"]


def check_account():
    username = MockData.user_info()["username"]
    response = client.get(
        "/api/check", params={"url": f"https://twitter.com/{username}"}
    )
    assert response.status_code == 200
    assert response.json()["user_info"]["username"] == username
    assert Report.objects().count() == 0


def report_account():
    response = client.post(
        f"/api/send-report/{TWITTER_ID}",
    )
    assert response.status_code == 200
    assert Report.objects().count() == 1


@pytest.fixture(autouse=False, scope="function")
def checked_twitter_account(mock_user_found):
    check_account()


@pytest.fixture(autouse=False, scope="function")
def reported_twitter_account(checked_twitter_account):
    report_account()
