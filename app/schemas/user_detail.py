from typing import List

from pydantic import BaseModel


class TimeSeries(BaseModel):
    time: List[str]
    value: List[int]


class UserDetailResponse(BaseModel):
    day_of_week: TimeSeries
    hour_of_day: TimeSeries
