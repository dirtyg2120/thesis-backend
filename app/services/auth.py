from datetime import datetime, timedelta
from random import randint

import jwt
from fastapi import Cookie, HTTPException
from fastapi.security import HTTPBearer
from passlib.context import CryptContext  # type: ignore

from app.core.config import settings
from app.schemas import TokenPayload


class UserAuthHandler:
    security = HTTPBearer()
    token_lifetime = timedelta(minutes=settings.TOKEN_EXPIRATION_TIME)
    private_key = settings.AUTH_PRIVATE_KEY
    supported_roles = ["user", "operator"]

    def encode_token(self):
        """
        Generate a token for user using a random UID
        Ret: token(str)
        """

        user_id = str(randint(0, 1000000))
        payload = TokenPayload(
            exp=datetime.utcnow() + self.token_lifetime,
            iat=datetime.utcnow(),
            sub={"user_id": user_id, "role": "user"},
        ).dict()

        return jwt.encode(payload, self.private_key)

    def decode_token(self, token):
        """
        Decode token back to payload and return the user_id

        Arg: token(str): accessToken from frontend
        Ret: user_id(str)
        """
        try:
            payload = jwt.decode(token, self.private_key, algorithms=["HS256"])

            user_identifier = payload["sub"]
            if not (user_identifier["role"] in self.supported_roles):
                raise HTTPException(status_code=401, detail="Not Authorized")
            return user_identifier

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def auth_wrapper(self, session_id: str = Cookie(None)):
        """
        This is the wrapper used to enforce authentication on protected endpoints
        Use this by declaring endpoints with Dependency
            'def protected_endpoint(username=Depends(auth_handler.auth_wrapper))'
        """
        return self.decode_token(session_id)


class OperatorAuthHandler(UserAuthHandler):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    supported_roles = ["operator"]

    def get_password_hash(self, password):
        """
        Hash a password

        Arg: password(str): plain password
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        """
        Verify non-hashed password matches with hashed_password

        Arg:
            plain_password(str)
            hashed_password(str)
        Ret: bool
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id):
        """
        Encode user_id along with other information into a JWT TOKEN

        Arg: user_id(str)
        Ret: access_token(str)
        """
        payload = TokenPayload(
            exp=datetime.utcnow() + self.token_lifetime,
            iat=datetime.utcnow(),
            sub={"user_id": user_id, "role": "operator"},
        ).dict()
        return jwt.encode(payload, self.private_key)

    def auth_wrapper(self, access_token: str = Cookie(None)):
        return self.decode_token(access_token)
