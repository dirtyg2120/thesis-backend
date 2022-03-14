from datetime import datetime
from typing import List

from pydantic import BaseModel


class TweetResponse(BaseModel):
    id: str
    text: str
    created_at: datetime


class TimeSeries(BaseModel):
    time: List[str]
    value: List[int]


class TweetStatistics(BaseModel):
    day_of_week: TimeSeries
    hour_of_day: TimeSeries


class TweetInfo(TweetStatistics):
    recent_tweets: List[TweetResponse]
