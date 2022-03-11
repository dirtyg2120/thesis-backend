from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.schemas.tweet import Tweet


class AccountReport(BaseModel):
    id: str
    name: str
    username: str
    created_at: datetime
    followers_count: int
    followings_count: int
    tweets: List[Tweet]
    scrape_date: datetime
    reset_date: datetime
    report_count: int
