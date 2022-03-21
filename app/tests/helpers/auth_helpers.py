from http import cookies

import pytest

from .. import client


@pytest.fixture(autouse=False, scope="function")
def login_operator():
    op_response = client.post(
        "/auth/login",
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={"username": "test", "password": "test"},
    )
    cookie = cookies.SimpleCookie(op_response.headers["set-cookie"])
    access_token = cookie["access_token"].value
    return access_token
