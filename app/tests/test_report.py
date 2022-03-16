from http import cookies

from . import client

TWITTER_ID = "250831586"


def test_user_report_twitter_account():
    client.get("/api/check", params={"url": "https://twitter.com/TheRock"})

    report_response = client.post(
        f"/api/send-report/{TWITTER_ID}",
    )
    assert report_response.status_code == 200

    re_report_response = client.post(
        f"/api/send-report/{TWITTER_ID}",
    )
    assert re_report_response.status_code == 420


def test_operator_view_reports(create_operator):
    # Send data to check
    test_user_report_twitter_account()

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
    assert view_report_response.json()[0]["id"] == TWITTER_ID
