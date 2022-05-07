from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TweetResponse(BaseModel):
    id: str
    text: str
    created_at: datetime

    class Config:
        orm_mode = True


class TimeSeries(BaseModel):
    time: List[str]
    value: List[int]


class TweetStatistics(BaseModel):
    day_of_week: TimeSeries
    hour_of_day: TimeSeries


class TweetInfo(TweetStatistics):
    recent_tweets: List[TweetResponse]


class UserInfo(BaseModel):
    id: str
    name: str
    screen_name: str = Field(alias="username")
    created_at: datetime
    followers_count: int
    friends_count: int = Field(alias="followings_count")
    verified: bool
    profile_image_url: str = Field(alias="avatar")
    profile_banner_url: Optional[str] = Field(alias="banner")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
