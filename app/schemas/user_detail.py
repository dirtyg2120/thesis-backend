from typing import List

from pydantic import BaseModel


class UserDetailResponse(BaseModel):
    day_of_week: List[int]
    hour_of_day: List[int]
