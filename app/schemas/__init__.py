from pydantic import BaseModel

from .tweet import TweetInfo
from .twitter_user import TwitterUser


class CheckResponse(BaseModel):
    is_real: bool
    twitter_user_info: TwitterUser


class DetailResponse(BaseModel):
    twitter_user_info: TwitterUser
    tweet_info: TweetInfo
