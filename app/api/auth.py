from re import T

from fastapi import APIRouter, Depends, HTTPException, Response

from app import schemas
from app.core.config import settings
from app.services.auth import OperatorAuthHandler, UserAuthHandler

router = APIRouter()
user_auth_handler = UserAuthHandler()
operator_auth_handler = OperatorAuthHandler()

users = []

# TODO: this is just temporary for operator registering, delete or modify later
@router.post("/register", status_code=201, response_model=str, name="operator:register")
def register(auth_details: schemas.AuthDetails):
    if any(x["username"] == auth_details.username for x in users):
        raise HTTPException(status_code=400, detail="Username is taken")
    hashed_password = operator_auth_handler.get_password_hash(auth_details.password)
    users.append({"username": auth_details.username, "password": hashed_password})
    return "Success"


@router.post("/login", response_model=schemas.AccessToken, name="operator:login")
def login(auth_details: schemas.AuthDetails):
    user = None
    for x in users:
        if x["username"] == auth_details.username:
            user = x
            break

    if (user is None) or (
        not operator_auth_handler.verify_password(
            auth_details.password, user["password"]
        )
    ):
        raise HTTPException(status_code=401, detail="Invalid username and/or password")
    token = operator_auth_handler.encode_token(user["username"])
    resp = Response()
    resp.set_cookie("token", token, max_age=3600)
    return resp


@router.post("/logout", name="operator:logout")
def logout():
    resp = Response()
    resp.delete_cookie("token")
    return resp


# NOTE: for normal user to get their session token
@router.post("/session_token", response_model=schemas.AccessToken, name="user:login")
def get_user_session_token():
    token = user_auth_handler.encode_token()
    return schemas.AccessToken(token=token)


# TODO: remove these test endpoints later

# NOTE: only for operator
@router.get(
    "/op_protected", response_model=schemas.UserIdentifier, name="operator:test"
)
def protected(user_identifier=Depends(operator_auth_handler.auth_wrapper)):
    return user_identifier


@router.get("/user_protected", response_model=schemas.UserIdentifier, name="user:test")
def protected(user_identifier=Depends(user_auth_handler.auth_wrapper)):
    return user_identifier


@router.get("/unprotected", name="test open endpoint")
def unprotected():
    return {"hello": "world"}
