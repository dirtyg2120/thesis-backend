from . import client


def test_no_input_url():
    response = client.get("/api/check?url=")
    assert response.status_code == 400
    assert response.json() == {"detail": "'url' argument is invalid!"}


def test_invalid_input_url():
    response = client.get("/api/check?url=TranQuo48955621/abc")
    assert response.status_code == 400
    assert response.json() == {"detail": "'url' argument is invalid!"}


def test_twitter_user_not_found():
    response = client.get("/api/check?url=https://twitter.com/TranQuoc48955621")
    assert response.status_code == 404
    assert response.json() == {"detail": "User account @TranQuoc48955621 not found"}


def test_twitter_user_found():
    response = client.get("/api/check?url=https://twitter.com/TranQuo48955621")
    assert response.status_code == 200
    assert response.json()["user_info"]["name"] == "Tran Quoc Anh"


def test_tweet_as_url_input():
    tweet_url = "https://twitter.com/fasterthanlime/status/1504573289435484160"
    response = client.get("/api/check?url=" + tweet_url)
    assert response.status_code == 200
