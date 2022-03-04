from fastapi.testclient import TestClient
from app.main import app
from app.models import Operator
from app.services.auth import OperatorAuthHandler

client = TestClient(app)

def setup():
    username='test'
    password='test'
    hashed_password = OperatorAuthHandler().get_password_hash(password)
    Operator(username=username, password=hashed_password).save()


setup()

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
    assert response.json() == {"detail": "'url' argument is invalid!"}


def test_invalid_input_url():
    # TODO: some one fix this one :v
    pass
    # response = client.get("/api/check?url=TranQuo48955621")
    # assert response.status_code == 400
    # assert response.json() == {"detail": "'url' argument is invalid!"}


def test_twitter_user_not_found():
    response = client.get("/api/check?url=https://twitter.com/TranQuoc48955621")
    assert response.status_code == 404
    assert response.json() == {"detail": "User account @TranQuoc48955621 not found"}


def test_twitter_user_found():
    response = client.get("/api/check?url=https://twitter.com/TranQuo48955621")
    assert response.status_code == 200
    assert response.json()["user_info"]["name"] == "Tran Quoc Anh"

def test_login():
    pass

def test_logout():
    pass

def test_get_user_session_token():
    pass

def test_operator_view_reports():
    pass

def test_operator_add_report_to_ml_data():
    pass

def test_user_report_twitter_account():
    pass
