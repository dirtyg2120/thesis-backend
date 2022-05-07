from pydantic import BaseModel

from .auth import AccessToken, AuthDetails, TokenPayload, UserIdentifier
from .report import ReportResponse
from .twitter import TweetInfo, TweetResponse, UserInfo


class CheckResponse(BaseModel):
    score: float
    user_info: UserInfo

    class Config:
        orm_mode = True


class DetailResponse(BaseModel):
    user_info: UserInfo
    tweet_info: TweetInfo
    score: float

    class Config:
        orm_mode = True
