from fastapi import APIRouter, Depends, HTTPException, Response

from app import schemas
from app.core.config import settings
from app.models import Operator
from app.services.auth import OperatorAuthHandler, UserAuthHandler

router = APIRouter()
user_auth_handler = UserAuthHandler()
operator_auth_handler = OperatorAuthHandler()


@router.post("/login", name="operator:login")
def login(auth_details: schemas.AuthDetails):
    operator = Operator.objects(username=auth_details.username).first()
    if (operator is None) or (
        not operator_auth_handler.verify_password(
            auth_details.password, operator["password"]
        )
    ):
        raise HTTPException(status_code=401, detail="Invalid username and/or password")
    token = operator_auth_handler.encode_token(operator["username"])
    resp = Response()
    resp.set_cookie("token", token, max_age=settings.TOKEN_EXPIRATION_TIME * 60)
    return resp


@router.get("/logout", name="operator:logout")
def logout(user_identifier=Depends(operator_auth_handler.auth_wrapper)):
    resp = Response()
    resp.delete_cookie("token")
    return resp


# NOTE: for normal user to get their session token
@router.get("/session-token", name="user:login")
def get_user_session_token():
    token = user_auth_handler.encode_token()
    resp = Response()
    resp.set_cookie("token", token, max_age=3600)
    return resp
