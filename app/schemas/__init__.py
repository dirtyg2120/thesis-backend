from pydantic import BaseModel

from .tweet import TweetInfo
from .user import User


class CheckResponse(BaseModel):
    is_real: bool
    user_info: User


class DetailResponse(BaseModel):
    user_info: User
    tweet_info: TweetInfo
