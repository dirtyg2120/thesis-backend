from mongoengine import connect, disconnect
from pytest import fixture

from app.models import Operator, TwitterUser
from app.services.auth import OperatorAuthHandler

DB_NAME = "mongoenginetest"
OP_UNAME = "test"
OP_PASS = "test"


@fixture(autouse=True, scope="function")
def setup_teardown():
    print()
    print("Setup")
    connect(DB_NAME, host="mongomock://localhost")
    yield
    print("Teardown")
    disconnect()


@fixture(autouse=True, scope="function")
def print_db_status(setup_teardown):
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
