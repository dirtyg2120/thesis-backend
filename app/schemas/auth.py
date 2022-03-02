from datetime import datetime
from typing import Optional
from typing import Literal

from pydantic import BaseModel

class AuthDetails(BaseModel):
    username: str
    password: str

class UserIdentifier(BaseModel):
    user_id: str
    role: Literal['user', 'operator']

class TokenPayload(BaseModel):
    exp: datetime
    iat: datetime
    sub: UserIdentifier

class AccessToken(BaseModel):
    token: str