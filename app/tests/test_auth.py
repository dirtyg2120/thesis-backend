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
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_logout_success(create_operator):
    client.post(
        "/auth/login",
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={"username": "test", "password": "test"},
    )

    logout_response = client.post(
        "/auth/logout",
    )
    assert logout_response.status_code == 200


def test_get_user_session_token():
    issued_ids = []
    for _ in range(20):
        response = client.get(
            "/auth/session-id", headers={"accept": "application/json"}
        )
        assert response.status_code == 200
        cookie = cookies.SimpleCookie(response.headers["set-cookie"])
        session_id = cookie["session_id"].value
        assert session_id not in issued_ids
        issued_ids.append(session_id)