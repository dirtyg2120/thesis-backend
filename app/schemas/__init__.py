from pydantic import BaseModel

from .auth import AccessToken, AuthDetails, TokenPayload, UserIdentifier
from .tweet import TweetInfo
from .twitter_user import TwitterUser
from .report import AccountReport


class CheckResponse(BaseModel):
    is_real: bool
    user_info: TwitterUser


class DetailResponse(BaseModel):
    user_info: TwitterUser
    tweet_info: TweetInfo
