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


def test_logout_success(create_operator, login_operator):
    logout_response = client.post(
        "/auth/logout",
    )
    assert logout_response.status_code == 200


def cookie(token):
    f"access_token={token}"


@pytest.mark.parametrize("url", ["api/view-reports"])
class TestUnauthorizedOperatorEndpoints:
    @pytest.mark.parametrize(
        "cookie", [cookie("fake-token"), cookie(""), cookie("    "), ""]
    )
    def test_wrong_token(self, cookie, url):
        response = client.get(
            url,
            headers={"accept": "application/json", "Cookie": cookie},
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid token"}

    def test_edited_token(self, url, create_operator, login_operator):
        access_token = login_operator
        # edit token
        access_token += ","
        response = client.get(
            url,
            headers={
                "accept": "application/json",
                "Cookie": f"access_token={access_token}",
            },
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid token"}
