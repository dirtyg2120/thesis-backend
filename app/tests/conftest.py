from http import cookies
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import Operator, TwitterUser
from app.services.auth import OperatorAuthHandler

from .helpers.mock_models import MockData, MockPaginator

OP_UNAME = "test"
OP_PASS = "test"


@pytest.fixture(autouse=True, scope="session")
def mock_tweepy_global():
    with (
        patch("tweepy.AppAuthHandler"),
        patch("tweepy.Client"),
        patch("tweepy.Paginator", wraps=MockPaginator),
    ):
        yield


@pytest.fixture
def mock_tweepy_api():
    with patch("tweepy.API") as mock_api:
        yield mock_api


@pytest.fixture
def mock_user_found(mock_tweepy_api):
    mock_tweepy_api().get_user.return_value = MockData.user_info()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True, scope="function")
def print_db_status(client):
    print("--before test--")
    print("Current twitter user count: ", TwitterUser.objects().count())
    print("Current operator count: ", Operator.objects().count())

    yield

    print("--after test--")
    print("Current twitter user count: ", TwitterUser.objects().count())
    print("Current operator count: ", Operator.objects().count())


@pytest.fixture(autouse=False, scope="function")
def create_operator():
    hashed_password = OperatorAuthHandler().get_password_hash(OP_PASS)
    Operator(username=OP_UNAME, password=hashed_password).save()
    assert Operator.objects().count() == 1


@pytest.fixture
def login_operator(client):
    op_response = client.post(
        "/auth/login",
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={"username": "test", "password": "test"},
    )
    cookie = cookies.SimpleCookie(op_response.headers["set-cookie"])
    access_token = cookie["access_token"].value
    return access_token
