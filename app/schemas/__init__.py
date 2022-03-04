from pydantic import BaseModel

from .auth import AccessToken, AuthDetails, TokenPayload, UserIdentifier
from .tweet import TweetInfo
from .twitter_user import TwitterUser


class CheckResponse(BaseModel):
    is_real: bool
    user_info: TwitterUser


class DetailResponse(BaseModel):
    user_info: TwitterUser
    tweet_info: TweetInfo

class AccountReport(BaseModel):
    # NOTE: this is just prototype, add more fields later!
    user_info: TwitterUser
