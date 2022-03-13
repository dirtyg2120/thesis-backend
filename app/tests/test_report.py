from http import cookies

from . import client


def test_user_report_twitter_account():
    auth_response = client.get(
        "/auth/session-id", headers={"accept": "application/json"}
    )
    assert auth_response.status_code == 200
    cookie = cookies.SimpleCookie(auth_response.headers["set-cookie"])
    session_id = cookie["session_id"].value

    username = "JohnCena"

    report_response = client.post(
        f"/api/send-report?username={username}",
        headers={"accept": "application/json", "Cookie": f"session_id={session_id}"},
    )
    assert report_response.json() == {"status": "success", "account": username}


def test_operator_view_reports(create_operator):
    # Send report
    user_response = client.get(
        "/auth/session-id", headers={"accept": "application/json"}
    )
    cookie = cookies.SimpleCookie(user_response.headers["set-cookie"])
    session_id = cookie["session_id"].value
    username = "JohnCena"
    client.post(
        f"/api/send-report?username={username}",
        headers={"accept": "application/json", "Cookie": f"session_id={session_id}"},
    )

    # Check report
    op_response = client.post(
        "/auth/login",
        headers={"accept": "application/json", "Content-Type": "application/json"},
        json={"username": "test", "password": "test"},
    )
    cookie = cookies.SimpleCookie(op_response.headers["set-cookie"])
    access_token = cookie["access_token"].value
    view_report_response = client.get(
        "/api/view-reports",
        headers={
            "accept": "application/json",
            "Cookie": f"access_token={access_token}",
        },
    )
    assert view_report_response.json()[0]["username"] == username
