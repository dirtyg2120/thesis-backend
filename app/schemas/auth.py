from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


class AuthDetails(BaseModel):
    username: str
    password: str


class UserIdentifier(BaseModel):
    user_id: str
    role: Literal["user", "operator"]


class TokenPayload(BaseModel):
    exp: datetime
    iat: datetime
    sub: UserIdentifier


class AccessToken(BaseModel):
    token: str
