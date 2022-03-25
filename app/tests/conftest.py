from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pytest import fixture

from app.main import app
from app.models import Operator, TwitterUser
from app.services.auth import OperatorAuthHandler

from .helpers.mock_models import MockPaginator

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


@fixture
def client():
    with TestClient(app) as c:
        yield c


@fixture(autouse=True, scope="function")
def print_db_status(client):
    print("--before test--")
    print("Current twitter user count: ", TwitterUser.objects().count())
    print("Current operator count: ", Operator.objects().count())

    yield

    print("--after test--")
    print("Current twitter user count: ", TwitterUser.objects().count())
    print("Current operator count: ", Operator.objects().count())


@fixture(autouse=False, scope="function")
def create_operator():
    hashed_password = OperatorAuthHandler().get_password_hash(OP_PASS)
    Operator(username=OP_UNAME, password=hashed_password).save()
    assert Operator.objects().count() == 1
