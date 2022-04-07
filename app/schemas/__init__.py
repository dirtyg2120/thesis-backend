from pydantic import BaseModel

from .auth import AccessToken, AuthDetails, TokenPayload, UserIdentifier
from .bot_prediction import BotPrediction
from .report import ReportResponse
from .tweet import TweetInfo, TweetResponse


class CheckResponse(BaseModel):
    score: float
    user_info: BotPrediction


class DetailResponse(BaseModel):
    user_info: BotPrediction
    tweet_info: TweetInfo
    score: float
