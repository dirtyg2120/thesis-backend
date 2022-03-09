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

    """
        NOTE: This could potentially break during deployment
        https://stackoverflow.com/questions/63010545/issue-with-cross-site-cookies-how-to-set-cookie-from-backend-to-frontend
        https://web.dev/samesite-cookies-explained/

    """
    resp.set_cookie(
        "accessToken",
        token,
        max_age=settings.TOKEN_EXPIRATION_TIME * 60,
    )
    return resp


@router.post("/logout", name="operator:logout")
def logout(user_identifier=Depends(operator_auth_handler.auth_wrapper)):
    resp = Response()
    resp.delete_cookie("accessToken")
    return resp


# NOTE: for normal user to get their session token
@router.get("/session-id", name="user:login")
def get_user_session_id():
    session_id = user_auth_handler.encode_token()
    resp = Response()
    # NOTE: age is 1 year cause we don't wanna user to keep changing ID
    resp.set_cookie("sessionID", session_id, max_age=31556952)
    return resp
