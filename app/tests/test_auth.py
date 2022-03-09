from http import cookies

import pytest

from . import client


@pytest.mark.parametrize(
    "username,password", [("test", "wrong"), ("wrong", "test"), ("wrong", "wrong")]
)
def test_login_invalid_credentials(create_operator, username, password):
    response = client.post(
        "/auth/login",
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={"username": username, "password": password},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username and/or password"}


def test_login_success(create_operator):
    response = client.post(
        "/auth/login",
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={"username": "test", "password": "test"},
    )
    assert response.status_code == 200


def test_logout_not_logged_in(create_operator):
    response = client.post("/auth/logout", headers={"accept": "application/json"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_logout_success(create_operator):
    login_response = client.post(
        "/auth/login",
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={"username": "test", "password": "test"},
    )
    access_token = login_response.headers["set-cookie"].split(";")[0].split("=")[1]

    logout_response = client.post(
        "/auth/logout",
        headers={
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
    )
    assert logout_response.status_code == 200


def test_get_user_session_token():
    issued_tokens = []
    for _ in range(20):
        response = client.get(
            "/auth/session-token", headers={"accept": "application/json"}
        )
        assert response.status_code == 200
        cookie = cookies.SimpleCookie(response.headers["set-cookie"])
        token = cookie["token"].value
        assert token not in issued_tokens
        issued_tokens.append(token)
