from pydantic import BaseModel

from .auth import *
from .tweet import TweetInfo
from .twitter_user import TwitterUser


class CheckResponse(BaseModel):
    is_real: bool
    user_info: TwitterUser


class DetailResponse(BaseModel):
    user_info: TwitterUser
    tweet_info: TweetInfo
