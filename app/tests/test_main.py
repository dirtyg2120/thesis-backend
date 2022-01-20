from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_main_404():
    response = client.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_main_docs():
    response = client.get("/docs")
    assert response.status_code == 200


def test_no_input_url():
    response = client.get("/api/check?url=")
    assert response.status_code == 400
    assert response.json() == {"detail": "'url_input' argument is invalid!"}


def test_invalid_input_url():
    response = client.get("/api/check?url=TranQuo48955621")
    assert response.status_code == 400
    assert response.json() == {"detail": "'url_input' argument is invalid!"}


def test_user_not_found():
    response = client.get("/api/check?url=https://twitter.com/TranQuoc48955621")
    assert response.status_code == 404
    assert response.json() == {"detail": "User @TranQuoc48955621 does not exist"}


def test_user_found():
    response = client.get("/api/check?url=https://twitter.com/TranQuo48955621")
    assert response.status_code == 200
    assert response.json()["user_info"]["name"] == "Tran Quoc Anh"
