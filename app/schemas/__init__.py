from pydantic import BaseModel

from .auth import AccessToken, AuthDetails, TokenPayload, UserIdentifier
from .report import ReportResponse
from .tweet import TweetInfo, TweetResponse
from .twitter_user import TwitterUser


class CheckResponse(BaseModel):
    score: float
    user_info: TwitterUser


class DetailResponse(BaseModel):
    user_info: TwitterUser
    tweet_info: TweetInfo
    score: float
